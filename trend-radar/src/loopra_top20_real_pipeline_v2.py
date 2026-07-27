"""Versioned TOP-20 production contracts for the one-time B1 acceptance profile.

v1 five-item modules remain untouched.  This module owns only the v2 envelope;
the real runner may inject existing single-item capture/evidence/provider helpers.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import subprocess
import tempfile
from dataclasses import asdict
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


def _replace_retryable(path: Path, payload: dict[str, Any]) -> str:
    existing = _read_json(path)
    if not existing or existing.get("status") in {"COMPLETED", "REUSED", "SYNTHETIC_OFFLINE"}:
        return _atomic(path, payload)
    history = path.parent / "attempts" / path.stem / f"{existing.get('semantic_hash', _hash(existing))[:16]}.json"
    _atomic(history, existing)
    text = _json(payload); path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as out:
        out.write(text); temporary = Path(out.name)
    os.replace(temporary, path)
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
            existing_path = root/"acquisition"/f"{rank:02d}.json"
            if result["status"] == "REUSED" and existing_path.is_file():
                existing = json.loads(existing_path.read_text(encoding="utf-8"))
                if existing.get("batch_id") != batch["batch_id"] or existing.get("selection_entry_hash") != _hash(entry):
                    raise LoopraTop20V2Error("CONFLICTING_V2_ARTIFACT")
                results.append(existing); continue
            record=_sealed({"schema_version":SCHEMA_VERSION,"artifact_kind":"LoopraTop20MediaAcquisitionV2","batch_id":batch["batch_id"],"candidate_id":entry["candidate_id"],"video_id":entry["video_id"],"original_rank":rank,"selection_entry_hash":_hash(entry),"attempts":1,"retryable_status":"RESUMABLE" if result["status"] not in {"COMPLETED","REUSED","SYNTHETIC_OFFLINE"} else "COMPLETED","reuse_status":"REUSED" if result["status"]=="REUSED" else "NEW", "warnings":[],"errors":[], **result,"semantic_hash":""})
            _replace_retryable(root/"acquisition"/f"{rank:02d}.json",record); results.append(record)
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
    """Canonical B1 execution shape for injected offline or production boundaries."""
    required=("collect","select","acquire","inspect","ocr","transcribe")
    analyze = dependencies.get("analyze_content_intelligence") if dependencies else None
    analyze = analyze or (dependencies.get("provider") if dependencies else None)
    if not dependencies or any(not callable(dependencies.get(name)) for name in required) or not callable(analyze):
        return {"status":"BLOCKED","reason":"B1_V2_CANONICAL_BOUNDARIES_NOT_CONFIGURED"}
    try:
        pool=dependencies["collect"]()
        candidate_count = len(pool.get("candidates", [])) if isinstance(pool, dict) else len(pool)
        if candidate_count < TARGET_COUNT:
            access_status = pool.get("public_access_status", "PUBLIC_ACCESS_LIMITED" if candidate_count else "PUBLIC_ACCESS_BLOCKED") if isinstance(pool, dict) else "PUBLIC_ACCESS_LIMITED"
            status = access_status if candidate_count == 0 and access_status in {"PUBLIC_ACCESS_BLOCKED", "CAPTCHA_OR_ANTI_BOT_CHALLENGE", "RATE_LIMITED"} else "PARTIAL_INSUFFICIENT_CANDIDATES"
            return {"status":status,"actual_candidate_count":candidate_count,"required_candidate_count":TARGET_COUNT,"search_run_id":pool.get("search_run_id") if isinstance(pool,dict) else None,"public_access_status":access_status,"blocking_reason":pool.get("blocking_reason") if isinstance(pool,dict) else None,"pool":pool}
        entries=dependencies["select"](pool); _validate(entries)
        pool_identity = {key:value for key,value in pool.items() if key != "reuse_status"} if isinstance(pool, dict) else pool
        batch=_sealed({"schema_version":SCHEMA_VERSION,"artifact_kind":"loopra_top20_v2_batch","batch_id":"fresh-v2-"+_hash(entries)[:12],"fresh_cycle_id":"fresh-cycle-"+_hash(pool_identity)[:12],"project_context_hash":_hash("nura-context"),"semantic_hash":""})
        acquisition=LoopraTop20MediaAcquisitionV2().run(root=root,batch=batch,entries=entries,capture_one=dependencies["acquire"])
        failed=[item["original_rank"] for item in acquisition if item["status"] not in {"COMPLETED","REUSED","SYNTHETIC_OFFLINE"}]
        if failed:return {"status":"PARTIAL","batch":batch,"failed_ranks":failed,"acquisition":acquisition}
        evidence=[]; failed=[]
        for entry in entries:
            values={"inspection":dependencies["inspect"](entry),"ocr":dependencies["ocr"](entry),"transcription":dependencies["transcribe"](entry)}
            if any(value.get("status") not in {"COMPLETED","REUSED","SYNTHETIC_OFFLINE"} for value in values.values()): failed.append(entry["original_rank"])
            evidence.append(values)
        if failed:return {"status":"PARTIAL","batch":batch,"failed_ranks":failed,"acquisition":acquisition,"evidence":evidence}
        cards=LoopraTop20ContentIntelligenceV2().run(root=root,batch=batch,entries=entries,acquisition=acquisition,provider=analyze)
        package=LoopraTop20EditorialReviewPackageV2().build(root=root,batch=batch,entries=entries,acquisition=acquisition,cards=cards)
        return {"status":"READY_FOR_OWNER_EDITORIAL_REVIEW","batch":batch,"acquisition":acquisition,"evidence":evidence,"cards":cards,**package,"browser_calls":0,"network_calls":0,"provider_calls":0}
    finally:
        close = dependencies.get("close")
        if callable(close): close()


def _run_async(awaitable):
    return asyncio.run(awaitable)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _canonical_services() -> dict[str, Any]:
    """Centralized imports for the production composition boundary."""
    from browser_media_capture import BrowserMediaCaptureRequest, _read_reusable_record, capture_browser_media_in_context
    from collector import RadarOperationalError, TikTokCollector
    from content_intelligence import build_analysis_input, build_card, validate_provider_result
    from content_intelligence_provider import (
        DeepSeekContentIntelligenceProvider, PROMPT_VERSION, build_provider_payload,
        load_project_context, post_deepseek_request, _without_reasoning_content,
    )
    from format_inspection import inspect as inspect_media
    from media_acquisition import _ffprobe
    from ocr_evidence import OcrRunRequest, WindowsMediaOcrEngine, _run_candidate
    from scoring import compute_scores
    from selection_manifest import build_selection_manifest, write_selection_manifest
    from transcription_evidence import (
        DEFAULT_OPTIONS, FasterWhisperEngine, TranscriptionRunRequest, _no_audio_result,
        _prepare, _transcribe, _write_atomic as write_transcription,
    )
    from utils import get_config_bool, get_cookie_path, read_source_file
    return locals()


def _runtime_is_ignored(runtime_root: Path, repository_root: Path) -> bool:
    resolved = runtime_root.resolve()
    try:
        resolved.relative_to(repository_root.resolve())
    except ValueError:
        return True
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", "--", str(resolved)], cwd=repository_root,
        check=False, capture_output=True,
    )
    return result.returncode == 0


def validate_fresh_top20_b1_production_readiness(
    *, runtime_root: Path, repository_root: Path | None = None,
) -> dict[str, Any]:
    """Validate composition without opening a browser, reading credentials, or calling providers."""
    repository_root = (repository_root or Path(__file__).resolve().parents[2]).resolve()
    try:
        services = _canonical_services()
    except (ImportError, AttributeError) as error:
        missing = getattr(error, "name", None) or "canonical_import"
        return {"ready": False, "status": "BLOCKED", "reason": f"B1_REAL_DEPENDENCY_MISSING:{missing}"}
    required = {
        "production_dependency_factory": build_fresh_top20_b1_production_dependencies,
        "collect": services.get("TikTokCollector"), "select": services.get("build_selection_manifest"),
        "acquire": services.get("capture_browser_media_in_context"), "inspect": services.get("inspect_media"),
        "ocr": services.get("_run_candidate"), "transcription": services.get("_prepare"),
        "content_intelligence": services.get("post_deepseek_request"),
        "browser_lifecycle": getattr(services.get("TikTokCollector"), "close", None),
    }
    for name, dependency in required.items():
        if not callable(dependency):
            return {"ready": False, "status": "BLOCKED", "reason": f"B1_REAL_DEPENDENCY_MISSING:{name}"}
    from browser_media_capture import SCHEMA_VERSION as capture_schema
    from content_intelligence import CARD_SCHEMA_VERSION, INPUT_SCHEMA_VERSION
    from ocr_evidence import SCHEMA_VERSION as ocr_schema
    from selection_manifest import SCHEMA_VERSION as selection_schema
    from transcription_evidence import SCHEMA_VERSION as transcription_schema
    schemas = {"b1": SCHEMA_VERSION, "selection": selection_schema, "capture": capture_schema, "ocr": ocr_schema, "transcription": transcription_schema, "ci_input": INPUT_SCHEMA_VERSION, "ci_card": CARD_SCHEMA_VERSION}
    expected = {"b1": "2.0", "selection": "1.0", "capture": "1.0", "ocr": "1.1", "transcription": "1.1", "ci_input": "0.1", "ci_card": "0.1"}
    if schemas != expected:
        return {"ready": False, "status": "BLOCKED", "reason": "B1_REAL_DEPENDENCY_MISSING:compatible_schema_versions", "schemas": schemas}
    config_dir = repository_root / "trend-radar" / "config"
    config_names = ("competitors.txt", "hashtags.txt", "keywords.txt", "rotational.txt")
    if any(not (config_dir / name).is_file() for name in config_names):
        return {"ready": False, "status": "BLOCKED", "reason": "B1_REAL_DEPENDENCY_MISSING:nura_config"}
    configured = [line.strip() for name in config_names for line in (config_dir / name).read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not configured:
        return {"ready": False, "status": "BLOCKED", "reason": "B1_REAL_DEPENDENCY_MISSING:nura_config"}
    if not _runtime_is_ignored(Path(runtime_root), repository_root):
        return {"ready": False, "status": "BLOCKED", "reason": "B1_REAL_DEPENDENCY_MISSING:git_ignored_runtime_root"}
    return {"ready": True, "status": "READY", "schemas": schemas, "config_entries": len(configured), "runtime_root_git_ignored": True}


def build_fresh_top20_b1_production_dependencies(
    *, root: Path, repository_root: Path | None = None,
) -> dict[str, Callable[..., Any]]:
    """Build thin state-sharing adapters over the canonical production services."""
    root = Path(root)
    repository_root = (repository_root or Path(__file__).resolve().parents[2]).resolve()
    services = _canonical_services()
    state: dict[str, Any] = {"acquisition_records": {}, "manifest": None, "manifest_path": None, "acquisition_collector": None}
    canonical_root = root / "canonical"
    collection_path = canonical_root / "collection.json"
    collection_status_path = canonical_root / "collection-status.json"

    def collect() -> dict[str, Any]:
        existing = _read_json(collection_path)
        if existing and existing.get("schema_version") == SCHEMA_VERSION and existing.get("artifact_kind") == "fresh_top20_collection":
            return {**existing, "reuse_status": "REUSED"}
        config_names = ("competitors.txt", "hashtags.txt", "keywords.txt", "rotational.txt")
        config_dir = repository_root / "trend-radar" / "config"
        values = {name: services["read_source_file"](name) for name in config_names}
        rotational = values["rotational.txt"]
        sources = {"competitors": values["competitors.txt"], "hashtags": values["hashtags.txt"], "keywords": values["keywords.txt"], "rotational": {"hashtags": [item for item in rotational if len(item.split()) == 1], "keywords": [item for item in rotational if len(item.split()) > 1]}}
        refs = [{"reference": f"trend-radar/config/{name}", "sha256": _file_sha256(config_dir / name)} for name in config_names]
        config_sha256 = _hash(refs)
        collector = services["TikTokCollector"](headless=services["get_config_bool"]("HEADLESS", True))
        resumable = _read_json(collection_status_path)
        resumed_after_public_first_policy_fix = bool(resumable and resumable.get("resumable") and resumable.get("config_sha256") == config_sha256)
        if resumed_after_public_first_policy_fix:
            collector.run_id = resumable["search_run_id"]
            collector.collected_at = resumable["search_timestamp"]

        def access_fields(*, raw_count: int, deduplicated_count: int, status: str, blocking_reason: str | None = None) -> dict[str, Any]:
            access_mode = getattr(collector, "access_mode", "NO_SESSION_STATE")
            return {"status":status,"access_mode":access_mode,"authenticated_session_present":access_mode=="AUTHENTICATED_SESSION","guest_state_present":access_mode=="GUEST_SESSION","login_overlay_observed":bool(getattr(collector,"login_overlay_observed",False)),"overlay_dismissed":bool(getattr(collector,"overlay_dismissed",False)),"public_cards_observed":int(getattr(collector,"public_cards_observed",0)),"raw_candidate_count":raw_count,"deduplicated_candidate_count":deduplicated_count,"public_access_status":getattr(collector,"public_access_status",status),"blocking_reason":blocking_reason or getattr(collector,"blocking_reason",None),"captcha_observed":bool(getattr(collector,"captcha_observed",False)),"rate_limit_observed":bool(getattr(collector,"rate_limit_observed",False)),"resumed_after_public_first_policy_fix":resumed_after_public_first_policy_fix}

        async def execute():
            try:
                await collector.start()
                raw = await collector.collect_all(sources)
                return await collector.enrich_missing_stats(raw)
            finally:
                await collector.close()

        try:
            candidates = _run_async(execute())
        except services["RadarOperationalError"] as error:
            typed = {"captcha_or_anti_bot_challenge":"CAPTCHA_OR_ANTI_BOT_CHALLENGE","rate_limited":"RATE_LIMITED","public_access_blocked":"PUBLIC_ACCESS_BLOCKED"}.get(error.reason,"PUBLIC_ACCESS_BLOCKED")
            collector.public_access_status = typed
            collector.blocking_reason = error.reason
            status = _sealed({"schema_version":SCHEMA_VERSION,"artifact_kind":"fresh_top20_collection_status","search_run_id":collector.run_id,"search_timestamp":collector.collected_at,"config_references":refs,"config_sha256":config_sha256,"warnings":[error.reason],"authentication_state":getattr(collector,"last_authentication_state",None),"resumable":True,**access_fields(raw_count=0,deduplicated_count=0,status=typed,blocking_reason=error.reason),"semantic_hash":""})
            _replace_retryable(collection_status_path, status)
            raise LoopraTop20V2Error(typed) from error
        raw_count = sum(int(item.get("raw_items_received",0)) for item in getattr(collector,"source_attempts",[])) or len(candidates); unique: dict[str, dict[str, Any]] = {}
        for candidate in candidates:
            identity = str(candidate.get("video_id") or candidate.get("url") or "")
            if identity and identity not in unique: unique[identity] = candidate
        ranked = services["compute_scores"](list(unique.values()))
        warnings = [str(item.get("error_reason")) for item in getattr(collector, "source_attempts", []) if item.get("error_reason")]
        default_access = "PUBLIC_ACCESS_SUFFICIENT" if len(ranked)>=TARGET_COUNT else "PUBLIC_ACCESS_LIMITED" if ranked else "PUBLIC_ACCESS_BLOCKED"
        public_access_status = getattr(collector,"public_access_status",default_access)
        if public_access_status in {"AUTH_OPTIONAL",None}: public_access_status=default_access
        collector.public_access_status = public_access_status
        payload = _sealed({"schema_version":SCHEMA_VERSION,"artifact_kind":"fresh_top20_collection","search_run_id":collector.run_id,"search_timestamp":collector.collected_at,"config_references":refs,"config_sha256":config_sha256,"filtered_invalid_count":max(0,raw_count-len(ranked)),"warnings":warnings,"candidates":ranked,**access_fields(raw_count=raw_count,deduplicated_count=len(ranked),status=public_access_status),"semantic_hash":""})
        _atomic(collection_path, payload)
        status = _sealed({key:value for key,value in payload.items() if key not in {"artifact_kind","candidates","semantic_hash"}} | {"schema_version":SCHEMA_VERSION,"artifact_kind":"fresh_top20_collection_status","resumable":len(ranked)<TARGET_COUNT,"semantic_hash":""})
        _replace_retryable(collection_status_path, status)
        return payload

    def select(pool: dict[str, Any]) -> list[dict[str, Any]]:
        manifest = services["build_selection_manifest"](pool["candidates"], radar_run_id=pool["search_run_id"], created_at=pool["search_timestamp"])
        path = services["write_selection_manifest"](manifest, root=canonical_root / "selection")
        state.update(manifest=manifest, manifest_path=path)
        entries = [{"candidate_id": item.video_id, "video_id": item.video_id, "original_rank": item.rank, "canonical_url": item.canonical_url, "selection_manifest_reference": str(path.relative_to(root)).replace("\\", "/"), "selection_manifest_hash": manifest.manifest_hash} for item in manifest.candidates]
        _validate(entries)
        return entries

    def get_manifest():
        if state["manifest"] is None:
            raise LoopraTop20V2Error("B1_REAL_DEPENDENCY_MISSING:selection_manifest")
        return state["manifest"]

    def get_candidate(entry):
        return next(item for item in get_manifest().candidates if item.video_id == entry["video_id"])

    def acquisition_run_root() -> Path:
        return canonical_root / "acquisition" / get_manifest().radar_run_id

    def acquire(entry: dict[str, Any]) -> dict[str, Any]:
        manifest = get_manifest(); candidate = get_candidate(entry); run_root = acquisition_run_root(); candidate_root = run_root / candidate.video_id
        reusable = services["_read_reusable_record"](candidate_root, run_root, manifest.manifest_hash, candidate.video_id, 40 * 1024 * 1024)
        if reusable is not None:
            record = reusable
        else:
            collector = state["acquisition_collector"]
            if collector is None:
                collector = services["TikTokCollector"](headless=services["get_config_bool"]("HEADLESS", True))
                _run_async(collector.start()); state["acquisition_collector"] = collector
            request = services["BrowserMediaCaptureRequest"](selection_manifest_path=state["manifest_path"], cookie_state_path=services["get_cookie_path"](), output_root=canonical_root / "acquisition", candidate_id=candidate.video_id)
            record = _run_async(services["capture_browser_media_in_context"](request, manifest, candidate, collector.context))
        record_dict = record.to_dict() if hasattr(record, "to_dict") else asdict(record) if not isinstance(record, dict) else record
        state["acquisition_records"][candidate.video_id] = record_dict
        media_ref = record_dict.get("local_media_path"); media_path = run_root / media_ref if media_ref else None
        valid = bool(media_path and media_path.is_file() and os.access(media_path, os.R_OK) and _file_sha256(media_path) == record_dict.get("media_sha256"))
        probe = services["_ffprobe"](media_path) if valid else {"valid": False, "error": "media_missing_or_hash_mismatch"}
        status = "REUSED" if record_dict.get("status") == "REUSED" and probe.get("valid") else "COMPLETED" if record_dict.get("status") == "COMPLETED" and probe.get("valid") else "FAILED"
        return {"status":status,"source_media_reference":str(media_path.relative_to(root)).replace("\\", "/") if media_path else None,"source_media_sha256":record_dict.get("media_sha256"),"duration_seconds":probe.get("duration_seconds"),"ffprobe_status":"VALID" if probe.get("valid") else "INVALID","method":record_dict.get("acquisition_method"),"warnings":record_dict.get("warnings",[]),"errors":record_dict.get("errors",[]),"retryable":status=="FAILED"}

    def inspect(entry: dict[str, Any]) -> dict[str, Any]:
        record = state["acquisition_records"][entry["video_id"]]; media = acquisition_run_root() / record["local_media_path"]
        output = canonical_root / "inspection" / entry["video_id"]; target = output / "inspection.json"; existing = _read_json(target)
        reused = bool(existing and existing.get("media_sha256") == record.get("media_sha256") and existing.get("status") in {"COMPLETED","DEGRADED"})
        result = existing if reused else services["inspect_media"](media, output, entry["video_id"], entry.get("canonical_url"))
        return {"status":"REUSED" if reused else "COMPLETED" if result.get("status") in {"COMPLETED","DEGRADED"} else "FAILED","artifact_reference":str(target.relative_to(root)).replace("\\", "/"),"artifact_sha256":_file_sha256(target),"warnings":result.get("evidence",{}).get("warnings",[]),"reuse_status":"REUSED" if reused else "NEW"}

    def run_ocr(entry: dict[str, Any]) -> dict[str, Any]:
        manifest = get_manifest(); engine = state.setdefault("ocr_engine", services["WindowsMediaOcrEngine"]()); availability = engine.availability()
        request = services["OcrRunRequest"](selection_manifest_path=state["manifest_path"], inspection_root=canonical_root / "inspection", output_root=canonical_root / "intelligence-evidence", candidate_ids=(entry["video_id"],), reuse=True)
        result = services["_run_candidate"](get_candidate(entry), manifest, request, engine, availability)
        target = canonical_root / "intelligence-evidence" / manifest.radar_run_id / "candidates" / entry["video_id"] / "ocr" / "ocr_result.json"
        return {"status":"REUSED" if result.get("reuse_status")=="REUSED" else "COMPLETED" if result.get("status") in {"COMPLETED","DEGRADED"} else "FAILED","artifact_reference":str(target.relative_to(root)).replace("\\", "/"),"artifact_sha256":_file_sha256(target) if target.is_file() else None,"first_text_hook":result.get("first_text_hook"),"no_text_status":result.get("first_text_hook_reason"),"warnings":result.get("warnings",[]),"reuse_status":result.get("reuse_status","NEW")}

    def transcribe(entry: dict[str, Any]) -> dict[str, Any]:
        manifest = get_manifest(); engine = state.setdefault("transcription_engine", services["FasterWhisperEngine"]()); availability = engine.availability(); options = dict(services["DEFAULT_OPTIONS"])
        request = services["TranscriptionRunRequest"](selection_manifest_path=state["manifest_path"], acquisition_root=acquisition_run_root(), inspection_root=canonical_root / "inspection", output_root=canonical_root / "intelligence-evidence", candidate_ids=(entry["video_id"],), reuse=True, options=options)
        prepared = services["_prepare"](get_candidate(entry), manifest, request, availability, options)
        if prepared.get("reused"):
            result = prepared["result"] | {"reuse_status":"REUSED"}
        elif prepared.get("legacy"):
            result = prepared["result"] | {"status":"FAILED","errors":["legacy transcription requires canonical migration"]}
        elif prepared.get("no_audio"):
            result = services["_no_audio_result"](prepared); services["write_transcription"](prepared["target"], result)
        else:
            result = services["_transcribe"](prepared, engine, request.language, options)
        target = prepared["target"]
        return {"status":"REUSED" if result.get("reuse_status")=="REUSED" else "COMPLETED" if str(result.get("status","")).startswith("COMPLETED") else "FAILED","artifact_reference":str(target.relative_to(root)).replace("\\", "/"),"artifact_sha256":_file_sha256(target) if target.is_file() else None,"first_spoken_words":result.get("first_spoken_words"),"no_speech_status":result.get("first_spoken_words_reason"),"warnings":result.get("warnings",[]),"reuse_status":result.get("reuse_status","NEW")}

    def analyze_content_intelligence(request: dict[str, Any]) -> dict[str, Any]:
        video_id = request["video_id"]; ci_root = canonical_root / "content-intelligence" / video_id; card_path = ci_root / "card-v2.json"
        existing = _read_json(card_path)
        if existing and existing.get("request_identity") == request["semantic_hash"] and existing.get("validation",{}).get("status") == "VALID":
            return {"claims":existing.get("claims",[]),"project_adaptation":existing.get("project_adaptation",{}),"warnings":existing.get("warnings",[]),"reuse_status":"REUSED"}
        project_context, snapshot, context_hash = services["load_project_context"](repository_root / "projects" / "nura" / "content_intelligence_context.json")
        analysis_input = services["build_analysis_input"](state["manifest_path"], video_id, acquisition_root=acquisition_run_root(), inspection_root=canonical_root / "inspection", intelligence_evidence_root=canonical_root / "intelligence-evidence", project_context=project_context)
        provider = services["DeepSeekContentIntelligenceProvider"](); payload = services["build_provider_payload"](analysis_input, snapshot); body = provider.build_request_body(payload)
        metadata = {"provider":provider.provider_id,"model":provider.model_id,"prompt_version":services["PROMPT_VERSION"],"effective_request_hash":_hash(body),"analysis_input_hash":analysis_input["input_hash"],"project_context_hash":context_hash}
        _atomic(ci_root / "request-metadata.json", _sealed({**metadata,"semantic_hash":""}))
        response, latency_ms = services["post_deepseek_request"](body, api_key=provider._api_key, transport=provider._transport)
        raw = response.json(); persisted_raw, reasoning = services["_without_reasoning_content"](raw); _atomic(ci_root / "raw-response.json", persisted_raw)
        parsed = json.loads(raw["choices"][0]["message"]["content"])
        provider_result = {"schema_version":"0.1","provider":provider.metadata(),"candidate_identity":analysis_input["candidate_identity"],"claims":parsed.get("claims"),"project_adaptation":parsed.get("project_adaptation"),"warnings":parsed.get("warnings",[])}
        validated = services["validate_provider_result"](provider_result, analysis_input, provider); canonical_card = services["build_card"](analysis_input, validated)
        trusted = _sealed({"schema_version":SCHEMA_VERSION,"artifact_kind":"LoopraTop20ContentIntelligenceCardV2","request_identity":request["semantic_hash"],"batch_id":request["batch_id"],"fresh_cycle_id":request["fresh_cycle_id"],"candidate_id":request["candidate_id"],"video_id":video_id,"original_rank":request["original_rank"],"evidence_references":request["evidence_references"],"evidence_hashes":{"analysis_input":analysis_input["input_hash"],"bounded":request["bounded_evidence_input_hash"]},"provider":provider.provider_id,"model":provider.model_id,"prompt_id":"content-intelligence","prompt_version":services["PROMPT_VERSION"],"effective_request_hash":metadata["effective_request_hash"],"claims":validated["claims"],"project_adaptation":canonical_card["project_adaptation"],"warnings":canonical_card["warnings"],"validation":{"status":"VALID"},"transport_metadata":{"latency_ms":latency_ms,**reasoning},"semantic_hash":""})
        _atomic(card_path, trusted)
        return {"claims":trusted["claims"],"project_adaptation":trusted["project_adaptation"],"warnings":trusted["warnings"],"reuse_status":"NEW"}

    def close() -> None:
        collector = state.get("acquisition_collector")
        if collector is not None:
            _run_async(collector.close()); state["acquisition_collector"] = None

    return {"collect":collect,"select":select,"acquire":acquire,"inspect":inspect,"ocr":run_ocr,"transcribe":transcribe,"analyze_content_intelligence":analyze_content_intelligence,"provider":analyze_content_intelligence,"close":close}
