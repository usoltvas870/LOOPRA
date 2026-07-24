from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

from ocr_evidence import OcrEvidenceError, OcrRunRequest, WindowsMediaOcrEngine, normalize_text, run_ocr_evidence
from selection_manifest import build_selection_manifest, write_selection_manifest


class FakeEngine:
    def availability(self) -> dict:
        return {"available": True, "engine_id": "fake", "engine_version": "1", "languages": ["en-US", "ru"]}

    def recognize(self, image_path: Path, language: str) -> dict:
        if image_path.name.startswith("missing"):
            raise OcrEvidenceError("synthetic failure")
        text = {"sample_00_0.000s.png": "  Привет   LOOPRA ", "sample_01_1.000s.png": "Привет LOOPRA", "sample_02_2.000s.png": "Next!"}.get(image_path.name, "")
        return {"text": text, "confidence": None, "blocks": [{"text": text, "reading_order": 0, "box": {"x": 1, "y": 2, "width": 3, "height": 4}}] if text else []}


def _candidate(video_id: str) -> dict:
    return {"video_id": video_id, "author_username": "test", "source_type": "test", "source_value": "test", "url": f"https://example.test/{video_id}", "caption": "test", "views": 1, "likes": 1, "comments": 0, "shares": 0, "author_followers": 1, "published_at": "2026-07-24T00:00:00Z", "collected_at": "2026-07-24T00:00:00Z", "final_score": 1, "reach_score": 1, "engagement_score": 1, "freshness_score": 1, "momentum_proxy": 1, "data_confidence": "HIGH", "identity_confidence": "HIGH", "classification": "CURRENT", "provenance": {"primary_source_type": "test", "primary_source_value": "test"}}


def _fixture(tmp_path: Path, names: list[str] | None = None) -> tuple[Path, Path]:
    manifest = write_selection_manifest(build_selection_manifest([_candidate("1")], radar_run_id="fixture"), tmp_path / "runs")
    root = tmp_path / "inspections" / "1"; frames = root / "frames"; frames.mkdir(parents=True)
    names = names or ["sample_00_0.000s.png", "sample_01_1.000s.png", "sample_02_2.000s.png"]
    results = []
    for index, name in enumerate(names):
        Image.new("RGB", (12, 8), "white").save(frames / name)
        results.append({"status": "success", "frame_path": name, "effective_timestamp_seconds": float(index)})
    (root / "inspection.json").write_text(json.dumps({"status": "COMPLETED", "media_sha256": "a" * 64, "sampling": {"frame_results": results}}), encoding="utf-8")
    return manifest, tmp_path / "inspections"


@pytest.mark.parametrize(("raw", "expected"), [("  a\n b  ", "a b"), ("Cafe\u0301", "Café"), ("✨  test", "✨ test")])
def test_normalization_is_mechanical(raw: str, expected: str) -> None:
    assert normalize_text(raw) == expected


def test_manifest_bound_result_orders_deduplicates_and_writes_atomically(tmp_path: Path) -> None:
    manifest, inspections = _fixture(tmp_path)
    result = run_ocr_evidence(OcrRunRequest(manifest, inspections, tmp_path / "out"), FakeEngine())
    candidate = result["candidates"][0]
    assert result["status"] == candidate["status"] == "COMPLETED"
    assert candidate["completed_frame_count"] == 3 and candidate["empty_frame_count"] == candidate["failed_frame_count"] == 0
    assert [event["text"] for event in candidate["text_events"]] == ["Привет LOOPRA", "Next!"]
    assert candidate["first_text_hook"]["hook_text"] == "Привет LOOPRA"
    assert candidate["ordered_observations"][0]["confidence"] is None
    saved = tmp_path / "out" / "fixture" / "candidates" / "1" / "ocr" / "ocr_result.json"
    assert json.loads(saved.read_text(encoding="utf-8"))["candidate_video_id"] == "1"
    reused = run_ocr_evidence(OcrRunRequest(manifest, inspections, tmp_path / "out"), FakeEngine())
    assert reused["candidates"][0]["reuse_status"] == "REUSED"


def test_missing_inspection_is_failed_without_escape(tmp_path: Path) -> None:
    manifest, inspections = _fixture(tmp_path)
    (inspections / "1" / "inspection.json").unlink()
    result = run_ocr_evidence(OcrRunRequest(manifest, inspections, tmp_path / "out"), FakeEngine())
    assert result["status"] == "FAILED"
    assert result["candidates"][0]["errors"] == ["inspection result is missing"]


def test_frame_failure_produces_degraded_result(tmp_path: Path) -> None:
    manifest, inspections = _fixture(tmp_path)
    payload = json.loads((inspections / "1" / "inspection.json").read_text(encoding="utf-8"))
    payload["sampling"]["frame_results"].append({"status": "success", "frame_path": "missing.png", "effective_timestamp_seconds": 4.0})
    (inspections / "1" / "inspection.json").write_text(json.dumps(payload), encoding="utf-8")
    result = run_ocr_evidence(OcrRunRequest(manifest, inspections, tmp_path / "out"), FakeEngine())
    candidate = result["candidates"][0]
    assert candidate["status"] == "DEGRADED" and candidate["failed_frame_count"] == 1


def test_out_of_bounds_box_is_a_frame_failure(tmp_path: Path) -> None:
    class InvalidBoxEngine(FakeEngine):
        def recognize(self, image_path: Path, language: str) -> dict:
            result = super().recognize(image_path, language)
            result["blocks"] = [{"text": "bad", "reading_order": 0, "box": {"x": 10, "y": 0, "width": 10, "height": 1}}]
            return result

    manifest, inspections = _fixture(tmp_path)
    result = run_ocr_evidence(OcrRunRequest(manifest, inspections, tmp_path / "out"), InvalidBoxEngine())
    candidate = result["candidates"][0]
    assert candidate["status"] == "FAILED" and candidate["failed_frame_count"] == 3


@pytest.mark.skipif(os.environ.get("LOOPRA_RUN_WINDOWS_OCR_INTEGRATION") != "1", reason="set LOOPRA_RUN_WINDOWS_OCR_INTEGRATION=1 to probe local Windows OCR")
@pytest.mark.parametrize(("language", "text"), [("en-US", "Hello LOOPRA"), ("ru", "Привет LOOPRA")])
def test_windows_ocr_reads_large_synthetic_text(tmp_path: Path, language: str, text: str) -> None:
    font_path = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "arial.ttf"
    if not font_path.is_file():
        pytest.skip("Arial is unavailable")
    image = Image.new("RGB", (1000, 220), "white")
    ImageDraw.Draw(image).text((20, 60), text, font=ImageFont.truetype(str(font_path), 64), fill="black")
    path = tmp_path / "synthetic.png"; image.save(path)
    result = WindowsMediaOcrEngine(timeout_seconds=30).recognize(path, language)
    assert text in result["text"]
