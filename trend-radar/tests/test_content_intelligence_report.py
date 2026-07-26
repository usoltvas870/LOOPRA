import hashlib
import json
import sys
from pathlib import Path

import pytest

RADAR_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RADAR_ROOT / "src")]

from content_intelligence import hash_payload
from content_intelligence_report import ContentIntelligenceReportError, generate_report


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _context(path: Path) -> Path:
    _write(path, {"schema_version": "1.0", "context_version": "1.0", "project_id": "nura", "project_name": "NURA", "audience_summary": "a", "brand_role": "b", "adaptation_objective": "c", "available_formats": [], "production_constraints": [], "allowed_claims": [], "prohibited_claims": [], "safety_constraints": [], "tone": "Russian"})
    return path


def _fixture(tmp_path: Path) -> dict[str, Path]:
    candidates = [{"rank": rank, "video_id": f"video-{rank}", "author": "safe-author", "source": {"type": "tiktok"}, "canonical_url": f"https://www.tiktok.com/@safe/video/{rank}", "caption": "caption", "metrics_snapshot": {"views": rank}, "score_snapshot": {"final_score": rank}, "classification": "CURRENT", "radar_confidence": "HIGH", "identity_confidence": "HIGH", "provenance_references": None, "source_artifact_references": [], "warnings": []} for rank in range(1, 6)]
    manifest = {"schema_version": "1.0", "manifest_type": "trend_radar_content_intelligence_selection", "manifest_id": "fixture", "created_at": "2026-01-01T00:00:00Z", "radar_run_id": "fixture", "radar_run_reference": "data/runs/run_fixture.json", "ranking_source": "test", "ranking_contract_version": "1", "requested_candidate_count": 20, "selected_candidate_count": 5, "selection_complete": False, "selection_status": "incomplete", "selection_reason": "fewer_ranked_candidates_than_requested", "candidates": candidates, "source_artifacts": []}
    content = {key: value for key, value in manifest.items() if key not in {"manifest_id", "created_at", "manifest_hash"}}
    manifest["manifest_hash"] = hashlib.sha256((json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")).hexdigest()
    manifest_path = tmp_path / "selection_manifest_fixture.json"; _write(manifest_path, manifest)
    context_path = _context(tmp_path / "context.json")
    context_hash = hash_payload(json.loads(context_path.read_text(encoding="utf-8")))
    run = tmp_path / "cards" / "real" / f"real-fixture-{manifest['manifest_hash'][:12]}-{context_hash[:8]}-deepseek-deepseek-v4-flash-2.0"
    for candidate in candidates:
        card = {"schema_version": "0.1", "candidate_identity": {"video_id": candidate["video_id"], "rank": candidate["rank"]}, "provider": {"provider_id": "deepseek", "provider_version": "1.0", "model_id": "deepseek-v4-flash", "fake": False, "configuration": {"prompt_version": "2.0"}}, "claims": [{"claim_id": "fact-001", "claim_type": "FACT", "field": "candidate_identity", "text": "immutable", "evidence_refs": ["inspection"]}, {"claim_id": "format-1", "claim_type": "INFERENCE", "field": "format", "text": "Вероятностный формат.", "evidence_refs": ["inspection"]}, {"claim_id": "mechanism-1", "claim_type": "AI_INTERPRETATION", "field": "mechanism", "text": "AI interpretation.", "evidence_refs": ["ocr:first_hook"]}], "evidence_index": [{"ref_id": "inspection", "kind": "format_inspection"}, {"ref_id": "ocr:first_hook", "kind": "ocr_first_hook"}], "evidence_quality": {"tier": "HIGH", "policy": "machine_observations_not_human_verified"}, "quality": {"status": "PASS", "warnings": []}, "project_adaptation": {"source_mechanism": "Существующий механизм.", "adaptation_idea": "Существующая адаптация.", "suggested_hook": "Существующий хук.", "production_elements_not_copied": "Чужое не копируется.", "applied_constraints": ["safe"]}, "status": "COMPLETED", "warnings": []}
        card["card_hash"] = hash_payload(card)
        _write(run / "candidates" / candidate["video_id"] / "content_intelligence_card.json", card)
    return {"manifest": manifest_path, "context": context_path, "cards": tmp_path / "cards", "reports": tmp_path / "reports", "run": run}


def _generate(paths: dict[str, Path], **kwargs: object) -> dict:
    return generate_report(manifest_path=paths["manifest"], context_path=paths["context"], card_runtime_root=paths["cards"], output_root=paths["reports"], **kwargs)


def test_report_is_ordered_bounded_and_reused(tmp_path: Path) -> None:
    paths = _fixture(tmp_path)
    first = _generate(paths); second = _generate(paths)
    assert first["status"] == "COMPLETED" and second["status"] == "REUSED"
    report = json.loads((paths["reports"] / first["report_id"] / "report.json").read_text(encoding="utf-8"))
    assert [item["original_rank"] for item in report["candidates"]] == [1, 2, 3, 4, 5]
    assert report["provider_summary"]["provider_calls"] == report["provider_summary"]["network_calls"] == 0
    assert all(item["hook_summary"]["hook_type"] == "NOT_TYPED" and item["human_verified"] is False for item in report["candidates"])
    assert first["report_json_sha256"] == second["report_json_sha256"]


def test_report_rejects_provider_fact_and_card_identity_mismatch(tmp_path: Path) -> None:
    paths = _fixture(tmp_path); card_path = paths["run"] / "candidates" / "video-1" / "content_intelligence_card.json"
    card = json.loads(card_path.read_text(encoding="utf-8")); card["claims"][1]["claim_type"] = "FACT"; card["card_hash"] = hash_payload({key: value for key, value in card.items() if key != "card_hash"}); _write(card_path, card)
    with pytest.raises(ContentIntelligenceReportError, match="PROVIDER_FACT"):
        _generate(paths)
    card["claims"][1]["claim_type"] = "INFERENCE"; card["candidate_identity"]["rank"] = 9; card["card_hash"] = hash_payload({key: value for key, value in card.items() if key != "card_hash"}); _write(card_path, card)
    with pytest.raises(ContentIntelligenceReportError, match="CARD_CANDIDATE_MISMATCH"):
        _generate(paths)


def test_card_change_invalidates_identity_and_markdown_is_safe(tmp_path: Path) -> None:
    paths = _fixture(tmp_path); first = _generate(paths)
    card_path = paths["run"] / "candidates" / "video-1" / "content_intelligence_card.json"
    card = json.loads(card_path.read_text(encoding="utf-8")); card["warnings"] = ["warning | <unsafe>"]; card["card_hash"] = hash_payload({key: value for key, value in card.items() if key != "card_hash"}); _write(card_path, card)
    changed = _generate(paths)
    markdown = (paths["reports"] / changed["report_id"] / "report.md").read_text(encoding="utf-8")
    assert first["report_id"] != changed["report_id"]
    assert "warning \\| &lt;unsafe&gt;" in markdown and "C:\\" not in markdown


@pytest.mark.parametrize("ranks", ((1, 2, 3, 4, 5, 6), (2, 1), (0,)))
def test_stage_5g_rank_scope_is_closed(tmp_path: Path, ranks: tuple[int, ...]) -> None:
    with pytest.raises(ContentIntelligenceReportError, match="RANK_SCOPE"):
        _generate(_fixture(tmp_path), ranks=ranks)
