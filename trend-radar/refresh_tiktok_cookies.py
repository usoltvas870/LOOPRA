#!/usr/bin/env python3
"""Check or manually refresh the isolated TikTok session without exposing secrets."""

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from playwright.async_api import async_playwright
from auth import (
    AUTH_CHECK_FAILED, AUTH_CHALLENGE, AUTH_REFRESH_REQUIRED, AUTH_SESSION_VALID,
    inspect_page_authentication, storage_state_diagnostics,
)
from utils import get_config_int, get_cookie_path, load_env, setup_logging


PROJECT_ROOT = Path(__file__).resolve().parent
PENDING_PATH = PROJECT_ROOT / 'data' / 'tiktok_cookies.pending.json'
BACKUP_DIR = PROJECT_ROOT / 'data' / 'cookie_backups'
AUTH_URL = 'https://www.tiktok.com/foryou?lang=ru-RU'


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(65536), b''):
            digest.update(chunk)
    return digest.hexdigest()


def storage_state_summary(path: Path) -> tuple[bool, int]:
    state, diagnostic = storage_state_diagnostics(path)
    return state is not None, diagnostic.cookie_count


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
        backup = BACKUP_DIR / f'{stem}_{suffix}.json'; suffix += 1
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


def emit(result: str) -> int:
    print(f'AUTH_RESULT={result}')
    return 0 if result == AUTH_SESSION_VALID else 2


async def check_session(cookie_path: Path, headless: bool = True) -> str:
    state, local = storage_state_diagnostics(cookie_path)
    print(f'AUTH_DIAGNOSTIC=profile=isolated_cookie_state cookie_file_exists={cookie_path.exists()} cookie_count={local.cookie_count} tiktok_cookie_count={local.tiktok_cookie_count}')
    if state is None:
        return local.result
    playwright = browser = context = None
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context(storage_state=state, locale='ru-RU')
        page = await context.new_page()
        await page.goto(AUTH_URL, wait_until='domcontentloaded', timeout=20_000)
        await asyncio.sleep(2)
        result = await inspect_page_authentication(page)
        print(f'AUTH_DIAGNOSTIC=final_hostname={result.final_hostname or "unknown"} reason={result.reason}')
        return result.result
    except Exception:
        return AUTH_CHECK_FAILED
    finally:
        if context: await context.close()
        if browser: await browser.close()
        if playwright: await playwright.stop()


async def refresh_session(cookie_path: Path, timeout_seconds: int) -> str:
    if not sys.stdin.isatty():
        return AUTH_REFRESH_REQUIRED
    if cookie_path.exists():
        create_backup(cookie_path)
    playwright = browser = context = None
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(locale='ru-RU')
        page = await context.new_page()
        await page.goto(AUTH_URL, wait_until='domcontentloaded', timeout=20_000)
        print(f'AUTH_REFRESH_WINDOW=opened timeout_seconds={timeout_seconds}')
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            result = await inspect_page_authentication(page)
            if result.result == AUTH_SESSION_VALID:
                state = await context.storage_state()
                valid, _ = validate_storage_state(state)
                if not valid:
                    return AUTH_CHECK_FAILED
                write_storage_state(PENDING_PATH, state)
                verification = await browser.new_context(storage_state=state, locale='ru-RU')
                try:
                    verify_page = await verification.new_page()
                    await verify_page.goto(AUTH_URL, wait_until='domcontentloaded', timeout=20_000)
                    second = await inspect_page_authentication(verify_page)
                finally:
                    await verification.close()
                if promote_pending(cookie_path, True, second.result == AUTH_SESSION_VALID):
                    return AUTH_SESSION_VALID
                return AUTH_CHECK_FAILED
            if result.result == AUTH_CHALLENGE:
                return AUTH_CHALLENGE
            await asyncio.sleep(5)
        return AUTH_REFRESH_REQUIRED
    except Exception:
        return AUTH_CHECK_FAILED
    finally:
        if context: await context.close()
        if browser: await browser.close()
        if playwright: await playwright.stop()


async def main(args) -> int:
    load_env(); setup_logging()
    cookie_path = get_cookie_path()
    if args.check:
        return emit(await check_session(cookie_path, headless=True))
    timeout = args.timeout or get_config_int('AUTH_REFRESH_TIMEOUT_SECONDS', 300)
    if timeout < 60:
        raise SystemExit('--timeout must be at least 60 seconds')
    return emit(await refresh_session(cookie_path, timeout))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='run a fast non-interactive session preflight')
    parser.add_argument('--timeout', type=int, help='manual refresh timeout in seconds (default: 300)')
    raise SystemExit(asyncio.run(main(parser.parse_args())))
