"""Stage 5N corrected NURA talking-guide scene package; no media execution."""
from __future__ import annotations
import hashlib, json, os, tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol
import httpx
from content_intelligence_provider import MODEL_ID, ProviderTransportError, post_deepseek_request
from nura_script_episode_bridge import hash_payload

SCHEMA_VERSION = "0.2"
PROVIDER_ID, PROMPT_ID, PROMPT_VERSION = "deepseek-nura-scene-production", "nura-scene-production", "1.1"
COMPOSER_ID, COMPOSER_VERSION = "nura-canonical-scene-prompt-composer", "1.0"
FINALIZER_ID, FINALIZER_VERSION = "nura-scene-human-finalizer", "1.0"
OPERATOR_EXPORT_ID, OPERATOR_EXPORT_VERSION = "nura-simplified-operator-export", "1.1"
VISUAL_GENERATION_STRATEGIES = ("ONE_IMAGE", "MULTI_IMAGE")
MAX_PAYLOAD_CHARS = 18_000
SCENE_GROUPS = (("scene-01", ("block-1",)), ("scene-02", ("block-2", "block-3")), ("scene-03", ("block-4", "block-5")))
SCENE_FIELDS = ("purpose", "emotional_state", "visual_action_pose", "environment_background", "composition_framing", "camera_direction", "lighting", "wardrobe_guidance", "facial_expression", "hand_gesture_guidance", "safe_area_guidance", "identity_reference_instruction", "positive_prompt", "negative_prompt", "prompt_language", "operator_note_ru", "operator_note_language")

class NuraSceneProductionError(ValueError): pass
def _json(value: Any) -> str: return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
def _read(path: Path) -> dict[str, Any]:
    try: value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error: raise NuraSceneProductionError("INVALID_STAGE_5N_INPUT") from error
    if not isinstance(value, dict): raise NuraSceneProductionError("STAGE_5N_OBJECT_REQUIRED")
    return value
def _verified(value: dict[str, Any], field: str = "content_hash") -> dict[str, Any]:
    if value.get(field) != hash_payload({key: item for key, item in value.items() if key != field}): raise NuraSceneProductionError(f"{field.upper()}_MISMATCH")
    return value
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

def _atomic_text(path: Path, value: str) -> str:
    text = value.rstrip() + "\n"; path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text: raise NuraSceneProductionError("CONFLICTING_OPERATOR_EXPORT_REUSE")
        return "REUSED"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as handle: handle.write(text); temporary = Path(handle.name)
    try: os.link(temporary, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text: raise NuraSceneProductionError("CONFLICTING_OPERATOR_EXPORT_REUSE")
    finally: temporary.unlink(missing_ok=True)
    return "COMPLETED"

def _atomic_bytes(path: Path, value: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != value: raise NuraSceneProductionError("CONFLICTING_OPERATOR_EXPORT_REUSE")
        return "REUSED"
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent) as handle: handle.write(value); temporary = Path(handle.name)
    try: os.link(temporary, path)
    except FileExistsError:
        if path.read_bytes() != value: raise NuraSceneProductionError("CONFLICTING_OPERATOR_EXPORT_REUSE")
    finally: temporary.unlink(missing_ok=True)
    return "COMPLETED"

def load_scene_authority(*, bridge_path: Path, profile_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    bridge, profile = _verified(_read(bridge_path)), _verified(_read(profile_path))
    if (bridge.get("artifact_kind"), bridge.get("original_rank"), bridge.get("script_format"), bridge.get("language")) != ("nura_script_to_production_bridge", 1, "TALKING_GUIDE", "ru"): raise NuraSceneProductionError("UNSUPPORTED_STAGE_5L_BRIDGE")
    if bridge.get("production_input_ready") is not True: raise NuraSceneProductionError("STAGE_5L_NOT_READY")
    visual, voice = profile.get("visual_identity_reference", {}), profile.get("voice_reference", {})
    if profile.get("artifact_kind") != "nura_production_reference_profile" or profile.get("readiness", {}).get("reference_profile_ready") is not True: raise NuraSceneProductionError("STAGE_5M_PROFILE_NOT_READY")
    if visual.get("role") != "VISUAL_IDENTITY_REFERENCE" or visual.get("usage") != "IMAGE_GENERATION_PROMPT_REFERENCE" or visual.get("status") != "READY": raise NuraSceneProductionError("VISUAL_REFERENCE_NOT_READY")
    if voice.get("role") != "OPTIONAL_VOICE_REFERENCE" or voice.get("status") != "READY" or voice.get("optional") is not True: raise NuraSceneProductionError("VOICE_REFERENCE_NOT_READY")
    return bridge, profile

def build_scene_input(*, bridge: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    blocks = bridge.get("spoken_script", {}).get("blocks")
    if not isinstance(blocks, list) or len(blocks) != 5: raise NuraSceneProductionError("FIVE_APPROVED_BLOCKS_REQUIRED")
    canonical = [{"block_id": f"block-{item['ordinal']}", "ordinal": item["ordinal"], "kind": item["kind"], "spoken_text": item["text"]} for item in blocks]
    if "\n\n".join(item["spoken_text"] for item in canonical) != bridge["spoken_script"]["text"]: raise NuraSceneProductionError("APPROVED_TEXT_ROUND_TRIP_MISMATCH")
    visual = profile["visual_identity_reference"]
    package = {"schema_version": SCHEMA_VERSION, "artifact_kind": "nura_scene_production_input", "project_id": "nura", "candidate_identity": bridge["candidate_identity"], "original_rank": 1, "script_format": "TALKING_GUIDE", "language": "ru", "bridge": {"bridge_id": bridge["bridge_id"], "content_hash": bridge["content_hash"]}, "reference_profile": {"profile_id": profile["profile_id"], "content_hash": profile["content_hash"]}, "approved_script": {"text": bridge["spoken_script"]["text"], "blocks": canonical}, "scene_grouping": [{"scene_id": scene_id, "source_block_ids": list(ids)} for scene_id, ids in SCENE_GROUPS], "visual_identity_reference": {key: visual[key] for key in ("sha256", "role", "usage", "media_type", "image")}, "canonical_direction": {"character": "NURA speaking directly to the viewer, never a heroine experiencing burnout", "identity": "same NURA, woman around 30, dark curly hair, soft expressive eyes, refined natural features, elegant ivory tailored blazer or ivory suit, restrained accessories", "style": "clean semi-realistic 2D / 2.5D editorial illustration; not photorealistic, anime, glamour, or cartoon", "continuity": "one modern bright NURA environment with warm beige textured walls, soft side light, one ivory outfit, one palette"}, "production_boundary": {"image_generation": "EXTERNAL_OPERATOR_ONLY", "heygen_transfer": False, "renderer_call": False, "voice_generation": False}}
    package["input_id"] = "nura-scene-input-" + hash_payload(package)[:12]; package["content_hash"] = hash_payload(package); return package

def build_bounded_provider_request(package: dict[str, Any]) -> dict[str, Any]:
    request = {"schema_version": SCHEMA_VERSION, "scene_input": {"input_id": package["input_id"], "content_hash": package["content_hash"]}, "rank": 1, "format": "TALKING_GUIDE", "language": "ru", "approved_blocks": package["approved_script"]["blocks"], "scene_grouping": package["scene_grouping"], "canonical_direction": package["canonical_direction"], "visual_identity_reference": {key: package["visual_identity_reference"][key] for key in ("sha256", "role", "usage", "media_type", "image")}, "required_scene_fields": list(SCENE_FIELDS)}
    encoded = json.dumps(request, ensure_ascii=False, sort_keys=True, allow_nan=False)
    if len(encoded) > MAX_PAYLOAD_CHARS or any(token in encoded.lower() for token in ("c:\\", "authorization", "api_key", "heygen", ".png", ".mp3")): raise NuraSceneProductionError("PROVIDER_PAYLOAD_FORBIDDEN_OR_TOO_LARGE")
    return request

@dataclass(frozen=True)
class ScenePromptContract:
    temperature: float = 0.2
    max_output_tokens: int = 2500
    def messages(self, request: dict[str, Any]) -> list[dict[str, str]]:
        system = "Return JSON only. Create exactly three talking-avatar source-image scenes matching supplied grouping. NURA is the sole on-camera speaker addressing the viewer, never a generic heroine or a person personally experiencing burnout. Preserve spoken text only by block IDs; add no spoken words. Every scene must use the same canonical NURA: woman around 30, dark curly hair, refined natural features, ivory tailored blazer/suit; clean semi-realistic 2D/2.5D editorial illustration, never photorealistic. Use one calm warm-beige NURA environment and soft side light. Vertical 9:16, chest-up/waist-up/medium-close, near-direct viewer address, mostly frontal, eyes and relaxed closed mouth fully visible, unobstructed face, hands below chest. No phone, cup, rear view, extreme profile, full body, text, logos, watermark, clinical/dramatic burnout imagery. identity_reference_instruction must explicitly bind every scene to the supplied visual reference. positive_prompt and negative_prompt must be English with prompt_language='en'; operator_note_ru must be Russian with operator_note_language='ru'."
        schema = {"scenes": [{"scene_id": "scene-01", "source_block_ids": ["block-1"], **{field: "..." for field in SCENE_FIELDS}, "warnings": []}]}
        return [{"role": "system", "content": system}, {"role": "user", "content": json.dumps({"request": request, "output_schema": schema}, ensure_ascii=False, separators=(",", ":"))}]

class SceneProvider(Protocol):
    def generate(self, request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]: ...
    def metadata(self) -> dict[str, Any]: ...
class DeepSeekSceneProvider:
    def __init__(self, api_key: str | None = None, transport: httpx.BaseTransport | None = None) -> None: self.api_key, self.transport, self.contract = api_key if api_key is not None else os.getenv("DEEPSEEK_API_KEY"), transport, ScenePromptContract()
    def metadata(self) -> dict[str, Any]: return {"provider_id": PROVIDER_ID, "model_id": MODEL_ID, "prompt_id": PROMPT_ID, "prompt_version": PROMPT_VERSION, "configuration": {"response_format": {"type": "json_object"}, "thinking": {"type": "disabled"}, "temperature": self.contract.temperature, "max_tokens": self.contract.max_output_tokens}, "fake": False}
    def generate(self, request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.api_key: raise NuraSceneProductionError("BLOCKED_PROVIDER_CREDENTIALS")
        body = {"model": MODEL_ID, "messages": self.contract.messages(request), "response_format": {"type": "json_object"}, "thinking": {"type": "disabled"}, "temperature": self.contract.temperature, "max_tokens": self.contract.max_output_tokens}
        try: response, latency = post_deepseek_request(body, api_key=self.api_key, transport=self.transport)
        except ProviderTransportError as error: raise NuraSceneProductionError(str(error)) from error
        try: raw = response.json()
        except json.JSONDecodeError as error: raise NuraSceneProductionError("PROVIDER_NON_JSON_RESPONSE") from error
        return raw, {"http_status": response.status_code, "latency_ms": latency, "response_hash": hashlib.sha256(response.content).hexdigest(), "request_id": response.headers.get("x-request-id")}

class FakeSceneProvider:
    def metadata(self) -> dict[str, Any]: return {"provider_id": "fake-nura-scene-production", "model_id": "deterministic", "prompt_id": PROMPT_ID, "prompt_version": PROMPT_VERSION, "fake": True}
    def generate(self, request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        poses = [("спокойная серьёзность и мягкая ясность", "устойчивая открытая поза, взгляд в камеру", "руки ниже груди, без предметов"), ("спокойное узнавание переходит в ясность", "небольшой открытый жест одной рукой", "ладонь открыта ниже груди"), ("тёплая тихая уверенность", "мягкий приглашающий жест", "одна рука слегка раскрыта ниже груди")]
        scenes = []
        for index, ((scene_id, ids), (state, pose, hands)) in enumerate(zip(SCENE_GROUPS, poses), 1):
            scenes.append({"scene_id": scene_id, "source_block_ids": list(ids), "purpose": ("Прямой вопрос зрителю." if index == 1 else "Мягкое переосмысление противоречия." if index == 2 else "Небольшой следующий шаг и спокойное завершение."), "emotional_state": state, "visual_action_pose": pose, "environment_background": "Спокойное современное светлое пространство NURA: тёплые бежевые фактурные стены, минимальный фон.", "composition_framing": "vertical 9:16, medium close-up" if index != 2 else "vertical 9:16, waist-up", "camera_direction": "near-direct eye-level address, mostly frontal", "lighting": "soft side light from the left; same warm palette", "wardrobe_guidance": "same elegant ivory tailored blazer, restrained minimal accessories", "facial_expression": "спокойное зрелое выражение, глаза и естественно расслабленные закрытые губы полностью видимы", "hand_gesture_guidance": hands, "safe_area_guidance": "Лицо и глаза в центральной safe area; верхние 15% без критичных деталей; нижняя subtitle zone спокойна и свободна от важных рук/объектов; учтены platform UI margins.", "identity_reference_instruction": "Use the supplied canonical NURA visual reference for the same dark-curly-haired identity and do not clone a real person.", "positive_prompt": f"NURA, same canonical woman around 30 with dark curly hair, soft expressive eyes and refined natural features, elegant ivory tailored blazer, clean semi-realistic 2D 2.5D editorial illustration, warm beige textured NURA environment, soft left side light, vertical 9:16, {'medium close-up' if index != 2 else 'waist-up'}, near-direct eye contact, mostly frontal head, eyes and naturally relaxed closed mouth fully visible, unobstructed face, shoulders and neck visible, {hands.lower()}, stable facial anatomy, no text.", "negative_prompt": "photorealistic, realistic photography, generic woman, light brown hair, straight hair, anime, glamour, phone, cup, looking down, rear view, side profile, full body, face obstruction, hand over face, object near mouth, open mouth, text, subtitles, speech bubbles, logo, watermark, clinical setting, personal burnout, dramatic exhaustion", "prompt_language": "en", "operator_note_ru": "Проверьте совпадение с каноническим образом NURA и пригодность лица для будущего lip-sync; используйте reference только как appearance reference, без клонирования.", "operator_note_language": "ru", "warnings": []})
        return {"scenes": scenes}, {"http_status": 200, "response_hash": "fake", "latency_ms": 0}

def _creative(raw: dict[str, Any]) -> list[dict[str, Any]]:
    try: return json.loads(raw["choices"][0]["message"]["content"] if "choices" in raw else json.dumps(raw, ensure_ascii=False))["scenes"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error: raise NuraSceneProductionError("PROVIDER_SCENE_SCHEMA_INVALID") from error

def _russian(value: str) -> bool: return any("а" <= char.lower() <= "я" or char.lower() == "ё" for char in value)
def _dedupe(parts: list[str]) -> str:
    seen: set[str] = set(); result: list[str] = []
    for part in parts:
        normalized = part.strip().lower()
        if normalized and normalized not in seen: seen.add(normalized); result.append(part.strip())
    return ", ".join(result)

def compose_canonical_prompts(scene: dict[str, Any]) -> tuple[str, str, list[str]]:
    provider_positive = scene.get("provider_creative_prompt", scene["positive_prompt"])
    provider_negative = scene.get("provider_negative_prompt", scene["negative_prompt"])
    omissions = [marker for marker in ("nura", "vertical 9:16") if marker not in provider_positive.lower()]
    prefix = "NURA, same canonical NURA identity from the supplied visual identity reference, woman around 30, dark curly hair, soft expressive eyes, refined natural facial features, calm wise emotionally safe presence, elegant ivory tailored blazer or ivory suit, restrained minimal accessories, clean semi-realistic 2D / 2.5D editorial illustration, not photorealistic, not anime"
    suffix = f"vertical 9:16 composition, {scene['composition_framing']}, head mostly frontal, direct or near-direct eye contact, eyes fully visible, mouth fully visible, lips naturally relaxed, face unobstructed, shoulders and neck visible, hands away from face, no object near mouth, suitable for future talking-avatar lip-sync, clean readable silhouette, calm lower subtitle zone, critical facial features inside central safe area, no text, no subtitles, no speech bubbles, no logo, no watermark"
    negative = ["no different character", "no light or straight hair", "no photorealistic photography", "no anime", "no extreme profile", "no rear view", "no full-body distant framing", "no face obstruction", "no hand over face", "no phone or object near mouth", "no exaggerated emotion", "no clinical imagery", "no lamp metaphor", "no text", "no subtitles", "no speech bubbles", "no logos", "no watermark", "no source-video imitation", "no generated-image claim", "no automatic HeyGen or renderer action"]
    return _dedupe([prefix, provider_positive, suffix]), _dedupe(negative + provider_negative.split(",")), omissions

def _provider_contradictions(scene: dict[str, Any]) -> list[str]:
    text = " ".join(str(scene.get(key, "")) for key in ("purpose", "visual_action_pose", "composition_framing", "camera_direction", "facial_expression", "positive_prompt")).lower()
    checks = {"generic woman": "GENERIC_CHARACTER", "light brown hair": "CONFLICTING_HAIR", "straight hair": "CONFLICTING_HAIR", "photorealistic": "PHOTOREALISTIC", "horizontal": "INCOMPATIBLE_ASPECT_RATIO", "rear view": "REAR_VIEW", "side profile": "EXTREME_PROFILE", "hidden mouth": "HIDDEN_MOUTH", "phone": "OBJECT_NEAR_MOUTH", "personal burnout": "PERSONAL_BURNOUT_ROLEPLAY"}
    return [code for token, code in checks.items() if token in text]

def materialize_composed_scenes(raw_scenes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    scenes, audit = [], []
    for raw_scene in raw_scenes:
        scene = dict(raw_scene); contradictions = _provider_contradictions(scene)
        if contradictions: raise NuraSceneProductionError("PROVIDER_CANONICAL_CONTRADICTION:" + ",".join(contradictions))
        scene["provider_creative_prompt"] = scene["positive_prompt"]
        scene["provider_negative_prompt"] = scene["negative_prompt"]
        scene["composed_positive_prompt"], scene["composed_negative_prompt"], omissions = compose_canonical_prompts(scene)
        scene["prompt_composition_mode"] = "APPLICATION_CANONICAL_COMPOSITION"
        scenes.append(scene); audit.append({"scene_id": scene.get("scene_id"), "canonical_omissions": omissions, "canonical_contradictions": contradictions})
    return scenes, audit
def _positive_text(scene: dict[str, Any]) -> str:
    return " ".join(
        str(scene.get(key, ""))
        for key in SCENE_FIELDS
        if key not in {"negative_prompt", "operator_note_ru", "operator_note_language"}
    ).lower()
def validate_scene_package(*, package: dict[str, Any], input_package: dict[str, Any]) -> None:
    scenes, blocks = package.get("scenes"), input_package["approved_script"]["blocks"]
    if not isinstance(scenes, list) or len(scenes) != 3: raise NuraSceneProductionError("THREE_SCENES_REQUIRED")
    expected, actual = [b["block_id"] for b in blocks], []
    for (scene_id, ids), scene in zip(SCENE_GROUPS, scenes):
        if not isinstance(scene, dict) or scene.get("scene_id") != scene_id or scene.get("source_block_ids") != list(ids) or any(not isinstance(scene.get(field), str) or not scene[field].strip() for field in SCENE_FIELDS): raise NuraSceneProductionError("REQUIRED_STRUCTURED_FIELD_MISSING")
        if not isinstance(scene.get("warnings", []), list): raise NuraSceneProductionError("INVALID_SCENE_WARNINGS")
        actual.extend(scene["source_block_ids"]); text = _positive_text(scene)
        if not _russian(scene["operator_note_ru"]): raise NuraSceneProductionError("OPERATOR_NOTE_RUSSIAN_REQUIRED")
        if scene["prompt_language"] != "en" or scene["operator_note_language"] != "ru": raise NuraSceneProductionError("SCENE_LANGUAGE_DECLARATION_REQUIRED")
        if any(token in text for token in ("photorealistic", "realistic photography", "generic woman", "light brown hair", "phone", "rear view", "side profile", "full body", "looking down", "personal burnout")): raise NuraSceneProductionError("TALKING_AVATAR_OR_IDENTITY_VIOLATION")
        final_prompt = scene.get("composed_positive_prompt", scene["positive_prompt"]).lower()
        required = ("nura", "dark curly hair", "ivory", "semi-realistic", "editorial", "vertical 9:16", "eye contact", "mouth fully visible")
        if not all(token in final_prompt for token in required): raise NuraSceneProductionError("CANONICAL_NURA_PROMPT_REQUIRED")
        if "direct" not in scene["camera_direction"].lower(): raise NuraSceneProductionError("TALKING_AVATAR_VIEWER_ADDRESS_REQUIRED")
        if "safe area" not in scene["safe_area_guidance"].lower() and "safe area" not in final_prompt: raise NuraSceneProductionError("SAFE_AREA_GUIDANCE_REQUIRED")
    for scene in scenes:
        continuity_text = " ".join(scene[field].lower() for field in ("environment_background", "lighting", "wardrobe_guidance"))
        requirements = (("warm", "тёпл"), ("beige", "беж"), ("soft", "мягк"), ("side light", "боков"), ("ivory", "слонов"), ("blazer", "пиджак"))
        if not all(any(token in continuity_text for token in variants) for variants in requirements):
            raise NuraSceneProductionError("SCENE_CONTINUITY_MISMATCH")
    if actual != expected: raise NuraSceneProductionError("EXACT_BLOCK_COVERAGE_REQUIRED")
    if package.get("spoken_text_round_trip") != input_package["approved_script"]["text"]: raise NuraSceneProductionError("SPOKEN_TEXT_CHANGED")
    if package.get("content_hash") != hash_payload({key: item for key, item in package.items() if key != "content_hash"}): raise NuraSceneProductionError("SCENE_PACKAGE_HASH_MISMATCH")

def record_operator_rejection(*, rejected_package_path: Path, raw_response_path: Path, output_path: Path) -> dict[str, Any]:
    package, raw = _verified(_read(rejected_package_path)), _read(raw_response_path)
    raw_hash = hashlib.sha256(Path(raw_response_path).read_bytes()).hexdigest()
    decision = {"schema_version": SCHEMA_VERSION, "artifact_kind": "nura_scene_operator_rejection", "reviewer": {"reviewer_id": "nura-owner", "reviewer_role": "OWNER", "reviewer_display_name": "Василий", "human_confirmation": True}, "rejected_package": {"package_id": package["package_id"], "content_hash": package["content_hash"], "raw_response_sha256": raw_hash}, "scene_decisions": [{"scene_id": item["scene_id"], "decision": "REQUEST_ALTERNATIVE_PROMPT"} for item in package["scenes"]], "rejection_reasons": ["WRONG_CHARACTER_IDENTITY", "WRONG_CHARACTER_ROLE", "WRONG_VISUAL_STYLE", "HEYGEN_UNSUITABLE", "EXCESSIVE_VISUAL_FRAGMENTATION", "MISSING_STRUCTURED_PRODUCTION_FIELDS"], "audit_trail": [{"event_type": "PACKAGE_RETAINED_IMMUTABLE", "raw_response_retained": True}]}
    decision["content_hash"] = hash_payload(decision); _atomic(output_path, decision); return decision

def record_owner_scene_decision(*, package_path: Path, output_path: Path, reviewed_at: str | None = None) -> dict[str, Any]:
    package = _verified(_read(package_path))
    if Path(output_path).is_file() and reviewed_at is None:
        existing = _verified(_read(output_path))
        if existing.get("reviewed_package") != {"package_id": package["package_id"], "content_hash": package["content_hash"]}: raise NuraSceneProductionError("OWNER_DECISION_PACKAGE_MISMATCH")
        return existing
    decision = {"schema_version": SCHEMA_VERSION, "artifact_kind": "nura_scene_owner_decision", "reviewed_package": {"package_id": package["package_id"], "content_hash": package["content_hash"]}, "reviewer": {"reviewer_id": "nura-owner", "reviewer_role": "OWNER", "reviewer_display_name": "Василий", "human_confirmation": True}, "reviewed_at": reviewed_at or datetime.now(timezone.utc).isoformat(), "scene_decisions": [{"scene_id": scene_id, "decision": "APPROVE_WITH_EDITS", "required_edits": ["DEDUPLICATE_PROMPTS", "SEPARATE_POSITIVE_NEGATIVE_BOUNDARY", "EXPAND_SAFE_AREA", f"APPLY_{scene_id.upper()}_OWNER_DIRECTION"]} for scene_id, _ in SCENE_GROUPS], "global_decisions": {"scene_count_approved": True, "continuity_approved": True, "visual_identity_approved": True, "talking_avatar_suitability_approved": True, "manual_heygen_handoff_approved": True, "ready_for_external_image_generation": True}}
    decision["content_hash"] = hash_payload(decision); _atomic(output_path, decision); return decision

def _final_positive(scene: dict[str, Any], index: int) -> str:
    identity = "NURA, same canonical identity from the supplied visual identity reference: woman around 30, dark curly hair, soft expressive eyes, refined natural facial features, calm wise emotionally safe presence, elegant ivory tailored blazer, restrained minimal accessories, clean semi-realistic 2D / 2.5D editorial illustration style"
    actions = ["calm seriousness, gentle emotional tension, attentive direct gaze, emotionally composed guide presence, lips naturally relaxed and closed", "recognition moving toward calm clarity, speaking directly to the viewer, one small open-hand gesture below chest, lips naturally relaxed and closed", "warm calm quietly confident and emotionally grounded presence, restrained warmth, very subtle half-smile or neutral warm expression, calm attentive eyes, lips naturally relaxed and closed"]
    environment = "calm contemporary NURA environment, warm beige textured wall, soft warm side light from the left"
    framing = ["vertical 9:16, medium close-up, chest-up, centered, head mostly frontal, direct or near-direct eye contact", "vertical 9:16, waist-up, centered, head mostly frontal, direct or near-direct eye contact", "vertical 9:16, medium close-up, chest-up, centered, head mostly frontal, direct eye contact"][index]
    technical = "eyes fully visible, mouth fully visible, face unobstructed, shoulders and neck visible, hands below chest and away from face, suitable for future talking-avatar lip-sync, clean readable silhouette"
    safe = "top 15% free of critical face and hair details, face and eyes inside central safe area, lower 25% calm for future subtitles, hands and important objects outside the lower subtitle zone, NURA positioned high enough for platform UI margins"
    return "; ".join((identity, actions[index], environment, framing, technical, safe))

def _final_negative() -> str:
    return ", ".join(("different character", "light or straight hair", "photorealistic photography", "anime", "childish cartoon style", "glamour", "extreme profile", "rear view", "full-body distant framing", "face obstruction", "hand over face", "phone or object near mouth", "open mouth", "exaggerated emotion", "personal burnout roleplay", "clinical imagery", "lamp metaphor", "busy background", "cold lighting", "text", "subtitles", "speech bubbles", "logos", "watermark", "source-video imitation", "generated-image claim", "automatic HeyGen or renderer action"))

def _safe_area_ru() -> str:
    return "Верхние 15% кадра свободны от критических деталей лица и волос; лицо и глаза находятся в центральной безопасной зоне; нижние 25% имеют спокойный фон для будущих субтитров; руки и важные объекты не занимают нижнюю subtitle zone; NURA не располагается слишком низко; учтены platform UI margins; точные timestamps и subtitle rendering пока отсутствуют."

def validate_finalized_scene_package(package: dict[str, Any], original: dict[str, Any]) -> None:
    if package.get("status") != "READY_FOR_EXTERNAL_IMAGE_GENERATION" or package.get("operator_review_status") != "HUMAN_APPROVED_WITH_EDITS" or package.get("human_confirmation") is not True: raise NuraSceneProductionError("FINAL_OWNER_APPROVAL_REQUIRED")
    if package.get("spoken_text_round_trip") != original.get("spoken_text_round_trip"): raise NuraSceneProductionError("SPOKEN_TEXT_CHANGED")
    scenes = package.get("scenes")
    if not isinstance(scenes, list) or [(item.get("scene_id"), item.get("source_block_ids")) for item in scenes] != [(scene_id, list(ids)) for scene_id, ids in SCENE_GROUPS]: raise NuraSceneProductionError("FINAL_SCENE_GROUPING_INVALID")
    for scene in scenes:
        positive, negative = scene.get("final_human_approved_positive_prompt", "").lower(), scene.get("final_human_approved_negative_prompt", "").lower()
        if any(token in positive.split() for token in ("no", "not")): raise NuraSceneProductionError("NEGATIVE_CONSTRAINT_IN_FINAL_POSITIVE")
        for marker in ("nura", "dark curly hair", "ivory tailored blazer", "2d / 2.5d editorial", "vertical 9:16", "eye contact", "mouth fully visible", "safe area"):
            if marker not in positive: raise NuraSceneProductionError("FINAL_CANONICAL_PROMPT_INCOMPLETE")
        for marker in ("photorealistic photography", "anime", "childish cartoon style", "extreme profile", "rear view", "phone or object near mouth", "text", "logos", "watermark"):
            if negative.count(marker) != 1: raise NuraSceneProductionError("FINAL_NEGATIVE_PROMPT_INVALID")
        if ", cartoon," in f", {negative}," or negative.startswith("cartoon,"): raise NuraSceneProductionError("GENERIC_CARTOON_PROHIBITION_FORBIDDEN")
        if not _russian(scene.get("operator_note_ru", "")) or not all(marker in scene.get("safe_area_guidance", "").lower() for marker in ("15%", "25%", "subtitle", "ui margins")): raise NuraSceneProductionError("FINAL_STRUCTURED_GUIDANCE_INVALID")
        if scene.get("original_provider_creative_delta") != scene.get("provider_creative_prompt") or scene.get("original_application_composed_prompt") != scene.get("composed_positive_prompt"): raise NuraSceneProductionError("ORIGINAL_PROMPT_PROVENANCE_CHANGED")
    if any(package.get(field) is not False for field in ("per_scene_images_ready", "generated_voice_tracks_ready", "heygen_clips_ready", "subtitle_timing_ready", "production_execution_ready", "image_generation_performed", "heygen_called", "renderer_called")): raise NuraSceneProductionError("FINAL_READINESS_OVERCLAIMED")

def finalize_scene_review(*, package_path: Path, handoff_path: Path, bridge_path: Path, profile_path: Path, decision_path: Path, output_root: Path) -> dict[str, Any]:
    original, original_handoff, decision = _verified(_read(package_path)), _verified(_read(handoff_path)), _verified(_read(decision_path))
    bridge, profile = load_scene_authority(bridge_path=bridge_path, profile_path=profile_path)
    reviewer = decision.get("reviewer", {})
    if (reviewer.get("reviewer_id"), reviewer.get("reviewer_role"), reviewer.get("human_confirmation")) != ("nura-owner", "OWNER", True): raise NuraSceneProductionError("OWNER_CONFIRMATION_REQUIRED")
    if decision.get("reviewed_package") != {"package_id": original["package_id"], "content_hash": original["content_hash"]}: raise NuraSceneProductionError("OWNER_DECISION_PACKAGE_MISMATCH")
    if [(item.get("scene_id"), item.get("decision")) for item in decision.get("scene_decisions", [])] != [(scene_id, "APPROVE_WITH_EDITS") for scene_id, _ in SCENE_GROUPS]: raise NuraSceneProductionError("THREE_APPROVE_WITH_EDITS_REQUIRED")
    finalizer = {"finalizer_id": FINALIZER_ID, "finalizer_version": FINALIZER_VERSION}; finalizer["finalizer_hash"] = hash_payload(finalizer)
    identity = hash_payload({"original_package": original["content_hash"], "original_handoff": original_handoff["content_hash"], "decision": decision["content_hash"], "finalizer": finalizer})
    root = Path(output_root) / ("nura-scene-production-finalized-" + identity[:12]); final_package_path, final_handoff_path = root / "finalized_scene_production_package.json", root / "finalized_manual_heygen_handoff.json"
    if final_package_path.is_file() and final_handoff_path.is_file():
        package = _verified(_read(final_package_path)); validate_finalized_scene_package(package, original); return {"status": "REUSED", "package": package, "package_path": str(final_package_path), "handoff_path": str(final_handoff_path), "network_calls": 0, "credentials_required": False, "provider_called": False}
    revised = []
    states = ["Calm seriousness, gentle emotional tension, attentive direct gaze.", "Recognition moving toward calm clarity; direct viewer address.", "Warm, calm, quietly confident, emotionally grounded."]
    faces = ["No smile; attentive direct gaze; calm seriousness; lips naturally relaxed and closed.", "Calm recognition and clarity; head mostly frontal; lips naturally relaxed and closed.", "Restrained warmth; very subtle half-smile or neutral warm expression; lips naturally relaxed and closed."]
    notes = ["Сцена 1: серьёзный прямой hook без улыбки и без изображения личного страдания NURA; проверьте спокойное напряжение, взгляд в камеру и руки ниже груди.", "Сцена 2: NURA обращается к зрителю и мягко переосмысливает противоречие; открытая ладонь остаётся ниже груди, без кивка и без ролевого изображения выгорания.", "Сцена 3: тёплое спокойное завершение с тихой уверенностью; допустима только очень лёгкая полуулыбка или нейтрально-тёплое выражение."]
    for index, scene in enumerate(original["scenes"]):
        item = dict(scene); item.update({"original_provider_creative_delta": scene["provider_creative_prompt"], "original_application_composed_prompt": scene["composed_positive_prompt"], "owner_decision": "APPROVE_WITH_EDITS", "required_edits": decision["scene_decisions"][index]["required_edits"], "revision_reasons": ["OWNER_DIRECTION", "PROMPT_DEDUPLICATION", "POSITIVE_NEGATIVE_BOUNDARY", "SAFE_AREA_COMPLETION"], "reviewer": reviewer, "reviewed_at": decision["reviewed_at"], "emotional_state": states[index], "facial_expression": faces[index], "safe_area_guidance": _safe_area_ru(), "final_human_approved_positive_prompt": _final_positive(scene, index), "final_human_approved_negative_prompt": _final_negative(), "operator_note_ru": notes[index]})
        item["human_revision_hash"] = hash_payload({key: value for key, value in item.items() if key != "human_revision_hash"}); revised.append(item)
    package = {"schema_version": "0.3", "artifact_kind": "nura_finalized_scene_production_package", "package_id": "nura-finalized-scene-package-" + identity[:12], "content_hash": "", "status": "READY_FOR_EXTERNAL_IMAGE_GENERATION", "operator_review_status": "HUMAN_APPROVED_WITH_EDITS", "human_confirmation": True, "original_package": {"package_id": original["package_id"], "content_hash": original["content_hash"]}, "owner_decision": {"content_hash": decision["content_hash"], "reviewer": reviewer, "reviewed_at": decision["reviewed_at"]}, "finalizer": finalizer, "bridge_hash": bridge["content_hash"], "reference_profile_hash": profile["content_hash"], "spoken_text_round_trip": original["spoken_text_round_trip"], "scenes": revised, **decision["global_decisions"], "per_scene_images_ready": False, "generated_voice_tracks_ready": False, "heygen_clips_ready": False, "subtitle_timing_ready": False, "production_execution_ready": False, "image_generation_performed": False, "heygen_called": False, "renderer_called": False}
    package["content_hash"] = hash_payload({key: value for key, value in package.items() if key != "content_hash"})
    validate_finalized_scene_package(package, original)
    scene_placeholders = [{"scene_id": scene_id, "selected_image_reference": None, "selected_image_hash": None, "visual_identity_review_status": "PENDING", "heygen_voice_selection": "PENDING_MANUAL_SELECTION", "heygen_clip_reference": None, "heygen_clip_hash": None, "measured_audio_duration_seconds": None, "subtitle_alignment_status": "NOT_STARTED"} for scene_id, _ in SCENE_GROUPS]
    handoff = {"schema_version": "0.3", "artifact_kind": "nura_finalized_manual_heygen_handoff", "handoff_id": "nura-finalized-manual-heygen-handoff-" + package["content_hash"][:12], "content_hash": "", "scene_package": {"package_id": package["package_id"], "content_hash": package["content_hash"]}, "status": "READY_FOR_EXTERNAL_IMAGE_GENERATION", "scene_order": [scene_id for scene_id, _ in SCENE_GROUPS], "subtitle_source": "EXACT_APPROVED_TEXT", "subtitle_source_reference": {"bridge_id": bridge["bridge_id"], "bridge_hash": bridge["content_hash"], "subtitle_source_hash": hash_payload(bridge["subtitle_source"])}, "subtitle_timing_status": "PROVISIONAL_NO_AUDIO_MEASUREMENT", "music_role": "SECONDARY_OPTIONAL", "music_track": None, "voice_selection": {"mode": "MANUAL_IN_HEYGEN", "optional_reference_role": "OPTIONAL_VOICE_REFERENCE", "automatic_transfer": False}, "scenes": scene_placeholders, "operator_checklist_ru": ["Используйте только final human-approved prompts и canonical NURA visual reference.", "Вручную сгенерируйте и выберите по одному изображению для каждой сцены.", "Проверьте visual identity, safe area и пригодность лица для lip-sync.", "Вручную загрузите утверждённые изображения в HeyGen и выберите голос NURA."], "direct_heygen_transfer": False, "manual_heygen_handoff_approved": True, "per_scene_images_ready": False, "generated_voice_tracks_ready": False, "heygen_clips_ready": False, "subtitle_timing_ready": False, "production_execution_ready": False, "heygen_called": False, "renderer_called": False}
    handoff["content_hash"] = hash_payload({key: value for key, value in handoff.items() if key != "content_hash"})
    first = (_atomic(final_package_path, package), _atomic(final_handoff_path, handoff)); return {"status": "COMPLETED" if "COMPLETED" in first else "REUSED", "package": package, "package_path": str(final_package_path), "handoff_path": str(final_handoff_path), "network_calls": 0, "credentials_required": False, "provider_called": False}

def _integrated_chatgpt_prompt(positive: str, negative: str) -> str:
    return f"Use the attached canonical NURA reference image as the primary identity anchor and preserve her recognizable face and identity.\n\nCreate this image:\n{positive}\n\nIntegrated constraints: Avoid {negative}. Do not add written text, captions, subtitles, speech bubbles, logos, or watermarks. Keep the face, eyes, and mouth clearly visible and suitable for a future talking-avatar lip-sync."

def _one_image_prompt() -> str:
    return """Use the attached NURA_REFERENCE.png as the primary identity anchor. Preserve NURA's recognizable face, apparent age, core facial features, and identity.

Create one strong source portrait for a complete Russian TALKING_GUIDE video. NURA is a calm, wise, emotionally safe guide speaking directly to the viewer about supporting others without abandoning oneself. Express one coherent emotional arc: calm seriousness and gentle recognition moving toward quiet clarity and grounded reassurance. She is a woman around 30 with canonical dark curly hair, soft expressive eyes, refined natural facial features, an elegant ivory tailored blazer, and restrained minimal accessories.

Use a clean semi-realistic 2D / 2.5D editorial illustration style. Place NURA in a calm contemporary interior with a naturally detailed warm beige textured wall and soft warm side light from the left.

Vertical 9:16 composition, medium close-up, chest-up, centered, head mostly frontal, direct or near-direct eye contact. Her lips are naturally relaxed and closed. Keep her face, eyes, mouth, shoulders, neck, clothing, and torso clearly visible and normally detailed. Keep her hands below the chest and away from the face. The portrait must be suitable for future talking-avatar lip-sync.

Keep the entire image naturally rendered, sharp, and visually coherent. Leave some clean, uncluttered, fully rendered and in-focus background space around and below NURA for future subtitles. Maintain natural breathing room above her hair without creating a large empty band. Position NURA high enough for platform UI, but do not make her unnaturally low or small. Keep the blazer, lower torso, background, and bottom edge normally detailed and in focus.

Integrated constraints: do not create an artificial subtitle panel or separate lower-third plate. Do not create blur, fog, haze, glow, bloom, gradient fade, frosted glass, translucent overlay, vignette, or a soft-focus wash at the bottom. Do not add a blurred foreground. Do not fade the lower torso or blazer into the background. Avoid a different character, changed facial identity, light or straight hair, photorealistic photography, anime, childish cartoon styling, glamour, broad advertising smile, extreme profile, rear view, full-body distant framing, face obstruction, hand over face, a phone or object near the mouth, open mouth, exaggerated emotion, personal-burnout roleplay, clinical imagery, lamp metaphor, busy background, cold lighting, anatomy artifacts, extra fingers, distorted hands, source-video imitation, or claims that an image has already been generated. Do not add written text, captions, subtitles, speech bubbles, logos, or watermarks."""

def _content_ru(text: str) -> str:
    blocks = text.split("\n\n")
    if len(blocks) != 5: raise NuraSceneProductionError("FIVE_APPROVED_BLOCKS_REQUIRED")
    sections = [("Хук", "Сразу обозначить узнаваемое противоречие и привлечь внимание."), ("Развитие проблемы", "Показать конкретный повторяющийся паттерн — внимание постоянно уходит к другим, а собственное состояние переносится на потом."), ("Поворот / переосмысление", "Отделить поддержку другого от полного отказа от собственных потребностей."), ("Небольшой следующий шаг", "Предложить один конкретный и реалистичный вопрос к себе без требования резко менять поведение."), ("Финальная мысль", "Уточнить, что внимание к себе не означает отказ от близкого человека.")]
    parts = ["# Заголовок ролика", blocks[0], "- `title_source`: `APPROVED_HOOK_FALLBACK`", "- Заголовок не входит в spoken text и не вставляется в речь HeyGen.", "", "# Основные параметры", "- Формат: `TALKING_GUIDE`", "- Количество роликов: `1`", "- Визуальная стратегия: `ONE_IMAGE`", "- Количество изображений: `1`", "- Ориентировочная длительность: `25–30 секунд`", "- Статус длительности: `ESTIMATED_NOT_MEASURED`", "", "# Структура сценария"]
    for index, (block, (name, purpose)) in enumerate(zip(blocks, sections), 1): parts.extend((f"## {index}. {name}", block, "**Назначение:**", purpose, ""))
    parts.extend(("# Чистый текст для HeyGen", "В HeyGen копировать только блок ниже. Заголовок, названия смысловых частей и пояснения не вставлять в речь.", "", "```text", text, "```"))
    return "\n".join(parts)

def build_simplified_operator_export(*, finalized_package_path: Path, finalized_handoff_path: Path, output_root: Path, reference_image_path: Path, visual_generation_strategy: str = "ONE_IMAGE") -> dict[str, Any]:
    package, handoff = _verified(_read(finalized_package_path)), _verified(_read(finalized_handoff_path))
    if visual_generation_strategy not in VISUAL_GENERATION_STRATEGIES: raise NuraSceneProductionError("UNSUPPORTED_VISUAL_GENERATION_STRATEGY")
    if package.get("status") != "READY_FOR_EXTERNAL_IMAGE_GENERATION" or package.get("human_confirmation") is not True: raise NuraSceneProductionError("FINALIZED_PACKAGE_NOT_READY_FOR_EXPORT")
    text = package["spoken_text_round_trip"]
    if visual_generation_strategy == "ONE_IMAGE":
        prompts = [_one_image_prompt()]
        justification = "Single-speaker 25–30 second TALKING_GUIDE in one continuous location and wardrobe; the approved script forms one emotional arc and does not require visual scene changes."
    else:
        prompts = [_integrated_chatgpt_prompt(scene["final_human_approved_positive_prompt"], scene["final_human_approved_negative_prompt"]) for scene in package["scenes"]]
        justification = "MULTI_IMAGE explicitly selected; each reviewed scene remains a separate self-contained image task."
    reference_bytes = Path(reference_image_path).read_bytes(); reference_hash = hashlib.sha256(reference_bytes).hexdigest()
    if reference_hash != "5d6350b968c6bd9ea3ced646eb835c1c040d9d9203113d193f8261f2c769f383": raise NuraSceneProductionError("CANONICAL_REFERENCE_HASH_MISMATCH")
    content = _content_ru(text)
    readme = "Это один ролик формата TALKING_GUIDE с одним изображением.\n\n1. Откройте 01_CONTENT_RU.md: там находятся заголовок, структура сценария и отдельный блок «Чистый текст для HeyGen».\n2. В HeyGen копируйте только блок «Чистый текст для HeyGen». Заголовок и пояснения в речь не вставляйте.\n3. Приложите NURA_REFERENCE.png к сообщению в ChatGPT и вставьте целиком 02_IMAGE_PROMPT.txt.\n4. Вручную сгенерируйте изображение и выберите лучший результат.\n\nLOOPRA не генерирует изображение и не вызывает HeyGen автоматически."
    descriptor = {"exporter_id": OPERATOR_EXPORT_ID, "exporter_version": OPERATOR_EXPORT_VERSION, "source_package": package["content_hash"], "source_handoff": handoff["content_hash"], "source_previous_export": {"export_id": "nura-operator-export-1d134f9abcd5", "content_hash": "bb5643aea2291af85b394aece3ffcbace83e77d2c9ce046fbfa237558bbc156c"}, "visual_generation_strategy": visual_generation_strategy, "video_title": text.split("\n\n")[0], "title_language": "ru", "title_source": "APPROVED_HOOK_FALLBACK", "title_review_status": "ACCEPTED_FOR_OPERATOR_EXPORT", "video_title_spoken": False, "subtitle_space_rendering": "NATURAL_UNCLUTTERED_IN_FOCUS", "forbidden_subtitle_space_rendering": ["ARTIFICIAL_BLUR_PANEL", "FOGGY_LOWER_ZONE", "GRADIENT_FADE", "FROSTED_OVERLAY", "TRANSLUCENT_SUBTITLE_PLATE"], "content": content, "prompts": prompts, "reference_sha256": reference_hash, "readme": readme}
    identity = hash_payload(descriptor); root = Path(output_root) / ("nura-operator-export-" + identity[:12]); user_root = root / "user-facing"
    files = {"01_CONTENT_RU.md": content}
    if visual_generation_strategy == "ONE_IMAGE": files["02_IMAGE_PROMPT.txt"] = prompts[0]
    else:
        for index, prompt in enumerate(prompts, 2): files[f"{index:02d}_IMAGE_PROMPT_{index - 1:02d}.txt"] = prompt
    files["README_RU.txt"] = readme
    manifest = {"schema_version": "0.2", "artifact_kind": "nura_simplified_operator_export", "export_id": "nura-operator-export-" + identity[:12], "content_hash": "", "source_finalized_package": {"package_id": package["package_id"], "content_hash": package["content_hash"]}, "source_finalized_handoff": {"handoff_id": handoff["handoff_id"], "content_hash": handoff["content_hash"]}, "source_previous_export": descriptor["source_previous_export"], "video_title": descriptor["video_title"], "title_language": "ru", "title_source": "APPROVED_HOOK_FALLBACK", "title_review_status": "ACCEPTED_FOR_OPERATOR_EXPORT", "video_title_spoken": False, "format": "TALKING_GUIDE", "video_count": 1, "estimated_duration": "25–30 seconds", "duration_status": "ESTIMATED_NOT_MEASURED", "visual_generation_strategy": visual_generation_strategy, "image_count": len(prompts), "subtitle_space_rendering": "NATURAL_UNCLUTTERED_IN_FOCUS", "forbidden_subtitle_space_rendering": descriptor["forbidden_subtitle_space_rendering"], "strategy_justification": justification, "structured_sections_count": 5, "clean_text_round_trip": True, "prompt_count": len(prompts), "reference_copy": {"file": "NURA_REFERENCE.png", "sha256": reference_hash, "exact_bytes": True}, "user_facing_files": list(files) + ["NURA_REFERENCE.png"], "json_required_for_manual_use": False, "provider_call_performed": False, "network_calls": 0, "credentials_required": False, "image_generator_called": False, "heygen_called": False, "renderer_called": False, "production_execution_ready": False}
    manifest["content_hash"] = hash_payload({key: value for key, value in manifest.items() if key != "content_hash"})
    statuses = [_atomic_text(user_root / name, value) for name, value in files.items()]; statuses.extend((_atomic_bytes(user_root / "NURA_REFERENCE.png", reference_bytes), _atomic(root / "operator_export_manifest.json", manifest)))
    return {"status": "COMPLETED" if "COMPLETED" in statuses else "REUSED", "export_id": manifest["export_id"], "export_hash": manifest["content_hash"], "export_path": str(user_root), "manifest_path": str(root / "operator_export_manifest.json"), "visual_generation_strategy": visual_generation_strategy, "prompt_count": len(prompts), "files": manifest["user_facing_files"], "text": text, "content": content, "video_title": manifest["video_title"], "title_source": manifest["title_source"], "prompts": prompts, "readme": readme, "reference_sha256": reference_hash, "network_calls": 0, "credentials_required": False, "provider_called": False}

def reprocess_existing_raw(*, bridge_path: Path, profile_path: Path, original_run_root: Path, output_root: Path, operator_rejection_path: Path) -> dict[str, Any]:
    """Materialize an audited package from an existing provider response; never calls a provider."""
    bridge, profile = load_scene_authority(bridge_path=bridge_path, profile_path=profile_path)
    input_package = build_scene_input(bridge=bridge, profile=profile)
    original_root = Path(original_run_root); raw_path = original_root / "raw_provider_response.json"
    raw_bytes = raw_path.read_bytes(); raw_hash = hashlib.sha256(raw_bytes).hexdigest(); envelope = _read(raw_path)
    request_envelope = _read(original_root / "provider_request.json")
    raw_scenes = _creative(envelope["response"]); scenes, audit = materialize_composed_scenes(raw_scenes)
    rejection = _verified(_read(operator_rejection_path))
    composer = {"composer_id": COMPOSER_ID, "composer_version": COMPOSER_VERSION}
    composer["composer_hash"] = hash_payload(composer)
    identity = hash_payload({"original_raw_hash": raw_hash, "input": input_package["content_hash"], "composer": composer, "operator_rejection": rejection["content_hash"], "scenes": scenes})
    root = Path(output_root) / ("nura-scene-production-offline-" + identity[:12]); scene_path, handoff_path, report_path = root / "scene_production_package.json", root / "manual_heygen_handoff.json", root / "offline_reprocessing_report.json"
    if scene_path.is_file() and handoff_path.is_file() and report_path.is_file():
        package = _read(scene_path); validate_scene_package(package=package, input_package=input_package)
        return {"status": "REUSED", "run_id": root.name, "package": package, "scene_package_path": str(scene_path), "handoff_path": str(handoff_path), "report_path": str(report_path), "network_calls": 0, "credentials_required": False, "provider_called": False}
    package = {"schema_version": SCHEMA_VERSION, "artifact_kind": "nura_scene_production_package", "package_id": "nura-scene-package-" + identity[:12], "project_id": "nura", "status": "READY_FOR_OPERATOR_REVIEW", "operator_review_required": True, "scene_input_hash": input_package["content_hash"], "bridge_hash": bridge["content_hash"], "reference_profile_hash": profile["content_hash"], "operator_rejection": {"content_hash": rejection["content_hash"], "rejected_package": rejection["rejected_package"]}, "provider": envelope["provider"], "provider_prompt_provenance": {"role": "SCENE_SPECIFIC_CREATIVE_DELTA", "original_run_id": original_root.name, "original_request_hash": request_envelope["request_hash"], "original_raw_sha256": raw_hash}, "prompt_composition_mode": "APPLICATION_CANONICAL_COMPOSITION", "composer": composer, "spoken_text_round_trip": input_package["approved_script"]["text"], "scenes": scenes, "warnings": ["SCENE_PROMPTS_REQUIRE_HUMAN_OPERATOR_REVIEW"], "per_scene_images_ready": False, "generated_voice_tracks_ready": False, "heygen_clips_ready": False, "subtitle_timing_ready": False, "production_execution_ready": False, "image_generation_performed": False, "heygen_called": False, "renderer_called": False}
    package["content_hash"] = hash_payload(package); validate_scene_package(package=package, input_package=input_package)
    handoff = {"schema_version": SCHEMA_VERSION, "artifact_kind": "nura_manual_heygen_handoff", "handoff_id": "nura-manual-heygen-handoff-" + package["content_hash"][:12], "scene_package": {"package_id": package["package_id"], "content_hash": package["content_hash"]}, "status": "READY_FOR_OPERATOR_REVIEW", "scene_order": [item["scene_id"] for item in scenes], "voice_selection": {"mode": "MANUAL_IN_HEYGEN", "optional_reference_role": "OPTIONAL_VOICE_REFERENCE", "automatic_transfer": False}, "operator_checklist_ru": ["Проверьте application-composed prompt, safe area и канонический образ NURA.", "Сгенерируйте и вручную выберите изображения внешним инструментом.", "Вручную загрузите выбранные изображения в HeyGen.", "Вручную выберите голос NURA внутри HeyGen."], "direct_heygen_transfer": False, "heygen_called": False, "renderer_called": False, "production_execution_ready": False}
    handoff["content_hash"] = hash_payload(handoff)
    report = {"artifact_kind": "nura_scene_offline_reprocessing_report", "original_run_id": original_root.name, "original_raw_sha256": raw_hash, "raw_unchanged": hashlib.sha256(raw_path.read_bytes()).hexdigest() == raw_hash, "offline_reprocessing": True, "provider_call_performed": False, "network_calls": 0, "credentials_required": False, "original_http_status": envelope["metadata"].get("http_status"), "provider": envelope["provider"], "composer": composer, "scene_audit": audit, "contradiction_count": 0, "canonical_omission_count": sum(len(item["canonical_omissions"]) for item in audit), "content_hash": ""}
    report["content_hash"] = hash_payload({key: value for key, value in report.items() if key != "content_hash"})
    first = [_atomic(scene_path, package), _atomic(handoff_path, handoff), _atomic(report_path, report)]
    return {"status": "COMPLETED" if "COMPLETED" in first else "REUSED", "run_id": root.name, "package": package, "scene_package_path": str(scene_path), "handoff_path": str(handoff_path), "report_path": str(report_path), "network_calls": 0, "credentials_required": False, "provider_called": False}

def run_scene_production(*, bridge_path: Path, profile_path: Path, output_root: Path, provider: SceneProvider | None = None, allow_network: bool = False, reuse_only: bool = False, operator_rejection_path: Path | None = None) -> dict[str, Any]:
    bridge, profile = load_scene_authority(bridge_path=bridge_path, profile_path=profile_path); input_package = build_scene_input(bridge=bridge, profile=profile); request = build_bounded_provider_request(input_package); chosen = provider or DeepSeekSceneProvider(); metadata = chosen.metadata()
    rejection = _verified(_read(operator_rejection_path)) if operator_rejection_path else None
    if rejection and rejection.get("artifact_kind") != "nura_scene_operator_rejection": raise NuraSceneProductionError("INVALID_OPERATOR_REJECTION")
    identity = hash_payload({"input": input_package["content_hash"], "provider": metadata, "request": request, "operator_rejection_hash": rejection.get("content_hash") if rejection else None}); root = Path(output_root) / ("nura-scene-production-" + identity[:12]); scene_path, handoff_path = root / "scene_production_package.json", root / "manual_heygen_handoff.json"
    if scene_path.is_file() and handoff_path.is_file():
        package = _read(scene_path); validate_scene_package(package=package, input_package=input_package); return {"status": "REUSED", "run_id": root.name, "scene_package_path": str(scene_path), "handoff_path": str(handoff_path), "package": package, "network_calls": 0, "credentials_required": False, "provider_called": False}
    if reuse_only: raise NuraSceneProductionError("REUSABLE_ARTIFACT_NOT_FOUND")
    if not metadata.get("fake") and not allow_network: raise NuraSceneProductionError("REAL_PROVIDER_REQUIRES_ALLOW_NETWORK")
    _atomic(root / "scene_production_input.json", input_package); _atomic(root / "provider_request.json", {"request": request, "request_hash": hash_payload(request), "provider": metadata})
    raw, response_meta = chosen.generate(request); _atomic(root / "raw_provider_response.json", {"provider": metadata, "request_hash": hash_payload(request), "metadata": response_meta, "response": raw}); scenes = _creative(raw)
    package = {"schema_version": SCHEMA_VERSION, "artifact_kind": "nura_scene_production_package", "package_id": "nura-scene-package-" + identity[:12], "project_id": "nura", "status": "READY_FOR_OPERATOR_REVIEW", "operator_review_required": True, "scene_input_hash": input_package["content_hash"], "bridge_hash": bridge["content_hash"], "reference_profile_hash": profile["content_hash"], "operator_rejection": None if not rejection else {"content_hash": rejection["content_hash"], "rejected_package": rejection["rejected_package"]}, "provider": metadata, "spoken_text_round_trip": input_package["approved_script"]["text"], "scenes": scenes, "warnings": ["SCENE_PROMPTS_REQUIRE_HUMAN_OPERATOR_REVIEW"], "production_execution_ready": False, "image_generation_performed": False, "heygen_called": False, "renderer_called": False}
    package["content_hash"] = hash_payload(package); validate_scene_package(package=package, input_package=input_package)
    handoff = {"schema_version": SCHEMA_VERSION, "artifact_kind": "nura_manual_heygen_handoff", "handoff_id": "nura-manual-heygen-handoff-" + package["content_hash"][:12], "scene_package": {"package_id": package["package_id"], "content_hash": package["content_hash"]}, "status": "READY_FOR_OPERATOR_REVIEW", "scene_order": [item["scene_id"] for item in scenes], "voice_selection": {"mode": "MANUAL_IN_HEYGEN", "optional_reference_role": "OPTIONAL_VOICE_REFERENCE", "automatic_transfer": False}, "operator_checklist_ru": ["Проверьте каждый prompt, safe area и совпадение с образом NURA.", "Сгенерируйте и вручную выберите изображения внешним инструментом.", "Вручную загрузите выбранные изображения в HeyGen.", "Вручную выберите голос NURA внутри HeyGen.", "Не используйте reference MP3 как voice track текущего эпизода."], "subtitle_source": bridge["subtitle_source"], "timing_status": "PROVISIONAL_NO_AUDIO_MEASUREMENT", "music": bridge["music"], "direct_heygen_transfer": False, "heygen_called": False, "renderer_called": False, "production_execution_ready": False}
    handoff["content_hash"] = hash_payload(handoff); first, second = _atomic(scene_path, package), _atomic(handoff_path, handoff); return {"status": "COMPLETED" if "COMPLETED" in (first, second) else "REUSED", "run_id": root.name, "scene_package_path": str(scene_path), "handoff_path": str(handoff_path), "package": package, "network_calls": 0 if metadata.get("fake") else 1, "credentials_required": not metadata.get("fake"), "provider_called": True}
