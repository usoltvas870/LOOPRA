import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

RADAR_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RADAR_ROOT / 'src'), str(RADAR_ROOT)]

from auth import (
    AUTH_CHALLENGE, AUTH_CHECK_FAILED, AUTH_REFRESH_REQUIRED, AUTH_SESSION_VALID,
    inspect_page_authentication, storage_state_diagnostics, write_state_atomic,
)
import refresh_tiktok_cookies as refresh


class AuthenticationTests(unittest.IsolatedAsyncioTestCase):
    async def test_page_states_are_distinct(self):
        cases = [
            ('https://www.tiktok.com/foryou', {'loginForm': False, 'loginText': False, 'challenge': False, 'consent': False, 'ssr': True, 'videoLinks': 1}, [{'name': 'sessionid', 'domain': '.tiktok.com'}], AUTH_SESSION_VALID),
            ('https://www.tiktok.com/foryou', {'loginForm': False, 'loginText': False, 'challenge': False, 'consent': False, 'ssr': True, 'videoLinks': 1}, [{'name': 'msToken', 'domain': '.tiktok.com'}], AUTH_REFRESH_REQUIRED),
            ('https://www.tiktok.com/login', {'loginForm': True, 'loginText': True, 'challenge': False, 'consent': False, 'ssr': False, 'videoLinks': 0}, [], AUTH_REFRESH_REQUIRED),
            ('https://www.tiktok.com/foryou', {'loginForm': False, 'loginText': False, 'challenge': True, 'consent': False, 'ssr': False, 'videoLinks': 0}, [], AUTH_CHALLENGE),
            ('https://www.tiktok.com/foryou', {'loginForm': False, 'loginText': False, 'challenge': False, 'consent': False, 'ssr': False, 'videoLinks': 0}, [{'name': 'sessionid', 'domain': '.tiktok.com'}], AUTH_CHECK_FAILED),
        ]
        for url, signals, cookies, expected in cases:
            with self.subTest(expected=expected):
                context = SimpleNamespace(cookies=AsyncMock(return_value=cookies))
                page = SimpleNamespace(url=url, context=context, evaluate=AsyncMock(return_value=signals))
                self.assertEqual((await inspect_page_authentication(page)).result, expected)

    async def test_network_failure_is_not_misclassified_as_logout(self):
        page = SimpleNamespace(url='https://www.tiktok.com/foryou', evaluate=AsyncMock(side_effect=RuntimeError('offline')))
        self.assertEqual((await inspect_page_authentication(page)).result, AUTH_CHECK_FAILED)


class StorageStateTests(unittest.TestCase):
    def test_atomic_write_and_missing_state_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'cookies.json'
            _, missing = storage_state_diagnostics(path)
            self.assertEqual(missing.result, AUTH_REFRESH_REQUIRED)
            write_state_atomic(path, {'cookies': [{'name': 'sessionid', 'domain': '.tiktok.com'}], 'origins': []})
            state, diagnostic = storage_state_diagnostics(path)
            self.assertIsNotNone(state)
            self.assertEqual(diagnostic.cookie_count, 1)
            self.assertEqual(json.loads(path.read_text(encoding='utf-8'))['cookies'][0]['domain'], '.tiktok.com')

    def test_guest_cookie_state_requires_real_login(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'cookies.json'
            write_state_atomic(path, {'cookies': [{'name': 'msToken', 'domain': '.tiktok.com'}], 'origins': []})
            state, diagnostic = storage_state_diagnostics(path)
            self.assertIsNone(state)
            self.assertEqual(diagnostic.result, AUTH_REFRESH_REQUIRED)
            self.assertEqual(diagnostic.reason, 'authenticated_tiktok_cookie_missing')

    def test_auth_result_is_emitted_once_without_secret_values(self):
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(refresh.emit(AUTH_SESSION_VALID), 0)
        self.assertEqual(output.getvalue().splitlines(), ['AUTH_RESULT=session_valid'])
