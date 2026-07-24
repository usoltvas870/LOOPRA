from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "inspect_video_format.py"
sys.path.insert(0, str(ROOT / "src"))
import format_inspection


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


@pytest.mark.parametrize("duration", [6.266667, 461.466667, 639.733333])
def test_sampling_plan_stays_strictly_inside_terminal_boundary(duration: float) -> None:
    plan = format_inspection._plan_sample_times(duration)
    assert plan == format_inspection._plan_sample_times(duration)
    assert plan == sorted(plan)
    assert len(plan) == len(set(plan))
    assert all(0 <= value < duration for value in plan)
    assert plan[-1] <= duration - format_inspection.TERMINAL_MARGIN_SECONDS


def test_sampling_plan_reduces_very_short_video_and_rejects_invalid_duration() -> None:
    assert format_inspection._plan_sample_times(0.02) == [0.0, 0.01]
    with pytest.raises(ValueError, match="duration"):
        format_inspection._plan_sample_times(float("nan"))


def test_terminal_failure_retries_earlier_timestamp_and_preserves_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "source.mp4"; source.write_bytes(b"fixture")
    frames = tmp_path / "frames"; frames.mkdir()
    calls: list[float] = []

    def fake_frame(_source: Path, timestamp: float, target: Path, **_kwargs) -> None:
        calls.append(timestamp)
        if len(calls) == 2:
            raise ValueError("FRAME_EXTRACTION_FAILED")
        Image.new("RGB", (8, 8), "blue").save(target)

    monkeypatch.setattr(format_inspection, "_frame", fake_frame)
    paths, times, results, warnings = format_inspection._extract_frames(source, frames, [0.0, 6.216], 6.266667, format_inspection.time.monotonic())
    assert len(paths) == 2 and times[-1] < 6.216
    assert results[-1]["status"] == "success" and results[-1]["retry_count"] == 1
    assert "TERMINAL_FRAME_RETRIED" in warnings


def test_metrics_report_unavailable_when_fewer_than_two_frames(tmp_path: Path) -> None:
    frame = tmp_path / "one.png"; Image.new("RGB", (8, 8), "blue").save(frame)
    metrics, warnings = format_inspection._metrics([frame], [0.0], 1.0)
    assert metrics["scene_count_estimate"] is None
    assert warnings == ["INSUFFICIENT_FRAMES_FOR_VISUAL_METRICS"]
