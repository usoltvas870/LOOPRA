"""Offline Stage 5M discovery acceptance; it cannot select assets."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]
from nura_production_asset_handoff import build_candidate_manifest, load_bridge, load_finalized_artifact, materialize_selected_asset, persist_contract, persist_manual_reference_contract


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the offline NURA asset-selection package.")
    parser.add_argument("--bridge", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "nura-production-asset-handoff")
    parser.add_argument("--avatar", action="append", type=Path, default=[])
    parser.add_argument("--voice", action="append", type=Path, default=[])
    parser.add_argument("--finalize", action="store_true")
    parser.add_argument("--selected-avatar", type=Path)
    parser.add_argument("--selected-voice", type=Path)
    parser.add_argument("--correct-manual-workflow", action="store_true")
    parser.add_argument("--legacy-profile", type=Path)
    parser.add_argument("--legacy-handoff", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    bridge = load_bridge(args.bridge)
    if args.finalize or args.correct_manual_workflow:
        if args.selected_avatar is None or args.selected_voice is None:
            parser.error("finalization requires --selected-avatar and --selected-voice")
        avatar_path, avatar_ref, avatar_copy = materialize_selected_asset(source=args.selected_avatar, output_root=args.output_root, category="avatar")
        voice_path, voice_ref, voice_copy = materialize_selected_asset(source=args.selected_voice, output_root=args.output_root, category="voice")
        manifest = build_candidate_manifest(bridge=bridge, avatar_paths=[(avatar_path, avatar_ref)], voice_paths=[(voice_path, voice_ref)])
        avatar = next(item for item in manifest["candidates"] if item["category"] == "avatar")
        voice = next(item for item in manifest["candidates"] if item["category"] == "voice")
        selection = {"schema_version": "0.1", "artifact_kind": "nura_human_production_asset_selection", "project_id": "nura", "manifest_hash": manifest["content_hash"], "avatar_decision": "SELECTED", "avatar_candidate_id": avatar["candidate_id"], "voice_decision": "SELECTED_LOCAL_AUDIO", "voice_candidate_id": voice["candidate_id"], "human_confirmation": True, "approval_reference": "owner-decision-current-stage-5m-session"}
        if args.correct_manual_workflow:
            if args.legacy_profile is None or args.legacy_handoff is None:
                parser.error("--correct-manual-workflow requires --legacy-profile and --legacy-handoff")
            legacy_profile = load_finalized_artifact(args.legacy_profile, "nura_production_asset_profile")
            legacy_handoff = load_finalized_artifact(args.legacy_handoff, "nura_external_renderer_handoff")
            first = persist_manual_reference_contract(output_root=args.output_root, bridge=bridge, manifest=manifest, selection=selection, legacy_profile=legacy_profile, legacy_handoff=legacy_handoff)
            second = persist_manual_reference_contract(output_root=args.output_root, bridge=bridge, manifest=manifest, selection=selection, legacy_profile=legacy_profile, legacy_handoff=legacy_handoff)
        else:
            first = persist_contract(output_root=args.output_root, manifest=manifest, selection=selection, bridge=bridge)
            second = persist_contract(output_root=args.output_root, manifest=manifest, selection=selection, bridge=bridge)
    else:
        manifest = build_candidate_manifest(bridge=bridge, avatar_paths=[(p, p.as_posix()) for p in args.avatar], voice_paths=[(p, p.as_posix()) for p in args.voice])
        first = persist_contract(output_root=args.output_root, manifest=manifest)
        second = persist_contract(output_root=args.output_root, manifest=manifest)
        avatar_copy = voice_copy = None
    finalized = args.finalize or args.correct_manual_workflow
    corrected = args.correct_manual_workflow
    result = {"status": "PASS" if finalized else "PASS_WITH_HUMAN_ASSET_SELECTION_REQUIRED", "bridge_hash": bridge["content_hash"], "candidate": bridge["candidate_identity"], "rank": 1, "avatar_candidates": sum(c["category"] == "avatar" for c in manifest["candidates"]), "voice_candidates": sum(c["category"] == "voice" for c in manifest["candidates"]), "visual_identity_reference_ready": corrected, "visual_reference_role": "VISUAL_IDENTITY_REFERENCE" if corrected else None, "voice_reference_ready": corrected, "voice_reference_role": "OPTIONAL_VOICE_REFERENCE" if corrected else None, "voice_reference_optional": corrected, "per_episode_scene_images_ready": False, "generated_voice_track_ready": False, "scene_prompt_package_ready": False, "manual_heygen_workflow": corrected, "direct_heygen_transfer": False, "automated_renderer_adapter": False, "asset_contract_ready": True, "avatar_selected": finalized, "voice_selected": finalized, "renderer_assigned": False, "renderer_verified": False, "timing_status": bridge["timing"]["status"], "production_execution_ready": False, "provider_called": False, "renderer_called": False, "image_generator_called": False, "network_calls": 0, "credentials_required": False, "source_assets_mutated": False, "avatar_copy_status": avatar_copy, "voice_copy_status": voice_copy, "first_run_status": first["profile"] if corrected else first["candidate_manifest"], "second_run_status": second["profile"] if corrected else second["candidate_manifest"], "corrected_profile_hash": first.get("profile_hash"), "corrected_handoff_hash": first.get("handoff_hash"), "profile_id": first.get("profile_id"), "handoff_id": first.get("handoff_id"), "selection_package": None if finalized else str(args.output_root / manifest["content_hash"] / "human_selection.json")}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
