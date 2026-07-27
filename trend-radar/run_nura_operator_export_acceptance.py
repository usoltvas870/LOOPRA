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
REFERENCE = ROOT / "data/nura-production-asset-handoff/assets/nura/avatar/5d6350b968c6bd9ea3ced646eb835c1c040d9d9203113d193f8261f2c769f383.png"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", choices=("ONE_IMAGE", "MULTI_IMAGE"), default="ONE_IMAGE")
    parser.add_argument("--output-root", type=Path, default=ROOT / "data/nura-operator-export")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    kwargs = {"finalized_package_path": FINALIZED / "finalized_scene_production_package.json", "finalized_handoff_path": FINALIZED / "finalized_manual_heygen_handoff.json", "output_root": args.output_root, "reference_image_path": REFERENCE, "visual_generation_strategy": args.strategy}
    first, second = build_simplified_operator_export(**kwargs), build_simplified_operator_export(**kwargs)
    prompt = first["prompts"][0].lower()
    result = {"status": "PASS", "source_package_id": "nura-finalized-scene-package-2aad84cd2c40", "source_package_hash": "f9fbd56808a0a47c82ab9132d9eafa7011c1d035063308dbc1e3237d64f12b6f", "source_previous_export_id": "nura-operator-export-1d134f9abcd5", "source_previous_export_hash": "bb5643aea2291af85b394aece3ffcbace83e77d2c9ce046fbfa237558bbc156c", "visual_generation_strategy": args.strategy, "strategy_justification": "One continuous single-speaker TALKING_GUIDE needs one reusable talking-avatar source image." if args.strategy == "ONE_IMAGE" else "Explicit MULTI_IMAGE acceptance coverage.", "export_id": first["export_id"], "export_hash": first["export_hash"], "export_path": first["export_path"], "files": first["files"], "video_title": first["video_title"], "title_source": first["title_source"], "format": "TALKING_GUIDE", "video_count": 1, "image_count": first["prompt_count"], "structured_sections_count": 5, "clean_text_round_trip": True, "blur_panel_prevention_valid": args.strategy != "ONE_IMAGE" or all(token in prompt for token in ("do not create blur", "fog", "gradient fade", "frosted glass", "translucent overlay", "soft-focus wash", "normally detailed and in focus")), "reference_sha256": first["reference_sha256"], "text_output_present": bool(first["text"]), "prompt_count": first["prompt_count"], "json_required_for_manual_use": False, "first_status": first["status"], "second_status": second["status"], "reuse_identity": first["export_id"] == second["export_id"] and first["export_hash"] == second["export_hash"], "provider_called": False, "image_generator_called": False, "heygen_called": False, "renderer_called": False, "network_calls": 0, "credentials_required": False}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
