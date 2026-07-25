"""Bounded Windows OCR evidence extraction for existing format-inspection frames."""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import statistics
import subprocess
import tempfile
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from PIL import Image

from browser_media_acquisition import select_manifest_candidates
from selection_manifest import read_selection_manifest

SCHEMA_VERSION = "1.1"
MIGRATOR_VERSION = "1.1"
DEFAULT_TIMEOUT_SECONDS = 30


class OcrEvidenceError(ValueError):
    """Raised for invalid manifest-bound OCR inputs or engine output."""


class OcrEngine(Protocol):
    def availability(self) -> dict: ...
    def recognize(self, image_path: Path, language: str) -> dict: ...


class WindowsMediaOcrEngine:
    """Windows Runtime OCR through a bounded, JSON-only PowerShell boundary."""

    def __init__(self, script_path: Path | None = None, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        self.script_path = script_path or Path(__file__).resolve().parents[1] / "scripts" / "windows_ocr.ps1"
        self.timeout_seconds = timeout_seconds

    def availability(self) -> dict:
        return self._run("probe")

    def recognize(self, image_path: Path, language: str) -> dict:
        return self._run("recognize", image_path=image_path, language=language)

    def _run(self, mode: str, image_path: Path | None = None, language: str | None = None) -> dict:
        if not self.script_path.is_file():
            raise OcrEvidenceError("Windows OCR helper script is missing")
        command = ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(self.script_path), "-Mode", mode]
        if image_path is not None:
            command += ["-ImagePath", str(image_path.resolve())]
        if language is not None:
            command += ["-Language", language]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=self.timeout_seconds)
        except FileNotFoundError as error:
            raise OcrEvidenceError("PowerShell is unavailable") from error
        except subprocess.TimeoutExpired as error:
            raise OcrEvidenceError("Windows OCR timed out") from error
        if completed.returncode:
            detail = re.sub(r"[\r\n]+", " ", completed.stderr).strip()[:300]
            raise OcrEvidenceError(f"Windows OCR failed: {detail or 'unknown error'}")
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise OcrEvidenceError("Windows OCR returned malformed JSON") from error


def normalize_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _contained(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if root.resolve() not in path.parents:
        raise OcrEvidenceError("inspection frame reference escapes candidate root")
    return path


def _write_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as output:
        json.dump(payload, output, ensure_ascii=False, indent=2); output.write("\n"); temporary = Path(output.name)
    os.replace(temporary, path)


def _validate_blocks(blocks: list[dict], image_path: Path) -> None:
    with Image.open(image_path) as image:
        width, height = image.size
    for block in blocks:
        box = block.get("box") or {}
        try:
            x, y, box_width, box_height = (float(box[key]) for key in ("x", "y", "width", "height"))
        except (KeyError, TypeError, ValueError) as error:
            raise OcrEvidenceError("Windows OCR returned malformed bounding box") from error
        if min(x, y, box_width, box_height) < 0 or x + box_width > width or y + box_height > height:
            raise OcrEvidenceError("Windows OCR returned out-of-bounds bounding box")


def _deduplicate(observations: list[dict]) -> list[dict]:
    events: list[dict] = []
    for observation in observations:
        text = observation["normalized_text"]
        if not text:
            continue
        key = re.sub(r"[^\w\s]", "", text.casefold())
        if events and events[-1]["dedupe_key"] == key:
            events[-1]["last_seen_at_sec"] = observation["sampled_at_sec"]
            events[-1]["supporting_observation_ids"].append(observation["observation_id"])
            continue
        events.append({"event_id": f"event-{len(events) + 1:03d}", "text": text, "dedupe_key": key, "matching_method": "exact_normalized" if text == key else "punctuation_light", "first_seen_at_sec": observation["sampled_at_sec"], "last_seen_at_sec": observation["sampled_at_sec"], "temporal_precision": "sampled_frame", "supporting_observation_ids": [observation["observation_id"]]})
    for event in events:
        event.pop("dedupe_key")
    return events


@dataclass(frozen=True)
class OcrRunRequest:
    selection_manifest_path: Path
    inspection_root: Path
    output_root: Path
    candidate_ids: tuple[str, ...] = ()
    limit: int | None = None
    language: str = "en-US"
    reuse: bool = True


@dataclass(frozen=True)
class OcrReferenceMigrationRequest:
    """Manifest-bound, ref-only migration of already validated OCR evidence."""

    selection_manifest_path: Path
    inspection_root: Path
    output_root: Path
    candidate_ids: tuple[str, ...] = ()
    limit: int | None = None
    apply: bool = False


def run_ocr_evidence(request: OcrRunRequest, engine: OcrEngine | None = None) -> dict:
    engine = engine or WindowsMediaOcrEngine()
    availability = engine.availability()
    if not availability.get("available") or request.language not in availability.get("languages", []):
        raise OcrEvidenceError(f"Windows OCR language unavailable: {request.language}")
    manifest = read_selection_manifest(request.selection_manifest_path)
    candidates = select_manifest_candidates(manifest, request.candidate_ids, request.limit)
    results = [_run_candidate(candidate, manifest, request, engine, availability) for candidate in candidates]
    return {"schema_version": SCHEMA_VERSION, "radar_run_id": manifest.radar_run_id, "selection_manifest_reference": str(request.selection_manifest_path), "selection_manifest_hash": manifest.manifest_hash, "engine": availability, "candidates": results, "status": "COMPLETED" if all(item["status"] == "COMPLETED" for item in results) else "DEGRADED" if any(item["status"] != "FAILED" for item in results) else "FAILED"}


def _run_candidate(candidate, manifest, request: OcrRunRequest, engine: OcrEngine, availability: dict) -> dict:
    root = (request.inspection_root / candidate.video_id).resolve()
    inspection_path = root / "inspection.json"
    target = request.output_root / manifest.radar_run_id / "candidates" / candidate.video_id / "ocr" / "ocr_result.json"
    if not inspection_path.is_file():
        return {"candidate_video_id": candidate.video_id, "rank": candidate.rank, "status": "FAILED", "errors": ["inspection result is missing"]}
    inspection = json.loads(inspection_path.read_text(encoding="utf-8"))
    if inspection.get("status") not in {"COMPLETED", "DEGRADED"}:
        return {"candidate_video_id": candidate.video_id, "rank": candidate.rank, "status": "FAILED", "errors": ["inspection result is not usable"]}
    inspection_hash = _hash(inspection_path)
    if request.reuse and _reusable_result(target, root, candidate.video_id, manifest.manifest_hash, inspection_hash, request.language, availability):
        reused = json.loads(target.read_text(encoding="utf-8"))
        return {**reused, "reuse_status": "REUSED"}
    observations: list[dict] = []
    for index, frame in enumerate(inspection.get("sampling", {}).get("frame_results", [])):
        if frame.get("status") != "success":
            continue
        path = _contained(root, f"frames/{frame['frame_path']}")
        if not path.is_file():
            observations.append({"observation_id": f"obs-{index:03d}", "sampled_at_sec": frame.get("effective_timestamp_seconds"), "status": "FAILED", "errors": ["sampled frame is missing"]})
            continue
        started = time.monotonic()
        try:
            recognized = engine.recognize(path, request.language)
            raw = recognized.get("text") or ""
            normalized = normalize_text(raw)
            blocks = recognized.get("blocks") or []
            _validate_blocks(blocks, path)
            observations.append({"observation_id": f"obs-{index:03d}", "frame_ref": str(path.relative_to(root)).replace("\\", "/"), "frame_sha256": _hash(path), "sampled_at_sec": frame.get("effective_timestamp_seconds"), "raw_text": raw, "normalized_text": normalized, "blocks": blocks, "confidence": recognized.get("confidence"), "preprocessing_profile": "original", "status": "COMPLETED" if normalized else "COMPLETED_EMPTY", "human_verified": False, "elapsed_ms": round((time.monotonic() - started) * 1000, 2), "warnings": [], "errors": []})
        except OcrEvidenceError as error:
            observations.append({"observation_id": f"obs-{index:03d}", "sampled_at_sec": frame.get("effective_timestamp_seconds"), "status": "FAILED", "errors": [str(error)]})
    completed = sum(item["status"] == "COMPLETED" for item in observations); empty = sum(item["status"] == "COMPLETED_EMPTY" for item in observations); failed = sum(item["status"] == "FAILED" for item in observations)
    events = _deduplicate([item for item in observations if item["status"] == "COMPLETED"])
    hook = next((event for event in events if event["text"]), None)
    status = "COMPLETED" if not failed else "DEGRADED" if completed or empty else "FAILED"
    payload = {"schema_version": SCHEMA_VERSION, "candidate_video_id": candidate.video_id, "rank": candidate.rank, "selection_manifest_hash": manifest.manifest_hash, "inspection_result_ref": "inspection.json", "inspection_result_sha256": inspection_hash, "inspection_schema_version": inspection.get("schema_version"), "inspection_media_sha256": inspection.get("media_sha256"), "engine": availability, "requested_language": request.language, "requested_frame_count": len(observations), "processed_frame_count": completed + empty + failed, "completed_frame_count": completed, "empty_frame_count": empty, "failed_frame_count": failed, "ordered_observations": observations, "text_events": events, "first_text_hook": None if hook is None else {"hook_text": hook["text"], "first_seen_at_sec": hook["first_seen_at_sec"], "supporting_observation_ids": hook["supporting_observation_ids"], "confidence_source": "unavailable"}, "first_text_hook_reason": None if hook else "no_reliable_text_observed", "status": status, "timings": {"average_elapsed_ms": round(statistics.mean([item["elapsed_ms"] for item in observations if "elapsed_ms" in item]), 2) if any("elapsed_ms" in item for item in observations) else None}, "warnings": ["Windows Media OCR does not expose confidence."], "errors": []}
    payload["result_sha256"] = _result_hash(payload)
    _write_atomic(target, payload)
    return payload


def _reusable_result(target: Path, inspection_root: Path, candidate_id: str, manifest_hash: str, inspection_hash: str, language: str, availability: dict) -> bool:
    if not target.is_file():
        return False
    try:
        result = json.loads(target.read_text(encoding="utf-8"))
        if result.get("schema_version") != SCHEMA_VERSION or result.get("candidate_video_id") != candidate_id or result.get("selection_manifest_hash") != manifest_hash or result.get("inspection_result_ref") != "inspection.json" or result.get("inspection_result_sha256") != inspection_hash or result.get("requested_language") != language or result.get("result_sha256") != _result_hash(result):
            return False
        engine = result.get("engine", {})
        if engine.get("engine_id") != availability.get("engine_id") or engine.get("engine_version") != availability.get("engine_version"):
            return False
        for observation in result.get("ordered_observations", []):
            if observation.get("status") not in {"COMPLETED", "COMPLETED_EMPTY"}:
                continue
            if observation.get("preprocessing_profile") != "original":
                return False
            path = _contained(inspection_root, observation["frame_ref"])
            if not path.is_file() or _hash(path) != observation.get("frame_sha256"):
                return False
        return result.get("status") in {"COMPLETED", "DEGRADED"}
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False


def migrate_ocr_evidence_references(request: OcrReferenceMigrationRequest) -> dict:
    """Audit or atomically canonicalize OCR inspection references without OCR execution."""
    manifest = read_selection_manifest(request.selection_manifest_path)
    candidates = select_manifest_candidates(manifest, request.candidate_ids, request.limit)
    results = [_migrate_candidate_reference(candidate, manifest, request) for candidate in candidates]
    if request.apply and any(item["status"] == "REJECTED" for item in results):
        for item in results:
            if item["status"] == "READY":
                item["status"] = "BLOCKED_BY_AUDIT"
    elif request.apply:
        for item in results:
            if item["status"] == "READY":
                _apply_reference_migration(Path(item["ocr_path"]), Path(item["inspection_path"]), manifest.manifest_hash)
                item["status"] = "MIGRATED"
            item.pop("ocr_path", None); item.pop("inspection_path", None)
    else:
        for item in results:
            item.pop("ocr_path", None); item.pop("inspection_path", None)
    return {"schema_version": SCHEMA_VERSION, "radar_run_id": manifest.radar_run_id, "apply": request.apply, "status": "COMPLETED" if all(item["status"] in {"MIGRATED", "ALREADY_CANONICAL", "READY"} for item in results) else "FAILED", "candidates": results}


def verify_ocr_evidence_reuse(request: OcrReferenceMigrationRequest) -> dict:
    """Verify reusable canonical OCR evidence without probing or invoking the OCR engine."""
    audit = migrate_ocr_evidence_references(request)
    candidates = [
        {"candidate_video_id": item["candidate_video_id"], "rank": item["rank"], "status": "REUSED" if item["status"] == "ALREADY_CANONICAL" else "NOT_REUSABLE"}
        for item in audit["candidates"]
    ]
    return {"schema_version": SCHEMA_VERSION, "radar_run_id": audit["radar_run_id"], "status": "COMPLETED" if all(item["status"] == "REUSED" for item in candidates) else "FAILED", "candidates": candidates}


def _migrate_candidate_reference(candidate, manifest, request: OcrReferenceMigrationRequest) -> dict:
    inspection_path = request.inspection_root / candidate.video_id / "inspection.json"
    ocr_path = request.output_root / manifest.radar_run_id / "candidates" / candidate.video_id / "ocr" / "ocr_result.json"
    result = {"candidate_video_id": candidate.video_id, "rank": candidate.rank, "ocr_path": str(ocr_path), "inspection_path": str(inspection_path)}
    try:
        ocr = json.loads(ocr_path.read_text(encoding="utf-8"))
        inspection = json.loads(inspection_path.read_text(encoding="utf-8"))
        _validate_migration_source(ocr, inspection, ocr_path, inspection_path, candidate.video_id, candidate.rank, manifest.manifest_hash)
        if _is_canonical_result(ocr, inspection_path):
            return result | {"status": "ALREADY_CANONICAL", "backup": "NOT_REQUIRED"}
        original = ocr_path.read_bytes()
        backup = _backup_path(ocr_path, original)
        if backup.exists() and backup.read_bytes() != original:
            raise OcrEvidenceError("OCR backup conflict")
        result["status"] = "READY"; result["backup"] = "REQUIRED"
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        result["status"] = "REJECTED"; result["error"] = str(error)
    return result


def _validate_migration_source(ocr: dict, inspection: dict, ocr_path: Path, inspection_path: Path, candidate_id: str, rank: int, manifest_hash: str) -> None:
    _assert_finite_json(ocr)
    if ocr.get("schema_version") not in {"1.0", SCHEMA_VERSION}:
        raise OcrEvidenceError("unsupported OCR schema")
    if inspection.get("schema_version") != "1.1" or inspection.get("status") not in {"COMPLETED", "DEGRADED"}:
        raise OcrEvidenceError("canonical inspection is not usable")
    if ocr.get("candidate_video_id") != candidate_id or ocr.get("rank") != rank or ocr.get("selection_manifest_hash") != manifest_hash:
        raise OcrEvidenceError("OCR candidate identity does not match manifest")
    if inspection.get("video_id") != candidate_id or ocr.get("inspection_media_sha256") != inspection.get("media_sha256"):
        raise OcrEvidenceError("OCR inspection media identity does not match")
    frames = {f"frames/{item['frame_path']}": item for item in inspection.get("sampling", {}).get("frame_results", []) if item.get("status") == "success"}
    observations = ocr.get("ordered_observations", [])
    if not isinstance(observations, list) or len(observations) != len(frames):
        raise OcrEvidenceError("OCR frame count does not match canonical inspection")
    if ocr.get("requested_frame_count") != len(frames) or ocr.get("processed_frame_count") != len(observations):
        raise OcrEvidenceError("OCR frame counters do not match canonical inspection")
    engine = ocr.get("engine", {})
    languages = engine.get("languages")
    if not engine.get("engine_id") or not engine.get("engine_version") or engine.get("available") is not True:
        raise OcrEvidenceError("OCR engine identity is incomplete")
    if not isinstance(languages, list) or not languages or ocr.get("requested_language") not in languages:
        raise OcrEvidenceError("OCR language identity is incomplete")
    for observation in observations:
        if observation.get("status") not in {"COMPLETED", "COMPLETED_EMPTY"}:
            raise OcrEvidenceError("OCR observation set is not safe for ref-only migration")
        frame = frames.get(observation.get("frame_ref"))
        if frame is None or frame.get("effective_timestamp_seconds") != observation.get("sampled_at_sec"):
            raise OcrEvidenceError("OCR frame timestamp does not match canonical inspection")
        path = _contained(inspection_path.parent, observation["frame_ref"])
        if not path.is_file() or _hash(path) != observation.get("frame_sha256"):
            raise OcrEvidenceError("OCR frame hash does not match canonical inspection")


def _is_canonical_result(ocr: dict, inspection_path: Path) -> bool:
    return ocr.get("schema_version") == SCHEMA_VERSION and ocr.get("inspection_result_ref") == "inspection.json" and ocr.get("inspection_result_sha256") == _hash(inspection_path) and ocr.get("inspection_schema_version") == "1.1" and ocr.get("result_sha256") == _result_hash(ocr)


def _apply_reference_migration(ocr_path: Path, inspection_path: Path, manifest_hash: str) -> None:
    original = ocr_path.read_bytes()
    backup = _backup_path(ocr_path, original)
    if backup.exists() and backup.read_bytes() != original:
        raise OcrEvidenceError("OCR backup conflict")
    if not backup.exists():
        _write_atomic_bytes(backup, original)
    migrated = json.loads(original)
    migrated.update({"schema_version": SCHEMA_VERSION, "inspection_result_ref": "inspection.json", "inspection_result_sha256": _hash(inspection_path), "inspection_schema_version": "1.1"})
    migrated["migration"] = {"type": "REF_ONLY", "source_schema_version": json.loads(original).get("schema_version"), "migrator_version": MIGRATOR_VERSION, "selection_manifest_hash": manifest_hash, "backup_ref": f"legacy-backups/{backup.name}"}
    migrated.pop("result_sha256", None)
    migrated["result_sha256"] = _result_hash(migrated)
    _write_atomic(ocr_path, migrated)


def _backup_path(ocr_path: Path, original: bytes) -> Path:
    schema = json.loads(original).get("schema_version", "unknown")
    return ocr_path.parent / "legacy-backups" / f"ocr.{schema}.{hashlib.sha256(original).hexdigest()[:12]}.json"


def _result_hash(payload: dict) -> str:
    copy = dict(payload); copy.pop("result_sha256", None)
    return hashlib.sha256(json.dumps(copy, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _write_atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent, suffix=".tmp") as output:
        output.write(payload); temporary = Path(output.name)
    os.replace(temporary, path)


def _assert_finite_json(value: object) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise OcrEvidenceError("OCR result contains a non-finite number")
    if isinstance(value, dict):
        for item in value.values():
            _assert_finite_json(item)
    if isinstance(value, list):
        for item in value:
            _assert_finite_json(item)
