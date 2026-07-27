import json
import sys
import wave
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

from nura_production_asset_handoff import (NuraProductionAssetHandoffError, build_candidate_manifest, build_manual_reference_profile_and_handoff, build_profile_and_handoff, inspect_candidate, load_bridge, materialize_selected_asset, persist_contract, persist_manual_reference_contract, selection_template)
from nura_script_episode_bridge import hash_payload


def bridge() -> dict:
    value = {"artifact_kind": "nura_script_to_production_bridge", "bridge_id": "b1", "candidate_identity": {"video_id": "v1"}, "original_rank": 1, "script_format": "TALKING_GUIDE", "language": "ru", "production_input_ready": True, "production_execution_ready": False, "character_avatar_requirement": {"character_id": "nura"}, "music": {"role": "SECONDARY_OPTIONAL"}, "spoken_script": {"text": "Точный текст"}, "subtitle_source": {"status": "EXACT_APPROVED_TEXT"}, "timing": {"status": "PROVISIONAL"}}
    value["content_hash"] = hash_payload(value)
    return value


def assets(tmp_path: Path):
    image = tmp_path / "avatar.png"; Image.new("RGBA", (100, 200), "white").save(image)
    audio = tmp_path / "voice.wav"
    with wave.open(str(audio), "wb") as output:
        output.setnchannels(1); output.setsampwidth(2); output.setframerate(8000); output.writeframes(b"\0\0" * 8000)
    return image, audio


def test_discovers_without_selection_and_reuses(tmp_path: Path):
    image, audio = assets(tmp_path)
    manifest = build_candidate_manifest(bridge=bridge(), avatar_paths=[(image, "runtime/nura/avatar.png")], voice_paths=[(audio, "runtime/nura/voice.wav")])
    assert len(manifest["candidates"]) == 2
    first = persist_contract(output_root=tmp_path / "runtime", manifest=manifest)
    second = persist_contract(output_root=tmp_path / "runtime", manifest=manifest)
    assert first["selection_required"] is True and second["candidate_manifest"] == "REUSED"
    assert selection_template(manifest)["human_confirmation"] is False


def test_explicit_approved_selection_builds_renderer_neutral_handoff(tmp_path: Path):
    image, audio = assets(tmp_path)
    manifest = build_candidate_manifest(bridge=bridge(), avatar_paths=[(image, "runtime/nura/avatar.png")], voice_paths=[(audio, "runtime/nura/voice.wav")])
    avatar, voice = manifest["candidates"]
    selection = {"manifest_hash": manifest["content_hash"], "human_confirmation": True, "approval_reference": "owner-decision-1", "avatar_decision": "SELECTED", "avatar_candidate_id": avatar["candidate_id"], "voice_decision": "SELECTED_LOCAL_AUDIO", "voice_candidate_id": voice["candidate_id"]}
    profile, handoff = build_profile_and_handoff(bridge=bridge(), manifest=manifest, selection=selection)
    assert profile["avatar"]["status"] == "SELECTED"
    assert handoff["script"]["text"] == "Точный текст"
    assert handoff["renderer"]["assignment"] == "UNASSIGNED"
    assert handoff["production_execution_ready"] is False


def test_rejects_missing_approval_unsafe_path_and_bad_bridge(tmp_path: Path):
    image, audio = assets(tmp_path)
    manifest = build_candidate_manifest(bridge=bridge(), avatar_paths=[(image, "runtime/nura/avatar.png")], voice_paths=[(audio, "runtime/nura/voice.wav")])
    avatar, voice = manifest["candidates"]
    selection = {"manifest_hash": manifest["content_hash"], "human_confirmation": False, "approval_reference": "x", "avatar_decision": "SELECTED", "avatar_candidate_id": avatar["candidate_id"], "voice_decision": "SELECTED_LOCAL_AUDIO", "voice_candidate_id": voice["candidate_id"]}
    with pytest.raises(NuraProductionAssetHandoffError, match="HUMAN_APPROVAL_REQUIRED"):
        build_profile_and_handoff(bridge=bridge(), manifest=manifest, selection=selection)
    manifest["candidates"][0]["reference"] = "C:/Users/a/avatar.png"
    selection["human_confirmation"] = True
    with pytest.raises(NuraProductionAssetHandoffError, match="UNSAFE_CANONICAL"):
        build_profile_and_handoff(bridge=bridge(), manifest=manifest, selection=selection)
    path = tmp_path / "bridge.json"; path.write_text(json.dumps(bridge()), encoding="utf-8")
    assert load_bridge(path)["bridge_id"] == "b1"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(NuraProductionAssetHandoffError, match="HASH_MISMATCH"):
        load_bridge(path)


def test_materializes_exact_selected_asset_without_external_path_dependency(tmp_path: Path):
    image, _ = assets(tmp_path)
    destination, reference, first = materialize_selected_asset(source=image, output_root=tmp_path / "runtime", category="avatar")
    repeated, repeated_reference, second = materialize_selected_asset(source=image, output_root=tmp_path / "runtime", category="avatar")
    assert first == "COPIED" and second == "REUSED"
    assert destination == repeated and reference == repeated_reference
    assert reference.startswith("assets/nura/avatar/") and "C:" not in reference
    assert image.read_bytes() == destination.read_bytes()


def test_corrects_legacy_assets_to_manual_reference_semantics(tmp_path: Path):
    image, audio = assets(tmp_path)
    manifest = build_candidate_manifest(bridge=bridge(), avatar_paths=[(image, "assets/nura/avatar.png")], voice_paths=[(audio, "assets/nura/voice.wav")])
    avatar, voice = manifest["candidates"]
    selection = {"manifest_hash": manifest["content_hash"], "human_confirmation": True, "approval_reference": "owner-decision-1", "avatar_decision": "SELECTED", "avatar_candidate_id": avatar["candidate_id"], "voice_decision": "SELECTED_LOCAL_AUDIO", "voice_candidate_id": voice["candidate_id"]}
    legacy_profile, legacy_handoff = build_profile_and_handoff(bridge=bridge(), manifest=manifest, selection=selection)
    profile, handoff = build_manual_reference_profile_and_handoff(bridge=bridge(), manifest=manifest, selection=selection, legacy_profile=legacy_profile, legacy_handoff=legacy_handoff)
    assert profile["schema_version"] == "0.2" and profile["content_hash"] != legacy_profile["content_hash"]
    assert profile["visual_identity_reference"]["role"] == "VISUAL_IDENTITY_REFERENCE"
    assert profile["visual_identity_reference"]["per_episode_scene_asset"] is False
    assert profile["voice_reference"]["optional"] is True
    assert profile["voice_reference"]["generated_voice_track"] is False
    assert handoff["artifact_kind"] == "nura_manual_production_reference_handoff"
    assert handoff["manual_workflow"]["direct_heygen_transfer"] is False
    assert handoff["renderer"]["automated_adapter_required_for_loopra_0_5"] is False
    assert handoff["production_execution_ready"] is False
    first = persist_manual_reference_contract(output_root=tmp_path / "runtime", bridge=bridge(), manifest=manifest, selection=selection, legacy_profile=legacy_profile, legacy_handoff=legacy_handoff)
    second = persist_manual_reference_contract(output_root=tmp_path / "runtime", bridge=bridge(), manifest=manifest, selection=selection, legacy_profile=legacy_profile, legacy_handoff=legacy_handoff)
    assert first["profile"] == "COMPLETED" and second["profile"] == "REUSED"


def test_optional_voice_absence_does_not_block_manual_reference_contract(tmp_path: Path):
    image, audio = assets(tmp_path)
    manifest = build_candidate_manifest(bridge=bridge(), avatar_paths=[(image, "assets/nura/avatar.png")], voice_paths=[(audio, "assets/nura/voice.wav")])
    avatar, voice = manifest["candidates"]
    legacy_selection = {"manifest_hash": manifest["content_hash"], "human_confirmation": True, "approval_reference": "owner-decision-1", "avatar_decision": "SELECTED", "avatar_candidate_id": avatar["candidate_id"], "voice_decision": "SELECTED_LOCAL_AUDIO", "voice_candidate_id": voice["candidate_id"]}
    legacy_profile, legacy_handoff = build_profile_and_handoff(bridge=bridge(), manifest=manifest, selection=legacy_selection)
    selection = {**legacy_selection, "voice_decision": "NOT_PROVIDED", "voice_candidate_id": None}
    profile, handoff = build_manual_reference_profile_and_handoff(bridge=bridge(), manifest=manifest, selection=selection, legacy_profile=legacy_profile, legacy_handoff=legacy_handoff)
    assert profile["voice_reference"]["status"] == "NOT_PROVIDED"
    assert profile["voice_reference"]["optional"] is True
    assert handoff["manual_workflow"]["operator_selects_heygen_voice"] is True
