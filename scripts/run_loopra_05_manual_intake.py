"""Public CLI for LOOPRA 0.5 manual source intake."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "trend-radar" / "src"))

from manual_source_intake import ManualIntakeError, default_paths, run_manual_intake  # noqa: E402


def parser() -> argparse.ArgumentParser:
    links, media, output = default_paths(ROOT)
    value = argparse.ArgumentParser(description="LOOPRA 0.5 manual-first source intake")
    value.add_argument("--project", default="nura")
    value.add_argument("--links-file", type=Path, default=links)
    value.add_argument("--media-dir", type=Path, default=media)
    value.add_argument("--output-root", type=Path, default=output)
    value.add_argument("--reuse-only", action="store_true")
    value.add_argument("--dry-run", action="store_true")
    value.add_argument("--json", action="store_true", dest="json_output")
    value.add_argument("--limit", type=int)
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = run_manual_intake(
            project_id=args.project, links_file=args.links_file.resolve(),
            media_dir=args.media_dir.resolve(), output_root=args.output_root.resolve(),
            repository_root=ROOT, reuse_only=args.reuse_only, dry_run=args.dry_run,
            limit=args.limit,
        )
    except (ManualIntakeError, OSError, ValueError) as error:
        result = {"status": "BLOCKED", "failure_code": type(error).__name__, "error": str(error)}
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"LOOPRA 0.5 manual intake: {result.get('status')}")
        for label, key in (
            ("Intake ID", "intake_id"), ("Parsed links", "parsed_link_count"),
            ("Local media files", "local_media_count"), ("Duplicates", "duplicate_input_count"),
            ("Accepted", "accepted_source_count"), ("Failed", "failed_source_count"),
            ("Output", "output_path"),
        ):
            if key in result:
                print(f"{label}: {result[key]}")
        if result.get("error"):
            print(f"Error: {result['error']}")
        if result.get("status") not in {"BLOCKED", "NO_VALID_INPUTS", "DRY_RUN"}:
            print("Next: open an item folder and upload source.mp4 with GPT_HANDOFF_RU.md to ChatGPT.")
    return 2 if result.get("status") in {"BLOCKED", "NO_VALID_INPUTS"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
