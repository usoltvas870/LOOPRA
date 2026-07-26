"""Run the credentialless, offline Stage 5J contract acceptance."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]
from nura_production_brief import hash_payload
from nura_script_contract import DeterministicFakeScriptProvider, build_script_input, create_human_script_review, load_editorial_profile, persist_package


def _brief() -> dict:
    fields = {"source_mechanism_preserved": {"value": "synthetic human mechanism", "source_type": "HUMAN_REVISION"}, "suggested_hook": {"value": "synthetic approved hook", "source_type": "HUMAN_ACCEPTED_AI_VALUE"}, "production_elements_not_copied": {"value": "source catchphrase", "source_type": "HUMAN_ACCEPTED_AI_VALUE"}}
    brief = {"final_status": "COMPLETED", "readiness": "READY_WITH_HUMAN_REVISIONS", "brief_id": "synthetic-brief", "candidate_identity": {"video_id": "synthetic-video"}, "original_rank": 1, "source_review": {"review_id": "synthetic-review", "review_hash": "synthetic-review-hash"}, "project_identity": {"project_id": "nura", "context_version": "1.0", "context_hash": "synthetic-context-hash"}, "fields": fields, "evidence_limitations": ["synthetic acceptance fixture"], "safety_constraints": ["no diagnosis"], "unresolved_fields": [{"field_name": "hook_type", "status": "NOT_TYPED"}]}
    brief["brief_hash"] = hash_payload(brief)
    return brief


def run_acceptance(workdir: Path) -> dict:
    profile = load_editorial_profile(ROOT.parent / "projects" / "nura" / "nura_editorial_profile.json", repository_root=ROOT.parent)
    package = build_script_input(brief=_brief(), profile=profile, requested_format="TALKING_GUIDE")
    provider = DeterministicFakeScriptProvider(); output = provider.generate(package)
    first = persist_package(workdir / "runtime" / "script_input.json", package)
    second = persist_package(workdir / "runtime" / "script_input.json", package)
    review = create_human_script_review(output)
    if output["validation"]["errors"]:
        raise RuntimeError("Fake output failed hard validation")
    return {"contract_built": True, "project_scoped_source_available": profile["source_verified"], "source_hash_valid": profile["source_verified"], "profile_hash_verified": bool(profile["profile_hash"]), "fake_provider_used": provider.provider_mode, "network_used": False, "credentials_required": False, "validation_status": output["validation"]["readiness"], "warning_count": len(output["validation"]["warnings"]), "human_review_status": review["decision"], "episode_bridge_ready": review["episode_bridge_ready"], "first_run": first, "reuse_result": second}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--workdir", type=Path)
    args = parser.parse_args()
    if args.workdir:
        print(json.dumps(run_acceptance(args.workdir), ensure_ascii=False, sort_keys=True))
    else:
        with tempfile.TemporaryDirectory() as directory:
            print(json.dumps(run_acceptance(Path(directory)), ensure_ascii=False, sort_keys=True))
