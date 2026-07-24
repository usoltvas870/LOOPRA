"""CLI for one browser-bound capture from a canonical Trend Radar manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from browser_media_capture import BrowserMediaCaptureRequest, capture_browser_media
from media_acquisition import MediaAcquisitionError


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Capture one manifest-selected TikTok MP4 inside an authenticated Playwright context.")
    parser.add_argument("--selection-manifest", required=True, type=Path)
    parser.add_argument("--candidate-id", help="Optional explicit candidate ID from the manifest; rank 1 is the default.")
    parser.add_argument("--cookie-state", type=Path, default=root / "data" / "tiktok_cookies.json")
    parser.add_argument("--output-root", type=Path, default=root / "data" / "acquisitions")
    args = parser.parse_args(argv)
    try:
        record = capture_browser_media(BrowserMediaCaptureRequest(
            selection_manifest_path=args.selection_manifest,
            cookie_state_path=args.cookie_state,
            output_root=args.output_root,
            candidate_id=args.candidate_id,
        ))
    except MediaAcquisitionError as error:
        print(json.dumps({"status": "FAILED", "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
    return 0 if record.status in {"COMPLETED", "REUSED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
