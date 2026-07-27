"""Offline forensic audit for an existing rejected LOOPRA 5O-B1 batch."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "trend-radar" / "src")]
from loopra_quality_recovery import QualityRecoveryError, run_quality_recovery

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run offline LOOPRA B1E quality recovery.")
    parser.add_argument("--batch", required=True)
    parser.add_argument("--runtime-root", type=Path, default=ROOT / "trend-radar" / "data" / "loopra-05-b1c-real-20260727-authenticated" / "loopra-top20-b1-0b0f4d016936" / "v2")
    parser.add_argument("--audit", action="store_true", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_quality_recovery(root=args.runtime_root)
        if result["rejection"]["batch_id"] != args.batch: raise QualityRecoveryError("BATCH_ID_MISMATCH")
    except QualityRecoveryError as error:
        result = {"status": "BLOCKED", "reason": str(error)}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result["status"])
    return 0 if result["status"] == "READY_FOR_OWNER_QUALITY_LABELING" else 1

if __name__ == "__main__": raise SystemExit(main())
