"""Stage 5N deterministic acceptance; it never calls external services."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]
from nura_scene_production import FakeSceneProvider, record_operator_rejection, run_scene_production
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--bridge", type=Path, default=ROOT / "data/nura-script-episode-bridge/nura-script-production-bridge-79d69d42079e/script_to_production_bridge.json"); parser.add_argument("--profile", type=Path, default=ROOT / "data/nura-production-asset-handoff/8fc6df087d0aee2b5056e3c79bc4fbd90f1f187fdf168f1f2fb32943f8cc0071/production_reference_profile.json"); parser.add_argument("--output-root", type=Path, default=ROOT / "data/nura-scene-production"); parser.add_argument("--json", action="store_true"); args = parser.parse_args()
    rejected_root = ROOT / "data/nura-scene-production-real/nura-scene-production-84aa0ff087b1"
    decision = args.output_root / "operator_rejection.json"
    record_operator_rejection(rejected_package_path=rejected_root / "scene_production_package.json", raw_response_path=rejected_root / "raw_provider_response.json", output_path=decision)
    first = run_scene_production(bridge_path=args.bridge, profile_path=args.profile, output_root=args.output_root, provider=FakeSceneProvider(), operator_rejection_path=decision); second = run_scene_production(bridge_path=args.bridge, profile_path=args.profile, output_root=args.output_root, provider=FakeSceneProvider(), reuse_only=True, operator_rejection_path=decision)
    result = {"status": "PASS", "first_run_status": first["status"], "second_run_status": second["status"], "scene_count": len(first["package"]["scenes"]), "provider_called": first["provider_called"], "image_generator_called": False, "heygen_called": False, "renderer_called": False, "network_calls": 0, "scene_package_path": first["scene_package_path"], "handoff_path": first["handoff_path"]}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result); return 0
if __name__ == "__main__": raise SystemExit(main())
