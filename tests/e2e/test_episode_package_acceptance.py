from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "produce_episode.py"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "episode_package"


@pytest.mark.e2e
@pytest.mark.requires_ffmpeg
def test_episode_package_runs_through_real_comic_pipeline(tmp_path: Path) -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("FFmpeg and ffprobe are required")
    if not Path("C:/Windows/Fonts/arial.ttf").is_file():
        pytest.skip("A supported system font is required")
    package_root = tmp_path / "input" / "fixture_episode"
    shutil.copytree(FIXTURE_ROOT, package_root)
    sources = sorted((package_root / "assets").glob("*.png"))
    before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in sources]

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--episode", str(package_root / "episode.json"), "--json"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
        timeout=240,
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["status"] == "success"
    assert result["artifact_count"] == 22
    comic_root = Path(result["package_root"])
    assert len(list(comic_root.glob("scene_*.png"))) == 9
    assert len(list((comic_root / "platforms" / "instagram").glob("*.png"))) == 9
    for platform in ("tiktok", "youtube_shorts", "vk_clips"):
        assert (comic_root / "platforms" / platform / "final_video.mp4").is_file()
    assert (comic_root / "manifest.json").is_file()
    assert [hashlib.sha256(path.read_bytes()).hexdigest() for path in sources] == before
