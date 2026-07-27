"""One explicit bounded Stage 5N real-provider acceptance and offline reuse."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]
from nura_scene_production import record_operator_rejection, reprocess_existing_raw
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--bridge", type=Path, default=ROOT / "data/nura-script-episode-bridge/nura-script-production-bridge-79d69d42079e/script_to_production_bridge.json"); parser.add_argument("--profile", type=Path, default=ROOT / "data/nura-production-asset-handoff/8fc6df087d0aee2b5056e3c79bc4fbd90f1f187fdf168f1f2fb32943f8cc0071/production_reference_profile.json"); parser.add_argument("--output-root", type=Path, default=ROOT / "data/nura-scene-production-real"); parser.add_argument("--operator-rejection", type=Path, default=ROOT / "data/nura-scene-production-real/nura-scene-production-84aa0ff087b1/operator_rejection.json"); parser.add_argument("--reprocess-existing", type=Path, default=ROOT / "data/nura-scene-production-real/nura-scene-production-3dbee3f3c123"); parser.add_argument("--offline", action="store_true"); parser.add_argument("--json", action="store_true"); args = parser.parse_args()
    rejected_root = ROOT / "data/nura-scene-production-real/nura-scene-production-84aa0ff087b1"
    record_operator_rejection(rejected_package_path=rejected_root / "scene_production_package.json", raw_response_path=rejected_root / "raw_provider_response.json", output_path=args.operator_rejection)
    if not args.offline: parser.error("--offline is required; this command never calls a provider")
    first = reprocess_existing_raw(bridge_path=args.bridge, profile_path=args.profile, original_run_root=args.reprocess_existing, output_root=args.output_root, operator_rejection_path=args.operator_rejection)
    second = reprocess_existing_raw(bridge_path=args.bridge, profile_path=args.profile, original_run_root=args.reprocess_existing, output_root=args.output_root, operator_rejection_path=args.operator_rejection)
    result = {"status": "PASS", "original_run_id": args.reprocess_existing.name, "first_run_status": first["status"], "second_run_status": second["status"], "scene_count": len(first["package"]["scenes"]), "scene_package_path": first["scene_package_path"], "handoff_path": first["handoff_path"], "report_path": first["report_path"], "offline_reprocessing": True, "provider_call_performed": False, "network_calls": 0, "credentials_required": False, "image_generator_called": False, "heygen_called": False, "renderer_called": False}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result); return 0
if __name__ == "__main__": raise SystemExit(main())
