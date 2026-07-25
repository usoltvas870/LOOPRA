import json
import sys
from pathlib import Path

import httpx
import pytest

RADAR_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RADAR_ROOT / "src")]

from content_intelligence import ContentIntelligenceError, ProjectAnalysisContext, build_analysis_input, build_card, hash_payload, validate_provider_result
from content_intelligence_provider import (
    MODEL_ID, DeepSeekContentIntelligenceProvider, ProviderTransportError,
    _reuse_identity, _reuse_real, _validate_request_body,
    _without_reasoning_content, build_provider_payload, load_project_context,
    run_real_analysis,
)
from test_content_intelligence import _fixture


def _input(tmp_path: Path) -> tuple[dict, dict]:
    paths = _fixture(tmp_path)
    value = build_analysis_input(paths["manifest"], "video-1", acquisition_root=paths["acquisition"], inspection_root=paths["inspection"], intelligence_evidence_root=paths["evidence"], project_context=ProjectAnalysisContext("nura", "1.0"))
    snapshot = {"schema_version": "1.0", "context_version": "1.0", "project_id": "nura", "project_name": "NURA", "audience_summary": "a", "brand_role": "b", "adaptation_objective": "c", "available_formats": [], "production_constraints": [], "allowed_claims": [], "prohibited_claims": [], "safety_constraints": [], "tone": "ru"}
    return value, snapshot


def test_provider_payload_is_bounded_and_private(tmp_path: Path) -> None:
    value, snapshot = _input(tmp_path)
    payload = build_provider_payload(value, snapshot)
    serialized = json.dumps(payload, ensure_ascii=False)
    assert "C:\\" not in serialized
    assert "source.mp4" not in serialized
    assert payload["ocr"]["events"][0]["text"] == "x" * 240
    assert len(payload["transcription"]["segments"][0]["text"]) == 240


def test_provider_rejects_fact_claim_before_card(tmp_path: Path) -> None:
    value, snapshot = _input(tmp_path)
    payload = build_provider_payload(value, snapshot)
    body = {"choices": [{"message": {"content": json.dumps({"claims": [{"claim_id": "bad", "claim_type": "FACT", "field": "x", "text": "bad", "evidence_refs": []}], "project_adaptation": {}, "warnings": []})}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 1, "completion_tokens": 1}}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=body, headers={"content-type": "application/json", "x-request-id": "r"}))
    provider = DeepSeekContentIntelligenceProvider(api_key="test-key", transport=transport)
    result, _, _ = provider.analyze(value, payload)
    with pytest.raises(ContentIntelligenceError, match="cannot emit FACT"):
        validate_provider_result(result, value, provider)


def test_provider_accepts_valid_structured_json(tmp_path: Path) -> None:
    value, snapshot = _input(tmp_path)
    payload = build_provider_payload(value, snapshot)
    body = {"choices": [{"message": {"content": json.dumps({"claims": [{"claim_id": "ok", "claim_type": "INFERENCE", "field": "format", "text": "Вероятностный вывод.", "evidence_refs": ["ocr:first_hook"], "confidence": 0.5}], "project_adaptation": {"suggested_hook": "Мягко исследуйте свой паттерн."}, "warnings": []})}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 1, "completion_tokens": 1}}
    provider = DeepSeekContentIntelligenceProvider(api_key="test-key", transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body, headers={"content-type": "application/json"})))
    result, _, metadata = provider.analyze(value, payload)
    assert validate_provider_result(result, value, provider)["claims"][0]["claim_type"] == "INFERENCE"
    assert metadata["payload_hash"]


def test_request_body_uses_official_json_object_mode(tmp_path: Path) -> None:
    value, snapshot = _input(tmp_path)
    body = DeepSeekContentIntelligenceProvider(api_key="test-key").build_request_body(build_provider_payload(value, snapshot))
    assert MODEL_ID == "deepseek-v4-flash"
    assert set(body) == {"model", "messages", "response_format", "thinking", "temperature", "max_tokens"}
    assert body["model"] == "deepseek-v4-flash"
    assert body["response_format"] == {"type": "json_object"}
    assert body["thinking"] == {"type": "disabled"}
    assert "max_output_tokens" not in body and "json_schema" not in json.dumps(body)
    assert [item["role"] for item in body["messages"]] == ["system", "user"]
    assert "JSON" in body["messages"][0]["content"]


@pytest.mark.parametrize("mutation", ("old_model", "reasoner", "pro", "thinking", "thinking_extra", "nan"))
def test_request_model_rejects_non_selected_contract(tmp_path: Path, mutation: str) -> None:
    value, snapshot = _input(tmp_path)
    body = DeepSeekContentIntelligenceProvider(api_key="test-key").build_request_body(build_provider_payload(value, snapshot))
    if mutation == "old_model":
        body["model"] = "deepseek-chat"
    elif mutation == "reasoner":
        body["model"] = "deepseek-reasoner"
    elif mutation == "pro":
        body["model"] = "deepseek-v4-pro"
    elif mutation == "thinking":
        body["thinking"] = {"type": "enabled"}
    elif mutation == "thinking_extra":
        body["thinking"] = {"type": "disabled", "reasoning_effort": "high"}
    else:
        body["temperature"] = float("nan")
    with pytest.raises(ContentIntelligenceError, match="REQUEST_CONTRACT_INVALID"):
        _validate_request_body(body)


def test_http_400_is_classified_and_redacted(tmp_path: Path) -> None:
    value, snapshot = _input(tmp_path)
    body = {"error": {"message": "unsupported field response_format", "type": "invalid_request_error", "code": "invalid_parameter"}}
    provider = DeepSeekContentIntelligenceProvider(api_key="secret-value", transport=httpx.MockTransport(lambda request: httpx.Response(400, json=body, headers={"content-type": "application/json", "x-request-id": "request-1"})))
    with pytest.raises(ProviderTransportError) as raised:
        provider.analyze(value, build_provider_payload(value, snapshot))
    assert raised.value.code == "PROVIDER_HTTP_400_INVALID_FORMAT"
    assert raised.value.metadata["request_id"] == "request-1"
    assert "secret-value" not in json.dumps(raised.value.metadata)


@pytest.mark.parametrize("content", ("", "   "))
def test_empty_json_content_is_typed_invalid_output(tmp_path: Path, content: str) -> None:
    value, snapshot = _input(tmp_path)
    body = {"choices": [{"message": {"content": content}, "finish_reason": "stop"}]}
    provider = DeepSeekContentIntelligenceProvider(api_key="test-key", transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body, headers={"content-type": "application/json"})))
    with pytest.raises(ContentIntelligenceError, match="PROVIDER_EMPTY_CONTENT"):
        provider.analyze(value, build_provider_payload(value, snapshot))


def test_minimal_probe_has_no_content_intelligence_payload() -> None:
    body = {"choices": [{"message": {"content": '{"status":"ok"}'}}]}
    provider = DeepSeekContentIntelligenceProvider(api_key="test-key", transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body, headers={"content-type": "application/json"})))
    metadata, shape = provider.probe()
    assert metadata["http_status"] == 200
    assert shape["response_format"] == {"type": "json_object"}


def test_reasoning_content_is_not_persisted_or_used() -> None:
    raw = {"choices": [{"message": {"content": '{"claims":[]}', "reasoning_content": "private chain"}}]}
    sanitized, metadata = _without_reasoning_content(raw)
    assert "reasoning_content" not in sanitized["choices"][0]["message"]
    assert metadata == {"reasoning_content_present": True, "reasoning_content_characters": 13}
    assert raw["choices"][0]["message"]["reasoning_content"] == "private chain"


def test_reuse_repairs_legacy_generic_context_hash_without_transport(tmp_path: Path) -> None:
    value, snapshot = _input(tmp_path)
    context_hash = hash_payload(snapshot)
    provider = DeepSeekContentIntelligenceProvider(api_key="")
    provider_result = {
        "schema_version": "0.1",
        "provider": provider.metadata(),
        "candidate_identity": {"video_id": "video-1", "rank": 1},
        "claims": [{"claim_id": "ok", "claim_type": "INFERENCE", "field": "format", "text": "Вывод.", "evidence_refs": ["ocr:first_hook"], "confidence": None}],
        "project_adaptation": {},
        "warnings": [],
    }
    card = build_card(value, validate_provider_result(provider_result, value, provider))
    card["reuse_identity"] = _reuse_identity(value, context_hash, provider)
    card["card_hash"] = hash_payload({key: item for key, item in card.items() if key != "card_hash"})
    path = tmp_path / "card.json"
    path.write_text(json.dumps(card), encoding="utf-8")
    reused = _reuse_real(path, value, context_hash)
    assert reused is not None
    assert reused["project_context_hash"] == context_hash
    normalized = path.read_bytes()
    assert json.loads(normalized)["card_hash"] == reused["card_hash"]
    assert _reuse_real(path, value, context_hash)["card_hash"] == reused["card_hash"]
    assert _reuse_real(path, value, context_hash)["card_hash"] == reused["card_hash"]
    assert path.read_bytes() == normalized


def test_corrupt_card_is_not_reused(tmp_path: Path) -> None:
    value, snapshot = _input(tmp_path)
    path = tmp_path / "card.json"
    path.write_text('{"schema_version":"0.1","card_hash":"wrong"}', encoding="utf-8")
    assert _reuse_real(path, value, hash_payload(snapshot)) is None


def test_reuse_only_miss_never_creates_transport(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = _fixture(tmp_path)
    _, snapshot = _input(tmp_path / "other")
    context_path = tmp_path / "context.json"
    context_path.write_text(json.dumps(snapshot), encoding="utf-8")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(httpx, "Client", lambda *args, **kwargs: pytest.fail("UNEXPECTED_PROVIDER_TRANSPORT_CALL"))
    with pytest.raises(ContentIntelligenceError, match="REUSE_ONLY_MISS"):
        run_real_analysis(
            paths["manifest"],
            candidate_id="video-1",
            acquisition_root=paths["acquisition"],
            inspection_root=paths["inspection"],
            intelligence_evidence_root=paths["evidence"],
            output_root=tmp_path / "out",
            context_path=context_path,
            allow_network=False,
            reuse_only=True,
        )


def test_missing_credentials_are_blocked_without_transport(tmp_path: Path) -> None:
    value, snapshot = _input(tmp_path)
    provider = DeepSeekContentIntelligenceProvider(api_key="", transport=httpx.MockTransport(lambda request: pytest.fail("network called")))
    with pytest.raises(ContentIntelligenceError, match="BLOCKED_PROVIDER_CREDENTIALS"):
        provider.analyze(value, build_provider_payload(value, snapshot))


def test_project_context_hash_is_deterministic(tmp_path: Path) -> None:
    source = tmp_path / "context.json"
    source.write_text(json.dumps({"schema_version": "1.0", "context_version": "1.0", "project_id": "nura", "project_name": "NURA", "audience_summary": "a", "brand_role": "b", "adaptation_objective": "c", "available_formats": [], "production_constraints": [], "allowed_claims": [], "prohibited_claims": [], "safety_constraints": [], "tone": "ru"}), encoding="utf-8")
    first = load_project_context(source)[2]
    second = load_project_context(source)[2]
    assert first == second
