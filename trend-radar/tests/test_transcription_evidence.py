from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

from selection_manifest import build_selection_manifest, write_selection_manifest
from transcription_evidence import SCHEMA_VERSION, TranscriptionEvidenceError, TranscriptionRunRequest, normalize_text, run_transcription_evidence


class FakeEngine:
    def __init__(self, segments: list[dict]) -> None:
        self.segments, self.calls = segments, 0

    def availability(self) -> dict:
        return {"available": True, "engine_id": "fake", "engine_version": "1", "model_id": "fake-base", "model_revision": "r1"}

    def transcribe(self, media_path: Path, language: str | None, options: dict) -> dict:
        self.calls += 1
        return {"language": language or "ru", "language_probability": .99, "segments": self.segments}


def _candidate(video_id: str, rank: int) -> dict:
    return {"video_id": video_id, "author_username": "test", "source_type": "test", "source_value": "test", "url": f"https://example.test/{video_id}", "caption": "test", "views": 1, "likes": 1, "comments": 0, "shares": 0, "author_followers": 1, "published_at": "2026-07-24T00:00:00Z", "collected_at": "2026-07-24T00:00:00Z", "final_score": 1, "reach_score": 1, "engagement_score": 1, "freshness_score": 1, "momentum_proxy": 1, "data_confidence": "HIGH", "identity_confidence": "HIGH", "classification": "CURRENT", "provenance": {"primary_source_type": "test", "primary_source_value": "test"}}


def _fixture(tmp_path: Path, *, audio: bool = True) -> tuple[Path, Path, Path]:
    manifest = write_selection_manifest(build_selection_manifest([_candidate("1", 1)], radar_run_id="fixture"), tmp_path / "runs")
    acquisition = tmp_path / "acquisitions" / "1"; inspection = tmp_path / "inspections" / "1"; acquisition.mkdir(parents=True); inspection.mkdir(parents=True)
    media = acquisition / "source.mp4"; media.write_bytes(b"synthetic-media"); digest = hashlib.sha256(media.read_bytes()).hexdigest()
    (acquisition / "acquisition_record.json").write_text(json.dumps({"candidate_video_id": "1", "local_media_path": "1/source.mp4", "media_sha256": digest}), encoding="utf-8")
    (inspection / "inspection.json").write_text(json.dumps({"media_sha256": digest, "media_facts": {"audio_present": audio, "audio_codec": "aac", "sample_rate": "44100", "channels": 2, "duration_seconds": 5.0}}), encoding="utf-8")
    return manifest, tmp_path / "acquisitions", tmp_path / "inspections"


def test_normalization_is_mechanical_for_cyrillic() -> None:
    assert normalize_text("  Привет\n LOOPRA ") == "Привет LOOPRA"


def test_segments_are_timestamped_and_reused_without_engine_load(tmp_path: Path) -> None:
    manifest, acquisitions, inspections = _fixture(tmp_path)
    engine = FakeEngine([{"start_seconds": 0, "end_seconds": 1.2, "raw_text": " Привет  LOOPRA ", "avg_logprob": -.1, "no_speech_prob": .01, "words": []}])
    request = TranscriptionRunRequest(manifest, acquisitions, inspections, tmp_path / "out")
    result = run_transcription_evidence(request, engine)
    candidate = result["candidates"][0]
    assert candidate["status"] == "COMPLETED" and candidate["segments"][0]["normalized_text"] == "Привет LOOPRA"
    first = candidate["first_spoken_words"]
    assert first["text"] == "Привет LOOPRA" and first["start_sec"] == 0 and first["supporting_segment_id"] == "segment-0001"
    assert first["human_verified"] is False and candidate["human_verified"] is False and engine.calls == 1
    reused = run_transcription_evidence(request, engine)
    assert reused["candidates"][0]["reuse_status"] == "REUSED" and engine.calls == 1


def test_no_audio_does_not_load_engine(tmp_path: Path) -> None:
    manifest, acquisitions, inspections = _fixture(tmp_path, audio=False)
    engine = FakeEngine([])
    result = run_transcription_evidence(TranscriptionRunRequest(manifest, acquisitions, inspections, tmp_path / "out"), engine)
    assert result["candidates"][0]["status"] == "COMPLETED_NO_AUDIO" and engine.calls == 0


def test_high_no_speech_segment_is_preserved_as_rejected_observation(tmp_path: Path) -> None:
    manifest, acquisitions, inspections = _fixture(tmp_path)
    engine = FakeEngine([{"start_seconds": 0, "end_seconds": 1, "raw_text": "noise", "avg_logprob": -.8, "no_speech_prob": .9, "words": []}])
    result = run_transcription_evidence(TranscriptionRunRequest(manifest, acquisitions, inspections, tmp_path / "out"), engine)
    candidate = result["candidates"][0]
    assert candidate["status"] == "COMPLETED_NO_SPEECH" and candidate["rejected_observations"][0]["raw_text"] == "noise"


def test_first_spoken_words_uses_first_reliable_segment_in_temporal_order(tmp_path: Path) -> None:
    manifest, acquisitions, inspections = _fixture(tmp_path)
    engine = FakeEngine([
        {"start_seconds": 2, "end_seconds": 3, "raw_text": "later", "avg_logprob": -.1, "no_speech_prob": .01, "words": []},
        {"start_seconds": 0, "end_seconds": 1, "raw_text": "earlier", "avg_logprob": -.1, "no_speech_prob": .01, "words": []},
    ])
    result = run_transcription_evidence(TranscriptionRunRequest(manifest, acquisitions, inspections, tmp_path / "out"), engine)
    assert result["candidates"][0]["first_spoken_words"]["text"] == "earlier"


@pytest.mark.parametrize("start,end", [(math.nan, 1), (0, math.nan), (math.inf, 1), (0, math.inf), (-math.inf, 1), (-1, 1), (2, 1), (0, 6)])
def test_non_finite_or_invalid_segment_timestamps_fail(tmp_path: Path, start: float, end: float) -> None:
    manifest, acquisitions, inspections = _fixture(tmp_path)
    engine = FakeEngine([{"start_seconds": start, "end_seconds": end, "raw_text": "bad", "avg_logprob": -.1, "no_speech_prob": .01, "words": []}])
    result = run_transcription_evidence(TranscriptionRunRequest(manifest, acquisitions, inspections, tmp_path / "out"), engine)
    assert result["candidates"][0]["status"] == "FAILED"


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_engine_observations_fail(tmp_path: Path, value: float) -> None:
    manifest, acquisitions, inspections = _fixture(tmp_path)
    engine = FakeEngine([{"start_seconds": 0, "end_seconds": 1, "raw_text": "bad", "avg_logprob": value, "no_speech_prob": .01, "words": []}])
    result = run_transcription_evidence(TranscriptionRunRequest(manifest, acquisitions, inspections, tmp_path / "out"), engine)
    assert result["candidates"][0]["status"] == "FAILED"


def test_invalid_word_timestamp_fails(tmp_path: Path) -> None:
    manifest, acquisitions, inspections = _fixture(tmp_path)
    engine = FakeEngine([{"start_seconds": 0, "end_seconds": 1, "raw_text": "word", "avg_logprob": -.1, "no_speech_prob": .01, "words": [{"start_seconds": math.nan, "end_seconds": .5, "word": "word", "probability": .5}]}])
    result = run_transcription_evidence(TranscriptionRunRequest(manifest, acquisitions, inspections, tmp_path / "out"), engine)
    assert result["candidates"][0]["status"] == "FAILED"


def test_word_materially_outside_segment_fails(tmp_path: Path) -> None:
    manifest, acquisitions, inspections = _fixture(tmp_path)
    engine = FakeEngine([{"start_seconds": 0, "end_seconds": 1, "raw_text": "word", "avg_logprob": -.1, "no_speech_prob": .01, "words": [{"start_seconds": 0, "end_seconds": 1.6, "word": "word", "probability": .5}]}])
    result = run_transcription_evidence(TranscriptionRunRequest(manifest, acquisitions, inspections, tmp_path / "out"), engine)
    assert result["candidates"][0]["status"] == "FAILED"


def test_word_boundary_overhang_within_engine_tolerance_is_accepted(tmp_path: Path) -> None:
    manifest, acquisitions, inspections = _fixture(tmp_path)
    engine = FakeEngine([{"start_seconds": 0, "end_seconds": 1, "raw_text": "word", "avg_logprob": -.1, "no_speech_prob": .01, "words": [{"start_seconds": 0, "end_seconds": 1.48, "word": "word", "probability": .5}]}])
    result = run_transcription_evidence(TranscriptionRunRequest(manifest, acquisitions, inspections, tmp_path / "out"), engine)
    assert result["candidates"][0]["status"] == "COMPLETED"


def test_legacy_result_migrates_without_model_load(tmp_path: Path) -> None:
    manifest, acquisitions, inspections = _fixture(tmp_path)
    engine = FakeEngine([{"start_seconds": 0, "end_seconds": 1, "raw_text": "first", "avg_logprob": -.1, "no_speech_prob": .01, "words": []}])
    request = TranscriptionRunRequest(manifest, acquisitions, inspections, tmp_path / "out")
    current = run_transcription_evidence(request, engine)["candidates"][0]
    target = tmp_path / "out" / "fixture" / "candidates" / "1" / "transcription" / "transcription_result.json"
    legacy = current | {"schema_version": "1.0", "first_spoken_words": "first"}
    legacy.pop("migrated_from_schema_version", None)
    target.write_text(json.dumps(legacy), encoding="utf-8")
    migrated = run_transcription_evidence(request, engine)["candidates"][0]
    assert migrated["schema_version"] == SCHEMA_VERSION and migrated["migrated_from_schema_version"] == "1.0"
    assert migrated["first_spoken_words"]["supporting_segment_id"] == "segment-0001" and engine.calls == 1
