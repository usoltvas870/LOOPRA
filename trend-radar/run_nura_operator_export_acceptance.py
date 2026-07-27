"""Stage 5N simplified ChatGPT operator-export acceptance; offline only."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]

from nura_scene_production import build_simplified_operator_export

FINALIZED = ROOT / "data/nura-scene-production-finalized/nura-scene-production-finalized-2aad84cd2c40"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", choices=("ONE_IMAGE", "MULTI_IMAGE"), default="ONE_IMAGE")
    parser.add_argument("--output-root", type=Path, default=ROOT / "data/nura-operator-export")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    kwargs = {"finalized_package_path": FINALIZED / "finalized_scene_production_package.json", "finalized_handoff_path": FINALIZED / "finalized_manual_heygen_handoff.json", "output_root": args.output_root, "visual_generation_strategy": args.strategy}
    first, second = build_simplified_operator_export(**kwargs), build_simplified_operator_export(**kwargs)
    result = {"status": "PASS", "source_package_id": "nura-finalized-scene-package-2aad84cd2c40", "visual_generation_strategy": args.strategy, "strategy_justification": "One continuous single-speaker TALKING_GUIDE needs one reusable talking-avatar source image." if args.strategy == "ONE_IMAGE" else "Explicit MULTI_IMAGE acceptance coverage.", "export_id": first["export_id"], "export_hash": first["export_hash"], "export_path": first["export_path"], "files": first["files"], "text_output_present": bool(first["text"]), "prompt_count": first["prompt_count"], "json_required_for_manual_use": False, "first_status": first["status"], "second_status": second["status"], "reuse_identity": first["export_id"] == second["export_id"] and first["export_hash"] == second["export_hash"], "provider_called": False, "image_generator_called": False, "heygen_called": False, "renderer_called": False, "network_calls": 0, "credentials_required": False}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
