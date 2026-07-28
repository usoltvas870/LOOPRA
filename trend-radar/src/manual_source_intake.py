"""LOOPRA 0.5 manual-first source intake.

This module orchestrates existing deterministic acquisition and evidence tools.
It deliberately does not search, rank, generate scripts, render, or publish.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from browser_media_capture import (
    BrowserMediaCaptureRequest,
    capture_browser_media_in_context,
)
from format_inspection import inspect as inspect_media
from media_acquisition import (
    DEFAULT_MAX_FILE_BYTES,
    MediaAcquisitionError,
    _copy_atomic,
    _safe_component,
    _sha256,
    _validate_local_file,
)
from ocr_evidence import OcrRunRequest, run_ocr_evidence
from selection_manifest import build_selection_manifest, write_selection_manifest
from transcription_evidence import TranscriptionRunRequest, run_transcription_evidence


SCHEMA_VERSION = "1.0"
INTAKE_VERSION = "0.5"
SUPPORTED_EXTENSIONS = {".mp4"}
DEFAULT_LINKS_REFERENCE = "input/selected_sources/selected_links.txt"
DEFAULT_MEDIA_REFERENCE = "input/selected_sources/media"
DEFAULT_OUTPUT_REFERENCE = "output/manual_intake"
SECRET_KEYS = {"authorization", "cookie", "cookies", "api_key", "token"}


class ManualIntakeError(ValueError):
    """Raised when the bounded manual-intake contract is invalid."""


@dataclass(frozen=True)
class ParsedLink:
    original_order: int
    raw_value: str
    normalized_url: str | None
    video_id: str | None
    status: str
    failure_code: str | None = None


@dataclass(frozen=True)
class ManualIntakePlan:
    intake_id: str
    identity_hash: str
    project_id: str
    links_file_reference: str
    media_directory_reference: str
    parsed_links: tuple[ParsedLink, ...]
    local_media: tuple[Path, ...]
    duplicate_input_count: int


@dataclass(frozen=True)
class LoopraManualSourceItem:
    schema_version: str
    item_id: str
    created_at: str
    intake_reference: str
    intake_hash: str
    input_type: str
    source_url: str | None
    source_filename: str | None
    normalized_source_identity: str
    original_input_order: int
    local_media_reference: str | None
    local_media_hash: str | None
    media_type: str | None
    duration: float | None
    dimensions: dict[str, int] | None
    video_codec: str | None
    audio_codec: str | None
    audio_presence: bool | None
    acquisition_status: str
    inspection_reference: str | None
    inspection_hash: str | None
    transcription_reference: str | None
    transcription_hash: str | None
    ocr_reference: str | None
    ocr_hash: str | None
    transcript_status: str
    ocr_status: str
    evidence_warnings: list[str]
    processing_status: str
    failure_code: str | None
    output_folder_reference: str | None
    content_hash: str
    reuse_metadata: dict[str, Any]


@dataclass(frozen=True)
class LoopraManualSourceIntake:
    schema_version: str
    intake_id: str
    intake_version: str
    project_id: str
    created_at: str
    links_file_reference: str
    media_directory_reference: str
    parsed_link_count: int
    local_media_count: int
    duplicate_input_count: int
    accepted_source_count: int
    failed_source_count: int
    item_references: list[dict[str, Any]]
    output_package_reference: str
    output_package_hash: str
    provider_calls: int
    search_calls: int
    script_calls: int
    image_calls: int
    reuse_metadata: dict[str, Any]
    content_hash: str
    status: str


@dataclass(frozen=True)
class ManualIntakeServices:
    validate_media: Callable[[Path, int], dict[str, Any]] = _validate_local_file
    copy_media: Callable[[Path, Path], None] = _copy_atomic
    acquire_link: Callable[..., dict[str, Any]] | None = None
    inspect: Callable[[Path, Path, str, str | None], dict[str, Any]] = inspect_media
    transcribe: Callable[..., dict[str, Any]] = run_transcription_evidence
    ocr: Callable[..., dict[str, Any]] = run_ocr_evidence


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _serialize(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash_payload(value: Any) -> str:
    return hashlib.sha256(_serialize(value).encode("utf-8")).hexdigest()


def _with_hash(value: dict[str, Any]) -> dict[str, Any]:
    payload = {key: item for key, item in value.items() if key != "content_hash"}
    return payload | {"content_hash": _hash_payload(payload)}


def _portable(path: Path, repository_root: Path) -> str:
    try:
        return path.resolve().relative_to(repository_root.resolve()).as_posix()
    except ValueError as error:
        raise ManualIntakeError(f"path must be inside repository root: {path}") from error


def normalize_tiktok_url(value: str) -> tuple[str, str | None]:
    """Validate and normalize one public TikTok video URL."""
    parsed = urlsplit(value.strip())
    host = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme not in {"http", "https"} or host not in {
        "tiktok.com", "www.tiktok.com", "m.tiktok.com", "vm.tiktok.com", "vt.tiktok.com",
    }:
        raise ManualIntakeError("INVALID_URL")
    if parsed.username or parsed.password:
        raise ManualIntakeError("INVALID_URL")
    path = re.sub(r"/{2,}", "/", parsed.path).rstrip("/") or "/"
    match = re.search(r"/video/(\d+)(?:/|$)", path)
    video_id = match.group(1) if match else None
    if host in {"tiktok.com", "www.tiktok.com", "m.tiktok.com"} and video_id is None:
        raise ManualIntakeError("INVALID_URL")
    query = urlencode(sorted((key, item) for key, item in parse_qsl(parsed.query) if key.lower() not in {
        "is_copy_url", "is_from_webapp", "sender_device", "sender_web_id", "utm_source", "utm_medium", "utm_campaign",
    }))
    normalized_host = "www.tiktok.com" if video_id else host
    normalized_path = f"/@source/video/{video_id}" if video_id else path
    return urlunsplit(("https", normalized_host, normalized_path, query, "")), video_id


def parse_links_file(path: Path) -> tuple[list[ParsedLink], int]:
    if not path.exists():
        return [], 0
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError as error:
        raise ManualIntakeError("selected_links.txt must be UTF-8") from error
    parsed: list[ParsedLink] = []
    seen: set[str] = set()
    duplicates = 0
    order = 0
    for raw in lines:
        value = raw.strip()
        if not value or value.startswith("#"):
            continue
        order += 1
        try:
            normalized, video_id = normalize_tiktok_url(value)
        except ManualIntakeError:
            parsed.append(ParsedLink(order, value, None, None, "INVALID_URL", "INVALID_URL"))
            continue
        identity = f"tiktok:{video_id}" if video_id else f"url:{normalized}"
        if identity in seen:
            duplicates += 1
            parsed.append(ParsedLink(order, value, normalized, video_id, "DUPLICATE_INPUT", "DUPLICATE_INPUT"))
            continue
        seen.add(identity)
        parsed.append(ParsedLink(order, value, normalized, video_id, "READY"))
    return parsed, duplicates


def discover_local_media(media_dir: Path) -> list[Path]:
    if not media_dir.exists():
        return []
    if not media_dir.is_dir():
        raise ManualIntakeError("media input must be a directory")
    return sorted(
        (path for path in media_dir.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS and not path.name.lower().endswith(".part")),
        key=lambda path: path.name.casefold(),
    )


def build_plan(*, project_id: str, links_file: Path, media_dir: Path, output_root: Path,
               repository_root: Path, limit: int | None = None) -> ManualIntakePlan:
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", project_id):
        raise ManualIntakeError("invalid project ID")
    if limit is not None and limit <= 0:
        raise ManualIntakeError("limit must be positive")
    links, duplicate_count = parse_links_file(links_file)
    media = discover_local_media(media_dir)
    actionable = [link for link in links if link.status != "DUPLICATE_INPUT"]
    combined: list[tuple[str, Any]] = [("link", link) for link in actionable] + [("local", path) for path in media]
    if limit is not None:
        combined = combined[:limit]
        allowed_links = {item.original_order for kind, item in combined if kind == "link"}
        allowed_media = {item for kind, item in combined if kind == "local"}
        links = [link for link in links if link.status == "DUPLICATE_INPUT" or link.original_order in allowed_links]
        media = [path for path in media if path in allowed_media]
    identity_inputs = []
    for link in links:
        identity_inputs.append({"type": "link", "order": link.original_order, "identity": link.normalized_url or _hash_payload(link.raw_value), "status": link.status})
    for path in media:
        identity_inputs.append({"type": "local", "name": path.name.casefold(), "sha256": _sha256(path)})
    identity = _hash_payload({"schema_version": SCHEMA_VERSION, "project_id": project_id, "inputs": identity_inputs})
    return ManualIntakePlan(
        intake_id=f"manual-{project_id}-{identity[:16]}", identity_hash=identity, project_id=project_id,
        links_file_reference=_portable(links_file, repository_root),
        media_directory_reference=_portable(media_dir, repository_root),
        parsed_links=tuple(links), local_media=tuple(media), duplicate_input_count=duplicate_count,
    )


def _candidate(item_id: str, source_url: str | None) -> dict[str, Any]:
    return {
        "video_id": item_id, "author_username": None, "source_type": "manual_owner_selection",
        "source_value": "manual_input", "url": source_url, "caption": None, "views": None,
        "likes": None, "comments": None, "shares": None, "author_followers": None,
        "published_at": None, "collected_at": None, "final_score": None, "reach_score": None,
        "engagement_score": None, "freshness_score": None, "momentum_proxy": None,
        "data_confidence": "MANUAL_INPUT", "identity_confidence": "HIGH",
        "classification": "MANUAL_OWNER_SELECTED", "provenance": {
            "primary_source_type": "manual_owner_selection", "primary_source_value": "manual_input",
        },
    }


def _acquisition_record(item_id: str, run_root: Path, media: Path, facts: dict[str, Any],
                        source_url: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": "1.0", "candidate_video_id": item_id, "rank": 1,
        "source_page_url": source_url, "acquisition_method": "operator_provided_local_file",
        "status": "COMPLETED", "started_at": _utc_now(), "completed_at": _utc_now(),
        "resolved_media_reference": None, "response_content_type": None,
        "content_length": media.stat().st_size, "local_media_path": media.relative_to(run_root).as_posix(),
        "media_sha256": facts["sha256"], "sha256": facts["sha256"],
        "ffprobe_validation": facts["ffprobe"], "reusable": True, "warnings": [], "errors": [],
        "tool_metadata": {"network_calls": 0, "credentials_required": False},
    }


def _write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as stream:
        stream.write(data)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


async def _capture_guest(request: BrowserMediaCaptureRequest, manifest, candidate) -> dict[str, Any]:
    playwright = browser = context = None
    try:
        from playwright.async_api import async_playwright

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(locale="ru-RU", viewport={"width": 1280, "height": 800})
        return (await capture_browser_media_in_context(request, manifest, candidate, context)).to_dict()
    finally:
        if context is not None:
            await context.close()
        if browser is not None:
            await browser.close()
        if playwright is not None:
            await playwright.stop()


def acquire_public_link(*, manifest_path: Path, acquisition_output_root: Path,
                        candidate_id: str) -> dict[str, Any]:
    """Use the canonical per-item capture in a fresh guest browser context."""
    from selection_manifest import read_selection_manifest

    manifest = read_selection_manifest(manifest_path)
    candidate = next(item for item in manifest.candidates if item.video_id == candidate_id)
    request = BrowserMediaCaptureRequest(
        selection_manifest_path=manifest_path,
        cookie_state_path=acquisition_output_root / ".guest-no-session.json",
        output_root=acquisition_output_root, candidate_id=candidate_id,
    )
    return asyncio.run(_capture_guest(request, manifest, candidate))


def _media_facts(probe: dict[str, Any]) -> dict[str, Any]:
    if "streams" not in probe:
        return {
            "duration": probe.get("duration_seconds"),
            "dimensions": {"width": int(probe["width"]), "height": int(probe["height"])} if probe.get("width") and probe.get("height") else None,
            "video_codec": probe.get("video_codec"), "audio_codec": probe.get("audio_codec"),
            "audio_presence": bool(probe.get("audio_stream_present")),
        }
    video = next((stream for stream in probe.get("streams", []) if stream.get("codec_type") == "video"), {})
    audio = next((stream for stream in probe.get("streams", []) if stream.get("codec_type") == "audio"), None)
    duration = probe.get("format", {}).get("duration") or video.get("duration")
    return {
        "duration": float(duration) if duration is not None else None,
        "dimensions": {"width": int(video["width"]), "height": int(video["height"])} if video.get("width") and video.get("height") else None,
        "video_codec": video.get("codec_name"), "audio_codec": audio.get("codec_name") if audio else None,
        "audio_presence": audio is not None,
    }


def _transcript_status(result: dict[str, Any], audio_present: bool) -> str:
    status = result.get("status")
    if not audio_present or status == "COMPLETED_NO_AUDIO":
        return "NO_AUDIO"
    if status == "COMPLETED":
        segments = result.get("segments", [])
        return "AUTHOR_SPEECH_USABLE" if len(" ".join(item.get("normalized_text", "") for item in segments).split()) >= 3 else "MANUAL_REVIEW_REQUIRED"
    if status == "COMPLETED_NO_SPEECH":
        return "NONSPEECH"
    return "TRANSCRIPTION_FAILED"


def _ocr_status(result: dict[str, Any]) -> str:
    if result.get("status") == "FAILED":
        return "OCR_FAILED"
    events = result.get("text_events", [])
    text = " ".join(item.get("text", "") for item in events).strip()
    if not text:
        return "EMPTY"
    return "READABLE" if result.get("status") == "COMPLETED" else "PARTIALLY_READABLE"


def _build_transcript_text(status: str, result: dict[str, Any]) -> str:
    lines = [f"Статус: {status}", f"Язык: {result.get('language') or 'не определён'}", "", "Полная транскрипция:"]
    segments = result.get("segments", [])
    if not segments:
        reason = "; ".join(result.get("errors", [])) or result.get("first_spoken_words_reason") or "надёжная речь не обнаружена"
        lines.append(f"Транскрипция отсутствует: {reason}.")
    else:
        lines.extend(f"[{item.get('start_seconds', 0):.2f}–{item.get('end_seconds', 0):.2f}] {item.get('normalized_text', '')}" for item in segments)
    return "\n".join(lines)


def _build_screen_text(status: str, result: dict[str, Any]) -> str:
    lines = [f"Статус: {status}", "", "Текст на экране:"]
    events = result.get("text_events", [])
    if events:
        lines.extend(f"[{item.get('first_seen_at_sec', 0):.2f}] {item.get('text', '')}" for item in events)
    else:
        reason = "; ".join(result.get("errors", [])) or "читаемый текст не обнаружен"
        lines.append(f"OCR evidence отсутствует или пуст: {reason}.")
    if status in {"PARTIALLY_READABLE", "GARBLED", "OCR_FAILED"}:
        lines.extend(["", "MANUAL_TEXT_CHECK: проверьте текст непосредственно в source.mp4."])
    return "\n".join(lines)


def _handoff(project_id: str, source_ref: str, facts: dict[str, Any], transcript_status: str,
             transcript: str, ocr_status: str, screen_text: str, warnings: list[str]) -> str:
    return f"""# GPT handoff — {project_id.upper()}

Источник: `{source_ref}`

## Evidence

- Duration: {facts.get('duration')}
- Dimensions: {facts.get('dimensions')}
- Video codec: {facts.get('video_codec')}
- Audio: {facts.get('audio_presence')} ({facts.get('audio_codec')})
- Transcript status: {transcript_status}
- OCR status: {ocr_status}
- Warnings: {', '.join(warnings) if warnings else 'нет'}

### Transcript

{transcript}

### On-screen text

{screen_text}

## Обязательный двухэтапный порядок

### ЭТАП 1 — ПОНИМАНИЕ ИСТОЧНИКА

Посмотри само приложенное видео. Опиши буквально, что происходит. Отдели речь автора,
текст на экране, музыку и визуальные события. Определи фактический hook и механизм
удержания внимания. Объясни, почему ролик может работать. Не придумывай содержание при
недостатке evidence. Сначала покажи анализ владельцу и дождись подтверждения.

### ЭТАП 2 — АДАПТАЦИЯ NURA

Только после подтверждения понимания владельцем выдели переносимый механизм. Не копируй
формулировки, персонажа, монтаж, музыку или footage. Создай source-specific сценарий NURA
с hook, development, turn, small next step и final thought. Сохрани спокойный, ясный,
поддерживающий голос NURA; не используй диагнозы, терапевтические обещания и предсказания.
Дай clean text для HeyGen и, только если нужно, предложи visual strategy/image prompt.

LOOPRA передаёт технические evidence, но не утверждает, что уже поняла смысл ролика.
"""


def _package_hash(root: Path) -> str:
    entries = []
    for path in sorted(item for item in root.rglob("*") if item.is_file() and item.name != "00_MANIFEST.json"):
        entries.append({"path": path.relative_to(root).as_posix(), "sha256": _sha256(path)})
    return _hash_payload(entries)


def _safe_public_error(error: Exception) -> str:
    text = str(error)
    text = re.sub(r"https?://\S+", "[URL_REDACTED]", text)
    return text[:500]


def _validate_no_secrets(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in SECRET_KEYS:
                raise ManualIntakeError(f"secret field is forbidden: {key}")
            _validate_no_secrets(item)
    elif isinstance(value, list):
        for item in value:
            _validate_no_secrets(item)


def _existing_package(package: Path, intake_id: str) -> dict[str, Any] | None:
    manifest_path = package / "00_MANIFEST.json"
    if not manifest_path.is_file():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        content_hash = manifest.pop("content_hash")
        if content_hash != _hash_payload(manifest) or manifest.get("intake_id") != intake_id:
            return None
        if manifest.get("output_package_hash") != _package_hash(package):
            return None
        return manifest | {"content_hash": content_hash}
    except (OSError, KeyError, json.JSONDecodeError):
        return None


def _overview(manifest: dict[str, Any], items: list[dict[str, Any]]) -> str:
    item_lines = [f"- `{item.get('output_folder_reference') or item['item_id']}` — {item['processing_status']}" for item in items]
    return f"""# LOOPRA 0.5 — ручной приём источников

- Intake ID: `{manifest['intake_id']}`
- Project: `{manifest['project_id']}`
- Created: `{manifest['created_at']}`
- Links input: `{manifest['links_file_reference']}`
- Local media input: `{manifest['media_directory_reference']}`
- Parsed links: {manifest['parsed_link_count']}
- Local files: {manifest['local_media_count']}
- Duplicates: {manifest['duplicate_input_count']}
- Accepted: {manifest['accepted_source_count']}
- Failed: {manifest['failed_source_count']}
- Status: {manifest['status']}

## Результаты

{chr(10).join(item_lines) if item_lines else '- Нет входов.'}

## Следующие действия

1. Откройте item folder и проверьте `source.mp4`.
2. При необходимости проверьте `transcript.txt` и `screen_text.txt`.
3. Загрузите `source.mp4` и `GPT_HANDOFF_RU.md` в ChatGPT.
4. Сначала попросите описать фактический смысл, hook и механизм внимания.
5. Только после подтверждения попросите адаптацию и сценарий NURA.

LOOPRA не изменяет входные файлы. После проверки вручную удалите обработанные ссылки,
перенесите MP4 в архив или оставьте входы для reuse.
"""


def run_manual_intake(*, project_id: str, links_file: Path, media_dir: Path,
                      output_root: Path, repository_root: Path, reuse_only: bool = False,
                      dry_run: bool = False, limit: int | None = None,
                      services: ManualIntakeServices | None = None,
                      maximum_file_bytes: int = DEFAULT_MAX_FILE_BYTES) -> dict[str, Any]:
    """Execute one bounded, failure-isolated manual intake."""
    services = services or ManualIntakeServices()
    plan = build_plan(project_id=project_id, links_file=links_file, media_dir=media_dir,
                      output_root=output_root, repository_root=repository_root, limit=limit)
    package = output_root / plan.intake_id
    if dry_run:
        return {
            "status": "DRY_RUN", "intake_id": plan.intake_id,
            "parsed_links": len(plan.parsed_links), "local_media_files": len(plan.local_media),
            "parsed_link_count": len(plan.parsed_links), "local_media_count": len(plan.local_media),
            "duplicates": plan.duplicate_input_count, "output_path": _portable(package, repository_root),
            "side_effects": 0, "browser_calls": 0, "acquisition_calls": 0,
            "inspection_calls": 0, "transcription_calls": 0, "ocr_calls": 0,
        }
    existing = _existing_package(package, plan.intake_id)
    if existing is not None:
        return existing | {
            "status": "REUSED", "output_path": _portable(package, repository_root), "reused": True,
            "browser_calls": 0, "acquisition_calls": 0, "inspection_calls": 0,
            "transcription_calls": 0, "ocr_calls": 0,
        }
    if reuse_only:
        return {
            "status": "BLOCKED", "failure_code": "REUSABLE_ARTIFACT_NOT_FOUND",
            "intake_id": plan.intake_id, "output_path": _portable(package, repository_root),
            "browser_calls": 0, "acquisition_calls": 0, "inspection_calls": 0,
            "transcription_calls": 0, "ocr_calls": 0,
        }

    runtime = output_root / ".runtime" / plan.intake_id
    acquisition_output_root = runtime / "acquisitions"
    acquisition_run_root = acquisition_output_root / plan.intake_id
    inspection_root = runtime / "inspections"
    transcription_root = runtime / "transcription"
    ocr_root = runtime / "ocr"
    manifest_root = runtime / "manifests"

    inputs: list[dict[str, Any]] = []
    for link in plan.parsed_links:
        item_id = f"tiktok-{link.video_id}" if link.video_id else f"invalid-{_hash_payload(link.raw_value)[:12]}"
        inputs.append({"item_id": _safe_component(item_id), "input_type": "TIKTOK_URL", "source_url": link.normalized_url,
                       "identity": f"tiktok:{link.video_id}" if link.video_id else f"invalid:{_hash_payload(link.raw_value)}",
                       "order": link.original_order, "initial_status": link.status, "failure_code": link.failure_code, "source": None})
    local_order_base = max((link.original_order for link in plan.parsed_links), default=0)
    seen_local_hashes: dict[str, str] = {}
    for offset, source in enumerate(plan.local_media, 1):
        digest = _sha256(source)
        duplicate_of = seen_local_hashes.get(digest)
        item_id = f"local-{digest[:16]}"
        if duplicate_of:
            item_id = f"duplicate-local-{offset:03d}-{digest[:8]}"
        else:
            seen_local_hashes[digest] = item_id
        inputs.append({"item_id": item_id, "input_type": "LOCAL_MP4", "source_url": None,
                       "identity": f"sha256:{digest}", "order": local_order_base + offset,
                       "initial_status": "DUPLICATE_INPUT" if duplicate_of else "READY",
                       "failure_code": "DUPLICATE_INPUT" if duplicate_of else None, "source": source})

    candidates = [_candidate(item["item_id"], item["source_url"]) for item in inputs if item["initial_status"] == "READY"]
    selection_manifest_path = None
    selection_manifest = None
    if candidates:
        selection_manifest = build_selection_manifest(candidates, radar_run_id=plan.intake_id)
        selection_manifest_path = write_selection_manifest(selection_manifest, manifest_root)

    work_parent = output_root / ".building"
    work_parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=f"{plan.intake_id}-", dir=work_parent))
    items_root = work / "items"
    items_root.mkdir()
    items: list[dict[str, Any]] = []
    known_media: dict[str, str] = {}
    counters = {"browser_calls": 0, "acquisition_calls": 0, "inspection_calls": 0, "transcription_calls": 0, "ocr_calls": 0}
    try:
        for source_input in sorted(inputs, key=lambda item: item["order"]):
            item_id = source_input["item_id"]
            base = {
                "schema_version": SCHEMA_VERSION, "item_id": item_id,
                "created_at": _utc_now(),
                "intake_reference": "00_MANIFEST.json", "intake_hash": plan.identity_hash,
                "input_type": source_input["input_type"], "source_url": source_input["source_url"],
                "source_filename": source_input["source"].name if source_input["source"] is not None else None,
                "normalized_source_identity": source_input["identity"], "original_input_order": source_input["order"],
                "local_media_reference": None, "local_media_hash": None, "media_type": None,
                "duration": None, "dimensions": None, "video_codec": None, "audio_codec": None,
                "audio_presence": None, "acquisition_status": source_input["initial_status"],
                "inspection_reference": None, "inspection_hash": None,
                "transcription_reference": None, "transcription_hash": None, "ocr_reference": None,
                "ocr_hash": None, "transcript_status": "MANUAL_REVIEW_REQUIRED", "ocr_status": "MANUAL_TEXT_CHECK",
                "evidence_warnings": [], "processing_status": source_input["initial_status"],
                "failure_code": source_input["failure_code"], "output_folder_reference": None,
                "reuse_metadata": {"mode": "CONTENT_IDENTICAL", "reused": False},
            }
            if source_input["initial_status"] != "READY":
                items.append(_with_hash(base))
                continue
            record: dict[str, Any]
            try:
                if source_input["input_type"] == "LOCAL_MP4":
                    source = source_input["source"]
                    facts = services.validate_media(source, maximum_file_bytes)
                    candidate_root = acquisition_run_root / item_id
                    candidate_root.mkdir(parents=True, exist_ok=True)
                    target = candidate_root / "source.mp4"
                    services.copy_media(source, target)
                    copied = services.validate_media(target, maximum_file_bytes)
                    if copied["sha256"] != facts["sha256"]:
                        raise MediaAcquisitionError("copied media SHA-256 does not match source")
                    record = _acquisition_record(item_id, acquisition_run_root, target, copied)
                    _write_json_atomic(candidate_root / "acquisition_record.json", record)
                else:
                    counters["browser_calls"] += 1
                    acquire = services.acquire_link or acquire_public_link
                    record = acquire(manifest_path=selection_manifest_path, acquisition_output_root=acquisition_output_root, candidate_id=item_id)
                counters["acquisition_calls"] += 1
                if record.get("status") not in {"COMPLETED", "REUSED"}:
                    raise ManualIntakeError("; ".join(record.get("errors", [])) or "media acquisition failed")
                media_ref = record.get("local_media_path")
                media = acquisition_run_root / media_ref if media_ref else None
                digest = record.get("media_sha256") or record.get("sha256")
                if media is None or not media.is_file() or not digest or _sha256(media) != digest:
                    raise ManualIntakeError("acquired media is missing or invalid")
                if digest in known_media:
                    base.update({"acquisition_status": "DUPLICATE_INPUT", "processing_status": "DUPLICATE_INPUT",
                                 "failure_code": "DUPLICATE_INPUT", "local_media_hash": digest,
                                 "reuse_metadata": {"mode": "EXACT_MEDIA_SHA256", "duplicate_of": known_media[digest]}})
                    items.append(_with_hash(base))
                    continue
                known_media[digest] = item_id
                probe = record.get("ffprobe_validation") or services.validate_media(media, maximum_file_bytes)["ffprobe"]
                media_data = _media_facts(probe)
                base.update({"acquisition_status": record.get("status", "COMPLETED"), "local_media_hash": digest,
                             "media_type": "video/mp4", **media_data})
            except Exception as error:
                base.update({"acquisition_status": "MEDIA_ACQUISITION_FAILED", "processing_status": "MEDIA_ACQUISITION_FAILED",
                             "failure_code": "INVALID_MEDIA" if source_input["input_type"] == "LOCAL_MP4" else "MEDIA_ACQUISITION_FAILED",
                             "evidence_warnings": [_safe_public_error(error)]})
                items.append(_with_hash(base))
                continue

            item_number = sum(item.get("output_folder_reference") is not None for item in items) + 1
            item_folder_ref = f"items/{item_number:02d}_{_safe_component(item_id)}"
            item_folder = work / item_folder_ref
            item_folder.mkdir(parents=True)
            services.copy_media(media, item_folder / "source.mp4")
            if _sha256(item_folder / "source.mp4") != base["local_media_hash"]:
                raise ManualIntakeError("output source SHA-256 mismatch")
            base["local_media_reference"] = f"{item_folder_ref}/source.mp4"
            base["output_folder_reference"] = item_folder_ref

            warnings: list[str] = []
            inspection: dict[str, Any] = {}
            inspection_dir = inspection_root / item_id
            try:
                counters["inspection_calls"] += 1
                inspection = services.inspect(media, inspection_dir, item_id, source_input["source_url"])
                if inspection.get("status") == "FAILED":
                    raise ManualIntakeError("canonical format inspection failed")
                inspection_path = inspection_dir / "inspection.json"
                base["inspection_reference"] = f"{item_folder_ref}/FORMAT_INSPECTION.md"
                base["inspection_hash"] = _sha256(inspection_path)
                inspection_facts = inspection.get("media_facts", {})
                visual = inspection.get("visual_structure", {})
                base.update({
                    "duration": inspection_facts.get("duration_seconds", base["duration"]),
                    "dimensions": {"width": inspection_facts["width"], "height": inspection_facts["height"]}
                    if inspection_facts.get("width") and inspection_facts.get("height") else base["dimensions"],
                    "video_codec": inspection_facts.get("codec", base["video_codec"]),
                    "audio_codec": inspection_facts.get("audio_codec", base["audio_codec"]),
                    "audio_presence": inspection_facts.get("audio_present", base["audio_presence"]),
                })
                inspection_warnings = [
                    warning for warning in inspection.get("evidence", {}).get("warnings", [])
                    if warning != "OCR and transcription are not run automatically in the local baseline."
                ]
                _write_text(item_folder / "FORMAT_INSPECTION.md", f"""# Format Inspection

- Status: {inspection.get('status')}
- Duration: {inspection_facts.get('duration_seconds')} s
- Resolution: {inspection_facts.get('width')}×{inspection_facts.get('height')}
- Aspect ratio: {inspection_facts.get('aspect_ratio')}
- Audio: {inspection_facts.get('audio_present')} ({inspection_facts.get('audio_codec')})
- Scenes/static assessment: {visual.get('dominant_motion_level', 'manual review required')}
- Contact sheets: {', '.join(inspection.get('evidence', {}).get('contact_sheets', [])) or 'нет'}
- Technical warnings: {', '.join(inspection_warnings) or 'нет'}
""")
                warnings.extend(inspection_warnings)
            except Exception as error:
                warnings.append(f"INSPECTION_FAILED: {_safe_public_error(error)}")
                _write_text(item_folder / "FORMAT_INSPECTION.md", f"# Format Inspection\n\nStatus: INSPECTION_FAILED\n\n{_safe_public_error(error)}")

            transcript_result: dict[str, Any] = {"status": "FAILED", "errors": ["inspection is unavailable"]}
            if inspection.get("status") in {"COMPLETED", "DEGRADED"}:
                try:
                    counters["transcription_calls"] += 1
                    response = services.transcribe(TranscriptionRunRequest(selection_manifest_path, acquisition_run_root, inspection_root, transcription_root, candidate_ids=(item_id,)))
                    transcript_result = response["candidates"][0]
                except Exception as error:
                    transcript_result = {"status": "FAILED", "errors": [_safe_public_error(error)]}
            transcript_status = _transcript_status(transcript_result, bool(base["audio_presence"]))
            transcript_text = _build_transcript_text(transcript_status, transcript_result)
            _write_text(item_folder / "transcript.txt", transcript_text)
            portable_segments = [{
                "index": index, "start": segment.get("start_seconds"), "end": segment.get("end_seconds"),
                "text": segment.get("normalized_text") or segment.get("raw_text") or "",
                "language": transcript_result.get("language"),
                "quality": {"avg_logprob": segment.get("avg_logprob"), "no_speech_prob": segment.get("no_speech_prob")},
                "audio_role": "speech",
            } for index, segment in enumerate(transcript_result.get("segments", []), 1)]
            _write_json_atomic(item_folder / "transcript_segments.json", {
                "schema_version": SCHEMA_VERSION, "status": transcript_status,
                "segments": portable_segments, "language": transcript_result.get("language"),
            })
            transcript_artifact = transcription_root / plan.intake_id / "candidates" / item_id / "transcription" / "transcription_result.json"
            base["transcription_reference"] = f"{item_folder_ref}/transcript_segments.json"
            base["transcription_hash"] = _sha256(transcript_artifact) if transcript_artifact.is_file() else _sha256(item_folder / "transcript_segments.json")
            base["transcript_status"] = transcript_status

            ocr_result: dict[str, Any] = {"status": "FAILED", "errors": ["inspection is unavailable"]}
            if inspection.get("status") in {"COMPLETED", "DEGRADED"}:
                try:
                    counters["ocr_calls"] += 1
                    response = services.ocr(OcrRunRequest(selection_manifest_path, inspection_root, ocr_root, candidate_ids=(item_id,), language="ru-RU"))
                    ocr_result = response["candidates"][0]
                except Exception as error:
                    ocr_result = {"status": "FAILED", "errors": [_safe_public_error(error)]}
            ocr_status = _ocr_status(ocr_result)
            screen_text = _build_screen_text(ocr_status, ocr_result)
            _write_text(item_folder / "screen_text.txt", screen_text)
            ocr_artifact = ocr_root / plan.intake_id / "candidates" / item_id / "ocr" / "ocr_result.json"
            base["ocr_reference"] = f"{item_folder_ref}/screen_text.txt"
            base["ocr_hash"] = _sha256(ocr_artifact) if ocr_artifact.is_file() else _sha256(item_folder / "screen_text.txt")
            base["ocr_status"] = ocr_status
            if transcript_status in {"TRANSCRIPTION_FAILED", "MANUAL_REVIEW_REQUIRED"}:
                warnings.extend(transcript_result.get("errors", []))
            if ocr_status in {"OCR_FAILED", "PARTIALLY_READABLE", "MANUAL_TEXT_CHECK"}:
                warnings.extend(ocr_result.get("errors", []))
            base["evidence_warnings"] = sorted(set(filter(None, warnings)))
            base["processing_status"] = "COMPLETED_WITH_WARNINGS" if base["evidence_warnings"] or transcript_status in {"TRANSCRIPTION_FAILED", "MANUAL_REVIEW_REQUIRED"} or ocr_status == "OCR_FAILED" else "COMPLETED"
            base["failure_code"] = None
            handoff_facts = {key: base[key] for key in ("duration", "dimensions", "video_codec", "audio_codec", "audio_presence")}
            handoff = _handoff(project_id, f"{item_folder_ref}/source.mp4", handoff_facts, transcript_status,
                               transcript_text, ocr_status, screen_text, base["evidence_warnings"])
            _write_text(item_folder / "GPT_HANDOFF_RU.md", handoff)
            item_payload = _with_hash(base)
            _validate_no_secrets(item_payload)
            _write_json_atomic(item_folder / "source_info.json", item_payload)
            items.append(item_payload)

        accepted = sum(item["processing_status"] in {"COMPLETED", "COMPLETED_WITH_WARNINGS"} for item in items)
        failed = sum(item["processing_status"] not in {"COMPLETED", "COMPLETED_WITH_WARNINGS", "DUPLICATE_INPUT"} for item in items)
        duplicates = sum(item["processing_status"] == "DUPLICATE_INPUT" for item in items)
        if not items or accepted == 0 and failed == 0:
            status = "NO_VALID_INPUTS"
        elif accepted and failed:
            status = "PARTIAL"
        elif accepted:
            status = "COMPLETED_WITH_WARNINGS" if any(item["processing_status"] == "COMPLETED_WITH_WARNINGS" for item in items) else "COMPLETED"
        else:
            status = "NO_VALID_INPUTS"
        provisional = {
            "schema_version": SCHEMA_VERSION, "intake_id": plan.intake_id, "intake_version": INTAKE_VERSION,
            "project_id": project_id, "created_at": _utc_now(), "links_file_reference": plan.links_file_reference,
            "media_directory_reference": plan.media_directory_reference,
            "parsed_link_count": sum(link.status != "DUPLICATE_INPUT" for link in plan.parsed_links),
            "local_media_count": len(plan.local_media), "duplicate_input_count": duplicates,
            "accepted_source_count": accepted, "failed_source_count": failed,
            "item_references": [{"item_id": item["item_id"], "content_hash": item["content_hash"],
                                 "processing_status": item["processing_status"], "output_folder_reference": item["output_folder_reference"]} for item in items],
            "output_package_reference": _portable(package, repository_root), "output_package_hash": "",
            "provider_calls": 0, "search_calls": 0, "script_calls": 0, "image_calls": 0,
            "reuse_metadata": {"supported": True, "mode": "CONTENT_IDENTICAL", **counters},
            "status": status,
        }
        _write_text(work / "00_OVERVIEW_RU.md", _overview(provisional, items))
        provisional["output_package_hash"] = _package_hash(work)
        manifest = _with_hash(provisional)
        _validate_no_secrets(manifest)
        _write_json_atomic(work / "00_MANIFEST.json", manifest)
        package.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.replace(work, package)
        except FileExistsError:
            concurrent = _existing_package(package, plan.intake_id)
            if concurrent is None:
                raise
            shutil.rmtree(work)
            manifest = concurrent
        return manifest | {"output_path": _portable(package, repository_root), "reused": False, **counters}
    except Exception:
        shutil.rmtree(work, ignore_errors=True)
        raise


def default_paths(repository_root: Path) -> tuple[Path, Path, Path]:
    return (
        repository_root / DEFAULT_LINKS_REFERENCE,
        repository_root / DEFAULT_MEDIA_REFERENCE,
        repository_root / DEFAULT_OUTPUT_REFERENCE,
    )
