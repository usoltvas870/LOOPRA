import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

from nura_production_brief import hash_payload
from nura_script_contract import (DeterministicFakeScriptProvider, NuraScriptContractError, build_script_input, create_human_script_review, load_editorial_profile, persist_package, validate_script_output)


def _write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def _brief() -> dict:
    fields = {
        "source_mechanism_preserved": {"value": "human mechanism", "source_type": "HUMAN_REVISION"},
        "suggested_hook": {"value": "approved hook", "source_type": "HUMAN_ACCEPTED_AI_VALUE"},
        "production_elements_not_copied": {"value": "source catchphrase", "source_type": "HUMAN_ACCEPTED_AI_VALUE"},
    }
    value = {"final_status": "COMPLETED", "readiness": "READY_WITH_HUMAN_REVISIONS", "brief_id": "brief-1", "candidate_identity": {"video_id": "synthetic-video"}, "original_rank": 1, "source_review": {"review_id": "review-1", "review_hash": "review-hash"}, "project_identity": {"project_id": "nura", "context_version": "1", "context_hash": "context-hash"}, "fields": fields, "evidence_limitations": ["synthetic"], "safety_constraints": ["no diagnosis"], "unresolved_fields": [{"field_name": "hook_type", "status": "NOT_TYPED"}]}
    value["brief_hash"] = hash_payload(value)
    return value


def _profile(tmp_path: Path) -> dict:
    profile = {"schema_version": "0.1", "profile_id": "nura", "profile_version": "1", "project_id": "nura", "source_document": {"reference": "guide", "sha256": "a" * 64}, "supported_content_scope": ["talking_guide", "background_voice", "text_led_video", "dialogue_comic"], "excluded_scope": ["core"], "voice_principles": ["concrete"], "prohibited_voice_patterns": ["imitation"], "safety_principles": ["no diagnosis"], "format_principles": {"talking_guide": {"required": []}, "background_voice": {"required": []}, "text_led_video": {"required": []}, "dialogue_comic": {"frame_count": 9}}, "checklist_version": "1"}
    path = tmp_path / "profile.json"; _write(path, profile)
    return load_editorial_profile(path)


@pytest.mark.parametrize("script_format", ["TALKING_GUIDE", "BACKGROUND_VOICE", "TEXT_LED_VIDEO", "DIALOGUE_COMIC"])
def test_fake_provider_preserves_identity_rank_human_priority_and_format(tmp_path: Path, script_format: str) -> None:
    package = build_script_input(brief=_brief(), profile=_profile(tmp_path), requested_format=script_format)
    output = DeterministicFakeScriptProvider().generate(package)
    assert output["validation"]["errors"] == []
    assert output["candidate_identity"] == package["candidate_identity"]
    assert output["original_rank"] == 1
    assert package["unresolved_fields"][0]["status"] == "NOT_TYPED"
    assert create_human_script_review(output)["episode_bridge_ready"] is False


def test_hard_gates_and_warning_are_distinct(tmp_path: Path) -> None:
    package = build_script_input(brief=_brief(), profile=_profile(tmp_path), requested_format="TALKING_GUIDE")
    output = DeterministicFakeScriptProvider().generate(package)
    output["original_rank"] = 2
    output["payload"] = {"text": "диагноз гарантирован source catchphrase"}
    result = validate_script_output(package, output)
    assert {"ORIGINAL_RANK_MISMATCH", "PROHIBITED_COPYING_ELEMENT_RETURNED", "MEDICAL_OR_DIAGNOSIS_CLAIM", "GUARANTEED_OUTCOME_OR_PREDICTION"}.issubset(result["errors"])
    output["original_rank"] = 1; output["payload"] = {"text": "human mechanism approved hook это нормально"}
    assert "EMPTY_VALIDATION" in validate_script_output(package, output)["warnings"]


def test_rejects_unsupported_format_and_reuses_atomic_artifact(tmp_path: Path) -> None:
    profile = _profile(tmp_path)
    with pytest.raises(NuraScriptContractError, match="UNSUPPORTED_SCRIPT_FORMAT"):
        build_script_input(brief=_brief(), profile=profile, requested_format="CAROUSEL")
    path = tmp_path / "runtime" / "input.json"; value = {"artifact": "synthetic"}
    assert persist_package(path, value) == "COMPLETED"
    assert persist_package(path, value) == "REUSED"
