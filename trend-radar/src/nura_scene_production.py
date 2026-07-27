"""Stage 5N: bounded scene planning and manual HeyGen handoff for NURA.

This module deliberately produces text-only operator material.  It never
creates media, invokes HeyGen, or assigns a renderer.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import httpx

from content_intelligence_provider import MODEL_ID, ProviderTransportError, post_deepseek_request
from nura_script_episode_bridge import hash_payload

SCHEMA_VERSION = "0.1"
PROVIDER_ID = "deepseek-nura-scene-production"
PROMPT_ID = "nura-scene-production"
PROMPT_VERSION = "1.0"
MAX_PAYLOAD_CHARS = 18_000


class NuraSceneProductionError(ValueError):
    pass


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise NuraSceneProductionError("INVALID_STAGE_5N_INPUT") from error
    if not isinstance(value, dict):
        raise NuraSceneProductionError("STAGE_5N_OBJECT_REQUIRED")
    return value


def _verified(value: dict[str, Any], field: str = "content_hash") -> dict[str, Any]:
    if value.get(field) != hash_payload({key: item for key, item in value.items() if key != field}):
        raise NuraSceneProductionError(f"{field.upper()}_MISMATCH")
    return value


def load_scene_authority(*, bridge_path: Path, profile_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    bridge, profile = _verified(_read(bridge_path)), _verified(_read(profile_path))
    if (bridge.get("artifact_kind"), bridge.get("original_rank"), bridge.get("script_format"), bridge.get("language")) != ("nura_script_to_production_bridge", 1, "TALKING_GUIDE", "ru"):
        raise NuraSceneProductionError("UNSUPPORTED_STAGE_5L_BRIDGE")
    if bridge.get("production_input_ready") is not True:
        raise NuraSceneProductionError("STAGE_5L_NOT_READY")
    if profile.get("artifact_kind") != "nura_production_reference_profile" or profile.get("readiness", {}).get("reference_profile_ready") is not True:
        raise NuraSceneProductionError("STAGE_5M_PROFILE_NOT_READY")
    visual, voice = profile.get("visual_identity_reference", {}), profile.get("voice_reference", {})
    if visual.get("role") != "VISUAL_IDENTITY_REFERENCE" or visual.get("usage") != "IMAGE_GENERATION_PROMPT_REFERENCE" or visual.get("status") != "READY":
        raise NuraSceneProductionError("VISUAL_REFERENCE_NOT_READY")
    if voice.get("role") != "OPTIONAL_VOICE_REFERENCE" or voice.get("status") != "READY" or voice.get("optional") is not True:
        raise NuraSceneProductionError("VOICE_REFERENCE_NOT_READY")
    if profile.get("production_class") != "single_speaker_talking_avatar_vertical_video" or bridge.get("candidate_identity") is None:
        raise NuraSceneProductionError("STAGE_5N_IDENTITY_MISMATCH")
    return bridge, profile


def build_scene_input(*, bridge: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    blocks = bridge.get("spoken_script", {}).get("blocks")
    if not isinstance(blocks, list) or len(blocks) != 5:
        raise NuraSceneProductionError("FIVE_APPROVED_BLOCKS_REQUIRED")
    canonical = [{"block_id": f"block-{item['ordinal']}", "ordinal": item["ordinal"], "kind": item["kind"], "spoken_text": item["text"]} for item in blocks]
    if "\n\n".join(item["spoken_text"] for item in canonical) != bridge["spoken_script"]["text"]:
        raise NuraSceneProductionError("APPROVED_TEXT_ROUND_TRIP_MISMATCH")
    visual = profile["visual_identity_reference"]
    package = {"schema_version": SCHEMA_VERSION, "artifact_kind": "nura_scene_production_input", "project_id": "nura", "candidate_identity": bridge["candidate_identity"], "original_rank": 1, "script_format": "TALKING_GUIDE", "language": "ru", "bridge": {"bridge_id": bridge["bridge_id"], "content_hash": bridge["content_hash"]}, "reference_profile": {"profile_id": profile["profile_id"], "content_hash": profile["content_hash"]}, "approved_script": {"text": bridge["spoken_script"]["text"], "blocks": canonical}, "visual_identity_reference": {key: visual[key] for key in ("reference", "sha256", "role", "usage", "media_type", "image")}, "editorial_context": {"tone": ["calm", "adult", "emotionally safe"], "visual_constraints": ["ordinary believable setting", "small realistic shift", "no diagnosis or promise", "do not imitate a real person"]}, "production_boundary": {"image_generation": "EXTERNAL_OPERATOR_ONLY", "heygen_transfer": False, "renderer_call": False, "voice_generation": False}}
    package["content_hash"] = hash_payload(package)
    package["input_id"] = "nura-scene-input-" + package["content_hash"][:12]
    package["content_hash"] = hash_payload({key: item for key, item in package.items() if key != "content_hash"})
    return package


def build_bounded_provider_request(package: dict[str, Any]) -> dict[str, Any]:
    request = {"schema_version": SCHEMA_VERSION, "scene_input": {"input_id": package["input_id"], "content_hash": package["content_hash"]}, "rank": 1, "format": "TALKING_GUIDE", "language": "ru", "approved_blocks": package["approved_script"]["blocks"], "visual_identity_reference": {key: package["visual_identity_reference"][key] for key in ("sha256", "role", "usage", "media_type", "image")}, "editorial_context": package["editorial_context"], "required_scene_fields": ["source_block_ids", "purpose", "image_prompt", "negative_constraints", "composition_framing", "expression_pose", "background_lighting", "operator_note"]}
    encoded = json.dumps(request, ensure_ascii=False, sort_keys=True, allow_nan=False)
    if len(encoded) > MAX_PAYLOAD_CHARS or any(token in encoded.lower() for token in ("c:\\", "authorization", "api_key", "heygen", ".png", ".mp3")):
        raise NuraSceneProductionError("PROVIDER_PAYLOAD_FORBIDDEN_OR_TOO_LARGE")
    return request


@dataclass(frozen=True)
class ScenePromptContract:
    temperature: float = 0.2
    max_output_tokens: int = 2200
    def messages(self, request: dict[str, Any]) -> list[dict[str, str]]:
        system = "Return JSON only. Plan visual scenes for the supplied approved Russian blocks. Preserve spoken_text exactly by referencing block ids; do not add spoken text. Every scene needs a detailed external image-generation prompt, negative constraints, composition/framing, expression/pose, background/lighting and a Russian operator note. The supplied identity is only a visual reference: do not claim identity cloning, do not generate media, do not mention HeyGen. Use vertical 9:16 talking-avatar compositions and keep scenes realistic, calm and non-clinical."
        schema = {"scenes": [{"source_block_ids": ["block-1"], "purpose": "...", "image_prompt": "...", "negative_constraints": ["..."], "composition_framing": "...", "expression_pose": "...", "background_lighting": "...", "operator_note": "...", "warnings": []}]}
        return [{"role": "system", "content": system}, {"role": "user", "content": json.dumps({"request": request, "output_schema": schema}, ensure_ascii=False, separators=(",", ":"))}]


class SceneProvider(Protocol):
    def generate(self, request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]: ...
    def metadata(self) -> dict[str, Any]: ...


class DeepSeekSceneProvider:
    def __init__(self, api_key: str | None = None, transport: httpx.BaseTransport | None = None) -> None:
        self.api_key, self.transport, self.contract = api_key if api_key is not None else os.getenv("DEEPSEEK_API_KEY"), transport, ScenePromptContract()
    def metadata(self) -> dict[str, Any]:
        return {"provider_id": PROVIDER_ID, "model_id": MODEL_ID, "prompt_id": PROMPT_ID, "prompt_version": PROMPT_VERSION, "configuration": {"response_format": {"type": "json_object"}, "thinking": {"type": "disabled"}, "temperature": self.contract.temperature, "max_tokens": self.contract.max_output_tokens}, "fake": False}
    def generate(self, request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.api_key: raise NuraSceneProductionError("BLOCKED_PROVIDER_CREDENTIALS")
        body = {"model": MODEL_ID, "messages": self.contract.messages(request), "response_format": {"type": "json_object"}, "thinking": {"type": "disabled"}, "temperature": self.contract.temperature, "max_tokens": self.contract.max_output_tokens}
        try: response, latency = post_deepseek_request(body, api_key=self.api_key, transport=self.transport)
        except ProviderTransportError as error: raise NuraSceneProductionError(str(error)) from error
        try: raw = response.json()
        except json.JSONDecodeError: raise NuraSceneProductionError("PROVIDER_NON_JSON_RESPONSE")
        return raw, {"http_status": response.status_code, "latency_ms": latency, "response_hash": hashlib.sha256(response.content).hexdigest(), "request_id": response.headers.get("x-request-id")}


class FakeSceneProvider:
    def metadata(self) -> dict[str, Any]: return {"provider_id": "fake-nura-scene-production", "model_id": "deterministic", "prompt_id": PROMPT_ID, "prompt_version": PROMPT_VERSION, "fake": True}
    def generate(self, request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        scenes = []
        for index, block in enumerate(request["approved_blocks"], 1):
            scenes.append({"source_block_ids": [block["block_id"]], "purpose": block["kind"], "image_prompt": f"Vertical 9:16 realistic portrait scene for a calm Russian talking guide, visual beat {index}; use the supplied NURA visual identity reference for appearance consistency, no text in image.", "negative_constraints": ["no text or captions", "no medical setting", "no identity imitation", "no extra people"], "composition_framing": "vertical 9:16, medium close-up, eye-level camera", "expression_pose": "calm attentive expression, natural seated posture", "background_lighting": "quiet home interior, soft natural window light", "operator_note": "Оператор: сгенерируйте изображение внешним инструментом с каноническим visual identity reference; затем вручную выберите кадр.", "warnings": []})
        return {"scenes": scenes}, {"http_status": 200, "response_hash": "fake", "latency_ms": 0}


def _creative(raw: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        content = raw["choices"][0]["message"]["content"] if "choices" in raw else json.dumps(raw, ensure_ascii=False)
        scenes = json.loads(content)["scenes"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error: raise NuraSceneProductionError("PROVIDER_SCENE_SCHEMA_INVALID") from error
    if not isinstance(scenes, list) or not scenes: raise NuraSceneProductionError("PROVIDER_SCENES_REQUIRED")
    return scenes


def validate_scene_package(*, package: dict[str, Any], input_package: dict[str, Any]) -> None:
    scenes, blocks = package.get("scenes"), input_package["approved_script"]["blocks"]
    if not isinstance(scenes, list) or not scenes: raise NuraSceneProductionError("SCENES_REQUIRED")
    expected, actual = [b["block_id"] for b in blocks], []
    for scene in scenes:
        if not isinstance(scene, dict) or any(not scene.get(key) for key in ("scene_id", "source_block_ids", "purpose", "image_prompt", "negative_constraints", "composition_framing", "expression_pose", "background_lighting", "operator_note")): raise NuraSceneProductionError("INVALID_SCENE_STRUCTURE")
        if not isinstance(scene["source_block_ids"], list) or not isinstance(scene["negative_constraints"], list): raise NuraSceneProductionError("INVALID_SCENE_LIST_FIELDS")
        actual.extend(scene["source_block_ids"])
    if actual != expected: raise NuraSceneProductionError("EXACT_BLOCK_COVERAGE_REQUIRED")
    if package.get("spoken_text_round_trip") != input_package["approved_script"]["text"]: raise NuraSceneProductionError("SPOKEN_TEXT_CHANGED")
    if package.get("content_hash") != hash_payload({key: item for key, item in package.items() if key != "content_hash"}): raise NuraSceneProductionError("SCENE_PACKAGE_HASH_MISMATCH")


def _atomic(path: Path, value: dict[str, Any]) -> str:
    text = _json(value); path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text: raise NuraSceneProductionError("CONFLICTING_SCENE_PACKAGE_REUSE")
        return "REUSED"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as handle: handle.write(text); temporary = Path(handle.name)
    try: os.link(temporary, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text: raise NuraSceneProductionError("CONFLICTING_SCENE_PACKAGE_REUSE")
    finally: temporary.unlink(missing_ok=True)
    return "COMPLETED"


def run_scene_production(*, bridge_path: Path, profile_path: Path, output_root: Path, provider: SceneProvider | None = None, allow_network: bool = False, reuse_only: bool = False) -> dict[str, Any]:
    bridge, profile = load_scene_authority(bridge_path=bridge_path, profile_path=profile_path); input_package = build_scene_input(bridge=bridge, profile=profile); request = build_bounded_provider_request(input_package)
    chosen = provider or DeepSeekSceneProvider(); metadata = chosen.metadata(); identity = hash_payload({"input": input_package["content_hash"], "provider": metadata, "request": request}); root = Path(output_root) / ("nura-scene-production-" + identity[:12]); scene_path, handoff_path = root / "scene_production_package.json", root / "manual_heygen_handoff.json"
    if scene_path.is_file() and handoff_path.is_file():
        package = _read(scene_path); validate_scene_package(package=package, input_package=input_package)
        return {"status": "REUSED", "run_id": root.name, "scene_package_path": str(scene_path), "handoff_path": str(handoff_path), "package": package, "network_calls": 0, "credentials_required": False, "provider_called": False}
    if reuse_only: raise NuraSceneProductionError("REUSABLE_ARTIFACT_NOT_FOUND")
    if not metadata.get("fake") and not allow_network: raise NuraSceneProductionError("REAL_PROVIDER_REQUIRES_ALLOW_NETWORK")
    _atomic(root / "scene_production_input.json", input_package); _atomic(root / "provider_request.json", {"request": request, "request_hash": hash_payload(request), "provider": metadata})
    raw, response_meta = chosen.generate(request); _atomic(root / "raw_provider_response.json", {"provider": metadata, "request_hash": hash_payload(request), "metadata": response_meta, "response": raw})
    scenes = _creative(raw)
    normalized = []
    for index, scene in enumerate(scenes, 1): normalized.append({"scene_id": f"scene-{index:02d}", "order": index, **scene, "identity_reference_instruction": "Use the canonical NURA visual identity reference only as an external image-generation appearance reference; do not upload or transfer it automatically to HeyGen.", "unresolved_checks": ["OPERATOR_VISUAL_IDENTITY_REVIEW", "OPERATOR_NON_IMITATION_REVIEW"]})
    package = {"schema_version": SCHEMA_VERSION, "artifact_kind": "nura_scene_production_package", "package_id": "nura-scene-package-" + identity[:12], "project_id": "nura", "status": "READY_FOR_OPERATOR_REVIEW", "operator_review_required": True, "scene_input_hash": input_package["content_hash"], "bridge_hash": bridge["content_hash"], "reference_profile_hash": profile["content_hash"], "provider": metadata, "spoken_text_round_trip": input_package["approved_script"]["text"], "scenes": normalized, "warnings": ["SCENE_PROMPTS_REQUIRE_HUMAN_OPERATOR_REVIEW"], "production_execution_ready": False, "image_generation_performed": False, "heygen_called": False, "renderer_called": False}
    package["content_hash"] = hash_payload(package); validate_scene_package(package=package, input_package=input_package)
    handoff = {"schema_version": SCHEMA_VERSION, "artifact_kind": "nura_manual_heygen_handoff", "handoff_id": "nura-manual-heygen-handoff-" + package["content_hash"][:12], "scene_package": {"package_id": package["package_id"], "content_hash": package["content_hash"]}, "status": "READY_FOR_OPERATOR_REVIEW", "scene_order": [item["scene_id"] for item in normalized], "voice_selection": {"mode": "MANUAL_IN_HEYGEN", "optional_reference_role": "OPTIONAL_VOICE_REFERENCE", "automatic_transfer": False}, "operator_checklist": ["Review each prompt and identity-reference use.", "Generate and select scene images externally.", "Upload selected images manually to HeyGen.", "Select the NURA voice manually in HeyGen.", "Do not treat the reference MP3 as this episode's voice track."], "subtitle_source": bridge["subtitle_source"], "timing_status": "PROVISIONAL_NO_AUDIO_MEASUREMENT", "music": bridge["music"], "direct_heygen_transfer": False, "heygen_called": False, "renderer_called": False, "production_execution_ready": False}
    handoff["content_hash"] = hash_payload(handoff); first, second = _atomic(scene_path, package), _atomic(handoff_path, handoff)
    return {"status": "COMPLETED" if "COMPLETED" in (first, second) else "REUSED", "run_id": root.name, "scene_package_path": str(scene_path), "handoff_path": str(handoff_path), "package": package, "network_calls": 0 if metadata.get("fake") else 1, "credentials_required": not metadata.get("fake"), "provider_called": True}
