from __future__ import annotations

import subprocess
from pathlib import Path

from .renderer import _find_ffmpeg


def mix_audio_with_ducking(
    voiceover_path: Path,
    music_path: Path,
    output_path: Path,
    ducking_db: int = 12,
    music_volume: float = 0.15,
) -> Path:
    if not voiceover_path.exists():
        raise FileNotFoundError(f"Voiceover file not found: {voiceover_path}")
    if not music_path.exists():
        raise FileNotFoundError(f"Music file not found: {music_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = _find_ffmpeg()

    threshold = 0.005
    ratio = max(2, min(10, ducking_db // 3))
    attack = 10
    release = 200
    makeup = -ducking_db

    filter_graph = (
        f"[0:a]asplit[voice_mix][sidechain];"
        f"[1:a]aloop=loop=-1:size=2e+09,volume={music_volume}[music_adj];"
        f"[music_adj][sidechain]sidechaincompress="
        f"threshold={threshold}:ratio={ratio}:"
        f"attack={attack}:release={release}:"
        f"makeup={makeup}:level_sc=1.0[ducked];"
        f"[voice_mix][ducked]amix=inputs=2:duration=first[out]"
    )

    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(voiceover_path),
        "-i", str(music_path),
        "-filter_complex", filter_graph,
        "-map", "[out]",
        str(output_path),
    ]

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"Audio mixing failed (code {proc.returncode}): {proc.stderr[-2000:]}"
        )

    return output_path


def normalize_audio(
    input_path: Path,
    output_path: Path,
    target_db: float = -16,
) -> Path:
    if not input_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = _find_ffmpeg()

    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(input_path),
        "-af", (
            f"loudnorm=I={target_db}:TP=-1.5:LRA=11:"
            f"measured_I={target_db}:measured_TP=-1.5:measured_LRA=11:"
            f"measured_thresh=-40:offset=0:linear=true:print_format=summary"
        ),
        str(output_path),
    ]

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"Audio normalization failed (code {proc.returncode}): {proc.stderr[-2000:]}"
        )

    return output_path
