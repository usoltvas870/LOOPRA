"""Offline Stage 5G Content Intelligence report CLI."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from content_intelligence_report import ContentIntelligenceReportError, generate_report  # noqa: E402


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Build or reuse an offline five-candidate Content Intelligence report.")
    value.add_argument("--manifest", type=Path, required=True)
    value.add_argument("--project-context", type=Path, default=ROOT.parent / "projects" / "nura" / "content_intelligence_context.json")
    value.add_argument("--card-runtime-root", type=Path, default=ROOT / "data" / "content-intelligence")
    value.add_argument("--output-root", type=Path, default=ROOT / "data" / "content-intelligence-reports")
    value.add_argument("--rank", type=int, action="append", default=[])
    value.add_argument("--json", action="store_true")
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = generate_report(manifest_path=args.manifest, context_path=args.project_context, card_runtime_root=args.card_runtime_root, output_root=args.output_root, ranks=tuple(args.rank) if args.rank else (1, 2, 3, 4, 5))
    except ContentIntelligenceReportError as error:
        print(json.dumps({"status": "FAILED", "error": str(error)}, ensure_ascii=False) if args.json else f"FAILED: {error}")
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else f"CONTENT INTELLIGENCE REPORT: {result['status']} {result['report_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
