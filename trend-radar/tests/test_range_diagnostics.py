from __future__ import annotations

import asyncio
import hashlib
import sys
from pathlib import Path

RADAR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADAR_ROOT / "src"))

from range_diagnostics import RangeProbeResult, consistency_verdict, fetch_page_range, parse_content_range, validate_range_response


def test_content_range_validation_requires_exact_response() -> None:
    assert parse_content_range("bytes 0-15/100") == (0, 15, 100)
    assert parse_content_range("bytes */100") is None
    assert validate_range_response({"status": 206, "content_type": "video/mp4", "content_range": "bytes 0-15/100", "body_length": 16}, 0, 15)[0] == "PASS"
    assert validate_range_response({"status": 206, "content_type": "text/html", "content_range": "bytes 0-15/100", "body_length": 16}, 0, 15)[0] == "RANGE_FETCH_NON_VIDEO"
    assert validate_range_response({"status": 206, "content_type": "video/mp4", "content_range": "bytes 1-16/100", "body_length": 16}, 0, 15)[0] == "RANGE_STREAM_SEQUENCE_MISMATCH"
    assert validate_range_response({"status": 403}, 0, 15)[0] == "RANGE_FETCH_FORBIDDEN"
    assert validate_range_response({"status": 416}, 0, 15)[0] == "RANGE_FETCH_UNSATISFIABLE"


class _Page:
    def __init__(self, result: dict) -> None:
        self.result = result

    async def evaluate(self, script, data):
        return self.result


def test_page_range_accepts_only_a_digest_and_never_exposes_body() -> None:
    result = asyncio.run(fetch_page_range(_Page({"result": "response", "status": 206, "content_type": "video/mp4", "content_range": "bytes 0-3/10", "body_length": 4, "body_sha256": hashlib.sha256(bytes([0, 1, 2, 3])).hexdigest(), "reader_cleanup": "cancelled"}), "https://example.invalid/signed", label="start", start=0, end=3, browser_timeout_ms=10, python_timeout_seconds=1))
    assert result.status == "PASS"
    assert result.body_sha256 and not hasattr(result, "body")
    assert result.reader_cleanup == "cancelled"


def test_browser_abort_and_python_timeout_are_distinguished() -> None:
    browser_abort = asyncio.run(fetch_page_range(_Page({"result": "aborted", "reader_cleanup": "cancelled"}), "memory", label="abort", start=0, end=1, browser_timeout_ms=10, python_timeout_seconds=1))
    assert browser_abort.status == "RANGE_FETCH_BROWSER_TIMEOUT"
    assert browser_abort.abort_requested and browser_abort.abort_confirmed

    class _HangingPage:
        async def evaluate(self, script, data):
            await asyncio.sleep(0.05)
    python_timeout = asyncio.run(fetch_page_range(_HangingPage(), "memory", label="timeout", start=0, end=1, browser_timeout_ms=5, python_timeout_seconds=0.01))
    assert python_timeout.status == "RANGE_FETCH_PYTHON_TIMEOUT"


def test_consistency_requires_equal_total_and_repeat_hash() -> None:
    def probe(label, digest, total=100):
        return RangeProbeResult(label, 0, 1, "PASS", 0, 1, total, 2, digest, 1, 10, 1, False, False, "cancelled")
    assert consistency_verdict([probe("start", "a"), probe("middle", "b"), probe("end", "c"), probe("repeat_start", "a")]) == "PASS"
    assert consistency_verdict([probe("start", "a"), probe("repeat_start", "b")]) == "RANGE_REPEAT_MISMATCH"
