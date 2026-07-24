from __future__ import annotations

import asyncio
import hashlib
import sys
from pathlib import Path

RADAR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADAR_ROOT / "src"))

from range_replay_diagnostics import (
    MAX_FRAGMENT_BYTES,
    RangeBridgeResult,
    RangeStreamBridgeError,
    SequentialRangeWriter,
    assemble_verified_ranges,
    prove_page_range_bridge,
)
from range_diagnostics import RangeProbeResult


def test_writer_requires_zero_based_monotonic_bounded_fragments(tmp_path: Path) -> None:
    path = tmp_path / "bridge.part"
    with SequentialRangeWriter(path, 8) as writer:
        assert writer.append(0, b"abc") == {"ack": 0}
        assert writer.append(1, b"def") == {"ack": 1}
        try:
            writer.append(3, b"x")
        except RangeStreamBridgeError as error:
            assert str(error) == "RANGE_STREAM_SEQUENCE_MISMATCH"
        else:
            raise AssertionError("duplicate or missing sequence was accepted")
    assert path.read_bytes() == b"abcdef"


def test_writer_rejects_oversized_fragment_and_total(tmp_path: Path) -> None:
    with SequentialRangeWriter(tmp_path / "bridge.part", 4) as writer:
        for fragment, error_code in ((b"abcde", "RANGE_MAX_BYTES_EXCEEDED"), (b"x" * (MAX_FRAGMENT_BYTES + 1), "RANGE_STREAM_BRIDGE_FAILED")):
            try:
                writer.append(0, fragment)
            except RangeStreamBridgeError as error:
                assert str(error) == error_code
            else:
                raise AssertionError("invalid fragment was accepted")


class _Page:
    def __init__(self, fragments: list[bytes]) -> None:
        self.fragments = fragments
        self.binding = None

    async def expose_binding(self, name, binding) -> None:
        self.binding = binding

    async def evaluate(self, script, data):
        for sequence, fragment in enumerate(self.fragments):
            await self.binding(None, {"sequence": sequence, "bytes": list(fragment)})
        return {"result": "complete", "fragment_count": len(self.fragments)}


def test_bridge_hashes_sequential_fragments_and_cleans_temporary_file(tmp_path: Path) -> None:
    body = b"range-stream-proof"
    result = asyncio.run(prove_page_range_bridge(
        _Page([body[:5], body[5:]]), "memory", temporary_path=tmp_path / "bridge.part",
        start=0, end=len(body) - 1, expected_sha256=hashlib.sha256(body).hexdigest(),
        browser_timeout_ms=10, python_timeout_seconds=1,
    ))
    assert result.status == "PASS"
    assert result.captured_bytes == len(body)
    assert result.fragment_count == 2
    assert not (tmp_path / "bridge.part").exists()


def test_bridge_rejects_duplicate_sequence_and_cleans_temporary_file(tmp_path: Path) -> None:
    class _DuplicatePage(_Page):
        async def evaluate(self, script, data):
            await self.binding(None, {"sequence": 0, "bytes": [1]})
            await self.binding(None, {"sequence": 0, "bytes": [2]})

    result = asyncio.run(prove_page_range_bridge(
        _DuplicatePage([]), "memory", temporary_path=tmp_path / "bridge.part", start=0, end=1,
        expected_sha256=hashlib.sha256(b"\x01\x02").hexdigest(), browser_timeout_ms=10, python_timeout_seconds=1,
    ))
    assert result.status == "RANGE_STREAM_SEQUENCE_MISMATCH"
    assert not (tmp_path / "bridge.part").exists()


def test_assembly_plan_is_sequential_gapless_and_atomically_finalized(
    tmp_path: Path, monkeypatch
) -> None:
    import range_replay_diagnostics as replay

    body = bytes(range(19))
    requested_ranges = []

    async def fake_probe(page, media_url, *, label, start, end, **kwargs):
        requested_ranges.append((start, end))
        chunk = body[start:end + 1]
        return RangeProbeResult(
            label, start, end, "PASS", start, end, len(body), len(chunk),
            hashlib.sha256(chunk).hexdigest(), 1, 8_000, 12, False, False, "cancelled",
        )

    async def fake_bridge(page, media_url, *, temporary_path, start, end, **kwargs):
        chunk = body[start:end + 1]
        temporary_path.write_bytes(chunk)
        return RangeBridgeResult(
            "PASS", len(chunk), 1, hashlib.sha256(chunk).hexdigest(), "retained",
        )

    monkeypatch.setattr(replay, "fetch_page_range", fake_probe)
    monkeypatch.setattr(replay, "prove_page_range_bridge", fake_bridge)
    target = tmp_path / "assembled.mp4"
    result = asyncio.run(assemble_verified_ranges(
        object(), "memory", target_path=target, total_bytes=len(body), chunk_bytes=8,
    ))

    assert requested_ranges == [(0, 7), (8, 15), (16, 18)]
    assert result.status == "PASS"
    assert result.captured_bytes == len(body)
    assert result.chunk_count == 3
    assert result.sha256 == hashlib.sha256(body).hexdigest()
    assert target.read_bytes() == body
    assert not target.with_suffix(".mp4.part").exists()


def test_assembly_failure_removes_part_and_does_not_create_final(
    tmp_path: Path, monkeypatch
) -> None:
    import range_replay_diagnostics as replay

    async def failing_probe(page, media_url, *, label, start, end, **kwargs):
        return RangeProbeResult(
            label, start, end, "RANGE_TOTAL_MISMATCH", start, end, 99,
            end - start + 1, "a" * 64, 1, 8_000, 12, False, False, "cancelled",
        )

    monkeypatch.setattr(replay, "fetch_page_range", failing_probe)
    target = tmp_path / "failed.mp4"
    result = asyncio.run(assemble_verified_ranges(
        object(), "memory", target_path=target, total_bytes=10, chunk_bytes=4,
    ))

    assert result.status == "FAILED"
    assert result.error_code == "RANGE_TOTAL_MISMATCH"
    assert not target.exists()
    assert not target.with_suffix(".mp4.part").exists()
