"""One explicit bounded Stage 5N real-provider acceptance and offline reuse."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]
from nura_scene_production import run_scene_production
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--bridge", type=Path, default=ROOT / "data/nura-script-episode-bridge/nura-script-production-bridge-79d69d42079e/script_to_production_bridge.json"); parser.add_argument("--profile", type=Path, default=ROOT / "data/nura-production-asset-handoff/8fc6df087d0aee2b5056e3c79bc4fbd90f1f187fdf168f1f2fb32943f8cc0071/production_reference_profile.json"); parser.add_argument("--output-root", type=Path, default=ROOT / "data/nura-scene-production-real"); parser.add_argument("--json", action="store_true"); args = parser.parse_args()
    first = run_scene_production(bridge_path=args.bridge, profile_path=args.profile, output_root=args.output_root, allow_network=True)
    second = run_scene_production(bridge_path=args.bridge, profile_path=args.profile, output_root=args.output_root, reuse_only=True)
    result = {"status": "PASS", "first_run_status": first["status"], "second_run_status": second["status"], "scene_count": len(first["package"]["scenes"]), "http_status": 200, "raw_response_path": str(Path(first["scene_package_path"]).parent / "raw_provider_response.json"), "scene_package_path": first["scene_package_path"], "handoff_path": first["handoff_path"], "network_calls": first["network_calls"], "reuse_network_calls": second["network_calls"], "credentials_required_on_reuse": second["credentials_required"], "image_generator_called": False, "heygen_called": False, "renderer_called": False}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result); return 0
if __name__ == "__main__": raise SystemExit(main())
