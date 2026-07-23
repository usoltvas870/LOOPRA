from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "inspect_video_format.py"


def _video(path: Path, filtergraph: str, audio: bool = False) -> None:
    command = ["ffmpeg", "-y", "-f", "lavfi", "-i", filtergraph]
    if audio:
        command += ["-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100", "-shortest"]
    command += ["-t", "2", "-pix_fmt", "yuv420p", str(path)]
    subprocess.run(command, capture_output=True, check=True)


def _inspect(tmp_path: Path, source: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CLI), "--input", str(source), "--video-id", "fixture", "--output-dir", str(tmp_path / "evidence")], capture_output=True, text=True, encoding="utf-8")


def test_static_video_creates_evidence_and_preserves_source(tmp_path: Path) -> None:
    source = tmp_path / "статичный ролик.mp4"; _video(source, "color=c=blue:s=360x640:r=24")
    before = source.read_bytes(); result = _inspect(tmp_path, source)
    assert result.returncode == 0 and result.stdout.splitlines() == ["INSPECTION_RESULT=success"] and source.read_bytes() == before
    payload = json.loads((tmp_path / "evidence" / "inspection.json").read_text(encoding="utf-8"))
    assert payload["media_facts"]["width"] == 360 and not payload["media_facts"]["audio_present"]
    assert payload["visual_structure"]["mostly_static"]
    assert (tmp_path / "evidence" / "full_video_contact_sheet.png").is_file()
    assert (tmp_path / "evidence" / "manual_review.json").is_file()


def test_two_states_and_audio_are_measured(tmp_path: Path) -> None:
    source = tmp_path / "two_states.mp4"
    _video(source, "color=c=red:s=360x640:r=24:d=1[red];color=c=green:s=360x640:r=24:d=1[green];[red][green]concat=n=2:v=1:a=0", audio=True)
    result = _inspect(tmp_path, source); assert result.returncode == 0
    payload = json.loads((tmp_path / "evidence" / "inspection.json").read_text(encoding="utf-8"))
    assert payload["media_facts"]["audio_present"] and payload["visual_structure"]["scene_count_estimate"] >= 2
    assert payload["visual_structure"]["uses_one_or_two_visual_states"]


def test_invalid_input_has_exactly_one_result(tmp_path: Path) -> None:
    source = tmp_path / "broken.mp4"; source.write_bytes(b"not media")
    result = _inspect(tmp_path, source)
    assert result.returncode == 2
    assert len([line for line in result.stdout.splitlines() if line.startswith("INSPECTION_RESULT=")]) == 1


def test_continuous_motion_is_not_mostly_static(tmp_path: Path) -> None:
    source = tmp_path / "continuous_motion.mp4"
    _video(source, "testsrc2=s=360x640:r=24")
    result = _inspect(tmp_path, source)
    assert result.returncode == 0
    payload = json.loads((tmp_path / "evidence" / "inspection.json").read_text(encoding="utf-8"))
    assert payload["visual_structure"]["mostly_static"] is False
    assert payload["visual_structure"]["first_visual_change_seconds"] is not None


def test_local_acceptance_generates_comparison(tmp_path: Path) -> None:
    runner = ROOT / "run_format_inspection_acceptance.py"
    result = subprocess.run([sys.executable, str(runner), "--workdir", str(tmp_path / "acceptance"), "--json"], capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0
    assert json.loads(result.stdout)["result"] == "success"
    assert (tmp_path / "acceptance" / "evidence" / "comparison.md").is_file()
