"""Bounded, public-first TikTok comment collection for LOOPRA 0.6.

The collector deliberately owns only the Playwright objects it creates.  It
never reads browser profiles, cookies, or credentials, and returns a
privacy-minimal in-memory projection for the Comment Intelligence layer.
"""

from __future__ import annotations

import asyncio
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


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
    diagnostic_reference: str | None = None


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


def _response_comment_roots(payload: Any) -> tuple[list[dict[str, Any]] | None, bool]:
    """Return only explicit comment-list shapes, never arbitrary text fields."""
    if not isinstance(payload, dict):
        return None, False
    for key in ("comments", "comment_list", "commentList"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)], True
    data = payload.get("data")
    if isinstance(data, dict):
        roots, recognized = _response_comment_roots(data)
        if recognized:
            return roots, True
    items = payload.get("item_list") or payload.get("itemList")
    if isinstance(items, list) and all(isinstance(item, dict) and isinstance(item.get("text") or item.get("commentText"), str) and (item.get("cid") is not None or item.get("comment_id") is not None) for item in items):
        return items, True
    return None, False


def extract_comments_from_response(payload: Any, *, start_order: int = 1) -> list[CollectedComment]:
    """Extract known comment-list shapes without retaining author/profile data."""
    roots, recognized = _response_comment_roots(payload)
    if not recognized or roots is None:
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
                 timeout_seconds: int = 45, no_new_limit: int = 3,
                 diagnostic_root: Path | None = None) -> None:
        if not 1 <= max_comments <= 800 or not 1 <= max_scrolls <= 50 or not 5 <= timeout_seconds <= 120:
            raise ValueError("COMMENT_COLLECTION_BOUNDS_INVALID")
        self.headless = headless
        self.max_comments = max_comments
        self.max_scrolls = max_scrolls
        self.timeout_seconds = timeout_seconds
        self.no_new_limit = no_new_limit
        self.diagnostic_root = diagnostic_root

    def collect(self, source_url: str) -> CommentCollectionResult:
        return asyncio.run(self._collect(source_url))

    async def _collect(self, source_url: str) -> CommentCollectionResult:
        playwright = browser = context = page = None
        captured: list[CollectedComment] = []
        network_calls = 0
        network_unrecognized = False
        network_inventory: list[dict[str, Any]] = []
        scrolls = 0
        stop_reason = "PUBLIC_COMMENTS_BLOCKED"
        captcha = rate_limit = login_overlay = False
        started = time.monotonic()
        recorder = _DiagnosticRecorder(self.diagnostic_root)
        try:
            from playwright.async_api import async_playwright

            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=self.headless)
            context = await browser.new_context(locale="ru-RU", viewport={"width": 1280, "height": 800})
            page = await context.new_page()

            async def on_response(response) -> None:
                nonlocal network_calls, network_unrecognized
                facts = _response_facts(response, len(network_inventory) + 1)
                candidate = facts["candidate_endpoint_category"] is not None
                if not candidate or not response.ok:
                    network_inventory.append(facts)
                    return
                try:
                    payload = await response.json()
                    facts["body_parsed"] = True
                except Exception as error:
                    facts["parse_error"] = type(error).__name__
                    network_inventory.append(facts)
                    return
                roots, recognized = _response_comment_roots(payload)
                rows = extract_comments_from_response(payload, start_order=len(captured) + 1)
                facts["extracted_comment_count"] = len(rows)
                facts["payload_shape_recognized"] = recognized
                if not recognized:
                    network_unrecognized = True
                if rows:
                    network_calls += 1
                    _append_unique(captured, rows, self.max_comments)
                network_inventory.append(facts)

            page.on("response", on_response)
            await page.goto(source_url, wait_until="domcontentloaded", timeout=self.timeout_seconds * 1000)
            await asyncio.sleep(1)
            await recorder.screenshot(page, "01_page_loaded.png")
            overlay_dismissed = await _dismiss_overlays(page)
            await recorder.screenshot(page, "02_after_overlay_attempt.png")
            panel = await _open_comment_panel(page)
            await recorder.screenshot(page, "03_after_comment_panel_attempt.png")
            dom_inventory = await _dom_inventory(page, panel)
            if panel["status"] == "COMMENTS_PANEL_NOT_FOUND":
                await recorder.screenshot(page, "04_after_first_comment_scroll.png")
                return await _result_and_diagnostics(
                    recorder, page, captured, network_calls, network_inventory, dom_inventory,
                    "COMMENTS_PANEL_NOT_FOUND", 1, 0, overlay_dismissed, panel,
                )
            if panel["status"] == "COMMENTS_PANEL_NOT_OPENED":
                await recorder.screenshot(page, "04_after_first_comment_scroll.png")
                return await _result_and_diagnostics(
                    recorder, page, captured, network_calls, network_inventory, dom_inventory,
                    "COMMENTS_PANEL_NOT_OPENED", 1, 0, overlay_dismissed, panel,
                )
            container = panel["container"]
            no_new = 0
            extraction_attempted = False
            while scrolls < self.max_scrolls and len(captured) < self.max_comments:
                if time.monotonic() - started >= self.timeout_seconds:
                    stop_reason = "TIMEOUT"; break
                dom_rows, visible_nodes = await _dom_rows(container)
                extraction_attempted = True
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
                    if visible_nodes and not dom_rows:
                        stop_reason = "COMMENTS_VISIBLE_BUT_NOT_EXTRACTED"
                    elif network_unrecognized:
                        stop_reason = "NETWORK_COMMENT_PAYLOAD_UNRECOGNIZED"
                    elif _explicit_zero_comment_evidence(await _comment_count_label(page, container)):
                        stop_reason = "ZERO_COMMENTS_CONFIRMED"
                    elif extraction_attempted:
                        stop_reason = "NO_NEW_COMMENTS"
                    else:
                        stop_reason = "COMMENTS_PANEL_OPEN_BUT_EMPTY"
                    break
                await _scroll_comment_container(container)
                scrolls += 1
                if scrolls == 1:
                    await recorder.screenshot(page, "04_after_first_comment_scroll.png")
                await asyncio.sleep(0.75)
            else:
                stop_reason = "MAX_SCROLLS" if scrolls >= self.max_scrolls else "MAX_COMMENTS"
            method = MIXED if network_calls and any(row.collection_method == DOM for row in captured) else (NETWORK_RESPONSE if network_calls else DOM)
            return await _result_and_diagnostics(
                recorder, page, captured, network_calls, network_inventory, dom_inventory, stop_reason,
                1, scrolls, overlay_dismissed, panel, collection_method=method,
                login_overlay_observed=login_overlay, captcha_observed=captcha, rate_limit_observed=rate_limit,
            )
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


_COMMENT_NAMES = re.compile(r"comment|comments|комментар", re.I)
_FORBIDDEN_BUTTON_NAMES = re.compile(r"like|share|login|log in|sign in|profile|лайк|подел|войти|профил", re.I)
_COMMENT_BUTTON_SELECTORS = (
    '[data-e2e="comment-icon"]', '[data-e2e="comment-button"]',
    '[data-e2e="browse-comment-icon"]', 'button[data-e2e*="comment"]',
)
_COMMENT_CONTAINER_SELECTORS = (
    '[data-e2e="comment-list"]', '[data-e2e="comment-list-container"]',
    '[data-e2e*="comment-list"]', '[role="dialog"] [data-e2e*="comment"]',
    '[class*="CommentList"]', '[class*="comment-list"]',
)


def _safe_button_name(value: str) -> bool:
    return bool(_COMMENT_NAMES.search(value)) and not bool(_FORBIDDEN_BUTTON_NAMES.search(value))


async def _first_unambiguous(locator) -> Any | None:
    try:
        return locator.first if await locator.count() == 1 else None
    except Exception:
        return None


async def _find_comment_button(page) -> tuple[Any | None, str | None]:
    try:
        role_target = await _first_unambiguous(page.get_by_role("button", name=_COMMENT_NAMES))
        if role_target is not None:
            name = await role_target.get_attribute("aria-label") or await role_target.inner_text()
            if _safe_button_name(name or ""):
                return role_target, "role=button[name~=comment]"
    except Exception:
        pass
    for selector in _COMMENT_BUTTON_SELECTORS:
        target = await _first_unambiguous(page.locator(selector))
        if target is None:
            continue
        try:
            label = " ".join(filter(None, [await target.get_attribute("aria-label"), await target.get_attribute("data-e2e"), await target.inner_text()]))
            if _safe_button_name(label):
                return target, selector
        except Exception:
            continue
    return None, None


async def _find_comment_container(page) -> tuple[Any | None, str | None]:
    for selector in _COMMENT_CONTAINER_SELECTORS:
        target = await _first_unambiguous(page.locator(selector))
        if target is None:
            continue
        try:
            if await target.is_visible():
                return target, selector
        except Exception:
            continue
    return None, None


async def _open_comment_panel(page) -> dict[str, Any]:
    button, button_selector = await _find_comment_button(page)
    if button is None:
        return {"status": "COMMENTS_PANEL_NOT_FOUND", "button_selector": None, "button_clicked": False, "container": None, "container_selector": None}
    try:
        await button.click(timeout=4_000)
    except Exception:
        return {"status": "COMMENTS_PANEL_NOT_OPENED", "button_selector": button_selector, "button_clicked": False, "container": None, "container_selector": None}
    for _ in range(4):
        container, selector = await _find_comment_container(page)
        if container is not None:
            return {"status": "OPEN", "button_selector": button_selector, "button_clicked": True, "container": container, "container_selector": selector}
        await asyncio.sleep(0.5)
    return {"status": "COMMENTS_PANEL_NOT_OPENED", "button_selector": button_selector, "button_clicked": True, "container": None, "container_selector": None}


async def _dom_rows(container) -> tuple[list[dict[str, Any]], int]:
    try:
        nodes = container.locator('[data-e2e="comment-item"]')
        count = await nodes.count()
        if not count:
            nodes = container.locator('article, [role="listitem"]'); count = await nodes.count()
        rows = await nodes.evaluate_all("""nodes => nodes.map((node, index) => ({
            id: node.getAttribute('data-comment-id') || null,
            text: (node.querySelector('[data-e2e="comment-level-1"], [data-e2e="comment-level-2"]') || node).innerText || '',
            like_count: (node.querySelector('[data-e2e="comment-like-count"]') || {}).innerText || '0',
            reply_count: 0,
            source_order: index + 1
        }))""")
        return rows, count
    except Exception:
        return [], 0


async def _scroll_comment_container(container) -> None:
    await container.evaluate("""el => {
        const target = el.scrollHeight > el.clientHeight ? el : el.querySelector('[style*="overflow"], [class*="scroll"]');
        if (target && target !== document.body && target !== document.documentElement) target.scrollBy(0, Math.max(target.clientHeight, 600));
    }""")


def _explicit_zero_comment_evidence(value: str | None) -> bool:
    return bool(value and re.search(r"(?:^|\s)0\s*(?:comments?|комментар(?:иев|ии|ия)?)\b|no comments", value, flags=re.I))


async def _comment_count_label(page, container) -> str | None:
    try:
        labels = await page.locator('[data-e2e*="comment"], [aria-label*="comment" i], [aria-label*="комментар" i]').evaluate_all("nodes => nodes.map(node => node.getAttribute('aria-label') || node.innerText || '').filter(Boolean).slice(0, 30)")
        return next((str(value) for value in labels if _COMMENT_NAMES.search(str(value))), None)
    except Exception:
        return None


def _response_facts(response, sequence: int) -> dict[str, Any]:
    parsed = urlsplit(response.url)
    path = parsed.path
    lowered = path.lower()
    category = "COMMENT_OR_REPLY" if any(value in lowered for value in ("comment", "reply", "aweme")) else None
    try:
        size = int(response.headers.get("content-length", "0")) or None
    except ValueError:
        size = None
    return {"sequence": sequence, "url_host": parsed.hostname, "url_path": path, "method": response.request.method, "status": response.status, "content_type": response.headers.get("content-type"), "response_size": size, "body_parsed": False, "candidate_endpoint_category": category, "extracted_comment_count": 0, "payload_shape_recognized": False, "parse_error": None}


async def _dom_inventory(page, panel: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for selector in _COMMENT_CONTAINER_SELECTORS:
        try:
            locator = page.locator(selector); count = await locator.count()
            if not count:
                continue
            text_nodes = await locator.locator('[data-e2e="comment-item"], article, [role="listitem"]').count()
            result.append({"selector": selector, "node_count": count, "text_bearing_count": text_nodes, "button_or_reply_indicators": 0, "scroll_container_identity": "CANDIDATE"})
        except Exception:
            continue
    return result


class _DiagnosticRecorder:
    def __init__(self, root: Path | None) -> None:
        self.root = root

    async def screenshot(self, page, name: str) -> None:
        if self.root is None:
            return
        self.root.mkdir(parents=True, exist_ok=True)
        try:
            await page.screenshot(path=str(self.root / name))
        except Exception:
            pass

    async def write(self, page, *, captured: list[CollectedComment], network_inventory: list[dict[str, Any]], dom_inventory: list[dict[str, Any]], stop_reason: str, overlay_dismissed: bool, panel: dict[str, Any]) -> str | None:
        if self.root is None:
            return None
        self.root.mkdir(parents=True, exist_ok=True)
        title = language = ""
        try:
            title = await page.title(); language = await page.locator("html").get_attribute("lang") or ""
        except Exception:
            pass
        video_visible = False
        try:
            video_visible = bool(await page.locator("video").count())
        except Exception:
            pass
        count_label = await _comment_count_label(page, panel.get("container")) if panel.get("container") is not None else None
        state = {"final_url": _safe_url(page.url), "document_title": title[:200], "video_id": _video_id_from_url(page.url), "access_mode": "GUEST_NO_SESSION", "login_overlay_observed": False, "login_overlay_dismissed": overlay_dismissed, "cookie_banner_observed": False, "captcha_observed": stop_reason == "CAPTCHA_OR_ANTI_BOT_CHALLENGE", "rate_limit_observed": stop_reason == "RATE_LIMITED", "video_player_visible": video_visible, "comment_button_candidates_found": 1 if panel.get("button_selector") else 0, "comment_button_selectors_or_roles_matched": [panel.get("button_selector")] if panel.get("button_selector") else [], "comment_button_clicked": bool(panel.get("button_clicked")), "comment_panel_visible": panel.get("status") == "OPEN", "comment_count_label_text": count_label[:120] if count_label else None, "comment_container_candidates_found": len(dom_inventory), "visible_comment_like_node_count": sum(item["text_bearing_count"] for item in dom_inventory), "page_language": language, "timestamps": {"written_at": datetime.now(timezone.utc).isoformat()}}
        (self.root / "page_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (self.root / "network_inventory.json").write_text(json.dumps(network_inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (self.root / "dom_inventory.json").write_text(json.dumps(dom_inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # Structural note is intentionally safer than serialising commenter DOM text/attributes.
        (self.root / "sanitized_comment_container.html").write_text("<section data-diagnostic=\"comment-container\"><!-- structural snapshot withheld to preserve commenter privacy --></section>\n", encoding="utf-8")
        (self.root / "diagnostic_summary.md").write_text(f"# Comment collection diagnostics\n\n- Stop reason: `{stop_reason}`\n- Extracted comment count: {len(captured)}\n- Network inventory entries: {len(network_inventory)}\n- DOM container candidates: {len(dom_inventory)}\n- Panel state: `{panel.get('status')}`\n- This diagnostic intentionally excludes commenter text, usernames, profile links, IDs, cookies and response payloads.\n", encoding="utf-8")
        return "diagnostics"


async def _result_and_diagnostics(recorder: _DiagnosticRecorder, page, captured: list[CollectedComment], network_calls: int, network_inventory: list[dict[str, Any]], dom_inventory: list[dict[str, Any]], stop_reason: str, browser_calls: int, scrolls: int, overlay_dismissed: bool, panel: dict[str, Any], *, collection_method: str = DOM, login_overlay_observed: bool = False, captcha_observed: bool = False, rate_limit_observed: bool = False) -> CommentCollectionResult:
    reference = await recorder.write(page, captured=captured, network_inventory=network_inventory, dom_inventory=dom_inventory, stop_reason=stop_reason, overlay_dismissed=overlay_dismissed, panel=panel)
    return CommentCollectionResult(tuple(captured), "GUEST_NO_SESSION", collection_method, stop_reason, browser_calls, network_calls, "PASS", login_overlay_observed, captcha_observed, rate_limit_observed, scrolls, reference)


def _safe_url(value: str) -> str:
    parsed = urlsplit(value)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def _video_id_from_url(value: str) -> str | None:
    match = re.search(r"/video/(\d{15,25})", urlsplit(value).path)
    return match.group(1) if match else None
