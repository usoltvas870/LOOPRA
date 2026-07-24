import json
import sys
from pathlib import Path

import pytest

RADAR_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RADAR_ROOT / "src")]

from content_intelligence import (
    ClaimType, ContentIntelligenceError, FakeDeterministicProvider,
    ProjectAnalysisContext, build_analysis_input, run_fake_analysis,
    validate_provider_result,
)
from evidence_resolution import adopt_legacy_inspection


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _fixture(tmp_path: Path) -> dict[str, Path]:
    candidate = {"rank": 1, "video_id": "video-1", "author": "a", "source": {}, "canonical_url": None, "caption": None, "metrics_snapshot": {}, "score_snapshot": {}, "classification": "CURRENT", "radar_confidence": "HIGH", "identity_confidence": "HIGH", "provenance_references": None, "source_artifact_references": [], "warnings": []}
    core = {"schema_version": "1.0", "manifest_type": "trend_radar_content_intelligence_selection", "manifest_id": "fixture", "created_at": "2026-01-01T00:00:00Z", "radar_run_id": "fixture", "radar_run_reference": "data/runs/run_fixture.json", "ranking_source": "test", "ranking_contract_version": "1", "requested_candidate_count": 20, "selected_candidate_count": 1, "selection_complete": False, "selection_status": "incomplete", "selection_reason": "fewer_ranked_candidates_than_requested", "candidates": [candidate], "source_artifacts": []}
    import hashlib
    core["manifest_hash"] = hashlib.sha256((json.dumps({key: value for key, value in core.items() if key not in {"manifest_id", "created_at", "manifest_hash"}}, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()
    manifest = tmp_path / "selection_manifest_fixture.json"; _write(manifest, core)
    acquisition = tmp_path / "acquisitions"; inspection = tmp_path / "inspections"; evidence = tmp_path / "evidence"
    media = acquisition / "video-1" / "source.mp4"; media.parent.mkdir(parents=True); media.write_bytes(b"fixture-media")
    import hashlib
    media_hash = hashlib.sha256(media.read_bytes()).hexdigest()
    _write(acquisition / "video-1" / "acquisition_record.json", {"candidate_video_id": "video-1", "candidate_rank": 1, "selection_manifest_hash": core["manifest_hash"], "local_media_path": "video-1/source.mp4", "media_sha256": media_hash})
    frame = inspection / "video-1" / "frames" / "frame.png"; frame.parent.mkdir(parents=True); frame.write_bytes(b"fixture-frame")
    _write(inspection / "video-1" / "inspection.json", {"schema_version": "1.1", "video_id": "video-1", "media_sha256": media_hash, "status": "COMPLETED", "media_facts": {"audio_present": True}, "sampling": {"frame_results": [{"status": "success", "frame_path": "frame.png", "effective_timestamp_seconds": 0}]}})
    _write(evidence / "video-1" / "ocr" / "ocr_result.json", {"candidate_video_id": "video-1", "rank": 1, "selection_manifest_hash": core["manifest_hash"], "inspection_media_sha256": media_hash, "status": "COMPLETED", "text_events": [{"event_id": "event-001", "text": "x" * 1000, "first_seen_at_sec": 0}], "first_text_hook": {"hook_text": "hello", "first_seen_at_sec": 0}})
    _write(evidence / "video-1" / "transcription" / "transcription_result.json", {"candidate_video_id": "video-1", "rank": 1, "selection_manifest_hash": core["manifest_hash"], "media_sha256": media_hash, "status": "COMPLETED", "segments": [{"segment_id": "segment-0001", "normalized_text": "y" * 1000, "start_seconds": 0, "end_seconds": 1}], "first_spoken_words": {"text": "word", "supporting_segment_id": "segment-0001"}})
    return {"manifest": manifest, "acquisition": acquisition, "inspection": inspection, "evidence": evidence}


def test_builder_bounds_evidence_and_validates_identity(tmp_path: Path) -> None:
    paths = _fixture(tmp_path)
    result = build_analysis_input(paths["manifest"], "video-1", acquisition_root=paths["acquisition"], inspection_root=paths["inspection"], intelligence_evidence_root=paths["evidence"], project_context=ProjectAnalysisContext("project", "1", requested_adaptation_fields=("suggested_hook",)))
    assert result["candidate_identity"]["rank"] == 1
    assert len(result["evidence"]["ocr"]["events"][0]["text"]) == 240
    assert result["input_hash"]


def test_provider_cannot_emit_fact_or_unknown_reference(tmp_path: Path) -> None:
    paths = _fixture(tmp_path)
    value = build_analysis_input(paths["manifest"], "video-1", acquisition_root=paths["acquisition"], inspection_root=paths["inspection"], intelligence_evidence_root=paths["evidence"], project_context=ProjectAnalysisContext("project", "1"))
    provider = FakeDeterministicProvider(); invalid = provider.analyze(value)
    invalid["claims"][0]["claim_type"] = ClaimType.FACT
    with pytest.raises(ContentIntelligenceError, match="cannot emit FACT"):
        validate_provider_result(invalid, value, provider)
    invalid["claims"][0]["claim_type"] = ClaimType.INFERENCE; invalid["claims"][0]["evidence_refs"] = ["unknown"]
    with pytest.raises(ContentIntelligenceError, match="unknown evidence"):
        validate_provider_result(invalid, value, provider)


def test_fake_run_is_atomic_and_reused(tmp_path: Path) -> None:
    paths = _fixture(tmp_path); context = ProjectAnalysisContext("project", "1")
    kwargs = dict(manifest_path=paths["manifest"], acquisition_root=paths["acquisition"], inspection_root=paths["inspection"], intelligence_evidence_root=paths["evidence"], output_root=tmp_path / "out", project_context=context, limit=1)
    first = run_fake_analysis(**kwargs); second = run_fake_analysis(**kwargs)
    assert first["results"][0]["reuse"] is False
    assert second["results"][0]["status"] == "REUSED"


def test_verified_legacy_inspection_is_adopted_without_overwriting_source(tmp_path: Path) -> None:
    paths = _fixture(tmp_path)
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    candidate = type("Candidate", (), {"video_id": "video-1", "rank": 1})()
    legacy_root = tmp_path / "legacy"
    source = paths["inspection"] / "video-1" / "inspection.json"
    target = legacy_root / "video-1" / "inspection.json"; target.parent.mkdir(parents=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    legacy_frame = legacy_root / "video-1" / "frames" / "frame.png"; legacy_frame.parent.mkdir(parents=True)
    legacy_frame.write_bytes((paths["inspection"] / "video-1" / "frames" / "frame.png").read_bytes())
    adopted = adopt_legacy_inspection(candidate=candidate, manifest_hash=manifest["manifest_hash"],
        acquisition_root=paths["acquisition"], inspection_root=tmp_path / "canonical",
        legacy_inspection_root=legacy_root)
    assert adopted.is_file() and target.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")


def test_resolver_rejects_cross_candidate_inspection(tmp_path: Path) -> None:
    paths = _fixture(tmp_path)
    inspection = paths["inspection"] / "video-1" / "inspection.json"
    payload = json.loads(inspection.read_text(encoding="utf-8")); payload["video_id"] = "other"; _write(inspection, payload)
    with pytest.raises(ContentIntelligenceError, match="INSPECTION_CANDIDATE_MISMATCH"):
        build_analysis_input(paths["manifest"], "video-1", acquisition_root=paths["acquisition"], inspection_root=paths["inspection"], intelligence_evidence_root=paths["evidence"], project_context=ProjectAnalysisContext("project", "1"))


def test_adoption_backs_up_stale_schema_one_canonical_result(tmp_path: Path) -> None:
    paths = _fixture(tmp_path); manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    candidate = type("Candidate", (), {"video_id": "video-1", "rank": 1})(); legacy_root = tmp_path / "legacy"
    source = paths["inspection"] / "video-1" / "inspection.json"; legacy = legacy_root / "video-1" / "inspection.json"; legacy.parent.mkdir(parents=True); legacy.write_bytes(source.read_bytes())
    frame = legacy.parent / "frames" / "frame.png"; frame.parent.mkdir(parents=True); frame.write_bytes((source.parent / "frames" / "frame.png").read_bytes())
    canonical = tmp_path / "canonical" / "video-1" / "inspection.json"; canonical.parent.mkdir(parents=True)
    stale = b'{"schema_version":"1.0"}\n'; canonical.write_bytes(stale)
    adopted = adopt_legacy_inspection(candidate=candidate, manifest_hash=manifest["manifest_hash"], acquisition_root=paths["acquisition"], inspection_root=tmp_path / "canonical", legacy_inspection_root=legacy_root)
    backup = next((canonical.parent / "legacy-backups").glob("*.json"))
    assert adopted.read_bytes() == source.read_bytes() and backup.read_bytes() == stale
