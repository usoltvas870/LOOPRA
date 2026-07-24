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
from urllib.parse import urlsplit

from auth import AUTH_SESSION_VALID, inspect_page_authentication, storage_state_diagnostics
from media_acquisition import MediaAcquisitionError, _ffprobe, _safe_component, _sha256
from selection_manifest import read_selection_manifest


SCHEMA_VERSION = "1.0"
ACQUISITION_METHOD = "authenticated_browser_response"
MIN_FILE_BYTES = 1024
DEFAULT_MAX_FILE_BYTES = 8 * 1024 * 1024


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
    page_status: int | None = None
    observed: list[tuple[int, object, dict]] = []
    playwright = browser = context = page = None
    try:
        from playwright.async_api import async_playwright

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=state, locale="ru-RU", viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        def on_response(response) -> None:
            facts = response_facts(response)
            if is_confirmed_media_response(facts, request.maximum_file_bytes):
                observed.append((len(observed), response, facts))

        page.on("response", on_response)
        navigation = await page.goto(candidate.canonical_url, wait_until="domcontentloaded", timeout=45_000)
        page_status = navigation.status if navigation else None
        await page.wait_for_timeout(8_000)
        page_auth = await inspect_page_authentication(page)
        if page_auth.result != AUTH_SESSION_VALID:
            raise MediaAcquisitionError(f"authenticated candidate page unavailable: {page_auth.reason}")
        if not observed:
            raise MediaAcquisitionError("no confirmed browser MP4 response was observed")

        _, response, facts = select_media_response(observed)
        body = await response.body()
        return _persist_capture(
            candidate_root=candidate_root,
            run_root=run_root,
            manifest=manifest,
            candidate=candidate,
            facts=facts,
            body=body,
            page_status=page_status,
            authenticated_session_status=page_auth.result,
            started_at=started_at,
            maximum_file_bytes=request.maximum_file_bytes,
        )
    finally:
        if page is not None:
            await page.close()
        if context is not None:
            await context.close()
        if browser is not None:
            await browser.close()
        if playwright is not None:
            await playwright.stop()


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
        "redacted_reference": f"{parsed.scheme}://{parsed.netloc}{parsed.path}",
        "url_sha256": hashlib.sha256(response.url.encode("utf-8")).hexdigest(),
        "status": response.status,
        "content_type": headers.get("content-type", "").split(";", 1)[0].lower(),
        "content_length": content_length,
        "accept_ranges": headers.get("accept-ranges"),
        "content_range": headers.get("content-range"),
        "resource_type": response.request.resource_type,
    }


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
                     authenticated_session_status, started_at, maximum_file_bytes) -> BrowserMediaCaptureRecord:
    target = candidate_root / "browser_source.mp4"
    target_existed_before_capture = target.exists()
    try:
        _validate_body(body, facts, maximum_file_bytes)
        candidate_root.mkdir(parents=True, exist_ok=True)
        _write_bytes_atomic(target, body)
        validation = _validate_captured_file(target, maximum_file_bytes)
        record = _record(
            manifest, candidate, facts, page_status, authenticated_session_status, started_at,
            "COMPLETED", run_root, target, len(body), validation, [], [],
        )
        _write_json_atomic(candidate_root / "acquisition_record.json", record.to_dict())
        return record
    except (OSError, MediaAcquisitionError) as error:
        if not target_existed_before_capture:
            target.unlink(missing_ok=True)
        failed = _record(
            manifest, candidate, facts, page_status, authenticated_session_status, started_at,
            "FAILED", run_root, None, None, {"valid": False}, [], [str(error)],
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


def _record(manifest, candidate, facts, page_status, session_status, started_at, status, run_root,
            media_path, captured_byte_count, validation, warnings, errors) -> BrowserMediaCaptureRecord:
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
        tool_metadata={"adapter": "browser_response", "browser_context_required": True},
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
