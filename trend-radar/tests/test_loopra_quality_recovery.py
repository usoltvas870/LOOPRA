from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from loopra_quality_recovery import (
    REJECTED_STATUS, contamination_findings, duplicate_pairs, evidence_sufficiency,
    production_brief_allowed, relevance_assessment, reject_batch, source_specificity,
    write_owner_triage,
)


def _item(rank: int, **fingerprint):
    return {"rank": rank, "video_id": str(rank), "canonical_url": f"https://example/{rank}", "author": "same", "duration": 10.0, "fingerprint": fingerprint}


def test_current_rejected_status_blocks_production_brief():
    rejection = reject_batch(batch_id="b", cycle_id="c", rejected_at="2026-07-27T00:00:00Z")
    assert rejection["decision"] == "REJECT_BATCH_FOR_QUALITY_RECOVERY"
    assert not production_brief_allowed(REJECTED_STATUS)


def test_exact_media_duplicate_is_detected_and_cannot_have_two_slots():
    digest = "a" * 64
    pairs = duplicate_pairs([_item(1, media_sha256=digest, frame_hashes=[], audio_sha256=None), _item(2, media_sha256=digest, frame_hashes=[], audio_sha256=None)])
    assert pairs[0]["confidence"] == "HIGH"
    assert pairs[0]["recommended_selection_action"] == "REMOVE_DUPLICATE_AND_BACKFILL"


def test_same_metadata_without_media_similarity_is_only_suspected():
    pairs = duplicate_pairs([_item(1, media_sha256="a", frame_hashes=[], audio_sha256=None), _item(2, media_sha256="b", frame_hashes=[], audio_sha256=None)])
    assert pairs[0]["confidence"] == "LOW"


def test_near_duplicate_frame_fingerprint_is_detected():
    pairs = duplicate_pairs([_item(1, media_sha256="a", frame_hashes=["0" * 16], audio_sha256=None), _item(2, media_sha256="b", frame_hashes=["0" * 15 + "1"], audio_sha256=None)])
    assert "PERCEPTUAL_FRAMES" in pairs[0]["reasons"]


def test_engagement_cannot_override_zero_relevance_and_junk_is_rejected():
    result = relevance_assessment("случайный мем про кота", engagement=100)
    assert result["engagement"] == 100
    assert result["hard_gate_passed"] is False


def test_relevant_low_engagement_item_remains_eligible():
    assert relevance_assessment("усталость от поддержки других", engagement=0)["hard_gate_passed"] is True


def test_speech_text_and_visual_evidence_paths():
    speech = evidence_sufficiency(transcript={"segments": [{"normalized_text": "hello"}]}, ocr=None, inspection=None)
    text = evidence_sufficiency(transcript=None, ocr={"ordered_observations": [{"normalized_text": "hello"}]}, inspection=None)
    visual = evidence_sufficiency(transcript=None, ocr=None, inspection={"sampling": {"successful_frame_count": 2}})
    assert speech["status"] == "SUFFICIENT_SPEECH_EVIDENCE"
    assert text["status"] == "SUFFICIENT_TEXT_EVIDENCE"
    assert visual["status"] == "LOW_QUALITY_REQUIRES_REPROCESSING"


def test_nonempty_evidence_marked_absent_is_a_contradiction():
    result = evidence_sufficiency(transcript={"segments": [{"normalized_text": "hello"}], "warnings": ["transcription absent"]}, ocr=None, inspection=None)
    assert result["status"] == "CONFLICTING_EVIDENCE_STATUS"
    assert result["adaptation_allowed"] is False


def test_insufficient_evidence_blocks_ci_adaptation():
    assert evidence_sufficiency(transcript=None, ocr=None, inspection=None)["adaptation_allowed"] is False


def test_source_specificity_requires_evidence_reference_and_source_mechanism():
    assert source_specificity({"claims": [], "project_adaptation": {}}, {"adaptation_allowed": True})["passed"] is False
    card = {"claims": [{"evidence_refs": ["transcript:1"]}], "project_adaptation": {"source_mechanism": "specific event", "suggested_hook": "specific hook"}}
    assert source_specificity(card, {"adaptation_allowed": True})["passed"] is True


def test_repeated_generic_hook_is_reported_not_silently_accepted():
    items = [{"rank": 1, "card": {"project_adaptation": {"suggested_hook": "повторяющиеся паттерны в отношениях"}}}, {"rank": 2, "card": {"project_adaptation": {"suggested_hook": "повторяющиеся паттерны в отношениях"}}}]
    assert contamination_findings(items)[0]["ranks"] == [1, 2]


def test_owner_template_has_twenty_blank_labels_and_confirmation_false(tmp_path: Path):
    items = [{"rank": rank, "paths": {"media": "x"}, "author": "a", "duration": 1, "canonical_url": "u", "evidence": {"status": "INSUFFICIENT_EVIDENCE"}, "excerpts": {"ocr": "", "transcription": ""}, "relevance": {"machine_suggestion": "IRRELEVANT"}, "card": {}} for rank in range(1, 21)]
    write_owner_triage({"batch_id": "b", "items": items, "duplicates": []}, tmp_path)
    import json
    template = json.loads((tmp_path / "00_OWNER_LABELS_TEMPLATE.json").read_text(encoding="utf-8"))
    assert len(template["items"]) == 20
    assert template["human_confirmation"] is False
