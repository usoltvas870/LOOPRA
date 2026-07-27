from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "trend-radar" / "src"))
from loopra_modality_script_pilot import PILOT_RANKS, run_pilot

def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded LOOPRA 05 modality script pilot")
    parser.add_argument("--batch", required=True); parser.add_argument("--ranks", default="2,6,9,16,17,19")
    parser.add_argument("--runtime-root", type=Path, required=True); parser.add_argument("--run", action="store_true"); parser.add_argument("--reuse-only", action="store_true"); parser.add_argument("--json", action="store_true")
    args = parser.parse_args(); ranks = tuple(int(x) for x in args.ranks.split(","))
    root = args.runtime_root / "loopra-top20-b1-0b0f4d016936" / "v2" / "quality-recovery-v1.2"
    result = run_pilot(evidence_root=root / "evidence-packets", output_root=root, ranks=ranks, run_scripts=args.run, reuse_only=args.reuse_only)
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result["content_hash"]); return 0
if __name__ == "__main__": raise SystemExit(main())
