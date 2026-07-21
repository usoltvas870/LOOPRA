from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "run_comic_pipeline_acceptance.py"


@pytest.mark.e2e
@pytest.mark.requires_ffmpeg
def test_comic_package_acceptance_runs_with_real_production_components(tmp_path: Path) -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("FFmpeg and ffprobe are required for comic package acceptance")
    if not Path("C:/Windows/Fonts/arial.ttf").is_file():
        pytest.skip("A Cyrillic TTF/OTF font is required for comic package acceptance")

    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--workdir", str(tmp_path), "--keep-output", "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["status"] == "passed"
    assert result["scene_count"] == 9
    assert result["instagram_slide_count"] == 9
    assert result["output_file_count"] == 22
    assert result["failure_smoke"]["render_job_status"] == "failed"
    assert result["failure_smoke"]["output_file_count"] == 0
    package_root = Path(result["package_root"])
    assert (package_root / "manifest.json").is_file()
    assert (package_root / "platforms" / "tiktok" / "final_video.mp4").is_file()
    assert (package_root / "platforms" / "youtube_shorts" / "final_video.mp4").is_file()
    assert (package_root / "platforms" / "vk_clips" / "final_video.mp4").is_file()


@pytest.mark.e2e
@pytest.mark.requires_ffmpeg
def test_comic_package_missing_font_failure_is_explicit(tmp_path: Path) -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("FFmpeg and ffprobe are required for comic package acceptance")
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--workdir", str(tmp_path), "--keep-output", "--failure-smoke", "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode != 0
    result = json.loads(completed.stdout)
    assert result["status"] == "failed_as_expected"
    assert result["failure"]["render_job_status"] == "failed"
    assert result["failure"]["output_file_count"] == 0
