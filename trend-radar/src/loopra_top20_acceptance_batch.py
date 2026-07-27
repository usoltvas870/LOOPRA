"""Stage 5O-B0: offline, versioned TOP-20 acceptance batch boundary.

This module is deliberately synthetic-only.  It proves batch state, human
gates, atomic persistence and resume semantics without invoking the existing
five-item or single-item production contracts.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "2.0"
PROFILE = "FRESH_TOP20_OPERATOR_BATCH_ACCEPTANCE"
TARGET_COUNT = 20
PHASES = (
    "INITIALIZED", "COLLECTING", "READY_FOR_EDITORIAL_REVIEW", "EDITORIAL_REVIEW_PENDING",
    "EDITORIAL_REVIEW_FINALIZED", "GENERATING_SCRIPTS", "READY_FOR_SCRIPT_REVIEW",
    "SCRIPT_REVIEW_PENDING", "SCRIPT_REVIEW_FINALIZED", "BUILDING_EXPORTS",
    "READY_FOR_OWNER_BATCH_ACCEPTANCE", "ACCEPTED", "ACCEPTED_WITH_GAPS",
    "NEEDS_MORE_TESTING", "BLOCKED",
)
EDITORIAL_DECISIONS = {"APPROVED_FOR_PRODUCTION_BRIEF", "APPROVED_WITH_EDITORIAL_EDITS", "REJECTED", "NEEDS_FURTHER_REVIEW"}
SCRIPT_DECISIONS = {"APPROVE", "APPROVE_WITH_EDITS", "REJECT", "REQUEST_ALTERNATIVE"}


class Top20AcceptanceError(ValueError):
    pass


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _atomic(path: Path, value: dict[str, Any]) -> str:
    text = _json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise Top20AcceptanceError("CONFLICTING_BATCH_ARTIFACT")
        return "REUSED"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as handle:
        handle.write(text); temporary = Path(handle.name)
    try:
        os.link(temporary, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text:
            raise Top20AcceptanceError("CONFLICTING_BATCH_ARTIFACT")
    finally:
        temporary.unlink(missing_ok=True)
    return "COMPLETED"


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise Top20AcceptanceError("INVALID_BATCH_ARTIFACT") from error
    if not isinstance(value, dict):
        raise Top20AcceptanceError("BATCH_OBJECT_REQUIRED")
    return value


def _item(batch_id: str, rank: int) -> dict[str, Any]:
    video_id = f"synthetic-fresh-{rank:02d}"
    value = {
        "schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_top20_acceptance_item",
        "item_id": f"top20-item-{batch_id[-12:]}-{rank:02d}", "batch_reference": batch_id,
        "project_id": "nura", "candidate_id": f"candidate-{video_id}", "video_id": video_id,
        "original_rank": rank, "selection_entry_reference": f"selection/candidates/{rank:02d}",
        "lifecycle_status": "PENDING", "current_stage": "INITIALIZED", "source_media_reference": None,
        "acquisition_reference": None, "inspection_reference": None, "ocr_reference": None,
        "transcription_reference": None, "content_intelligence_reference": None,
        "editorial_review_reference": None, "production_brief_reference": None,
        "script_input_reference": None, "provider_draft_reference": None,
        "human_script_review_reference": None, "human_approved_script_reference": None,
        "operator_export_reference": None, "errors": [], "warnings": ["SYNTHETIC_OFFLINE_FIXTURE"],
        "retryable_status": "PENDING", "resume_status": "RESUMABLE", "reuse_metadata": {"mode": "CONTENT_IDENTICAL_ONLY"},
        "content_hash": "",
    }
    value["content_hash"] = _hash({key: item for key, item in value.items() if key != "content_hash"})
    return value


def _batch_id() -> str:
    return "loopra-top20-" + _hash({"schema": SCHEMA_VERSION, "profile": PROFILE, "project": "nura", "target": TARGET_COUNT})[:12]


def _root(runtime_root: Path) -> Path:
    return Path(runtime_root) / _batch_id()


def _store_state(root: Path, batch: dict[str, Any]) -> str:
    """Append an immutable state snapshot; a batch never overwrites its past."""
    batch["content_hash"] = ""
    batch["content_hash"] = _hash({key: value for key, value in batch.items() if key != "content_hash"})
    identity = batch["content_hash"][:16]
    return _atomic(root / "states" / f"{batch['current_phase'].lower()}-{identity}.json", batch)


def _store_item(root: Path, item: dict[str, Any]) -> str:
    return _atomic(root / "items" / f"{item['original_rank']:02d}" / f"{item['content_hash'][:16]}.json", item)


def initialize(*, runtime_root: Path) -> dict[str, Any]:
    batch_id = _batch_id(); root = _root(runtime_root)
    items = [_item(batch_id, rank) for rank in range(1, TARGET_COUNT + 1)]
    refs = [{"rank": item["original_rank"], "item_id": item["item_id"], "content_hash": item["content_hash"]} for item in items]
    batch = {
        "schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_top20_acceptance_batch", "batch_id": batch_id,
        "batch_version": 1, "acceptance_profile": PROFILE, "project_id": "nura", "target_count": TARGET_COUNT,
        "fresh_cycle_id": "synthetic-fresh-cycle-" + batch_id[-12:],
        "search_config_reference": "SYNTHETIC_OFFLINE_NO_SEARCH", "selection_manifest_reference": "SYNTHETIC_OFFLINE_NO_MANIFEST",
        "selection_manifest_hash": _hash(refs), "original_ranking_preserved": True, "batch_status": "PENDING",
        "current_phase": "INITIALIZED", "human_gate_status": "EDITORIAL_REVIEW_PENDING", "item_count": TARGET_COUNT,
        "item_references": refs, "progress_counts": {"initialized": TARGET_COUNT, "collected": 0, "ci_completed": 0, "editorial_finalized": 0, "scripts_finalized": 0, "exports_completed": 0},
        "provider_call_budget": {"content_intelligence_primary": 20, "script_primary": 20, "scene_image_prompt": 0},
        "provider_call_counts": {"content_intelligence_primary": 0, "script_primary": 0, "retry": 0, "reused": 0, "skipped": 0, "network_calls": 0},
        "unresolved_requirements": ["Synthetic fixture only; real fresh search is a later gate."],
        "persistence_metadata": {"mode": "ATOMIC_CONTENT_IDENTICAL_REUSE", "runtime_ignored": True}, "reuse_metadata": {"batch_identity": batch_id}, "content_hash": "",
    }
    batch["content_hash"] = _hash({key: item for key, item in batch.items() if key != "content_hash"})
    statuses = [_atomic(root / "batch.json", batch), _store_state(root, batch)] + [_store_item(root, item) for item in items]
    return {"status": "COMPLETED" if "COMPLETED" in statuses else "REUSED", "root": root, "batch": batch}


def _load(runtime_root: Path) -> tuple[Path, dict[str, Any], list[dict[str, Any]]]:
    result = initialize(runtime_root=runtime_root); root = result["root"]
    states = sorted((root / "states").glob("*.json"), key=lambda path: path.stat().st_mtime_ns)
    batch = _read(states[-1] if states else root / "batch.json")
    items = []
    for rank in range(1, TARGET_COUNT + 1):
        snapshots = sorted((root / "items" / f"{rank:02d}").glob("*.json"), key=lambda path: path.stat().st_mtime_ns)
        if not snapshots: raise Top20AcceptanceError("MISSING_ITEM_SNAPSHOT")
        items.append(_read(snapshots[-1]))
    _validate(batch, items)
    return root, batch, items


def _validate(batch: dict[str, Any], items: list[dict[str, Any]]) -> None:
    if batch.get("acceptance_profile") != PROFILE or batch.get("target_count") != TARGET_COUNT or batch.get("item_count") != TARGET_COUNT:
        raise Top20AcceptanceError("INVALID_BATCH_PROFILE_OR_COUNT")
    ranks = [item.get("original_rank") for item in items]; ids = [item.get("video_id") for item in items]
    if ranks != list(range(1, TARGET_COUNT + 1)): raise Top20AcceptanceError("ORIGINAL_RANK_ORDER_REQUIRED")
    if len(set(ids)) != TARGET_COUNT or any(not value for value in ids): raise Top20AcceptanceError("UNIQUE_VIDEO_IDS_REQUIRED")
    if any(item.get("batch_reference") != batch["batch_id"] for item in items): raise Top20AcceptanceError("ITEM_BATCH_REFERENCE_MISMATCH")
    if any(item.get("content_hash") != _hash({key: value for key, value in item.items() if key != "content_hash"}) for item in items): raise Top20AcceptanceError("ITEM_HASH_MISMATCH")


def _transition(runtime_root: Path, phase: str, mutate) -> dict[str, Any]:
    root, old, items = _load(runtime_root); new_items = mutate(items)
    refs = [{"rank": item["original_rank"], "item_id": item["item_id"], "content_hash": item["content_hash"]} for item in new_items]
    updated = dict(old); updated["current_phase"] = phase; updated["batch_status"] = "PENDING" if phase not in {"ACCEPTED", "ACCEPTED_WITH_GAPS", "NEEDS_MORE_TESTING", "BLOCKED"} else phase
    updated["item_references"] = refs; updated["content_hash"] = ""; updated["content_hash"] = _hash({key: value for key, value in updated.items() if key != "content_hash"})
    statuses = [_store_state(root, updated)] + [_store_item(root, item) for item in new_items]
    return {"status": "COMPLETED" if "COMPLETED" in statuses else "REUSED", "root": root, "batch": updated, "items": new_items}


def _changed(item: dict[str, Any], **updates: Any) -> dict[str, Any]:
    value = dict(item); value.update(updates); value["content_hash"] = ""; value["content_hash"] = _hash({key: data for key, data in value.items() if key != "content_hash"}); return value


def collect_synthetic(*, runtime_root: Path, fail_rank: int | None = None) -> dict[str, Any]:
    def mutate(items):
        result=[]
        for item in items:
            rank=item["original_rank"]
            if fail_rank == rank:
                result.append(_changed(item, lifecycle_status="RETRYABLE_FAILURE", current_stage="COLLECTING", retryable_status="RETRYABLE_FAILURE", resume_status="RESUMABLE", errors=["SYNTHETIC_INJECTED_FAILURE"]))
            elif item["current_stage"] == "INITIALIZED" or item["retryable_status"] == "RETRYABLE_FAILURE":
                refs={name: f"synthetic/{rank:02d}/{name}.json" for name in ("source_media_reference", "acquisition_reference", "inspection_reference", "ocr_reference", "transcription_reference", "content_intelligence_reference")}
                result.append(_changed(item, lifecycle_status="COMPLETED", current_stage="CONTENT_INTELLIGENCE_COMPLETED", retryable_status="COMPLETED", resume_status="REUSED", **refs))
            else: result.append(item)
        return result
    result=_transition(runtime_root, "EDITORIAL_REVIEW_PENDING", mutate)
    result["batch"]["progress_counts"]["collected"] = sum(item["current_stage"] == "CONTENT_INTELLIGENCE_COMPLETED" for item in result["items"])
    result["batch"]["progress_counts"]["ci_completed"] = result["batch"]["progress_counts"]["collected"]
    result["batch"]["human_gate_status"] = "EDITORIAL_REVIEW_PENDING"
    _store_state(result["root"], result["batch"])
    return result


def create_editorial_package(*, runtime_root: Path) -> dict[str, Any]:
    root, batch, items = _load(runtime_root)
    if any(item["current_stage"] != "CONTENT_INTELLIGENCE_COMPLETED" for item in items): raise Top20AcceptanceError("EDITORIAL_GATE_REQUIRES_20_COMPLETED_ITEMS")
    package={"schema_version":SCHEMA_VERSION,"artifact_kind":"loopra_top20_editorial_review","batch_id":batch["batch_id"],"ranking":[item["original_rank"] for item in items],"review_items":[{"rank":item["original_rank"],"video_id":item["video_id"],"content_intelligence_reference":item["content_intelligence_reference"],"decision":"PENDING"} for item in items],"reviewer":{"human_confirmation":False},"content_hash":""}
    package["content_hash"]=_hash({key:value for key,value in package.items() if key!="content_hash"}); _atomic(root/"editorial_review_package.json",package); return {"root":root,"package":package}


def finalize_editorial(*, runtime_root: Path, decisions: list[dict[str, Any]], human_confirmation: bool) -> dict[str, Any]:
    if not human_confirmation or len(decisions) != TARGET_COUNT: raise Top20AcceptanceError("COMPLETED_HUMAN_EDITORIAL_REVIEW_REQUIRED")
    ranks=[value.get("rank") for value in decisions]
    if ranks != list(range(1,TARGET_COUNT+1)) or any(value.get("decision") not in EDITORIAL_DECISIONS for value in decisions): raise Top20AcceptanceError("INVALID_EDITORIAL_DECISIONS")
    _, _, existing_items = _load(runtime_root)
    if any(item["current_stage"] != "CONTENT_INTELLIGENCE_COMPLETED" for item in existing_items): raise Top20AcceptanceError("EDITORIAL_GATE_REQUIRES_20_COMPLETED_ITEMS")
    def mutate(items):
        return [_changed(item, editorial_review_reference=f"editorial/{item['original_rank']:02d}.json", current_stage="EDITORIAL_REVIEW_FINALIZED", lifecycle_status="PENDING", retryable_status="PENDING", resume_status="RESUMABLE") for item in items]
    result=_transition(runtime_root,"EDITORIAL_REVIEW_FINALIZED",mutate); result["batch"]["human_gate_status"]="EDITORIAL_REVIEW_FINALIZED"; result["batch"]["progress_counts"]["editorial_finalized"]=TARGET_COUNT; result["batch"]["content_hash"]=""; result["batch"]["content_hash"]=_hash({key:value for key,value in result["batch"].items() if key!="content_hash"}); _store_state(result["root"],result["batch"]); _atomic(result["root"] / "finalized_editorial_decisions.json",{"batch_id":result["batch"]["batch_id"],"human_confirmation":True,"decisions":decisions,"content_hash":_hash(decisions)}); return result


def generate_scripts(*, runtime_root: Path) -> dict[str, Any]:
    def mutate(items):
        if any(item["current_stage"] != "EDITORIAL_REVIEW_FINALIZED" for item in items): raise Top20AcceptanceError("SCRIPT_GATE_BLOCKED_BY_EDITORIAL_REVIEW")
        return [_changed(item, production_brief_reference=f"briefs/{item['original_rank']:02d}.json", script_input_reference=f"scripts/{item['original_rank']:02d}/input.json", provider_draft_reference=f"scripts/{item['original_rank']:02d}/draft.json", current_stage="SCRIPT_DRAFT_CREATED", lifecycle_status="PENDING") for item in items]
    result=_transition(runtime_root,"SCRIPT_REVIEW_PENDING",mutate); result["batch"]["human_gate_status"]="SCRIPT_REVIEW_PENDING"; result["batch"]["content_hash"]=""; result["batch"]["content_hash"]=_hash({key:value for key,value in result["batch"].items() if key!="content_hash"}); _store_state(result["root"],result["batch"]); return result


def create_script_package(*, runtime_root: Path) -> dict[str, Any]:
    root,batch,items=_load(runtime_root)
    if any(item["current_stage"] != "SCRIPT_DRAFT_CREATED" for item in items): raise Top20AcceptanceError("SCRIPT_REVIEW_REQUIRES_20_DRAFTS")
    package={"schema_version":SCHEMA_VERSION,"artifact_kind":"loopra_top20_script_review","batch_id":batch["batch_id"],"ranking":[item["original_rank"] for item in items],"review_items":[{"rank":item["original_rank"],"title":f"Synthetic NURA {item['original_rank']:02d}","structured_script":item["provider_draft_reference"],"clean_heygen_text":True,"visual_strategy":"ONE_IMAGE","chatgpt_ready_prompts":1,"decision":"PENDING"} for item in items],"reviewer":{"human_confirmation":False},"content_hash":""}; package["content_hash"]=_hash({key:value for key,value in package.items() if key!="content_hash"}); _atomic(root/"script_review_package.json",package); return {"root":root,"package":package}


def finalize_scripts(*, runtime_root: Path, decisions: list[dict[str, Any]], human_confirmation: bool) -> dict[str, Any]:
    if not human_confirmation or len(decisions)!=TARGET_COUNT: raise Top20AcceptanceError("COMPLETED_HUMAN_SCRIPT_REVIEW_REQUIRED")
    if [value.get("rank") for value in decisions] != list(range(1,TARGET_COUNT+1)) or any(value.get("decision") not in SCRIPT_DECISIONS for value in decisions): raise Top20AcceptanceError("INVALID_SCRIPT_DECISIONS")
    def mutate(items):
        return [_changed(item,human_script_review_reference=f"script-review/{item['original_rank']:02d}.json",human_approved_script_reference=f"approved/{item['original_rank']:02d}.json",current_stage="SCRIPT_REVIEW_FINALIZED",lifecycle_status="PENDING") for item in items]
    result=_transition(runtime_root,"SCRIPT_REVIEW_FINALIZED",mutate); result["batch"]["human_gate_status"]="SCRIPT_REVIEW_FINALIZED"; result["batch"]["progress_counts"]["scripts_finalized"]=TARGET_COUNT; result["batch"]["content_hash"]=""; result["batch"]["content_hash"]=_hash({key:value for key,value in result["batch"].items() if key!="content_hash"}); _store_state(result["root"],result["batch"]); return result


def build_exports(*, runtime_root: Path) -> dict[str, Any]:
    def mutate(items):
        if any(item["current_stage"] != "SCRIPT_REVIEW_FINALIZED" for item in items): raise Top20AcceptanceError("EXPORT_GATE_BLOCKED_BY_SCRIPT_REVIEW")
        return [_changed(item,operator_export_reference=f"exports/{item['original_rank']:02d}/manifest.json",current_stage="OPERATOR_EXPORT_READY",lifecycle_status="COMPLETED",retryable_status="COMPLETED",resume_status="REUSED") for item in items]
    result=_transition(runtime_root,"READY_FOR_OWNER_BATCH_ACCEPTANCE",mutate); result["batch"]["human_gate_status"]="OWNER_BATCH_ACCEPTANCE_PENDING"; result["batch"]["progress_counts"]["exports_completed"]=TARGET_COUNT; result["batch"]["content_hash"]=""; result["batch"]["content_hash"]=_hash({key:value for key,value in result["batch"].items() if key!="content_hash"}); _store_state(result["root"],result["batch"]); index={"schema_version":SCHEMA_VERSION,"artifact_kind":"loopra_top20_operator_export_index","batch_id":result["batch"]["batch_id"],"exports":[{"rank":item["original_rank"],"candidate_id":item["candidate_id"],"source_video_filename":None,"video_id":item["video_id"],"title":f"Synthetic NURA {item['original_rank']:02d}","material_folder":f"materials/{item['original_rank']:02d}","visual_strategy":"ONE_IMAGE","image_prompt_count":1,"final_status":"SYNTHETIC_NOT_USER_FACING"} for item in result["items"]],"content_hash":""}; index["content_hash"]=_hash({key:value for key,value in index.items() if key!="content_hash"}); _atomic(result["root"] / "operator_export_index.json",index); return result


def owner_accept(*, runtime_root: Path, decision: str, human_confirmation: bool) -> dict[str, Any]:
    if decision not in {"ACCEPTED","ACCEPTED_WITH_GAPS","NEEDS_MORE_TESTING"} or not human_confirmation: raise Top20AcceptanceError("OWNER_BATCH_ACCEPTANCE_REQUIRED")
    root,batch,items=_load(runtime_root)
    if batch["current_phase"] != "READY_FOR_OWNER_BATCH_ACCEPTANCE" or sum(bool(item["operator_export_reference"]) for item in items)!=TARGET_COUNT: raise Top20AcceptanceError("OWNER_ACCEPTANCE_REQUIRES_20_EXPORTS")
    def mutate(current): return current
    result=_transition(runtime_root,decision,mutate); result["batch"]["human_gate_status"]="OWNER_BATCH_ACCEPTANCE_FINALIZED"; result["batch"]["scope_frozen"] = decision == "ACCEPTED"; result["batch"]["loopra_0_5_status"]="LOOPRA_0_5_ACCEPTED" if decision=="ACCEPTED" else decision; result["batch"]["content_hash"]=""; result["batch"]["content_hash"]=_hash({key:value for key,value in result["batch"].items() if key!="content_hash"}); _store_state(result["root"],result["batch"]); return result


def verify(*, runtime_root: Path) -> dict[str, Any]:
    root,batch,items=_load(runtime_root); _validate(batch,items)
    return {"status":"PASS","batch_id":batch["batch_id"],"target_count":TARGET_COUNT,"item_count":len(items),"original_ranking_preserved":True,"network_calls":batch["provider_call_counts"]["network_calls"],"provider_calls":0,"credentials_required":False,"current_phase":batch["current_phase"],"scope_frozen":batch.get("scope_frozen",False),"root":str(root)}
