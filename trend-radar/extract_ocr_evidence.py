"""CLI for manifest-bound, offline Windows OCR evidence extraction."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from media_acquisition import MediaAcquisitionError
from ocr_evidence import OcrEvidenceError, OcrRunRequest, run_ocr_evidence


def _summary(result: dict) -> dict:
    return {
        "schema_version": result["schema_version"],
        "status": result["status"],
        "radar_run_id": result["radar_run_id"],
        "engine": result["engine"],
        "candidates": [
            {key: candidate.get(key) for key in ("candidate_video_id", "rank", "status", "reuse_status", "requested_frame_count", "processed_frame_count", "completed_frame_count", "empty_frame_count", "failed_frame_count")}
            | {"unique_text_event_count": len(candidate.get("text_events", [])), "first_text_hook_available": candidate.get("first_text_hook") is not None}
            for candidate in result["candidates"]
        ],
    }


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Extract local Windows OCR evidence from existing format-inspection frames.")
    parser.add_argument("--selection-manifest", required=True, type=Path)
    parser.add_argument("--inspection-root", required=True, type=Path)
    parser.add_argument("--candidate-id", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--language", default="en-US", choices=("en-US", "ru"))
    parser.add_argument("--output-root", type=Path, default=root / "data" / "content-intelligence")
    args = parser.parse_args(argv)
    try:
        result = run_ocr_evidence(OcrRunRequest(args.selection_manifest, args.inspection_root, args.output_root, tuple(args.candidate_id), args.limit, args.language))
    except (OcrEvidenceError, MediaAcquisitionError) as error:
        print(json.dumps({"status": "FAILED", "error": str(error)}, ensure_ascii=False)); return 2
    print(json.dumps(_summary(result), ensure_ascii=False, indent=2)); return 0 if result["status"] != "FAILED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
