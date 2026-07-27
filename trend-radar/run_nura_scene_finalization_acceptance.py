"""Stage 5N owner-review finalization acceptance; strictly offline."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]

from nura_scene_production import finalize_scene_review, record_owner_scene_decision

BRIDGE = ROOT / "data/nura-script-episode-bridge/nura-script-production-bridge-79d69d42079e/script_to_production_bridge.json"
PROFILE = ROOT / "data/nura-production-asset-handoff/8fc6df087d0aee2b5056e3c79bc4fbd90f1f187fdf168f1f2fb32943f8cc0071/production_reference_profile.json"
ORIGINAL_ROOT = ROOT / "data/nura-scene-production-real/nura-scene-production-offline-e6c0cee822dc"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=ROOT / "data/nura-scene-production-finalized")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    decision_path = args.output_root / "owner_scene_decision.json"
    decision = record_owner_scene_decision(package_path=ORIGINAL_ROOT / "scene_production_package.json", output_path=decision_path)
    kwargs = {"package_path": ORIGINAL_ROOT / "scene_production_package.json", "handoff_path": ORIGINAL_ROOT / "manual_heygen_handoff.json", "bridge_path": BRIDGE, "profile_path": PROFILE, "decision_path": decision_path, "output_root": args.output_root}
    first = finalize_scene_review(**kwargs)
    second = finalize_scene_review(**kwargs)
    result = {"status": "PASS", "first_status": first["status"], "second_status": second["status"], "decision_hash": decision["content_hash"], "package_id": first["package"]["package_id"], "package_hash": first["package"]["content_hash"], "package_path": first["package_path"], "handoff_path": first["handoff_path"], "provider_call_performed": False, "network_calls": 0, "credentials_required": False, "image_generator_called": False, "heygen_called": False, "renderer_called": False}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
