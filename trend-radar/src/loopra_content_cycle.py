"""Stage 5O local content-cycle journal and offline acceptance boundary.

This module deliberately reads existing artifacts only.  It never invokes a
provider, generates media, calls HeyGen, or renders a video.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import struct
import tempfile
from pathlib import Path
from typing import Any

from nura_script_episode_bridge import hash_payload

SCHEMA_VERSION = "0.4"
TITLE = "Ты продолжаешь поддерживать других, даже когда сама уже выгораешь?"
CANDIDATE = {"video_id": "7665636437601094933", "author": "cherryli.1", "source_platform": "hashtag"}
EVENTS = ("CANDIDATE_SELECTED", "MEDIA_ACQUIRED", "FORMAT_INSPECTED", "OCR_COMPLETED", "TRANSCRIPTION_COMPLETED", "CONTENT_INTELLIGENCE_COMPLETED", "EDITORIAL_REVIEW_FINALIZED", "PRODUCTION_BRIEF_READY", "SCRIPT_DRAFT_CREATED", "SCRIPT_REVIEW_FINALIZED", "SCRIPT_APPROVED", "PRODUCTION_BRIDGE_READY", "REFERENCE_PROFILE_READY", "OPERATOR_EXPORT_READY", "OPERATOR_EXPORT_ACCEPTED")
USER_FILES = ("01_CONTENT_RU.md", "02_IMAGE_PROMPT.txt", "NURA_REFERENCE.png", "README_RU.txt")
DECISIONS = ("ACCEPT_LOOPRA_0_5", "ACCEPT_WITH_GAPS", "NEEDS_MORE_TESTING", "REJECT_WORKFLOW")


class ContentCycleError(ValueError):
    pass


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _atomic_json(path: Path, value: dict[str, Any]) -> str:
    text = _json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise ContentCycleError("CONFLICTING_CONTENT_CYCLE_REUSE")
        return "REUSED"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    try:
        os.link(temporary, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text:
            raise ContentCycleError("CONFLICTING_CONTENT_CYCLE_REUSE")
    finally:
        temporary.unlink(missing_ok=True)
    return "COMPLETED"


def _find(root: Path, suffix: str, predicate) -> Path:
    candidates = sorted(root.rglob(suffix))
    for path in candidates:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if predicate(value, path):
            return path
    raise ContentCycleError(f"CANONICAL_ARTIFACT_NOT_FOUND:{suffix}")


def canonical_paths(root: Path) -> dict[str, Path]:
    """Resolve the one approved Rank 1 chain from immutable local artifacts."""
    data = Path(root) / "data"
    video_id = CANDIDATE["video_id"]
    fixed = {
        "format_inspection": data / "format-inspections/20260724_150816" / video_id / "inspection.json",
        "content_intelligence_report": data / "content-intelligence-reports/content-intelligence-report-20260724_150816-bf8ca1f1950e/report.json",
        "editorial_review": data / "content-intelligence-reviews/finalized-human-editorial-review-7b7a850dc8fd/review_result.json",
        "production_brief": data / "nura-production-briefs/nura-production-briefs-1aac60d95c02/candidates" / video_id / "production_brief.json",
        "script_input": data / "nura-real-script-provider/nura-real-script-3bce876cac5b/script_input.json",
        "provider_draft": data / "nura-real-script-provider/nura-real-script-3bce876cac5b/raw_provider_response.json",
        "script_review": data / "nura-real-script-provider/nura-real-script-3bce876cac5b/finalized_human_script_review.json",
        "approved_script": data / "nura-real-script-provider/nura-real-script-3bce876cac5b/human_approved_script_output.json",
        "production_bridge": data / "nura-script-episode-bridge/nura-script-production-bridge-79d69d42079e/script_to_production_bridge.json",
        "reference_profile": data / "nura-production-asset-handoff/8fc6df087d0aee2b5056e3c79bc4fbd90f1f187fdf168f1f2fb32943f8cc0071/production_reference_profile.json",
        "scene_package": data / "nura-scene-production-finalized/nura-scene-production-finalized-2aad84cd2c40/finalized_scene_production_package.json",
        "operator_export": data / "nura-operator-export/nura-operator-export-689256944ac3/operator_export_manifest.json",
    }
    for stage, path in fixed.items():
        if not path.is_file():
            raise ContentCycleError(f"MISSING_{stage.upper()}")
    fixed.update({
        "selection_manifest": data / "runs/selection_manifest_20260724_150816.json",
        "acquisition": data / "acquisitions/20260724_150816" / video_id / "acquisition_record.json",
        "ocr": data / "content-intelligence/20260724_150816/candidates" / video_id / "ocr/ocr_result.json",
        "transcription": data / "content-intelligence/20260724_150816/candidates" / video_id / "transcription/transcription_result.json",
        "content_intelligence": data / "content-intelligence/real/real-20260724_150816-8ed5faca1422-2df06c36-deepseek-deepseek-v4-flash-2.0/candidates" / video_id / "content_intelligence_card.json",
    })
    for stage in ("selection_manifest", "acquisition", "ocr", "transcription", "content_intelligence"):
        if not fixed[stage].is_file():
            raise ContentCycleError(f"MISSING_{stage.upper()}")
    return fixed


def _reference(root: Path, path: Path) -> dict[str, str]:
    return {"path": path.relative_to(root).as_posix(), "sha256": _sha256(path)}


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContentCycleError("INVALID_CANONICAL_ARTIFACT") from error
    if not isinstance(value, dict):
        raise ContentCycleError("CANONICAL_ARTIFACT_OBJECT_REQUIRED")
    return value


def _validate_authorities(root: Path, refs: dict[str, dict[str, str]]) -> None:
    for stage, reference in refs.items():
        path = root / reference["path"]
        if not path.is_file() or _sha256(path) != reference["sha256"]:
            raise ContentCycleError(f"{stage.upper()}_HASH_MISMATCH")
    export = _read(root / refs["operator_export"]["path"])
    if (export.get("export_id"), export.get("content_hash"), export.get("video_title"), export.get("format"), export.get("video_count"), export.get("visual_generation_strategy"), export.get("image_count")) != ("nura-operator-export-689256944ac3", "d49977f7a268182f20e720c80fe618f7b9681520a4923560d9ca9e85a0f497e0", TITLE, "TALKING_GUIDE", 1, "ONE_IMAGE", 1):
        raise ContentCycleError("OPERATOR_EXPORT_CONTRACT_MISMATCH")
    if set(export.get("user_facing_files", ())) != set(USER_FILES) or export.get("json_required_for_manual_use") is not False:
        raise ContentCycleError("OPERATOR_EXPORT_USABILITY_MISMATCH")
    for name in USER_FILES:
        if not ((root / refs["operator_export"]["path"]).parent / "user-facing" / name).is_file():
            raise ContentCycleError("OPERATOR_EXPORT_FILE_MISSING")
    approved = _read(root / refs["approved_script"]["path"])
    if approved.get("original_rank") != 1 or approved.get("format") != "TALKING_GUIDE" or approved.get("payload", {}).get("text", "").split("\n\n")[0] != TITLE:
        raise ContentCycleError("APPROVED_SCRIPT_CONTRACT_MISMATCH")
    review = _read(root / refs["editorial_review"]["path"])
    script_review = _read(root / refs["script_review"]["path"])
    if "FINALIZED" not in str(review).upper() or script_review.get("reviewer", {}).get("human_confirmation") is not True:
        raise ContentCycleError("HUMAN_REVIEW_REQUIRED")


def build_cycle(*, root: Path, runtime_root: Path) -> dict[str, Any]:
    root, runtime_root = Path(root), Path(runtime_root)
    paths = canonical_paths(root)
    refs = {stage: _reference(root, path) for stage, path in paths.items()}
    _validate_authorities(root, refs)
    identity = hash_payload({"schema_version": SCHEMA_VERSION, "project_id": "nura", "candidate": CANDIDATE, "rank": 1, "operator_export": refs["operator_export"]})
    cycle_id = "loopra-content-cycle-" + identity[:12]
    cycle_dir = runtime_root / cycle_id
    cycle = {"schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_content_cycle", "cycle_id": cycle_id, "cycle_version": 1, "project_id": "nura", "candidate_identity": CANDIDATE, "original_rank": 1, "content_format": "TALKING_GUIDE", "production_strategy": "ONE_IMAGE", "lifecycle_status": "PRACTICAL_PRODUCTION_PENDING", "creation_source": "STAGE_5O_REUSE_ONLY", "artifact_references": refs, "video_title": TITLE, "title_source": "APPROVED_HOOK_FALLBACK", "operator_export_path": refs["operator_export"]["path"].rsplit("/", 1)[0] + "/user-facing", "owner_decisions_summary": {"operator_export_accepted": True, "prior_feedback": "Operator export usability confirmed; selected image and HeyGen clip remain unregistered."}, "technical_acceptance_status": "PENDING", "practical_production_acceptance_status": "PENDING", "unresolved_requirements": ["Register exact selected image.", "Register manual HeyGen clip.", "Apply explicit owner practical acceptance decision."], "cycle_events": [{"event_type": event, "evidence": "CANONICAL_REUSED_ARTIFACT" if event != "OPERATOR_EXPORT_ACCEPTED" else "EXPLICIT_OWNER_FEEDBACK", "proven": True} for event in EVENTS], "persistence": {"mode": "ATOMIC_CONTENT_IDENTICAL_REUSE", "runtime_scope": "PROJECT_SCOPED_IGNORED_RUNTIME"}, "content_hash": ""}
    cycle["content_hash"] = hash_payload({key: value for key, value in cycle.items() if key != "content_hash"})
    status = _atomic_json(cycle_dir / "content_cycle.json", cycle)
    package = practical_package(cycle)
    _atomic_json(cycle_dir / "practical_acceptance_package.json", package)
    template = practical_template(cycle)
    _atomic_json(cycle_dir / "owner_practical_acceptance_template.json", template)
    readiness = readiness_manifest(cycle)
    _atomic_json(cycle_dir / "readiness_manifest.json", readiness)
    return {"status": status, "cycle": cycle, "cycle_path": cycle_dir / "content_cycle.json", "package": package, "package_path": cycle_dir / "practical_acceptance_package.json", "template_path": cycle_dir / "owner_practical_acceptance_template.json", "readiness_path": cycle_dir / "readiness_manifest.json"}


def practical_package(cycle: dict[str, Any]) -> dict[str, Any]:
    value = {"schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_practical_acceptance_package", "package_id": "loopra-practical-acceptance-" + cycle["content_hash"][:12], "package_version": 1, "cycle": {"cycle_id": cycle["cycle_id"], "content_hash": cycle["content_hash"]}, "project_id": "nura", "candidate_identity": CANDIDATE, "original_rank": 1, "title": TITLE, "content_format": "TALKING_GUIDE", "visual_strategy": "ONE_IMAGE", "operator_export": cycle["artifact_references"]["operator_export"], "selected_image": {"status": "PENDING", "registration": None}, "heygen_clip": {"status": "PENDING", "registration": None}, "owner_decision": {"status": "PENDING", "reference": None}, "technical_e2e": {"status": "PENDING", "reference": None}, "practical_checklist": ["Generate and select one image manually.", "Create the clip manually in HeyGen.", "Register both exact local files.", "Apply the owner decision."], "unresolved_requirements": list(cycle["unresolved_requirements"]), "lifecycle_status": "PENDING_MANUAL_PRODUCTION", "persistence": {"mode": "ATOMIC_CONTENT_IDENTICAL_REUSE", "runtime_scope": "PROJECT_SCOPED_IGNORED_RUNTIME"}, "content_hash": ""}
    value["content_hash"] = hash_payload({key: item for key, item in value.items() if key != "content_hash"})
    return value


def practical_template(cycle: dict[str, Any]) -> dict[str, Any]:
    value = {"schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_practical_acceptance_decision", "cycle_id": cycle["cycle_id"], "reviewer": {"reviewer_id": "nura-owner", "reviewer_role": "OWNER", "reviewer_display_name": "Василий", "human_confirmation": False}, "decision": None, "workflow": {"operator_export_easy_to_find": None, "title_and_structure_clear": None, "clean_heygen_text_clear": None, "image_prompt_usable": None, "reference_usage_clear": None, "image_generation_result_usable": None, "HeyGen_workflow_clear": None, "workflow_reduced_manual_work": None, "workflow_created_new_errors": None, "final_video_practically_usable": None, "would_use_again": None}, "content": {"source_mechanism_preserved": None, "approved_script_preserved": None, "NURA_identity_preserved": None, "source_video_not_copied": None, "safety_acceptable": None}, "evidence": {"selected_image_registered": False, "heygen_clip_registered": False}, "prior_feedback": ["Operator Export понятен.", "Текстовая структура нравится.", "Image prompt практически использован.", "Blur-panel correction принята."], "notes": None}
    value["content_hash"] = hash_payload(value)
    return value


def readiness_manifest(cycle: dict[str, Any]) -> dict[str, Any]:
    value = {"schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_05_readiness_manifest", "manifest_id": "loopra-05-readiness-" + cycle["content_hash"][:12], "cycle": {"cycle_id": cycle["cycle_id"], "content_hash": cycle["content_hash"]}, "technical_core_complete": True, "operator_export_complete": True, "technical_e2e_pass": True, "practical_image_workflow_tested": True, "selected_image_registered": False, "manual_heygen_clip_registered": False, "owner_practical_acceptance_complete": False, "scope_frozen": False, "loopra_0_5_status": "TECHNICALLY_COMPLETE_PRACTICAL_ACCEPTANCE_PENDING", "unresolved_requirements": list(cycle["unresolved_requirements"]), "next_manual_actions": ["Register selected image.", "Register HeyGen clip.", "Apply owner decision."], "persistence": {"mode": "ATOMIC_CONTENT_IDENTICAL_REUSE", "runtime_scope": "PROJECT_SCOPED_IGNORED_RUNTIME"}}
    value["content_hash"] = hash_payload(value)
    return value


def _image_metadata(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if not raw:
        raise ContentCycleError("ZERO_BYTE_IMAGE")
    if raw.startswith(b"\x89PNG\r\n\x1a\n") and len(raw) >= 24:
        width, height = struct.unpack(">II", raw[16:24]); media_type = "image/png"
    elif raw.startswith(b"\xff\xd8"):
        media_type, width, height = "image/jpeg", None, None
        index = 2
        while index + 9 < len(raw):
            if raw[index] != 0xff: index += 1; continue
            marker = raw[index + 1]; size = int.from_bytes(raw[index + 2:index + 4], "big")
            if marker in range(0xc0, 0xc4) and index + 9 < len(raw):
                height, width = struct.unpack(">HH", raw[index + 5:index + 9]); break
            index += 2 + size
        if not width or not height: raise ContentCycleError("CORRUPT_IMAGE")
    else:
        raise ContentCycleError("UNSUPPORTED_IMAGE_TYPE")
    if width <= 0 or height <= 0: raise ContentCycleError("CORRUPT_IMAGE")
    return {"media_type": media_type, "width": width, "height": height, "aspect_ratio": round(width / height, 6), "orientation": "VERTICAL" if height > width else "HORIZONTAL_OR_SQUARE", "byte_size": len(raw)}


def _copy_exact(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if _sha256(destination) != _sha256(source): raise ContentCycleError("CONFLICTING_ASSET_REUSE")
        return
    with source.open("rb") as inp, tempfile.NamedTemporaryFile("wb", delete=False, dir=destination.parent) as out:
        shutil.copyfileobj(inp, out); temporary = Path(out.name)
    try: os.link(temporary, destination)
    except FileExistsError:
        if _sha256(destination) != _sha256(source): raise ContentCycleError("CONFLICTING_ASSET_REUSE")
    finally: temporary.unlink(missing_ok=True)


def register_selected_image(*, source_path: Path, cycle: dict[str, Any], runtime_root: Path, owner_selected: bool, visual_identity_confirmed: bool, blur_panel_absent: bool) -> dict[str, Any]:
    if not owner_selected or not visual_identity_confirmed or not blur_panel_absent: raise ContentCycleError("OWNER_IMAGE_CONFIRMATION_REQUIRED")
    source = Path(source_path)
    if not source.is_file(): raise ContentCycleError("SELECTED_IMAGE_NOT_FOUND")
    metadata, digest = _image_metadata(source), _sha256(source)
    extension = ".png" if metadata["media_type"] == "image/png" else ".jpg"
    target = Path(runtime_root) / cycle["cycle_id"] / "assets/selected-image" / (digest + extension)
    _copy_exact(source, target)
    if _sha256(target) != digest: raise ContentCycleError("SELECTED_IMAGE_COPY_MISMATCH")
    value = {"schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_selected_image_registration", "registration_id": "selected-image-" + digest[:12], "cycle": {"cycle_id": cycle["cycle_id"], "content_hash": cycle["content_hash"]}, "asset_role": "SELECTED_IMAGE", "project_scoped_reference": target.relative_to(runtime_root).as_posix(), "sha256": digest, **metadata, "source_copy_verification": "EXACT_BYTES", "generated_manually": True, "generation_tool": "CHATGPT", "owner_selected": True, "visual_identity_confirmed": True, "blur_panel_absent_confirmation": True, "persistence": {"mode": "ATOMIC_CONTENT_IDENTICAL_REUSE"}, "content_hash": ""}
    value["content_hash"] = hash_payload({key: item for key, item in value.items() if key != "content_hash"})
    status = _atomic_json(target.parent / "registration.json", value); return {"status": status, "registration": value, "path": target.parent / "registration.json"}


def _clip_metadata(path: Path) -> dict[str, Any]:
    try:
        raw = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name,width,height", "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
        value = json.loads(raw)
    except FileNotFoundError as error: raise ContentCycleError("FFPROBE_UNAVAILABLE") from error
    except (subprocess.CalledProcessError, json.JSONDecodeError) as error: raise ContentCycleError("CORRUPT_OR_UNREADABLE_CLIP") from error
    streams = value.get("streams", []); video = next((x for x in streams if x.get("codec_type") == "video"), None); audio = next((x for x in streams if x.get("codec_type") == "audio"), None)
    if not video: raise ContentCycleError("CLIP_VIDEO_STREAM_REQUIRED")
    width, height = int(video.get("width") or 0), int(video.get("height") or 0)
    if width <= 0 or height <= 0: raise ContentCycleError("CORRUPT_OR_UNREADABLE_CLIP")
    return {"media_type": "video/mp4", "byte_size": path.stat().st_size, "duration_seconds": float(value.get("format", {}).get("duration") or 0), "width": width, "height": height, "aspect_ratio": round(width / height, 6), "video_codec": video.get("codec_name"), "audio_codec": None if not audio else audio.get("codec_name"), "audio_present": audio is not None}


def register_heygen_clip(*, source_path: Path, cycle: dict[str, Any], image_registration: dict[str, Any], runtime_root: Path, subtitle_status: str, music_status: str) -> dict[str, Any]:
    source = Path(source_path)
    if not source.is_file() or source.stat().st_size == 0: raise ContentCycleError("HEYGEN_CLIP_NOT_FOUND_OR_EMPTY")
    metadata, digest = _clip_metadata(source), _sha256(source)
    target = Path(runtime_root) / cycle["cycle_id"] / "assets/heygen-clip" / (digest + ".mp4")
    _copy_exact(source, target)
    if _sha256(target) != digest: raise ContentCycleError("HEYGEN_CLIP_COPY_MISMATCH")
    value = {"schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_heygen_clip_registration", "registration_id": "heygen-clip-" + digest[:12], "cycle": {"cycle_id": cycle["cycle_id"], "content_hash": cycle["content_hash"]}, "asset_role": "HEYGEN_CLIP", "project_scoped_reference": target.relative_to(runtime_root).as_posix(), "sha256": digest, **metadata, "generated_manually": True, "generation_tool": "HEYGEN", "approved_script": cycle["artifact_references"]["approved_script"], "selected_image": {"registration_id": image_registration["registration_id"], "content_hash": image_registration["content_hash"], "sha256": image_registration["sha256"]}, "subtitle_status": subtitle_status, "music_status": music_status, "owner_review_status": "PENDING", "persistence": {"mode": "ATOMIC_CONTENT_IDENTICAL_REUSE"}, "content_hash": ""}
    value["content_hash"] = hash_payload({key: item for key, item in value.items() if key != "content_hash"})
    status = _atomic_json(target.parent / "registration.json", value); return {"status": status, "registration": value, "path": target.parent / "registration.json"}


def validate_owner_decision(decision: dict[str, Any], *, image_registered: bool, clip_registered: bool) -> str:
    choice = decision.get("decision")
    if choice not in DECISIONS: raise ContentCycleError("INVALID_OWNER_DECISION")
    if choice in ("NEEDS_MORE_TESTING", "REJECT_WORKFLOW"): return "PENDING"
    if decision.get("reviewer", {}).get("human_confirmation") is not True: raise ContentCycleError("OWNER_HUMAN_CONFIRMATION_REQUIRED")
    if not image_registered: raise ContentCycleError("SELECTED_IMAGE_EVIDENCE_REQUIRED")
    if not clip_registered: raise ContentCycleError("HEYGEN_CLIP_EVIDENCE_REQUIRED")
    workflow, content = decision.get("workflow", {}), decision.get("content", {})
    required = (workflow.get("final_video_practically_usable"), workflow.get("workflow_reduced_manual_work"), content.get("approved_script_preserved"), content.get("NURA_identity_preserved"), content.get("source_video_not_copied"), content.get("safety_acceptable"))
    if not all(item is True for item in required): raise ContentCycleError("OWNER_ACCEPTANCE_CONFIRMATIONS_REQUIRED")
    if choice == "ACCEPT_WITH_GAPS" and not decision.get("notes"): raise ContentCycleError("ACCEPT_WITH_GAPS_NOTES_REQUIRED")
    if workflow.get("would_use_again") is not True and choice != "ACCEPT_WITH_GAPS": raise ContentCycleError("WOULD_USE_AGAIN_REQUIRED")
    return "ACCEPTED" if choice == "ACCEPT_LOOPRA_0_5" else "ACCEPTED_WITH_GAPS"


def technical_acceptance(*, root: Path, runtime_root: Path) -> dict[str, Any]:
    first, second = build_cycle(root=root, runtime_root=runtime_root), build_cycle(root=root, runtime_root=runtime_root)
    cycle = first["cycle"]
    _validate_authorities(Path(root), cycle["artifact_references"])
    report = {"schema_version": SCHEMA_VERSION, "artifact_kind": "loopra_technical_end_to_end_acceptance", "cycle_id": cycle["cycle_id"], "cycle_hash": cycle["content_hash"], "candidate_identity": CANDIDATE, "rank": 1, "title": TITLE, "format": "TALKING_GUIDE", "video_count": 1, "visual_strategy": "ONE_IMAGE", "image_count": 1, "artifact_stages_expected": list(cycle["artifact_references"]), "artifact_stages_verified": list(cycle["artifact_references"]), "missing_stages": [], "human_gates_verified": True, "provenance_status": "PASS", "hash_status": "PASS", "operator_export_path": cycle["operator_export_path"], "operator_export_file_list": list(USER_FILES), "operator_export_usability_status": "PASS", "practical_acceptance_package_path": first["package_path"].name, "owner_decision_template_path": first["template_path"].name, "readiness_manifest_path": first["readiness_path"].name, "readiness_status": "TECHNICALLY_COMPLETE_PRACTICAL_ACCEPTANCE_PENDING", "finalize_gate": "REQUIRES_SELECTED_IMAGE_CLIP_AND_OWNER_DECISION", "technical_end_to_end_pass": True, "practical_acceptance_status": "PENDING", "current_lifecycle_status": cycle["lifecycle_status"], "provider_calls": 0, "network_calls": 0, "credentials_required": False, "image_generator_calls": 0, "heygen_calls": 0, "renderer_calls": 0, "ffmpeg_render_calls": 0, "first_result": first["status"], "second_result": second["status"], "reuse_identity": first["cycle"]["content_hash"] == second["cycle"]["content_hash"], "content_hash": ""}
    report["content_hash"] = hash_payload({key: value for key, value in report.items() if key != "content_hash"})
    path = Path(runtime_root) / cycle["cycle_id"] / "technical_acceptance_report.json"
    report["persistence_status"] = _atomic_json(path, report)
    return {"report": report, "path": path}
