"""Offline Stage 5M discovery acceptance; it cannot select assets."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]
from nura_production_asset_handoff import build_candidate_manifest, load_bridge, persist_contract


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the offline NURA asset-selection package.")
    parser.add_argument("--bridge", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "nura-production-asset-handoff")
    parser.add_argument("--avatar", action="append", type=Path, default=[])
    parser.add_argument("--voice", action="append", type=Path, default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    bridge = load_bridge(args.bridge)
    manifest = build_candidate_manifest(bridge=bridge, avatar_paths=[(p, p.as_posix()) for p in args.avatar], voice_paths=[(p, p.as_posix()) for p in args.voice])
    first = persist_contract(output_root=args.output_root, manifest=manifest)
    second = persist_contract(output_root=args.output_root, manifest=manifest)
    result = {"status": "PASS_WITH_HUMAN_ASSET_SELECTION_REQUIRED", "bridge_hash": bridge["content_hash"], "candidate": bridge["candidate_identity"], "rank": 1, "avatar_candidates": sum(c["category"] == "avatar" for c in manifest["candidates"]), "voice_candidates": sum(c["category"] == "voice" for c in manifest["candidates"]), "asset_contract_ready": True, "avatar_selected": False, "voice_selected": False, "renderer_handoff_contract_ready": True, "renderer_assigned": False, "renderer_verified": False, "timing_status": bridge["timing"]["status"], "production_execution_ready": False, "provider_called": False, "renderer_called": False, "network_calls": 0, "credentials_required": False, "source_assets_mutated": False, "first_run_status": first["candidate_manifest"], "second_run_status": second["candidate_manifest"], "selection_package": str(args.output_root / manifest["content_hash"] / "human_selection.json")}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
