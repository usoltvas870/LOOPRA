"""Stage 5M offline, renderer-neutral NURA production asset handoff.

This module never calls a provider or renderer.  It turns a verified Stage 5L
bridge plus an explicit human decision into immutable, portable asset and
handoff records.  Discovery deliberately does not imply selection.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

from nura_script_episode_bridge import NuraScriptEpisodeBridgeError, hash_payload


ASSET_PROFILE_SCHEMA_VERSION = "0.1"
HANDOFF_SCHEMA_VERSION = "0.1"
REFERENCE_PROFILE_SCHEMA_VERSION = "0.2"
MANUAL_HANDOFF_SCHEMA_VERSION = "0.2"
CANDIDATE_MANIFEST_SCHEMA_VERSION = "0.1"
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
AUDIO_TYPES = {".wav": "audio/wav", ".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".aac": "audio/aac", ".ogg": "audio/ogg", ".flac": "audio/flac"}
SECRET_FIELD = re.compile(r"(token|secret|password|authorization|api[_-]?key)", re.I)


class NuraProductionAssetHandoffError(ValueError):
    pass


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_reference(reference: str) -> bool:
    value = reference.replace("\\", "/")
    return bool(value) and not Path(value).is_absolute() and not re.match(r"^[A-Za-z]:", value) and ".." not in Path(value).parts and not value.startswith("//")


def _atomic(path: Path, value: dict[str, Any]) -> str:
    text = _json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise NuraProductionAssetHandoffError("CONFLICTING_FINALIZED_ARTIFACT")
        return "REUSED"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    try:
        os.link(temporary, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text:
            raise NuraProductionAssetHandoffError("CONFLICTING_FINALIZED_ARTIFACT")
    finally:
        temporary.unlink(missing_ok=True)
    return "COMPLETED"


def materialize_selected_asset(*, source: Path, output_root: Path, category: str) -> tuple[Path, str, str]:
    """Copy exact owner-selected bytes into ignored project-scoped storage."""
    source = Path(source)
    if category not in {"avatar", "voice"} or not source.is_file() or source.stat().st_size == 0:
        raise NuraProductionAssetHandoffError("SELECTED_ASSET_MISSING")
    extension = source.suffix.lower()
    if extension not in (IMAGE_TYPES if category == "avatar" else AUDIO_TYPES):
        raise NuraProductionAssetHandoffError("UNSUPPORTED_SELECTED_ASSET_TYPE")
    content_hash = _sha256(source)
    reference = f"assets/nura/{category}/{content_hash}{extension}"
    destination = Path(output_root) / reference
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if _sha256(destination) != content_hash:
            raise NuraProductionAssetHandoffError("SELECTED_ASSET_HASH_CONFLICT")
        return destination, reference, "REUSED"
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        shutil.copyfile(source, temporary)
        if _sha256(temporary) != content_hash:
            raise NuraProductionAssetHandoffError("SELECTED_ASSET_COPY_HASH_MISMATCH")
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination, reference, "COPIED"


def load_bridge(path: Path) -> dict[str, Any]:
    try:
        bridge = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise NuraProductionAssetHandoffError("STAGE_5L_BRIDGE_MISSING_OR_INVALID") from error
    if not isinstance(bridge, dict) or bridge.get("content_hash") != hash_payload({k: v for k, v in bridge.items() if k != "content_hash"}):
        raise NuraProductionAssetHandoffError("STAGE_5L_BRIDGE_HASH_MISMATCH")
    if (bridge.get("artifact_kind"), bridge.get("original_rank"), bridge.get("script_format"), bridge.get("language")) != ("nura_script_to_production_bridge", 1, "TALKING_GUIDE", "ru"):
        raise NuraProductionAssetHandoffError("UNSUPPORTED_STAGE_5L_BRIDGE")
    if bridge.get("character_avatar_requirement", {}).get("character_id") != "nura" or bridge.get("production_input_ready") is not True:
        raise NuraProductionAssetHandoffError("STAGE_5L_IDENTITY_MISMATCH")
    if bridge.get("music", {}).get("role") != "SECONDARY_OPTIONAL" or bridge.get("production_execution_ready") is not False:
        raise NuraProductionAssetHandoffError("STAGE_5L_READINESS_MISMATCH")
    return bridge


def inspect_candidate(*, path: Path, category: str, reference: str, provenance: str = "UNKNOWN_PROVENANCE") -> dict[str, Any]:
    path = Path(path)
    extension = path.suffix.lower()
    types = IMAGE_TYPES if category == "avatar" else AUDIO_TYPES
    if category not in {"avatar", "voice"} or extension not in types or not path.is_file() or path.stat().st_size == 0:
        raise NuraProductionAssetHandoffError("INVALID_ASSET_CANDIDATE")
    candidate: dict[str, Any] = {"candidate_id": f"nura-{category}-{_sha256(path)[:16]}", "category": category, "reference": reference, "media_type": types[extension], "size_bytes": path.stat().st_size, "sha256": _sha256(path), "provenance": provenance, "approval_status": "UNCONFIRMED", "technical_validation": "VALID", "limitations": ["HUMAN_SELECTION_REQUIRED"]}
    if category == "avatar":
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
                candidate["image"] = {"width": width, "height": height, "aspect_ratio": f"{width}:{height}", "has_alpha": "A" in image.getbands()}
        except (OSError, UnidentifiedImageError) as error:
            raise NuraProductionAssetHandoffError("UNREADABLE_IMAGE") from error
    else:
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,codec_type,channels,sample_rate:format=duration", "-of", "json", str(path)], capture_output=True, text=True, check=False)
        try:
            data = json.loads(probe.stdout)
            stream = next(item for item in data.get("streams", []) if item.get("codec_type") == "audio")
            duration = float(data.get("format", {}).get("duration"))
            if duration <= 0:
                raise ValueError
        except (json.JSONDecodeError, StopIteration, TypeError, ValueError) as error:
            raise NuraProductionAssetHandoffError("UNREADABLE_AUDIO") from error
        candidate["audio"] = {"codec": stream.get("codec_name"), "channels": stream.get("channels"), "sample_rate": stream.get("sample_rate"), "duration_sec": duration}
    return candidate


def build_candidate_manifest(*, bridge: dict[str, Any], avatar_paths: list[tuple[Path, str]], voice_paths: list[tuple[Path, str]]) -> dict[str, Any]:
    candidates = []
    for category, values in (("avatar", avatar_paths), ("voice", voice_paths)):
        for path, reference in values:
            try:
                candidates.append(inspect_candidate(path=path, category=category, reference=reference))
            except NuraProductionAssetHandoffError:
                continue
    unique = {item["sha256"]: item for item in candidates}
    manifest = {"schema_version": CANDIDATE_MANIFEST_SCHEMA_VERSION, "artifact_kind": "nura_production_asset_candidate_manifest", "project_id": "nura", "character_id": "nura", "candidate_identity": bridge["candidate_identity"], "original_rank": 1, "production_class": "single_speaker_talking_avatar_vertical_video", "bridge_hash": bridge["content_hash"], "candidates": sorted(unique.values(), key=lambda item: (item["category"], item["candidate_id"]))}
    manifest["content_hash"] = hash_payload(manifest)
    return manifest


def selection_template(manifest: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version": "0.1", "artifact_kind": "nura_human_production_asset_selection", "project_id": "nura", "manifest_hash": manifest["content_hash"], "avatar_decision": "NEEDS_FURTHER_REVIEW", "avatar_candidate_id": None, "voice_decision": "NEEDS_FURTHER_REVIEW", "voice_candidate_id": None, "human_confirmation": False, "approval_reference": None}


def _selected(manifest: dict[str, Any], selection: dict[str, Any], category: str) -> dict[str, Any]:
    if selection.get("human_confirmation") is not True or not isinstance(selection.get("approval_reference"), str) or not selection["approval_reference"]:
        raise NuraProductionAssetHandoffError("HUMAN_APPROVAL_REQUIRED")
    expected = "SELECTED" if category == "avatar" else "SELECTED_LOCAL_AUDIO"
    if selection.get(f"{category}_decision") != expected:
        raise NuraProductionAssetHandoffError(f"{category.upper()}_NOT_SELECTED")
    candidate_id = selection.get(f"{category}_candidate_id")
    matches = [candidate for candidate in manifest["candidates"] if candidate["category"] == category and candidate["candidate_id"] == candidate_id]
    if len(matches) != 1:
        raise NuraProductionAssetHandoffError("SELECTED_CANDIDATE_NOT_FOUND")
    return matches[0]


def _optional_voice(manifest: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any] | None:
    if selection.get("voice_decision") == "NOT_PROVIDED":
        return None
    return _selected(manifest, selection, "voice")


def build_profile_and_handoff(*, bridge: dict[str, Any], manifest: dict[str, Any], selection: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if selection.get("manifest_hash") != manifest.get("content_hash"):
        raise NuraProductionAssetHandoffError("SELECTION_MANIFEST_HASH_MISMATCH")
    avatar, voice = _selected(manifest, selection, "avatar"), _selected(manifest, selection, "voice")
    for candidate in (avatar, voice):
        if not _safe_reference(candidate["reference"]):
            raise NuraProductionAssetHandoffError("UNSAFE_CANONICAL_ASSET_REFERENCE")
    profile = {"schema_version": ASSET_PROFILE_SCHEMA_VERSION, "artifact_kind": "nura_production_asset_profile", "project_id": "nura", "character_id": "nura", "production_class": manifest["production_class"], "avatar": {"status": "SELECTED", "asset_id": avatar["candidate_id"], "reference": avatar["reference"], "sha256": avatar["sha256"], "media_type": avatar["media_type"], "image": avatar["image"], "approval_reference": selection["approval_reference"], "compatibility": "UNVERIFIED"}, "voice": {"status": "SELECTED", "reference_type": "LOCAL_AUDIO_REFERENCE", "asset_id": voice["candidate_id"], "reference": voice["reference"], "sha256": voice["sha256"], "media_type": voice["media_type"], "language": "ru", "approval_reference": selection["approval_reference"]}, "unresolved_requirements": ["RENDERER_COMPATIBILITY", "AUDIO_DURATION", "SUBTITLE_TIMING_ALIGNMENT"], "safety": {"canonical_references": "PROJECT_RELATIVE", "contains_credentials": False}, "reuse": {"source_manifest_hash": manifest["content_hash"]}}
    profile["profile_id"] = "nura-production-assets-" + hash_payload(profile)[:12]
    profile["content_hash"] = hash_payload(profile)
    handoff = {"schema_version": HANDOFF_SCHEMA_VERSION, "artifact_kind": "nura_external_renderer_handoff", "handoff_id": "nura-renderer-handoff-" + hash_payload({"bridge": bridge["content_hash"], "profile": profile["content_hash"]})[:12], "project_id": "nura", "character_id": "nura", "production_class": manifest["production_class"], "bridge": {"bridge_id": bridge["bridge_id"], "content_hash": bridge["content_hash"]}, "asset_profile": {"profile_id": profile["profile_id"], "content_hash": profile["content_hash"]}, "script": {"text": bridge["spoken_script"]["text"], "sha256": hashlib.sha256(bridge["spoken_script"]["text"].encode("utf-8")).hexdigest(), "language": "ru"}, "subtitle_source": bridge["subtitle_source"], "timing": bridge["timing"], "music": bridge["music"], "renderer": {"assignment": "UNASSIGNED", "verification": "UNVERIFIED"}, "required_capabilities": ["talking_avatar_image_input", "voice_reference_input", "russian_script_input", "vertical_9_16_output", "subtitle_timing_compatibility"], "production_execution_ready": False}
    handoff["content_hash"] = hash_payload(handoff)
    return profile, handoff


def load_finalized_artifact(path: Path, artifact_kind: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise NuraProductionAssetHandoffError("LEGACY_ARTIFACT_MISSING_OR_INVALID") from error
    if not isinstance(value, dict) or value.get("artifact_kind") != artifact_kind:
        raise NuraProductionAssetHandoffError("LEGACY_ARTIFACT_KIND_MISMATCH")
    if value.get("content_hash") != hash_payload({key: item for key, item in value.items() if key != "content_hash"}):
        raise NuraProductionAssetHandoffError("LEGACY_ARTIFACT_HASH_MISMATCH")
    return value


def build_manual_reference_profile_and_handoff(*, bridge: dict[str, Any], manifest: dict[str, Any], selection: dict[str, Any], legacy_profile: dict[str, Any], legacy_handoff: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Correct legacy asset semantics without changing legacy immutable records."""
    if legacy_profile.get("artifact_kind") != "nura_production_asset_profile" or legacy_handoff.get("artifact_kind") != "nura_external_renderer_handoff":
        raise NuraProductionAssetHandoffError("LEGACY_ARTIFACT_KIND_MISMATCH")
    avatar, voice = _selected(manifest, selection, "avatar"), _optional_voice(manifest, selection)
    for candidate in (candidate for candidate in (avatar, voice) if candidate is not None):
        if not _safe_reference(candidate["reference"]):
            raise NuraProductionAssetHandoffError("UNSAFE_CANONICAL_ASSET_REFERENCE")
    legacy = {"profile_id": legacy_profile["profile_id"], "profile_hash": legacy_profile["content_hash"], "handoff_id": legacy_handoff["handoff_id"], "handoff_hash": legacy_handoff["content_hash"]}
    voice_reference = {"status": "READY", "role": "OPTIONAL_VOICE_REFERENCE", "optional": True, "generated_voice_track": False, "renderer_input_required": False, "automatically_transferred_to_renderer": False, "operator_selects_heygen_voice_manually": True, "asset_id": voice["candidate_id"], "reference": voice["reference"], "sha256": voice["sha256"], "media_type": voice["media_type"], "audio": voice["audio"], "language": "ru", "approval_reference": selection["approval_reference"]} if voice else {"status": "NOT_PROVIDED", "role": "OPTIONAL_VOICE_REFERENCE", "optional": True, "generated_voice_track": False, "renderer_input_required": False, "automatically_transferred_to_renderer": False, "operator_selects_heygen_voice_manually": True}
    profile = {"schema_version": REFERENCE_PROFILE_SCHEMA_VERSION, "artifact_kind": "nura_production_reference_profile", "project_id": "nura", "character_id": "nura", "production_class": manifest["production_class"], "visual_identity_reference": {"status": "READY", "role": "VISUAL_IDENTITY_REFERENCE", "usage": "IMAGE_GENERATION_PROMPT_REFERENCE", "per_episode_scene_asset": False, "renderer_input_required": False, "automatically_transferred_to_renderer": False, "asset_id": avatar["candidate_id"], "reference": avatar["reference"], "sha256": avatar["sha256"], "media_type": avatar["media_type"], "image": avatar["image"], "approval_reference": selection["approval_reference"], "source_bytes_immutable": True}, "voice_reference": voice_reference, "readiness": {"reference_profile_ready": True, "script_ready": True, "scene_prompt_package_ready": False, "per_episode_scene_images_ready": False, "voice_selection_instruction_ready": True, "generated_voice_track_ready": False, "manual_heygen_handoff_ready": False, "automated_renderer_handoff_ready": False, "production_execution_ready": False}, "legacy_provenance": legacy, "unresolved_requirements": ["SCENE_PROMPT_PACKAGE", "EXTERNAL_SCENE_IMAGE_GENERATION", "MANUAL_SCENE_IMAGE_SELECTION", "MANUAL_HEYGEN_UPLOAD", "MANUAL_HEYGEN_VOICE_SELECTION", "FINAL_AUDIO_DURATION", "SUBTITLE_TIMING_ALIGNMENT"], "safety": {"canonical_references": "PROJECT_RELATIVE", "contains_credentials": False}}
    profile["profile_id"] = "nura-production-references-" + hash_payload(profile)[:12]
    profile["content_hash"] = hash_payload(profile)
    handoff = {"schema_version": MANUAL_HANDOFF_SCHEMA_VERSION, "artifact_kind": "nura_manual_production_reference_handoff", "handoff_id": "nura-manual-production-handoff-" + hash_payload({"bridge": bridge["content_hash"], "profile": profile["content_hash"]})[:12], "project_id": "nura", "character_id": "nura", "production_class": manifest["production_class"], "bridge": {"bridge_id": bridge["bridge_id"], "content_hash": bridge["content_hash"]}, "reference_profile": {"profile_id": profile["profile_id"], "content_hash": profile["content_hash"]}, "legacy_provenance": legacy, "script": {"text": bridge["spoken_script"]["text"], "sha256": hashlib.sha256(bridge["spoken_script"]["text"].encode("utf-8")).hexdigest(), "language": "ru"}, "subtitle_source": bridge["subtitle_source"], "timing": bridge["timing"], "music": bridge["music"], "visual_identity_reference": profile["visual_identity_reference"], "voice_reference": profile["voice_reference"], "manual_workflow": {"scene_prompt_package_created": False, "per_scene_images_created": False, "generate_images_externally": True, "operator_selects_scene_images": True, "operator_uploads_images_to_heygen": True, "operator_selects_heygen_voice": True, "direct_heygen_transfer": False, "automated_heygen_integration": False}, "renderer": {"assignment": "UNASSIGNED", "verification": "UNVERIFIED", "automated_adapter_required_for_loopra_0_5": False}, "production_execution_ready": False}
    handoff["content_hash"] = hash_payload(handoff)
    return profile, handoff


def persist_contract(*, output_root: Path, manifest: dict[str, Any], selection: dict[str, Any] | None = None, bridge: dict[str, Any] | None = None) -> dict[str, Any]:
    result = {"candidate_manifest": _atomic(Path(output_root) / manifest["content_hash"] / "candidate_manifest.json", manifest), "selection_required": selection is None, "provider_called": False, "renderer_called": False, "network_calls": 0, "credentials_required": False}
    if selection is None:
        result["selection_template"] = _atomic(Path(output_root) / manifest["content_hash"] / "human_selection.json", selection_template(manifest))
        return result
    if bridge is None:
        raise NuraProductionAssetHandoffError("BRIDGE_REQUIRED_FOR_SELECTION")
    profile, handoff = build_profile_and_handoff(bridge=bridge, manifest=manifest, selection=selection)
    result["selection"] = _atomic(Path(output_root) / manifest["content_hash"] / "human_selection.json", selection)
    result["profile"] = _atomic(Path(output_root) / profile["content_hash"] / "production_asset_profile.json", profile)
    result["handoff"] = _atomic(Path(output_root) / handoff["content_hash"] / "external_renderer_handoff.json", handoff)
    result.update({"selection_required": False, "profile_id": profile["profile_id"], "handoff_id": handoff["handoff_id"], "production_execution_ready": False})
    return result


def persist_manual_reference_contract(*, output_root: Path, bridge: dict[str, Any], manifest: dict[str, Any], selection: dict[str, Any], legacy_profile: dict[str, Any], legacy_handoff: dict[str, Any]) -> dict[str, Any]:
    profile, handoff = build_manual_reference_profile_and_handoff(bridge=bridge, manifest=manifest, selection=selection, legacy_profile=legacy_profile, legacy_handoff=legacy_handoff)
    return {"profile": _atomic(Path(output_root) / profile["content_hash"] / "production_reference_profile.json", profile), "handoff": _atomic(Path(output_root) / handoff["content_hash"] / "manual_production_reference_handoff.json", handoff), "profile_id": profile["profile_id"], "profile_hash": profile["content_hash"], "handoff_id": handoff["handoff_id"], "handoff_hash": handoff["content_hash"], "provider_called": False, "renderer_called": False, "image_generator_called": False, "network_calls": 0, "credentials_required": False, "production_execution_ready": False}
