"""Run one bounded Rank 1 real NURA script-provider acceptance."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src")]
from nura_real_script_provider import finalize_human_script_review, reprocess_existing_raw, run_real_script_provider

OWNER_APPROVED_TEXT = """Ты продолжаешь поддерживать других, даже когда сама уже выгораешь?

Ты слушаешь, отвечаешь, находишь нужные слова — и снова откладываешь собственную усталость на потом.

Поддерживать близкого не значит каждый раз исчезать из собственной жизни.

Сегодня перед тем, как снова стать для кого-то опорой, спроси себя: «Что сейчас нужно мне?»

Это не отказ от другого. Это возможность остаться рядом, не оставляя себя."""

OWNER_REVISION_REASONS = [
    "Музыка удалена из spoken meaning: она остаётся вторичным эмоциональным каналом.",
    "Категоричная формулировка об отказе от помощи заменена сохранением связи с другим человеком.",
    "Убраны чрезмерно драматичные и шаблонные формулировки provider draft.",
    "Финал заменён на небольшой реалистичный шаг без отказа от человечности.",
    "Exact human-approved hook сохранён без изменений.",
]


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
    parser.add_argument("--finalize-owner-approved", action="store_true")
    parser.add_argument("--pending-review", type=Path)
    parser.add_argument("--runtime-root", type=Path, default=ROOT / "data" / "nura-real-script-provider")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    brief = args.brief or _rank_one_brief(ROOT)
    if args.finalize_owner_approved:
        if not args.pending_review: parser.error("--finalize-owner-approved requires --pending-review")
        result = finalize_human_script_review(pending_path=args.pending_review, approved_text=OWNER_APPROVED_TEXT, revision_reasons=OWNER_REVISION_REASONS, reviewer_id="nura-owner", reviewer_role="OWNER", reviewer_display_name="Василий")
    elif args.reprocess_raw:
        if not args.offline: parser.error("--reprocess-raw requires --offline")
        result = reprocess_existing_raw(raw_path=args.reprocess_raw, brief_path=brief, profile_path=ROOT.parent / "projects" / "nura" / "nura_editorial_profile.json", repository_root=ROOT.parent)
    else:
        result = run_real_script_provider(brief_path=brief, profile_path=ROOT.parent / "projects" / "nura" / "nura_editorial_profile.json", repository_root=ROOT.parent, output_root=args.runtime_root, requested_format=args.format, allow_network=args.provider_mode == "real", reuse_only=args.provider_mode == "reuse")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, default=str))


if __name__ == "__main__": main()
