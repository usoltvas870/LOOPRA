import hashlib
import json
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

from content_intelligence_provider import ProviderTransportError
from nura_production_brief import hash_payload
from nura_real_script_provider import (
    DeepSeekNuraScriptProvider, NuraRealScriptProviderError, NuraScriptPromptContract,
    build_bounded_provider_request, reprocess_existing_raw, run_real_script_provider,
)
from nura_script_contract import build_script_input, load_editorial_profile


HOOK = "Ты продолжаешь поддерживать других, даже когда сама уже выгораешь?"
MECHANISM = "Поддержка другого человека при собственном выгорании; музыка вторична."


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def _fixture(tmp_path: Path) -> tuple[Path, Path, dict]:
    guide = tmp_path / "guide.md"; guide.write_text("full editorial markdown must never leave this fixture", encoding="utf-8")
    profile_path = tmp_path / "profile.json"
    _write(profile_path, {"schema_version": "0.1", "profile_id": "nura", "profile_version": "1", "project_id": "nura", "source_document": {"reference": "guide.md", "sha256": hashlib.sha256(guide.read_bytes()).hexdigest()}, "supported_content_scope": ["talking_guide"], "excluded_scope": ["core"], "voice_principles": ["calm"], "prohibited_voice_patterns": ["imitation"], "safety_principles": ["no diagnosis"], "format_principles": {"talking_guide": {"duration_seconds": [20, 35], "required": ["hook", "turn", "calm ending"]}}, "checklist_version": "1"})
    fields = {"source_mechanism_preserved": {"value": MECHANISM, "source_type": "HUMAN_REVISION"}, "suggested_hook": {"value": HOOK, "source_type": "HUMAN_ACCEPTED_AI_VALUE"}, "production_elements_not_copied": {"value": "лампа, исходный ролик и авторский стиль", "source_type": "HUMAN_ACCEPTED_AI_VALUE"}}
    brief = {"final_status": "COMPLETED", "readiness": "READY_WITH_HUMAN_REVISIONS", "brief_id": "brief-rank-one", "candidate_identity": {"video_id": "video-1"}, "original_rank": 1, "source_review": {"review_id": "review-1", "review_hash": "review-hash"}, "project_identity": {"project_id": "nura", "context_version": "1", "context_hash": "context-hash"}, "fields": fields, "evidence_limitations": ["evidence is bounded"], "safety_constraints": ["no diagnosis"], "unresolved_fields": []}
    brief["brief_hash"] = hash_payload(brief)
    brief_path = tmp_path / "production_brief.json"; _write(brief_path, brief)
    profile = load_editorial_profile(profile_path, repository_root=tmp_path)
    return brief_path, profile_path, build_script_input(brief=brief, profile=profile, requested_format="TALKING_GUIDE")


def _raw(text: str) -> dict:
    blocks = [{"kind": "hook", "text": HOOK}, {"kind": "development", "text": MECHANISM}, {"kind": "ending", "text": "Можно заметить это сегодня и оставить себе немного бережности."}]
    revisions = {name: {"application": "bounded", "block_ids": ["development"], "spans": [MECHANISM]} for name in ("revision_1",)}
    return {"choices": [{"message": {"content": json.dumps({"payload": {"text": text, "blocks": blocks}, "constraint_realization": {"approved_mechanism": {"application": "narrative", "block_ids": ["development"], "spans": [MECHANISM]}, "mandatory_human_revisions": revisions}})}}], "usage": {"total_tokens": 1}}


def _raw_with_realization(text: str, development: str, span: str) -> dict:
    blocks = [{"kind": "hook", "text": HOOK}, {"kind": "development", "text": development}, {"kind": "ending", "text": "Можно заметить это сегодня и оставить себе немного бережности."}]
    realization = {"approved_mechanism": {"application": "narrative", "block_ids": ["development"], "spans": [span]}, "mandatory_human_revisions": {"revision_1": {"application": "human-reviewed direction", "block_ids": ["development"], "spans": [span]}}}
    return {"choices": [{"message": {"content": json.dumps({"payload": {"text": text, "blocks": blocks}, "constraint_realization": realization})}}]}


def _transport(body: dict, seen: list[httpx.Request] | None = None) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if seen is not None: seen.append(request)
        return httpx.Response(200, json=body, headers={"content-type": "application/json", "x-request-id": "test-request"})
    return httpx.MockTransport(handler)


def test_bounded_request_contains_human_authority_and_excludes_corpora(tmp_path: Path) -> None:
    _, _, package = _fixture(tmp_path)
    request = build_bounded_provider_request(package)
    encoded = json.dumps(request, ensure_ascii=False)
    assert request["candidate"]["rank"] == 1
    assert request["approved_hook"] == HOOK
    assert request["mandatory_human_revisions"][0]["value"] == MECHANISM
    assert "лампа" in request["prohibited_copying_elements"][0]
    assert all(token not in encoded.lower() for token in ("full editorial markdown", "c:\\", "ocr", "transcript", "rank\": 2"))


def test_deepseek_adapter_uses_shared_json_thinking_disabled_transport(tmp_path: Path) -> None:
    _, _, package = _fixture(tmp_path); seen: list[httpx.Request] = []
    provider = DeepSeekNuraScriptProvider(api_key="test-key", transport=_transport(_raw(HOOK + " " + MECHANISM), seen))
    provider.generate(build_bounded_provider_request(package))
    body = json.loads(seen[0].content)
    assert body["response_format"] == {"type": "json_object"}
    assert body["thinking"] == {"type": "disabled"}
    assert seen[0].headers["authorization"] == "Bearer test-key"
    assert "test-key" not in json.dumps(body, ensure_ascii=False)


def test_valid_output_persists_draft_and_pending_human_review(tmp_path: Path) -> None:
    brief, profile, _ = _fixture(tmp_path)
    result = run_real_script_provider(brief_path=brief, profile_path=profile, repository_root=tmp_path, output_root=tmp_path / "runtime", allow_network=True, api_key="test-key", transport=_transport(_raw(HOOK + " " + MECHANISM)))
    assert result["status"] == "COMPLETED"
    assert result["output"]["draft_status"] == "DRAFT_AWAITING_HUMAN_REVIEW"
    review = json.loads(Path(result["review_path"]).read_text(encoding="utf-8"))
    assert review["episode_bridge_ready"] is False and review["human_confirmation"] is False


def test_mechanism_realization_uses_actual_spans_not_service_phrase(tmp_path: Path) -> None:
    brief, profile, _ = _fixture(tmp_path)
    development = "Ты остаёшься опорой для близкого, а собственную усталость снова откладываешь."
    text = HOOK + " " + development + " Можно заметить это и не исчезать из собственной жизни."
    result = run_real_script_provider(brief_path=brief, profile_path=profile, repository_root=tmp_path, output_root=tmp_path / "runtime", allow_network=True, api_key="test-key", transport=_transport(_raw_with_realization(text, development, development)))
    assert result["output"]["validation"]["errors"] == []
    assert "MECHANISM_REALIZATION_REQUIRES_HUMAN_REVIEW" in result["output"]["validation"]["unresolved_checks"]


def test_no_music_mention_is_not_a_hard_revision_failure(tmp_path: Path) -> None:
    brief, profile, _ = _fixture(tmp_path)
    development = "Ты поддерживаешь близкого, хотя своё истощение оставляешь без внимания."
    text = HOOK + " " + development + " Маленький шаг — спросить себя, что тебе сейчас нужно."
    result = run_real_script_provider(brief_path=brief, profile_path=profile, repository_root=tmp_path, output_root=tmp_path / "runtime", allow_network=True, api_key="test-key", transport=_transport(_raw_with_realization(text, development, development)))
    assert "MANDATORY_HUMAN_REVISION_IGNORED" not in result["output"]["validation"]["errors"]


def test_music_led_meaning_remains_hard_failure(tmp_path: Path) -> None:
    brief, profile, _ = _fixture(tmp_path)
    development = "Музыка объясняет главный смысл: ты поддерживаешь близкого, хотя своё истощение оставляешь без внимания."
    text = HOOK + " " + development
    with pytest.raises(NuraRealScriptProviderError, match="MUSIC_AS_PRIMARY_MEANING"):
        run_real_script_provider(brief_path=brief, profile_path=profile, repository_root=tmp_path, output_root=tmp_path / "runtime", allow_network=True, api_key="test-key", transport=_transport(_raw_with_realization(text, development, development)))


@pytest.mark.parametrize("bad_text,code", [
    ("Привет! " + HOOK + " " + MECHANISM, "APPROVED_HOOK_NOT_OPENING"),
    (HOOK + " " + MECHANISM + " Лампа всё объясняет.", "PROHIBITED_LAMP_METAPHOR"),
    (HOOK + " " + MECHANISM + " Это диагноз.", "MEDICAL_OR_DIAGNOSIS_CLAIM"),
    (HOOK + " " + MECHANISM + " Я гарантирую результат.", "GUARANTEED_OUTCOME_OR_PREDICTION"),
])
def test_hard_validation_rejects_unsafe_or_altered_drafts_and_retains_raw(tmp_path: Path, bad_text: str, code: str) -> None:
    brief, profile, _ = _fixture(tmp_path)
    with pytest.raises(NuraRealScriptProviderError, match="SCRIPT_OUTPUT_VALIDATION_FAILED"):
        run_real_script_provider(brief_path=brief, profile_path=profile, repository_root=tmp_path, output_root=tmp_path / "runtime", allow_network=True, api_key="test-key", transport=_transport(_raw(bad_text)))
    assert list((tmp_path / "runtime").glob("*/raw_provider_response.json"))
    assert not list((tmp_path / "runtime").glob("*/validated_script_output.json"))
    report = json.loads(next((tmp_path / "runtime").glob("*/validation_report.json")).read_text(encoding="utf-8"))
    assert code in report["errors"]


def test_malformed_json_is_rejected_after_raw_persistence(tmp_path: Path) -> None:
    brief, profile, _ = _fixture(tmp_path)
    bad = {"choices": [{"message": {"content": "not json"}}]}
    with pytest.raises(NuraRealScriptProviderError, match="MALFORMED"):
        run_real_script_provider(brief_path=brief, profile_path=profile, repository_root=tmp_path, output_root=tmp_path / "runtime", allow_network=True, api_key="test-key", transport=_transport(bad))
    assert list((tmp_path / "runtime").glob("*/raw_provider_response.json"))


def test_reuse_requires_no_credentials_or_network(tmp_path: Path) -> None:
    brief, profile, _ = _fixture(tmp_path)
    first = run_real_script_provider(brief_path=brief, profile_path=profile, repository_root=tmp_path, output_root=tmp_path / "runtime", allow_network=True, api_key="test-key", transport=_transport(_raw(HOOK + " " + MECHANISM)))
    second = run_real_script_provider(brief_path=brief, profile_path=profile, repository_root=tmp_path, output_root=tmp_path / "runtime", reuse_only=True, transport=httpx.MockTransport(lambda request: pytest.fail("network called")))
    assert first["output"]["content_hash"] == second["output"]["content_hash"]
    assert second["status"] == "REUSED" and second["network_calls"] == 0 and second["credentials_required"] is False


@pytest.mark.parametrize("status,code", [(401, "AUTHENTICATION"), (429, "RATE_LIMITED")])
def test_provider_http_failures_are_classified(tmp_path: Path, status: int, code: str) -> None:
    _, _, package = _fixture(tmp_path)
    provider = DeepSeekNuraScriptProvider(api_key="test-key", transport=httpx.MockTransport(lambda request: httpx.Response(status, json={"error": {"message": "safe"}}, headers={"content-type": "application/json"})))
    with pytest.raises(ProviderTransportError, match=code): provider.generate(build_bounded_provider_request(package))


def _offline_raw(path: Path, response: dict) -> Path:
    artifact = {"provider": {"provider_id": "deepseek-nura-script", "provider_version": "1.0", "model_id": "deepseek-v4-flash", "prompt_id": "nura-script-generation", "prompt_version": "1.2", "configuration": {}, "fake": False}, "request_hash": "legacy-request", "metadata": {"http_status": 200, "response_hash": "recorded-raw"}, "response": response}
    _write(path, artifact)
    return path


def test_offline_reprocessing_materializes_canonical_blocks_without_network(tmp_path: Path) -> None:
    brief, profile, _ = _fixture(tmp_path)
    raw = _offline_raw(tmp_path / "runtime" / "raw_provider_response.json", _raw(HOOK + " " + MECHANISM))
    before = raw.read_bytes()
    result = reprocess_existing_raw(raw_path=raw, brief_path=brief, profile_path=profile, repository_root=tmp_path)
    assert result["provider_call_performed"] is False and result["current_network_calls"] == 0 and result["credentials_required"] is False
    assert raw.read_bytes() == before
    evidence = result["output"]["resolved_constraint_evidence"][0]
    assert evidence["resolved_block_texts"][0] == MECHANISM
    assert result["episode_bridge_ready"] is False
    assert reprocess_existing_raw(raw_path=raw, brief_path=brief, profile_path=profile, repository_root=tmp_path)["status"] == "REUSED"


@pytest.mark.parametrize("constraint", [
    {"constraint_id": "approved_mechanism", "block_ids": ["unknown"]},
    {"constraint_id": "unknown", "block_ids": ["development"]},
])
def test_advisory_unknown_constraint_or_block_remains_hard_failure(tmp_path: Path, constraint: dict) -> None:
    brief, profile, _ = _fixture(tmp_path)
    response = _raw(HOOK + " " + MECHANISM)
    creative = json.loads(response["choices"][0]["message"]["content"])
    creative["constraint_realization"] = [constraint]
    response["choices"][0]["message"]["content"] = json.dumps(creative)
    raw = _offline_raw(tmp_path / "runtime" / "raw_provider_response.json", response)
    with pytest.raises(NuraRealScriptProviderError, match="SCRIPT_OUTPUT_VALIDATION_FAILED"):
        reprocess_existing_raw(raw_path=raw, brief_path=brief, profile_path=profile, repository_root=tmp_path)


def test_effective_request_identity_changes_for_prompt_version_and_body(tmp_path: Path) -> None:
    _, _, package = _fixture(tmp_path); request = build_bounded_provider_request(package)
    provider = DeepSeekNuraScriptProvider(api_key="test-key")
    first = provider.effective_request_identity(request)
    provider.contract = NuraScriptPromptContract(prompt_version="test-version")
    version_identity = provider.effective_request_identity(request)
    assert version_identity != first
    class ChangedBodyContract(NuraScriptPromptContract):
        def system_contract(self) -> str: return super().system_contract() + "\nChanged effective instruction."
    provider.contract = ChangedBodyContract(prompt_version="test-version")
    assert provider.effective_request_identity(request) != version_identity
