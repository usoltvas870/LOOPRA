from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import trend_workbook


@pytest.fixture(autouse=True)
def valid_media(monkeypatch):
    monkeypatch.setattr(trend_workbook, "_media_is_valid", lambda path: True)


def candidate(video_id: str, media: Path | None, **extra):
    return {
        "video_id": video_id, "candidate_id": f"candidate-{video_id}", "local_media_path": str(media) if media else None,
        "topical_relevance": 0.9, "audience_relevance": 0.8, "transferable_potential": 0.7,
        "virality_score": 0.6, "freshness_score": 0.5, "evidence_quality": 0.8,
        "caption": "Это осмысленная тема про личные границы", "query": "личные границы", "query_cluster": "личные границы",
        "url": f"https://www.tiktok.com/@example/video/{video_id}", "audio_role": "AUTHOR_SPEECH_USABLE",
        "transcript_segments": [{"start_seconds": 0, "end_seconds": 3, "text": "Я долго поддерживала всех и забывала о себе."}],
        "ocr_status": "GARBLED", "ocr_text": "???", **extra,
    }


def test_package_has_portable_relative_links_and_operator_workbook(tmp_path: Path):
    source = tmp_path / "source.mp4"; source.write_bytes(b"a valid test byte stream")
    result = trend_workbook.build_package(project_id="nura", search_run_id="run-01", candidates=[candidate("123", source)], output_root=tmp_path / "output")
    assert result["exported"] == 1 and result["relative_links"] == 1
    package = Path(result["package_path"]); workbook = load_workbook(result["workbook_path"])
    assert tuple(workbook.sheetnames) == trend_workbook.REQUIRED_SHEETS
    sheet = workbook["Кандидаты"]
    assert [cell.value for cell in sheet[1]][:3] == list(trend_workbook.OPERATOR_COLUMNS)
    assert sheet.freeze_panes == "D2" and sheet.auto_filter.ref
    target = sheet.cell(2, 12).hyperlink.target
    assert target == "videos\\001_123.mp4" and not Path(target).is_absolute()
    assert (package / target.replace("\\", "/")).is_file()
    assert sheet.cell(2, 8).value == "Я долго поддерживала всех и забывала о себе."
    assert sheet.cell(2, 9).value == "TRANSCRIPT_FIRST_CONTENT_SEGMENT"


def test_rejections_keep_missing_media_duplicate_and_low_relevance_out_of_main_sheet(tmp_path: Path):
    media = tmp_path / "source.mp4"; media.write_bytes(b"same media")
    other = tmp_path / "other.mp4"; other.write_bytes(b"other media")
    result = trend_workbook.build_package(project_id="nura", search_run_id="run-02", candidates=[candidate("a", media), candidate("b", media), candidate("c", None), candidate("d", other, topical_relevance=0.1)], output_root=tmp_path / "output")
    workbook = load_workbook(result["workbook_path"])
    assert workbook["Кандидаты"].max_row == 2
    reasons = {workbook["Отбраковано"].cell(row, 5).value for row in range(2, workbook["Отбраковано"].max_row + 1)}
    assert {"EXACT_DUPLICATE", "MEDIA_NOT_ACQUIRED", "LOW_RELEVANCE"} <= reasons


def test_low_relevance_cannot_be_rescued_by_virality():
    item = trend_workbook.assess_candidate({"topical_relevance": 0.1, "virality_score": 100.0})
    assert item["eligible"] is False and item["final_score"] == 0


def test_portability_detects_absolute_link(tmp_path: Path):
    source = tmp_path / "source.mp4"; source.write_bytes(b"media")
    result = trend_workbook.build_package(project_id="nura", search_run_id="run-03", candidates=[candidate("123", source)], output_root=tmp_path / "output")
    workbook = load_workbook(result["workbook_path"]); workbook["Кандидаты"].cell(2, 12).hyperlink = "C:\\absolute.mp4"; workbook.save(result["workbook_path"])
    with pytest.raises(trend_workbook.TrendWorkbookError, match="relative"):
        trend_workbook.validate_portability(Path(result["package_path"]))


def test_package_reuse_is_deterministic(tmp_path: Path):
    source = tmp_path / "source.mp4"; source.write_bytes(b"media")
    first = trend_workbook.build_package(project_id="nura", search_run_id="run-04", candidates=[candidate("123", source)], output_root=tmp_path / "output")
    second = trend_workbook.build_package(project_id="nura", search_run_id="run-04", candidates=[], output_root=tmp_path / "output")
    assert second["reuse"] is True and second["workbook_path"] == first["workbook_path"]
    manifest = json.loads((Path(first["package_path"]) / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == trend_workbook.SCHEMA_VERSION
