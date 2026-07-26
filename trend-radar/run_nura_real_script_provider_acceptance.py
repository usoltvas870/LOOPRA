"""Run one bounded Rank 1 real NURA script-provider acceptance."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]
from nura_real_script_provider import reprocess_existing_raw, run_real_script_provider


def _rank_one_brief(root: Path) -> Path:
    candidates = sorted((root / "data" / "nura-production-briefs").glob("nura-production-briefs-*/candidates/*/production_brief.json"))
    matches = [path for path in candidates if json.loads(path.read_text(encoding="utf-8")).get("original_rank") == 1]
    if not matches: raise RuntimeError("CANONICAL_RANK_1_PRODUCTION_BRIEF_NOT_FOUND")
    return matches[-1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", type=Path)
    parser.add_argument("--format", default="TALKING_GUIDE")
    parser.add_argument("--provider-mode", choices=("real", "reuse"), default="real")
    parser.add_argument("--reprocess-raw", type=Path)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--runtime-root", type=Path, default=ROOT / "data" / "nura-real-script-provider")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    brief = args.brief or _rank_one_brief(ROOT)
    if args.reprocess_raw:
        if not args.offline: parser.error("--reprocess-raw requires --offline")
        result = reprocess_existing_raw(raw_path=args.reprocess_raw, brief_path=brief, profile_path=ROOT.parent / "projects" / "nura" / "nura_editorial_profile.json", repository_root=ROOT.parent)
    else:
        result = run_real_script_provider(brief_path=brief, profile_path=ROOT.parent / "projects" / "nura" / "nura_editorial_profile.json", repository_root=ROOT.parent, output_root=args.runtime_root, requested_format=args.format, allow_network=args.provider_mode == "real", reuse_only=args.provider_mode == "reuse")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, default=str))


if __name__ == "__main__": main()
