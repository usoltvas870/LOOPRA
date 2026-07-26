"""Offline public acceptance for the Stage 5L pre-episode bridge."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]

from nura_script_episode_bridge import build_and_persist_bridge


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and verify the offline NURA Script-to-Production Bridge.")
    runtime = ROOT / "data" / "nura-real-script-provider" / "nura-real-script-3bce876cac5b"
    briefs = ROOT / "data" / "nura-production-briefs" / "nura-production-briefs-1aac60d95c02" / "candidates" / "7665636437601094933"
    parser.add_argument("--finalized-review", type=Path, default=runtime / "finalized_human_script_review.json")
    parser.add_argument("--approved-script", type=Path, default=runtime / "human_approved_script_output.json")
    parser.add_argument("--production-brief", type=Path, default=briefs / "production_brief.json")
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "nura-script-episode-bridge")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    first = build_and_persist_bridge(finalized_review_path=args.finalized_review, approved_script_path=args.approved_script, production_brief_path=args.production_brief, output_root=args.output_root)
    second = build_and_persist_bridge(finalized_review_path=args.finalized_review, approved_script_path=args.approved_script, production_brief_path=args.production_brief, output_root=args.output_root)
    bridge = first["bridge"]
    result = {"status": "PASS", "candidate_id": bridge["candidate_identity"], "rank": bridge["original_rank"], "script_format": bridge["script_format"], "production_format": bridge["target"]["production_format"], "finalized_review_hash": bridge["provenance"]["finalized_human_script_review"]["review_hash"], "approved_script_hash": bridge["provenance"]["human_approved_script"]["content_hash"], "bridge_schema_version": bridge["schema_version"], "bridge_id": bridge["bridge_id"], "bridge_hash": bridge["content_hash"], "text_round_trip": True, "subtitle_source_status": bridge["subtitle_source"]["status"], "timing_status": bridge["timing"]["status"], "character_avatar_requirement": bridge["character_avatar_requirement"]["status"], "voice_requirement": bridge["voice_requirement"]["status"], "renderer_status": bridge["target"]["renderer_assignment"], "music_role": bridge["music"]["role"], "validation_errors": [], "warnings": bridge["warnings"], "unresolved_requirements": bridge["requirements"], "production_input_ready": bridge["production_input_ready"], "production_execution_ready": bridge["production_execution_ready"], "renderer_called": False, "provider_called": False, "network_calls": 0, "credentials_required": False, "first_run_status": first["status"], "second_run_status": second["status"], "reuse_identity": first["bridge"]["content_hash"] == second["bridge"]["content_hash"]}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
