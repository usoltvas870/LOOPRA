from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from core.domain import ProductionBrief

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

SUPPORTED_FONT_EXTENSIONS = {".ttf", ".otf"}


@dataclass
class AssetReport:
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)
    corrupt_files: list[str] = field(default_factory=list)
    wrong_resolution: list[str] = field(default_factory=list)


def validate_image(path: Path) -> dict:
    if not path.exists():
        return {"corrupt": True, "error": f"File not found: {path}"}

    try:
        file_size = path.stat().st_size
    except OSError as exc:
        return {"corrupt": True, "error": f"Cannot stat file: {path} — {exc}"}

    if file_size == 0:
        return {"corrupt": True, "error": f"File is empty: {path}"}

    if not HAS_PILLOW:
        return {
            "width": 0,
            "height": 0,
            "format": path.suffix.lstrip(".").lower() or "unknown",
            "file_size": file_size,
            "corrupt": False,
        }

    try:
        with Image.open(path) as im:
            width, height = im.size
            fmt = (im.format or path.suffix.lstrip(".")).lower()
        return {
            "width": width,
            "height": height,
            "format": fmt,
            "file_size": file_size,
            "corrupt": False,
        }
    except Exception as exc:
        return {"corrupt": True, "error": f"Cannot open image: {path} — {exc}"}


def validate_audio(path: Path) -> dict:
    if not path.exists():
        return {"corrupt": True, "error": f"File not found: {path}"}

    try:
        file_size = path.stat().st_size
    except OSError as exc:
        return {"corrupt": True, "error": f"Cannot stat file: {path} — {exc}"}

    if file_size == 0:
        return {"corrupt": True, "error": f"File is empty: {path}"}

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {
            "duration": 0.0,
            "bitrate_bps": 0,
            "channels": 0,
            "corrupt": False,
        }

    if result.returncode != 0:
        return {"corrupt": True, "error": f"ffprobe failed for: {path} — {result.stderr.strip()}"}

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return {"corrupt": True, "error": f"ffprobe output parse error for: {path} — {exc}"}

    duration = 0.0
    bitrate_bps = 0
    channels = 0

    fmt = data.get("format", {})
    if fmt:
        duration = float(fmt.get("duration", 0))
        bitrate_bps = int(fmt.get("bit_rate", 0))

    streams = data.get("streams", [])
    for stream in streams:
        if stream.get("codec_type") == "audio":
            channels = max(channels, stream.get("channels", 0))

    return {
        "duration": duration,
        "bitrate_bps": bitrate_bps,
        "channels": channels,
        "corrupt": False,
    }


def validate_font(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "format": "unknown", "corrupt": True}

    try:
        file_size = path.stat().st_size
    except OSError:
        return {"exists": True, "format": "unknown", "corrupt": True}

    if file_size == 0:
        return {"exists": True, "format": "unknown", "corrupt": True}

    suffix = path.suffix.lower()
    if suffix in SUPPORTED_FONT_EXTENSIONS:
        return {"exists": True, "format": suffix.lstrip("."), "corrupt": False}

    return {"exists": True, "format": "unknown", "corrupt": True}


def _resolve_asset_path(raw: str, project_root: Path) -> Path | None:
    if not raw:
        return None
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    return candidate


def validate_production_assets(
    brief: ProductionBrief, project_root: Path
) -> AssetReport:
    report = AssetReport()
    target_w = brief.output.resolution_width
    target_h = brief.output.resolution_height

    for i, scene in enumerate(brief.scenes):
        image_path = _resolve_asset_path(scene.image_source, project_root)
        if image_path is None:
            report.missing_files.append(f"Scene {i}: empty image_source")
            report.passed = False
            continue

        result = validate_image(image_path)

        if result.get("corrupt"):
            if "not found" in str(result.get("error", "")):
                report.missing_files.append(
                    f"Scene {i} image: {scene.image_source}"
                )
            else:
                report.corrupt_files.append(
                    f"Scene {i} image: {scene.image_source}"
                )
            report.passed = False
            continue

        if (
            HAS_PILLOW
            and target_w > 0
            and target_h > 0
            and result.get("width", 0) > 0
            and result.get("height", 0) > 0
            and (
                result["width"] != target_w
                or result["height"] != target_h
            )
        ):
            report.wrong_resolution.append(
                f"Scene {i} image: {scene.image_source} "
                f"({result['width']}x{result['height']} "
                f"vs target {target_w}x{target_h})"
            )

    voiceover_path = _resolve_asset_path(brief.audio.voiceover_path, project_root)
    if voiceover_path is not None:
        result = validate_audio(voiceover_path)
        if result.get("corrupt"):
            if "not found" in str(result.get("error", "")):
                report.missing_files.append(
                    f"Voiceover: {brief.audio.voiceover_path}"
                )
            else:
                report.corrupt_files.append(
                    f"Voiceover: {brief.audio.voiceover_path}"
                )
            report.passed = False

    music_path = _resolve_asset_path(brief.audio.music_path, project_root)
    if music_path is not None:
        result = validate_audio(music_path)
        if result.get("corrupt"):
            if "not found" in str(result.get("error", "")):
                report.missing_files.append(
                    f"Music: {brief.audio.music_path}"
                )
            else:
                report.corrupt_files.append(
                    f"Music: {brief.audio.music_path}"
                )
            report.passed = False

    font_path = _resolve_asset_path(brief.subtitles.font_path, project_root)
    if font_path is not None:
        result = validate_font(font_path)
        if result.get("corrupt"):
            if not result.get("exists"):
                report.missing_files.append(
                    f"Subtitles font: {brief.subtitles.font_path}"
                )
            else:
                report.corrupt_files.append(
                    f"Subtitles font: {brief.subtitles.font_path}"
                )
            report.passed = False

    return report
