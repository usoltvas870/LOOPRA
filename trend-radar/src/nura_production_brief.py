"""Deterministic, offline NURA Production Brief contract.

This module is intentionally downstream from finalized human editorial review.
It neither invokes providers nor produces scripts or production assets.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1"
BUILDER_VERSION = "0.1"
RENDERER_VERSION = "0.2"
MAX_CANDIDATES = 5
MAX_TEXT_CHARS = 2_000
READY_FOR_SCRIPT_CONTRACT = "READY_FOR_SCRIPT_CONTRACT"
READY_WITH_HUMAN_REVISIONS = "READY_WITH_HUMAN_REVISIONS"
BLOCKED_UNRESOLVED_REVIEW = "BLOCKED_UNRESOLVED_REVIEW"
BLOCKED_STALE_HUMAN_REVISION = "BLOCKED_STALE_HUMAN_REVISION"
BLOCKED_INVALID_SOURCE = "BLOCKED_INVALID_SOURCE"


class NuraProductionBriefError(ValueError):
    """A source, validation, or persistence error in the brief boundary."""


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def hash_payload(value: Any) -> str:
    return hashlib.sha256((_json(value) if not isinstance(value, str) else value).encode("utf-8")).hexdigest()


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise NuraProductionBriefError(f"INVALID_SOURCE_JSON:{path.name}") from error
    if not isinstance(value, dict):
        raise NuraProductionBriefError("SOURCE_JSON_OBJECT_REQUIRED")
    return value


def _portable(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError as error:
        raise NuraProductionBriefError("PATH_OUTSIDE_ALLOWED_ROOT") from error


def _safe_text(value: Any, *, limit: int = MAX_TEXT_CHARS) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise NuraProductionBriefError("UNSAFE_OR_EMPTY_TEXT")
    result = value.strip()
    if re.search(r"<[^>]+>|[A-Za-z]:[\\/]", result, re.I):
        raise NuraProductionBriefError("UNSAFE_OR_EMPTY_TEXT")
    return result


def _bounded(value: Any) -> Any:
    if isinstance(value, str):
        return _safe_text(value)
    if isinstance(value, list):
        if len(value) > 20:
            raise NuraProductionBriefError("UNBOUNDED_SOURCE_VALUE")
        return [_bounded(item) for item in value]
    if value is None:
        return None
    raise NuraProductionBriefError("UNSUPPORTED_SOURCE_VALUE")


def _atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise NuraProductionBriefError("CONFLICTING_BRIEF_ARTIFACT")
        return
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as temporary:
        temporary.write(text)
        temporary_path = Path(temporary.name)
    try:
        os.link(temporary_path, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text:
            raise NuraProductionBriefError("CONFLICTING_BRIEF_ARTIFACT")
    finally:
        temporary_path.unlink(missing_ok=True)


def load_finalized_review(review_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load only a finalized, owner-confirmed review and validate its manifest."""
    result = _read(review_root / "review_result.json")
    manifest = _read(review_root / "review_manifest.json")
    if result.get("schema_version") != "0.1" or result.get("final_status") != "COMPLETED":
        raise NuraProductionBriefError("FINALIZED_REVIEW_REQUIRED")
    if manifest.get("review_id") != review_root.name:
        raise NuraProductionBriefError("FINALIZED_REVIEW_DIRECTORY_ID_MISMATCH")
    if manifest.get("finalization_identity") != result.get("finalization_identity"):
        raise NuraProductionBriefError("REVIEW_FINALIZATION_IDENTITY_MISMATCH")
    if manifest.get("review_result_sha256") != hash_payload(result):
        raise NuraProductionBriefError("REVIEW_HASH_MISMATCH")
    reviewer = result.get("reviewer", {})
    if reviewer.get("reviewer_id") != "nura-owner" or reviewer.get("reviewer_role") != "OWNER" or reviewer.get("human_confirmation") is not True:
        raise NuraProductionBriefError("OWNER_CONFIRMED_FINALIZED_REVIEW_REQUIRED")
    candidates = result.get("candidate_reviews")
    if not isinstance(candidates, list) or [item.get("original_rank") for item in candidates] != [1, 2, 3, 4, 5]:
        raise NuraProductionBriefError("INVALID_FINALIZED_REVIEW_SCOPE")
    ids = [item.get("candidate_identity", {}).get("video_id") for item in candidates]
    if len(set(ids)) != MAX_CANDIDATES or any(not item for item in ids):
        raise NuraProductionBriefError("DUPLICATE_OR_MISSING_REVIEW_CANDIDATE")
    return result, manifest


def _load_manifest(path: Path) -> dict[str, Any]:
    manifest = _read(path)
    candidates = manifest.get("candidates")
    if not isinstance(candidates, list):
        raise NuraProductionBriefError("INVALID_CANONICAL_MANIFEST")
    expected_hash = manifest.get("manifest_hash")
    if not isinstance(expected_hash, str) or not expected_hash:
        raise NuraProductionBriefError("INVALID_CANONICAL_MANIFEST")
    return manifest


def _load_context(path: Path) -> tuple[dict[str, Any], str]:
    context = _read(path)
    if context.get("project_id") != "nura" or not context.get("context_version"):
        raise NuraProductionBriefError("INVALID_NURA_PROJECT_CONTEXT")
    return context, hash_payload(context)


def _candidate_source_values(card: dict[str, Any]) -> dict[str, Any]:
    adaptation = card.get("project_adaptation")
    if not isinstance(adaptation, dict):
        raise NuraProductionBriefError("INVALID_SOURCE_CARD_ADAPTATION")
    return {
        "source_mechanism": adaptation.get("source_mechanism"),
        "source_mechanism_preserved": adaptation.get("source_mechanism"),
        "adaptation_idea": adaptation.get("adaptation_idea"),
        "suggested_hook": adaptation.get("suggested_hook"),
        "production_elements_not_copied": adaptation.get("production_elements_not_copied"),
        "applied_constraints": adaptation.get("applied_constraints"),
    }


def _field_review(candidate: dict[str, Any], field: str) -> dict[str, Any] | None:
    items = [item for item in candidate.get("field_reviews", []) if item.get("field") == field]
    if len(items) > 1:
        raise NuraProductionBriefError("DUPLICATE_FIELD_REVIEW")
    return items[0] if items else None


def _provenance(*, field_name: str, value: Any, source_type: str, source_ref: str, source_hash: str,
                source_field_path: str, reviewer_id: str | None = None, human_verified: bool = False,
                claim_ids: list[str] | None = None, evidence_refs: list[str] | None = None,
                status: str = "RESOLVED", warnings: list[str] | None = None) -> dict[str, Any]:
    return {"field_name": field_name, "value": value, "source_type": source_type,
            "source_ref": source_ref, "source_hash": source_hash,
            "source_field_path": source_field_path, "reviewer_id": reviewer_id,
            "human_verified": human_verified, "source_claim_ids": claim_ids or [],
            "evidence_refs": evidence_refs or [], "status": status, "warnings": warnings or []}


def _resolve_field(*, candidate: dict[str, Any], card: dict[str, Any], field: str,
                   card_ref: str, card_hash: str, reviewer_id: str) -> dict[str, Any]:
    values = _candidate_source_values(card)
    value = values.get(field)
    review = _field_review(candidate, field)
    revision = next((item for item in candidate.get("human_revisions", []) if item.get("field_path") == field), None)
    if revision is not None:
        if review is None or review.get("status") != "EDIT_REQUIRED":
            raise NuraProductionBriefError("HUMAN_REVISION_WITHOUT_EDIT_REQUIRED_FIELD")
        if revision.get("reviewer_id") != reviewer_id or revision.get("human_verified") is not True or revision.get("revision_status") != "APPROVED_BY_OWNER":
            raise NuraProductionBriefError("INVALID_HUMAN_REVISION_REVIEWER_OR_STATUS")
        if not revision.get("revision_reason"):
            raise NuraProductionBriefError("HUMAN_REVISION_REASON_REQUIRED")
        if field not in values or hash_payload(value) != revision.get("source_value_hash"):
            raise NuraProductionBriefError("HUMAN_REVISION_STALE")
        if review.get("source_value_hash") != revision.get("source_value_hash"):
            raise NuraProductionBriefError("HUMAN_REVISION_FIELD_HASH_MISMATCH")
        allowed_claims = set(candidate.get("allowed_claim_ids", []))
        allowed_evidence = set(candidate.get("allowed_evidence_refs", []))
        if not set(revision.get("source_claim_ids", [])).issubset(allowed_claims):
            raise NuraProductionBriefError("UNKNOWN_REVISION_CLAIM_ID")
        reviewed_evidence_refs = revision.get("evidence_refs_reviewed", [])
        if not set(reviewed_evidence_refs).issubset(allowed_evidence):
            raise NuraProductionBriefError("UNKNOWN_REVISION_EVIDENCE_REF")
        return _provenance(field_name=field, value=_bounded(revision.get("revised_value")), source_type="HUMAN_REVISION",
            source_ref="review_result.json", source_hash=hash_payload(revision), source_field_path=f"candidate_reviews.rank_{candidate['original_rank']}.human_revisions.{field}",
            reviewer_id=reviewer_id, human_verified=True, claim_ids=revision.get("source_claim_ids", []),
            evidence_refs=reviewed_evidence_refs, warnings=[_safe_text(revision["revision_reason"])])
    if field == "source_mechanism_preserved" and review and review.get("status") == "ACCEPTED_WITH_NOTE" and review.get("human_note"):
        return _provenance(field_name=field, value=_bounded(review["human_note"]), source_type="HUMAN_APPROVED_DIRECTION",
            source_ref="review_result.json", source_hash=hash_payload(review), source_field_path=f"candidate_reviews.rank_{candidate['original_rank']}.field_reviews.{field}",
            reviewer_id=reviewer_id, human_verified=True, claim_ids=review.get("source_claim_ids", []), status="HUMAN_APPROVED_DIRECTION")
    if review and review.get("status") in {"ACCEPTED", "ACCEPTED_WITH_NOTE"} and value is not None:
        if review.get("source_value_hash") != hash_payload(value):
            raise NuraProductionBriefError("ACCEPTED_SOURCE_VALUE_HASH_MISMATCH")
        return _provenance(field_name=field, value=_bounded(value), source_type="HUMAN_ACCEPTED_AI_VALUE",
            source_ref=card_ref, source_hash=card_hash, source_field_path=f"project_adaptation.{field}", reviewer_id=reviewer_id,
            human_verified=True, claim_ids=review.get("source_claim_ids", []), status="HUMAN_ACCEPTED_AI_ORIGIN")
    reason = "NOT_TYPED" if field in {"hook_type", "production_complexity"} else "UNRESOLVED_UPSTREAM_FIELD"
    return _provenance(field_name=field, value=None, source_type=reason, source_ref="review_result.json", source_hash=hash_payload(candidate),
        source_field_path=field, status=reason, warnings=[reason])


def _validate_candidate(*, review_candidate: dict[str, Any], manifest_candidate: dict[str, Any], card: dict[str, Any], context_hash: str) -> None:
    identity = review_candidate.get("candidate_identity", {})
    if identity.get("video_id") != manifest_candidate.get("video_id") or review_candidate.get("original_rank") != manifest_candidate.get("rank"):
        raise NuraProductionBriefError("CANDIDATE_OR_RANK_MISMATCH")
    card_identity = card.get("candidate_identity", {})
    if card_identity.get("video_id") != identity.get("video_id") or card_identity.get("rank") != review_candidate.get("original_rank"):
        raise NuraProductionBriefError("SOURCE_CARD_CANDIDATE_MISMATCH")
    if card.get("project_context_hash") != context_hash:
        raise NuraProductionBriefError("PROJECT_CONTEXT_HASH_MISMATCH")
    provider = card.get("provider", {})
    if provider.get("provider_id") != "deepseek" or provider.get("model_id") != "deepseek-v4-flash" or provider.get("configuration", {}).get("prompt_version") != "2.0":
        raise NuraProductionBriefError("SOURCE_CARD_PROVIDER_CONTRACT_INVALID")
    card_hash = card.get("card_hash")
    if not isinstance(card_hash, str) or card_hash != hash_payload({key: value for key, value in card.items() if key != "card_hash"}):
        raise NuraProductionBriefError("SOURCE_CARD_HASH_INVALID")
    if review_candidate.get("source_card_hash") != card_hash:
        raise NuraProductionBriefError("SOURCE_CARD_HASH_MISMATCH")


def _markdown(brief: dict[str, Any]) -> str:
    fields = brief["fields"]
    def show(name: str) -> str:
        value = fields[name]["value"]
        return "Не определено в upstream-контракте." if value is None else ("; ".join(value) if isinstance(value, list) else value)
    lines = [f"# NURA Production Brief — Rank {brief['original_rank']}", "",
        f"Видео: `{brief['candidate_identity']['video_id']}`", "",
        "## Статус", "", f"- Human review: `COMPLETED`", f"- Решение: `{brief['human_editorial_decision']}`",
        f"- Eligibility: `{brief['eligibility']}`", f"- Readiness: `{brief['readiness']}`", "",
        "## Что подтверждено человеком", "", "Исходная Content Intelligence card была AI-generated. Этот brief использует только human-approved направление; исходный rank сохранён.", "",
        "## Source mechanism", "", show("source_mechanism_preserved"), "", "## NURA adaptation direction", "", show("adaptation_idea"), "",
        "## Suggested hook", "", show("suggested_hook"), "", "## Format direction", "", show("inferred_source_format"), "",
        "## Required high-level production elements", "", show("source_mechanism_preserved"), "", "## What must not be copied", "", show("production_elements_not_copied"), "",
        "## Safety constraints", ""]
    lines.extend(f"- {item}" for item in brief["safety_constraints"])
    lines += ["", "## Evidence limitations", ""]
    lines.extend(f"- {item}" for item in brief["evidence_limitations"])
    lines += ["", "## Human revisions applied", ""]
    revisions = [value for value in fields.values() if value["source_type"] == "HUMAN_REVISION"]
    lines.extend(f"- `{item['field_name']}`: human revision applied." for item in revisions) or lines.append("- Нет: использованы human-accepted AI-values.")
    lines += ["", "## Unresolved fields", ""]
    lines.extend(f"- `{item['field_name']}`: `{item['status']}`." for item in brief["unresolved_fields"])
    lines += ["", "## Provenance summary", "", "AI origin сохранён в provenance; human acceptance и human revisions обозначены отдельно.", "",
        "## Что этот brief не содержит", "", "Этот документ не содержит сценарий, готовые реплики, покадровый план, assets, музыку, монтажный план или publishing metadata.", ""]
    return "\n".join(lines)


def _brief(*, review: dict[str, Any], review_candidate: dict[str, Any], manifest_candidate: dict[str, Any], card: dict[str, Any],
           card_ref: str, context: dict[str, Any], context_hash: str, manifest: dict[str, Any]) -> dict[str, Any]:
    decision, eligibility = review_candidate.get("overall_decision"), review_candidate.get("production_brief_eligibility")
    if decision == "APPROVED_FOR_PRODUCTION_BRIEF" and eligibility == "ELIGIBLE": readiness = READY_FOR_SCRIPT_CONTRACT
    elif decision == "APPROVED_WITH_EDITORIAL_EDITS" and eligibility == "ELIGIBLE_WITH_HUMAN_REVISIONS": readiness = READY_WITH_HUMAN_REVISIONS
    else: raise NuraProductionBriefError("CANDIDATE_NOT_ELIGIBLE_FOR_PRODUCTION_BRIEF")
    card_hash = card["card_hash"]
    reviewer_id = review["reviewer"]["reviewer_id"]
    fields = {name: _resolve_field(candidate=review_candidate, card=card, field=name, card_ref=card_ref, card_hash=card_hash, reviewer_id=reviewer_id)
              for name in ("source_mechanism", "source_mechanism_preserved", "adaptation_idea", "suggested_hook", "production_elements_not_copied", "applied_constraints")}
    fields["inferred_source_format"] = _provenance(field_name="inferred_source_format", value=None, source_type="UNRESOLVED", source_ref="review_result.json", source_hash=hash_payload(review_candidate), source_field_path="inferred_source_format", status="UNRESOLVED", warnings=["FORMAT_SUMMARY_IS_NOT_A_TYPED_SOURCE_CARD_FIELD"])
    for name in ("hook_type", "production_complexity", "suggested_nura_format", "core_message", "narrative_direction", "exact_duration", "exact_asset_list", "exact_cta"):
        fields[name] = _provenance(field_name=name, value=None, source_type="NOT_TYPED" if name in {"hook_type", "production_complexity"} else "UNRESOLVED", source_ref="review_result.json", source_hash=hash_payload(review_candidate), source_field_path=name, status="NOT_TYPED" if name in {"hook_type", "production_complexity"} else "UNRESOLVED", warnings=["NO_SEMANTIC_COMPLETION"])
    unresolved = [item for item in fields.values() if item["value"] is None]
    warnings = [_safe_text(item, limit=MAX_TEXT_CHARS) for item in card.get("warnings", [])[:10] if isinstance(item, str)]
    brief = {"schema_version": SCHEMA_VERSION, "brief_kind": "nura_production_brief", "project_identity": {"project_id": context["project_id"], "context_version": context["context_version"], "context_hash": context_hash},
        "radar_run_id": manifest.get("radar_run_id"), "manifest_identity": {"manifest_hash": manifest["manifest_hash"], "manifest_ref": "selection_manifest.json"},
        "candidate_identity": {"video_id": manifest_candidate["video_id"], "author": review_candidate["candidate_identity"].get("author"), "source_platform": review_candidate["candidate_identity"].get("source_platform")},
        "original_rank": review_candidate["original_rank"], "source_review": {"review_id": review["review_id"], "review_hash": review["review_hash"], "ref": "review_result.json"},
        "source_card": {"ref": card_ref, "card_hash": card_hash, "provider": {key: card["provider"].get(key) for key in ("provider_id", "model_id", "provider_version")}},
        "human_editorial_decision": decision, "eligibility": eligibility, "fields": fields,
        "safety_constraints": _bounded(context.get("safety_constraints", [])) + _bounded(context.get("production_constraints", [])),
        "evidence_limitations": warnings, "unresolved_fields": unresolved, "readiness": readiness,
        "final_status": "COMPLETED", "warnings": warnings, "errors": []}
    identity = {"review_hash": review["review_hash"], "card_hash": card_hash, "rank": brief["original_rank"], "schema": SCHEMA_VERSION, "builder": BUILDER_VERSION, "renderer": RENDERER_VERSION}
    brief["brief_id"] = f"nura-production-brief-{hash_payload(identity)[:12]}"
    brief["brief_hash"] = hash_payload(brief)
    return brief


def _validate_existing(root: Path, run: dict[str, Any]) -> bool:
    try:
        if _read(root / "brief_run.json").get("run_hash") != run.get("run_hash"): return False
        if _read(root / "brief_manifest.json").get("run_hash") != run.get("run_hash"): return False
        if not (root / "brief_index.md").is_file(): return False
        for item in run["candidates"]:
            candidate_root = root / "candidates" / item["video_id"]
            brief = _read(candidate_root / "production_brief.json")
            if brief.get("brief_hash") != hash_payload({key: value for key, value in brief.items() if key != "brief_hash"}): return False
            if not (candidate_root / "production_brief.md").is_file(): return False
        return True
    except NuraProductionBriefError:
        return False


def build_production_briefs(*, finalized_review_root: Path, manifest_path: Path, source_cards_root: Path,
                            project_context_path: Path, output_root: Path, ranks: tuple[int, ...] = (1, 2, 3, 4, 5), reuse: bool = True) -> dict[str, Any]:
    """Build five or fewer candidate-scoped briefs in canonical manifest order."""
    if not ranks or len(ranks) > MAX_CANDIDATES or any(rank not in {1, 2, 3, 4, 5} for rank in ranks) or len(set(ranks)) != len(ranks):
        raise NuraProductionBriefError("STAGE_5I_RANK_SCOPE_INVALID")
    review, _ = load_finalized_review(finalized_review_root)
    manifest, context = _load_manifest(manifest_path), None
    context, context_hash = _load_context(project_context_path)
    manifest_by_rank = {item.get("rank"): item for item in manifest["candidates"]}
    review_by_rank = {item["original_rank"]: item for item in review["candidate_reviews"]}
    selected = []
    for rank in sorted(ranks):
        if rank not in manifest_by_rank or rank not in review_by_rank: raise NuraProductionBriefError("MISSING_CANONICAL_CANDIDATE")
        candidate = review_by_rank[rank]; video_id = candidate["candidate_identity"]["video_id"]
        card_path = (source_cards_root / video_id / "content_intelligence_card.json").resolve()
        if source_cards_root.resolve() not in card_path.parents or not card_path.is_file(): raise NuraProductionBriefError("SOURCE_CARD_NOT_FOUND")
        card = _read(card_path); _validate_candidate(review_candidate=candidate, manifest_candidate=manifest_by_rank[rank], card=card, context_hash=context_hash)
        selected.append(_brief(review=review, review_candidate=candidate, manifest_candidate=manifest_by_rank[rank], card=card,
            card_ref=_portable(card_path, source_cards_root), context=context, context_hash=context_hash, manifest=manifest))
    identity = {"review_hash": review["review_hash"], "manifest_hash": manifest["manifest_hash"], "context_hash": context_hash,
        "candidates": [{"rank": item["original_rank"], "video_id": item["candidate_identity"]["video_id"], "brief_hash": item["brief_hash"]} for item in selected],
        "schema": SCHEMA_VERSION, "builder": BUILDER_VERSION, "renderer": RENDERER_VERSION}
    run_id = f"nura-production-briefs-{hash_payload(identity)[:12]}"; root = output_root / run_id
    readiness = Counter(item["readiness"] for item in selected)
    run = {"schema_version": SCHEMA_VERSION, "run_id": run_id, "project_id": "nura", "radar_run_id": manifest.get("radar_run_id"), "manifest_hash": manifest["manifest_hash"],
        "source_review": {"review_id": review["review_id"], "review_hash": review["review_hash"]}, "candidates": [{"rank": item["original_rank"], "video_id": item["candidate_identity"]["video_id"], "brief_ref": f"candidates/{item['candidate_identity']['video_id']}/production_brief.json", "brief_hash": item["brief_hash"], "readiness": item["readiness"]} for item in selected],
        "readiness_counts": dict(sorted(readiness.items())), "unresolved_field_count": sum(len(item["unresolved_fields"]) for item in selected), "final_status": "COMPLETED", "provider_calls": 0, "network_calls": 0, "ai_calls": 0, "scripts_generated": 0}
    run["run_hash"] = hash_payload(run)
    if reuse and root.exists() and _validate_existing(root, run): return run | {"status": "REUSED", "output_root": str(root)}
    index = ["# NURA Production Brief Index", "", "Original ranking is immutable; this index does not select a winner.", "", "| Rank | Video ID | Decision | Revisions | Eligibility | Readiness | Hook | Unresolved | Brief |", "| --- | --- | --- | ---: | --- | --- | --- | ---: | --- |"]
    for item in selected:
        hook = item["fields"]["suggested_hook"]["value"] or "UNRESOLVED"
        revisions = sum(field["source_type"] == "HUMAN_REVISION" for field in item["fields"].values())
        index.append(f"| {item['original_rank']} | {item['candidate_identity']['video_id']} | {item['human_editorial_decision']} | {revisions} | {item['eligibility']} | {item['readiness']} | {hook[:160]} | {len(item['unresolved_fields'])} | candidates/{item['candidate_identity']['video_id']}/production_brief.md |")
    index_text = "\n".join(index) + "\n"
    manifest_payload = {"schema_version": SCHEMA_VERSION, "run_id": run_id, "run_hash": run["run_hash"], "brief_run_sha256": hash_payload(run), "brief_index_sha256": hash_payload(index_text), "briefs": run["candidates"]}
    for item in selected:
        candidate_root = root / "candidates" / item["candidate_identity"]["video_id"]
        _atomic(candidate_root / "production_brief.json", _json(item)); _atomic(candidate_root / "production_brief.md", _markdown(item))
    _atomic(root / "brief_run.json", _json(run)); _atomic(root / "brief_manifest.json", _json(manifest_payload)); _atomic(root / "brief_index.md", index_text)
    return run | {"status": "COMPLETED", "output_root": str(root)}
