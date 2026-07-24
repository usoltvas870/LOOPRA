"""Production-safe page-context range replay for one observed TikTok response.

The signed media URL is accepted only while the candidate Playwright page is
open.  This adapter never serializes it, exports browser credentials, or lets
the page choose an output path.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import secrets
from dataclasses import dataclass
from pathlib import Path

from media_acquisition import MediaAcquisitionError, _ffprobe, _sha256


MAX_TOTAL_BYTES = 40 * 1024 * 1024
MIN_REPLAY_BYTES = 8 * 1024 * 1024
PROBE_BYTES = 16 * 1024
CHUNK_BYTES = 256 * 1024
FRAGMENT_BYTES = 64 * 1024
BROWSER_TIMEOUT_MS = 8_000
PYTHON_TIMEOUT_SECONDS = 12


@dataclass(frozen=True)
class PageRangeCaptureResult:
    status: str
    captured_bytes: int
    chunk_count: int
    media_sha256: str | None
    ffprobe_validation: dict
    error_code: str | None = None


def is_range_replay_eligible(facts: dict, body_status: str | None, maximum_file_bytes: int) -> bool:
    """Return true only for the proven large player-bound primary-path gap."""
    return bool(
        body_status in {"unavailable", "response_finished_timeout"}
        and facts.get("scheme") == "https"
        and facts.get("content_type") == "video/mp4"
        and facts.get("status") == 200
        and str(facts.get("accept_ranges") or "").lower() == "bytes"
        and isinstance(facts.get("content_length"), int)
        and MIN_REPLAY_BYTES <= facts["content_length"] <= min(MAX_TOTAL_BYTES, maximum_file_bytes)
    )


async def capture_page_ranges(page, media_url: str, *, target_path: Path, total_bytes: int) -> PageRangeCaptureResult:
    """Validate repeatable ranges then atomically assemble the exact MP4."""
    if total_bytes < MIN_REPLAY_BYTES or total_bytes > MAX_TOTAL_BYTES:
        return PageRangeCaptureResult("FAILED", 0, 0, None, {"valid": False}, "RANGE_MAX_BYTES_EXCEEDED")
    if target_path.exists() or target_path.with_suffix(target_path.suffix + ".part").exists():
        return PageRangeCaptureResult("FAILED", 0, 0, None, {"valid": False}, "RANGE_ASSEMBLY_INCOMPLETE")

    total = await _verify_range_consistency(page, media_url, total_bytes)
    if isinstance(total, str):
        return PageRangeCaptureResult("FAILED", 0, 0, None, {"valid": False}, total)

    part = target_path.with_suffix(target_path.suffix + ".part")
    captured = chunks = 0
    digest = hashlib.sha256()
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with part.open("xb") as output:
            for start in range(0, total, CHUNK_BYTES):
                end = min(total - 1, start + CHUNK_BYTES - 1)
                payload = await _fetch_range(page, media_url, start, end, binding_name=f"__loopraRange_{secrets.token_hex(8)}")
                if isinstance(payload, str):
                    return PageRangeCaptureResult("FAILED", captured, chunks, None, {"valid": False}, payload)
                chunk, returned_total = payload
                if returned_total != total:
                    return PageRangeCaptureResult("FAILED", captured, chunks, None, {"valid": False}, "RANGE_TOTAL_MISMATCH")
                if len(chunk) != end - start + 1:
                    return PageRangeCaptureResult("FAILED", captured, chunks, None, {"valid": False}, "RANGE_BODY_LENGTH_MISMATCH")
                output.write(chunk)
                digest.update(chunk)
                captured += len(chunk)
                chunks += 1
            output.flush()
            os.fsync(output.fileno())
        if captured != total or part.stat().st_size != total:
            return PageRangeCaptureResult("FAILED", captured, chunks, None, {"valid": False}, "RANGE_ASSEMBLY_INCOMPLETE")
        os.replace(part, target_path)
        validation = _validate_media(target_path, total)
        return PageRangeCaptureResult("COMPLETED", captured, chunks, validation["sha256"], validation["ffprobe"])
    except (OSError, MediaAcquisitionError) as error:
        return PageRangeCaptureResult("FAILED", captured, chunks, None, {"valid": False}, _error_code(error))
    finally:
        part.unlink(missing_ok=True)


async def _verify_range_consistency(page, media_url: str, expected_total: int) -> int | str:
    positions = (0, max(PROBE_BYTES, (expected_total // 2 // PROBE_BYTES) * PROBE_BYTES), expected_total - PROBE_BYTES, 0)
    hashes: list[str] = []
    for start in positions:
        end = min(expected_total - 1, start + PROBE_BYTES - 1)
        payload = await _fetch_range(page, media_url, start, end, binding_name=f"__loopraProbe_{secrets.token_hex(8)}")
        if isinstance(payload, str):
            return payload
        chunk, returned_total = payload
        if returned_total != expected_total:
            return "RANGE_TOTAL_MISMATCH"
        if len(chunk) != end - start + 1:
            return "RANGE_BODY_LENGTH_MISMATCH"
        hashes.append(hashlib.sha256(chunk).hexdigest())
    if hashes[0] != hashes[-1]:
        return "RANGE_REPEAT_FAILED"
    return expected_total


async def _fetch_range(page, media_url: str, start: int, end: int, *, binding_name: str) -> tuple[bytes, int] | str:
    fragments: list[bytes] = []
    expected_sequence = 0

    async def receive(_source, payload: dict) -> dict:
        nonlocal expected_sequence
        sequence, values = payload.get("sequence"), payload.get("bytes")
        if sequence != expected_sequence:
            raise MediaAcquisitionError("RANGE_STREAM_SEQUENCE_MISMATCH")
        if not isinstance(values, list) or not values or len(values) > FRAGMENT_BYTES:
            raise MediaAcquisitionError("RANGE_STREAM_BRIDGE_FAILED")
        if any(not isinstance(value, int) or value < 0 or value > 255 for value in values):
            raise MediaAcquisitionError("RANGE_STREAM_BRIDGE_FAILED")
        fragments.append(bytes(values))
        expected_sequence += 1
        return {"ack": sequence}

    try:
        await page.expose_binding(binding_name, receive)
        result = await asyncio.wait_for(page.evaluate(_RANGE_FETCH_SCRIPT, {
            "url": media_url, "start": start, "end": end, "bindingName": binding_name,
            "browserTimeoutMs": BROWSER_TIMEOUT_MS, "fragmentBytes": FRAGMENT_BYTES,
        }), timeout=PYTHON_TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        return "RANGE_FETCH_PYTHON_TIMEOUT"
    except MediaAcquisitionError as error:
        return str(error)
    except Exception:
        return "RANGE_STREAM_BRIDGE_FAILED"
    if result.get("result") == "aborted":
        return "RANGE_FETCH_BROWSER_TIMEOUT"
    if result.get("result") != "complete":
        return result.get("error_code", "RANGE_STREAM_BRIDGE_FAILED")
    content_range = result.get("content_range", "")
    if result.get("status") != 206:
        return "RANGE_STATUS_UNEXPECTED"
    if result.get("content_type") != "video/mp4":
        return "RANGE_HTML_RESPONSE"
    if content_range != f"bytes {start}-{end}/{result.get('total_bytes')}":
        return "RANGE_CONTENT_RANGE_INVALID"
    if result.get("total_bytes") is None or result["total_bytes"] > MAX_TOTAL_BYTES:
        return "RANGE_MAX_BYTES_EXCEEDED"
    if sum(map(len, fragments)) != end - start + 1:
        return "RANGE_BODY_LENGTH_MISMATCH"
    return b"".join(fragments), result["total_bytes"]


def _validate_media(path: Path, expected_size: int) -> dict:
    if path.stat().st_size != expected_size:
        raise MediaAcquisitionError("RANGE_TOTAL_MISMATCH")
    with path.open("rb") as input_file:
        head = input_file.read(512).lower()
    if b"<html" in head or b"<!doctype html" in head:
        raise MediaAcquisitionError("RANGE_HTML_RESPONSE")
    probe = _ffprobe(path)
    if not probe["valid"]:
        raise MediaAcquisitionError("RANGE_VALIDATION_FAILED")
    return {"sha256": _sha256(path), "ffprobe": probe}


def _error_code(error: Exception) -> str:
    text = str(error)
    return text if text.startswith("RANGE_") else "RANGE_VALIDATION_FAILED"


_RANGE_FETCH_SCRIPT = """async ({url, start, end, bindingName, browserTimeoutMs, fragmentBytes}) => {
    const controller = new AbortController(); let reader = null;
    const timer = setTimeout(() => controller.abort(), browserTimeoutMs);
    try {
        const response = await fetch(url, {headers: {'Range': `bytes=${start}-${end}`}, credentials: 'include', signal: controller.signal});
        if (response.status !== 206 || !response.body) return {result: 'failed', error_code: 'RANGE_STATUS_UNEXPECTED'};
        const contentType = (response.headers.get('content-type') || '').split(';', 1)[0].toLowerCase();
        const contentRange = response.headers.get('content-range') || '';
        const match = /^bytes (\\d+)-(\\d+)\\/(\\d+)$/.exec(contentRange);
        if (!match) return {result: 'failed', error_code: 'RANGE_CONTENT_RANGE_INVALID'};
        reader = response.body.getReader(); let sequence = 0;
        while (true) { const {done, value} = await reader.read(); if (done) break;
            for (let offset = 0; offset < value.byteLength; offset += fragmentBytes) {
                const fragment = value.slice(offset, Math.min(offset + fragmentBytes, value.byteLength));
                await globalThis[bindingName]({sequence, bytes: Array.from(fragment)}); sequence += 1;
            }
        }
        return {result: 'complete', status: response.status, content_type: contentType, content_range: contentRange, total_bytes: Number(match[3])};
    } catch (error) { return error?.name === 'AbortError' ? {result: 'aborted'} : {result: 'failed', error_code: 'RANGE_STREAM_BRIDGE_FAILED'}; }
    finally { clearTimeout(timer); if (reader) { try { await reader.cancel(); } catch (_) {} try { reader.releaseLock(); } catch (_) {} } }
}"""
