"""Build a LOOPRA 0.5 portable trend workbook from bounded local evidence."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "trend-radar" / "src"))
from trend_workbook import TrendWorkbookError, build_package


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="LOOPRA 0.5 Trend Workbook package builder")
    parser.add_argument("--project", default="nura")
    parser.add_argument("--search-run-id", required=True)
    parser.add_argument("--candidates-json", type=Path, required=True, help="Bounded acquired candidate records; no provider data is accepted.")
    parser.add_argument("--output-root", type=Path, default=ROOT / "output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        candidates = json.loads(args.candidates_json.read_text(encoding="utf-8-sig"))
        if isinstance(candidates, dict):
            candidates = [candidates]
        if not isinstance(candidates, list): raise TrendWorkbookError("candidates JSON must be a list")
        result = build_package(project_id=args.project, search_run_id=args.search_run_id, candidates=candidates, output_root=args.output_root)
        result["status"] = "READY_FOR_OWNER_WORKBOOK_REVIEW" if result["exported"] >= 20 else "PARTIAL_INSUFFICIENT_VALID_MEDIA"
    except (OSError, json.JSONDecodeError, TrendWorkbookError) as error:
        result = {"status": "BLOCKED", "reason": str(error)}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result["status"])
    return 0 if result["status"] == "READY_FOR_OWNER_WORKBOOK_REVIEW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
