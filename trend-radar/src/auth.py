"""Secret-safe TikTok session diagnostics shared by refresh and collection."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


AUTH_SESSION_VALID = 'session_valid'
AUTH_REFRESH_REQUIRED = 'session_refresh_required'
AUTH_CHALLENGE = 'challenge_detected'
AUTH_CHECK_FAILED = 'session_check_failed'


@dataclass(frozen=True)
class AuthDiagnostic:
    result: str
    reason: str
    final_hostname: str | None = None
    cookie_count: int = 0
    tiktok_cookie_count: int = 0


def storage_state_diagnostics(path: Path) -> tuple[dict | None, AuthDiagnostic]:
    try:
        state = json.loads(path.read_text(encoding='utf-8'))
        cookies = state.get('cookies') if isinstance(state, dict) else None
        if not isinstance(cookies, list):
            return None, AuthDiagnostic(AUTH_REFRESH_REQUIRED, 'cookie_state_invalid')
    except FileNotFoundError:
        return None, AuthDiagnostic(AUTH_REFRESH_REQUIRED, 'cookie_file_missing')
    except (OSError, json.JSONDecodeError):
        return None, AuthDiagnostic(AUTH_REFRESH_REQUIRED, 'cookie_state_unreadable')
    tiktok = sum(1 for cookie in cookies if isinstance(cookie, dict) and 'tiktok.com' in str(cookie.get('domain', '')).lower())
    if not cookies or not tiktok:
        return None, AuthDiagnostic(AUTH_REFRESH_REQUIRED, 'tiktok_cookies_missing', cookie_count=len(cookies), tiktok_cookie_count=tiktok)
    return state, AuthDiagnostic(AUTH_CHECK_FAILED, 'browser_check_pending', cookie_count=len(cookies), tiktok_cookie_count=tiktok)


def write_state_atomic(path: Path, state: dict) -> None:
    """Write only validated Playwright state; never leave a partial cookie file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as temporary:
        json.dump(state, temporary)
        temporary_path = temporary.name
    os.replace(temporary_path, path)


async def inspect_page_authentication(page) -> AuthDiagnostic:
    """Classify UI state using independent URL, form, text and challenge signals."""
    hostname = None
    try:
        from urllib.parse import urlparse
        hostname = urlparse(page.url).hostname
        signals = await page.evaluate('''
            () => {
                const text = (document.body?.innerText || '').slice(0, 4000).toLowerCase();
                const includes = terms => terms.some(term => text.includes(term));
                return {
                    loginForm: Boolean(document.querySelector('input[type="password"], input[name="password"]')),
                    loginText: includes(['log in to continue', 'login required', 'войдите в аккаунт', 'войдите или зарегистрируйтесь']),
                    challenge: includes(['captcha', 'verify to continue', 'security check', 'подтвердите, что вы не робот']),
                    consent: includes(['accept all cookies', 'принять все cookies', 'cookie settings']),
                    ssr: Boolean(document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__')),
                    videoLinks: document.querySelectorAll('a[href*="/video/"]').length,
                };
            }
        ''')
    except Exception:
        return AuthDiagnostic(AUTH_CHECK_FAILED, 'browser_or_network_check_failed', hostname)

    url = page.url.lower()
    if 'challenge' in url or signals['challenge']:
        return AuthDiagnostic(AUTH_CHALLENGE, 'challenge_detected', hostname)
    if 'login' in url or '/auth' in url or signals['loginForm'] or signals['loginText']:
        return AuthDiagnostic(AUTH_REFRESH_REQUIRED, 'login_detected', hostname)
    if signals['consent'] and not (signals['ssr'] or signals['videoLinks']):
        return AuthDiagnostic(AUTH_CHECK_FAILED, 'consent_required', hostname)
    if signals['ssr'] or signals['videoLinks']:
        return AuthDiagnostic(AUTH_SESSION_VALID, 'authenticated_page_available', hostname)
    return AuthDiagnostic(AUTH_CHECK_FAILED, 'ui_state_unknown', hostname)
