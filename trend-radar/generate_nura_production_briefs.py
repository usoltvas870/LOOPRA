"""CLI for the offline Stage 5I NURA Production Brief contract."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.nura_production_brief import NuraProductionBriefError, build_production_briefs


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic NURA Production Briefs from finalized human review only.")
    parser.add_argument("--finalized-review-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-cards-root", type=Path, required=True)
    parser.add_argument("--project-context", type=Path, default=Path("projects/nura/content_intelligence_context.json"))
    parser.add_argument("--output-root", type=Path, default=Path("trend-radar/data/nura-production-briefs"))
    parser.add_argument("--ranks", default="1,2,3,4,5", help="Comma-separated original ranks; only 1 through 5 are allowed.")
    parser.add_argument("--no-reuse", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit the machine-readable run summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        ranks = tuple(int(value) for value in args.ranks.split(",") if value)
        result = build_production_briefs(finalized_review_root=args.finalized_review_dir, manifest_path=args.manifest,
            source_cards_root=args.source_cards_root, project_context_path=args.project_context, output_root=args.output_root,
            ranks=ranks, reuse=not args.no_reuse)
    except (ValueError, NuraProductionBriefError) as error:
        print(json.dumps({"status": "FAILED", "error": str(error)}, ensure_ascii=False) if args.json else f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else f"{result['status']}: {result['run_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
