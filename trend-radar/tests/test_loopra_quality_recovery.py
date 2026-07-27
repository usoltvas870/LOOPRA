from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from loopra_quality_recovery import (
    REJECTED_STATUS, contamination_findings, duplicate_pairs, evidence_sufficiency,
    production_brief_allowed, relevance_assessment, reject_batch, source_specificity,
    write_owner_triage,
)
from grounded_triage import (
    ACTIONABLE_PACKAGE_VERSION, build_evidence_packet, build_grounded_payload,
    contamination_findings as grounded_contamination_findings, validate_grounded_result,
    write_actionable_owner_package,
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


def _packet(rank: int = 6):
    return build_evidence_packet(
        batch_id="batch", candidate={"rank": rank, "video_id": str(rank), "canonical_url": "https://source", "author": "author", "provenance_references": {"primary_source_value": "границы", "primary_source_type": "keyword"}, "score_snapshot": {"final_score": 1, "engagement_score": 1, "freshness_score": 1}},
        acquisition={"media_sha256": "a" * 64}, inspection={"media_facts": {"duration_seconds": 12}, "sampling": {"frame_results": [{"status": "success", "frame_path": "sample.png"}]}},
        transcript={"status": "COMPLETED", "language": "ru", "segments": [{"segment_id": "s1", "start_seconds": 0, "end_seconds": 2, "normalized_text": "Личные границы помогают сохранять уважение."}]},
        ocr={"status": "COMPLETED", "requested_language": "ru", "ordered_observations": [{"observation_id": "o1", "sampled_at_sec": 0, "frame_ref": "frame.png", "normalized_text": "Уважение начинается с границ"}]}, paths={"media": "media.mp4"},
    )


def _result(packet):
    return {"literal_content_summary": "Автор говорит: личные границы помогают сохранять уважение.", "primary_topic": "личные границы", "secondary_topics": [], "content_format": "talking_head", "source_language": "ru", "source_hook": "Личные границы помогают сохранять уважение", "hook_evidence_refs": ["s1"], "key_content_points": ["границы"], "key_evidence_refs": ["s1"], "attention_mechanism": "прямое утверждение", "attention_evidence_refs": ["s1"], "NURA_relevance_decision": "RELEVANT", "relevance_rationale": "Тема личных границ явно произносится в источнике.", "relevance_evidence_refs": ["s1"], "transferable_mechanism_available": True, "transferable_mechanism": "Коротко назвать границы и их эффект.", "junk_category": None, "safety_fit": "SAFE", "confidence": "HIGH", "unresolved_questions": [], "prohibited_copying_elements": []}


def test_grounded_packet_uses_full_meaningful_transcript_and_ocr():
    packet = _packet()
    assert packet["schema_version"] == "2.0"
    assert packet["transcript_segments"][0]["text"].startswith("Личные границы")
    assert packet["OCR_normalized_lines"][0]["quality_status"] == "READABLE"
    assert build_grounded_payload(packet)["prompt_version"] == "NURA_TOP20_GROUNDED_TRIAGE_V2"


def test_music_and_one_symbol_do_not_count_as_speech_or_text():
    packet = build_evidence_packet(batch_id="b", candidate={"rank": 1, "video_id": "1"}, acquisition={}, inspection=None, transcript={"segments": [{"text": "Music"}, {"text": "I"}]}, ocr={"ordered_observations": [{"text": "?"}]}, paths={})
    assert packet["evidence_sufficiency_status"] == "INSUFFICIENT_EVIDENCE"


def test_grounded_result_requires_source_specific_summary_and_refs():
    packet, result = _packet(), _result(_packet())
    assert validate_grounded_result(result, packet)["status"] == "VALID"
    result["literal_content_summary"] = "Высокие просмотры и лайки."
    assert "SUMMARY_NOT_SOURCE_SPECIFIC" in validate_grounded_result(result, packet)["errors"]


def test_actionable_package_has_confirmation_only_and_twenty_files(tmp_path: Path):
    packets = [_packet(rank) for rank in range(1, 21)]
    results = [{"rank": rank, "result": _result(packets[rank - 1]), "duplicate_status": "DUPLICATE" if rank == 18 else "CANONICAL", "duplicate_of_rank": 13 if rank == 18 else None} for rank in range(1, 21)]
    write_actionable_owner_package(packets=packets, results=results, output=tmp_path)
    assert len(list((tmp_path / "items").glob("*_actionable.md"))) == 20
    assert ACTIONABLE_PACKAGE_VERSION == "1.2"
    assert "agree_with_machine_decision: null" in (tmp_path / "items" / "01_actionable.md").read_text(encoding="utf-8")


def test_grounded_contamination_blocks_repeated_summary():
    result = _result(_packet())
    assert grounded_contamination_findings([{"rank": 1, "result": result}, {"rank": 2, "result": result}])


def test_semantic_paraphrase_does_not_require_literal_substring():
    packet, result = _packet(), _result(_packet())
    result["literal_content_summary"] = "Речь объясняет, что уважительное общение невозможно без обозначения личных пределов."
    validation = validate_grounded_result(result, packet)
    assert validation["status"] == "VALID"
    assert validation["supporting_evidence"][0]["exact_excerpt"].startswith("Личные границы")


def test_unknown_evidence_ref_is_rejected():
    packet, result = _packet(), _result(_packet())
    result["key_evidence_refs"] = ["other-rank-segment"]
    assert any(error.startswith("UNKNOWN_EVIDENCE_REF") for error in validate_grounded_result(result, packet)["errors"])


def test_metrics_only_summary_is_rejected():
    packet, result = _packet(), _result(_packet())
    result["literal_content_summary"] = "Высокие views, likes и comments показывают популярность публикации."
    assert "METRICS_ONLY_SUMMARY" in validate_grounded_result(result, packet)["errors"]


def test_unsupported_psychology_rationale_is_rejected():
    packet, result = _packet(), _result(_packet())
    result["content_format"] = "animal"
    result["relevance_rationale"] = "The animal joke is about relationships and self-esteem."
    assert "UNSUPPORTED_PSYCHOLOGY_RATIONALE" in validate_grounded_result(result, packet)["errors"]


def test_paraphrased_hook_gets_application_grounding_type():
    packet, result = _packet(), _result(_packet())
    result["source_hook"] = "Без личных пределов невозможно устойчивое уважение."
    validation = validate_grounded_result(result, packet)
    assert validation["source_hook_type"] == "paraphrased_source_hook"
    assert validation["status"] == "VALID"


def test_provider_rejected_alias_is_canonicalized_without_changing_raw_audit_value():
    packet, result = _packet(), _result(_packet())
    result["NURA_relevance_decision"] = "REJECTED"
    result["relevance_rationale"] = "The source discusses personal limits, not the requested unrelated topic."
    assert validate_grounded_result(result, packet)["status"] == "VALID"
    assert result["NURA_relevance_decision"] == "IRRELEVANT"
    assert result["provider_relevance_decision_raw"] == "REJECTED"


def test_duplicate_reuse_does_not_trigger_contamination():
    result = _result(_packet())
    rows = [{"rank": 13, "result": result, "duplicate_of_rank": None}, {"rank": 18, "result": result, "duplicate_of_rank": 13}]
    assert grounded_contamination_findings(rows) == []
