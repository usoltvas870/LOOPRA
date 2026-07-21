from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class QAResult:
    """Result of a quality assurance check on production output."""

    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    video_playable: bool = False
    has_audio: bool = False
    duration_sec: float = 0.0
    resolution: str = ""
    bitrate_kbps: int = 0
    subtitle_count: int = 0
    fps: float = 0.0


def check_video_output(
    video_path: Path,
    *,
    expected_resolution: tuple[int, int] | None = None,
    expected_fps: int | None = None,
    expected_duration_sec: float | None = None,
    duration_tolerance_sec: float = 0.25,
    expected_video_codec: str | None = None,
    expected_pixel_format: str | None = None,
) -> QAResult:
    """Check a rendered video file for quality issues."""
    result = QAResult()

    if not video_path.exists():
        result.passed = False
        result.errors.append(f"Video file not found: {video_path}")
        return result

    if video_path.stat().st_size == 0:
        result.passed = False
        result.errors.append("Video file is empty (0 bytes)")
        return result

    try:
        probe = _ffprobe_json(video_path)
    except Exception as e:
        result.passed = False
        result.errors.append(f"ffprobe failed: {e}")
        return result

    streams = probe.get("streams", [])
    fmt = probe.get("format", {})

    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    subtitle_streams = [s for s in streams if s.get("codec_type") == "subtitle"]

    result.video_playable = len(video_streams) > 0
    result.has_audio = len(audio_streams) > 0
    result.subtitle_count = len(subtitle_streams)

    if not result.video_playable:
        result.passed = False
        result.errors.append("No video stream found — file may be corrupt")

    if not result.has_audio:
        result.warnings.append("No audio stream — video may be silent")

    if video_streams:
        vs = video_streams[0]
        w = vs.get("width", 0)
        h = vs.get("height", 0)
        result.resolution = f"{w}x{h}"
        frame_rate = vs.get("r_frame_rate", "0/1")
        try:
            numerator, denominator = frame_rate.split("/", maxsplit=1)
            result.fps = float(numerator) / float(denominator)
        except (ValueError, ZeroDivisionError):
            result.warnings.append(f"Unable to parse video FPS: {frame_rate}")
        if w < 360 or h < 640:
            result.warnings.append(f"Low resolution: {result.resolution}")
        if expected_resolution is not None and (w, h) != expected_resolution:
            result.passed = False
            result.errors.append(
                f"Unexpected resolution: {w}x{h} vs {expected_resolution[0]}x{expected_resolution[1]}"
            )
        if expected_fps is not None and abs(result.fps - expected_fps) > 0.01:
            result.passed = False
            result.errors.append(f"Unexpected FPS: {result.fps:g} vs {expected_fps}")
        if expected_video_codec is not None and vs.get("codec_name") != expected_video_codec:
            result.passed = False
            result.errors.append(
                f"Unexpected video codec: {vs.get('codec_name')} vs {expected_video_codec}"
            )
        if expected_pixel_format is not None and vs.get("pix_fmt") != expected_pixel_format:
            result.passed = False
            result.errors.append(
                f"Unexpected pixel format: {vs.get('pix_fmt')} vs {expected_pixel_format}"
            )

    result.duration_sec = float(fmt.get("duration", 0))
    if expected_duration_sec is not None and abs(result.duration_sec - expected_duration_sec) > duration_tolerance_sec:
        result.passed = False
        result.errors.append(
            f"Unexpected duration: {result.duration_sec:.3f}s vs {expected_duration_sec:.3f}s"
        )
    result.bitrate_kbps = int(int(fmt.get("bit_rate", 0)) / 1000)

    if result.duration_sec < 5:
        result.warnings.append(f"Very short duration: {result.duration_sec:.1f}s")

    if result.bitrate_kbps > 0 and result.bitrate_kbps < 500:
        result.warnings.append(f"Low bitrate: {result.bitrate_kbps} kbps")

    return result


def check_carousel_output(
    carousel_dir: Path,
    *,
    expected_count: int | None = None,
    expected_size: tuple[int, int] | None = None,
) -> QAResult:
    """Check a carousel output directory for quality issues."""
    result = QAResult()

    if not carousel_dir.exists():
        result.passed = False
        result.errors.append(f"Carousel output dir not found: {carousel_dir}")
        return result

    pngs = sorted(carousel_dir.glob("*.png"))
    if not pngs:
        result.passed = False
        result.errors.append("No PNG files in carousel output")
        return result

    result.subtitle_count = len(pngs)

    if expected_count is not None and len(pngs) != expected_count:
        result.passed = False
        result.errors.append(f"Expected {expected_count} PNG files, found {len(pngs)}")

    try:
        from PIL import Image
    except ImportError:
        result.warnings.append("Pillow not installed — skipping image validation")
        return result

    for p in pngs:
        if p.stat().st_size == 0:
            result.errors.append(f"Empty PNG: {p.name}")
            result.passed = False
            continue

        try:
            im = Image.open(p)
            w, h = im.size
            image_format = im.format
            im.close()
            if image_format != "PNG":
                result.errors.append(f"Unexpected image format: {p.name} ({image_format})")
                result.passed = False
            if expected_size is not None and (w, h) != expected_size:
                result.errors.append(
                    f"Unexpected size: {p.name} ({w}x{h} vs {expected_size[0]}x{expected_size[1]})"
                )
                result.passed = False
            if w < 500 or h < 500:
                result.warnings.append(f"Low resolution: {p.name} ({w}x{h})")
        except Exception:
            result.errors.append(f"Corrupt image: {p.name}")
            result.passed = False

    return result


def check_comic_output(
    comic_dir: Path,
    *,
    expected_count: int,
    expected_sizes: list[tuple[int, int]],
) -> QAResult:
    """Validate the exact ordered PNG frame set of a static comic episode."""
    result = QAResult()
    expected_names = [f"scene_{index:02d}.png" for index in range(1, expected_count + 1)]
    if not comic_dir.exists():
        result.passed = False
        result.errors.append(f"Comic output dir not found: {comic_dir}")
        return result

    frames = sorted(comic_dir.glob("scene_*.png"))
    if [path.name for path in frames] != expected_names:
        result.passed = False
        result.errors.append("Comic frame names or order do not match the expected scene set")
        return result

    result.subtitle_count = len(frames)
    try:
        from PIL import Image
    except ImportError:
        result.passed = False
        result.errors.append("Pillow is required for comic image validation")
        return result

    for path, expected_size in zip(frames, expected_sizes, strict=True):
        if path.stat().st_size == 0:
            result.passed = False
            result.errors.append(f"Empty PNG: {path.name}")
            continue
        try:
            with Image.open(path) as image:
                if image.format != "PNG":
                    result.passed = False
                    result.errors.append(f"Unexpected image format: {path.name} ({image.format})")
                if image.size != expected_size:
                    result.passed = False
                    result.errors.append(f"Unexpected size: {path.name} ({image.size} vs {expected_size})")
        except Exception:
            result.passed = False
            result.errors.append(f"Corrupt image: {path.name}")
    return result


def check_platform_video_package(
    platforms_dir: Path,
    *,
    expected_paths: dict[str, Path],
) -> QAResult:
    """Validate an exact set of platform MP4 outputs and their directories."""
    result = QAResult()
    platforms_dir = Path(platforms_dir).resolve()
    expected = {
        slug: Path(path).resolve()
        for slug, path in expected_paths.items()
    }
    expected_set = set(expected.values())

    actual = (
        {path.resolve() for path in platforms_dir.rglob("*.mp4")}
        if platforms_dir.is_dir()
        else set()
    )
    if actual != expected_set:
        result.passed = False
        result.errors.append(
            f"Platform MP4 set does not match request: expected {len(expected_set)}, found {len(actual)}"
        )

    expected_directories = set(expected)
    actual_directories = (
        {path.name for path in platforms_dir.iterdir() if path.is_dir()}
        if platforms_dir.is_dir()
        else set()
    )
    if actual_directories != expected_directories:
        result.passed = False
        result.errors.append("Platform output directories do not match the requested platforms")

    for slug, path in expected.items():
        expected_path = platforms_dir / slug / "final_video.mp4"
        if path != expected_path:
            result.passed = False
            result.errors.append(f"Unexpected platform output path for {slug}: {path}")
        if not path.is_file() or path.stat().st_size == 0:
            result.passed = False
            result.errors.append(f"Missing or empty platform MP4 for {slug}: {path}")

    temporary_mp4s = (
        [path for path in platforms_dir.rglob("*.mp4") if ".tmp" in path.name]
        if platforms_dir.is_dir()
        else []
    )
    if temporary_mp4s:
        result.passed = False
        result.errors.append("Temporary MP4 files remain in the platform package")
    return result


def format_qa_result(result: QAResult, label: str = "Video") -> str:
    """Format a QAResult as a human-readable string."""
    lines = [f"QA check for {label}:"]
    lines.append(f"  Status: {'PASSED' if result.passed else 'FAILED'}")
    lines.append(f"  Playable: {result.video_playable}")
    lines.append(f"  Audio: {result.has_audio}")
    lines.append(f"  Duration: {result.duration_sec:.1f}s")
    if result.resolution:
        lines.append(f"  Resolution: {result.resolution}")
    if result.bitrate_kbps:
        lines.append(f"  Bitrate: {result.bitrate_kbps} kbps")
    if result.subtitle_count:
        lines.append(f"  Subtitles/slides: {result.subtitle_count}")

    if result.errors:
        lines.append(f"  Errors ({len(result.errors)}):")
        for e in result.errors:
            lines.append(f"    - {e}")

    if result.warnings:
        lines.append(f"  Warnings ({len(result.warnings)}):")
        for w in result.warnings:
            lines.append(f"    - {w}")

    return "\n".join(lines)


def _ffprobe_json(path: Path) -> dict:
    proc = subprocess.run(
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
    proc.check_returncode()
    return json.loads(proc.stdout)
