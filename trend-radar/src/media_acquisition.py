"""Selective, local-only media acquisition for canonical Trend Radar selections.

This module deliberately has no network or browser behaviour.  It accepts only
operator-provided files for entries already present in a validated selection
manifest, then records reproducible technical provenance in ignored runtime.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from selection_manifest import ContentIntelligenceSelectionManifest, read_selection_manifest


SCHEMA_VERSION = "1.0"
ACQUISITION_METHOD = "operator_provided_local_file"
MAX_SELECTED_CANDIDATES = 5
DEFAULT_MAX_FILE_BYTES = 2 * 1024 * 1024 * 1024
MIN_FILE_BYTES = 1024


class MediaAcquisitionError(ValueError):
    """Raised when a bounded local media acquisition cannot be completed."""


@dataclass(frozen=True)
class MediaAcquisitionRequest:
    selection_manifest_path: Path
    output_root: Path
    local_file_mapping: dict[str, Path]
    candidate_ids: tuple[str, ...] = ()
    limit: int | None = None
    maximum_file_bytes: int = DEFAULT_MAX_FILE_BYTES


@dataclass(frozen=True)
class MediaAcquisitionRecord:
    schema_version: str
    candidate_video_id: str
    rank: int
    source_page_url: str | None
    acquisition_method: str
    status: str
    started_at: str
    completed_at: str
    resolved_media_reference: str | None
    response_content_type: str | None
    content_length: int | None
    local_media_path: str | None
    sha256: str | None
    ffprobe_validation: dict
    reusable: bool
    warnings: list[str]
    errors: list[str]
    tool_metadata: dict
    selection_manifest_reference: str
    selection_manifest_hash: str

    def to_dict(self) -> dict:
        return asdict(self)


def acquire_local_media(request: MediaAcquisitionRequest) -> list[MediaAcquisitionRecord]:
    """Copy and validate only explicitly selected manifest candidates.

    Selection preserves manifest order; it never scores, sorts, filters, opens a
    browser, or makes network requests.
    """
    _validate_request(request)
    manifest = read_selection_manifest(request.selection_manifest_path)
    selected = _select_candidates(manifest, request.candidate_ids, request.limit)
    missing_mappings = [candidate.video_id for candidate in selected if candidate.video_id not in request.local_file_mapping]
    if missing_mappings:
        raise MediaAcquisitionError(
            f"missing local file mappings for candidate IDs: {', '.join(missing_mappings)}"
        )
    run_root = request.output_root / _safe_component(
        f"acquisition_{manifest.radar_run_id}_{manifest.manifest_hash[:12]}"
    )
    records = []
    for candidate in selected:
        records.append(_acquire_candidate(manifest, candidate, request, run_root))
    return records


def _validate_request(request: MediaAcquisitionRequest) -> None:
    if request.limit is not None and request.limit <= 0:
        raise MediaAcquisitionError("limit must be positive")
    if request.limit is not None and request.limit > MAX_SELECTED_CANDIDATES:
        raise MediaAcquisitionError(f"limit cannot exceed {MAX_SELECTED_CANDIDATES}")
    if request.maximum_file_bytes < MIN_FILE_BYTES:
        raise MediaAcquisitionError("maximum_file_bytes is below the minimum media size")
    if not request.local_file_mapping:
        raise MediaAcquisitionError("local_file_mapping is required for local acquisition")


def _select_candidates(
    manifest: ContentIntelligenceSelectionManifest,
    candidate_ids: tuple[str, ...],
    limit: int | None,
) -> list:
    requested = set(candidate_ids)
    known = {candidate.video_id for candidate in manifest.candidates}
    unknown = requested - known
    if unknown:
        raise MediaAcquisitionError(f"unknown candidate IDs: {', '.join(sorted(unknown))}")
    selected = [candidate for candidate in manifest.candidates if not requested or candidate.video_id in requested]
    if limit is not None:
        selected = selected[:limit]
    if len(selected) > MAX_SELECTED_CANDIDATES:
        raise MediaAcquisitionError(
            f"select no more than {MAX_SELECTED_CANDIDATES} candidates with --limit or --candidate-id"
        )
    if not selected:
        raise MediaAcquisitionError("selection is empty")
    return selected


def _acquire_candidate(manifest, candidate, request: MediaAcquisitionRequest, run_root: Path) -> MediaAcquisitionRecord:
    # This assignment allows _select_candidates to stay free of filesystem and mapping policy.
    candidate_root = run_root / _safe_component(candidate.video_id)
    record_path = candidate_root / "acquisition_record.json"
    source = request.local_file_mapping[candidate.video_id]
    existing = _read_reusable_record(
        record_path, run_root, manifest, candidate.video_id, request.maximum_file_bytes
    )
    if existing is not None:
        return existing

    started_at = _utc_iso()
    target: Path | None = None
    copied_target = False
    try:
        facts = _validate_local_file(source, request.maximum_file_bytes)
        candidate_root.mkdir(parents=True, exist_ok=True)
        target = candidate_root / f"source{source.suffix.lower()}"
        _copy_atomic(source, target)
        copied_target = True
        copied_facts = _validate_local_file(target, request.maximum_file_bytes)
        if copied_facts["sha256"] != facts["sha256"]:
            raise MediaAcquisitionError("copied media SHA-256 does not match source")
        record = _record(
            manifest, candidate, started_at, "COMPLETED", run_root, target, copied_facts, [], []
        )
    except (OSError, MediaAcquisitionError) as error:
        if copied_target and target is not None:
            target.unlink(missing_ok=True)
        record = _record(manifest, candidate, started_at, "FAILED", run_root, None, None, [], [str(error)])
    _write_json_atomic(record_path, record.to_dict())
    return record


def _read_reusable_record(
    record_path: Path, run_root: Path, manifest, video_id: str, maximum_file_bytes: int
) -> MediaAcquisitionRecord | None:
    if not record_path.is_file():
        return None
    try:
        payload = json.loads(record_path.read_text(encoding="utf-8"))
        record = MediaAcquisitionRecord(**payload)
        if (
            record.status not in {"COMPLETED", "REUSED"}
            or record.candidate_video_id != video_id
            or record.selection_manifest_hash != manifest.manifest_hash
            or not record.local_media_path
        ):
            return None
        media_path = _contained_path(run_root, record.local_media_path)
        facts = _validate_local_file(media_path, maximum_file_bytes)
        if facts["sha256"] != record.sha256:
            return None
        return MediaAcquisitionRecord(**{**record.to_dict(), "status": "REUSED", "reusable": True})
    except (OSError, ValueError, json.JSONDecodeError, MediaAcquisitionError, TypeError):
        return None


def _record(manifest, candidate, started_at, status, run_root, media_path, facts, warnings, errors):
    completed_at = _utc_iso()
    relative_path = str(media_path.relative_to(run_root)).replace("\\", "/") if media_path else None
    return MediaAcquisitionRecord(
        schema_version=SCHEMA_VERSION,
        candidate_video_id=candidate.video_id,
        rank=candidate.rank,
        source_page_url=candidate.canonical_url,
        acquisition_method=ACQUISITION_METHOD,
        status=status,
        started_at=started_at,
        completed_at=completed_at,
        resolved_media_reference=None,
        response_content_type=None,
        content_length=facts["size"] if facts else None,
        local_media_path=relative_path,
        sha256=facts["sha256"] if facts else None,
        ffprobe_validation=facts["ffprobe"] if facts else {"valid": False},
        reusable=status == "COMPLETED",
        warnings=warnings,
        errors=errors,
        tool_metadata={"adapter": "local_file", "python": sys.version.split()[0], "ffprobe": "system PATH"},
        selection_manifest_reference=str(manifest.radar_run_reference),
        selection_manifest_hash=manifest.manifest_hash,
    )


def _validate_local_file(path: Path, maximum_file_bytes: int) -> dict:
    if not path.is_file():
        raise MediaAcquisitionError(f"local media file does not exist: {path}")
    size = path.stat().st_size
    if size < MIN_FILE_BYTES:
        raise MediaAcquisitionError("local media file is too small")
    if size > maximum_file_bytes:
        raise MediaAcquisitionError("local media file exceeds maximum_file_bytes")
    head = path.read_bytes()[:512].lower()
    if b"<html" in head or b"<!doctype html" in head:
        raise MediaAcquisitionError("local media file appears to be HTML")
    probe = _ffprobe(path)
    if not probe["valid"]:
        raise MediaAcquisitionError(probe["error"])
    return {"size": size, "sha256": _sha256(path), "ffprobe": probe}


def _ffprobe(path: Path) -> dict:
    if shutil.which("ffprobe") is None:
        raise MediaAcquisitionError("ffprobe is required")
    completed = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode:
        return {"valid": False, "error": completed.stderr.strip() or "ffprobe failed"}
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"valid": False, "error": "ffprobe returned invalid JSON"}
    streams = payload.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    duration = payload.get("format", {}).get("duration") or (video or {}).get("duration")
    if video is None:
        return {"valid": False, "error": "ffprobe found no video stream"}
    return {
        "valid": True,
        "duration_seconds": float(duration) if duration else None,
        "container": payload.get("format", {}).get("format_name"),
        "video_codec": video.get("codec_name"),
        "width": video.get("width"),
        "height": video.get("height"),
        "audio_stream_present": audio is not None,
    }


def _copy_atomic(source: Path, target: Path) -> None:
    if target.exists():
        raise MediaAcquisitionError(f"refusing to overwrite existing media: {target}")
    temporary = target.with_suffix(target.suffix + ".part")
    try:
        with source.open("rb") as input_file, temporary.open("xb") as output_file:
            shutil.copyfileobj(input_file, output_file, length=1024 * 1024)
        os.replace(temporary, target)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def _write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as file:
        file.write(serialized)
        temporary = Path(file.name)
    os.replace(temporary, path)


def _contained_path(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    if root.resolve() not in candidate.parents:
        raise MediaAcquisitionError("record local_media_path escapes acquisition root")
    return candidate


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_component(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    if not sanitized:
        raise MediaAcquisitionError("candidate identifier is not safe for a runtime path")
    return sanitized


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
