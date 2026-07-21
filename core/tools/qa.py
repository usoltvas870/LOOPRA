from __future__ import annotations

import json
import hashlib
import mimetypes
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath


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


def check_comic_instagram_output(
    instagram_dir: Path,
    *,
    source_frames: list[Path],
    expected_size: tuple[int, int],
    filename_width: int = 2,
    render_job_root: Path,
) -> QAResult:
    """Validate an exact contain-adapted Instagram comic slide batch."""
    from PIL import Image

    from core.tools.comic.instagram import contain_geometry

    result = QAResult()
    instagram_dir = Path(instagram_dir).resolve()
    render_job_root = Path(render_job_root).resolve()
    expected_dir = (render_job_root / "comic" / "platforms" / "instagram").resolve()
    if instagram_dir != expected_dir:
        result.passed = False
        result.errors.append(f"Instagram directory must be {expected_dir}")
        return result
    if not instagram_dir.is_dir():
        result.passed = False
        result.errors.append(f"Instagram output dir not found: {instagram_dir}")
        return result

    expected_names = [f"{index:0{filename_width}d}.png" for index in range(1, len(source_frames) + 1)]
    owned = sorted(
        (path for path in instagram_dir.iterdir() if path.is_file() and re.fullmatch(r"\d+\.png", path.name)),
        key=lambda path: path.name,
    )
    if [path.name for path in owned] != expected_names:
        result.passed = False
        result.errors.append("Instagram slide names or order do not match the comic frame set")
        return result
    temporary = [path for path in instagram_dir.iterdir() if path.is_file() and ".tmp" in path.name]
    if temporary:
        result.passed = False
        result.errors.append("Temporary files remain in the Instagram output directory")

    for source_path, output_path in zip(source_frames, owned, strict=True):
        try:
            output_path.resolve().relative_to(instagram_dir)
            with Image.open(source_path) as source, Image.open(output_path) as output:
                if source.format != "PNG" or output.format != "PNG":
                    result.passed = False
                    result.errors.append(f"Instagram input/output is not PNG: {output_path.name}")
                    continue
                if output.size != expected_size:
                    result.passed = False
                    result.errors.append(f"Unexpected Instagram size: {output_path.name} ({output.size})")
                contained_width, contained_height, offset_x, offset_y = contain_geometry(
                    source.size, expected_size
                )
                scale_x = contained_width / source.width
                scale_y = contained_height / source.height
                if abs(scale_x - scale_y) > max(1 / source.width, 1 / source.height):
                    result.passed = False
                    result.errors.append(f"Instagram contain scale is not uniform: {output_path.name}")
                if offset_x < 0 or offset_y < 0 or contained_width > expected_size[0] or contained_height > expected_size[1]:
                    result.passed = False
                    result.errors.append(f"Instagram contain geometry crops the source: {output_path.name}")
        except Exception as exc:
            result.passed = False
            result.errors.append(f"Corrupt Instagram PNG {output_path.name}: {exc}")
    result.subtitle_count = len(owned)
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
        {path.name for path in platforms_dir.iterdir() if path.is_dir() and list(path.rglob("*.mp4"))}
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


def check_comic_package_manifest(
    manifest_path: Path,
    *,
    comic_root: Path,
    project_id: str,
    production_brief_id: str,
    render_job_id: str,
    requested_platforms: list[str],
    scene_count: int | None = None,
    video_metadata: dict[Path, QAResult] | None = None,
) -> QAResult:
    """Validate comic manifest identity, safety, hashes, metadata, and disk completeness."""
    from PIL import Image

    from core.tools.comic.package import COMIC_PACKAGE_SCHEMA_VERSION

    result = QAResult()
    manifest_path = Path(manifest_path).resolve()
    comic_root = Path(comic_root).resolve()
    expected_manifest_path = comic_root / "manifest.json"
    if manifest_path != expected_manifest_path or not manifest_path.is_file():
        result.passed = False
        result.errors.append(f"Comic manifest not found at {expected_manifest_path}")
        return result
    if manifest_path.stat().st_size == 0:
        result.passed = False
        result.errors.append("Comic manifest is empty")
        return result
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result.passed = False
        result.errors.append(f"Comic manifest is not valid UTF-8 JSON: {exc}")
        return result
    if not isinstance(payload, dict):
        result.passed = False
        result.errors.append("Comic manifest root must be an object")
        return result

    expected_values = {
        "schema_version": COMIC_PACKAGE_SCHEMA_VERSION,
        "project_id": project_id,
        "production_brief_id": production_brief_id,
        "render_job_id": render_job_id,
        "content_type": "dialog_miniseries",
        "status": "ready",
    }
    for key, expected in expected_values.items():
        if payload.get(key) != expected:
            result.passed = False
            result.errors.append(f"Comic manifest {key} does not match the current package")
    if scene_count is not None and payload.get("scene_count") != scene_count:
        result.passed = False
        result.errors.append("Comic manifest scene_count does not match the current package")

    if payload.get("requested_platforms") != requested_platforms:
        result.passed = False
        result.errors.append("Comic manifest requested platforms do not match the brief")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict):
        result.passed = False
        result.errors.append("Comic manifest artifacts must be an object")
        return result
    intermediate_items = artifacts.get("intermediates")
    deliverable_items = artifacts.get("deliverables")
    if not isinstance(intermediate_items, list) or not isinstance(deliverable_items, list):
        result.passed = False
        result.errors.append("Comic manifest artifact groups must be arrays")
        return result
    all_items = [*intermediate_items, *deliverable_items]
    paths: list[str] = []
    generated_platforms: list[str] = []
    video_metadata = {Path(path).resolve(): qa for path, qa in (video_metadata or {}).items()}
    for item in all_items:
        if not isinstance(item, dict):
            result.passed = False
            result.errors.append("Comic manifest artifact entry must be an object")
            continue
        relative_path = item.get("relative_path")
        if not isinstance(relative_path, str) or not _safe_relative_path(relative_path):
            result.passed = False
            result.errors.append(f"Unsafe comic manifest artifact path: {relative_path}")
            continue
        paths.append(relative_path)
        if relative_path == "manifest.json":
            result.passed = False
            result.errors.append("Comic manifest must not include itself")
        artifact_path = (comic_root / PurePosixPath(relative_path)).resolve()
        try:
            artifact_path.relative_to(comic_root)
        except ValueError:
            result.passed = False
            result.errors.append(f"Comic manifest artifact escapes the current RenderJob: {relative_path}")
            continue
        if not artifact_path.is_file():
            result.passed = False
            result.errors.append(f"Comic manifest artifact is missing: {relative_path}")
            continue
        expected_mime = mimetypes.guess_type(artifact_path.name)[0]
        if item.get("mime_type") != expected_mime:
            result.passed = False
            result.errors.append(f"Comic manifest MIME mismatch: {relative_path}")
        if item.get("size_bytes") != artifact_path.stat().st_size:
            result.passed = False
            result.errors.append(f"Comic manifest size mismatch: {relative_path}")
        if item.get("sha256") != hashlib.sha256(artifact_path.read_bytes()).hexdigest():
            result.passed = False
            result.errors.append(f"Comic manifest sha256 mismatch: {relative_path}")
        if expected_mime == "image/png":
            try:
                with Image.open(artifact_path) as image:
                    if image.format != "PNG" or [item.get("width"), item.get("height")] != list(image.size):
                        result.passed = False
                        result.errors.append(f"Comic manifest image metadata mismatch: {relative_path}")
            except OSError:
                result.passed = False
                result.errors.append(f"Corrupt comic manifest PNG: {relative_path}")
        if expected_mime == "video/mp4" and artifact_path in video_metadata:
            qa = video_metadata[artifact_path]
            expected_video = {
                "fps": qa.fps or None,
                "duration_sec": qa.duration_sec or None,
            }
            if qa.resolution and "x" in qa.resolution:
                width, height = qa.resolution.split("x", maxsplit=1)
                expected_video.update({"width": int(width), "height": int(height)})
            for key, expected in expected_video.items():
                if item.get(key) != expected:
                    result.passed = False
                    result.errors.append(f"Comic manifest video metadata mismatch: {relative_path} ({key})")
        platform = item.get("platform")
        if isinstance(platform, str) and platform not in generated_platforms:
            generated_platforms.append(platform)

    if len(paths) != len(set(paths)):
        result.passed = False
        result.errors.append("Comic manifest contains duplicate artifact paths")
    if payload.get("generated_platforms") != generated_platforms:
        result.passed = False
        result.errors.append("Comic manifest generated platforms do not match its artifacts")
    if any(platform not in requested_platforms for platform in generated_platforms):
        result.passed = False
        result.errors.append("Comic manifest contains an unrequested platform")
    if generated_platforms != requested_platforms:
        result.passed = False
        result.errors.append("Comic manifest is missing a requested platform")

    actual = _comic_package_artifact_paths(comic_root)
    if set(paths) != actual:
        result.passed = False
        result.errors.append("Comic manifest artifact set does not match package files")
    return result


def _safe_relative_path(value: str) -> bool:
    pure = PurePosixPath(value)
    return (
        bool(value)
        and not pure.is_absolute()
        and re.match(r"^[A-Za-z]:/", value) is None
        and ".." not in pure.parts
        and "\\" not in value
    )


def _comic_package_artifact_paths(comic_root: Path) -> set[str]:
    paths = {path.relative_to(comic_root).as_posix() for path in comic_root.glob("scene_*.png") if path.is_file()}
    instagram_dir = comic_root / "platforms" / "instagram"
    if instagram_dir.is_dir():
        paths.update(
            path.relative_to(comic_root).as_posix()
            for path in instagram_dir.iterdir()
            if path.is_file() and re.fullmatch(r"\d+\.png", path.name)
        )
    for relative in (
        "video/final_video.mp4",
        "video/cover.png",
        "video/audio_only.mp3",
        "platforms/tiktok/final_video.mp4",
        "platforms/youtube_shorts/final_video.mp4",
        "platforms/vk_clips/final_video.mp4",
    ):
        path = comic_root / relative
        if path.is_file():
            paths.add(relative)
    return paths


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
