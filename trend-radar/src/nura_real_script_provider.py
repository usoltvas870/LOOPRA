"""Bounded real NURA script provider; it stops before the Episode bridge."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import httpx

from content_intelligence import ContentIntelligenceError
from content_intelligence_provider import MODEL_ID, ProviderTransportError, post_deepseek_request
from nura_production_brief import hash_payload
from nura_script_contract import (
    NuraScriptContractError, build_script_input, load_editorial_profile,
    persist_package, validate_script_output,
)

PROVIDER_ID = "deepseek-nura-script"
PROVIDER_VERSION = "1.0"
PROMPT_ID = "nura-script-generation"
PROMPT_VERSION = "1.3"
OUTPUT_SCHEMA_VERSION = "1.0"
PARSER_VERSION = "1.1"
VALIDATOR_VERSION = "1.1"
TRACEABILITY_RESOLUTION_VERSION = "1.0"
HUMAN_REVIEW_FINALIZATION_VERSION = "1.0"
MAX_PAYLOAD_CHARS = 18_000
MAX_RESPONSE_BYTES = 256_000
MAX_RETRIES = 1


class NuraRealScriptProviderError(ValueError):
    pass


@dataclass(frozen=True)
class NuraScriptPromptContract:
    provider_id: str = PROVIDER_ID
    model_id: str = MODEL_ID
    prompt_id: str = PROMPT_ID
    prompt_version: str = PROMPT_VERSION
    temperature: float = 0.2
    max_output_tokens: int = 1400

    def system_contract(self) -> str:
        return "\n".join((
            "You generate one bounded Russian NURA draft, not advice, diagnosis, therapy, or an imitation.",
            "Return JSON only and follow the supplied output schema exactly.",
            "Authority order is immutable: finalized human revisions, validated brief facts, bounded editorial profile, then your creative choices.",
            "Do not override, paraphrase, move, or precede the approved hook. Do not greet the viewer.",
            "Make the mechanism visible as: support another person, defer the speaker's own exhaustion, then a small realistic shift without abandoning humanity.",
            "Keep the approved mechanism central. Music is secondary emotional support, never the main explanation.",
            "Do not use the prohibited copying element, source script, source author style, invented facts, citations, statistics, diagnoses, promises, or personal lived experience.",
            "Return advisory constraint_realization entries with existing block IDs and optional provider_note. Do not invent exact quotes: the application extracts canonical block text. Your note is not authoritative evidence and semantic fidelity remains for human review.",
            "Do not add identity, rank, hashes, provenance, or provider metadata; the trusted application attaches them.",
        ))

    def output_contract(self) -> dict[str, Any]:
        return {
            "schema_version": OUTPUT_SCHEMA_VERSION,
            "required": ["payload"],
            "payload": {
                "text": "Russian spoken text, begins exactly with approved_hook",
                "blocks": "ordered list of {kind: hook|development|turn|ending, text: string}",
            },
            "constraint_realization": "optional list of {constraint_id, block_ids, provider_note?, provider_claimed_spans?}; advisory only",
        }

    def messages(self, request: dict[str, Any]) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.system_contract()},
            {"role": "user", "content": json.dumps({"request": request, "output_contract": self.output_contract()}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))},
        ]


def build_bounded_provider_request(package: dict[str, Any]) -> dict[str, Any]:
    """Create the only provider-facing representation of a Script Input."""
    request = {
        "schema_version": "1.0",
        "script_input": {"package_id": package["package_id"], "content_hash": package["content_hash"]},
        "candidate": {"video_id": package["candidate_identity"]["video_id"], "rank": package["original_rank"]},
        "requested_format": package["requested_format"],
        "language": package["language"],
        "approved_mechanism": package["approved_mechanism"]["value"],
        "approved_hook": package["approved_hook"]["value"],
        "mandatory_human_revisions": [{"field_name": item.get("field_name", f"revision_{index}"), "value": item["value"]} for index, item in enumerate(package["mandatory_human_revisions"], 1) if item.get("value")],
        "prohibited_copying_elements": [package["prohibited_copying_elements"].get("value", "")],
        "evidence_limitations": package["evidence_limitations"],
        "safety_constraints": package["safety_constraints"],
        "editorial_profile": package["editorial_profile"],
        "editorial_principles": package["format_constraints"],
    }
    validate_bounded_provider_request(request)
    return request


def validate_bounded_provider_request(request: dict[str, Any]) -> None:
    encoded = json.dumps(request, ensure_ascii=False, sort_keys=True, allow_nan=False)
    if len(encoded) > MAX_PAYLOAD_CHARS:
        raise NuraRealScriptProviderError("INPUT_TOO_LARGE")
    lowered = encoded.lower()
    # Evidence limitations may name OCR or a transcript, but the request never
    # has fields that carry either corpus. Block private transport/path data.
    forbidden = ("c:\\", "/home/", "authorization", "api_key", "content_intelligence_report")
    if any(token in lowered for token in forbidden):
        raise NuraRealScriptProviderError("PROVIDER_PAYLOAD_FORBIDDEN_DATA")
    candidate = request.get("candidate", {})
    if not isinstance(candidate.get("rank"), int) or candidate["rank"] < 1 or not candidate.get("video_id") or request.get("requested_format") != "TALKING_GUIDE":
        raise NuraRealScriptProviderError("UNSUPPORTED_SCRIPT_SELECTION")


class DeepSeekNuraScriptProvider:
    """Script adapter over the shared DeepSeek HTTP transport, not a second client."""
    provider_id = PROVIDER_ID
    provider_version = PROVIDER_VERSION
    model_id = MODEL_ID

    def __init__(self, api_key: str | None = None, transport: httpx.BaseTransport | None = None) -> None:
        self._api_key = api_key if api_key is not None else os.environ.get("DEEPSEEK_API_KEY")
        self._transport = transport
        self.contract = NuraScriptPromptContract()

    @property
    def credentials_available(self) -> bool:
        return bool(self._api_key)

    def metadata(self) -> dict[str, Any]:
        return {"provider_id": self.provider_id, "provider_version": self.provider_version, "model_id": self.model_id,
                "prompt_id": PROMPT_ID, "prompt_version": PROMPT_VERSION,
                "configuration": {"response_format": {"type": "json_object"}, "thinking": {"type": "disabled"}, "temperature": self.contract.temperature, "max_tokens": self.contract.max_output_tokens}, "fake": False}

    def effective_request_identity(self, request: dict[str, Any]) -> str:
        body = self.build_request_body(request)
        return hash_payload({"bounded_input": request, "provider_id": self.provider_id, "model_id": self.model_id,
                             "prompt_id": self.contract.prompt_id, "prompt_version": self.contract.prompt_version,
                             "effective_prompt_content_hash": hash_payload(body["messages"]),
                             "requested_format": request["requested_format"],
                             "editorial_profile_hash": request["editorial_profile"]["profile_hash"],
                             "script_input_hash": request["script_input"]["content_hash"]})

    def build_request_body(self, request: dict[str, Any]) -> dict[str, Any]:
        validate_bounded_provider_request(request)
        return {"model": self.model_id, "messages": self.contract.messages(request), "response_format": {"type": "json_object"}, "thinking": {"type": "disabled"}, "temperature": self.contract.temperature, "max_tokens": self.contract.max_output_tokens}

    def generate(self, request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.credentials_available:
            raise NuraRealScriptProviderError("BLOCKED_PROVIDER_CREDENTIALS")
        body = self.build_request_body(request)
        response, latency_ms = post_deepseek_request(body, api_key=self._api_key, transport=self._transport)
        if len(response.content) > MAX_RESPONSE_BYTES:
            raise NuraRealScriptProviderError("PROVIDER_RESPONSE_TOO_LARGE")
        try:
            raw = response.json()
        except json.JSONDecodeError:
            raw = {"unparseable_response": response.text}
        return raw, {"http_status": response.status_code, "latency_ms": latency_ms, "request_id": response.headers.get("x-request-id"), "response_hash": sha256(response.content).hexdigest(), "usage": raw.get("usage") if isinstance(raw, dict) else None}


def _creative_payload(raw: dict[str, Any]) -> dict[str, Any]:
    try:
        content = raw["choices"][0]["message"]["content"]
        parsed = json.loads(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        raise NuraRealScriptProviderError("PROVIDER_MALFORMED_SCRIPT_JSON") from error
    if not isinstance(parsed, dict) or not isinstance(parsed.get("payload"), dict):
        raise NuraRealScriptProviderError("PROVIDER_SCHEMA_INVALID")
    return parsed


def _constraint_ids(package: dict[str, Any]) -> set[str]:
    return {"approved_mechanism", *{f"mandatory_revision:{item.get('field_name', f'revision_{index}') }" for index, item in enumerate(package["mandatory_human_revisions"], 1)}}


def _normalize_advisory_traceability(creative: dict[str, Any], package: dict[str, Any]) -> list[dict[str, Any]]:
    value = creative.get("constraint_realization")
    if value is None: return []
    entries: list[dict[str, Any]] = []
    if isinstance(value, list):
        entries = value
    elif isinstance(value, dict):  # Backward-compatible adapter for prompt 1.2.
        mechanism = value.get("approved_mechanism")
        if isinstance(mechanism, dict): entries.append({"constraint_id": "approved_mechanism", "block_ids": mechanism.get("block_ids", []), "provider_note": mechanism.get("application"), "provider_claimed_spans": mechanism.get("spans", [])})
        revisions = value.get("mandatory_human_revisions", {})
        if isinstance(revisions, dict):
            for field, item in revisions.items():
                if isinstance(item, dict): entries.append({"constraint_id": f"mandatory_revision:{field}", "block_ids": item.get("block_ids", []), "provider_note": item.get("application"), "provider_claimed_spans": item.get("spans", [])})
    else: raise NuraRealScriptProviderError("MALFORMED_ADVISORY_TRACEABILITY")
    if not all(isinstance(item, dict) for item in entries): raise NuraRealScriptProviderError("MALFORMED_ADVISORY_TRACEABILITY")
    return entries


def _resolve_constraint_evidence(payload: dict[str, Any], entries: list[dict[str, Any]], package: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    blocks = {item.get("kind"): item.get("text") for item in payload.get("blocks", []) if isinstance(item, dict)}
    known, seen, resolved, errors, warnings = _constraint_ids(package), set(), [], [], []
    for entry in entries:
        constraint_id, block_ids = entry.get("constraint_id"), entry.get("block_ids")
        if not isinstance(constraint_id, str) or constraint_id not in known: errors.append("UNKNOWN_CONSTRAINT_ID"); continue
        if constraint_id in seen: errors.append("DUPLICATE_CONSTRAINT_REFERENCE"); continue
        seen.add(constraint_id)
        if not isinstance(block_ids, list) or not block_ids or any(not isinstance(block_id, str) or block_id not in blocks for block_id in block_ids): errors.append("UNKNOWN_CONSTRAINT_BLOCK_ID"); continue
        spans = entry.get("provider_claimed_spans", [])
        if spans is None: spans = []
        if not isinstance(spans, list) or any(not isinstance(span, str) for span in spans): warnings.append("MALFORMED_PROVIDER_SPAN_ADVISORY"); spans = []
        referenced_text = "\n".join(blocks[block_id] for block_id in block_ids)
        invalid_spans = [span for span in spans if span not in referenced_text]
        if invalid_spans: warnings.append("NONAUTHORITATIVE_PROVIDER_SPAN_MISMATCH")
        resolved.append({"constraint_id": constraint_id, "resolved_block_ids": block_ids, "resolved_block_texts": [blocks[block_id] for block_id in block_ids], "resolution_status": "RESOLVED_FROM_CANONICAL_BLOCKS", "unresolved_human_check": True, "provider_note": entry.get("provider_note"), "provider_span_status": "MISMATCH" if invalid_spans else ("VERIFIED_ADVISORY" if spans else "NOT_PROVIDED"), "invalid_provider_spans": invalid_spans})
    return resolved, errors, warnings


def _validate_talking_guide(package: dict[str, Any], output: dict[str, Any], *, traceability_errors: list[str], traceability_warnings: list[str]) -> dict[str, Any]:
    result = validate_script_output(package, output)
    payload = output.get("payload", {})
    text = payload.get("text")
    blocks = payload.get("blocks")
    if not isinstance(text, str) or not text.strip() or not isinstance(blocks, list) or len(blocks) < 3:
        result["errors"].append("INVALID_TALKING_GUIDE_STRUCTURE")
    else:
        hook = package["approved_hook"].get("value", "")
        if not text.startswith(hook): result["errors"].append("APPROVED_HOOK_NOT_OPENING")
        if any(not isinstance(item, dict) or not isinstance(item.get("kind"), str) or not isinstance(item.get("text"), str) for item in blocks): result["errors"].append("INVALID_TALKING_GUIDE_BLOCKS")
        if re.search(r"\bламп\w*", text, re.I): result["errors"].append("PROHIBITED_LAMP_METAPHOR")
        if re.search(r"музык\w*.{0,40}(?:главн|объясня|смысл)", text, re.I): result["errors"].append("MUSIC_AS_PRIMARY_MEANING")
    result["errors"].extend(traceability_errors)
    result["warnings"].extend(traceability_warnings)
    text_lower = str(text or "").lower()
    editorial_patterns = (("музыка", "EDITORIAL_MUSIC_MAY_EXCEED_SECONDARY_CHANNEL"), ("не спасать никого, кроме себя", "EDITORIAL_CATEGORICAL_WITHDRAWAL_RISK"), ("внутри уже пусто", "EDITORIAL_DRAMATIC_OR_CLICHE_LANGUAGE"), ("отдаёшь последнее", "EDITORIAL_DRAMATIC_OR_CLICHE_LANGUAGE"), ("сама давно на нуле", "EDITORIAL_DRAMATIC_OR_CLICHE_LANGUAGE"))
    result["warnings"].extend(code for phrase, code in editorial_patterns if phrase in text_lower)
    result["errors"] = sorted(set(result["errors"]))
    result["readiness"] = "DRAFT_AWAITING_HUMAN_REVIEW" if not result["errors"] else "BLOCKED"
    return result


def _output(package: dict[str, Any], creative: dict[str, Any], provider_metadata: dict[str, Any]) -> dict[str, Any]:
    advisory = _normalize_advisory_traceability(creative, package)
    resolved, traceability_errors, traceability_warnings = _resolve_constraint_evidence(creative["payload"], advisory, package)
    output = {"schema_version": "0.1", "script_id": "real-script-" + package["content_hash"][:12], "script_input_hash": package["content_hash"], "candidate_identity": package["candidate_identity"], "original_rank": package["original_rank"], "provider": provider_metadata, "editorial_profile": package["editorial_profile"], "format": package["requested_format"], "language": package["language"], "draft_status": "DRAFT_AWAITING_HUMAN_REVIEW", "payload": creative["payload"], "provider_advisory_traceability": advisory, "resolved_constraint_evidence": resolved, "provenance": {"brief_hash": package["production_brief"]["brief_hash"]}}
    output["validation"] = _validate_talking_guide(package, output, traceability_errors=traceability_errors, traceability_warnings=traceability_warnings)
    output["content_hash"] = hash_payload({key: value for key, value in output.items() if key != "content_hash"})
    return output


def _review(output: dict[str, Any], package: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version": "0.1", "review_kind": "nura_human_script_review", "script_id": output["script_id"], "script_hash": output["content_hash"], "candidate_identity": output["candidate_identity"], "original_rank": output["original_rank"], "format": output["format"], "production_brief": package["production_brief"], "finalized_human_review": package["finalized_human_review"], "script_input": {"package_id": package["package_id"], "content_hash": package["content_hash"]}, "provider": output["provider"], "editorial_profile": package["editorial_profile"], "approved_hook": package["approved_hook"], "approved_mechanism": package["approved_mechanism"], "mandatory_human_revisions": package["mandatory_human_revisions"], "prohibited_copying_elements": package["prohibited_copying_elements"], "payload": output["payload"], "provider_advisory_traceability": output["provider_advisory_traceability"], "resolved_constraint_evidence": output["resolved_constraint_evidence"], "validation": output["validation"], "decision": "NEEDS_FURTHER_REVIEW", "allowed_decisions": ["APPROVED_FOR_EPISODE_BRIDGE", "APPROVED_WITH_REQUIRED_REVISIONS", "REJECTED", "NEEDS_FURTHER_REVIEW"], "human_confirmation": False, "episode_bridge_ready": False, "reviewer_form": {"reviewer_id": None, "reviewer_role": None, "decision": None, "required_revisions": []}}


def _reusable(path: Path, package: dict[str, Any]) -> dict[str, Any] | None:
    try: output = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return None
    if output.get("script_input_hash") != package.get("content_hash") or output.get("validation", {}).get("errors") or output.get("draft_status") != "DRAFT_AWAITING_HUMAN_REVIEW": return None
    expected = hash_payload({key: value for key, value in output.items() if key != "content_hash"})
    return output if output.get("content_hash") == expected else None


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise NuraRealScriptProviderError("INVALID_REVIEW_ARTIFACT") from error
    if not isinstance(value, dict): raise NuraRealScriptProviderError("INVALID_REVIEW_ARTIFACT")
    return value


def _human_text_payload(text: str, hook: str) -> dict[str, Any]:
    paragraphs = text.split("\n\n")
    if len(paragraphs) != 5 or paragraphs[0] != hook: raise NuraRealScriptProviderError("INVALID_HUMAN_APPROVED_TEXT")
    return {"text": text, "blocks": [
        {"kind": "hook", "text": paragraphs[0]},
        {"kind": "development", "text": paragraphs[1]},
        {"kind": "turn", "text": paragraphs[2]},
        {"kind": "ending", "text": paragraphs[3]},
        {"kind": "ending", "text": paragraphs[4]},
    ]}


def finalize_human_script_review(*, pending_path: Path, approved_text: str, revision_reasons: list[str],
                                 reviewer_id: str, reviewer_role: str, reviewer_display_name: str,
                                 decision: str = "APPROVED_FOR_EPISODE_BRIDGE") -> dict[str, Any]:
    """Persist an owner-confirmed immutable final script without any provider call."""
    pending = _read_json(pending_path)
    root = pending_path.parent
    provider_output = _read_json(root / "validated_script_output.json")
    if pending.get("decision") != "NEEDS_FURTHER_REVIEW" or pending.get("human_confirmation") is not False or pending.get("episode_bridge_ready") is not False:
        raise NuraRealScriptProviderError("PENDING_REVIEW_NOT_FINALIZABLE")
    if pending.get("script_hash") != provider_output.get("content_hash") or pending.get("script_id") != provider_output.get("script_id"):
        raise NuraRealScriptProviderError("PENDING_REVIEW_IDENTITY_MISMATCH")
    if reviewer_id != "nura-owner" or reviewer_role != "OWNER" or decision != "APPROVED_FOR_EPISODE_BRIDGE" or not reviewer_display_name:
        raise NuraRealScriptProviderError("INVALID_HUMAN_REVIEWER_OR_DECISION")
    payload = _human_text_payload(approved_text, pending["approved_hook"]["value"])
    finalization_identity = hash_payload({"version": HUMAN_REVIEW_FINALIZATION_VERSION, "pending_review_hash": hash_payload(pending), "provider_output_hash": provider_output["content_hash"], "approved_text": approved_text, "revision_reasons": revision_reasons, "reviewer_id": reviewer_id, "reviewer_role": reviewer_role, "decision": decision})
    final_review_path, final_script_path = root / "finalized_human_script_review.json", root / "human_approved_script_output.json"
    if final_review_path.exists():
        existing = _read_json(final_review_path)
        if existing.get("finalization_identity") != finalization_identity: raise NuraRealScriptProviderError("CONFLICTING_HUMAN_FINALIZATION")
        final_script = _read_json(final_script_path)
        return {"status": "REUSED", "provider_call_performed": False, "network_calls": 0, "credentials_required": False, "finalized_review_path": str(final_review_path), "final_script_path": str(final_script_path), "finalized_review": existing, "final_script": final_script}
    raw_response_hash = _read_json(root / "raw_provider_response.json").get("metadata", {}).get("response_hash")
    if not isinstance(raw_response_hash, str): raise NuraRealScriptProviderError("PROVIDER_RAW_PROVENANCE_REQUIRED")
    final_script = {"schema_version": "0.1", "script_kind": "nura_human_approved_script", "script_id": "human-approved-script-" + finalization_identity[:12], "source_provider_script": {"script_id": provider_output["script_id"], "content_hash": provider_output["content_hash"], "raw_response_hash": raw_response_hash, "prompt_version": provider_output["provider"]["prompt_version"]}, "script_input_hash": provider_output["script_input_hash"], "candidate_identity": provider_output["candidate_identity"], "original_rank": provider_output["original_rank"], "format": provider_output["format"], "language": provider_output["language"], "provenance": provider_output["provenance"], "editorial_profile": provider_output["editorial_profile"], "payload": payload, "status": "HUMAN_APPROVED", "episode_bridge_ready": True, "human_revision_provenance": {"pending_review_hash": hash_payload(pending), "revision_reasons": revision_reasons, "reviewer_id": reviewer_id, "decision": decision}}
    package = {"content_hash": provider_output["script_input_hash"], "candidate_identity": provider_output["candidate_identity"], "original_rank": provider_output["original_rank"], "requested_format": provider_output["format"], "production_brief": provider_output["provenance"], "approved_hook": pending["approved_hook"], "prohibited_copying_elements": pending["prohibited_copying_elements"]}
    validation = _validate_talking_guide(package, {"script_input_hash": final_script["script_input_hash"], "candidate_identity": final_script["candidate_identity"], "original_rank": final_script["original_rank"], "format": final_script["format"], "provenance": final_script["provenance"], "payload": payload}, traceability_errors=[], traceability_warnings=[])
    if validation["errors"]: raise NuraRealScriptProviderError("HUMAN_APPROVED_SCRIPT_VALIDATION_FAILED:" + ",".join(validation["errors"]))
    final_script["validation"] = validation
    final_script["content_hash"] = hash_payload(final_script)
    review = {"schema_version": "0.1", "review_kind": "nura_finalized_human_script_review", "finalization_identity": finalization_identity, "pending_review_hash": hash_payload(pending), "provider_output_hash": provider_output["content_hash"], "final_script_id": final_script["script_id"], "final_script_hash": final_script["content_hash"], "reviewer": {"reviewer_id": reviewer_id, "reviewer_role": reviewer_role, "reviewer_display_name": reviewer_display_name, "human_confirmation": True}, "decision": decision, "final_status": "HUMAN_APPROVED", "episode_bridge_ready": True, "revision_reasons": revision_reasons, "reviewed_at": datetime.now(timezone.utc).isoformat(), "audit_trail": [{"event_type": "PROVIDER_DRAFT_PRESERVED", "provider_script_hash": provider_output["content_hash"]}, {"event_type": "HUMAN_REVISIONS_APPLIED", "actor_type": "HUMAN_OWNER"}, {"event_type": "HUMAN_SCRIPT_APPROVED_FOR_EPISODE_BRIDGE", "actor_type": "HUMAN_OWNER"}]}
    review["review_hash"] = hash_payload(review)
    persist_package(final_script_path, final_script)
    persist_package(final_review_path, review)
    return {"status": "COMPLETED", "provider_call_performed": False, "network_calls": 0, "credentials_required": False, "finalized_review_path": str(final_review_path), "final_script_path": str(final_script_path), "finalized_review": review, "final_script": final_script}


def reprocess_existing_raw(*, raw_path: Path, brief_path: Path, profile_path: Path, repository_root: Path) -> dict[str, Any]:
    """Process an existing provider response offline without altering that raw artifact."""
    raw_bytes = raw_path.read_bytes()
    raw_artifact_hash = sha256(raw_bytes).hexdigest()
    try:
        artifact = json.loads(raw_bytes)
        brief = json.loads(brief_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise NuraRealScriptProviderError("INVALID_OFFLINE_REPROCESSING_INPUT") from error
    if not isinstance(artifact.get("response"), dict) or artifact.get("metadata", {}).get("http_status") != 200:
        raise NuraRealScriptProviderError("UNSUPPORTED_RAW_ARTIFACT")
    profile = load_editorial_profile(profile_path, repository_root=repository_root)
    package = build_script_input(brief=brief, profile=profile, requested_format="TALKING_GUIDE")
    provider_metadata = artifact.get("provider", {})
    if provider_metadata.get("prompt_version") != "1.2": raise NuraRealScriptProviderError("ATTEMPT_3_PROMPT_VERSION_REQUIRED")
    creative = _creative_payload(artifact["response"])
    output = _output(package, creative, provider_metadata)
    output["offline_reprocessing"] = {"mode": "OFFLINE_EXISTING_RAW", "provider_call_performed": False, "current_network_calls": 0, "credentials_required": False, "original_http_status": 200, "original_prompt_version": provider_metadata["prompt_version"], "current_prompt_version_for_future_calls": PROMPT_VERSION, "original_raw_response_hash": artifact["metadata"].get("response_hash"), "raw_artifact_sha256": raw_artifact_hash, "legacy_request_hash": artifact.get("request_hash"), "effective_request_identity_status": "LEGACY_REQUEST_HASH_EXCLUDES_PROMPT_VERSION_AND_CONTENT", "parser_version": PARSER_VERSION, "validator_version": VALIDATOR_VERSION, "traceability_resolution_version": TRACEABILITY_RESOLUTION_VERSION}
    output["content_hash"] = hash_payload({key: value for key, value in output.items() if key != "content_hash"})
    root = raw_path.parent
    persist_package(root / "offline_reprocessing_report.json", {"raw_artifact_sha256": raw_artifact_hash, "original_raw_response_hash": artifact["metadata"].get("response_hash"), "provider_call_performed": False, "current_network_calls": 0, "credentials_required": False, "validation": output["validation"], "resolved_constraint_evidence": output["resolved_constraint_evidence"]})
    if output["validation"]["errors"]:
        raise NuraRealScriptProviderError("SCRIPT_OUTPUT_VALIDATION_FAILED:" + ",".join(output["validation"]["errors"]))
    validated_path = root / "validated_script_output.json"
    output_status = persist_package(validated_path, output)
    review = _review(output, package)
    review["offline_reprocessing"] = output["offline_reprocessing"]
    review_status = persist_package(root / "pending_human_script_review.json", review)
    return {"status": "REUSED" if output_status == review_status == "REUSED" else "COMPLETED", "provider_call_performed": False, "original_http_status": 200, "current_network_calls": 0, "credentials_required": False, "original_prompt_version": "1.2", "current_prompt_version_for_future_calls": PROMPT_VERSION, "raw_artifact_sha256": raw_artifact_hash, "raw_response_hash": artifact["metadata"].get("response_hash"), "legacy_request_hash": artifact.get("request_hash"), "creative_schema_status": "PASS", "hard_validation_status": output["validation"]["readiness"], "traceability_warning_count": len([item for item in output["validation"]["warnings"] if "PROVIDER_SPAN" in item]), "editorial_warning_count": len(output["validation"]["warnings"]), "unresolved_human_check_count": len(output["validation"]["unresolved_checks"]), "validated_output_status": output_status, "pending_review_status": review_status, "validated_output_path": str(validated_path), "review_path": str(root / "pending_human_script_review.json"), "episode_bridge_ready": False, "output": output}


def run_real_script_provider(*, brief_path: Path, profile_path: Path, repository_root: Path, output_root: Path,
                             requested_format: str = "TALKING_GUIDE", allow_network: bool = False,
                             reuse_only: bool = False, api_key: str | None = None,
                             transport: httpx.BaseTransport | None = None) -> dict[str, Any]:
    if requested_format != "TALKING_GUIDE": raise NuraRealScriptProviderError("UNSUPPORTED_SCRIPT_SELECTION")
    if reuse_only and allow_network: raise NuraRealScriptProviderError("REUSE_ONLY_FORBIDS_NETWORK")
    try: brief = json.loads(brief_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error: raise NuraRealScriptProviderError("INVALID_PRODUCTION_BRIEF") from error
    profile = load_editorial_profile(profile_path, repository_root=repository_root)
    package = build_script_input(brief=brief, profile=profile, requested_format=requested_format)
    request = build_bounded_provider_request(package)
    run_id = "nura-real-script-" + hash_payload({"script_input_hash": package["content_hash"], "provider": PROVIDER_ID, "model": MODEL_ID, "prompt": PROMPT_VERSION})[:12]
    root = output_root / run_id
    validated_path = root / "validated_script_output.json"
    existing = _reusable(validated_path, package)
    if existing:
        return {"status": "REUSED", "run_id": run_id, "network_calls": 0, "credentials_required": False, "script_input_hash": package["content_hash"], "validated_output_path": str(validated_path), "review_path": str(root / "pending_human_script_review.json"), "output": existing}
    if reuse_only: raise NuraRealScriptProviderError("REUSABLE_ARTIFACT_NOT_FOUND")
    if not allow_network: raise NuraRealScriptProviderError("REAL_PROVIDER_REQUIRES_ALLOW_NETWORK")
    provider = DeepSeekNuraScriptProvider(api_key=api_key, transport=transport)
    if not provider.credentials_available: raise NuraRealScriptProviderError("BLOCKED_PROVIDER_CREDENTIALS")
    persist_package(root / "script_input.json", package)
    legacy_request_hash, effective_request_identity = hash_payload(request), provider.effective_request_identity(request)
    persist_package(root / "provider_request.json", {"request": request, "request_hash": legacy_request_hash, "effective_request_identity": effective_request_identity, "provider": provider.metadata()})
    try:
        raw, metadata = provider.generate(request)
    except ProviderTransportError as error:
        raise NuraRealScriptProviderError(str(error)) from error
    persist_package(root / "raw_provider_response.json", {"provider": provider.metadata(), "request_hash": legacy_request_hash, "effective_request_identity": effective_request_identity, "metadata": metadata, "response": raw})
    creative = _creative_payload(raw)
    output = _output(package, creative, provider.metadata())
    persist_package(root / "validation_report.json", output["validation"])
    if output["validation"]["errors"]: raise NuraRealScriptProviderError("SCRIPT_OUTPUT_VALIDATION_FAILED:" + ",".join(output["validation"]["errors"]))
    persist_package(validated_path, output)
    review = _review(output, package)
    persist_package(root / "pending_human_script_review.json", review)
    return {"status": "COMPLETED", "run_id": run_id, "network_calls": 1, "credentials_required": True, "script_input_hash": package["content_hash"], "request_hash": legacy_request_hash, "effective_request_identity": effective_request_identity, "validated_output_path": str(validated_path), "review_path": str(root / "pending_human_script_review.json"), "output": output}
