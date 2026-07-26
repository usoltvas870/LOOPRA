import json
import sys
import wave
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

from nura_production_asset_handoff import (NuraProductionAssetHandoffError, build_candidate_manifest, build_profile_and_handoff, inspect_candidate, load_bridge, persist_contract, selection_template)
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
