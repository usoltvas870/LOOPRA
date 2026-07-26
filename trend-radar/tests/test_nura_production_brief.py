import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

from nura_production_brief import NuraProductionBriefError, build_production_briefs, hash_payload


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _fixture(tmp_path: Path) -> dict[str, Path]:
    context = {"schema_version": "1.0", "context_version": "1.0", "project_id": "nura", "safety_constraints": ["No diagnosis."], "production_constraints": ["No copying."]}
    context_path = tmp_path / "context.json"; _write(context_path, context)
    candidates = [{"rank": rank, "video_id": f"video-{rank}"} for rank in range(1, 6)]
    manifest = {"manifest_hash": "manifest-hash", "radar_run_id": "run-1", "candidates": candidates}
    manifest_path = tmp_path / "manifest.json"; _write(manifest_path, manifest)
    cards_root = tmp_path / "cards"; review_candidates = []
    for item in candidates:
        rank = item["rank"]
        adaptation = {"source_mechanism": f"mechanism {rank}", "adaptation_idea": f"adaptation {rank}", "suggested_hook": f"hook {rank}", "production_elements_not_copied": f"do not copy {rank}", "applied_constraints": ["No copying."]}
        card = {"schema_version": "0.1", "candidate_identity": {"video_id": item["video_id"], "rank": rank}, "project_context_hash": hash_payload(context), "provider": {"provider_id": "deepseek", "model_id": "deepseek-v4-flash", "provider_version": "1.0", "configuration": {"prompt_version": "2.0"}}, "project_adaptation": adaptation, "warnings": ["limited evidence"]}
        card["card_hash"] = hash_payload(card); _write(cards_root / item["video_id"] / "content_intelligence_card.json", card)
        fields = []
        for field, value in adaptation.items():
            source = adaptation["source_mechanism"] if field == "source_mechanism" else value
            fields.append({"field": field, "status": "EDIT_REQUIRED" if rank == 1 and field == "source_mechanism" else "ACCEPTED", "source_value_hash": hash_payload(source), "source_claim_ids": []})
        revisions = []
        if rank == 1:
            revisions.append({"revision_id": "r1", "field_path": "source_mechanism", "source_value_hash": hash_payload(adaptation["source_mechanism"]), "revised_value": "human mechanism", "revision_reason": "Correct source mechanism.", "reviewer_id": "nura-owner", "human_verified": True, "revision_status": "APPROVED_BY_OWNER", "source_claim_ids": [], "evidence_refs_reviewed": []})
        review_candidates.append({"original_rank": rank, "candidate_identity": {"video_id": item["video_id"], "author": "a", "source_platform": "p"}, "source_card_hash": card["card_hash"], "field_reviews": fields, "human_revisions": revisions, "allowed_claim_ids": [], "allowed_evidence_refs": [], "overall_decision": "APPROVED_FOR_PRODUCTION_BRIEF" if rank == 4 else "APPROVED_WITH_EDITORIAL_EDITS", "production_brief_eligibility": "ELIGIBLE" if rank == 4 else "ELIGIBLE_WITH_HUMAN_REVISIONS"})
    result = {"schema_version": "0.1", "review_id": "source-review", "finalization_identity": "final", "reviewer": {"reviewer_id": "nura-owner", "reviewer_role": "OWNER", "human_confirmation": True}, "candidate_reviews": review_candidates, "final_status": "COMPLETED"}
    result["review_hash"] = hash_payload(result)
    review_root = tmp_path / "finalized-review"; _write(review_root / "review_result.json", result)
    _write(review_root / "review_manifest.json", {"review_id": review_root.name, "finalization_identity": "final", "review_result_sha256": hash_payload(result)})
    return {"review": review_root, "manifest": manifest_path, "cards": cards_root, "context": context_path, "output": tmp_path / "out"}


def _build(paths: dict[str, Path]) -> dict:
    return build_production_briefs(finalized_review_root=paths["review"], manifest_path=paths["manifest"], source_cards_root=paths["cards"], project_context_path=paths["context"], output_root=paths["output"])


def test_builds_candidate_scoped_briefs_with_human_revision_and_preserved_rank(tmp_path: Path) -> None:
    result = _build(_fixture(tmp_path))
    assert result["status"] == "COMPLETED"
    assert [item["rank"] for item in result["candidates"]] == [1, 2, 3, 4, 5]
    root = Path(result["output_root"])
    rank_one = json.loads((root / "candidates/video-1/production_brief.json").read_text(encoding="utf-8"))
    assert rank_one["fields"]["source_mechanism"]["value"] == "human mechanism"
    assert rank_one["fields"]["source_mechanism"]["source_type"] == "HUMAN_REVISION"
    assert rank_one["fields"]["hook_type"]["status"] == "NOT_TYPED"
    rank_four = json.loads((root / "candidates/video-4/production_brief.json").read_text(encoding="utf-8"))
    assert rank_four["readiness"] == "READY_FOR_SCRIPT_CONTRACT"
    assert rank_four["fields"]["suggested_hook"]["source_type"] == "HUMAN_ACCEPTED_AI_VALUE"


def test_reuses_unchanged_complete_package(tmp_path: Path) -> None:
    paths = _fixture(tmp_path); first = _build(paths); second = _build(paths)
    assert first["run_hash"] == second["run_hash"]
    assert second["status"] == "REUSED"


def test_stale_human_revision_blocks_without_ai_fallback(tmp_path: Path) -> None:
    paths = _fixture(tmp_path)
    review = json.loads((paths["review"] / "review_result.json").read_text(encoding="utf-8"))
    review["candidate_reviews"][0]["human_revisions"][0]["source_value_hash"] = "bad"
    review["review_hash"] = hash_payload({key: value for key, value in review.items() if key != "review_hash"})
    _write(paths["review"] / "review_result.json", review)
    _write(paths["review"] / "review_manifest.json", {"review_id": paths["review"].name, "finalization_identity": "final", "review_result_sha256": hash_payload(review)})
    with pytest.raises(NuraProductionBriefError, match="HUMAN_REVISION_STALE"):
        _build(paths)


def test_rejects_rank_six_and_does_not_accept_arbitrary_card_paths(tmp_path: Path) -> None:
    paths = _fixture(tmp_path)
    with pytest.raises(NuraProductionBriefError, match="RANK_SCOPE"):
        build_production_briefs(finalized_review_root=paths["review"], manifest_path=paths["manifest"], source_cards_root=paths["cards"], project_context_path=paths["context"], output_root=paths["output"], ranks=(6,))
