from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "trend-radar/src"))

from loopra_top20_b1_adapter import (
    LoopraTop20B1Adapter,
    LoopraTop20B1Error,
    run_synthetic_acceptance,
)


def test_synthetic_b1_creates_exact_ordered_top20_and_pending_human_gate(tmp_path: Path):
    result = run_synthetic_acceptance(runtime_root=tmp_path)
    assert result["status"] == "PASS"
    assert result["original_ranks"] == list(range(1, 21))
    assert result["completed"] == 20
    assert result["human_gate"] == "EDITORIAL_REVIEW_PENDING"
    assert result["production_brief_allowed"] is False
    assert result["network_calls"] == result["browser_calls"] == result["provider_calls"] == 0
    assert result["credentials_required"] is False


def test_item_plans_preserve_unique_identity_and_portable_refs(tmp_path: Path):
    adapter = LoopraTop20B1Adapter(runtime_root=tmp_path)
    items = adapter.initialize()["items"]
    assert [item["original_rank"] for item in items] == list(range(1, 21))
    assert len({item["candidate_id"] for item in items}) == len({item["video_id"] for item in items}) == 20
    assert all(not Path(ref).is_absolute() for item in items for ref in item["expected_runtime_references"].values())
    assert len({item["content_intelligence_call_identity"] for item in items}) == 20


def test_selection_rejects_rank_mapping_or_duplicate_ids(tmp_path: Path):
    adapter = LoopraTop20B1Adapter(runtime_root=tmp_path)
    entries = adapter.synthetic_selection()
    entries[5]["original_rank"] = 1
    with pytest.raises(LoopraTop20B1Error, match="EXACT_ORIGINAL_RANKS"):
        adapter.initialize(entries=entries)
    entries = adapter.synthetic_selection()
    entries[1]["video_id"] = entries[0]["video_id"]
    with pytest.raises(LoopraTop20B1Error, match="UNIQUE_CANDIDATE"):
        adapter.initialize(entries=entries)


def test_report_and_review_are_own_v2_aggregates(tmp_path: Path):
    adapter = LoopraTop20B1Adapter(runtime_root=tmp_path)
    adapter.initialize(); adapter.simulate_execution()
    report = adapter.build_content_intelligence_report()["report"]
    review = adapter.build_pending_editorial_review()["review"]
    assert report["artifact_kind"] == "LoopraTop20ContentIntelligenceReport"
    assert [card["original_rank"] for card in report["cards"]] == list(range(1, 21))
    assert report["winner"] is None and report["human_verified"] is False
    assert [item["original_rank"] for item in review["items"]] == list(range(1, 21))
    assert review["finalized"] is False and review["production_brief_allowed"] is False


def test_failure_is_resumable_without_stopping_other_items(tmp_path: Path):
    adapter = LoopraTop20B1Adapter(runtime_root=tmp_path)
    adapter.initialize()
    failed = adapter.simulate_execution(fail_rank=7)
    assert failed["completed"] == 19
    assert failed["items"][6]["current_stage"] == "RETRYABLE_FAILURE"
    assert failed["items"][0]["current_stage"] == "CONTENT_INTELLIGENCE_COMPLETED"
    resumed = adapter.simulate_execution()
    assert resumed["completed"] == 20


def test_second_run_reuses_deterministic_artifacts(tmp_path: Path):
    first = run_synthetic_acceptance(runtime_root=tmp_path)
    second = run_synthetic_acceptance(runtime_root=tmp_path)
    assert first["batch_id"] == second["batch_id"]
    assert first["report_hash"] == second["report_hash"]
    assert first["review_hash"] == second["review_hash"]


def test_call_identity_changes_with_rank_or_prompt_input(tmp_path: Path):
    adapter = LoopraTop20B1Adapter(runtime_root=tmp_path)
    items = adapter.initialize()["items"]
    assert items[0]["content_intelligence_call_identity"] != items[1]["content_intelligence_call_identity"]
    assert items[0]["selection_entry_hash"] != items[1]["selection_entry_hash"]


def test_real_b1_readiness_replaces_unconditional_blocker(tmp_path: Path):
    result = LoopraTop20B1Adapter(runtime_root=tmp_path).real_b1_readiness()
    assert result["ready"] is True
    assert result["status"] == "READY"
    assert result["runtime_root_git_ignored"] is True
