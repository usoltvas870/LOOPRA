import asyncio
import logging
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from playwright.async_api import async_playwright, Browser

from parser import extract_video_data, extract_from_api_responses, parse_detail_page_stats
from utils import get_config_int, get_config, async_random_sleep, extract_video_id, get_cookie_path
from run_data import apply_freshness, utc_iso
from auth import AUTH_CHALLENGE, AUTH_REFRESH_REQUIRED, AUTH_SESSION_VALID, inspect_page_authentication, write_state_atomic

logger = logging.getLogger(__name__)


class RadarOperationalError(RuntimeError):
    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


class TikTokCollector:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.diagnostic_mode = get_config('DIAGNOSTIC_MODE', '').lower() in ('true', '1', 'yes')
        self.browser: Optional[Browser] = None
        self.context = None
        self.playwright = None
        self.connected_over_cdp = False
        self.owns_browser = False
        self.last_collection_reason: Optional[str] = None
        self.last_collection_method = 'none'
        self.last_raw_items_received = 0
        self.last_final_page_url = None
        self.last_authentication_state = 'unknown'
        self.last_unsupported_schema_count = 0
        self.authentication_state = 'unknown'
        self.source_attempts: list[dict] = []
        self.provenance: list[dict] = []
        self.max_results = get_config_int('MAX_RESULTS_PER_SOURCE', 20)
        self.collected_at = utc_iso()
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.cookie_path = get_cookie_path()
        self.screenshots_dir = Path(__file__).resolve().parent.parent / 'data' / 'debug'
        self._hashtag_blocked = False
        self._debug_mode = os.getenv('LOG_LEVEL', '').upper() == 'DEBUG'

    async def start(self):
        self.playwright = await async_playwright().start()
        debug_port = get_config('CHROME_DEBUG_PORT')
        if debug_port:
            try:
                self.browser = await self.playwright.chromium.connect_over_cdp(
                    f'http://127.0.0.1:{debug_port}'
                )
                self.context = self.browser.contexts[0]
                self.connected_over_cdp = True
                logger.info(f'Connected to existing Chrome on port {debug_port}')
                return
            except Exception as e:
                logger.error(
                    f'Failed to connect to Chrome on port {debug_port}: {e}'
                )
                logger.warning(
                    '  ┌────────────────────────────────────────────────────┐\n'
                    '  │ CHROME_DEBUG_PORT указан, но Chrome не запущен     │\n'
                    '  │                                                  │\n'
                    '  │ 1. Закрой все окна Chrome                        │\n'
                    '  │ 2. Win+R → chrome.exe --remote-debugging-port=9222│\n'
                    '  │ 3. Войди в TikTok (tiktok.com)                   │\n'
                    '  │ 4. Запусти скрипт снова                         │\n'
                    '  │                                                  │\n'
                    '  │ Сейчас скрипт запустит свой браузер (headless)    │\n'
                    '  └────────────────────────────────────────────────────┘'
                )
        try:
            self.browser = await self.playwright.chromium.launch(headless=self.headless, args=[
                '--disable-blink-features=AutomationControlled',
            ])
            self.owns_browser = True
        except Exception as e:
            await self._stop_playwright()
            raise RadarOperationalError('browser_start_failed', f'Cannot start Chromium: {e}') from e
        storage_state = None
        if self.cookie_path.exists():
            try:
                import json
                with open(self.cookie_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    storage_state = {'cookies': data, 'origins': []}
                else:
                    storage_state = data
                logger.info(f'Loaded cookies from {self.cookie_path}')
            except Exception as e:
                raise RadarOperationalError(
                    'cookies_invalid',
                    f'Cannot read cookie file {self.cookie_path}. Replace it manually after fixing JSON.',
                ) from e

        if self.context is None:
            self.context = await self.browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={'width': 1280, 'height': 800},
                locale='ru-RU',
                storage_state=storage_state,
            )
        self.authentication_state = 'public'

        self._cleanup_old_screenshots()

        if storage_state:
            valid, validation_reason = await self._validate_cookies()
            if valid:
                self.authentication_state = 'authenticated'
            if not valid and self.cookie_path.exists():
                failure_reason = 'challenge_detected' if validation_reason == 'challenge_detected' else 'authentication_required'
                if self.diagnostic_mode or self.headless:
                    raise RadarOperationalError(
                        failure_reason,
                        f'TikTok authentication is required ({validation_reason}).',
                    )
                self.last_authentication_state = validation_reason
                raise RadarOperationalError(
                    failure_reason,
                    f'TikTok authentication preflight failed ({validation_reason}); run refresh_tiktok_cookies.py.',
                )

        logger.info('Browser started')

    async def close(self):
        if not self.diagnostic_mode and self.authentication_state == 'authenticated' and self.owns_browser and self.context and self.cookie_path:
            try:
                cookies = await self.context.cookies()
                storage_data = {'cookies': cookies, 'origins': []}
                write_state_atomic(self.cookie_path, storage_data)
                logger.info(f'Saved {len(cookies)} cookies to {self.cookie_path}')
            except Exception as e:
                logger.warning(f'Failed to save cookies: {e}')
        if self.browser:
            if self.connected_over_cdp:
                logger.info('Detached from Chrome (keeping browser open)')
            elif self.owns_browser:
                await self.browser.close()
                logger.info('Browser closed')
        await self._stop_playwright()

    async def _stop_playwright(self):
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def collect_all(self, sources: dict) -> list[dict]:
        planned = [('competitor', v) for v in sources.get('competitors', [])]
        planned += [('hashtag', v) for v in sources.get('hashtags', [])]
        planned += [('keyword', v) for v in sources.get('keywords', [])]
        rotational = sources.get('rotational', {})
        planned += [('hashtag', v) for v in rotational.get('hashtags', [])]
        planned += [('keyword', v) for v in rotational.get('keywords', [])]
        all_videos, seen = [], {}
        for ordinal, (source_type, value) in enumerate(planned, 1):
            started = datetime.now()
            attempt = {'run_id': self.run_id, 'ordinal': ordinal, 'source_type': source_type, 'source_value': value,
                       'started_at': utc_iso(), 'requested_limit': self.max_results, 'raw_items_received': 0,
                       'parsed_items': 0, 'items_with_valid_url': 0, 'unique_within_source': 0, 'duplicates_within_source': 0,
                       'unique_added_to_run': 0, 'duplicates_already_seen_in_run': 0, 'items_rejected': 0,
                       'rejection_reasons': {}, 'collection_method': 'none', 'status': 'error', 'error_reason': None,
                       'final_page_url': None, 'authentication_state': 'unknown'}
            try:
                videos = await (self.collect_from_hashtag(value) if source_type == 'hashtag' else self.collect_from_keyword(value) if source_type == 'keyword' else self.collect_from_competitor(value))
                attempt.update(raw_items_received=self.last_raw_items_received, parsed_items=len(videos), collection_method=self.last_collection_method,
                               final_page_url=self.last_final_page_url, authentication_state=self.last_authentication_state)
                limit_excluded = max(0, self.last_raw_items_received - len(videos))
                if limit_excluded:
                    attempt['items_rejected'] += limit_excluded
                    attempt['rejection_reasons']['requested_limit'] = limit_excluded
                local = set()
                for video in videos:
                    url = video.get('url')
                    if not url:
                        attempt['items_rejected'] += 1; attempt['rejection_reasons']['missing_url'] = attempt['rejection_reasons'].get('missing_url', 0) + 1; continue
                    attempt['items_with_valid_url'] += 1
                    key = video.get('video_id') or url
                    if key in local:
                        attempt['duplicates_within_source'] += 1; continue
                    local.add(key); attempt['unique_within_source'] += 1
                    if key in seen:
                        attempt['duplicates_already_seen_in_run'] += 1
                        seen[key]['matched_sources'].append({'source_type': source_type, 'source_value': value, 'ordinal': ordinal})
                        seen[key]['discovery_methods'].append(self.last_collection_method)
                        seen[key]['repeat_discoveries'] += 1
                    else:
                        apply_freshness(video, self.collected_at)
                        provenance = {'video_id': video.get('video_id'), 'canonical_url': url, 'primary_source_type': source_type,
                                      'primary_source_value': value, 'first_discovery_ordinal': ordinal,
                                      'matched_sources': [{'source_type': source_type, 'source_value': value, 'ordinal': ordinal}],
                                      'discovery_methods': [self.last_collection_method], 'repeat_discoveries': 0, 'new_to_database': False}
                        video['provenance'] = provenance; seen[key] = provenance; all_videos.append(video); attempt['unique_added_to_run'] += 1
                attempt['status'] = 'success' if videos else ('blocked' if self.last_collection_reason in ('authentication_required', 'tiktok_blocked') else 'empty')
                attempt['error_reason'] = self.last_collection_reason if not videos else None
            except RadarOperationalError as error:
                attempt.update(
                    raw_items_received=self.last_raw_items_received,
                    parsed_items=0,
                    collection_method=self.last_collection_method,
                    status='timeout' if error.reason == 'authentication_timeout' else 'error',
                    error_reason=error.reason,
                    final_page_url=self.last_final_page_url,
                    authentication_state=self.last_authentication_state,
                )
                raise
            except Exception as error:
                attempt.update(status='error', error_reason=type(error).__name__)
                logger.error('Source %s failed: %s', value, error)
            finally:
                attempt['completed_at'] = utc_iso(); attempt['duration_ms'] = int((datetime.now() - started).total_seconds() * 1000)
                self.source_attempts.append(attempt)
            if ordinal < len(planned):
                await async_random_sleep(3, 6)
        self.provenance = list(seen.values())
        return all_videos

    async def _dismiss_overlays(self, page) -> None:
        try:
            await page.evaluate('''
                () => {
                    document.querySelectorAll('[class*="Modal-overlay"], [data-floating-ui-portal]')
                        .forEach(el => el.remove());
                }
            ''')
            await asyncio.sleep(0.5)
        except Exception:
            pass

    async def _save_debug_screenshot(self, page, name: str) -> None:
        if not self._debug_mode:
            return
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        safe_name = name.replace('/', '_').replace('\\', '_').replace(' ', '_')[:80]
        path = str(self.screenshots_dir / f'{self.run_id}_{safe_name}.png')
        await page.screenshot(path=path)
        logger.debug(f'Screenshot saved: {path}')

    def _cleanup_old_screenshots(self) -> None:
        if not self.screenshots_dir.exists():
            return
        cutoff = time.time() - 7 * 86400
        for f in self.screenshots_dir.glob('*.png'):
            try:
                if f.stat().st_mtime < cutoff:
                    f.unlink()
                    logger.debug(f'Removed old screenshot: {f.name}')
            except Exception:
                pass

    async def _validate_cookies(self) -> tuple[bool, str]:
        if not self.cookie_path.exists():
            logger.info('No cookie file found, running without cookies')
            return False, 'cookie file is missing'

        page = await self.context.new_page()
        try:
            await page.goto(
                'https://www.tiktok.com/foryou?lang=ru-RU',
                wait_until='domcontentloaded',
                timeout=20000,
            )
            await asyncio.sleep(2)
            diagnostic = await inspect_page_authentication(page)
            if diagnostic.result == AUTH_SESSION_VALID:
                logger.info('Cookie preflight passed: %s', diagnostic.reason)
                return True, ''
            if diagnostic.result == AUTH_CHALLENGE:
                return False, 'challenge_detected'
            if diagnostic.result == AUTH_REFRESH_REQUIRED:
                return False, 'login_detected'
            return False, diagnostic.reason
        except Exception as e:
            logger.warning(f'Cookie validation error: {e}')
            return False, str(e)
        finally:
            await page.close()

    async def _activate_videos_tab(self, page) -> None:
        try:
            await page.evaluate('''
                () => {
                    const tab = document.querySelector('[data-e2e="videos-tab"]');
                    if (tab) {
                        tab.click();
                        return true;
                    }
                    return false;
                }
            ''')
            await asyncio.sleep(2)
        except Exception:
            pass

    async def _navigate_and_extract(
        self, url: str, source_type: str, source_value: str
    ) -> list[dict]:
        self.last_collection_reason = None
        self.last_collection_method = 'none'
        self.last_raw_items_received = 0
        self.last_final_page_url = None
        self.last_authentication_state = self.authentication_state
        page = await self.context.new_page()
        api_data: list[tuple[str, dict]] = []

        async def on_response(response):
            if not response.ok:
                return
            url_path = response.url
            if any(kw in url_path for kw in ['/api/', '/item_list/', '/search/', '/post/']):
                try:
                    body = await response.json()
                    if body:
                        api_data.append((url_path.split('?', 1)[0], body))
                        logger.debug(
                            f'API captured [{source_type}/{source_value}]: '
                            f'{url_path[:120]} | keys={list(body.keys())[:5]}'
                        )
                except Exception:
                    pass

        page.on('response', on_response)

        try:
            logger.info(f'Fetching {source_type}: {source_value}')

            for strategy in ('load', 'domcontentloaded'):
                try:
                    await page.goto(url, wait_until=strategy, timeout=30000)
                    break
                except Exception:
                    if strategy == 'domcontentloaded':
                        raise
                    logger.debug(
                        f'{strategy} timed out for {source_value}, '
                        f'falling back to domcontentloaded'
                    )

            await asyncio.sleep(3)
            try:
                await page.wait_for_selector(
                    'a[href*="/video/"], [data-e2e="user-post-item"], [data-e2e="search-video-item"]',
                    timeout=8000,
                )
            except Exception:
                pass

            await self._dismiss_overlays(page)

            blocked, reason = await self._is_blocked(page, source_value)
            self.last_final_page_url = page.url
            if 'login' in reason.lower():
                self.last_authentication_state = 'login_overlay'
            if blocked:
                logger.warning(f'Blocked at {url} — {reason}')
                self.last_collection_reason = (
                    'authentication_timeout' if 'login' in reason.lower()
                    else 'tiktok_blocked'
                )
                await self._save_debug_screenshot(page, f'blocked_{source_value}')
                if self.last_collection_reason == 'authentication_timeout':
                    raise RadarOperationalError(
                        'authentication_timeout',
                        'TikTok login overlay detected; interactive login is not automated.',
                    )
                return []

            videos = extract_from_api_responses(api_data, source_type, source_value)
            self.last_unsupported_schema_count = max(0, sum(len(body.get('itemList') or body.get('items') or body.get('data') or []) for _, body in api_data if isinstance(body, dict)) - len(videos))
            if len(videos) < self.max_results:
                await self._activate_videos_tab(page)
                await self._scroll(page, 4)
                await asyncio.sleep(2)
                try:
                    await page.wait_for_selector(
                        'a[href*="/video/"], [data-e2e="user-post-item"]',
                        timeout=5000,
                    )
                except Exception:
                    pass
                videos = extract_from_api_responses(api_data, source_type, source_value)
            if videos:
                self.last_collection_method = 'api'
                self.last_raw_items_received = len(videos)
                logger.info(f'  Got {len(videos)} videos (API)')
            else:
                self.last_collection_method = 'none'
                self.last_raw_items_received = 0
                logger.info('  No supported endpoint-specific video objects')

            if not videos:
                await self._save_debug_screenshot(page, f'empty_{source_value}')

            for v in videos:
                v['collected_at'] = self.collected_at
                v['run_id'] = self.run_id
                v['platform'] = 'tiktok'
                if not v.get('video_id'):
                    v['video_id'] = extract_video_id(v.get('url', ''))

            return videos[:self.max_results]

        except Exception as e:
            logger.error(f'Error at {url}: {e}')
            self.last_collection_reason = 'collection_failed'
            return []
        finally:
            page.remove_listener('response', on_response)
            await page.close()

    async def _fetch_video_stats(self, url: str) -> dict | None:
        page = await self.context.new_page()
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=20000)
            await asyncio.sleep(1)
            text = await page.content()
            import re as _re
            m = _re.search(
                r'<script[^>]*id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>'
                r'(.*?)</script>',
                text,
                _re.DOTALL,
            )
            if not m:
                return None
            import json as _json
            raw = m.group(1)
            json_data = _json.loads(raw)
            return parse_detail_page_stats(json_data)
        except Exception as e:
            logger.debug(f'Stats fetch failed for {url}: {e}')
            return None
        finally:
            await page.close()

    async def enrich_missing_stats(self, videos: list[dict]) -> list[dict]:
        need_stats = [
            (i, v) for i, v in enumerate(videos)
            if v.get('views') is None and not v.get('is_playlist')
        ]
        if not need_stats:
            return videos

        logger.info(
            f'Enriching stats for {len(need_stats)} videos (detail page visits)...'
        )
        enriched = 0
        for idx, v in need_stats:
            url = v.get('url', '')
            if not url:
                continue
            stats = await self._fetch_video_stats(url)
            if stats:
                for key in ('views', 'likes', 'comments', 'shares',
                            'author_followers', 'publish_time', 'published_at',
                            'caption', 'author_username'):
                    if stats.get(key) is not None and v.get(key) is None:
                        v[key] = stats[key]
                apply_freshness(v, self.collected_at)
                enriched += 1
            await asyncio.sleep(random.uniform(1.0, 2.0))

        logger.info(f'Stats enriched: {enriched}/{len(need_stats)}')
        return videos

    async def validate_candidate_links(self, videos: list[dict]) -> list[dict]:
        """Validate a bounded manual-review set; 200 error pages are not accepted."""
        for video in videos:
            page = await self.context.new_page()
            try:
                await page.goto(video['url'], wait_until='domcontentloaded', timeout=20_000)
                await asyncio.sleep(1)
                text = (await page.locator('body').inner_text())[:3000].lower()
                final_url = page.url
                found_id = extract_video_id(final_url)
                unavailable = any(term in text for term in ('video is unavailable', 'видео недоступно', 'couldn\'t find this video'))
                if 'challenge' in final_url.lower() or 'captcha' in text:
                    status = 'CHALLENGE'
                elif 'login' in final_url.lower():
                    status = 'LOGIN_REQUIRED'
                elif unavailable:
                    status = 'PRIVATE_OR_DELETED'
                elif found_id == video['video_id']:
                    status = 'AVAILABLE' if final_url.split('?', 1)[0] == video['url'] else 'REDIRECTED_TO_CANONICAL'
                else:
                    status = 'VALIDATION_UNKNOWN'
                video.update(link_status=status, link_validation_timestamp=utc_iso(), link_final_hostname=final_url.split('/')[2] if '//' in final_url else None)
                video['canonical_url_status'] = status
                if status not in ('AVAILABLE', 'REDIRECTED_TO_CANONICAL'):
                    video.setdefault('identity_warnings', []).append(f'link_validation={status}')
            except Exception:
                video.update(link_status='NETWORK_ERROR', link_validation_timestamp=utc_iso(), canonical_url_status='NETWORK_ERROR')
                video.setdefault('identity_warnings', []).append('link_validation=NETWORK_ERROR')
            finally:
                await page.close()
        return videos

    async def _is_blocked(self, page, label: str) -> tuple[bool, str]:
        try:
            url = page.url

            has_videos = await page.evaluate(
                'document.querySelectorAll("a[href*=\'/video/\']").length'
            )
            has_login_form = await page.evaluate(
                'document.querySelectorAll("input[type=\'password\'], input[name=\'password\']").length'
            )
            has_login_overlay = await page.evaluate('''
                () => {
                    const text = document.body.innerText.substring(0, 2000).toLowerCase();
                    const keywords = [
                        'log in to continue', 'войдите в аккаунт', 'login required',
                        'войдите или зарегистрируйтесь', 'вход', 'войти', 'log in', 'sign in',
                    ];
                    return keywords.some(k => text.includes(k));
                }
            ''')

            redirect_to_login = 'login' in url.lower() or 'auth' in url.lower()

            if redirect_to_login:
                return True, f'redirect to login (url: {url})'
            if has_login_form and not has_videos:
                return True, 'login form detected, no video content'
            if has_login_overlay and not has_videos:
                return True, 'login overlay detected, no video content'

            return False, ''
        except Exception as e:
            return False, str(e)

    async def _scroll(self, page, times: int = 4):
        for _ in range(times):
            try:
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(random.uniform(2, 4))
            except Exception:
                break

    async def collect_from_competitor(self, username: str) -> list[dict]:
        name = username.replace('@', '').strip()
        url = f'https://www.tiktok.com/@{name}'
        return await self._navigate_and_extract(url, 'competitor', name)

    async def collect_from_hashtag(self, hashtag: str) -> list[dict]:
        tag = hashtag.replace('#', '').strip()
        url = f'https://www.tiktok.com/tag/{tag}'
        return await self._navigate_and_extract(url, 'hashtag', tag)

    async def collect_from_keyword(self, keyword: str) -> list[dict]:
        url = f'https://www.tiktok.com/search?q={quote(keyword)}'
        return await self._navigate_and_extract(url, 'keyword', keyword)
