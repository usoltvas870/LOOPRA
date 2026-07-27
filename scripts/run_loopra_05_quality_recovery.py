"""Offline forensic audit for an existing rejected LOOPRA 5O-B1 batch."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "trend-radar" / "src")]
from loopra_quality_recovery import QualityRecoveryError, build_grounded_evidence_packets, run_quality_recovery
from grounded_triage import GroundedTriageError, run_grounded_reprocess, write_actionable_owner_package

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run offline LOOPRA B1E quality recovery.")
    parser.add_argument("--batch", required=True)
    parser.add_argument("--runtime-root", type=Path, default=ROOT / "trend-radar" / "data" / "loopra-05-b1c-real-20260727-authenticated" / "loopra-top20-b1-0b0f4d016936" / "v2")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--grounded-preflight", action="store_true")
    parser.add_argument("--grounded-reprocess", action="store_true")
    parser.add_argument("--build-actionable-package", action="store_true")
    parser.add_argument("--reuse-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if sum((args.audit, args.grounded_preflight, args.grounded_reprocess)) != 1:
            raise QualityRecoveryError("SELECT_EXACTLY_ONE_OFFLINE_MODE")
        if args.grounded_reprocess:
            recovery = args.runtime_root / "quality-recovery-v1.2"
            result = run_grounded_reprocess(packets_root=recovery / "evidence-packets", output_root=recovery / "grounded-results", reuse_only=args.reuse_only)
            if args.build_actionable_package:
                write_actionable_owner_package(packets=[json.loads(path.read_text(encoding="utf-8")) for path in sorted((recovery / "evidence-packets").glob("*.json"))], results=result["results"], output=recovery / "actionable-owner-triage")
                result["owner_package"] = "quality-recovery-v1.2/actionable-owner-triage"
        else: result = build_grounded_evidence_packets(root=args.runtime_root) if args.grounded_preflight else run_quality_recovery(root=args.runtime_root)
        result_batch = result.get("batch_id") or result.get("rejection", {}).get("batch_id")
        if result_batch != args.batch: raise QualityRecoveryError("BATCH_ID_MISMATCH")
    except (QualityRecoveryError, GroundedTriageError) as error:
        result = {"status": "BLOCKED", "reason": str(error)}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result["status"])
    return 0 if result["status"] in {"READY_FOR_OWNER_QUALITY_LABELING", "OFFLINE_EVIDENCE_PACKETS_READY", "READY_FOR_OWNER_ACTIONABLE_TRIAGE"} else 1

if __name__ == "__main__": raise SystemExit(main())
