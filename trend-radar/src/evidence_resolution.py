"""Manifest-bound resolution and repair of local Trend Radar evidence.

The resolver deliberately knows only the canonical candidate paths supplied by
the caller.  It never scans a runtime tree and never invokes media, OCR, or
transcription producers.  ``adopt_legacy_inspection`` is an explicit repair
operation for a verified Stage 3M result; it preserves the source artifact.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


INSPECTION_SCHEMA_VERSION = "1.1"
VALID_INSPECTION_STATUSES = {"COMPLETED", "DEGRADED"}
VALID_OCR_STATUSES = {"COMPLETED", "COMPLETED_EMPTY"}
VALID_TRANSCRIPTION_STATUSES = {"COMPLETED", "COMPLETED_NO_SPEECH", "COMPLETED_NO_AUDIO"}


class EvidenceResolutionError(ValueError):
    """Raised when an evidence artifact violates the manifest-bound contract."""


@dataclass(frozen=True)
class ResolvedCandidateEvidence:
    evidence: dict
    missing: tuple[str, ...]
    diagnostics: tuple[dict, ...]


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_candidate_evidence(*, candidate, manifest_hash: str, acquisition_root: Path,
                               inspection_root: Path, intelligence_root: Path) -> ResolvedCandidateEvidence:
    """Resolve one candidate without discovery outside its canonical paths."""
    video_id, rank = candidate.video_id, candidate.rank
    acquisition_path = acquisition_root / video_id / "acquisition_record.json"
    inspection_path = inspection_root / video_id / "inspection.json"
    ocr_path = intelligence_root / video_id / "ocr" / "ocr_result.json"
    transcription_path = intelligence_root / video_id / "transcription" / "transcription_result.json"
    loaded, missing, diagnostics = {}, [], []

    acquisition = _read_optional(acquisition_path, "acquisition", missing, diagnostics)
    if acquisition is not None:
        _require(acquisition.get("candidate_video_id") == video_id, "ACQUISITION_CANDIDATE_MISMATCH")
        _require(acquisition.get("candidate_rank") == rank, "ACQUISITION_RANK_MISMATCH")
        _require(acquisition.get("selection_manifest_hash") == manifest_hash, "ACQUISITION_MANIFEST_MISMATCH")
        media_sha = acquisition.get("media_sha256")
        _require(_is_hash(media_sha), "ACQUISITION_MEDIA_HASH_INVALID")
        media = _contained(acquisition_root, acquisition.get("local_media_path"))
        _require(media.is_file(), "ACQUISITION_MEDIA_MISSING")
        _require(hash_file(media) == media_sha, "ACQUISITION_MEDIA_HASH_MISMATCH")
        loaded["acquisition"] = acquisition
        loaded["acquisition_path"] = acquisition_path

    inspection = _read_optional(inspection_path, "inspection", missing, diagnostics)
    if inspection is not None:
        _validate_inspection(inspection, video_id, loaded.get("acquisition", {}).get("media_sha256"), inspection_path)
        loaded["inspection"] = inspection
        loaded["inspection_path"] = inspection_path

    for name, path, statuses in (("ocr", ocr_path, VALID_OCR_STATUSES), ("transcription", transcription_path, VALID_TRANSCRIPTION_STATUSES)):
        artifact = _read_optional(path, name, missing, diagnostics)
        if artifact is None:
            continue
        _require(artifact.get("candidate_video_id") == video_id, f"{name.upper()}_CANDIDATE_MISMATCH")
        _require(artifact.get("rank") == rank, f"{name.upper()}_RANK_MISMATCH")
        _require(artifact.get("selection_manifest_hash") == manifest_hash, f"{name.upper()}_MANIFEST_MISMATCH")
        _require(artifact.get("status") in statuses, f"{name.upper()}_STATUS_INVALID")
        expected_media = loaded.get("acquisition", {}).get("media_sha256")
        actual_media = artifact.get("inspection_media_sha256") if name == "ocr" else artifact.get("media_sha256")
        _require(actual_media == expected_media, f"{name.upper()}_MEDIA_HASH_MISMATCH")
        loaded[name] = artifact
        loaded[f"{name}_path"] = path

    return ResolvedCandidateEvidence(_bounded(loaded, inspection_root, intelligence_root), tuple(missing), tuple(diagnostics))


def adopt_legacy_inspection(*, candidate, manifest_hash: str, acquisition_root: Path,
                            inspection_root: Path, legacy_inspection_root: Path) -> Path:
    """Atomically adopt one verified legacy inspection under the canonical root."""
    source = legacy_inspection_root / candidate.video_id / "inspection.json"
    target = inspection_root / candidate.video_id / "inspection.json"
    legacy = _read_json(source)
    acquisition = _read_json(acquisition_root / candidate.video_id / "acquisition_record.json")
    _require(acquisition.get("candidate_video_id") == candidate.video_id, "ACQUISITION_CANDIDATE_MISMATCH")
    _require(acquisition.get("candidate_rank") == candidate.rank, "ACQUISITION_RANK_MISMATCH")
    _require(acquisition.get("selection_manifest_hash") == manifest_hash, "ACQUISITION_MANIFEST_MISMATCH")
    _validate_inspection(legacy, candidate.video_id, acquisition.get("media_sha256"), source)
    source_bytes = source.read_bytes()
    if target.exists():
        if target.read_bytes() == source_bytes:
            _validate_inspection(_read_json(target), candidate.video_id, acquisition.get("media_sha256"), target)
            return target
        previous = _read_json(target)
        if previous.get("schema_version") != "1.0" or previous.get("status") is not None:
            raise EvidenceResolutionError("CANONICAL_INSPECTION_CONFLICT")
        _backup_legacy_canonical(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    for frame in legacy.get("sampling", {}).get("frame_results", []):
        if frame.get("status") != "success":
            continue
        source_frame = _contained(source.parent / "frames", frame.get("frame_path"))
        target_frame = _contained(target.parent / "frames", frame.get("frame_path"))
        target_frame.parent.mkdir(parents=True, exist_ok=True)
        if not target_frame.exists():
            try:
                os.link(source_frame, target_frame)
            except OSError:
                _copy_new(source_frame, target_frame)
    _write_replace_bytes(target, source_bytes)
    return target


def _validate_inspection(inspection: dict, video_id: str, media_sha: str | None, path: Path) -> None:
    _require(inspection.get("schema_version") == INSPECTION_SCHEMA_VERSION, "INSPECTION_SCHEMA_UNSUPPORTED")
    _require(inspection.get("video_id") == video_id, "INSPECTION_CANDIDATE_MISMATCH")
    _require(inspection.get("media_sha256") == media_sha, "INSPECTION_MEDIA_HASH_MISMATCH")
    _require(inspection.get("status") in VALID_INSPECTION_STATUSES, "INSPECTION_STATUS_INVALID")
    frames = inspection.get("sampling", {}).get("frame_results", [])
    _require(isinstance(frames, list) and any(item.get("status") == "success" for item in frames), "INSPECTION_FRAMES_INVALID")
    for frame in frames:
        if frame.get("status") != "success":
            continue
        frame_path = _contained(path.parent / "frames", frame.get("frame_path"))
        _require(frame_path.is_file(), "INSPECTION_FRAME_MISSING")


def _bounded(loaded: dict, inspection_root: Path, intelligence_root: Path) -> dict:
    result = {"acquisition": None, "inspection": None}
    if "acquisition" in loaded:
        result["acquisition"] = {"ref": _portable(loaded["acquisition_path"], loaded["acquisition_path"].parents[2]), "sha256": hash_file(loaded["acquisition_path"]), "media_sha256": loaded["acquisition"].get("media_sha256")}
    if "inspection" in loaded:
        frames = [item for item in loaded["inspection"].get("sampling", {}).get("frame_results", []) if item.get("status") == "success"][:12]
        result["inspection"] = {"ref": _portable(loaded["inspection_path"], inspection_root), "sha256": hash_file(loaded["inspection_path"]), "status": loaded["inspection"].get("status"), "media_facts": loaded["inspection"].get("media_facts", {}), "frames": [{"frame_ref": item.get("frame_path"), "timestamp_seconds": item.get("effective_timestamp_seconds")} for item in frames]}
    for name in ("ocr", "transcription"):
        if name in loaded:
            artifact = loaded[name]
            result[name] = {"ref": _portable(loaded[f"{name}_path"], intelligence_root), "sha256": hash_file(loaded[f"{name}_path"]), "status": artifact.get("status")}
            if name == "ocr":
                result[name]["events"] = [{"event_id": item.get("event_id"), "text": str(item.get("text") or "")[:240], "first_seen_at_sec": item.get("first_seen_at_sec")} for item in artifact.get("text_events", [])[:12]]
                result[name]["first_text_hook"] = artifact.get("first_text_hook")
            else:
                result[name]["segments"] = [{"segment_id": item.get("segment_id"), "text": str(item.get("normalized_text") or "")[:240], "start_seconds": item.get("start_seconds"), "end_seconds": item.get("end_seconds")} for item in artifact.get("segments", [])[:12]]
                result[name]["first_spoken_words"] = artifact.get("first_spoken_words")
    return result


def _read_optional(path: Path, name: str, missing: list[str], diagnostics: list[dict]) -> dict | None:
    if not path.is_file():
        missing.append(name); diagnostics.append({"code": f"{name.upper()}_MISSING", "severity": "missing"}); return None
    return _read_json(path)


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvidenceResolutionError(f"EVIDENCE_JSON_INVALID:{path.name}") from error
    if not isinstance(value, dict):
        raise EvidenceResolutionError("EVIDENCE_JSON_OBJECT_REQUIRED")
    return value


def _contained(root: Path, reference: str | None) -> Path:
    if not isinstance(reference, str) or not reference:
        raise EvidenceResolutionError("EVIDENCE_REFERENCE_INVALID")
    candidate = (root / reference).resolve()
    if candidate != root.resolve() and root.resolve() not in candidate.parents:
        raise EvidenceResolutionError("EVIDENCE_PATH_ESCAPES_ROOT")
    return candidate


def _write_new(path: Path, serialized: str) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as output:
        output.write(serialized); temporary = Path(output.name)
    try:
        os.link(temporary, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != serialized:
            raise EvidenceResolutionError("CANONICAL_INSPECTION_CONFLICT")
    finally:
        temporary.unlink(missing_ok=True)


def _write_replace_bytes(path: Path, payload: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent, suffix=".tmp") as output:
        output.write(payload); temporary = Path(output.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _backup_legacy_canonical(path: Path) -> Path:
    original = path.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    backup = path.parent / "legacy-backups" / f"inspection.schema-1.0.{digest[:12]}.json"
    backup.parent.mkdir(parents=True, exist_ok=True)
    if backup.exists():
        if backup.read_bytes() != original:
            raise EvidenceResolutionError("BACKUP_CONFLICT")
        return backup
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=backup.parent, suffix=".tmp") as output:
        output.write(original); temporary = Path(output.name)
    try:
        os.link(temporary, backup)
    except FileExistsError:
        if backup.read_bytes() != original:
            raise EvidenceResolutionError("BACKUP_CONFLICT")
    finally:
        temporary.unlink(missing_ok=True)
    if hashlib.sha256(backup.read_bytes()).hexdigest() != digest:
        raise EvidenceResolutionError("BACKUP_HASH_MISMATCH")
    return backup


def _copy_new(source: Path, target: Path) -> None:
    with source.open("rb") as input_file, tempfile.NamedTemporaryFile("wb", delete=False, dir=target.parent, suffix=".tmp") as output:
        output.write(input_file.read()); temporary = Path(output.name)
    try:
        os.link(temporary, target)
    except FileExistsError:
        if hash_file(target) != hash_file(source):
            raise EvidenceResolutionError("CANONICAL_FRAME_CONFLICT")
    finally:
        temporary.unlink(missing_ok=True)


def _portable(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")


def _is_hash(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value.lower())


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise EvidenceResolutionError(code)
