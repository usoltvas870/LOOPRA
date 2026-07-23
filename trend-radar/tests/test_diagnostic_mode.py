import asyncio
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch


RADAR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADAR_ROOT / 'src'))
sys.path.insert(0, str(RADAR_ROOT))

import collector
import run_radar


class CollectorDiagnosticModeTests(unittest.IsolatedAsyncioTestCase):
    def _playwright(self, browser, cdp_error=None):
        chromium = SimpleNamespace(
            launch=AsyncMock(return_value=browser),
            connect_over_cdp=AsyncMock(side_effect=cdp_error),
        )
        return SimpleNamespace(chromium=chromium, stop=AsyncMock())

    async def test_diagnostic_close_does_not_save_cookies(self):
        instance = collector.TikTokCollector()
        instance.diagnostic_mode = True
        instance.owns_browser = True
        instance.browser = SimpleNamespace(close=AsyncMock())
        instance.context = SimpleNamespace(cookies=AsyncMock(return_value=[]))
        instance.playwright = SimpleNamespace(stop=AsyncMock())

        with patch('builtins.open', Mock(side_effect=AssertionError('must not write cookies'))):
            await instance.close()

        instance.browser.close.assert_awaited_once()
        instance.playwright = None

    async def test_invalid_cookie_json_is_not_deleted(self):
        with tempfile.TemporaryDirectory() as directory:
            cookie_path = Path(directory) / 'cookies.json'
            cookie_path.write_text('{not json', encoding='utf-8')
            browser = SimpleNamespace(close=AsyncMock(), new_context=AsyncMock())
            playwright = self._playwright(browser)
            with patch('collector.get_cookie_path', return_value=cookie_path), \
                 patch('collector.async_playwright') as async_playwright:
                async_playwright.return_value.start = AsyncMock(return_value=playwright)
                instance = collector.TikTokCollector()
                with self.assertRaisesRegex(collector.RadarOperationalError, 'Cannot read cookie file') as error:
                    await instance.start()
                self.assertEqual(error.exception.reason, 'cookies_invalid')
                self.assertTrue(cookie_path.exists())
                await instance.close()

    async def test_diagnostic_and_headless_modes_do_not_wait_for_login(self):
        for diagnostic_mode, headless in ((True, False), (False, True)):
            with self.subTest(diagnostic_mode=diagnostic_mode, headless=headless), tempfile.TemporaryDirectory() as directory:
                cookie_path = Path(directory) / 'cookies.json'
                cookie_path.write_text(json.dumps({'cookies': [], 'origins': []}), encoding='utf-8')
                context = SimpleNamespace(new_page=AsyncMock(), cookies=AsyncMock(return_value=[]))
                browser = SimpleNamespace(close=AsyncMock(), new_context=AsyncMock(return_value=context))
                playwright = self._playwright(browser)
                with patch('collector.get_cookie_path', return_value=cookie_path), \
                     patch('collector.async_playwright') as async_playwright:
                    async_playwright.return_value.start = AsyncMock(return_value=playwright)
                    instance = collector.TikTokCollector(headless=headless)
                    instance.diagnostic_mode = diagnostic_mode
                    instance._validate_cookies = AsyncMock(return_value=(False, 'login wall'))
                    with self.assertRaises(collector.RadarOperationalError) as error:
                        await instance.start()
                    self.assertEqual(error.exception.reason, 'authentication_required')
                    context.new_page.assert_not_awaited()
                    await instance.close()

    async def test_cdp_fallback_is_owned_and_successful_cdp_is_not_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            cookie_path = Path(directory) / 'missing.json'
            fallback_context = SimpleNamespace(cookies=AsyncMock(return_value=[]))
            fallback = SimpleNamespace(close=AsyncMock(), new_context=AsyncMock(return_value=fallback_context))
            fallback_playwright = self._playwright(fallback, cdp_error=RuntimeError('not running'))
            with patch('collector.get_cookie_path', return_value=cookie_path), \
                 patch('collector.get_config', side_effect=lambda key, default=None: '9222' if key == 'CHROME_DEBUG_PORT' else default), \
                 patch('collector.async_playwright') as async_playwright:
                async_playwright.return_value.start = AsyncMock(return_value=fallback_playwright)
                instance = collector.TikTokCollector()
                await instance.start()
                self.assertTrue(instance.owns_browser)
                await instance.close()
                fallback.close.assert_awaited_once()

            context = SimpleNamespace()
            attached = SimpleNamespace(contexts=[context], close=AsyncMock())
            attached_playwright = self._playwright(attached)
            attached_playwright.chromium.connect_over_cdp = AsyncMock(return_value=attached)
            with patch('collector.get_cookie_path', return_value=cookie_path), \
                 patch('collector.get_config', side_effect=lambda key, default=None: '9222' if key == 'CHROME_DEBUG_PORT' else default), \
                 patch('collector.async_playwright') as async_playwright:
                async_playwright.return_value.start = AsyncMock(return_value=attached_playwright)
                instance = collector.TikTokCollector()
                await instance.start()
                self.assertTrue(instance.connected_over_cdp)
                await instance.close()
                attached.close.assert_not_awaited()

    async def test_login_wall_is_classified_from_visible_login_text(self):
        instance = collector.TikTokCollector()
        page = SimpleNamespace(
            url='https://www.tiktok.com/tag/example',
            evaluate=AsyncMock(side_effect=[0, 0, True]),
        )

        blocked, reason = await instance._is_blocked(page, 'example')

        self.assertTrue(blocked)
        self.assertEqual(reason, 'login overlay detected, no video content')


class RunRadarResultTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_and_successful_collection_return_observable_codes(self):
        connection = SimpleNamespace(commit=Mock(), close=Mock())

        class EmptyCollector:
            last_collection_reason = 'tiktok_blocked'
            async def start(self): pass
            async def collect_all(self, sources): return []
            async def enrich_missing_stats(self, videos): return videos
            async def close(self): pass

        with patch.multiple(run_radar, setup_logging=Mock(), load_env=Mock(),
                            read_source_file=Mock(side_effect=lambda name: ['source'] if name == 'hashtags.txt' else []),
                            init_db=Mock(), get_connection=Mock(return_value=connection),
                            TikTokCollector=Mock(return_value=EmptyCollector())):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(await run_radar.main(), 3)
            self.assertIn('RADAR_RESULT=tiktok_blocked', output.getvalue())

        video = {'url': 'https://example.invalid/video/1', 'caption': 'test', 'views': 10000}

        class SuccessCollector(EmptyCollector):
            collected_at = 'now'
            run_id = 'run'
            last_collection_reason = None
            async def collect_all(self, sources): return [video]
            async def validate_candidate_links(self, videos):
                for item in videos:
                    item.update(link_status='AVAILABLE', identity_confidence='HIGH')
                return videos

        with patch.multiple(run_radar, setup_logging=Mock(), load_env=Mock(),
                            read_source_file=Mock(side_effect=lambda name: ['source'] if name == 'hashtags.txt' else []),
                            init_db=Mock(), get_connection=Mock(return_value=connection),
                            TikTokCollector=Mock(return_value=SuccessCollector()), save_video=Mock(return_value=True),
                            compute_scores=Mock(return_value=[video]), generate_report=Mock(return_value='report'),
                            save_report=Mock(return_value='report.md'), save_xlsx=Mock(return_value='report.xlsx'),
                            save_scenarios_xlsx=Mock(return_value=None), save_carousel_texts=Mock(return_value=None),
                            get_config_bool=Mock(side_effect=lambda key, default: False if key in ('ENABLE_AI_ANALYSIS', 'ENABLE_TELEGRAM') else default)):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(await run_radar.main(), 0)
            self.assertIn('RADAR_RESULT=success', output.getvalue())
