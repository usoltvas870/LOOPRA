"""Bounded, sequential browser media acquisition for manifest candidates only."""

from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from auth import storage_state_diagnostics
from browser_media_capture import (
    ACQUISITION_METHOD, BrowserMediaCaptureRecord, BrowserMediaCaptureRequest,
    _read_reusable_record, _record, _safe_component, _write_json_atomic,
    capture_browser_media_in_context,
)
from media_acquisition import MAX_SELECTED_CANDIDATES, MediaAcquisitionError
from selection_manifest import read_selection_manifest

RUN_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class BrowserMediaAcquisitionRunRequest:
    selection_manifest_path: Path
    cookie_state_path: Path
    output_root: Path
    candidate_ids: tuple[str, ...] = ()
    limit: int | None = None
    maximum_file_bytes: int = 8 * 1024 * 1024


@dataclass(frozen=True)
class CandidateAcquisitionSummary:
    video_id: str
    rank: int
    status: str
    acquisition_method: str
    acquisition_record_ref: str
    local_media_path: str | None
    media_sha256: str | None
    captured_bytes: int | None
    duration_seconds: float | None
    video_codec: str | None
    audio_present: bool | None
    warnings: list[str]
    errors: list[str]


@dataclass(frozen=True)
class BrowserMediaAcquisitionRun:
    schema_version: str
    acquisition_run_id: str
    selection_manifest_reference: str
    selection_manifest_hash: str
    radar_run_id: str
    requested_candidate_count: int
    selected_candidate_count: int
    completed_count: int
    reused_count: int
    failed_count: int
    skipped_count: int
    run_status: str
    started_at: str
    completed_at: str
    candidates: list[CandidateAcquisitionSummary]
    warnings: list[str]
    errors: list[str]
    tool_version: str = "stage-3d"

    def to_dict(self) -> dict:
        return asdict(self)


def select_manifest_candidates(manifest, candidate_ids: tuple[str, ...] = (), limit: int | None = None) -> list:
    """Select at most five entries, preserving the immutable manifest order."""
    if limit is not None and (limit < 1 or limit > MAX_SELECTED_CANDIDATES):
        raise MediaAcquisitionError(f"limit must be between 1 and {MAX_SELECTED_CANDIDATES}")
    if len(set(candidate_ids)) != len(candidate_ids):
        raise MediaAcquisitionError("duplicate candidate IDs are not allowed")
    known = {candidate.video_id for candidate in manifest.candidates}
    unknown = set(candidate_ids) - known
    if unknown:
        raise MediaAcquisitionError(f"unknown candidate IDs: {', '.join(sorted(unknown))}")
    selected = (
        [candidate for candidate in manifest.candidates if candidate.video_id in candidate_ids]
        if candidate_ids else list(manifest.candidates[:MAX_SELECTED_CANDIDATES])
    )
    if limit is not None:
        selected = selected[:limit]
    if len(selected) > MAX_SELECTED_CANDIDATES:
        raise MediaAcquisitionError(f"select no more than {MAX_SELECTED_CANDIDATES} candidates")
    if not selected:
        raise MediaAcquisitionError("selection is empty")
    return selected


def run_browser_media_acquisition(request: BrowserMediaAcquisitionRunRequest) -> BrowserMediaAcquisitionRun:
    return asyncio.run(_run(request))


async def _run(request: BrowserMediaAcquisitionRunRequest) -> BrowserMediaAcquisitionRun:
    manifest = read_selection_manifest(request.selection_manifest_path)
    selected = select_manifest_candidates(manifest, request.candidate_ids, request.limit)
    run_root = request.output_root / _safe_component(manifest.radar_run_id)
    selection_key = hashlib.sha256(",".join(candidate.video_id for candidate in selected).encode("utf-8")).hexdigest()[:12]
    run_id = f"browser-acquisition-{manifest.radar_run_id}-{manifest.manifest_hash[:12]}-{selection_key}"
    started_at = _utc_iso()
    summaries: list[CandidateAcquisitionSummary] = []
    pending = []
    for candidate in selected:
        record = _read_reusable_record(run_root / _safe_component(candidate.video_id), run_root, manifest.manifest_hash, candidate.video_id, request.maximum_file_bytes)
        if record is None:
            pending.append(candidate)
        else:
            summaries.append(_summary(record))

    if pending:
        state, diagnostic = storage_state_diagnostics(request.cookie_state_path)
        if state is None:
            for candidate in pending:
                summaries.append(_persist_failed_summary(request, manifest, candidate, "BLOCKED_AUTH", f"authenticated browser session unavailable: {diagnostic.reason}"))
        else:
            await _capture_pending(request, manifest, pending, state, summaries)
    return _finish(run_id, manifest, selected, summaries, started_at, run_root)


async def _capture_pending(request, manifest, pending, state, summaries) -> None:
    playwright = browser = context = None
    blocked = False
    try:
        from playwright.async_api import async_playwright
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=state, locale="ru-RU", viewport={"width": 1280, "height": 800})
        for candidate in pending:
            if blocked:
                summaries.append(_persist_failed_summary(request, manifest, candidate, "BLOCKED_AUTH", "capture stopped after session/authentication failure"))
                continue
            capture_request = BrowserMediaCaptureRequest(request.selection_manifest_path, request.cookie_state_path, request.output_root, candidate.video_id, request.maximum_file_bytes)
            try:
                record = await capture_browser_media_in_context(capture_request, manifest, candidate, context)
                summaries.append(_summary(record))
            except MediaAcquisitionError as error:
                message = str(error)
                status = "BLOCKED_AUTH" if "authenticated candidate page unavailable" in message else "FAILED"
                summaries.append(_persist_failed_summary(request, manifest, candidate, status, message))
                blocked = status == "BLOCKED_AUTH"
            except Exception as error:
                summaries.append(_persist_failed_summary(request, manifest, candidate, "FAILED", f"browser capture failed: {type(error).__name__}"))
    except Exception as error:
        captured_ids = {summary.video_id for summary in summaries}
        summaries.extend(_persist_failed_summary(request, manifest, candidate, "FAILED", f"browser context unavailable: {type(error).__name__}") for candidate in pending if candidate.video_id not in captured_ids)
    finally:
        if context is not None:
            await context.close()
        if browser is not None:
            await browser.close()
        if playwright is not None:
            await playwright.stop()


def _summary(record: BrowserMediaCaptureRecord) -> CandidateAcquisitionSummary:
    probe = record.ffprobe_validation or {}
    return CandidateAcquisitionSummary(record.candidate_video_id, record.candidate_rank, record.status, record.acquisition_method,
        f"{record.candidate_video_id}/acquisition_record.json", record.local_media_path, record.media_sha256,
        record.captured_byte_count, probe.get("duration_seconds"), probe.get("video_codec"), probe.get("audio_stream_present"), record.warnings, record.errors)


def _failed_summary(candidate, status: str, message: str) -> CandidateAcquisitionSummary:
    return CandidateAcquisitionSummary(candidate.video_id, candidate.rank, status, ACQUISITION_METHOD,
        f"{candidate.video_id}/acquisition_record.json", None, None, None, None, None, None, [], [message])


def _persist_failed_summary(request, manifest, candidate, status: str, message: str) -> CandidateAcquisitionSummary:
    run_root = request.output_root / _safe_component(manifest.radar_run_id)
    candidate_root = run_root / _safe_component(candidate.video_id)
    record = _record(manifest, candidate, {}, None, "session_unavailable" if status == "BLOCKED_AUTH" else "capture_failed",
        _utc_iso(), status, run_root, None, None, {"valid": False}, [], [message])
    _write_json_atomic(candidate_root / "acquisition_record.json", record.to_dict())
    return _summary(record)


def _finish(run_id, manifest, selected, summaries, started_at, run_root: Path) -> BrowserMediaAcquisitionRun:
    summaries.sort(key=lambda summary: summary.rank)
    completed = sum(summary.status == "COMPLETED" for summary in summaries)
    reused = sum(summary.status == "REUSED" for summary in summaries)
    failed = sum(summary.status not in {"COMPLETED", "REUSED", "SKIPPED"} for summary in summaries)
    skipped = sum(summary.status == "SKIPPED" for summary in summaries)
    usable = completed + reused
    status = "COMPLETED" if usable == len(selected) else "PARTIAL" if usable else "FAILED"
    result = BrowserMediaAcquisitionRun(RUN_SCHEMA_VERSION, run_id, manifest.radar_run_reference, manifest.manifest_hash,
        manifest.radar_run_id, len(selected), len(selected), completed, reused, failed, skipped, status, started_at, _utc_iso(), summaries, [], [])
    _write_json_atomic(run_root / f"{run_id}.json", result.to_dict())
    return result


def _utc_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
