"""Bounded, public-first TikTok comment collection for LOOPRA 0.6.

The collector deliberately owns only the Playwright objects it creates.  It
never reads browser profiles, cookies, or credentials, and returns a
privacy-minimal in-memory projection for the Comment Intelligence layer.
"""

from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


NETWORK_RESPONSE = "NETWORK_RESPONSE"
DOM = "DOM"
MIXED = "MIXED"


@dataclass(frozen=True)
class CollectedComment:
    """Transient public comment projection; external IDs never leave memory."""

    external_id: str | None
    parent_external_id: str | None
    thread_depth: int
    text: str
    like_count: int
    reply_count: int
    created_at: str | None
    source_order: int
    collection_method: str


@dataclass(frozen=True)
class CommentCollectionResult:
    comments: tuple[CollectedComment, ...]
    access_mode: str
    collection_method: str
    stop_reason: str
    browser_calls: int
    network_calls: int
    cleanup_status: str
    login_overlay_observed: bool
    captcha_observed: bool
    rate_limit_observed: bool
    scrolls: int


def _positive_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _created_at(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
        try:
            return datetime.fromtimestamp(int(value), tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        except (OSError, OverflowError, ValueError):
            return None
    return None


def _comment_from_mapping(value: dict[str, Any], *, source_order: int, method: str,
                          parent_external_id: str | None = None, depth: int = 0) -> CollectedComment | None:
    text = value.get("text") or value.get("commentText") or value.get("content")
    if not isinstance(text, str) or not text.strip():
        return None
    external_id = value.get("cid") or value.get("comment_id") or value.get("id")
    parent = parent_external_id or value.get("parent_comment_id") or value.get("parent_cid")
    return CollectedComment(
        external_id=str(external_id) if external_id is not None else None,
        parent_external_id=str(parent) if parent is not None else None,
        thread_depth=depth,
        text=text,
        like_count=_positive_int(value.get("digg_count") or value.get("like_count") or value.get("likeCount")),
        reply_count=_positive_int(value.get("reply_comment_total") or value.get("reply_count") or value.get("replyCount")),
        created_at=_created_at(value.get("create_time") or value.get("created_at") or value.get("createTime")),
        source_order=source_order,
        collection_method=method,
    )


def extract_comments_from_response(payload: Any, *, start_order: int = 1) -> list[CollectedComment]:
    """Extract known comment-list shapes without retaining author/profile data."""
    if not isinstance(payload, dict):
        return []
    roots = payload.get("comments") or payload.get("comment_list") or payload.get("commentList")
    if not isinstance(roots, list):
        data = payload.get("data")
        if isinstance(data, dict):
            return extract_comments_from_response(data, start_order=start_order)
        return []
    result: list[CollectedComment] = []
    seen: set[tuple[str | None, str]] = set()

    def append(value: dict[str, Any], parent: str | None = None, depth: int = 0) -> None:
        item = _comment_from_mapping(value, source_order=start_order + len(result), method=NETWORK_RESPONSE,
                                     parent_external_id=parent, depth=depth)
        if item is not None and (item.external_id, item.text) not in seen:
            seen.add((item.external_id, item.text)); result.append(item)
        reply_parent = item.external_id if item is not None else parent
        for key in ("reply_comment", "replies", "replyComments"):
            replies = value.get(key)
            if isinstance(replies, list):
                for reply in replies:
                    if isinstance(reply, dict):
                        append(reply, reply_parent, depth + 1)

    for value in roots:
        if isinstance(value, dict):
            append(value)
    return result


def extract_comments_from_dom(rows: list[dict[str, Any]], *, start_order: int = 1) -> list[CollectedComment]:
    """Convert the DOM fallback's minimal fields into the same projection."""
    result: list[CollectedComment] = []
    for row in rows:
        item = _comment_from_mapping(row, source_order=start_order + len(result), method=DOM)
        if item is not None:
            result.append(item)
    return result


def classify_page_signals(*, url: str, text: str, visible_comment_count: int) -> str | None:
    """Visible comments take precedence over a non-blocking login overlay."""
    lowered = f"{url}\n{text}".lower()
    if "captcha" in lowered or "/challenge" in lowered:
        return "CAPTCHA_OR_ANTI_BOT_CHALLENGE"
    if "too many requests" in lowered or "rate limit" in lowered:
        return "RATE_LIMITED"
    if visible_comment_count == 0 and ("log in" in lowered or "login" in lowered or "sign in" in lowered):
        return "PUBLIC_COMMENTS_BLOCKED"
    return None


class PublicTikTokCommentCollector:
    """One video, one guest context, bounded scrolling, guaranteed cleanup."""

    def __init__(self, *, headless: bool = True, max_comments: int = 800, max_scrolls: int = 24,
                 timeout_seconds: int = 45, no_new_limit: int = 3) -> None:
        if not 1 <= max_comments <= 800 or not 1 <= max_scrolls <= 50 or not 5 <= timeout_seconds <= 120:
            raise ValueError("COMMENT_COLLECTION_BOUNDS_INVALID")
        self.headless = headless
        self.max_comments = max_comments
        self.max_scrolls = max_scrolls
        self.timeout_seconds = timeout_seconds
        self.no_new_limit = no_new_limit

    def collect(self, source_url: str) -> CommentCollectionResult:
        return asyncio.run(self._collect(source_url))

    async def _collect(self, source_url: str) -> CommentCollectionResult:
        playwright = browser = context = page = None
        captured: list[CollectedComment] = []
        network_calls = 0
        scrolls = 0
        stop_reason = "PUBLIC_COMMENTS_BLOCKED"
        captcha = rate_limit = login_overlay = False
        started = time.monotonic()
        try:
            from playwright.async_api import async_playwright

            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=self.headless)
            context = await browser.new_context(locale="ru-RU", viewport={"width": 1280, "height": 800})
            page = await context.new_page()

            async def on_response(response) -> None:
                nonlocal network_calls
                response_url = response.url.lower()
                if "comment" not in response_url or not response.ok:
                    return
                try:
                    payload = await response.json()
                except Exception:
                    return
                rows = extract_comments_from_response(payload, start_order=len(captured) + 1)
                if rows:
                    network_calls += 1
                    _append_unique(captured, rows, self.max_comments)

            page.on("response", on_response)
            await page.goto(source_url, wait_until="domcontentloaded", timeout=self.timeout_seconds * 1000)
            await asyncio.sleep(1)
            await _dismiss_overlays(page)
            no_new = 0
            while scrolls < self.max_scrolls and len(captured) < self.max_comments:
                if time.monotonic() - started >= self.timeout_seconds:
                    stop_reason = "TIMEOUT"; break
                dom_rows = await _dom_rows(page)
                before = len(captured)
                _append_unique(captured, extract_comments_from_dom(dom_rows, start_order=len(captured) + 1), self.max_comments)
                text = await page.locator("body").inner_text(timeout=3_000)
                signal = classify_page_signals(url=page.url, text=text, visible_comment_count=len(captured))
                captcha = signal == "CAPTCHA_OR_ANTI_BOT_CHALLENGE"
                rate_limit = signal == "RATE_LIMITED"
                login_overlay = "login" in text.lower() or "log in" in text.lower()
                if signal in {"CAPTCHA_OR_ANTI_BOT_CHALLENGE", "RATE_LIMITED", "PUBLIC_COMMENTS_BLOCKED"}:
                    stop_reason = signal; break
                if len(captured) >= self.max_comments:
                    stop_reason = "MAX_COMMENTS"; break
                no_new = no_new + 1 if len(captured) == before else 0
                if no_new >= self.no_new_limit:
                    stop_reason = "NO_NEW_COMMENTS"; break
                await page.evaluate("window.scrollBy(0, Math.max(window.innerHeight, 700))")
                scrolls += 1
                await asyncio.sleep(0.75)
            else:
                stop_reason = "MAX_SCROLLS" if scrolls >= self.max_scrolls else "MAX_COMMENTS"
            method = MIXED if network_calls and any(row.collection_method == DOM for row in captured) else (NETWORK_RESPONSE if network_calls else DOM)
            return CommentCollectionResult(tuple(captured), "GUEST_NO_SESSION", method, stop_reason, 1,
                                           network_calls, "PASS", login_overlay, captcha, rate_limit, scrolls)
        finally:
            cleanup_errors: list[Exception] = []
            for resource in (page, context, browser, playwright):
                if resource is None:
                    continue
                try:
                    close = getattr(resource, "close", None) or getattr(resource, "stop", None)
                    if close is not None:
                        await close()
                except Exception as error:  # cleanup is reported by callers/tests, never leaks resources silently
                    cleanup_errors.append(error)
            if cleanup_errors:
                # Avoid replacing a useful collection failure, but make cleanup failure observable.
                raise RuntimeError("BROWSER_CLEANUP_FAILED") from cleanup_errors[0]


def _append_unique(target: list[CollectedComment], values: list[CollectedComment], maximum: int) -> None:
    seen = {(item.external_id, item.text) for item in target}
    for value in values:
        key = (value.external_id, value.text)
        if key not in seen and len(target) < maximum:
            seen.add(key); target.append(value)


async def _dismiss_overlays(page) -> bool:
    try:
        return bool(await page.evaluate("""() => {
            const close = document.querySelector('[data-e2e="modal-close-inner-button"], [data-e2e="login-modal-close-button"], button[aria-label="Close"]');
            if (close) { close.click(); return true; }
            return false;
        }"""))
    except Exception:
        return False


async def _dom_rows(page) -> list[dict[str, Any]]:
    try:
        return await page.locator('[data-e2e="comment-item"]').evaluate_all("""nodes => nodes.map((node, index) => ({
            id: node.getAttribute('data-comment-id') || null,
            text: (node.querySelector('[data-e2e="comment-level-1"]') || node).innerText || '',
            like_count: (node.querySelector('[data-e2e="comment-like-count"]') || {}).innerText || '0',
            reply_count: 0,
            source_order: index + 1
        }))""")
    except Exception:
        return []
