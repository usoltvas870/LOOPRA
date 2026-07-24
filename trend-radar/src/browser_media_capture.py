"""Bounded browser-context capture for one canonical Trend Radar candidate.

The adapter never exports cookies or replays a media URL outside Playwright.
It observes one response while an authenticated browser visits the canonical
candidate page, then persists only redacted technical provenance.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from auth import AUTH_SESSION_VALID, inspect_page_authentication, storage_state_diagnostics
from media_acquisition import MediaAcquisitionError, _ffprobe, _safe_component, _sha256
from selection_manifest import read_selection_manifest


SCHEMA_VERSION = "1.0"
ACQUISITION_METHOD = "authenticated_browser_response"
MIN_FILE_BYTES = 1024
# Rank 2/4 production evidence includes complete TikTok MP4 responses up to
# 35,521,949 bytes. Keep a bounded headroom without admitting unbounded media.
DEFAULT_MAX_FILE_BYTES = 40 * 1024 * 1024
BODY_CAPTURE_TIMEOUT_SECONDS = 30
MAX_BODY_CAPTURE_TASKS = 3


@dataclass(frozen=True)
class BrowserMediaCaptureRequest:
    selection_manifest_path: Path
    cookie_state_path: Path
    output_root: Path
    candidate_id: str | None = None
    maximum_file_bytes: int = DEFAULT_MAX_FILE_BYTES


@dataclass(frozen=True)
class BrowserMediaCaptureRecord:
    schema_version: str
    selection_manifest_reference: str
    selection_manifest_hash: str
    radar_run_id: str
    candidate_video_id: str
    candidate_rank: int
    canonical_page_url: str | None
    acquisition_method: str
    status: str
    authenticated_session_status: str
    browser_page_status: int | None
    media_url_redacted_reference: str | None
    media_url_sha256: str | None
    response_status: int | None
    response_content_type: str | None
    declared_content_length: int | None
    accept_ranges: str | None
    content_range: str | None
    resource_type: str | None
    captured_byte_count: int | None
    local_media_path: str | None
    media_sha256: str | None
    ffprobe_validation: dict
    started_at: str
    completed_at: str
    warnings: list[str]
    errors: list[str]
    tool_metadata: dict

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class MediaResponseObservation:
    """Portable, redacted reason why an observed response was or was not usable."""

    observed_order: int
    redacted_host: str | None
    redacted_path_pattern: str
    url_sha256: str
    query_parameter_names: list[str]
    status: int
    resource_type: str
    content_type: str
    content_length: int | None
    content_range: str | None
    accept_ranges: str | None
    candidate_classification: str
    accepted: bool
    rejection_codes: list[str]
    body_attempted: bool = False
    body_status: str | None = None
    captured_byte_count: int | None = None
    signature_result: str | None = None
    ffprobe_result: dict | None = None
    response_event_at: str | None = None
    response_finished_wait_started_at: str | None = None
    response_finished_wait_completed_at: str | None = None
    body_attempt_started_at: str | None = None
    body_attempt_completed_at: str | None = None
    body_attempt_context: str | None = None
    page_open_at_body_attempt: bool | None = None
    context_open_at_body_attempt: bool | None = None
    from_service_worker: bool | None = None
    exception_type: str | None = None
    redacted_exception_message: str | None = None
    selected_strategy: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def capture_browser_media(request: BrowserMediaCaptureRequest) -> BrowserMediaCaptureRecord:
    """Capture rank 1 (or one explicit manifest candidate) through Playwright."""
    return asyncio.run(_capture_browser_media(request))


async def _capture_browser_media(request: BrowserMediaCaptureRequest) -> BrowserMediaCaptureRecord:
    _validate_request(request)
    manifest = read_selection_manifest(request.selection_manifest_path)
    candidate = _select_candidate(manifest, request.candidate_id)
    run_root = request.output_root / _safe_component(manifest.radar_run_id)
    candidate_root = run_root / _safe_component(candidate.video_id)
    reusable = _read_reusable_record(candidate_root, run_root, manifest.manifest_hash, candidate.video_id, request.maximum_file_bytes)
    if reusable is not None:
        return reusable

    state, diagnostic = storage_state_diagnostics(request.cookie_state_path)
    if state is None:
        raise MediaAcquisitionError(f"authenticated browser session unavailable: {diagnostic.reason}")

    started_at = _utc_iso()
    playwright = browser = context = page = None
    try:
        from playwright.async_api import async_playwright

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=state, locale="ru-RU", viewport={"width": 1280, "height": 800}
        )
        return await capture_browser_media_in_context(request, manifest, candidate, context, started_at)
    finally:
        if context is not None:
            await context.close()
        if browser is not None:
            await browser.close()
        if playwright is not None:
            await playwright.stop()


async def capture_browser_media_in_context(
    request: BrowserMediaCaptureRequest, manifest, candidate, context, started_at: str | None = None
) -> BrowserMediaCaptureRecord:
    """Capture one candidate using an already authenticated context.

    A fresh page is deliberately created and closed for every candidate so
    response listeners cannot cross candidate boundaries.
    """
    run_root = request.output_root / _safe_component(manifest.radar_run_id)
    candidate_root = run_root / _safe_component(candidate.video_id)
    started_at = started_at or _utc_iso()
    page = None
    page_status: int | None = None
    observed: list[tuple[int, object, dict]] = []
    body_tasks: list[tuple[int, object, dict, asyncio.Task]] = []
    observations: list[MediaResponseObservation] = []
    page_diagnostics: dict = {}
    on_response = None
    try:
        page = await context.new_page()

        def on_response(response) -> None:
            facts = response_facts(response)
            if is_potential_media_response(facts):
                observation = classify_media_response(facts, len(observations), request.maximum_file_bytes)
                observations.append(observation)
            if is_confirmed_media_response(facts, request.maximum_file_bytes):
                observed_order = len(observed)
                observed.append((observed_order, response, facts))
                if len(body_tasks) < MAX_BODY_CAPTURE_TASKS:
                    body_tasks.append((
                        observed_order,
                        response,
                        facts,
                        asyncio.create_task(_capture_response_body(response, page)),
                    ))

        page.on("response", on_response)
        navigation = await page.goto(candidate.canonical_url, wait_until="domcontentloaded", timeout=45_000)
        page_status = navigation.status if navigation else None
        await page.wait_for_timeout(8_000)
        page_auth = await inspect_page_authentication(page)
        page_diagnostics = await page_player_diagnostics(page)
        if page_auth.result != AUTH_SESSION_VALID:
            raise MediaAcquisitionError(f"authenticated candidate page unavailable: {page_auth.reason}")
        if not observed:
            if page_diagnostics["video_element_count"]:
                page_diagnostics["activation_attempted"] = await activate_first_video_once(page)
                if page_diagnostics["activation_attempted"]:
                    await page.wait_for_timeout(3_000)
            if not observed:
                return _persist_failed_capture(
                    candidate_root, run_root, manifest, candidate, page_status, page_auth.result,
                    started_at, observations, page_diagnostics,
                    "no confirmed browser MP4 response was observed",
                )
        body_results = await _await_body_tasks(body_tasks)
        _apply_body_diagnostics(observations, body_results)
        selected = _select_successful_body(observed, body_results)
        if selected is None:
            return _persist_failed_capture(
                candidate_root, run_root, manifest, candidate, page_status, page_auth.result,
                started_at, observations, page_diagnostics, "selected browser response body unavailable",
            )
        _, facts, body = selected
        return _persist_capture(
            candidate_root=candidate_root, run_root=run_root, manifest=manifest, candidate=candidate,
            facts=facts, body=body, page_status=page_status,
            authenticated_session_status=page_auth.result, started_at=started_at,
            maximum_file_bytes=request.maximum_file_bytes,
            observations=observations, page_diagnostics=page_diagnostics,
        )
    finally:
        await _await_body_tasks(body_tasks)
        if page is not None and on_response is not None and hasattr(page, "off"):
            page.off("response", on_response)
        if page is not None:
            await page.close()


def response_facts(response) -> dict:
    """Return allowlisted response metadata; the signed query is never retained."""
    headers = response.headers
    parsed = urlsplit(response.url)
    length_text = headers.get("content-length")
    try:
        content_length = int(length_text) if length_text else None
    except ValueError:
        content_length = None
    return {
        "host": parsed.hostname,
        "path": parsed.path,
        "scheme": parsed.scheme,
        "has_url_credentials": bool(parsed.username or parsed.password),
        "redacted_reference": f"{parsed.scheme}://{parsed.hostname or ''}{parsed.path}",
        "redacted_host": parsed.hostname,
        "redacted_path_pattern": parsed.path,
        "url_sha256": hashlib.sha256(response.url.encode("utf-8")).hexdigest(),
        "query_parameter_names": sorted({name for name, _ in parse_qsl(parsed.query, keep_blank_values=True)}),
        "status": response.status,
        "content_type": headers.get("content-type", "").split(";", 1)[0].lower(),
        "content_length": content_length,
        "accept_ranges": headers.get("accept-ranges"),
        "content_range": headers.get("content-range"),
        "resource_type": response.request.resource_type,
        "from_service_worker": bool(getattr(response, "from_service_worker", False)),
    }


async def _capture_response_body(response, page) -> dict:
    """Read a selected response before its page can be closed.

    This deliberately keeps only a bounded body in memory.  It records no URL,
    headers, body bytes, or exception stack trace in the diagnostic result.
    """
    result = {
        "body": None,
        "body_status": "unavailable",
        "response_event_at": _utc_iso(),
        "response_finished_wait_started_at": _utc_iso(),
        "response_finished_wait_completed_at": None,
        "body_attempt_started_at": None,
        "body_attempt_completed_at": None,
        "body_attempt_context": "response_event_task",
        "page_open_at_body_attempt": None,
        "context_open_at_body_attempt": None,
        "exception_type": None,
        "redacted_exception_message": None,
        "selected_strategy": "immediate_response_event",
    }
    try:
        await asyncio.wait_for(response.finished(), timeout=BODY_CAPTURE_TIMEOUT_SECONDS)
        result["response_finished_wait_completed_at"] = _utc_iso()
        result["body_attempt_started_at"] = _utc_iso()
        result["page_open_at_body_attempt"] = not page.is_closed()
        # The caller owns the context and does not close it until all tasks end.
        result["context_open_at_body_attempt"] = True
        result["body"] = await asyncio.wait_for(response.body(), timeout=BODY_CAPTURE_TIMEOUT_SECONDS)
        result["body_status"] = "captured"
    except Exception as error:
        result["exception_type"] = type(error).__name__
        if isinstance(error, TimeoutError) and result["body_attempt_started_at"] is None:
            result["body_status"] = "response_finished_timeout"
            result["redacted_exception_message"] = (
                f"response finished wait exceeded {BODY_CAPTURE_TIMEOUT_SECONDS} seconds"
            )
        else:
            result["redacted_exception_message"] = _redact_exception_message(str(error))
    finally:
        result["body_attempt_completed_at"] = _utc_iso()
    return result


async def _await_body_tasks(body_tasks: list[tuple[int, object, dict, asyncio.Task]]) -> dict[str, dict]:
    """Await all bounded lifecycle tasks so their failures cannot be lost."""
    results: dict[str, dict] = {}
    for _, _, facts, task in body_tasks:
        try:
            results[facts["url_sha256"]] = await task
        except asyncio.CancelledError:
            results[facts["url_sha256"]] = {
                "body": None, "body_status": "unavailable", "exception_type": "CancelledError",
                "redacted_exception_message": "body capture task cancelled",
                "selected_strategy": "immediate_response_event",
            }
    return results


def _apply_body_diagnostics(observations: list[MediaResponseObservation], body_results: dict[str, dict]) -> None:
    for index, observation in enumerate(observations):
        result = body_results.get(observation.url_sha256)
        if result is None:
            continue
        captured = result.get("body")
        unavailable = captured is None
        rejection_codes = [*observation.rejection_codes, "BODY_UNAVAILABLE"] if unavailable else observation.rejection_codes
        if result["body_status"] == "response_finished_timeout":
            rejection_codes.append("RESPONSE_FINISHED_TIMEOUT")
        observations[index] = MediaResponseObservation(**{
            **observation.to_dict(),
            "body_attempted": True,
            "body_status": result["body_status"],
            "captured_byte_count": len(captured) if captured is not None else None,
            "candidate_classification": "selected_body_unavailable" if unavailable else observation.candidate_classification,
            "rejection_codes": rejection_codes,
            **{key: result.get(key) for key in (
                "response_event_at", "response_finished_wait_started_at", "response_finished_wait_completed_at",
                "body_attempt_started_at", "body_attempt_completed_at", "body_attempt_context",
                "page_open_at_body_attempt", "context_open_at_body_attempt", "exception_type",
                "redacted_exception_message", "selected_strategy",
            )},
        })


def _select_successful_body(observed: list[tuple[int, object, dict]], body_results: dict[str, dict]):
    for _, _, facts in sorted(observed, key=lambda item: item[0]):
        body = body_results.get(facts["url_sha256"], {}).get("body")
        if body is not None:
            return 0, facts, body
    return None


def _redact_exception_message(message: str) -> str:
    """Keep a concise exception reason without retaining URLs or secret-like values."""
    message = message.replace("\r", " ").replace("\n", " ")
    for marker in ("http://", "https://"):
        start = message.find(marker)
        if start >= 0:
            end = message.find(" ", start)
            message = f"{message[:start]}<redacted-url>{'' if end < 0 else message[end:]}"
    return message[:240]


def is_potential_media_response(facts: dict) -> bool:
    """Keep diagnostics bounded to media-shaped responses, never response bodies."""
    return bool(
        facts["resource_type"] == "media"
        or facts["content_type"].startswith("video/")
        or facts["content_type"] == "application/octet-stream"
        or "/video/" in facts["path"]
    )


def classify_media_response(facts: dict, observed_order: int, maximum_file_bytes: int) -> MediaResponseObservation:
    rejection_codes: list[str] = []
    host = facts["host"]
    if facts["scheme"] != "https":
        rejection_codes.append("UNSUPPORTED_SCHEME")
    if facts["has_url_credentials"]:
        rejection_codes.append("URL_CREDENTIALS_UNSUPPORTED")
    if not host or not (host == "tiktok.com" or host.endswith(".tiktok.com")):
        rejection_codes.append("UNSUPPORTED_HOST")
    if facts["status"] == 206:
        rejection_codes.append("RANGE_RESPONSE_UNSUPPORTED")
    elif facts["status"] != 200:
        rejection_codes.append("UNSUPPORTED_STATUS")
    if facts["content_type"] == "application/octet-stream":
        rejection_codes.append("OCTET_STREAM_WITHOUT_MEDIA_EVIDENCE")
    elif facts["content_type"] != "video/mp4":
        rejection_codes.append("NON_VIDEO_CONTENT_TYPE")
    if "/video/" not in facts["path"]:
        rejection_codes.append("NO_VIDEO_STREAM")
    if facts["content_length"] is None:
        rejection_codes.append("MISSING_CONTENT_LENGTH")
    elif facts["content_length"] < MIN_FILE_BYTES:
        rejection_codes.append("SIZE_BELOW_MINIMUM")
    elif facts["content_length"] > maximum_file_bytes:
        rejection_codes.append("SIZE_ABOVE_LIMIT")
    accepted = not rejection_codes
    return MediaResponseObservation(
        observed_order=observed_order, redacted_host=facts["redacted_host"],
        redacted_path_pattern=facts["redacted_path_pattern"], url_sha256=facts["url_sha256"],
        query_parameter_names=facts["query_parameter_names"], status=facts["status"],
        resource_type=facts["resource_type"], content_type=facts["content_type"],
        content_length=facts["content_length"], content_range=facts["content_range"],
        accept_ranges=facts["accept_ranges"], candidate_classification="accepted_media" if accepted else "rejected_media",
        accepted=accepted, rejection_codes=rejection_codes,
        from_service_worker=facts.get("from_service_worker"),
    )


async def page_player_diagnostics(page) -> dict:
    """Read browser-bound player facts without retaining player URLs or page HTML."""
    return await page.evaluate("""() => {
        const videos = [...document.querySelectorAll('video')];
        const sourceKinds = videos.map((video) => {
            const source = video.currentSrc || video.src || '';
            return source.startsWith('blob:') ? 'blob' : source ? 'network' : 'empty';
        });
        return {
            video_element_count: videos.length,
            player_source_kinds: sourceKinds,
            source_element_count: videos.reduce((count, video) => count + video.querySelectorAll('source').length, 0),
            ready_states: videos.map((video) => video.readyState),
            network_states: videos.map((video) => video.networkState),
            durations: videos.map((video) => Number.isFinite(video.duration) ? video.duration : null),
            dimensions: videos.map((video) => [video.videoWidth, video.videoHeight]),
            activation_attempted: false,
        };
    }""")


async def activate_first_video_once(page) -> bool:
    return await page.evaluate("""async () => {
        const video = document.querySelector('video');
        if (!video) return false;
        video.muted = true;
        try { await video.play(); } catch (_) { }
        return true;
    }""")


def is_confirmed_media_response(facts: dict, maximum_file_bytes: int) -> bool:
    host = facts["host"]
    return bool(
        facts["status"] == 200
        and facts["content_type"] == "video/mp4"
        and host
        and (host == "tiktok.com" or host.endswith(".tiktok.com"))
        and "/video/" in facts["path"]
        and facts["content_length"] is not None
        and MIN_FILE_BYTES <= facts["content_length"] <= maximum_file_bytes
    )


def select_media_response(observed: list[tuple[int, object, dict]]) -> tuple[int, object, dict]:
    """Prefer a complete HTTP 200 response and preserve network observation order."""
    return sorted(observed, key=lambda item: (item[2]["status"] != 200, item[0]))[0]


def _persist_capture(*, candidate_root, run_root, manifest, candidate, facts, body, page_status,
                     authenticated_session_status, started_at, maximum_file_bytes,
                     observations: list[MediaResponseObservation] | None = None,
                     page_diagnostics: dict | None = None) -> BrowserMediaCaptureRecord:
    target = candidate_root / "browser_source.mp4"
    target_existed_before_capture = target.exists()
    try:
        _validate_body(body, facts, maximum_file_bytes)
        candidate_root.mkdir(parents=True, exist_ok=True)
        _write_bytes_atomic(target, body)
        validation = _validate_captured_file(target, maximum_file_bytes)
        record = _record(
            manifest, candidate, facts, page_status, authenticated_session_status, started_at,
            "COMPLETED", run_root, target, len(body), validation, [], [], observations, page_diagnostics,
        )
        _write_json_atomic(candidate_root / "acquisition_record.json", record.to_dict())
        return record
    except (OSError, MediaAcquisitionError) as error:
        if not target_existed_before_capture:
            target.unlink(missing_ok=True)
        failed = _record(
            manifest, candidate, facts, page_status, authenticated_session_status, started_at,
            "FAILED", run_root, None, None, {"valid": False}, [], [str(error)], observations, page_diagnostics,
        )
        _write_json_atomic(candidate_root / "acquisition_record.json", failed.to_dict())
        return failed


def _validate_request(request: BrowserMediaCaptureRequest) -> None:
    if request.maximum_file_bytes < MIN_FILE_BYTES:
        raise MediaAcquisitionError("maximum_file_bytes is below the minimum media size")


def _select_candidate(manifest, candidate_id: str | None):
    if candidate_id is None:
        return manifest.candidates[0]
    for candidate in manifest.candidates:
        if candidate.video_id == candidate_id:
            return candidate
    raise MediaAcquisitionError(f"unknown candidate ID: {candidate_id}")


def _validate_body(body: bytes, facts: dict, maximum_file_bytes: int) -> None:
    if not body:
        raise MediaAcquisitionError("browser response body is empty")
    if len(body) < MIN_FILE_BYTES:
        raise MediaAcquisitionError("browser response body is too small")
    if len(body) > maximum_file_bytes:
        raise MediaAcquisitionError("browser response body exceeds maximum_file_bytes")
    if facts["content_length"] != len(body):
        raise MediaAcquisitionError("captured byte count does not match Content-Length")
    head = body[:512].lower()
    if b"<html" in head or b"<!doctype html" in head:
        raise MediaAcquisitionError("browser response body appears to be HTML")
    if b"ftyp" not in body[:32]:
        raise MediaAcquisitionError("browser response body does not have an MP4 container signature")


def _validate_captured_file(path: Path, maximum_file_bytes: int) -> dict:
    size = path.stat().st_size
    if size > maximum_file_bytes:
        raise MediaAcquisitionError("captured media exceeds maximum_file_bytes")
    probe = _ffprobe(path)
    if not probe["valid"]:
        raise MediaAcquisitionError(probe["error"])
    return {"size": size, "sha256": _sha256(path), "ffprobe": probe}


def _write_bytes_atomic(target: Path, body: bytes) -> None:
    if target.exists():
        raise MediaAcquisitionError(f"refusing to overwrite existing media: {target}")
    temporary = target.with_suffix(target.suffix + ".part")
    try:
        with temporary.open("xb") as output:
            output.write(body)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def _read_reusable_record(candidate_root: Path, run_root: Path, manifest_hash: str, video_id: str,
                          maximum_file_bytes: int) -> BrowserMediaCaptureRecord | None:
    record_path = candidate_root / "acquisition_record.json"
    if not record_path.is_file():
        return None
    try:
        record = BrowserMediaCaptureRecord(**json.loads(record_path.read_text(encoding="utf-8")))
        if (record.status not in {"COMPLETED", "REUSED"} or record.acquisition_method != ACQUISITION_METHOD
                or record.selection_manifest_hash != manifest_hash or record.candidate_video_id != video_id
                or not record.local_media_path):
            return None
        media_path = _contained_path(run_root, record.local_media_path)
        validation = _validate_captured_file(media_path, maximum_file_bytes)
        if validation["sha256"] != record.media_sha256:
            return None
        return BrowserMediaCaptureRecord(**{**record.to_dict(), "status": "REUSED"})
    except (OSError, ValueError, TypeError, json.JSONDecodeError, MediaAcquisitionError):
        return None


def _persist_failed_capture(candidate_root, run_root, manifest, candidate, page_status, session_status,
                            started_at, observations, page_diagnostics, error) -> BrowserMediaCaptureRecord:
    record = _record(
        manifest, candidate, {}, page_status, session_status, started_at, "FAILED", run_root,
        None, None, {"valid": False}, [], [error], observations, page_diagnostics,
    )
    _write_json_atomic(candidate_root / "acquisition_record.json", record.to_dict())
    return record


def _record(manifest, candidate, facts, page_status, session_status, started_at, status, run_root,
            media_path, captured_byte_count, validation, warnings, errors,
            observations: list[MediaResponseObservation] | None = None,
            page_diagnostics: dict | None = None) -> BrowserMediaCaptureRecord:
    relative_path = str(media_path.relative_to(run_root)).replace("\\", "/") if media_path else None
    return BrowserMediaCaptureRecord(
        schema_version=SCHEMA_VERSION,
        selection_manifest_reference=manifest.radar_run_reference,
        selection_manifest_hash=manifest.manifest_hash,
        radar_run_id=manifest.radar_run_id,
        candidate_video_id=candidate.video_id,
        candidate_rank=candidate.rank,
        canonical_page_url=candidate.canonical_url,
        acquisition_method=ACQUISITION_METHOD,
        status=status,
        authenticated_session_status=session_status,
        browser_page_status=page_status,
        media_url_redacted_reference=facts.get("redacted_reference"),
        media_url_sha256=facts.get("url_sha256"),
        response_status=facts.get("status"),
        response_content_type=facts.get("content_type"),
        declared_content_length=facts.get("content_length"),
        accept_ranges=facts.get("accept_ranges"),
        content_range=facts.get("content_range"),
        resource_type=facts.get("resource_type"),
        captured_byte_count=captured_byte_count,
        local_media_path=relative_path,
        media_sha256=validation.get("sha256"),
        ffprobe_validation=validation.get("ffprobe", {"valid": False}),
        started_at=started_at,
        completed_at=_utc_iso(),
        warnings=warnings,
        errors=errors,
        tool_metadata={
            "adapter": "browser_response", "browser_context_required": True,
            "page_diagnostics": page_diagnostics or {},
            "response_observations": [observation.to_dict() for observation in observations or []],
        },
    )


def _contained_path(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    if root.resolve() not in candidate.parents:
        raise MediaAcquisitionError("record local_media_path escapes acquisition root")
    return candidate


def _write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as output:
        json.dump(payload, output, ensure_ascii=False, indent=2)
        output.write("\n")
        temporary = Path(output.name)
    os.replace(temporary, path)


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
