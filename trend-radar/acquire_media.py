"""CLI boundary for bounded, operator-provided Trend Radar media acquisition."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from media_acquisition import MediaAcquisitionError, MediaAcquisitionRequest, acquire_local_media


def _mapping(value: str) -> tuple[str, Path]:
    video_id, separator, path = value.partition("=")
    if not separator or not video_id or not path:
        raise argparse.ArgumentTypeError("--local-file must use VIDEO_ID=PATH")
    return video_id, Path(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Register selected local media from a canonical Trend Radar manifest.")
    parser.add_argument("--selection-manifest", required=True, type=Path)
    parser.add_argument("--local-file", required=True, action="append", type=_mapping, metavar="VIDEO_ID=PATH")
    parser.add_argument("--candidate-id", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parent / "data" / "acquisitions")
    args = parser.parse_args(argv)
    mappings = dict(args.local_file)
    try:
        records = acquire_local_media(MediaAcquisitionRequest(
            selection_manifest_path=args.selection_manifest,
            output_root=args.output_root,
            local_file_mapping=mappings,
            candidate_ids=tuple(args.candidate_id),
            limit=args.limit,
        ))
    except MediaAcquisitionError as error:
        print(json.dumps({"status": "FAILED", "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"records": [record.to_dict() for record in records]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
