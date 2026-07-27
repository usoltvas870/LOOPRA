import json, sys
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]; sys.path[:0] = [str(ROOT / "src")]
from nura_scene_production import FakeSceneProvider, NuraSceneProductionError, compose_canonical_prompts, finalize_scene_review, record_operator_rejection, record_owner_scene_decision, reprocess_existing_raw, run_scene_production
BRIDGE = ROOT / "data/nura-script-episode-bridge/nura-script-production-bridge-79d69d42079e/script_to_production_bridge.json"
PROFILE = ROOT / "data/nura-production-asset-handoff/8fc6df087d0aee2b5056e3c79bc4fbd90f1f187fdf168f1f2fb32943f8cc0071/production_reference_profile.json"
OLD = ROOT / "data/nura-scene-production-real/nura-scene-production-84aa0ff087b1"
REVIEW = ROOT / "data/nura-scene-production-real/nura-scene-production-offline-e6c0cee822dc"
def _decision(tmp_path: Path) -> Path:
    path = tmp_path / "decision.json"; record_operator_rejection(rejected_package_path=OLD / "scene_production_package.json", raw_response_path=OLD / "raw_provider_response.json", output_path=path); return path
def test_corrected_fake_package_has_three_talking_avatar_scenes_and_reuses(tmp_path: Path) -> None:
    decision = _decision(tmp_path); first = run_scene_production(bridge_path=BRIDGE, profile_path=PROFILE, output_root=tmp_path / "out", provider=FakeSceneProvider(), operator_rejection_path=decision); second = run_scene_production(bridge_path=BRIDGE, profile_path=PROFILE, output_root=tmp_path / "out", provider=FakeSceneProvider(), reuse_only=True, operator_rejection_path=decision)
    assert first["status"] == "COMPLETED" and second["status"] == "REUSED" and [s["source_block_ids"] for s in first["package"]["scenes"]] == [["block-1"], ["block-2", "block-3"], ["block-4", "block-5"]]
    for scene in first["package"]["scenes"]: assert "dark curly hair" in scene["positive_prompt"].lower() and scene["operator_note_ru"] and "safe area" in scene["safe_area_guidance"].lower()
def test_rejection_is_immutable_and_records_all_old_scenes(tmp_path: Path) -> None:
    path = _decision(tmp_path); value = json.loads(path.read_text(encoding="utf-8")); assert len(value["scene_decisions"]) == 5 and value["reviewer"]["human_confirmation"] is True
    assert _decision(tmp_path) == path


@pytest.mark.parametrize("field,value,error", [
    ("positive_prompt", "generic woman with light brown hair, photorealistic", "TALKING_AVATAR_OR_IDENTITY_VIOLATION"),
    ("positive_prompt", "NURA with a phone, looking down", "TALKING_AVATAR_OR_IDENTITY_VIOLATION"),
    ("positive_prompt", "NURA in rear view and side profile, full body", "TALKING_AVATAR_OR_IDENTITY_VIOLATION"),
    ("purpose", "NURA relives her personal burnout", "TALKING_AVATAR_OR_IDENTITY_VIOLATION"),
    ("operator_note_ru", "English note", "OPERATOR_NOTE_RUSSIAN_REQUIRED"),
    ("safe_area_guidance", "missing", "SAFE_AREA_GUIDANCE_REQUIRED"),
    ("camera_direction", "eye-level camera without viewer address", "TALKING_AVATAR_VIEWER_ADDRESS_REQUIRED"),
    ("wardrobe_guidance", "different dark evening dress", "SCENE_CONTINUITY_MISMATCH"),
    ("environment_background", "different domestic sofa and lamp", "SCENE_CONTINUITY_MISMATCH"),
    ("prompt_language", "ru", "SCENE_LANGUAGE_DECLARATION_REQUIRED"),
])
def test_rejects_known_old_defect_fixtures(tmp_path: Path, field: str, value: str, error: str) -> None:
    decision = _decision(tmp_path)
    class Bad(FakeSceneProvider):
        def generate(self, request):
            raw, meta = super().generate(request); raw["scenes"][0][field] = value; return raw, meta
    with pytest.raises(NuraSceneProductionError, match=error): run_scene_production(bridge_path=BRIDGE, profile_path=PROFILE, output_root=tmp_path / field, provider=Bad(), operator_rejection_path=decision)


def test_rejects_five_scenes(tmp_path: Path) -> None:
    decision = _decision(tmp_path)
    class Bad(FakeSceneProvider):
        def generate(self, request):
            raw, meta = super().generate(request); raw["scenes"].extend(raw["scenes"][-2:]); return raw, meta
    with pytest.raises(NuraSceneProductionError, match="THREE_SCENES_REQUIRED"):
        run_scene_production(bridge_path=BRIDGE, profile_path=PROFILE, output_root=tmp_path / "five", provider=Bad(), operator_rejection_path=decision)
def test_real_provider_requires_explicit_network_permission(tmp_path: Path) -> None:
    with pytest.raises(NuraSceneProductionError, match="REAL_PROVIDER_REQUIRES_ALLOW_NETWORK"): run_scene_production(bridge_path=BRIDGE, profile_path=PROFILE, output_root=tmp_path, operator_rejection_path=_decision(tmp_path))


def test_composer_allows_omissions_but_preserves_delta_and_negatives() -> None:
    scene = FakeSceneProvider().generate({"approved_blocks": []})[0]["scenes"][0]
    scene["positive_prompt"] = "woman around 30 with dark curly hair, ivory blazer"
    scene["negative_prompt"] = "no phone, no text"
    positive, negative, omissions = compose_canonical_prompts(scene)
    assert "nura" in positive.lower() and "vertical 9:16" in positive.lower()
    assert "dark curly hair" in positive.lower() and "talking-avatar lip-sync" in positive.lower()
    assert "no phone" in negative and negative.lower().count("no text") == 1
    assert omissions == ["nura", "vertical 9:16"] and scene["positive_prompt"] == "woman around 30 with dark curly hair, ivory blazer"


def test_existing_raw_reprocesses_offline_and_reuses(tmp_path: Path) -> None:
    original = ROOT / "data/nura-scene-production-real/nura-scene-production-3dbee3f3c123"
    raw_before = (original / "raw_provider_response.json").read_bytes()
    decision = _decision(tmp_path)
    first = reprocess_existing_raw(bridge_path=BRIDGE, profile_path=PROFILE, original_run_root=original, output_root=tmp_path / "out", operator_rejection_path=decision)
    second = reprocess_existing_raw(bridge_path=BRIDGE, profile_path=PROFILE, original_run_root=original, output_root=tmp_path / "out", operator_rejection_path=decision)
    assert first["status"] == "COMPLETED" and second["status"] == "REUSED"
    assert first["network_calls"] == 0 and first["credentials_required"] is False
    assert (original / "raw_provider_response.json").read_bytes() == raw_before
    assert all("vertical 9:16" in scene["composed_positive_prompt"].lower() for scene in first["package"]["scenes"])


def test_owner_finalization_preserves_prompts_and_reuses(tmp_path: Path) -> None:
    decision = tmp_path / "owner.json"
    record_owner_scene_decision(package_path=REVIEW / "scene_production_package.json", output_path=decision, reviewed_at="2026-07-27T00:00:00+00:00")
    kwargs = {"package_path": REVIEW / "scene_production_package.json", "handoff_path": REVIEW / "manual_heygen_handoff.json", "bridge_path": BRIDGE, "profile_path": PROFILE, "decision_path": decision, "output_root": tmp_path / "final"}
    first, second = finalize_scene_review(**kwargs), finalize_scene_review(**kwargs)
    assert first["status"] == "COMPLETED" and second["status"] == "REUSED"
    assert first["network_calls"] == 0 and first["provider_called"] is False
    package = first["package"]
    assert package["ready_for_external_image_generation"] is True and package["production_execution_ready"] is False
    for scene in package["scenes"]:
        assert scene["original_provider_creative_delta"] == scene["provider_creative_prompt"]
        assert scene["original_application_composed_prompt"] == scene["composed_positive_prompt"]
        assert " not " not in f" {scene['final_human_approved_positive_prompt'].lower()} "
        assert " no " not in f" {scene['final_human_approved_positive_prompt'].lower()} "
        assert "childish cartoon style" in scene["final_human_approved_negative_prompt"]
        assert "15%" in scene["safe_area_guidance"] and "25%" in scene["safe_area_guidance"]


def test_owner_finalization_handoff_is_self_contained(tmp_path: Path) -> None:
    decision = tmp_path / "owner.json"
    record_owner_scene_decision(package_path=REVIEW / "scene_production_package.json", output_path=decision, reviewed_at="2026-07-27T00:00:00+00:00")
    result = finalize_scene_review(package_path=REVIEW / "scene_production_package.json", handoff_path=REVIEW / "manual_heygen_handoff.json", bridge_path=BRIDGE, profile_path=PROFILE, decision_path=decision, output_root=tmp_path / "final")
    handoff = json.loads(Path(result["handoff_path"]).read_text(encoding="utf-8"))
    assert handoff["subtitle_source"] == "EXACT_APPROVED_TEXT" and handoff["subtitle_timing_status"] == "PROVISIONAL_NO_AUDIO_MEASUREMENT"
    assert handoff["music_role"] == "SECONDARY_OPTIONAL" and handoff["music_track"] is None
    assert all(scene["selected_image_reference"] is None and scene["heygen_clip_reference"] is None for scene in handoff["scenes"])


def test_conflicting_owner_decision_is_rejected(tmp_path: Path) -> None:
    decision = tmp_path / "owner.json"
    record_owner_scene_decision(package_path=REVIEW / "scene_production_package.json", output_path=decision, reviewed_at="2026-07-27T00:00:00+00:00")
    with pytest.raises(NuraSceneProductionError, match="CONFLICTING_SCENE_PACKAGE_REUSE"):
        record_owner_scene_decision(package_path=REVIEW / "scene_production_package.json", output_path=decision, reviewed_at="2026-07-27T00:00:01+00:00")
