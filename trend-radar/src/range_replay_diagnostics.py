"""Bounded, synthetic-testable proof for a page-to-Python range stream.

This is a diagnostic boundary only.  It writes a caller-owned temporary file,
never serializes a media URL, and removes the file after its hash comparison.
It is intentionally not wired into browser acquisition until live gates pass.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import secrets
import tempfile
from dataclasses import dataclass
from pathlib import Path

from range_diagnostics import fetch_page_range


MAX_FRAGMENT_BYTES = 64 * 1024
MAX_BRIDGE_BYTES = 256 * 1024


class RangeStreamBridgeError(ValueError):
    """Typed failure for a bounded page range bridge."""


@dataclass(frozen=True)
class RangeBridgeResult:
    status: str
    captured_bytes: int
    fragment_count: int
    sha256: str | None
    cleanup: str
    error_code: str | None = None


class SequentialRangeWriter:
    """Validate a strictly sequential, bounded stream and incrementally hash it."""

    def __init__(self, path: Path, maximum_bytes: int) -> None:
        if maximum_bytes < 1 or maximum_bytes > MAX_BRIDGE_BYTES:
            raise ValueError("maximum_bytes must be between 1 and MAX_BRIDGE_BYTES")
        self.path = path
        self.maximum_bytes = maximum_bytes
        self.expected_sequence = 0
        self.captured_bytes = 0
        self.fragment_count = 0
        self.digest = hashlib.sha256()
        self._file = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("xb")
        return self

    def append(self, sequence: int, fragment: bytes) -> dict:
        if sequence != self.expected_sequence:
            raise RangeStreamBridgeError("RANGE_STREAM_SEQUENCE_MISMATCH")
        if not fragment or len(fragment) > MAX_FRAGMENT_BYTES:
            raise RangeStreamBridgeError("RANGE_STREAM_BRIDGE_FAILED")
        if self.captured_bytes + len(fragment) > self.maximum_bytes:
            raise RangeStreamBridgeError("RANGE_MAX_BYTES_EXCEEDED")
        assert self._file is not None
        self._file.write(fragment)
        self.digest.update(fragment)
        self.expected_sequence += 1
        self.captured_bytes += len(fragment)
        self.fragment_count += 1
        return {"ack": sequence}

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self._file is not None:
            self._file.close()


async def prove_page_range_bridge(page, media_url: str, *, temporary_path: Path,
                                  start: int, end: int, expected_sha256: str,
                                  browser_timeout_ms: int = 8_000,
                                  python_timeout_seconds: int = 12,
                                  remove_temporary: bool = True,
                                  binding_name: str | None = None) -> RangeBridgeResult:
    """Bridge one ≤256 KiB range and always remove its temporary artifact."""
    expected_bytes = end - start + 1
    if start < 0 or end < start or expected_bytes > MAX_BRIDGE_BYTES:
        raise ValueError("bridge range must be positive and no larger than MAX_BRIDGE_BYTES")
    if browser_timeout_ms <= 0 or python_timeout_seconds <= 0 or browser_timeout_ms >= python_timeout_seconds * 1000:
        raise ValueError("browser timeout must be positive and shorter than Python timeout")

    binding_name = binding_name or f"__loopraRangeFragment_{secrets.token_hex(8)}"
    writer = SequentialRangeWriter(temporary_path, expected_bytes)

    async def receive(_source, payload: dict) -> dict:
        sequence = payload.get("sequence")
        values = payload.get("bytes")
        if not isinstance(sequence, int) or not isinstance(values, list) or any(not isinstance(value, int) or value < 0 or value > 255 for value in values):
            raise RangeStreamBridgeError("RANGE_STREAM_BRIDGE_FAILED")
        return writer.append(sequence, bytes(values))

    cleanup = "removed"
    try:
        with writer:
            await page.expose_binding(binding_name, receive)
            payload = await asyncio.wait_for(page.evaluate(_RANGE_BRIDGE_SCRIPT, {
                "url": media_url, "start": start, "end": end,
                "bindingName": binding_name, "browserTimeoutMs": browser_timeout_ms,
                "maxBytes": expected_bytes, "fragmentBytes": MAX_FRAGMENT_BYTES,
            }), timeout=python_timeout_seconds)
            if payload.get("result") == "aborted":
                return RangeBridgeResult("RANGE_FETCH_BROWSER_TIMEOUT", writer.captured_bytes, writer.fragment_count, None, cleanup)
            if payload.get("result") != "complete" or writer.captured_bytes != expected_bytes:
                return RangeBridgeResult("RANGE_STREAM_BRIDGE_FAILED", writer.captured_bytes, writer.fragment_count, None, cleanup,
                                         payload.get("error_code", "RANGE_STREAM_BRIDGE_FAILED"))
            digest = writer.digest.hexdigest()
            if digest != expected_sha256:
                return RangeBridgeResult("RANGE_STREAM_BRIDGE_FAILED", writer.captured_bytes, writer.fragment_count, digest, cleanup,
                                         "RANGE_STREAM_SEQUENCE_MISMATCH")
            return RangeBridgeResult("PASS", writer.captured_bytes, writer.fragment_count, digest, cleanup)
    except asyncio.TimeoutError:
        return RangeBridgeResult("RANGE_FETCH_PYTHON_TIMEOUT", writer.captured_bytes, writer.fragment_count, None, cleanup)
    except RangeStreamBridgeError as error:
        return RangeBridgeResult(str(error), writer.captured_bytes, writer.fragment_count, None, cleanup, str(error))
    except Exception as error:
        return RangeBridgeResult("RANGE_STREAM_BRIDGE_FAILED", writer.captured_bytes, writer.fragment_count, None, cleanup, type(error).__name__)
    finally:
        if remove_temporary:
            temporary_path.unlink(missing_ok=True)


@dataclass(frozen=True)
class RangeAssemblyResult:
    status: str
    captured_bytes: int
    chunk_count: int
    sha256: str | None
    local_path: str | None
    error_code: str | None = None


async def assemble_verified_ranges(page, media_url: str, *, target_path: Path, total_bytes: int,
                                   chunk_bytes: int = MAX_BRIDGE_BYTES,
                                   python_timeout_seconds: int = 12) -> RangeAssemblyResult:
    """Sequentially assemble a verified resource from independently hashed ranges."""
    if total_bytes < 1 or total_bytes > 40 * 1024 * 1024:
        raise ValueError("total_bytes must be between 1 and 40 MiB")
    if chunk_bytes < 1 or chunk_bytes > MAX_BRIDGE_BYTES:
        raise ValueError("chunk_bytes must be between 1 and MAX_BRIDGE_BYTES")
    if target_path.exists():
        raise ValueError("refusing to overwrite existing target")
    part = target_path.with_suffix(target_path.suffix + ".part")
    if part.exists():
        raise ValueError("refusing to reuse an incomplete part file")
    captured = 0
    chunks = 0
    digest = hashlib.sha256()
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with part.open("xb") as output:
            for start in range(0, total_bytes, chunk_bytes):
                end = min(total_bytes - 1, start + chunk_bytes - 1)
                probe = await fetch_page_range(page, media_url, label="assembly_probe", start=start, end=end,
                                               python_timeout_seconds=python_timeout_seconds, fetch_variant="credentials_only")
                if probe.status != "PASS" or probe.total_bytes != total_bytes or not probe.body_sha256:
                    return RangeAssemblyResult("FAILED", captured, chunks, None, None, probe.status)
                temporary = Path(tempfile.gettempdir()) / f"loopra-range-{secrets.token_hex(12)}.part"
                bridge = await prove_page_range_bridge(page, media_url, temporary_path=temporary, start=start, end=end,
                                                        expected_sha256=probe.body_sha256,
                                                        python_timeout_seconds=python_timeout_seconds,
                                                        remove_temporary=False,
                                                        binding_name=f"__loopraRangeAssembly_{chunks}_{secrets.token_hex(8)}")
                if bridge.status != "PASS":
                    temporary.unlink(missing_ok=True)
                    return RangeAssemblyResult("FAILED", captured, chunks, None, None, bridge.status)
                chunk = temporary.read_bytes()
                temporary.unlink(missing_ok=True)
                if len(chunk) != end - start + 1:
                    return RangeAssemblyResult("FAILED", captured, chunks, None, None, "RANGE_BODY_LENGTH_MISMATCH")
                output.write(chunk)
                digest.update(chunk)
                captured += len(chunk)
                chunks += 1
            output.flush()
            os.fsync(output.fileno())
        if captured != total_bytes or part.stat().st_size != total_bytes:
            return RangeAssemblyResult("FAILED", captured, chunks, None, None, "RANGE_ASSEMBLY_INCOMPLETE")
        os.replace(part, target_path)
        return RangeAssemblyResult("PASS", captured, chunks, digest.hexdigest(), str(target_path))
    finally:
        if part.exists():
            part.unlink(missing_ok=True)


_RANGE_BRIDGE_SCRIPT = """async ({url, start, end, bindingName, browserTimeoutMs, maxBytes, fragmentBytes}) => {
    const controller = new AbortController();
    let reader = null;
    const timer = setTimeout(() => controller.abort(), browserTimeoutMs);
    try {
        const response = await fetch(url, {headers: {'Range': `bytes=${start}-${end}`}, credentials: 'include', cache: 'no-store', redirect: 'follow', referrer: document.URL, referrerPolicy: 'strict-origin-when-cross-origin', signal: controller.signal});
        if (response.status !== 206 || !response.body) return {result: 'failed', error_code: 'RANGE_STATUS_UNEXPECTED'};
        reader = response.body.getReader();
        let sequence = 0;
        let total = 0;
        while (true) {
            const {done, value} = await reader.read();
            if (done) break;
            for (let offset = 0; offset < value.byteLength; offset += fragmentBytes) {
                const fragment = value.slice(offset, Math.min(offset + fragmentBytes, value.byteLength));
                total += fragment.byteLength;
                if (total > maxBytes) return {result: 'failed', error_code: 'RANGE_MAX_BYTES_EXCEEDED'};
                await globalThis[bindingName]({sequence, bytes: Array.from(fragment)});
                sequence += 1;
            }
        }
        if (total !== maxBytes) return {result: 'failed', error_code: 'RANGE_BODY_LENGTH_MISMATCH'};
        return {result: 'complete', fragment_count: sequence};
    } catch (error) {
        if (error?.name === 'AbortError') return {result: 'aborted'};
        return {result: 'failed', error_code: 'RANGE_STREAM_BRIDGE_FAILED'};
    } finally {
        clearTimeout(timer);
        if (reader) { try { await reader.cancel(); } catch (_) {} try { reader.releaseLock(); } catch (_) {} }
    }
}"""
