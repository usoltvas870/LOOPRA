"""Run the isolated Stage 3I range consistency diagnostic for one candidate."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from auth import inspect_page_authentication, storage_state_diagnostics
from range_diagnostics import DEFAULT_BROWSER_TIMEOUT_MS, consistency_verdict, fetch_page_range
from selection_manifest import read_selection_manifest


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


async def run(args) -> dict:
    manifest = read_selection_manifest(args.selection_manifest)
    candidate = next((item for item in manifest.candidates if item.rank == args.rank), None)
    if candidate is None:
        raise ValueError(f"rank {args.rank} is absent from the manifest")
    state, session = storage_state_diagnostics(args.cookie_state)
    if state is None:
        return {"schema_version": "1.0", "status": "BLOCKED_AUTH", "candidate_rank": args.rank, "session": session.result}

    from playwright.async_api import async_playwright
    playwright = browser = context = page = None
    media_url: str | None = None
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=not args.visible)
        context = await browser.new_context(storage_state=state, locale="ru-RU", viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        def observe(response) -> None:
            nonlocal media_url
            parsed = urlsplit(response.url)
            if media_url is None and response.status == 200 and response.headers.get("content-type", "").split(";", 1)[0] == "video/mp4" and parsed.hostname and parsed.hostname.endswith("tiktok.com") and "/video/" in parsed.path:
                media_url = response.url

        page.on("response", observe)
        await page.goto(candidate.canonical_url, wait_until="domcontentloaded", timeout=45_000)
        await page.wait_for_timeout(5_000)
        auth = await inspect_page_authentication(page)
        if auth.result != "session_valid":
            return {"schema_version": "1.0", "status": "BLOCKED_AUTH", "candidate_rank": args.rank, "session": auth.result}
        await page.evaluate("""async () => { const v = document.querySelector('video'); if (v) { v.muted = true; try { await v.play(); } catch (_) {} } }""")
        await page.wait_for_timeout(5_000)
        if media_url is None:
            return {"schema_version": "1.0", "status": "NO_MEDIA_RESPONSE", "candidate_rank": args.rank}

        first = await fetch_page_range(page, media_url, label="start", start=0, end=args.probe_bytes - 1)
        probes = [first]
        if first.status == "PASS" and first.total_bytes:
            size = args.probe_bytes
            middle = max(size, (first.total_bytes // 2 // size) * size)
            middle = min(middle, first.total_bytes - size)
            probes.extend([
                await fetch_page_range(page, media_url, label="middle", start=middle, end=middle + size - 1),
                await fetch_page_range(page, media_url, label="end", start=first.total_bytes - size, end=first.total_bytes - 1),
                await fetch_page_range(page, media_url, label="repeat_start", start=0, end=size - 1),
            ])
        cancellation = await fetch_page_range(page, media_url, label="cancellation", start=0, end=args.probe_bytes - 1, browser_timeout_ms=1, python_timeout_seconds=args.python_timeout_seconds)
        page_usable = await page.evaluate("() => document.readyState") == "complete"
        return {
            "schema_version": "1.0", "status": "COMPLETED", "candidate_rank": args.rank,
            "manifest_hash": manifest.manifest_hash, "probes": [item.to_dict() for item in probes],
            "consistency": consistency_verdict(probes), "cancellation": cancellation.to_dict(),
            "page_remained_usable": page_usable, "browser_timeout_ms": DEFAULT_BROWSER_TIMEOUT_MS,
            "python_timeout_seconds": args.python_timeout_seconds, "completed_at": _utc_iso(),
        }
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
    parser = argparse.ArgumentParser(description="Run bounded, page-context TikTok range diagnostics without persisting signed URLs or bodies.")
    parser.add_argument("--selection-manifest", required=True, type=Path)
    parser.add_argument("--rank", required=True, type=int)
    parser.add_argument("--cookie-state", type=Path, default=ROOT / "data" / "tiktok_cookies.json")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--probe-bytes", type=int, default=16 * 1024)
    parser.add_argument("--python-timeout-seconds", type=int, default=12)
    parser.add_argument("--visible", action="store_true")
    args = parser.parse_args(argv)
    if args.probe_bytes < 1024 or args.probe_bytes > 2 * 1024 * 1024:
        parser.error("--probe-bytes must be between 1024 and 2097152")
    result = asyncio.run(run(args))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": result["status"], "candidate_rank": args.rank, "output": str(args.output)}, ensure_ascii=False))
    return 0 if result["status"] == "COMPLETED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
