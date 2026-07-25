"""Vendor-isolated Stage 5D DeepSeek adapter and prompt/payload contract."""
from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from content_intelligence import (
    AnalysisStatus, ContentIntelligenceError, ProjectAnalysisContext, build_analysis_input,
    build_card, hash_payload, validate_provider_result,
)

PROMPT_VERSION = "1.0"
OUTPUT_SCHEMA_VERSION = "1.0"
PROVIDER_ID = "deepseek"
MODEL_ID = "deepseek-v4-flash"
ENDPOINT = "https://api.deepseek.com/chat/completions"
TIMEOUT_SECONDS = 45.0
MAX_RESPONSE_BYTES = 256_000
MAX_PAYLOAD_CHARS = 24_000
MAX_CAPTION_CHARS = 500
MAX_OCR_EVENTS = 8
MAX_OCR_CHARS = 1_200
MAX_TRANSCRIPT_SEGMENTS = 8
MAX_TRANSCRIPT_CHARS = 1_600
MAX_FRAME_REFS = 8
MAX_EVIDENCE_REFS = 40
MAX_ERROR_BODY_BYTES = 4096
MAX_ERROR_MESSAGE_CHARS = 500


@dataclass(frozen=True)
class ContentIntelligencePromptContract:
    provider_id: str = PROVIDER_ID
    model_id: str = MODEL_ID
    prompt_version: str = PROMPT_VERSION
    output_schema_version: str = OUTPUT_SCHEMA_VERSION
    temperature: float = 0.2
    max_output_tokens: int = 1800

    def system_contract(self) -> str:
        return "\n".join((
            "You are a bounded Content Intelligence analyst.",
            "Use only the supplied evidence summary; do not use external knowledge about this video or author.",
            "Return JSON only, with no Markdown.",
            "Do not return candidate identity, rank, metrics, scoring, classification, caption source, OCR text, transcript, or visual facts as authoritative data.",
            "Never create FACT claims. Every claim must be INFERENCE or AI_INTERPRETATION.",
            "Every evidence-dependent claim must cite only an evidence_id from evidence_index. If support is insufficient, omit the conclusion and add a warning.",
            "OCR and transcript are machine observations and are not human-verified.",
            "Analyse transferable mechanism; do not reconstruct the script, imitate the author, or copy visual production.",
            "NURA is a calm AI guide: no human lived experience, therapy, diagnosis, guaranteed result, or deterministic prediction.",
            "Production complexity never changes ranking.",
            "Write Russian output because the project context requires it.",
            "Return exactly one JSON object. Example: {\"claims\":[{\"claim_id\":\"example-1\",\"claim_type\":\"INFERENCE\",\"field\":\"format\",\"text\":\"Синтетический вероятностный вывод.\",\"evidence_refs\":[\"evidence-example\"],\"confidence\":null}],\"project_adaptation\":{},\"warnings\":[]}.",
        ))

    def output_contract(self) -> dict[str, Any]:
        return {
            "schema_version": self.output_schema_version,
            "required": ["claims", "project_adaptation", "warnings"],
            "claim": {"claim_id": "string", "claim_type": ["INFERENCE", "AI_INTERPRETATION"], "field": "string", "text": "string <= 1000 chars", "evidence_refs": "list[evidence_id]", "confidence": "number|null"},
            "project_adaptation": "object with safe, materially rewritten Russian recommendations",
            "warnings": "list[string]",
        }

    def messages(self, provider_payload: dict[str, Any]) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.system_contract()},
            {"role": "user", "content": json.dumps({"input_contract": provider_payload, "output_contract": self.output_contract()}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))},
        ]


def load_project_context(path: Path) -> tuple[ProjectAnalysisContext, dict[str, Any], str]:
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContentIntelligenceError("invalid project context snapshot") from error
    required = {"schema_version", "context_version", "project_id", "project_name", "audience_summary", "brand_role", "adaptation_objective", "available_formats", "production_constraints", "allowed_claims", "prohibited_claims", "safety_constraints", "tone"}
    if not required <= snapshot.keys() or snapshot["project_id"] != "nura":
        raise ContentIntelligenceError("project context snapshot is incomplete or has an unexpected project id")
    context = ProjectAnalysisContext(snapshot["project_id"], snapshot["context_version"], snapshot["audience_summary"], ("suggested_hook", "adaptation_idea", "format"), "projects/nura/content_intelligence_context.json")
    return context, snapshot, hash_payload(snapshot)


def build_provider_payload(analysis_input: dict[str, Any], context_snapshot: dict[str, Any]) -> dict[str, Any]:
    evidence = analysis_input["evidence"]
    index = analysis_input["evidence_index"][:MAX_EVIDENCE_REFS]
    safe_index = [{key: item[key] for key in ("ref_id", "kind", "timestamp_seconds") if key in item} for item in index]
    ocr_events = evidence.get("ocr", {}).get("events", [])[:MAX_OCR_EVENTS]
    transcript = evidence.get("transcription", {}).get("segments", [])[:MAX_TRANSCRIPT_SEGMENTS]
    payload = {
        "schema_version": "1.0",
        "candidate": {"video_id": analysis_input["candidate_identity"]["video_id"], "rank": analysis_input["candidate_identity"]["rank"], "classification": analysis_input["candidate_identity"]["classification"], "metrics": analysis_input["candidate_identity"]["metrics_snapshot"], "scores": analysis_input["candidate_identity"]["score_snapshot"]},
        "caption": "",
        "media_facts": evidence.get("inspection", {}).get("media_facts", {}),
        "ocr": {"first_hook": evidence.get("ocr", {}).get("first_text_hook"), "events": [{"event_id": item.get("event_id"), "text": _clip(str(item.get("text") or ""), MAX_OCR_CHARS), "timestamp_seconds": item.get("first_seen_at_sec")} for item in ocr_events]},
        "transcription": {"first_words": evidence.get("transcription", {}).get("first_spoken_words"), "segments": [{"segment_id": item.get("segment_id"), "text": _clip(str(item.get("text") or ""), MAX_TRANSCRIPT_CHARS), "start_seconds": item.get("start_seconds"), "end_seconds": item.get("end_seconds")} for item in transcript]},
        "frame_summaries": [{"ref_id": item["ref_id"], "timestamp_seconds": item.get("timestamp_seconds")} for item in safe_index if item.get("kind") == "format_frame"][:MAX_FRAME_REFS],
        "missing_evidence": analysis_input["missing_evidence"],
        "evidence_index": safe_index,
        "project_context": context_snapshot,
        "truncation": {"caption_max_chars": MAX_CAPTION_CHARS, "ocr_events_included": len(ocr_events), "transcript_segments_included": len(transcript)},
    }
    _validate_provider_payload(payload)
    return payload


class DeepSeekContentIntelligenceProvider:
    provider_id = PROVIDER_ID
    provider_version = "1.0"
    model_id = MODEL_ID
    configuration = {
        "endpoint": ENDPOINT,
        "response_format": {"type": "json_object"},
        "thinking": {"type": "disabled"},
        "temperature": 0.2,
        "max_tokens": 1800,
        "prompt_version": PROMPT_VERSION,
        "output_schema_version": OUTPUT_SCHEMA_VERSION,
    }

    def __init__(self, api_key: str | None = None, transport: httpx.BaseTransport | None = None) -> None:
        self._api_key = api_key if api_key is not None else os.environ.get("DEEPSEEK_API_KEY")
        self._transport = transport
        self.contract = ContentIntelligencePromptContract()

    @property
    def credentials_available(self) -> bool:
        return bool(self._api_key)

    def analyze(self, analysis_input: dict[str, Any], provider_payload: dict[str, Any], *, corrective_errors: list[str] | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        if not self.credentials_available:
            raise ContentIntelligenceError("BLOCKED_PROVIDER_CREDENTIALS")
        body = self.build_request_body(provider_payload)
        if corrective_errors:
            body["messages"].append({"role": "user", "content": "Correct the previous output. Validation errors: " + "; ".join(corrective_errors[:5]) + ". Return complete JSON only."})
        started = time.perf_counter()
        try:
            with httpx.Client(timeout=TIMEOUT_SECONDS, follow_redirects=False, transport=self._transport) as client:
                response = client.post(ENDPOINT, headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}, json=body)
        except httpx.TimeoutException as error:
            raise ProviderTransportError("PROVIDER_TIMEOUT") from error
        latency_ms = round((time.perf_counter() - started) * 1000)
        if response.status_code in {401, 403}:
            raise _provider_error("PROVIDER_AUTHENTICATION_FAILED", response, latency_ms)
        if response.status_code == 402:
            raise _provider_error("PROVIDER_BALANCE_OR_ACCOUNT_BLOCKED", response, latency_ms)
        if response.status_code == 429:
            raise _provider_error("PROVIDER_RATE_LIMITED", response, latency_ms)
        if response.status_code >= 500:
            raise _provider_error("PROVIDER_TRANSIENT_ERROR", response, latency_ms)
        if response.status_code == 400:
            raise _provider_error("PROVIDER_HTTP_400_INVALID_FORMAT", response, latency_ms)
        if response.status_code != 200:
            raise _provider_error(f"PROVIDER_HTTP_{response.status_code}", response, latency_ms)
        if "application/json" not in response.headers.get("content-type", "") or len(response.content) > MAX_RESPONSE_BYTES:
            raise ContentIntelligenceError("PROVIDER_RESPONSE_UNSAFE")
        raw = response.json()
        try:
            content = raw["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ContentIntelligenceError("PROVIDER_EMPTY_CONTENT")
            parsed = json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise ContentIntelligenceError("PROVIDER_INVALID_JSON") from error
        result = {"schema_version": "0.1", "provider": self.metadata(), "candidate_identity": {"video_id": analysis_input["candidate_identity"]["video_id"], "rank": analysis_input["candidate_identity"]["rank"]}, "claims": parsed.get("claims"), "project_adaptation": parsed.get("project_adaptation"), "warnings": parsed.get("warnings", [])}
        persisted_raw, reasoning_metadata = _without_reasoning_content(raw)
        metadata = {"provider_id": self.provider_id, "model_id": self.model_id, "request_id": response.headers.get("x-request-id"), "prompt_version": PROMPT_VERSION, "output_schema_version": OUTPUT_SCHEMA_VERSION, "payload_hash": hash_payload(provider_payload), "response_hash": hash_payload(persisted_raw), "latency_ms": latency_ms, "usage": raw.get("usage"), "finish_reason": raw.get("choices", [{}])[0].get("finish_reason"), "cost": None, **reasoning_metadata}
        return result, persisted_raw, metadata

    def build_request_body(self, provider_payload: dict[str, Any]) -> dict[str, Any]:
        body = {"model": self.model_id, "messages": self.contract.messages(provider_payload), "response_format": {"type": "json_object"}, "thinking": {"type": "disabled"}, "temperature": self.contract.temperature, "max_tokens": self.contract.max_output_tokens}
        _validate_request_body(body)
        return body

    def probe(self) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.credentials_available:
            raise ContentIntelligenceError("BLOCKED_PROVIDER_CREDENTIALS")
        body = {"model": self.model_id, "messages": [{"role": "system", "content": "Return exactly one JSON object. Example: {\"status\":\"ok\"}."}, {"role": "user", "content": "Return JSON with status ok."}], "response_format": {"type": "json_object"}, "thinking": {"type": "disabled"}, "temperature": 0, "max_tokens": 64}
        _validate_request_body(body)
        started = time.perf_counter()
        try:
            with httpx.Client(timeout=TIMEOUT_SECONDS, follow_redirects=False, transport=self._transport) as client:
                response = client.post(ENDPOINT, headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}, json=body)
        except httpx.TimeoutException as error:
            raise ProviderTransportError("PROVIDER_TIMEOUT") from error
        latency_ms = round((time.perf_counter() - started) * 1000)
        if response.status_code != 200:
            code = "PROVIDER_HTTP_400_INVALID_FORMAT" if response.status_code == 400 else f"PROVIDER_HTTP_{response.status_code}"
            raise _provider_error(code, response, latency_ms)
        try:
            raw = response.json(); parsed = json.loads(raw["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise ContentIntelligenceError("PROVIDER_INVALID_JSON") from error
        if parsed != {"status": "ok"}:
            raise ContentIntelligenceError("PROVIDER_SCHEMA_INVALID")
        return {"http_status": 200, "request_id": response.headers.get("x-request-id"), "latency_ms": latency_ms, "response_hash": hash_payload(raw)}, {"request_keys": list(body), "response_format": body["response_format"], "message_roles": [item["role"] for item in body["messages"]]}

    def metadata(self) -> dict[str, Any]:
        return {"provider_id": self.provider_id, "provider_version": self.provider_version, "model_id": self.model_id, "configuration": self.configuration, "fake": False}


def run_real_analysis(manifest_path: Path, *, candidate_id: str, acquisition_root: Path, inspection_root: Path, intelligence_evidence_root: Path, output_root: Path, context_path: Path, allow_network: bool, dry_run: bool = False, reuse_only: bool = False) -> dict[str, Any]:
    if reuse_only and allow_network:
        raise ContentIntelligenceError("reuse-only mode forbids --allow-network")
    if not allow_network and not dry_run and not reuse_only:
        raise ContentIntelligenceError("real provider requires --allow-network")
    context, snapshot, context_hash = load_project_context(context_path)
    analysis_input = build_analysis_input(manifest_path, candidate_id, acquisition_root=acquisition_root, inspection_root=inspection_root, intelligence_evidence_root=intelligence_evidence_root, project_context=context)
    if analysis_input["candidate_identity"]["rank"] != 1:
        raise ContentIntelligenceError("Stage 5D real mode accepts rank 1 only")
    payload = build_provider_payload(analysis_input, snapshot)
    identity_provider = DeepSeekContentIntelligenceProvider(api_key="")
    request_body = identity_provider.build_request_body(payload)
    run_id = f"real-{analysis_input['input_hash'][:12]}-{context_hash[:8]}-{PROVIDER_ID}-{MODEL_ID}-{PROMPT_VERSION}"
    root = output_root / run_id / "candidates" / candidate_id
    reuse_identity = _reuse_identity(analysis_input, context_hash, identity_provider)
    summary = {"status": "DRY_RUN", "video_id": candidate_id, "rank": 1, "provider": PROVIDER_ID, "model": MODEL_ID, "prompt_version": PROMPT_VERSION, "input_hash": analysis_input["input_hash"], "context_hash": context_hash, "payload_chars": len(json.dumps(payload, ensure_ascii=False)), "payload_bytes": len(json.dumps(payload, ensure_ascii=False).encode("utf-8")), "evidence_refs": len(payload["evidence_index"]), "endpoint": "api.deepseek.com/chat/completions", "request_keys": list(request_body), "response_format": request_body["response_format"], "thinking": request_body["thinking"], "message_roles": [message["role"] for message in request_body["messages"]], "request_hash": hash_payload(request_body), "reuse_identity": reuse_identity, "network": "NOT_RUN"}
    if dry_run:
        _write(root / "analysis_input.json", analysis_input); _write(root / "provider_payload.json", payload); _write(root / "project_context_snapshot.json", snapshot); _write(root / "provider_request_metadata.json", summary)
        return summary
    card_path = root / "content_intelligence_card.json"
    existing = _reuse_real(card_path, analysis_input, context_hash)
    if existing:
        return summary | {"status": AnalysisStatus.REUSED, "network": "NOT_CALLED", "card_hash": existing["card_hash"]}
    if reuse_only:
        raise ContentIntelligenceError("REUSE_ONLY_MISS")
    provider = DeepSeekContentIntelligenceProvider()
    last_error: ContentIntelligenceError | None = None
    for attempt in (1, 2):
        try:
            result, raw, metadata = provider.analyze(analysis_input, payload, corrective_errors=[str(last_error)] if last_error else None)
            validated = validate_provider_result(result, analysis_input, provider)
            card = build_card(analysis_input, validated)
            card["project_context_hash"] = context_hash
            card["reuse_identity"] = reuse_identity
            card["card_hash"] = hash_payload({key: value for key, value in card.items() if key != "card_hash"})
            metadata["attempt_count"] = attempt; metadata["validation_status"] = "VALID"
            _write(root / "analysis_input.json", analysis_input); _write(root / "provider_payload.json", payload); _write(root / "project_context_snapshot.json", snapshot); _write(root / "provider_raw_response.json", raw); _write(root / "provider_request_metadata.json", metadata); _write(root / "content_intelligence_card.json", card); _write(root / "validation.json", {"status": "VALID", "claim_count": len(card["claims"]), "evidence_refs": len(analysis_input["evidence_index"])})
            return summary | {"status": card["status"], "network": "CALLED", "attempts": attempt, "card_hash": card["card_hash"], "claim_counts": _claim_counts(card), "metadata": metadata}
        except ContentIntelligenceError as error:
            _write(root / "analysis_input.json", analysis_input); _write(root / "provider_payload.json", payload); _write(root / "project_context_snapshot.json", snapshot)
            if isinstance(error, ProviderTransportError):
                _write(root / "provider_error.json", error.metadata)
                _write(root / "provider_request_metadata.json", {"status": error.code, **error.metadata, "payload_hash": hash_payload(payload), "attempt_count": attempt})
            last_error = error
            if attempt == 2 or str(error) not in {"PROVIDER_EMPTY_CONTENT", "PROVIDER_INVALID_JSON", "AI provider cannot emit FACT claims", "claim contains an unknown evidence reference"}:
                raise
    raise last_error or ContentIntelligenceError("FAILED_PROVIDER_OUTPUT_INVALID")


def run_minimal_probe(*, output_root: Path, allow_network: bool) -> dict[str, Any]:
    if not allow_network:
        raise ContentIntelligenceError("real provider requires --allow-network")
    root = output_root / "minimal-transport-probe"
    try:
        metadata, shape = DeepSeekContentIntelligenceProvider().probe()
        result = {"status": "COMPLETED", "provider": PROVIDER_ID, "model": MODEL_ID, "network": "CALLED", **metadata, **shape}
        _write(root / "probe_metadata.json", result)
        return result
    except ProviderTransportError as error:
        _write(root / "probe_error.json", error.metadata)
        raise


class ProviderTransportError(ContentIntelligenceError):
    def __init__(self, code: str, metadata: dict[str, Any] | None = None) -> None:
        super().__init__(code); self.code = code; self.metadata = metadata or {}


def _provider_error(code: str, response: httpx.Response, latency_ms: int) -> ProviderTransportError:
    raw = response.content[:MAX_ERROR_BODY_BYTES]
    body_hash = hash_payload(raw.decode("utf-8", errors="replace"))
    message = ""
    error_type = None
    error_code = None
    try:
        parsed = json.loads(raw)
        item = parsed.get("error", parsed) if isinstance(parsed, dict) else {}
        if isinstance(item, dict):
            message = str(item.get("message", ""))[:MAX_ERROR_MESSAGE_CHARS]
            error_type = item.get("type")
            error_code = item.get("code")
    except json.JSONDecodeError:
        message = "non-json provider error body"
    return ProviderTransportError(code, {"http_status": response.status_code, "provider_error_type": error_type, "provider_error_code": error_code, "message": message, "request_id": response.headers.get("x-request-id"), "response_body_hash": body_hash, "response_body_bytes": len(response.content), "latency_ms": latency_ms})


def _validate_request_body(body: dict[str, Any]) -> None:
    if set(body) != {"model", "messages", "response_format", "thinking", "temperature", "max_tokens"}:
        raise ContentIntelligenceError("REQUEST_CONTRACT_INVALID")
    if body["model"] != MODEL_ID or body["response_format"] != {"type": "json_object"} or body["thinking"] != {"type": "disabled"}:
        raise ContentIntelligenceError("REQUEST_CONTRACT_INVALID")
    if not isinstance(body["temperature"], (int, float)) or not 0 <= body["temperature"] <= 1 or not isinstance(body["max_tokens"], int) or not 1 <= body["max_tokens"] <= 4096:
        raise ContentIntelligenceError("REQUEST_CONTRACT_INVALID")
    if not isinstance(body["messages"], list) or not body["messages"] or any(set(message) != {"role", "content"} or message["role"] not in {"system", "user", "assistant"} or not isinstance(message["content"], str) or not message["content"] for message in body["messages"]):
        raise ContentIntelligenceError("REQUEST_CONTRACT_INVALID")
    try:
        encoded = json.dumps(body, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ContentIntelligenceError("REQUEST_CONTRACT_INVALID") from error
    if len(encoded) > MAX_PAYLOAD_CHARS + 6000:
        raise ContentIntelligenceError("REQUEST_CONTRACT_INVALID")


def _clip(value: str, limit: int) -> str: return value[:limit]
def _validate_provider_payload(payload: dict[str, Any]) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if len(serialized) > MAX_PAYLOAD_CHARS: raise ContentIntelligenceError("INPUT_TOO_LARGE")
    lowered = serialized.lower()
    if any(token in lowered for token in ("c:\\", "/home/", "cookie", "base64", "data:video", "authorization")): raise ContentIntelligenceError("provider payload contains prohibited private data")
def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as temp: temp.write(encoded); name = temp.name
    Path(name).replace(path)
def _reuse_real(path: Path, analysis_input: dict[str, Any], context_hash: str) -> dict[str, Any] | None:
    try: card = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return None
    provider = card.get("provider", {})
    active = DeepSeekContentIntelligenceProvider(api_key="")
    expected_identity = _reuse_identity(analysis_input, context_hash, active)
    if card.get("input_hash") == analysis_input["input_hash"] and provider.get("provider_id") == PROVIDER_ID and provider.get("model_id") == MODEL_ID and provider.get("configuration") == active.configuration and card.get("reuse_identity") == expected_identity and not provider.get("fake"):
        if card.get("project_context_hash") != context_hash:
            card["project_context_hash"] = context_hash
            card["card_hash"] = hash_payload({key: value for key, value in card.items() if key != "card_hash"})
            _write(path, card)
        return card if _validate_reusable_card(card, analysis_input) else None
    return None


def _reuse_identity(analysis_input: dict[str, Any], context_hash: str, provider: DeepSeekContentIntelligenceProvider) -> str:
    return hash_payload({
        "input_hash": analysis_input["input_hash"],
        "evidence_hash": hash_payload(analysis_input["evidence"]),
        "context_hash": context_hash,
        "provider_id": provider.provider_id,
        "provider_version": provider.provider_version,
        "model_id": provider.model_id,
        "configuration": provider.configuration,
        "prompt_version": PROMPT_VERSION,
        "output_schema_version": OUTPUT_SCHEMA_VERSION,
    })


def _validate_reusable_card(card: dict[str, Any], analysis_input: dict[str, Any]) -> bool:
    if card.get("schema_version") != "0.1" or card.get("status") not in {AnalysisStatus.COMPLETED, AnalysisStatus.DEGRADED}:
        return False
    if card.get("candidate_identity") != analysis_input["candidate_identity"]:
        return False
    if card.get("card_hash") != hash_payload({key: value for key, value in card.items() if key != "card_hash"}):
        return False
    allowed_refs = {item["ref_id"] for item in analysis_input["evidence_index"]}
    claims = card.get("claims")
    if not isinstance(claims, list) or not claims:
        return False
    for claim in claims:
        if claim.get("claim_type") == "FACT" and claim.get("producer") != "deterministic_input_builder":
            return False
        refs = claim.get("evidence_refs")
        if not isinstance(refs, list) or any(ref not in allowed_refs for ref in refs):
            return False
    return card.get("evidence_index") == analysis_input["evidence_index"] and card.get("missing_evidence") == analysis_input["missing_evidence"]


def _without_reasoning_content(raw: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    sanitized = json.loads(json.dumps(raw))
    present = False
    characters = 0
    for choice in sanitized.get("choices", []):
        message = choice.get("message", {})
        reasoning = message.pop("reasoning_content", None)
        if reasoning is not None:
            present = True
            characters += len(str(reasoning))
    return sanitized, {"reasoning_content_present": present, "reasoning_content_characters": characters}
def _claim_counts(card: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for claim in card["claims"]: counts[str(claim["claim_type"])] = counts.get(str(claim["claim_type"]), 0) + 1
    return counts
