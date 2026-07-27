import asyncio
import logging
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import quote
from urllib.parse import urlparse
import re

from playwright.async_api import async_playwright, Browser

from parser import extract_video_data, extract_from_api_responses, parse_detail_page_stats
from utils import get_config_int, get_config, async_random_sleep, extract_video_id, get_cookie_path
from run_data import apply_freshness, utc_iso
from auth import (
    AUTH_CHALLENGE, AUTH_REFRESH_REQUIRED, AUTH_SESSION_VALID,
    has_authenticated_tiktok_cookie, inspect_page_authentication, write_state_atomic,
)

logger = logging.getLogger(__name__)

PUBLIC_ACCESS_SUFFICIENT = 'PUBLIC_ACCESS_SUFFICIENT'
PUBLIC_ACCESS_LIMITED = 'PUBLIC_ACCESS_LIMITED'
PUBLIC_ACCESS_BLOCKED = 'PUBLIC_ACCESS_BLOCKED'
CAPTCHA_OR_ANTI_BOT_CHALLENGE = 'CAPTCHA_OR_ANTI_BOT_CHALLENGE'
RATE_LIMITED = 'RATE_LIMITED'


class RadarOperationalError(RuntimeError):
    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

_VIDEO_PATH_RE = re.compile(r'^/@[^/]+/video/(\d{15,25})/?$')
_UNAVAILABLE_MARKERS = ('video is unavailable', 'video currently unavailable', 'видео недоступно', "couldn't find this video")
_PRIVATE_MARKERS = ('this account is private', 'this video is private', 'private video', 'video has been removed', 'video was deleted')
_REGION_MARKERS = ('unavailable in your region', 'not available in your region', 'not available in your country')


def _classify_video_page(expected_video_id: str, final_url: str, text: str, evidence: dict) -> tuple[str, str]:
    """Classify the user-visible permalink state; a successful navigation is insufficient."""
    normalized_text = (text or '').lower()
    parsed = urlparse(final_url)
    path_match = _VIDEO_PATH_RE.match(parsed.path)
    final_video_id = path_match.group(1) if path_match else None

    if 'challenge' in final_url.lower() or 'captcha' in normalized_text:
        return 'CHALLENGE', 'challenge_or_captcha_detected'
    if 'login' in final_url.lower() or (evidence.get('login_overlay') and not (evidence.get('metadata_video_id') == expected_video_id or evidence.get('item_detail_video_id') == expected_video_id)):
        return 'LOGIN_REQUIRED', 'login_overlay_or_redirect_detected'
    if any(marker in normalized_text for marker in _REGION_MARKERS):
        return 'REGION_RESTRICTED', 'region_restriction_marker_detected'
    if any(marker in normalized_text for marker in _PRIVATE_MARKERS):
        return 'PRIVATE_OR_DELETED', 'private_or_deleted_marker_detected'
    if any(marker in normalized_text for marker in _UNAVAILABLE_MARKERS):
        return 'NOT_FOUND', 'unavailable_or_not_found_marker_detected'
    if parsed.hostname not in ('tiktok.com', 'www.tiktok.com') or final_video_id != expected_video_id:
        return 'REDIRECTED_AWAY', 'final_url_is_not_the_expected_video_permalink'

    has_expected_page_identity = evidence.get('metadata_video_id') == expected_video_id or evidence.get('item_detail_video_id') == expected_video_id
    if not has_expected_page_identity:
        return 'GENERIC_SHELL', 'expected_video_id_not_present_in_video_page_state'
    if not evidence.get('video_playback_ready'):
        return 'RADAR_CONTEXT_UNCONFIRMED', 'expected_video_identity_present_but_media_not_ready'
    return 'RADAR_PLAYABLE', 'media_ready_in_radar_context_user_confirmation_required'


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
        self.access_mode = 'NO_SESSION_STATE'
        self.public_access_status = 'AUTH_OPTIONAL'
        self.login_overlay_observed = False
        self.overlay_dismissed = False
        self.public_cards_observed = 0
        self.captcha_observed = False
        self.rate_limit_observed = False
        self.blocking_reason: Optional[str] = None
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
                self.authentication_state = 'cdp_session_unknown'
                self.access_mode = 'AUTH_OPTIONAL'
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
        cookies = storage_state.get('cookies', []) if isinstance(storage_state, dict) else []
        if has_authenticated_tiktok_cookie(cookies):
            self.access_mode = 'AUTHENTICATED_SESSION'
            self.authentication_state = 'authenticated'
        elif cookies:
            self.access_mode = 'GUEST_SESSION'
            self.authentication_state = 'guest'
        else:
            self.access_mode = 'NO_SESSION_STATE'
            self.authentication_state = 'public'

        self._cleanup_old_screenshots()

        if self.access_mode == 'AUTHENTICATED_SESSION':
            valid, validation_reason = await self._validate_cookies()
            if not valid:
                self.authentication_state = 'public_fallback'
                self.last_authentication_state = validation_reason
                logger.warning('Authenticated session validation failed; continuing public-first (%s)', validation_reason)

        logger.info('Browser started')

    async def close(self):
        try:
            if not self.diagnostic_mode and self.authentication_state == 'authenticated' and self.owns_browser and self.context and self.cookie_path:
                try:
                    cookies = await self.context.cookies()
                    write_state_atomic(self.cookie_path, {'cookies': cookies, 'origins': []})
                    logger.info(f'Saved {len(cookies)} cookies to {self.cookie_path}')
                except Exception as e:
                    logger.warning(f'Failed to save cookies: {e}')
            if self.connected_over_cdp:
                logger.info('Detached from Chrome (keeping browser open)')
            else:
                if self.context is not None and hasattr(self.context, 'close'):
                    await self.context.close()
                self.context = None
                if self.owns_browser and self.browser is not None:
                    await self.browser.close()
                    logger.info('Browser closed')
        finally:
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
                               final_page_url=self.last_final_page_url, authentication_state=self.last_authentication_state,
                               access_mode=self.access_mode, public_access_status=self.public_access_status,
                               login_overlay_observed=self.login_overlay_observed, overlay_dismissed=self.overlay_dismissed,
                               public_cards_observed=self.public_cards_observed, captcha_observed=self.captcha_observed,
                               rate_limit_observed=self.rate_limit_observed)
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
                attempt['status'] = 'success' if videos else ('blocked' if self.last_collection_reason in ('public_access_blocked', 'captcha_or_anti_bot_challenge', 'rate_limited') else 'empty')
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
                    access_mode=self.access_mode,
                    public_access_status=self.public_access_status,
                    login_overlay_observed=self.login_overlay_observed,
                    overlay_dismissed=self.overlay_dismissed,
                    public_cards_observed=self.public_cards_observed,
                    captcha_observed=self.captcha_observed,
                    rate_limit_observed=self.rate_limit_observed,
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
        if len(all_videos) >= 20:
            self.public_access_status = PUBLIC_ACCESS_SUFFICIENT
            self.blocking_reason = None
        elif all_videos:
            self.public_access_status = PUBLIC_ACCESS_LIMITED
            self.blocking_reason = 'fewer_than_20_public_candidates'
        else:
            self.public_access_status = PUBLIC_ACCESS_BLOCKED
            self.blocking_reason = self.blocking_reason or 'public_candidates_not_observed'
        return all_videos

    async def _dismiss_overlays(self, page) -> bool:
        try:
            dismissed = await page.evaluate('''
                () => {
                    const close = document.querySelector(
                        '[data-e2e="modal-close-inner-button"], [data-e2e="login-modal-close-button"], button[aria-label="Close"], button[aria-label="Закрыть"]'
                    );
                    if (close) { close.click(); return true; }
                    const overlay = document.querySelector('[class*="Modal-overlay"], [data-floating-ui-portal]');
                    if (overlay) { overlay.remove(); return true; }
                    return false;
                }
            ''')
            await asyncio.sleep(0.5)
            return bool(dismissed)
        except Exception:
            return False

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

            videos = extract_from_api_responses(api_data, source_type, source_value)
            blocked, reason = await self._is_blocked(page, source_value, len(videos))
            if 'login_' in reason:
                self.login_overlay_observed = True
                self.last_authentication_state = 'login_overlay'
                self.overlay_dismissed = await self._dismiss_overlays(page) or self.overlay_dismissed
            if reason == 'captcha_or_anti_bot_challenge':
                self.captcha_observed = True; self.blocking_reason = reason; self.last_collection_reason = reason
                raise RadarOperationalError(reason, 'TikTok CAPTCHA or anti-bot challenge blocks public collection.')
            if reason == 'rate_limited':
                self.rate_limit_observed = True; self.blocking_reason = reason; self.last_collection_reason = reason
                raise RadarOperationalError(reason, 'TikTok rate limit blocks public collection.')

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
            blocked, reason = await self._is_blocked(page, source_value, len(videos))
            self.last_final_page_url = page.url
            if 'login_' in reason:
                self.login_overlay_observed = True
                self.last_authentication_state = 'login_overlay'
            if reason == 'captcha_or_anti_bot_challenge':
                self.captcha_observed = True; self.blocking_reason = reason; self.last_collection_reason = reason
                raise RadarOperationalError(reason, 'TikTok CAPTCHA or anti-bot challenge blocks public collection.')
            if reason == 'rate_limited':
                self.rate_limit_observed = True; self.blocking_reason = reason; self.last_collection_reason = reason
                raise RadarOperationalError(reason, 'TikTok rate limit blocks public collection.')
            if blocked and not videos:
                logger.warning(f'Public access blocked at {url} — {reason}')
                self.blocking_reason = reason
                self.last_collection_reason = 'public_access_blocked'
                await self._save_debug_screenshot(page, f'blocked_{source_value}')
                return []
            if videos:
                self.last_collection_method = 'api'
                self.last_raw_items_received = len(videos)
                self.public_cards_observed = max(self.public_cards_observed, len(videos))
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

        except RadarOperationalError:
            raise
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
        """Validate a bounded manual-review set from the user-visible permalink page."""
        for video in videos:
            page = await self.context.new_page()
            try:
                await page.goto(video['url'], wait_until='domcontentloaded', timeout=20_000)
                await page.wait_for_timeout(2_000)
                text = (await page.locator('body').inner_text())[:10_000]
                final_url = page.url
                evidence = await page.evaluate("""(expectedId) => {
                    const meta = [...document.querySelectorAll('meta')];
                    const value = (name) => meta.find((node) => node.getAttribute('property') === name || node.getAttribute('name') === name)?.getAttribute('content') || '';
                    const html = document.documentElement.innerHTML;
                    const itemDetail = /(?:ItemModule|itemDetail)[\\s\\S]{0,2000}?\\\"id\\\"\\s*:\\s*\\\"?(\\d{15,25})/.exec(html);
                    const ogUrl = value('og:url');
                    const metadataId = /\\/video\\/(\\d{15,25})/.exec(ogUrl)?.[1] || null;
                    const videos = [...document.querySelectorAll('video')];
                    return {
                        metadata_video_id: metadataId || null,
                        item_detail_video_id: itemDetail?.[1] || null,
                        video_playback_ready: videos.some((video) =>
                            Boolean(video.currentSrc || video.src)
                            && video.readyState >= 1
                            && video.videoWidth > 0
                            && video.videoHeight > 0
                            && Number.isFinite(video.duration)
                            && video.duration > 0
                        ),
                        login_overlay: Boolean(document.querySelector('[data-e2e*=login], [data-e2e*=Login], input[type=password]')),
                    };
                }""", video['video_id'])
                status, reason = _classify_video_page(video['video_id'], final_url, text, evidence)
                video.update(link_status=status, link_validation_timestamp=utc_iso(), link_final_hostname=urlparse(final_url).hostname,
                             link_final_url=final_url, link_validation_reason=reason)
                video['canonical_url_status'] = status
                if status != 'RADAR_PLAYABLE':
                    video.setdefault('identity_warnings', []).append(f'link_validation={status}')
            except Exception as error:
                video.update(link_status='NETWORK_ERROR', link_validation_timestamp=utc_iso(), canonical_url_status='NETWORK_ERROR',
                             link_validation_reason=f'navigation_or_inspection_failed:{type(error).__name__}')
                video.setdefault('identity_warnings', []).append('link_validation=NETWORK_ERROR')
            finally:
                await page.close()
        return videos

    async def _is_blocked(self, page, label: str, public_data_count: int = 0) -> tuple[bool, str]:
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
            try:
                access_signals = await page.evaluate('''
                    () => {
                        const text = (document.body?.innerText || '').slice(0, 4000).toLowerCase();
                        return {
                            challenge: ['captcha', 'verify to continue', 'security check', 'подтвердите, что вы не робот'].some(k => text.includes(k)),
                            rateLimited: ['too many requests', 'rate limit', 'слишком много запросов', 'попробуйте позже'].some(k => text.includes(k)),
                        };
                    }
                ''')
            except Exception:
                access_signals = {'challenge': False, 'rateLimited': False}

            redirect_to_login = 'login' in url.lower() or 'auth' in url.lower()
            public_results = int(has_videos or 0) + max(0, public_data_count)
            self.public_cards_observed = max(self.public_cards_observed, int(has_videos or 0), public_data_count)

            if access_signals.get('challenge') or 'challenge' in url.lower() or 'captcha' in url.lower():
                return True, 'captcha_or_anti_bot_challenge'
            if access_signals.get('rateLimited'):
                return True, 'rate_limited'
            if redirect_to_login or has_login_form or has_login_overlay:
                if public_results:
                    return False, 'login_overlay_with_public_results'
                return True, 'login_wall_blocks_public_results'

            return False, 'public_results_available' if public_results else ''
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
