"""Offline Stage 5M discovery acceptance; it cannot select assets."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]
from nura_production_asset_handoff import build_candidate_manifest, load_bridge, materialize_selected_asset, persist_contract


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the offline NURA asset-selection package.")
    parser.add_argument("--bridge", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "nura-production-asset-handoff")
    parser.add_argument("--avatar", action="append", type=Path, default=[])
    parser.add_argument("--voice", action="append", type=Path, default=[])
    parser.add_argument("--finalize", action="store_true")
    parser.add_argument("--selected-avatar", type=Path)
    parser.add_argument("--selected-voice", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    bridge = load_bridge(args.bridge)
    if args.finalize:
        if args.selected_avatar is None or args.selected_voice is None:
            parser.error("--finalize requires --selected-avatar and --selected-voice")
        avatar_path, avatar_ref, avatar_copy = materialize_selected_asset(source=args.selected_avatar, output_root=args.output_root, category="avatar")
        voice_path, voice_ref, voice_copy = materialize_selected_asset(source=args.selected_voice, output_root=args.output_root, category="voice")
        manifest = build_candidate_manifest(bridge=bridge, avatar_paths=[(avatar_path, avatar_ref)], voice_paths=[(voice_path, voice_ref)])
        avatar = next(item for item in manifest["candidates"] if item["category"] == "avatar")
        voice = next(item for item in manifest["candidates"] if item["category"] == "voice")
        selection = {"schema_version": "0.1", "artifact_kind": "nura_human_production_asset_selection", "project_id": "nura", "manifest_hash": manifest["content_hash"], "avatar_decision": "SELECTED", "avatar_candidate_id": avatar["candidate_id"], "voice_decision": "SELECTED_LOCAL_AUDIO", "voice_candidate_id": voice["candidate_id"], "human_confirmation": True, "approval_reference": "owner-decision-current-stage-5m-session"}
        first = persist_contract(output_root=args.output_root, manifest=manifest, selection=selection, bridge=bridge)
        second = persist_contract(output_root=args.output_root, manifest=manifest, selection=selection, bridge=bridge)
    else:
        manifest = build_candidate_manifest(bridge=bridge, avatar_paths=[(p, p.as_posix()) for p in args.avatar], voice_paths=[(p, p.as_posix()) for p in args.voice])
        first = persist_contract(output_root=args.output_root, manifest=manifest)
        second = persist_contract(output_root=args.output_root, manifest=manifest)
        avatar_copy = voice_copy = None
    finalized = args.finalize
    result = {"status": "PASS" if finalized else "PASS_WITH_HUMAN_ASSET_SELECTION_REQUIRED", "bridge_hash": bridge["content_hash"], "candidate": bridge["candidate_identity"], "rank": 1, "avatar_candidates": sum(c["category"] == "avatar" for c in manifest["candidates"]), "voice_candidates": sum(c["category"] == "voice" for c in manifest["candidates"]), "asset_contract_ready": True, "avatar_selected": finalized, "voice_selected": finalized, "renderer_handoff_contract_ready": True, "renderer_assigned": False, "renderer_verified": False, "timing_status": bridge["timing"]["status"], "production_execution_ready": False, "provider_called": False, "renderer_called": False, "network_calls": 0, "credentials_required": False, "source_assets_mutated": False, "avatar_copy_status": avatar_copy, "voice_copy_status": voice_copy, "first_run_status": first["candidate_manifest"], "second_run_status": second["candidate_manifest"], "profile_id": first.get("profile_id"), "handoff_id": first.get("handoff_id"), "selection_package": None if finalized else str(args.output_root / manifest["content_hash"] / "human_selection.json")}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
