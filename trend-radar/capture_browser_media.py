"""CLI for one browser-bound capture from a canonical Trend Radar manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from browser_media_acquisition import BrowserMediaAcquisitionRunRequest, run_browser_media_acquisition
from media_acquisition import MediaAcquisitionError


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Sequentially capture up to five manifest-selected TikTok MP4 files inside one authenticated Playwright context.")
    parser.add_argument("--selection-manifest", required=True, type=Path)
    parser.add_argument("--candidate-id", action="append", default=[], help="Explicit candidate ID from the manifest (repeat at most five times).")
    parser.add_argument("--limit", type=int, help="Optional manifest-order limit from 1 to 5; default is 5.")
    parser.add_argument("--cookie-state", type=Path, default=root / "data" / "tiktok_cookies.json")
    parser.add_argument("--output-root", type=Path, default=root / "data" / "acquisitions")
    args = parser.parse_args(argv)
    try:
        record = run_browser_media_acquisition(BrowserMediaAcquisitionRunRequest(
            selection_manifest_path=args.selection_manifest,
            cookie_state_path=args.cookie_state,
            output_root=args.output_root,
            candidate_ids=tuple(args.candidate_id),
            limit=args.limit,
        ))
    except MediaAcquisitionError as error:
        print(json.dumps({"status": "FAILED", "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
    return 0 if record.run_status == "COMPLETED" else 2 if record.run_status == "PARTIAL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
