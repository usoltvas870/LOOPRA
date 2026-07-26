"""Stage 5L offline bridge from an approved NURA script to future production.

This is deliberately a pre-episode artifact.  The existing Episode Input
Package is a comic/image-sequence contract and must not be used to invent
frames, bubbles, timings, or rendered media for a TALKING_GUIDE.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


BRIDGE_SCHEMA_VERSION = "0.1"
BUILDER_VERSION = "0.1"
TARGET_PRODUCTION_FORMAT = "TALKING_GUIDE_AVATAR"


class NuraScriptEpisodeBridgeError(ValueError):
    pass


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def hash_payload(value: dict[str, Any]) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise NuraScriptEpisodeBridgeError("INVALID_RUNTIME_ARTIFACT") from error
    if not isinstance(value, dict):
        raise NuraScriptEpisodeBridgeError("RUNTIME_ARTIFACT_OBJECT_REQUIRED")
    return value


def _verify_hash(value: dict[str, Any], field: str) -> None:
    stored = value.get(field)
    payload = {key: item for key, item in value.items() if key != field}
    if not isinstance(stored, str) or stored != hash_payload(payload):
        raise NuraScriptEpisodeBridgeError(f"{field.upper()}_MISMATCH")


def _load_linked(path: Path, name: str) -> dict[str, Any]:
    candidate = path.parent / name
    if not candidate.is_file():
        raise NuraScriptEpisodeBridgeError(f"LINKED_{name.upper().replace('.', '_')}_NOT_FOUND")
    return _read(candidate)


def load_finalized_script_inputs(*, finalized_review_path: Path, approved_script_path: Path,
                                 script_input_path: Path | None = None,
                                 provider_output_path: Path | None = None,
                                 production_brief_path: Path | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Load and verify the immutable Stage 5K authority chain without mutation."""
    review = _read(finalized_review_path)
    script = _read(approved_script_path)
    _verify_hash(review, "review_hash")
    _verify_hash(script, "content_hash")
    if review.get("review_kind") != "nura_finalized_human_script_review" or review.get("decision") != "APPROVED_FOR_EPISODE_BRIDGE":
        raise NuraScriptEpisodeBridgeError("FINALIZED_REVIEW_NOT_APPROVED_FOR_EPISODE_BRIDGE")
    reviewer = review.get("reviewer")
    if not isinstance(reviewer, dict) or reviewer.get("human_confirmation") is not True:
        raise NuraScriptEpisodeBridgeError("HUMAN_CONFIRMATION_REQUIRED")
    if script.get("script_kind") != "nura_human_approved_script" or script.get("status") != "HUMAN_APPROVED":
        raise NuraScriptEpisodeBridgeError("HUMAN_APPROVED_SCRIPT_REQUIRED")
    if script.get("episode_bridge_ready") is not True or review.get("episode_bridge_ready") is not True:
        raise NuraScriptEpisodeBridgeError("EPISODE_BRIDGE_READINESS_REQUIRED")
    if review.get("final_script_id") != script.get("script_id") or review.get("final_script_hash") != script.get("content_hash"):
        raise NuraScriptEpisodeBridgeError("FINAL_REVIEW_SCRIPT_IDENTITY_MISMATCH")
    if review.get("provider_output_hash") != script.get("source_provider_script", {}).get("content_hash"):
        raise NuraScriptEpisodeBridgeError("PROVIDER_PROVENANCE_MISMATCH")
    if script_input_path is None:
        script_input_path = approved_script_path.parent / "script_input.json"
    if provider_output_path is None:
        provider_output_path = approved_script_path.parent / "validated_script_output.json"
    script_input = _read(script_input_path)
    provider_output = _read(provider_output_path)
    if script.get("script_input_hash") != script_input.get("content_hash"):
        raise NuraScriptEpisodeBridgeError("SCRIPT_INPUT_PROVENANCE_MISMATCH")
    if provider_output.get("content_hash") != review.get("provider_output_hash"):
        raise NuraScriptEpisodeBridgeError("PROVIDER_OUTPUT_PROVENANCE_MISMATCH")
    if production_brief_path is None:
        raise NuraScriptEpisodeBridgeError("PRODUCTION_BRIEF_PATH_REQUIRED")
    brief = _read(production_brief_path)
    if script.get("provenance", {}).get("brief_hash") != brief.get("brief_hash"):
        raise NuraScriptEpisodeBridgeError("PRODUCTION_BRIEF_PROVENANCE_MISMATCH")
    if script.get("candidate_identity") != brief.get("candidate_identity") or script.get("original_rank") != brief.get("original_rank"):
        raise NuraScriptEpisodeBridgeError("CANDIDATE_OR_RANK_PROVENANCE_MISMATCH")
    return review, script, brief


def _spoken_blocks(script: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    payload = script.get("payload")
    if not isinstance(payload, dict) or not isinstance(payload.get("text"), str) or not isinstance(payload.get("blocks"), list):
        raise NuraScriptEpisodeBridgeError("INVALID_HUMAN_APPROVED_PAYLOAD")
    blocks = payload["blocks"]
    if len(blocks) != 5:
        raise NuraScriptEpisodeBridgeError("FIVE_APPROVED_SPOKEN_BLOCKS_REQUIRED")
    result: list[dict[str, Any]] = []
    for index, block in enumerate(blocks):
        if not isinstance(block, dict) or not isinstance(block.get("kind"), str) or not isinstance(block.get("text"), str) or not block["text"]:
            raise NuraScriptEpisodeBridgeError("INVALID_APPROVED_SPOKEN_BLOCK")
        result.append({"ordinal": index + 1, "kind": block["kind"], "text": block["text"]})
    reconstructed = "\n\n".join(block["text"] for block in result)
    if reconstructed != payload["text"]:
        raise NuraScriptEpisodeBridgeError("APPROVED_TEXT_BLOCK_ROUND_TRIP_MISMATCH")
    if result[0]["kind"] != "hook" or result[0]["text"] != script.get("payload", {}).get("blocks", [{}])[0].get("text"):
        raise NuraScriptEpisodeBridgeError("APPROVED_HOOK_NOT_FIRST")
    return result, reconstructed


def build_script_to_production_bridge(*, finalized_review: dict[str, Any], approved_script: dict[str, Any], production_brief: dict[str, Any]) -> dict[str, Any]:
    """Build the canonical, non-rendering Stage 5L input artifact."""
    blocks, full_text = _spoken_blocks(approved_script)
    if approved_script.get("format") != "TALKING_GUIDE" or approved_script.get("language") != "ru":
        raise NuraScriptEpisodeBridgeError("ONLY_RANK_ONE_RUSSIAN_TALKING_GUIDE_SUPPORTED")
    if approved_script.get("original_rank") != 1:
        raise NuraScriptEpisodeBridgeError("ONLY_RANK_ONE_SUPPORTED")
    identity = {
        "schema_version": BRIDGE_SCHEMA_VERSION,
        "builder_version": BUILDER_VERSION,
        "finalized_review_hash": finalized_review["review_hash"],
        "approved_script_hash": approved_script["content_hash"],
        "production_brief_hash": production_brief["brief_hash"],
        "target_production_format": TARGET_PRODUCTION_FORMAT,
    }
    bridge_id = "nura-script-production-bridge-" + hash_payload(identity)[:12]
    bridge = {
        "schema_version": BRIDGE_SCHEMA_VERSION,
        "artifact_kind": "nura_script_to_production_bridge",
        "builder_version": BUILDER_VERSION,
        "bridge_id": bridge_id,
        "candidate_identity": approved_script["candidate_identity"],
        "original_rank": approved_script["original_rank"],
        "script_format": "TALKING_GUIDE",
        "language": "ru",
        "target": {"production_format": TARGET_PRODUCTION_FORMAT, "renderer_assignment": "UNASSIGNED", "rendering_performed": False},
        "spoken_script": {"text": full_text, "blocks": blocks},
        "subtitle_source": {"status": "EXACT_APPROVED_TEXT", "text": full_text, "segments": blocks, "timing": "PROVISIONAL_NO_AUDIO_MEASUREMENT"},
        "timing": {"status": "PROVISIONAL", "measured_audio_duration_sec": None, "cues": []},
        "character_avatar_requirement": {"character_id": "nura", "avatar_asset_reference": None, "status": "UNRESOLVED_REQUIRED"},
        "voice_requirement": {"voice_asset_reference": None, "status": "UNRESOLVED_REQUIRED"},
        "music": {"role": "SECONDARY_OPTIONAL", "track_reference": None},
        "requirements": ["NURA_AVATAR_ASSET", "VOICE_ASSET", "EXTERNAL_RENDERER_ADAPTER", "AUDIO_TIMING_ALIGNMENT"],
        "provenance": {
            "production_brief": {"brief_id": production_brief.get("brief_id"), "brief_hash": production_brief["brief_hash"]},
            "script_input": {"content_hash": approved_script["script_input_hash"]},
            "provider_output": {"script_id": approved_script["source_provider_script"]["script_id"], "content_hash": approved_script["source_provider_script"]["content_hash"]},
            "finalized_human_script_review": {"finalization_identity": finalized_review["finalization_identity"], "review_hash": finalized_review["review_hash"]},
            "human_approved_script": {"script_id": approved_script["script_id"], "content_hash": approved_script["content_hash"]},
        },
        "production_input_ready": True,
        "production_execution_ready": False,
        "warnings": [],
    }
    bridge["content_hash"] = hash_payload(bridge)
    return bridge


def persist_bridge(*, output_root: Path, bridge: dict[str, Any]) -> tuple[Path, str]:
    """Atomically persist one immutable bridge and reuse only identical content."""
    path = Path(output_root) / bridge["bridge_id"] / "script_to_production_bridge.json"
    text = _json(bridge)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise NuraScriptEpisodeBridgeError("CONFLICTING_BRIDGE_REUSE")
        return path, "REUSED"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    try:
        os.link(temporary, path)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != text:
            raise NuraScriptEpisodeBridgeError("CONFLICTING_BRIDGE_REUSE")
    finally:
        temporary.unlink(missing_ok=True)
    return path, "COMPLETED"


def build_and_persist_bridge(*, finalized_review_path: Path, approved_script_path: Path,
                             production_brief_path: Path, output_root: Path) -> dict[str, Any]:
    review, script, brief = load_finalized_script_inputs(finalized_review_path=finalized_review_path, approved_script_path=approved_script_path, production_brief_path=production_brief_path)
    bridge = build_script_to_production_bridge(finalized_review=review, approved_script=script, production_brief=brief)
    path, status = persist_bridge(output_root=output_root, bridge=bridge)
    return {"status": status, "bridge_path": str(path), "bridge": bridge, "provider_called": False, "renderer_called": False, "network_calls": 0, "credentials_required": False}
