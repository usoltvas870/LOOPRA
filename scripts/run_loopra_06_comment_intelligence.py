"""Public CLI for the bounded LOOPRA 0.6 Comment Intelligence pilot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "trend-radar" / "src"))

from comment_intelligence import CommentIntelligenceError, default_paths, run_comment_intelligence  # noqa: E402


def parser() -> argparse.ArgumentParser:
    input_file, output_root = default_paths(ROOT)
    value = argparse.ArgumentParser(description="LOOPRA 0.6 bounded public TikTok Comment Intelligence")
    value.add_argument("--project", default="nura")
    value.add_argument("--url")
    value.add_argument("--input-file", type=Path, default=input_file)
    value.add_argument("--output-root", type=Path, default=output_root)
    value.add_argument("--max-comments", type=int, default=800)
    value.add_argument("--max-scrolls", type=int, default=24)
    value.add_argument("--timeout", type=int, default=45)
    value.add_argument("--headed", action="store_true")
    value.add_argument("--reuse-only", action="store_true")
    value.add_argument("--dry-run", action="store_true")
    value.add_argument("--refresh", action="store_true", help="Explicitly collect a new immutable snapshot.")
    value.add_argument("--diagnostic", action="store_true", help="Persist privacy-safe browser diagnostics in ignored runtime output.")
    value.add_argument("--json", action="store_true", dest="json_output")
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = run_comment_intelligence(
            project_id=args.project, url=args.url, input_file=args.input_file.resolve(),
            output_root=args.output_root.resolve(), repository_root=ROOT,
            max_comments=args.max_comments, max_scrolls=args.max_scrolls,
            timeout_seconds=args.timeout, headed=args.headed, reuse_only=args.reuse_only,
            dry_run=args.dry_run, refresh=args.refresh, diagnostic=args.diagnostic,
        )
    except (CommentIntelligenceError, OSError, ValueError) as error:
        result = {"status": "BLOCKED", "failure_code": str(error), "browser_calls": 0, "network_calls": 0, "provider_calls": 0}
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"LOOPRA 0.6 Comment Intelligence: {result.get('status')}")
        for label, key in (("Source video", "source_video_id"), ("Clean comments", "cleaned_comment_count"), ("Output", "output_path")):
            if key in result:
                print(f"{label}: {result[key]}")
        if result.get("status") == "READY_FOR_OWNER_COMMENT_PILOT_INPUT":
            print(f"Add one TikTok URL to: {ROOT / 'input' / 'comment_intelligence' / 'selected_video.txt'}")
    return 0 if result.get("status") in {"READY_FOR_OWNER_COMMENT_INSIGHTS_REVIEW", "READY_FOR_OWNER_COMMENT_PILOT_INPUT", "PARTIAL_INSUFFICIENT_COMMENTS", "DRY_RUN", "REUSED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
