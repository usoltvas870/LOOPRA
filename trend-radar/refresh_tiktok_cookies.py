#!/usr/bin/env python3
"""Safely refresh TikTok cookies through a user-operated visible browser."""

import asyncio
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from playwright.async_api import async_playwright
from utils import get_cookie_path, load_env, setup_logging


PROJECT_ROOT = Path(__file__).resolve().parent
PENDING_PATH = PROJECT_ROOT / 'data' / 'tiktok_cookies.pending.json'
BACKUP_DIR = PROJECT_ROOT / 'data' / 'cookie_backups'


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(65536), b''):
            digest.update(chunk)
    return digest.hexdigest()


def storage_state_summary(path: Path) -> tuple[bool, int]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return False, 0
    cookies = data.get('cookies') if isinstance(data, dict) else None
    return isinstance(cookies, list), len(cookies) if isinstance(cookies, list) else 0


def validate_storage_state(data: object) -> tuple[bool, str]:
    if not isinstance(data, dict):
        return False, 'storage state must be an object'
    cookies = data.get('cookies')
    if not isinstance(cookies, list) or not cookies:
        return False, 'cookies must be a non-empty list'
    if 'origins' not in data:
        return False, 'origins is missing'
    if not any('tiktok.com' in str(cookie.get('domain', '')).lower() for cookie in cookies if isinstance(cookie, dict)):
        return False, 'TikTok domain cookies are missing'
    return True, ''


def write_storage_state(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as temporary:
        json.dump(data, temporary)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)


def create_backup(cookie_path: Path) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stem = f'tiktok_cookies_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    backup = BACKUP_DIR / f'{stem}.json'
    suffix = 1
    while backup.exists():
        backup = BACKUP_DIR / f'{stem}_{suffix}.json'
        suffix += 1
    shutil.copy2(cookie_path, backup)
    if file_sha256(cookie_path) != file_sha256(backup):
        raise RuntimeError('Cookie backup integrity check failed')
    return backup


def promote_pending(cookie_path: Path, first_check_ok: bool, second_check_ok: bool) -> bool:
    if not first_check_ok or not second_check_ok or not PENDING_PATH.exists():
        return False
    try:
        data = json.loads(PENDING_PATH.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return False
    valid, _ = validate_storage_state(data)
    if not valid:
        return False
    os.replace(PENDING_PATH, cookie_path)
    return True


async def authenticated_page_check(page) -> tuple[bool, str]:
    if '/login' in page.url.lower() or '/auth' in page.url.lower():
        return False, 'login_or_auth_url'
    indicators = await page.evaluate('''
        () => {
            const text = document.body.innerText.substring(0, 2000).toLowerCase();
            const loginTerms = ['log in to continue', 'войдите в аккаунт', 'login required',
                'войдите или зарегистрируйтесь', 'вход', 'войти', 'log in', 'sign in'];
            return {
                hasPassword: Boolean(document.querySelector('input[type="password"], input[name="password"]')),
                hasLoginText: loginTerms.some(term => text.includes(term)),
                hasSsr: Boolean(document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__')),
            };
        }
    ''')
    if indicators['hasPassword'] or indicators['hasLoginText']:
        return False, 'login_wall_detected'
    if not indicators['hasSsr']:
        return False, 'ordinary_tiktok_page_not_confirmed'
    return True, ''


async def refresh() -> int:
    setup_logging()
    load_env()
    if not sys.stdin.isatty():
        print('LOGIN_RESULT=interactive_terminal_required')
        return 2

    cookie_path = get_cookie_path()
    if not cookie_path.exists():
        print('LOGIN_RESULT=authentication_not_confirmed')
        return 2

    valid, cookie_count = storage_state_summary(cookie_path)
    if not valid:
        print('LOGIN_RESULT=authentication_not_confirmed')
        return 2
    original_hash = file_sha256(cookie_path)
    original_stat = cookie_path.stat()
    backup = create_backup(cookie_path)
    print(f'COOKIE_BACKUP={backup}')
    print(f'COOKIE_PRE size={original_stat.st_size} mtime_ns={original_stat.st_mtime_ns} count={cookie_count} sha256={original_hash}')

    playwright = browser = context = verification_context = None
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://www.tiktok.com/login/phone-or-email', wait_until='domcontentloaded')
        print('В открывшемся браузере вручную войдите в TikTok. Не вводите логин, пароль или код в терминал. После полного входа и появления обычной страницы TikTok вернитесь в этот терминал и нажмите Enter. Для отмены нажмите Ctrl+C.')
        input('После успешного входа нажмите Enter...')

        first_ok, first_reason = await authenticated_page_check(page)
        print(f'LOGIN_FIRST_CHECK={"ok" if first_ok else first_reason}')
        if not first_ok:
            print('LOGIN_RESULT=authentication_not_confirmed')
            return 2

        storage_state = await context.storage_state()
        pending_ok, pending_reason = validate_storage_state(storage_state)
        if not pending_ok:
            print(f'LOGIN_PENDING_VALIDATION={pending_reason}')
            print('LOGIN_RESULT=pending_validation_failed')
            return 2
        write_storage_state(PENDING_PATH, storage_state)
        print(f'LOGIN_PENDING_VALIDATION=ok count={len(storage_state["cookies"])}')
        await context.close()
        context = None

        verification_context = await browser.new_context(storage_state=storage_state)
        verification_page = await verification_context.new_page()
        await verification_page.goto('https://www.tiktok.com/', wait_until='domcontentloaded')
        second_ok, second_reason = await authenticated_page_check(verification_page)
        print(f'LOGIN_SECOND_CHECK={"ok" if second_ok else second_reason}')
        if not promote_pending(cookie_path, first_ok, second_ok):
            print('LOGIN_RESULT=pending_validation_failed')
            return 2

        new_valid, new_count = storage_state_summary(cookie_path)
        if not new_valid:
            raise RuntimeError('Promoted cookie file cannot be read')
        print(f'COOKIE_POST count={new_count} sha256={file_sha256(cookie_path)}')
        print('LOGIN_RESULT=success')
        return 0
    except KeyboardInterrupt:
        print('LOGIN_RESULT=cancelled')
        return 2
    except Exception:
        print('LOGIN_RESULT=internal_error')
        return 1
    finally:
        if verification_context:
            await verification_context.close()
        if context:
            await context.close()
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()


if __name__ == '__main__':
    raise SystemExit(asyncio.run(refresh()))
