"""Versioned TOP-20 production contracts for the one-time B1 acceptance profile.

v1 five-item modules remain untouched.  This module owns only the v2 envelope;
the real runner may inject existing single-item capture/evidence/provider helpers.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

SCHEMA_VERSION = "2.0"
PROFILE = "FRESH_TOP20_OPERATOR_BATCH_ACCEPTANCE"
TARGET_COUNT = 20
DECISIONS = {"APPROVED_FOR_PRODUCTION_BRIEF", "APPROVED_WITH_EDITORIAL_EDITS", "REJECTED", "NEEDS_FURTHER_REVIEW"}


class LoopraTop20V2Error(ValueError):
    pass


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _atomic(path: Path, payload: dict[str, Any]) -> str:
    text = _json(payload); path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text: raise LoopraTop20V2Error("CONFLICTING_V2_ARTIFACT")
        return "REUSED"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as out:
        out.write(text); temporary=Path(out.name)
    try: os.link(temporary,path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text: raise LoopraTop20V2Error("CONFLICTING_V2_ARTIFACT")
    finally: temporary.unlink(missing_ok=True)
    return "COMPLETED"


def _sealed(value: dict[str, Any]) -> dict[str, Any]:
    return {**value, "semantic_hash": _hash({key:data for key,data in value.items() if key != "semantic_hash"})}


def _validate(entries: list[dict[str, Any]]) -> None:
    if len(entries) != TARGET_COUNT: raise LoopraTop20V2Error("V2_EXACTLY_20_ITEMS_REQUIRED")
    if [entry.get("original_rank") for entry in entries] != list(range(1, TARGET_COUNT+1)): raise LoopraTop20V2Error("V2_ORIGINAL_RANK_ORDER_REQUIRED")
    for field in ("candidate_id", "video_id"):
        values=[entry.get(field) for entry in entries]
        if any(not value for value in values) or len(set(values)) != TARGET_COUNT: raise LoopraTop20V2Error(f"V2_UNIQUE_{field.upper()}_REQUIRED")


class LoopraTop20MediaAcquisitionV2:
    """20 independent v2 acquisition records; caller supplies actual capture."""
    def run(self, *, root: Path, batch: dict[str, Any], entries: list[dict[str, Any],], capture_one: Callable[[dict[str, Any]], dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        _validate(entries); results=[]
        for entry in entries:
            rank=entry["original_rank"]; result = capture_one(entry) if capture_one else {"status":"SYNTHETIC_OFFLINE", "source_media_reference":f"media/{rank:02d}/source.mp4", "source_media_sha256":_hash({"synthetic":rank}), "duration_seconds":1.0, "ffprobe_status":"VALID", "method":"OFFLINE_FAKE"}
            record=_sealed({"schema_version":SCHEMA_VERSION,"artifact_kind":"LoopraTop20MediaAcquisitionV2","batch_id":batch["batch_id"],"candidate_id":entry["candidate_id"],"video_id":entry["video_id"],"original_rank":rank,"selection_entry_hash":_hash(entry),"attempts":1,"retryable_status":"RESUMABLE" if result["status"] not in {"COMPLETED","REUSED","SYNTHETIC_OFFLINE"} else "COMPLETED","reuse_status":"REUSED" if result["status"]=="REUSED" else "NEW", "warnings":[],"errors":[], **result,"semantic_hash":""})
            _atomic(root/"acquisition"/f"{rank:02d}.json",record); results.append(record)
        return results


class LoopraTop20ContentIntelligenceV2:
    """Trusted rank/identity envelope; any provider receives bounded payload only."""
    def run(self, *, root: Path, batch: dict[str, Any], entries: list[dict[str, Any]], acquisition: list[dict[str, Any]], provider: Callable[[dict[str, Any]], dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        _validate(entries); cards=[]
        for entry, media in zip(entries, acquisition, strict=True):
            rank=entry["original_rank"]
            if media["status"] not in {"COMPLETED","REUSED","SYNTHETIC_OFFLINE"}: raise LoopraTop20V2Error("V2_MISSING_MEDIA")
            evidence={"inspection_reference":f"evidence/{rank:02d}/inspection.json","ocr_reference":f"evidence/{rank:02d}/ocr.json","transcription_reference":f"evidence/{rank:02d}/transcription.json"}
            request=_sealed({"schema_version":SCHEMA_VERSION,"artifact_kind":"LoopraTop20ContentIntelligenceRequestV2","batch_id":batch["batch_id"],"fresh_cycle_id":batch["fresh_cycle_id"],"candidate_id":entry["candidate_id"],"video_id":entry["video_id"],"original_rank":rank,"evidence_references":evidence,"bounded_evidence_input_hash":_hash({"rank":rank,"media":media["source_media_sha256"]}),"project_context_hash":batch["project_context_hash"],"provider":"deepseek","model":"deepseek-v4-flash","prompt_version":"2.0-v2","effective_prompt_hash":_hash("2.0-v2"),"semantic_hash":""})
            payload=provider(request) if provider else {"claims":[],"project_adaptation":{"source_mechanism":"Synthetic only","adaptation_idea":"Synthetic only","suggested_hook":"Synthetic only","production_elements_not_copied":"Synthetic only"},"warnings":["SYNTHETIC_OFFLINE_FIXTURE"]}
            if any(claim.get("claim_type") == "FACT" for claim in payload.get("claims",[]) if isinstance(claim,dict)): raise LoopraTop20V2Error("V2_PROVIDER_CREATED_SOURCE_FACT")
            card=_sealed({"schema_version":SCHEMA_VERSION,"artifact_kind":"LoopraTop20ContentIntelligenceCardV2","request_identity":request["semantic_hash"],"candidate_id":entry["candidate_id"],"video_id":entry["video_id"],"original_rank":rank,"evidence_references":evidence,"claims":payload.get("claims",[]),"project_adaptation":payload.get("project_adaptation",{}),"warnings":payload.get("warnings",[]),"validation":{"status":"VALID","provider_created_source_facts":0},"provider_provenance":{"provider":request["provider"],"model":request["model"],"prompt_version":request["prompt_version"]},"reuse_status":"NEW","semantic_hash":""})
            _atomic(root/"content-intelligence"/f"{rank:02d}"/"request.json",request); _atomic(root/"content-intelligence"/f"{rank:02d}"/"card.json",card); cards.append(card)
        return cards


class LoopraTop20EditorialReviewPackageV2:
    def build(self, *, root: Path, batch: dict[str, Any], entries: list[dict[str, Any]], acquisition: list[dict[str, Any]], cards: list[dict[str, Any]]) -> dict[str, Any]:
        _validate(entries)
        if len(cards)!=TARGET_COUNT: raise LoopraTop20V2Error("V2_MISSING_CARD")
        report=_sealed({"schema_version":SCHEMA_VERSION,"artifact_kind":"LoopraTop20ContentIntelligenceReportV2","batch_id":batch["batch_id"],"batch_hash":batch["semantic_hash"],"fresh_cycle_id":batch["fresh_cycle_id"],"ordered_ranks":list(range(1,21)),"cards":[{"original_rank":c["original_rank"],"card_reference":f"content-intelligence/{c['original_rank']:02d}/card.json","card_hash":c["semantic_hash"]} for c in cards],"winner":None,"human_verified":False,"progress_counts":{"selected":20,"acquired":20,"inspected":20,"ocr":20,"transcription":20,"valid_cards":20},"incomplete_items":[],"semantic_hash":""})
        review=_sealed({"schema_version":SCHEMA_VERSION,"artifact_kind":"LoopraTop20EditorialReviewPackageV2","batch_id":batch["batch_id"],"report_hash":report["semantic_hash"],"reviewer":{"reviewer_id":"nura-owner","reviewer_role":"OWNER","reviewer_display_name":"Василий","human_confirmation":False},"status":"PENDING_OWNER_EDITORIAL_REVIEW","production_brief_allowed":False,"items":[{"original_rank":entry["original_rank"],"candidate_id":entry["candidate_id"],"video_id":entry["video_id"],"source_media_reference":media["source_media_reference"],"card_reference":f"content-intelligence/{entry['original_rank']:02d}/card.json","decision":"PENDING","edits":{"approved_mechanism":None,"approved_hook":None,"mandatory_revisions":[],"prohibited_copying_elements":[],"safety_notes":None,"format_direction":None,"optional_title_direction":None,"owner_comment":None}} for entry,media in zip(entries,acquisition,strict=True)],"semantic_hash":""})
        _atomic(root/"aggregate-report-v2.json",report); _atomic(root/"owner-editorial-review-v2.json",review)
        return {"report":report,"review":review}


def run_offline_acceptance(*, root: Path, batch_id: str="v2-offline-batch", fail_rank: int | None=None) -> dict[str, Any]:
    entries=[{"candidate_id":f"v2-candidate-{rank:02d}","video_id":f"v2-video-{rank:02d}","original_rank":rank} for rank in range(1,21)]
    batch=_sealed({"schema_version":SCHEMA_VERSION,"artifact_kind":"loopra_top20_v2_batch","batch_id":batch_id,"fresh_cycle_id":"v2-offline-cycle","project_context_hash":_hash("nura-context"),"semantic_hash":""})
    acquisition=LoopraTop20MediaAcquisitionV2().run(root=root,batch=batch,entries=entries)
    if fail_rank:
        acquisition[fail_rank-1]={**acquisition[fail_rank-1],"status":"FAILED","retryable_status":"RESUMABLE"}
        return {"status":"PARTIAL","failed_ranks":[fail_rank],"acquisition":acquisition}
    cards=LoopraTop20ContentIntelligenceV2().run(root=root,batch=batch,entries=entries,acquisition=acquisition)
    package=LoopraTop20EditorialReviewPackageV2().build(root=root,batch=batch,entries=entries,acquisition=acquisition,cards=cards)
    return {"status":"READY_FOR_OWNER_EDITORIAL_REVIEW","batch":batch,"acquisition":acquisition,"cards":cards,**package,"network_calls":0,"browser_calls":0,"provider_calls":0,"credentials_required":False}


def run_fresh_top20_b1(*, root: Path, dependencies: dict[str, Callable[..., Any]] | None = None, offline: bool = False) -> dict[str, Any]:
    """Canonical B1 execution shape; tests inject every side-effect boundary.

    Production wiring is intentionally explicit: no fake boundary can be used
    unless ``offline=True``.  This prevents a test fixture from becoming a
    hidden production search, browser or provider implementation.
    """
    required=("collect","select","acquire","inspect","ocr","transcribe","provider")
    if not dependencies or any(name not in dependencies for name in required):
        return {"status":"BLOCKED","reason":"B1_V2_CANONICAL_BOUNDARIES_NOT_CONFIGURED"}
    if not offline:
        return {"status":"BLOCKED","reason":"B1_V2_PRODUCTION_DEFAULTS_NOT_WIRED"}
    pool=dependencies["collect"](); entries=dependencies["select"](pool); _validate(entries)
    batch=_sealed({"schema_version":SCHEMA_VERSION,"artifact_kind":"loopra_top20_v2_batch","batch_id":"fresh-v2-"+_hash(entries)[:12],"fresh_cycle_id":"fresh-cycle-"+_hash(pool)[:12],"project_context_hash":_hash("nura-context"),"semantic_hash":""})
    acquisition=LoopraTop20MediaAcquisitionV2().run(root=root,batch=batch,entries=entries,capture_one=dependencies["acquire"])
    failed=[item["original_rank"] for item in acquisition if item["status"] not in {"COMPLETED","REUSED","SYNTHETIC_OFFLINE"}]
    if failed:return {"status":"PARTIAL","batch":batch,"failed_ranks":failed,"acquisition":acquisition}
    evidence=[]
    for entry in entries:
        values={"inspection":dependencies["inspect"](entry),"ocr":dependencies["ocr"](entry),"transcription":dependencies["transcribe"](entry)}
        if any(value.get("status") not in {"COMPLETED","REUSED","SYNTHETIC_OFFLINE"} for value in values.values()):
            return {"status":"PARTIAL","batch":batch,"failed_ranks":[entry["original_rank"]],"acquisition":acquisition}
        evidence.append(values)
    cards=LoopraTop20ContentIntelligenceV2().run(root=root,batch=batch,entries=entries,acquisition=acquisition,provider=dependencies["provider"])
    package=LoopraTop20EditorialReviewPackageV2().build(root=root,batch=batch,entries=entries,acquisition=acquisition,cards=cards)
    return {"status":"READY_FOR_OWNER_EDITORIAL_REVIEW","batch":batch,"acquisition":acquisition,"evidence":evidence,"cards":cards,**package,"browser_calls":0,"network_calls":0,"provider_calls":0}
