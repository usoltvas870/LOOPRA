"""Local, manifest-bound speech transcription evidence for acquired media."""
from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from browser_media_acquisition import select_manifest_candidates
from selection_manifest import read_selection_manifest

SCHEMA_VERSION = "1.1"
LEGACY_SCHEMA_VERSION = "1.0"
# Faster-whisper word boundaries can trail their containing segment by up to
# 0.26 seconds in the accepted local evidence; 0.30 keeps that engine rounding
# margin while rejecting materially detached words.
TIMESTAMP_TOLERANCE_SECONDS = 0.30
ENGINE_ID = "faster-whisper"
MODEL_ID = "Systran/faster-whisper-base"
DEFAULT_OPTIONS = {"device": "cpu", "compute_type": "int8", "cpu_threads": 8, "beam_size": 5, "vad_filter": False, "word_timestamps": True}


class TranscriptionEvidenceError(ValueError):
    """Raised when manifest-bound transcription evidence cannot be produced."""


class TranscriptionEngine(Protocol):
    def availability(self) -> dict: ...
    def transcribe(self, media_path: Path, language: str | None, options: dict) -> dict: ...


def normalize_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as output:
        json.dump(payload, output, ensure_ascii=False, indent=2, allow_nan=False)
        output.write("\n")
        temporary = Path(output.name)
    os.replace(temporary, path)


class FasterWhisperEngine:
    """CPU-only adapter that never downloads a model at runtime."""

    def __init__(self, model_id: str = MODEL_ID) -> None:
        self.model_id = model_id
        self._model = None

    def availability(self) -> dict:
        try:
            from faster_whisper import __version__ as version
        except (ImportError, AttributeError):
            try:
                from importlib.metadata import version as package_version
                version = package_version("faster-whisper")
            except Exception:
                return {"available": False, "engine_id": ENGINE_ID, "reason": "faster-whisper is not installed"}
        cache = Path.home() / ".cache" / "huggingface" / "hub" / "models--Systran--faster-whisper-base" / "snapshots"
        snapshots = sorted(path for path in cache.iterdir() if path.is_dir()) if cache.is_dir() else []
        model_path = snapshots[-1] if snapshots else None
        required = ("model.bin", "config.json", "tokenizer.json")
        cached = model_path is not None and all((model_path / name).is_file() for name in required)
        return {"available": cached, "engine_id": ENGINE_ID, "engine_version": version, "model_id": self.model_id,
                "model_revision": model_path.name if model_path else None, "model_cached": cached,
                "device": "cpu", "compute_type": "int8", "input_method": "direct_mp4", "downloads_allowed": False,
                "capabilities": {"language_detection": True, "segment_timestamps": True, "word_timestamps": True,
                                 "avg_logprob": True, "no_speech_prob": True}}

    def transcribe(self, media_path: Path, language: str | None, options: dict) -> dict:
        availability = self.availability()
        if not availability.get("available"):
            raise TranscriptionEvidenceError("approved faster-whisper base model is not cached")
        from faster_whisper import WhisperModel
        if self._model is None:
            cache = Path.home() / ".cache" / "huggingface" / "hub" / "models--Systran--faster-whisper-base" / "snapshots" / availability["model_revision"]
            self._model = WhisperModel(str(cache), device=options["device"], compute_type=options["compute_type"], cpu_threads=options["cpu_threads"], local_files_only=True)
        segments, info = self._model.transcribe(str(media_path), language=language, beam_size=options["beam_size"], vad_filter=options["vad_filter"], word_timestamps=options["word_timestamps"])
        values = []
        for item in segments:
            values.append({"start_seconds": item.start, "end_seconds": item.end, "raw_text": item.text,
                           "avg_logprob": item.avg_logprob, "no_speech_prob": item.no_speech_prob,
                           "words": [{"start_seconds": word.start, "end_seconds": word.end, "word": word.word,
                                      "probability": getattr(word, "probability", None)} for word in (item.words or [])]})
        return {"language": info.language, "language_probability": getattr(info, "language_probability", None), "segments": values}


@dataclass(frozen=True)
class TranscriptionRunRequest:
    selection_manifest_path: Path
    acquisition_root: Path
    inspection_root: Path
    output_root: Path
    candidate_ids: tuple[str, ...] = ()
    limit: int | None = None
    language: str | None = None
    reuse: bool = True
    options: dict | None = None


def run_transcription_evidence(request: TranscriptionRunRequest, engine: TranscriptionEngine | None = None) -> dict:
    engine = engine or FasterWhisperEngine()
    availability = engine.availability()
    if not availability.get("available"):
        raise TranscriptionEvidenceError(availability.get("reason", "local transcription engine or model is unavailable"))
    manifest = read_selection_manifest(request.selection_manifest_path)
    candidates = select_manifest_candidates(manifest, request.candidate_ids, request.limit)
    options = {**DEFAULT_OPTIONS, **(request.options or {})}
    prepared = [_prepare(candidate, manifest, request, availability, options) for candidate in candidates]
    results = []
    for item in prepared:
        if item.get("reused"):
            results.append(item["result"] | {"reuse_status": "REUSED"})
        elif item.get("legacy"):
            result = _migrate_legacy_result(item)
            _write_atomic(item["target"], result); results.append(result | {"reuse_status": "MIGRATED"})
        elif item.get("no_audio"):
            result = _no_audio_result(item)
            _write_atomic(item["target"], result); results.append(result)
        else:
            results.append(_transcribe(item, engine, request.language, options))
    status = "COMPLETED" if all(item["status"].startswith("COMPLETED") for item in results) else "DEGRADED" if any(item["status"] != "FAILED" for item in results) else "FAILED"
    return {"schema_version": SCHEMA_VERSION, "radar_run_id": manifest.radar_run_id,
            "selection_manifest_reference": request.selection_manifest_path.name, "selection_manifest_hash": manifest.manifest_hash,
            "engine": availability, "candidates": results, "status": status}


def _prepare(candidate, manifest, request, availability, options) -> dict:
    acquisition_root = (request.acquisition_root / candidate.video_id).resolve()
    record_path = acquisition_root / "acquisition_record.json"
    inspection_root = (request.inspection_root / candidate.video_id).resolve()
    inspection_path = inspection_root / "inspection.json"
    target = request.output_root / manifest.radar_run_id / "candidates" / candidate.video_id / "transcription" / "transcription_result.json"
    base = {"candidate": candidate, "target": target, "record_path": record_path, "inspection_path": inspection_path,
            "availability": availability, "options": options, "manifest_hash": manifest.manifest_hash, "language": request.language}
    if not record_path.is_file() or not inspection_path.is_file():
        return base | {"error": "acquisition record or final inspection result is missing"}
    record, inspection = json.loads(record_path.read_text(encoding="utf-8")), json.loads(inspection_path.read_text(encoding="utf-8"))
    media_ref = record.get("local_media_path")
    media = (request.acquisition_root / media_ref).resolve() if media_ref else None
    if media is not None and request.acquisition_root.resolve() not in media.parents:
        return base | {"error": "acquisition media reference escapes the acquisition root"}
    if not media or not media.is_file() or _hash(media) != record.get("media_sha256"):
        return base | {"error": "acquired media is missing or its SHA-256 does not match the record"}
    if inspection.get("media_sha256") != record.get("media_sha256"):
        return base | {"error": "inspection media SHA-256 does not match acquisition record"}
    context = base | {"record": record, "inspection": inspection, "media": media, "media_sha256": record["media_sha256"],
                      "record_hash": _hash(record_path), "inspection_hash": _hash(inspection_path)}
    if request.reuse and target.is_file():
        existing = json.loads(target.read_text(encoding="utf-8"))
        if _reusable_result(existing, context, manifest.manifest_hash, request.language):
            return context | {"reused": True, "result": existing}
        if _migratable_legacy_result(existing, context, manifest.manifest_hash, request.language):
            return context | {"legacy": True, "result": existing}
    return context | {"no_audio": not bool(inspection.get("media_facts", {}).get("audio_present"))}


def _base(item: dict) -> dict:
    candidate, inspection, record = item["candidate"], item["inspection"], item["record"]
    return {"schema_version": SCHEMA_VERSION, "candidate_video_id": candidate.video_id, "rank": candidate.rank,
            "selection_manifest_hash": item["manifest_hash"],
            "acquisition_record_ref": f"{candidate.video_id}/acquisition_record.json", "acquisition_record_sha256": item["record_hash"],
            "media_ref": record.get("local_media_path"), "media_sha256": item["media_sha256"],
            "inspection_result_ref": "inspection.json", "inspection_result_sha256": item["inspection_hash"],
            "audio": {"present": inspection.get("media_facts", {}).get("audio_present"), "codec": inspection.get("media_facts", {}).get("audio_codec"),
                      "sample_rate": inspection.get("media_facts", {}).get("sample_rate"), "channels": inspection.get("media_facts", {}).get("channels"),
                      "duration_seconds": inspection.get("media_facts", {}).get("duration_seconds")},
            "engine": item["availability"], "input_method": "direct_mp4", "human_verified": False,
            "requested_language": item.get("language"), "decoding_options": item["options"]}


def _finite(value, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise TranscriptionEvidenceError(f"{name} must be numeric") from error
    if not math.isfinite(number):
        raise TranscriptionEvidenceError(f"{name} must be finite")
    return number


def _optional_finite(value, name: str) -> float | None:
    return None if value is None else _finite(value, name)


def _validate_segment(raw: dict, duration: float | None, index: int) -> dict:
    start = _finite(raw.get("start_seconds"), "segment start_seconds")
    end = _finite(raw.get("end_seconds"), "segment end_seconds")
    if start < 0 or end < start or (duration is not None and end > duration + TIMESTAMP_TOLERANCE_SECONDS):
        raise TranscriptionEvidenceError("engine returned invalid segment timestamps")
    words = []
    for word in raw.get("words") or []:
        word_start = _finite(word.get("start_seconds"), "word start_seconds")
        word_end = _finite(word.get("end_seconds"), "word end_seconds")
        if word_start < start - TIMESTAMP_TOLERANCE_SECONDS or word_end > end + TIMESTAMP_TOLERANCE_SECONDS or word_start < 0 or word_end < word_start:
            raise TranscriptionEvidenceError("engine returned word timestamps outside its segment")
        words.append({"start_seconds": word_start, "end_seconds": word_end, "word": word.get("word", ""), "probability": _optional_finite(word.get("probability"), "word probability")})
    return {"segment_id": f"segment-{index:04d}", "start_seconds": start, "end_seconds": end, "raw_text": raw.get("raw_text") or "",
            "normalized_text": normalize_text(raw.get("raw_text") or ""), "avg_logprob": _optional_finite(raw.get("avg_logprob"), "avg_logprob"),
            "no_speech_prob": _optional_finite(raw.get("no_speech_prob"), "no_speech_prob"), "words": words, "human_verified": False}


def _first_spoken_words(segments: list[dict]) -> dict | None:
    first = next((segment for segment in sorted(segments, key=lambda item: (item["start_seconds"], item["segment_id"])) if segment["normalized_text"]), None)
    if first is None:
        return None
    return {"text": " ".join(first["normalized_text"].split()[:12]), "start_sec": first["start_seconds"], "end_sec": first["end_seconds"],
            "supporting_segment_id": first["segment_id"], "source": "transcript_segment", "human_verified": False,
            "selection_rule": "first_reliable_accepted_segment"}


def _no_audio_result(item: dict) -> dict:
    payload = _base(item) | {"status": "COMPLETED_NO_AUDIO", "language": None, "language_probability": None, "segments": [],
                              "rejected_observations": [], "first_spoken_words": None, "first_spoken_words_reason": "no_audio_stream",
                              "completeness": {"processed_duration_seconds": 0, "media_duration_seconds": item["inspection"]["media_facts"].get("duration_seconds"), "partial": False},
                              "warnings": [], "errors": [], "timings": {"elapsed_seconds": 0, "realtime_factor": None}}
    return payload


def _transcribe(item: dict, engine: TranscriptionEngine, language: str | None, options: dict) -> dict:
    if item.get("error"):
        return {"candidate_video_id": item["candidate"].video_id, "rank": item["candidate"].rank, "status": "FAILED", "errors": [item["error"]]}
    started = time.monotonic()
    try:
        response = engine.transcribe(item["media"], language, options)
        duration = item["inspection"]["media_facts"].get("duration_seconds")
        accepted, rejected = [], []
        language_probability = _optional_finite(response.get("language_probability"), "language probability")
        for index, raw in enumerate(response.get("segments", []), 1):
            observation = _validate_segment(raw, duration, index)
            low_speech = observation["no_speech_prob"] is not None and observation["no_speech_prob"] >= .6 and (observation["avg_logprob"] is None or observation["avg_logprob"] < 0)
            if not observation["normalized_text"] or low_speech:
                rejected.append(observation | {"rejection_reason": "empty_text" if not observation["normalized_text"] else "high_no_speech_probability"})
            else:
                accepted.append(observation)
        elapsed = _finite(round(time.monotonic() - started, 3), "elapsed_seconds")
        first = _first_spoken_words(accepted)
        payload = _base(item) | {"status": "COMPLETED" if accepted else "COMPLETED_NO_SPEECH", "language": response.get("language"),
                                  "language_probability": language_probability, "segments": accepted, "rejected_observations": rejected,
                                  "first_spoken_words": first,
                                  "first_spoken_words_reason": None if first else "no_reliable_speech_observed",
                                  "completeness": {"processed_duration_seconds": duration, "media_duration_seconds": duration, "partial": False, "segment_count": len(accepted)},
                                  "warnings": [], "errors": [], "timings": {"elapsed_seconds": elapsed, "realtime_factor": _optional_finite(round(elapsed / duration, 4), "realtime_factor") if duration else None}}
    except (OSError, ValueError, KeyError, TranscriptionEvidenceError) as error:
        payload = {"candidate_video_id": item["candidate"].video_id, "rank": item["candidate"].rank, "status": "FAILED", "errors": [str(error)]}
    _write_atomic(item["target"], payload)
    return payload


def _same_identity(result: dict, item: dict, manifest_hash: str, language: str | None) -> bool:
    engine = result.get("engine", {})
    available = item["availability"]
    return result.get("candidate_video_id") == item["candidate"].video_id and result.get("selection_manifest_hash") == manifest_hash and result.get("media_sha256") == item["media_sha256"] and result.get("acquisition_record_sha256") == item["record_hash"] and result.get("inspection_result_sha256") == item["inspection_hash"] and result.get("requested_language") == language and result.get("decoding_options") == item["options"] and engine.get("engine_id") == available.get("engine_id") and engine.get("engine_version") == available.get("engine_version") and engine.get("model_id") == available.get("model_id") and engine.get("model_revision") == available.get("model_revision")


def _reusable_result(result: dict, item: dict, manifest_hash: str, language: str | None) -> bool:
    try:
        return result.get("schema_version") == SCHEMA_VERSION and _same_identity(result, item, manifest_hash, language) and result.get("status") in {"COMPLETED", "COMPLETED_NO_SPEECH", "COMPLETED_NO_AUDIO"} and _valid_current_result(result)
    except (TypeError, ValueError, KeyError):
        return False


def _migratable_legacy_result(result: dict, item: dict, manifest_hash: str, language: str | None) -> bool:
    return result.get("schema_version") == LEGACY_SCHEMA_VERSION and _same_identity(result, item, manifest_hash, language) and result.get("status") in {"COMPLETED", "COMPLETED_NO_SPEECH", "COMPLETED_NO_AUDIO"}


def _migrate_legacy_result(item: dict) -> dict:
    legacy = item["result"]
    duration = legacy.get("audio", {}).get("duration_seconds")
    duration = _optional_finite(duration, "media duration")
    accepted = [_validate_segment(segment, duration, index) for index, segment in enumerate(legacy.get("segments", []), 1)]
    rejected = [_validate_segment(segment, duration, index) | {"rejection_reason": segment.get("rejection_reason", "legacy_rejected_observation")} for index, segment in enumerate(legacy.get("rejected_observations", []), 1)]
    first = _first_spoken_words(accepted)
    migrated = legacy | {"schema_version": SCHEMA_VERSION, "migrated_from_schema_version": LEGACY_SCHEMA_VERSION, "segments": accepted, "rejected_observations": rejected,
                         "first_spoken_words": first, "first_spoken_words_reason": None if first else legacy.get("first_spoken_words_reason", "no_reliable_speech_observed")}
    _validate_numeric_result(migrated)
    return migrated


def _validate_numeric_result(result: dict) -> None:
    _optional_finite(result.get("language_probability"), "language probability")
    for name, value in result.get("timings", {}).items():
        _optional_finite(value, name)


def _valid_current_result(result: dict) -> bool:
    _validate_numeric_result(result)
    duration = _optional_finite(result.get("audio", {}).get("duration_seconds"), "media duration")
    accepted = [_validate_segment(segment, duration, index) for index, segment in enumerate(result.get("segments", []), 1)]
    first = result.get("first_spoken_words")
    if first is None:
        return not accepted
    return first.get("supporting_segment_id") in {segment["segment_id"] for segment in accepted} and first.get("start_sec") == next(segment["start_seconds"] for segment in accepted if segment["segment_id"] == first.get("supporting_segment_id")) and first.get("human_verified") is False
