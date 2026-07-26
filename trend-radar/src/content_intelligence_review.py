"""Offline human editorial review workflow for immutable CI reports."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

REVIEW_SCHEMA_VERSION = "0.1"
REVIEW_TEMPLATE_VERSION = "0.1"
REVIEW_RENDERER_VERSION = "0.1"
REVIEW_FINALIZER_VERSION = "0.1"
MAX_CANDIDATES = 5
MAX_NOTE_CHARS = 2_000
MAX_REVISION_CHARS = 2_000
DECISIONS = {"PENDING", "APPROVED_FOR_PRODUCTION_BRIEF", "APPROVED_WITH_EDITORIAL_EDITS", "NEEDS_EVIDENCE_REVIEW", "REJECTED_EDITORIALLY"}
DIMENSIONS = ("grounding", "candidate_specificity", "source_mechanism_clarity", "uncertainty_calibration", "nura_relevance", "actionability", "safety", "copyright_non_imitation", "overall_usefulness")
DIMENSION_DECISIONS = {"PENDING", "PASS", "PASS_WITH_NOTES", "FAIL", "NOT_APPLICABLE"}
FIELDS = ("source_mechanism", "hook", "core_message", "audience_pain", "emotional_trigger", "insight", "opening", "development", "ending_cta", "inferred_source_format", "adaptation_idea", "suggested_nura_format", "suggested_hook", "source_mechanism_preserved", "production_elements_not_copied", "applied_constraints", "warnings", "hook_type", "production_complexity")
FIELD_STATUSES = {"PENDING", "ACCEPTED", "ACCEPTED_WITH_NOTE", "EDIT_REQUIRED", "UNSUPPORTED_BY_EVIDENCE", "REJECTED", "NOT_APPLICABLE", "NOT_TYPED"}

class ContentIntelligenceReviewError(ValueError): pass

def _json(value: Any) -> str: return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
def _hash(value: Any) -> str: return hashlib.sha256((_json(value) if not isinstance(value, str) else value).encode("utf-8")).hexdigest()
def _portable(value: str) -> str: return value.replace("\\", "/")
def _atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text: raise ContentIntelligenceReviewError("CONFLICTING_REVIEW_ARTIFACT")
        return
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as f: f.write(text); temp=Path(f.name)
    try: os.link(temp, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text: raise ContentIntelligenceReviewError("CONFLICTING_REVIEW_ARTIFACT")
    finally: temp.unlink(missing_ok=True)
def _read(path: Path) -> dict[str, Any]:
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e: raise ContentIntelligenceReviewError("INVALID_JSON") from e
    if not isinstance(value, dict): raise ContentIntelligenceReviewError("JSON_OBJECT_REQUIRED")
    return value
def _safe_text(value: Any, limit: int=MAX_NOTE_CHARS) -> str:
    if not isinstance(value, str) or not value.strip() or len(value)>limit or re.search(r"<[^>]+>|<script|[A-Za-z]:[\\/]", value, re.I): raise ContentIntelligenceReviewError("UNSAFE_OR_EMPTY_HUMAN_TEXT")
    return value.strip()

def load_report(report_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    report, manifest = _read(report_root/"report.json"), _read(report_root/"report_manifest.json")
    if report.get("final_status") != "COMPLETED" or report.get("schema_version") != "0.1": raise ContentIntelligenceReviewError("INVALID_REPORT_STATUS")
    if report.get("report_identity") != manifest.get("report_identity") or manifest.get("report_json_sha256") != _hash(report): raise ContentIntelligenceReviewError("REPORT_HASH_MISMATCH")
    candidates=report.get("candidates", [])
    if len(candidates)!=MAX_CANDIDATES or [x.get("original_rank") for x in candidates] != [1,2,3,4,5]: raise ContentIntelligenceReviewError("STAGE_5H_RANK_SCOPE_INVALID")
    if any(x.get("provider_metadata",{}).get("prompt_version")!="2.0" or x.get("provider_metadata",{}).get("provider_id")!="deepseek" for x in candidates): raise ContentIntelligenceReviewError("SOURCE_CARD_CONTRACT_INVALID")
    return report, manifest

def _candidate(report_item: dict[str, Any]) -> dict[str, Any]:
    claims=report_item.get("claims", [])
    claim_ids=[x.get("claim_id") for x in claims]
    values={"source_mechanism": report_item.get("nura_adaptation",{}).get("source_mechanism"), "hook": report_item.get("hook_summary",{}).get("existing_hook_interpretation"), "core_message": report_item.get("meaning_summary",{}).get("core_message"), "audience_pain": report_item.get("meaning_summary",{}).get("audience_pain"), "emotional_trigger": report_item.get("meaning_summary",{}).get("emotional_trigger"), "insight": report_item.get("meaning_summary",{}).get("insight"), "opening": report_item.get("structure_summary",{}).get("opening"), "development": report_item.get("structure_summary",{}).get("development"), "ending_cta": report_item.get("structure_summary",{}).get("ending") or report_item.get("structure_summary",{}).get("cta"), "inferred_source_format": report_item.get("format_summary"), "adaptation_idea": report_item.get("nura_adaptation",{}).get("adaptation_idea"), "suggested_nura_format": None, "suggested_hook": report_item.get("nura_adaptation",{}).get("suggested_hook"), "source_mechanism_preserved": report_item.get("nura_adaptation",{}).get("source_mechanism"), "production_elements_not_copied": report_item.get("nura_adaptation",{}).get("production_elements_not_copied"), "applied_constraints": report_item.get("nura_adaptation",{}).get("applied_constraints"), "warnings": report_item.get("warnings", [])}
    fields=[]
    for field in FIELDS:
        source=values.get(field)
        fields.append({"field":field,"status":"NOT_TYPED" if field in {"hook_type","production_complexity"} else "PENDING","source_value_hash":None if source is None else _hash(source),"source_claim_ids":[x.get("claim_id") for x in claims if x.get("field") in {field, "mechanism" if field=="source_mechanism" else field}],"human_note":None})
    return {"candidate_identity":report_item["candidate_identity"],"original_rank":report_item["original_rank"],"source_card_ref":report_item["source_card_ref"],"source_card_hash":report_item["source_card_hash"],"source_report_entry_ref":f"candidates/rank-{report_item['original_rank']}","source_quality":{"evidence_quality":report_item.get("evidence_quality"),"warnings":report_item.get("warnings",[])},"overall_decision":"PENDING","dimension_reviews":[{"dimension":x,"decision":"PENDING","note":None,"related_claim_ids":[],"evidence_refs":[],"required_human_action":None} for x in DIMENSIONS],"field_reviews":fields,"claim_reviews":[],"evidence_review_actions":[],"human_revisions":[],"editorial_notes":None,"production_brief_eligibility":"BLOCKED_PENDING_HUMAN_REVIEW","reviewed_at":None,"reviewer_id":None,"final_status":"PENDING","allowed_claim_ids":claim_ids,"allowed_evidence_refs":sorted({r for x in claims for r in x.get("evidence_refs",[])})}

def create_review(*, report_root: Path, output_root: Path) -> dict[str, Any]:
    report, report_manifest=load_report(report_root)
    identity_input={"report_identity":report["report_identity"],"report_hash":report_manifest["report_json_sha256"],"report_schema":report["schema_version"],"report_builder":report["report_configuration"]["builder_version"],"ordered_candidates":[{"rank":x["original_rank"],"video_id":x["candidate_identity"]["video_id"],"card_hash":x["source_card_hash"]} for x in report["candidates"]],"project_context_hash":report["generated_from"]["project_context_hash"],"review_schema":REVIEW_SCHEMA_VERSION,"template":REVIEW_TEMPLATE_VERSION,"renderer":REVIEW_RENDERER_VERSION}
    identity=_hash(identity_input); review_id=f"human-editorial-review-{report['generated_from']['radar_run_id']}-{identity[:12]}"; root=output_root/review_id
    existing=root/"review_manifest.json"
    if existing.exists():
        m=_read(existing)
        if m.get("review_identity")==identity: return {"status":"REUSED","review_id":review_id,**_hashes(root)}
        raise ContentIntelligenceReviewError("CONFLICTING_REVIEW_IDENTITY")
    package={"schema_version":REVIEW_SCHEMA_VERSION,"review_id":review_id,"review_kind":"human_editorial_review","review_identity":identity,"source_report_identity":report["report_identity"],"source_report_ref":"report.json","source_report_hash":report_manifest["report_json_sha256"],"project_id":report["generated_from"]["project_id"],"radar_run_id":report["generated_from"]["radar_run_id"],"manifest_ref":report["generated_from"]["manifest_ref"],"manifest_hash":report["generated_from"]["manifest_hash"],"reviewer":{"reviewer_id":None,"reviewer_role":None,"reviewer_display_name":None,"review_started_at":None,"review_completed_at":None,"review_method":None,"human_confirmation":False},"review_configuration":{"template_version":REVIEW_TEMPLATE_VERSION,"renderer_version":REVIEW_RENDERER_VERSION,"ranking_policy":"canonical_manifest_order_immutable"},"candidate_reviews":[_candidate(x) for x in report["candidates"]],"review_summary":{"candidate_count":5,"approved_for_production_brief":0},"audit_trail":[{"event_type":"PACKAGE_CREATED","actor_type":"SYSTEM"},{"event_type":"TEMPLATE_GENERATED","actor_type":"SYSTEM"}],"created_at":None,"finalized_at":None,"final_status":"PENDING_HUMAN_REVIEW","warnings":["AI-generated source cards remain human_verified=false."],"errors":[]}
    package["review_hash"]=_hash(package)
    template={"schema_version":REVIEW_SCHEMA_VERSION,"review_id":review_id,"review_identity":identity,"reviewer":{"reviewer_id":None,"reviewer_role":None,"reviewer_display_name":None,"review_started_at":None,"review_completed_at":None,"review_method":None,"human_confirmation":False},"candidate_reviews":package["candidate_reviews"]}
    text=render_form(package); manifest={"schema_version":REVIEW_SCHEMA_VERSION,"review_id":review_id,"review_identity":identity,"review_package_sha256":_hash(package),"review_form_sha256":_hash(text),"decision_template_sha256":_hash(template),"source_report_hash":report_manifest["report_json_sha256"]}
    _atomic(root/"review_package.json",_json(package)); _atomic(root/"review_form.md",text); _atomic(root/"review_decisions.template.json",_json(template)); _atomic(root/"review_manifest.json",_json(manifest))
    return {"status":"COMPLETED","review_id":review_id,**_hashes(root),"candidate_count":5,"provider_calls":0,"network_calls":0}

def _hashes(root:Path)->dict[str,Any]:
    names=("review_package.json","review_form.md","review_decisions.template.json","review_manifest.json")
    result={}
    for name in names:
        path=root/name
        if path.exists(): result[name.replace(".json","").replace(".md","")+"_sha256"]=_hash(path.read_text(encoding="utf-8"))
    result["provider_calls"]=result["network_calls"]=0
    return result

def render_form(package:dict[str,Any])->str:
    lines=["# Форма редакционной проверки Content Intelligence","","AI-источники остаются AI-generated и `human_verified=false`. Эта форма не меняет ranking и не создаёт Production Brief.","","## Как заполнить","","Для каждого кандидата выберите одно решение, заполните обязательные оценки и при необходимости добавьте отдельные человеческие правки в JSON-template."]
    for c in package["candidate_reviews"]:
        lines += ["",f"## Rank {c['original_rank']} — `{c['candidate_identity']['video_id']}`","",f"Evidence quality: `{c['source_quality']['evidence_quality'].get('tier')}`. Warnings: {'; '.join(c['source_quality']['warnings'])}","","Решение: `PENDING` / `APPROVED_FOR_PRODUCTION_BRIEF` / `APPROVED_WITH_EDITORIAL_EDITS` / `NEEDS_EVIDENCE_REVIEW` / `REJECTED_EDITORIALLY`.","Проверьте grounding, релевантность NURA, безопасность и отсутствие имитации. Исходный rank неизменяем."]
    return "\n".join(lines)+"\n"

def validate_decisions(path:Path, *, require_completed:bool=False)->dict[str,Any]:
    data=_read(path); reviewer=data.get("reviewer",{}); candidates=data.get("candidate_reviews",[])
    if len(candidates)!=5 or [x.get("original_rank") for x in candidates] != [1,2,3,4,5]: raise ContentIntelligenceReviewError("INVALID_CANDIDATE_SCOPE")
    completed=all(x.get("overall_decision")!="PENDING" for x in candidates)
    if require_completed and (not completed or reviewer.get("reviewer_role") not in {"OWNER","EDITOR"} or not reviewer.get("reviewer_id") or reviewer.get("human_confirmation") is not True): raise ContentIntelligenceReviewError("COMPLETED_HUMAN_REVIEW_REQUIRED")
    for c in candidates:
        if c.get("overall_decision") not in DECISIONS: raise ContentIntelligenceReviewError("UNKNOWN_DECISION")
        if len({x.get('field') for x in c.get('field_reviews',[])}) != len(c.get('field_reviews',[])) or any(x.get('field') not in FIELDS or x.get('status') not in FIELD_STATUSES for x in c.get('field_reviews',[])): raise ContentIntelligenceReviewError("INVALID_FIELD_REVIEW")
        for revision in c.get("human_revisions",[]):
            if not revision.get("source_value_hash") or not revision.get("reviewer_id") or not revision.get("revision_reason"): raise ContentIntelligenceReviewError("INVALID_REVISION_PROVENANCE")
            _safe_text(revision.get("revised_value"),MAX_REVISION_CHARS); _safe_text(revision.get("revision_reason"))
    return {"status":"VALID","completed":completed,"candidate_count":5,"provider_calls":0,"network_calls":0}

def finalize_review(*, decision_path:Path, output_root:Path)->dict[str,Any]:
    validate_decisions(decision_path,require_completed=True); decision=_read(decision_path); identity=_hash({"decision":decision,"finalizer":REVIEW_FINALIZER_VERSION}); review_id=f"finalized-human-editorial-review-{identity[:12]}"; root=output_root/review_id
    if (root/"review_result.json").exists(): return {"status":"REUSED","review_id":review_id,**_hashes(root)}
    decision["final_status"]="COMPLETED"; decision["finalized_at"]=None; decision["finalization_identity"]=identity; decision["audit_trail"]=(decision.get("audit_trail",[])+[{"event_type":"REVIEW_VALIDATED","actor_type":"SYSTEM"},{"event_type":"REVIEW_FINALIZED","actor_type":"SYSTEM"}]); decision["review_hash"]=_hash(decision)
    summary="# Итог редакционной проверки\n\nHuman review завершён; исходные AI cards не изменялись.\n"; manifest={"review_id":review_id,"finalization_identity":identity,"review_result_sha256":_hash(decision),"review_summary_sha256":_hash(summary)}
    _atomic(root/"review_result.json",_json(decision)); _atomic(root/"review_summary.md",summary); _atomic(root/"review_manifest.json",_json(manifest)); return {"status":"COMPLETED","review_id":review_id,**_hashes(root)}
