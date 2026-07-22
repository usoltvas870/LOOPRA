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
    handoff_root = Path(result["handoff_package_root"])
    assert handoff_root == tmp_path / "output" / "fixture_episode" / "final"
    assert (handoff_root / "manifest.json").is_file()
    comic_root = Path(result["package_root"])
    assert len(list(comic_root.glob("scene_*.png"))) == 9
    assert len(list((comic_root / "platforms" / "instagram").glob("*.png"))) == 9
    for platform in ("tiktok", "youtube_shorts", "vk_clips"):
        assert (comic_root / "platforms" / platform / "final_video.mp4").is_file()
    assert (comic_root / "manifest.json").is_file()
    verified = subprocess.run(
        [sys.executable, str(SCRIPT), "--verify-package", str(handoff_root), "--json"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
        timeout=240,
    )
    assert verified.returncode == 0, verified.stderr
    assert json.loads(verified.stdout)["package_validation_status"] == "passed"
    handoff_payload = json.loads((handoff_root / "manifest.json").read_text(encoding="utf-8"))
    assert [item["path"] for item in handoff_payload["artifacts"]] == [
        *(f"instagram_carousel/frame_{index:02d}.png" for index in range(1, 10)),
        "fixture_episode_tiktok.mp4",
        "fixture_episode_youtube_shorts.mp4",
        "fixture_episode_vk_clips.mp4",
    ]
    assert [hashlib.sha256(path.read_bytes()).hexdigest() for path in sources] == before
