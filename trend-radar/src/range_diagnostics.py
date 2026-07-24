"""Bounded, secret-safe page-context HTTP Range diagnostics.

This module is deliberately not connected to the media acquisition pipeline.
It proves (or rejects) one candidate's small-range semantics before any full
media assembly is considered.  Signed URLs are observed and used only in
memory inside the active Playwright page.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import asdict, dataclass


DEFAULT_BROWSER_TIMEOUT_MS = 8_000
DEFAULT_PYTHON_TIMEOUT_SECONDS = 12
MAX_PROBE_BYTES = 2 * 1024 * 1024

# These are deliberately names, not caller-provided fetch dictionaries.  The
# page context owns credentials and redirects; Python never receives headers.
FETCH_VARIANTS = {
    "default": {},
    "credentials_only": {"credentials": "include"},
    "credentials_referrer": {"credentials": "include", "referrer": "document"},
    "credentials_cache": {"credentials": "include", "cache": "no-store"},
    "page_native_bundle": {
        "credentials": "include",
        "cache": "no-store",
        "redirect": "follow",
        "referrer": "document",
        "referrer_policy": "strict-origin-when-cross-origin",
    },
}
# Compatibility name for Stage 3J evidence.  New code should use the explicit
# page_native_bundle identifier in records and reports.
FETCH_VARIANTS["page_native"] = FETCH_VARIANTS["page_native_bundle"]


@dataclass(frozen=True)
class RangeProbeResult:
    label: str
    requested_start: int
    requested_end: int
    status: str
    returned_start: int | None
    returned_end: int | None
    total_bytes: int | None
    body_length: int | None
    body_sha256: str | None
    elapsed_ms: int
    browser_timeout_ms: int
    python_timeout_seconds: int
    abort_requested: bool
    abort_confirmed: bool
    reader_cleanup: str
    exception_type: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def parse_content_range(value: str | None) -> tuple[int, int, int] | None:
    """Parse the only Content-Range shape accepted by the diagnostic."""
    if not value or not value.startswith("bytes ") or "/" not in value or "-" not in value:
        return None
    try:
        interval, total = value[6:].split("/", 1)
        start, end = interval.split("-", 1)
        start_value, end_value, total_value = int(start), int(end), int(total)
    except ValueError:
        return None
    if start_value < 0 or end_value < start_value or total_value <= end_value:
        return None
    return start_value, end_value, total_value


def validate_range_response(payload: dict, requested_start: int, requested_end: int) -> tuple[str, tuple[int, int, int] | None]:
    """Classify allowlisted page-context response metadata without raw headers."""
    if payload.get("status") == 403:
        return "RANGE_FETCH_FORBIDDEN", None
    if payload.get("status") == 416:
        return "RANGE_FETCH_UNSATISFIABLE", None
    if payload.get("status") != 206:
        return "RANGE_FETCH_UNEXPECTED_STATUS", None
    if payload.get("content_type") != "video/mp4":
        return "RANGE_FETCH_NON_VIDEO", None
    content_range = parse_content_range(payload.get("content_range"))
    if content_range is None:
        return "RANGE_FETCH_INVALID_CONTENT_RANGE", None
    if content_range[:2] != (requested_start, requested_end):
        return "RANGE_STREAM_SEQUENCE_MISMATCH", content_range
    expected_length = requested_end - requested_start + 1
    if payload.get("body_length") != expected_length:
        return "RANGE_BODY_LENGTH_MISMATCH", content_range
    return "PASS", content_range


async def fetch_page_range(
    page,
    media_url: str,
    *,
    label: str,
    start: int,
    end: int,
    browser_timeout_ms: int = DEFAULT_BROWSER_TIMEOUT_MS,
    python_timeout_seconds: int = DEFAULT_PYTHON_TIMEOUT_SECONDS,
    fetch_variant: str = "default",
) -> RangeProbeResult:
    """Fetch one bounded range with browser-side cancellation and reader cleanup."""
    if start < 0 or end < start or end - start + 1 > MAX_PROBE_BYTES:
        raise ValueError("range must be non-negative and no larger than MAX_PROBE_BYTES")
    if browser_timeout_ms <= 0 or python_timeout_seconds <= 0:
        raise ValueError("timeouts must be positive")
    if browser_timeout_ms >= python_timeout_seconds * 1000:
        raise ValueError("browser timeout must be shorter than Python timeout")
    if fetch_variant not in FETCH_VARIANTS:
        raise ValueError("fetch_variant must be default or page_native, or another allowlisted diagnostic variant")

    started = time.monotonic()
    try:
        payload = await asyncio.wait_for(
            page.evaluate(_RANGE_FETCH_SCRIPT, {
                "url": media_url, "start": start, "end": end,
                "browserTimeoutMs": browser_timeout_ms,
                "maxBytes": end - start + 1,
                "fetchVariant": fetch_variant,
            }),
            timeout=python_timeout_seconds,
        )
    except TimeoutError:
        return RangeProbeResult(label, start, end, "RANGE_FETCH_PYTHON_TIMEOUT", None, None, None, None, None,
                                _elapsed_ms(started), browser_timeout_ms, python_timeout_seconds, False, False, "unknown", "TimeoutError")
    except Exception as error:
        return RangeProbeResult(label, start, end, "RANGE_PAGE_CONTEXT_LOST", None, None, None, None, None,
                                _elapsed_ms(started), browser_timeout_ms, python_timeout_seconds, False, False, "unknown", type(error).__name__)

    if payload.get("result") == "aborted":
        return RangeProbeResult(label, start, end, "RANGE_FETCH_BROWSER_TIMEOUT", None, None, None, None, None,
                                _elapsed_ms(started), browser_timeout_ms, python_timeout_seconds, True, True,
                                payload.get("reader_cleanup", "unknown"))
    if payload.get("result") != "response":
        return RangeProbeResult(label, start, end, "RANGE_STREAM_READER_FAILED", None, None, None, None, None,
                                _elapsed_ms(started), browser_timeout_ms, python_timeout_seconds,
                                bool(payload.get("abort_requested")), bool(payload.get("abort_confirmed")),
                                payload.get("reader_cleanup", "unknown"), payload.get("exception_type"))

    body_length = payload.get("body_length")
    body_sha256 = payload.get("body_sha256")
    if not isinstance(body_length, int) or body_length < 0 or not isinstance(body_sha256, str) or len(body_sha256) != 64:
        return RangeProbeResult(label, start, end, "RANGE_STREAM_BRIDGE_FAILED", None, None, None, None, None,
                                _elapsed_ms(started), browser_timeout_ms, python_timeout_seconds, False, False,
                                payload.get("reader_cleanup", "unknown"))
    status, returned = validate_range_response(payload, start, end)
    returned_start, returned_end, total = returned if returned else (None, None, None)
    return RangeProbeResult(label, start, end, status, returned_start, returned_end, total, body_length,
                            body_sha256, _elapsed_ms(started), browser_timeout_ms,
                            python_timeout_seconds, bool(payload.get("abort_requested")),
                            bool(payload.get("abort_confirmed")), payload.get("reader_cleanup", "unknown"),
                            payload.get("exception_type"))


def consistency_verdict(probes: list[RangeProbeResult]) -> str:
    """Return PASS only for exact ranges, stable total and matching repeat hashes."""
    if not probes or any(probe.status != "PASS" for probe in probes):
        return "FAIL"
    totals = {probe.total_bytes for probe in probes}
    if len(totals) != 1:
        return "RANGE_TOTAL_MISMATCH"
    repeats = [probe for probe in probes if probe.label == "repeat_start"]
    starts = [probe for probe in probes if probe.label == "start"]
    if len(repeats) != 1 or len(starts) != 1 or repeats[0].body_sha256 != starts[0].body_sha256:
        return "RANGE_REPEAT_MISMATCH"
    return "PASS"


def _elapsed_ms(started: float) -> int:
    return round((time.monotonic() - started) * 1000)


_RANGE_FETCH_SCRIPT = """async ({url, start, end, browserTimeoutMs, maxBytes, fetchVariant}) => {
    const controller = new AbortController();
    let abortRequested = false;
    let abortConfirmed = false;
    let reader = null;
    let readerCleanup = 'not_started';
    const timer = setTimeout(() => { abortRequested = true; controller.abort(); }, browserTimeoutMs);
    try {
        const options = {headers: {'Range': `bytes=${start}-${end}`}, signal: controller.signal};
        const variants = {
            default: {},
            credentials_only: {credentials: 'include'},
            credentials_referrer: {credentials: 'include', referrer: document.URL},
            credentials_cache: {credentials: 'include', cache: 'no-store'},
            page_native_bundle: {credentials: 'include', cache: 'no-store', redirect: 'follow', referrer: document.URL, referrerPolicy: 'strict-origin-when-cross-origin'},
            page_native: {credentials: 'include', cache: 'no-store', redirect: 'follow', referrer: document.URL, referrerPolicy: 'strict-origin-when-cross-origin'},
        };
        Object.assign(options, variants[fetchVariant]);
        const response = await fetch(url, options);
        reader = response.body?.getReader();
        if (!reader) return {result: 'reader_failed', reader_cleanup: 'no_reader'};
        const bytes = [];
        while (true) {
            const {done, value} = await reader.read();
            if (done) break;
            if (bytes.length + value.byteLength > maxBytes) return {result: 'reader_failed', reader_cleanup: 'max_bytes_exceeded'};
            for (const byte of value) bytes.push(byte);
        }
        try { await reader.cancel(); readerCleanup = 'cancelled'; } catch (_) { readerCleanup = 'cancel_failed'; }
        const digest = await crypto.subtle.digest('SHA-256', new Uint8Array(bytes));
        const bodySha256 = [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, '0')).join('');
        return {result: 'response', status: response.status,
                content_type: (response.headers.get('content-type') || '').split(';', 1)[0].toLowerCase(),
                content_range: response.headers.get('content-range'), body_length: bytes.length, body_sha256: bodySha256,
                abort_requested: abortRequested, abort_confirmed: false, reader_cleanup: readerCleanup};
    } catch (error) {
        if (error?.name === 'AbortError') {
            abortConfirmed = true;
            if (reader) { try { await reader.cancel(); readerCleanup = 'cancelled'; } catch (_) { readerCleanup = 'cancel_failed'; } }
            else { readerCleanup = 'not_started'; }
            return {result: 'aborted', abort_requested: abortRequested, abort_confirmed: true, reader_cleanup: readerCleanup};
        }
        return {result: 'reader_failed', abort_requested: abortRequested, abort_confirmed: abortConfirmed,
                reader_cleanup: 'pending', exception_type: error?.name || 'Error'};
    } finally {
        clearTimeout(timer);
        if (reader) { try { await reader.cancel(); readerCleanup = 'cancelled'; } catch (_) { readerCleanup = 'cancel_failed'; } }
    }
}"""
