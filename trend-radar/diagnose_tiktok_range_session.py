"""Run the isolated Stage 3J fresh-response range-session diagnostic for rank 2 only."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from auth import inspect_page_authentication, storage_state_diagnostics
from range_session_diagnostics import run_fresh_range_session
from selection_manifest import read_selection_manifest

CANONICAL_MANIFEST = ROOT / "data" / "runs" / "selection_manifest_20260724_150816.json"


async def run(args) -> dict:
    manifest = read_selection_manifest(CANONICAL_MANIFEST)
    candidate = next(item for item in manifest.candidates if item.rank == 2)
    state, session = storage_state_diagnostics(args.cookie_state)
    if state is None:
        return {"status": "BLOCKED_AUTH", "candidate_rank": 2, "session": session.result}
    from playwright.async_api import async_playwright
    playwright = browser = context = page = None
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=not args.visible)
        context = await browser.new_context(storage_state=state, locale="ru-RU", viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        assembly_target = ROOT / "media-inbox" / f"rank2_{candidate.video_id}.mp4" if args.assemble_rank2 else None
        result = await run_fresh_range_session(page, candidate.canonical_url, probe_bytes=args.probe_bytes,
                                               python_timeout_seconds=args.python_timeout_seconds,
                                               assembly_target=assembly_target)
        auth = await inspect_page_authentication(page)
        return {"schema_version": "1.0", "candidate_rank": 2, "manifest_hash_prefix": manifest.manifest_hash[:12],
                "auth": auth.result, **result}
    finally:
        if page is not None:
            await page.close()
        if context is not None:
            await context.close()
        if browser is not None:
            await browser.close()
        if playwright is not None:
            await playwright.stop()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diagnose one fresh TikTok media range session without writing URLs, headers, bodies, or runtime evidence.")
    parser.add_argument("--cookie-state", type=Path, default=ROOT / "data" / "tiktok_cookies.json")
    parser.add_argument("--probe-bytes", type=int, default=16 * 1024)
    parser.add_argument("--python-timeout-seconds", type=int, default=12)
    parser.add_argument("--visible", action="store_true")
    parser.add_argument("--assemble-rank2", action="store_true", help="After all gates pass, write the rank-2 MP4 under ignored media-inbox.")
    args = parser.parse_args(argv)
    if args.probe_bytes < 1024 or args.probe_bytes > 2 * 1024 * 1024:
        parser.error("--probe-bytes must be between 1024 and 2097152")
    print(json.dumps(asyncio.run(run(args)), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
