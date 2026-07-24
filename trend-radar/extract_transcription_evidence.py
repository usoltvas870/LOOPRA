from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]

from transcription_evidence import TranscriptionEvidenceError, TranscriptionRunRequest, run_transcription_evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract local, manifest-bound speech transcription evidence.")
    parser.add_argument("--selection-manifest", required=True, type=Path)
    parser.add_argument("--acquisition-root", required=True, type=Path)
    parser.add_argument("--inspection-root", required=True, type=Path)
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "content-intelligence")
    parser.add_argument("--candidate-id", action="append", default=[]); parser.add_argument("--limit", type=int)
    parser.add_argument("--language", choices=("ru", "en")); parser.add_argument("--no-reuse", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_transcription_evidence(TranscriptionRunRequest(args.selection_manifest, args.acquisition_root, args.inspection_root, args.output_root, tuple(args.candidate_id), args.limit, args.language, not args.no_reuse))
    except TranscriptionEvidenceError as error:
        print(json.dumps({"status": "FAILED", "error": str(error)}, ensure_ascii=False)); return 2
    print(json.dumps({"status": result["status"], "candidates": [{"rank": item["rank"], "video_id": item["candidate_video_id"], "status": item["status"], "segments": len(item.get("segments", [])), "reuse_status": item.get("reuse_status")} for item in result["candidates"]]}, ensure_ascii=False, indent=2))
    return 0 if result["status"] != "FAILED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
