"""Offline Stage 5J NURA script contract; no real provider or episode bridge."""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Protocol

from nura_production_brief import hash_payload

SCHEMA_VERSION = "0.1"
SCRIPT_FORMATS = frozenset({"TALKING_GUIDE", "BACKGROUND_VOICE", "TEXT_LED_VIDEO", "DIALOGUE_COMIC"})
REVIEW_DECISIONS = frozenset({"APPROVED_FOR_EPISODE_BRIDGE", "APPROVED_WITH_REQUIRED_REVISIONS", "REJECTED", "NEEDS_FURTHER_REVIEW"})


class NuraScriptContractError(ValueError):
    pass


class ScriptProvider(Protocol):
    def generate(self, package: dict[str, Any]) -> dict[str, Any]: ...


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise NuraScriptContractError("INVALID_JSON") from error
    if not isinstance(value, dict):
        raise NuraScriptContractError("JSON_OBJECT_REQUIRED")
    return value


def load_editorial_profile(path: Path) -> dict[str, Any]:
    profile = _read(path)
    required = {"schema_version", "profile_id", "profile_version", "project_id", "source_document", "supported_content_scope", "excluded_scope", "voice_principles", "prohibited_voice_patterns", "safety_principles", "format_principles", "checklist_version"}
    if profile.get("schema_version") != SCHEMA_VERSION or profile.get("project_id") != "nura" or not required.issubset(profile):
        raise NuraScriptContractError("INVALID_EDITORIAL_PROFILE")
    source = profile["source_document"]
    if not isinstance(source, dict) or not re.fullmatch(r"[0-9a-f]{64}", str(source.get("sha256", ""))):
        raise NuraScriptContractError("INVALID_EDITORIAL_PROFILE_SOURCE")
    profile["profile_hash"] = hash_payload(profile)
    return profile


def build_script_input(*, brief: dict[str, Any], profile: dict[str, Any], requested_format: str, language: str = "ru") -> dict[str, Any]:
    if requested_format not in SCRIPT_FORMATS or requested_format.lower() not in profile["supported_content_scope"]:
        raise NuraScriptContractError("UNSUPPORTED_SCRIPT_FORMAT")
    if brief.get("final_status") != "COMPLETED" or brief.get("readiness") not in {"READY_FOR_SCRIPT_CONTRACT", "READY_WITH_HUMAN_REVISIONS"}:
        raise NuraScriptContractError("VALIDATED_PRODUCTION_BRIEF_REQUIRED")
    fields = brief.get("fields", {})
    required = ("source_mechanism_preserved", "suggested_hook", "production_elements_not_copied")
    if any(name not in fields for name in required):
        raise NuraScriptContractError("BRIEF_FIELDS_MISSING")
    payload = {
        "schema_version": SCHEMA_VERSION, "package_kind": "nura_script_input", "candidate_identity": brief["candidate_identity"],
        "original_rank": brief["original_rank"], "production_brief": {"brief_id": brief["brief_id"], "brief_hash": brief["brief_hash"]},
        "finalized_human_review": brief["source_review"], "project_context": brief["project_identity"],
        "editorial_profile": {key: profile[key] for key in ("profile_id", "profile_version", "profile_hash")},
        "requested_format": requested_format, "language": language,
        "approved_mechanism": fields["source_mechanism_preserved"], "approved_hook": fields["suggested_hook"],
        "mandatory_human_revisions": [value for value in fields.values() if value.get("source_type") == "HUMAN_REVISION"],
        "prohibited_copying_elements": fields["production_elements_not_copied"], "evidence_limitations": brief.get("evidence_limitations", []),
        "safety_constraints": brief.get("safety_constraints", []), "unresolved_fields": brief.get("unresolved_fields", []),
        "format_constraints": profile["format_principles"][requested_format.lower()], "builder_version": SCHEMA_VERSION,
    }
    payload["package_id"] = "nura-script-input-" + hash_payload(payload)[:12]
    payload["content_hash"] = hash_payload(payload)
    return payload


def _text(output: dict[str, Any]) -> str:
    return json.dumps(output.get("payload", {}), ensure_ascii=False).lower()


def validate_script_output(package: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if output.get("script_input_hash") != package.get("content_hash"): errors.append("SCRIPT_INPUT_HASH_MISMATCH")
    if output.get("candidate_identity") != package.get("candidate_identity"): errors.append("CANDIDATE_IDENTITY_MISMATCH")
    if output.get("original_rank") != package.get("original_rank"): errors.append("ORIGINAL_RANK_MISMATCH")
    if output.get("format") != package.get("requested_format"): errors.append("UNSUPPORTED_OR_MISMATCHED_FORMAT")
    if output.get("provenance", {}).get("brief_hash") != package["production_brief"]["brief_hash"]: errors.append("UNKNOWN_OR_INVALID_PROVENANCE")
    text = _text(output)
    for forbidden, code in ((package["approved_mechanism"].get("value"), "HUMAN_APPROVED_MECHANISM_CHANGED"), (package["approved_hook"].get("value"), "APPROVED_HOOK_CHANGED")):
        if forbidden and forbidden.lower() not in text: errors.append(code)
    for item in package["mandatory_human_revisions"]:
        if item.get("value") and item["value"].lower() not in text: errors.append("MANDATORY_HUMAN_REVISION_IGNORED")
    prohibited = package["prohibited_copying_elements"].get("value", "")
    if prohibited and prohibited.lower() in text: errors.append("PROHIBITED_COPYING_ELEMENT_RETURNED")
    patterns = ((r"диагноз|депресси", "MEDICAL_OR_DIAGNOSIS_CLAIM"), (r"гарантир|точно получится", "GUARANTEED_OUTCOME_OR_PREDICTION"), (r"исследовани|статистик|ученые доказали", "INVENTED_FACTUAL_CLAIM"), (r"я пережила|я чувствую", "NURA_PERSONAL_EXPERIENCE_CLAIM"), (r"в стиле автора|как автор", "AUTHOR_IMITATION"))
    errors.extend(code for pattern, code in patterns if re.search(pattern, text))
    payload = output.get("payload", {})
    if output.get("format") == "DIALOGUE_COMIC" and len(payload.get("frames", [])) != 9: errors.append("INVALID_FORMAT_STRUCTURE")
    warnings = []
    for pattern, code in ((r"это нормально", "EMPTY_VALIDATION"), (r"ресурс|трансформац", "COACHING_JARGON"), (r"\?[^?]*\?[^?]*\?", "EXCESSIVE_RHETORICAL_QUESTIONS"), (r"—.*—.*—", "EXCESSIVE_EM_DASH")):
        if re.search(pattern, text): warnings.append(code)
    return {"errors": errors, "warnings": warnings, "unresolved_checks": ["LEGAL_NON_IMITATION_REQUIRES_HUMAN_REVIEW", "SUBJECTIVE_EDITORIAL_QUALITY_REQUIRES_HUMAN_REVIEW"], "readiness": "DRAFT_AWAITING_HUMAN_REVIEW" if not errors else "BLOCKED"}


class DeterministicFakeScriptProvider:
    provider_id = "fake-nura-script"
    provider_version = "0.1"
    provider_mode = "OFFLINE_FAKE"
    def generate(self, package: dict[str, Any]) -> dict[str, Any]:
        text = "Синтетический текст: " + " ".join(filter(None, [package["approved_mechanism"].get("value"), package["approved_hook"].get("value"), *[x.get("value", "") for x in package["mandatory_human_revisions"]]]))
        fmt = package["requested_format"]
        payload: dict[str, Any] = {"text": text}
        if fmt == "DIALOGUE_COMIC": payload = {"frames": [{"speaker": "heroine" if index == 9 else "nura", "text": text} for index in range(1, 10)]}
        output = {"schema_version": SCHEMA_VERSION, "script_id": "fake-script-" + package["content_hash"][:12], "script_input_hash": package["content_hash"], "candidate_identity": package["candidate_identity"], "original_rank": package["original_rank"], "provider": {"provider_id": self.provider_id, "mode": self.provider_mode, "version": self.provider_version}, "editorial_profile": package["editorial_profile"], "format": fmt, "language": package["language"], "draft_status": "DRAFT_AWAITING_HUMAN_REVIEW", "payload": payload, "provenance": {"brief_hash": package["production_brief"]["brief_hash"]}}
        output["content_hash"] = hash_payload(output)
        output["validation"] = validate_script_output(package, output)
        return output


def create_human_script_review(output: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "review_kind": "nura_human_script_review", "script_id": output["script_id"], "script_hash": output["content_hash"], "decision": "NEEDS_FURTHER_REVIEW", "allowed_decisions": sorted(REVIEW_DECISIONS), "human_confirmation": False, "episode_bridge_ready": False, "required_revisions": [], "audit_trail": [{"event_type": "PACKAGE_CREATED", "actor_type": "SYSTEM"}]}


def persist_package(path: Path, value: dict[str, Any]) -> str:
    text = _json(value); path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text: raise NuraScriptContractError("CONFLICTING_ARTIFACT")
        return "REUSED"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as handle:
        handle.write(text); temporary = Path(handle.name)
    try: os.link(temporary, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text: raise NuraScriptContractError("CONFLICTING_ARTIFACT")
    finally: temporary.unlink(missing_ok=True)
    return "COMPLETED"
