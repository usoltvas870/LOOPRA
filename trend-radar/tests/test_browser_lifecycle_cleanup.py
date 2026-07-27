import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "trend-radar/src"))
from collector import TikTokCollector


class _Context:
    def __init__(self): self.closed = 0
    async def close(self): self.closed += 1


class _Browser:
    def __init__(self): self.closed = 0
    async def close(self): self.closed += 1


class _Playwright:
    def __init__(self): self.stopped = 0
    async def stop(self): self.stopped += 1


def test_owned_browser_context_and_playwright_close_on_success() -> None:
    collector = TikTokCollector()
    collector.owns_browser = True
    collector.context, collector.browser, collector.playwright = _Context(), _Browser(), _Playwright()
    context, browser, playwright = collector.context, collector.browser, collector.playwright
    asyncio.run(collector.close())
    assert (context.closed, browser.closed, playwright.stopped) == (1, 1, 1)


def test_cdp_connection_detaches_without_closing_user_browser() -> None:
    collector = TikTokCollector()
    collector.connected_over_cdp = True
    collector.context, collector.browser, collector.playwright = _Context(), _Browser(), _Playwright()
    context, browser, playwright = collector.context, collector.browser, collector.playwright
    asyncio.run(collector.close())
    assert (context.closed, browser.closed, playwright.stopped) == (0, 0, 1)
