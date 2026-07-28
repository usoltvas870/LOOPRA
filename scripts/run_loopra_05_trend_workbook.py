"""Build a LOOPRA 0.5 portable trend workbook from bounded local evidence."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(ROOT / "trend-radar" / "src"))
from trend_workbook import TrendWorkbookError, build_package, resume_public_first_workbook, run_public_first_workbook


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="LOOPRA 0.5 Trend Workbook package builder")
    parser.add_argument("--project", default="nura")
    parser.add_argument("--search-run-id")
    parser.add_argument("--candidates-json", type=Path, help="Bounded acquired candidate records; no provider data is accepted.")
    parser.add_argument("--output-root", type=Path, default=ROOT / "output")
    parser.add_argument("--runtime-root", type=Path, default=ROOT / ".runtime" / "loopra-05-trend-workbook")
    parser.add_argument("--fresh", action="store_true", help="Use the existing guest-capable v2 collector and per-item acquisition path.")
    parser.add_argument("--resume", action="store_true", help="Resume an existing collection without a new TikTok search.")
    parser.add_argument("--build-id", help="Stable package build ID required for resume/reuse.")
    parser.add_argument("--maximum-attempts", type=int, default=30)
    parser.add_argument("--maximum-shortlist-size", type=int, default=50)
    parser.add_argument("--maximum-consecutive-failures", type=int, default=5)
    parser.add_argument("--target-count", type=int, default=20, choices=range(20, 31))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.fresh and args.resume:
            raise TrendWorkbookError("--fresh and --resume are mutually exclusive")
        if args.resume:
            if not args.build_id:
                raise TrendWorkbookError("--build-id is required for deterministic resume/reuse")
            result = resume_public_first_workbook(
                project_id=args.project, runtime_root=args.runtime_root, output_root=args.output_root,
                target_count=args.target_count, build_id=args.build_id,
                maximum_attempts=args.maximum_attempts,
                maximum_shortlist_size=args.maximum_shortlist_size,
                maximum_consecutive_failures=args.maximum_consecutive_failures,
            )
            print(json.dumps(result, ensure_ascii=False, sort_keys=True, default=str) if args.json else result["status"])
            return 0 if result["status"] == "READY_FOR_OWNER_WORKBOOK_REVIEW" else 1
        if args.fresh:
            result = run_public_first_workbook(project_id=args.project, runtime_root=args.runtime_root, output_root=args.output_root)
            print(json.dumps(result, ensure_ascii=False, sort_keys=True, default=str) if args.json else result["status"])
            return 0 if result["status"] == "READY_FOR_OWNER_WORKBOOK_REVIEW" else 1
        if not args.search_run_id or not args.candidates_json:
            raise TrendWorkbookError("--search-run-id and --candidates-json are required unless --fresh is used")
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
