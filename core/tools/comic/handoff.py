from __future__ import annotations

import hashlib
import json
import mimetypes
import shutil
import subprocess
import uuid
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from PIL import Image

from core.domain import ProductionBrief, PublishingPlatform, RenderJob, RenderJobStatus
from core.tools.qa import check_video_output


HANDOFF_PACKAGE_SCHEMA_VERSION = "1.0"
_VIDEO_TARGETS = (
    (PublishingPlatform.TIKTOK, "tiktok", "tiktok"),
    (PublishingPlatform.YOUTUBE_SHORTS, "youtube_shorts", "youtube_shorts"),
    (PublishingPlatform.VK, "vk_clips", "vk_clips"),
)


class ComicHandoffError(ValueError):
    """Raised when a user-facing comic handoff package is invalid."""


def build_comic_handoff_package(
    brief: ProductionBrief,
    render_job: RenderJob,
    comic_root: Path,
    handoff_output_root: Path,
    *,
    source_manifest_path: Path,
) -> Path:
    """Materialize a validated external package from an already rendered comic job."""
    if render_job.status != RenderJobStatus.RENDERED:
        raise ComicHandoffError("Handoff package requires a rendered RenderJob")
    if brief.production_brief_id != render_job.input_snapshot.get("brief_id"):
        raise ComicHandoffError("RenderJob does not belong to the supplied ProductionBrief")

    comic_root = Path(comic_root).resolve()
    source_manifest_path = Path(source_manifest_path).resolve()
    if not (comic_root / "manifest.json").is_file():
        raise ComicHandoffError("Internal comic manifest is missing")
    if not source_manifest_path.is_file():
        raise ComicHandoffError("Source episode manifest is missing")

    episode_id = brief.production_brief_id
    episode_root = Path(handoff_output_root).resolve() / episode_id
    final_root = episode_root / "final"
    stage_root = episode_root / f".final.building-{uuid.uuid4().hex}"
    stage_root.mkdir(parents=True, exist_ok=False)
    try:
        artifacts, warnings = _copy_deliverables(brief, comic_root, stage_root)
        payload = {
            "schema_version": HANDOFF_PACKAGE_SCHEMA_VERSION,
            "status": "ready",
            "episode_id": episode_id,
            "title": brief.title,
            "content_format": brief.content_format.value,
            "created_at": datetime.now(UTC).isoformat(),
            "source_episode_manifest": source_manifest_path.name,
            "source_episode_manifest_sha256": _sha256(source_manifest_path),
            "source_render_manifest_sha256": _sha256(comic_root / "manifest.json"),
            "render_job_id": render_job.render_job_id,
            "platforms": [platform.value for platform in brief.target_platforms],
            "artifacts": artifacts,
            "validation": {"status": "passed", "warnings": warnings},
            "manual_actions_required": [
                "Add platform-native music if desired.",
                "Write and paste a caption manually.",
                "Choose a cover if the destination platform requires one.",
                "Upload, schedule, and publish manually.",
            ],
            "captions": {"status": "manual_required"},
        }
        manifest_path = stage_root / "manifest.json"
        manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        verification = verify_comic_handoff_package(stage_root)
        if verification["status"] != "passed":
            raise ComicHandoffError("Handoff validation failed: " + "; ".join(verification["errors"]))
        _replace_final_directory(stage_root, final_root)
        return final_root
    except Exception:
        shutil.rmtree(stage_root, ignore_errors=True)
        raise


def verify_comic_handoff_package(package_root: Path) -> dict[str, Any]:
    """Verify a handoff package without rendering or changing it."""
    root = Path(package_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    manifest_path = root / "manifest.json"
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return _verification(root, "failed", [f"Manifest is not valid UTF-8 JSON: {exc}"], warnings)
    if not isinstance(payload, dict):
        return _verification(root, "failed", ["Manifest root must be an object"], warnings)
    if payload.get("schema_version") != HANDOFF_PACKAGE_SCHEMA_VERSION:
        errors.append("Unsupported handoff package schema version")
    if payload.get("status") != "ready":
        errors.append("Handoff manifest status must be ready")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("Handoff manifest must contain artifacts")
        return _verification(root, "failed", errors, warnings)

    relative_paths: list[str] = []
    platforms: set[str] = set()
    for item in artifacts:
        if not isinstance(item, dict):
            errors.append("Artifact entry must be an object")
            continue
        relative_path = item.get("path")
        if not isinstance(relative_path, str) or not _safe_relative_path(relative_path):
            errors.append(f"Unsafe artifact path: {relative_path}")
            continue
        relative_paths.append(relative_path)
        artifact_path = (root / PurePosixPath(relative_path)).resolve()
        try:
            artifact_path.relative_to(root)
        except ValueError:
            errors.append(f"Artifact escapes package root: {relative_path}")
            continue
        if not artifact_path.is_file() or artifact_path.stat().st_size == 0:
            errors.append(f"Missing or empty artifact: {relative_path}")
            continue
        if item.get("size_bytes") != artifact_path.stat().st_size:
            errors.append(f"Size mismatch: {relative_path}")
        if item.get("sha256") != _sha256(artifact_path):
            errors.append(f"Checksum mismatch: {relative_path}")
        if item.get("mime_type") != mimetypes.guess_type(artifact_path.name)[0]:
            errors.append(f"MIME mismatch: {relative_path}")
        platform = item.get("platform")
        if not isinstance(platform, str):
            errors.append(f"Artifact platform is invalid: {relative_path}")
        else:
            platforms.add(platform)
        _verify_media(artifact_path, item, errors, warnings)

    if len(relative_paths) != len(set(relative_paths)):
        errors.append("Manifest contains duplicate artifact paths")
    actual_paths = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    if set(relative_paths) != actual_paths:
        errors.append("Package files do not exactly match the manifest")
    requested = payload.get("platforms")
    if not isinstance(requested, list) or not all(isinstance(item, str) for item in requested):
        errors.append("Manifest platforms must be an array of strings")
    elif set(requested) != platforms:
        errors.append("Manifest platforms do not match artifact platforms")
    if "instagram" in platforms:
        _verify_instagram_sequence(relative_paths, errors)
    return _verification(root, "passed" if not errors else "failed", errors, warnings)


def _copy_deliverables(
    brief: ProductionBrief, comic_root: Path, stage_root: Path
) -> tuple[list[dict[str, Any]], list[str]]:
    artifacts: list[dict[str, Any]] = []
    warnings: list[str] = []
    targets = set(brief.target_platforms)
    if PublishingPlatform.INSTAGRAM in targets:
        slides = sorted((comic_root / "platforms" / "instagram").glob("*.png"))
        if len(slides) != len(brief.scenes):
            raise ComicHandoffError("Required Instagram carousel slides are missing")
        for index, source in enumerate(slides, start=1):
            relative = f"instagram_carousel/frame_{index:02d}.png"
            artifacts.append(_copy_image(source, stage_root / relative, relative, "instagram", index))
    for platform, slug, filename_slug in _VIDEO_TARGETS:
        if platform not in targets:
            continue
        source = comic_root / "platforms" / slug / "final_video.mp4"
        relative = f"{brief.production_brief_id}_{filename_slug}.mp4"
        artifacts.append(_copy_video(source, stage_root / relative, relative, platform.value, brief, warnings))
    if not artifacts:
        raise ComicHandoffError("No supported platform artifacts were requested")
    return artifacts, warnings


def _copy_image(source: Path, destination: Path, relative: str, platform: str, index: int) -> dict[str, Any]:
    _copy(source, destination)
    try:
        with Image.open(destination) as image:
            if image.format != "PNG":
                raise ComicHandoffError(f"Instagram artifact is not PNG: {source}")
            width, height = image.size
    except OSError as exc:
        raise ComicHandoffError(f"Instagram artifact is unreadable: {source}") from exc
    return _artifact(destination, relative, "instagram_carousel_slide", platform, index=index, width=width, height=height)


def _copy_video(
    source: Path, destination: Path, relative: str, platform: str, brief: ProductionBrief, warnings: list[str]
) -> dict[str, Any]:
    _copy(source, destination)
    qa = check_video_output(
        destination,
        expected_resolution=(brief.output.resolution_width, brief.output.resolution_height),
        expected_fps=brief.output.fps,
        expected_video_codec="h264",
        expected_pixel_format="yuv420p",
    )
    if not qa.passed:
        raise ComicHandoffError(f"Video validation failed for {source.name}: {'; '.join(qa.errors)}")
    warnings.extend(f"{platform}: {item}" for item in qa.warnings)
    media = _probe_video(destination)
    _decode_video(destination)
    audio_semantics = "source_audio" if brief.audio.voiceover_path or brief.audio.music_path else "silent_technical_track"
    return _artifact(
        destination,
        relative,
        "platform_video",
        platform,
        width=media["width"],
        height=media["height"],
        fps=media["fps"],
        duration_sec=media["duration_sec"],
        video_codec=media["video_codec"],
        pixel_format=media["pixel_format"],
        audio_present=media["audio_present"],
        audio_codec=media["audio_codec"],
        audio_semantics=audio_semantics if media["audio_present"] else "audio_absent_manual_music_required",
    )


def _artifact(path: Path, relative: str, role: str, platform: str, **metadata: Any) -> dict[str, Any]:
    return {
        "path": relative,
        "role": role,
        "platform": platform,
        "mime_type": mimetypes.guess_type(path.name)[0],
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
        **{key: value for key, value in metadata.items() if value is not None},
    }


def _copy(source: Path, destination: Path) -> None:
    if not source.is_file() or source.stat().st_size == 0:
        raise ComicHandoffError(f"Required render artifact is missing or empty: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if _sha256(source) != _sha256(destination):
        raise ComicHandoffError(f"Copied artifact checksum differs: {source.name}")


def _probe_video(path: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)],
            capture_output=True, text=True, timeout=30, check=True,
        )
        payload = json.loads(completed.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        raise ComicHandoffError(f"ffprobe failed for {path.name}: {exc}") from exc
    streams = payload.get("streams", [])
    video = next((item for item in streams if item.get("codec_type") == "video"), None)
    audio = next((item for item in streams if item.get("codec_type") == "audio"), None)
    if not isinstance(video, dict):
        raise ComicHandoffError(f"No video stream found: {path.name}")
    frame_rate = video.get("r_frame_rate", "0/1")
    numerator, denominator = frame_rate.split("/", maxsplit=1)
    return {
        "width": video.get("width"), "height": video.get("height"),
        "fps": float(numerator) / float(denominator),
        "duration_sec": float(payload.get("format", {}).get("duration", 0)),
        "video_codec": video.get("codec_name"), "pixel_format": video.get("pix_fmt"),
        "audio_present": isinstance(audio, dict),
        "audio_codec": audio.get("codec_name") if isinstance(audio, dict) else None,
    }


def _decode_video(path: Path) -> None:
    try:
        completed = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"],
            capture_output=True, text=True, timeout=120, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ComicHandoffError(f"ffmpeg decode failed for {path.name}: {exc}") from exc
    if completed.returncode != 0:
        raise ComicHandoffError(f"ffmpeg decode failed for {path.name}: {completed.stderr.strip()}")


def _verify_media(path: Path, item: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    if item.get("mime_type") == "image/png":
        try:
            with Image.open(path) as image:
                if image.format != "PNG" or [item.get("width"), item.get("height")] != list(image.size):
                    errors.append(f"Image metadata mismatch: {item.get('path')}")
        except OSError:
            errors.append(f"Corrupt PNG: {item.get('path')}")
        return
    if item.get("mime_type") != "video/mp4":
        errors.append(f"Unsupported handoff media type: {item.get('path')}")
        return
    qa = check_video_output(path, expected_video_codec=item.get("video_codec"), expected_pixel_format=item.get("pixel_format"))
    if not qa.passed:
        errors.extend(f"Video validation failed ({item.get('path')}): {error}" for error in qa.errors)
    warnings.extend(f"{item.get('path')}: {warning}" for warning in qa.warnings)
    try:
        media = _probe_video(path)
        for key in ("width", "height", "fps", "video_codec", "pixel_format", "audio_present", "audio_codec"):
            if item.get(key) != media.get(key):
                errors.append(f"Video metadata mismatch ({key}): {item.get('path')}")
        if abs(float(item.get("duration_sec", 0)) - float(media["duration_sec"])) > 0.25:
            errors.append(f"Video metadata mismatch (duration_sec): {item.get('path')}")
        _decode_video(path)
    except ComicHandoffError as exc:
        errors.append(str(exc))


def _verify_instagram_sequence(paths: list[str], errors: list[str]) -> None:
    slides = sorted(path for path in paths if path.startswith("instagram_carousel/"))
    expected = [f"instagram_carousel/frame_{index:02d}.png" for index in range(1, len(slides) + 1)]
    if slides != expected:
        errors.append("Instagram carousel filenames are not a contiguous stable sequence")


def _replace_final_directory(stage_root: Path, final_root: Path) -> None:
    final_root.parent.mkdir(parents=True, exist_ok=True)
    backup = final_root.with_name(f".final.previous-{uuid.uuid4().hex}")
    moved_old = False
    try:
        if final_root.exists():
            final_root.replace(backup)
            moved_old = True
        stage_root.replace(final_root)
        if moved_old:
            shutil.rmtree(backup)
    except Exception:
        if not final_root.exists() and moved_old and backup.exists():
            backup.replace(final_root)
        raise


def _safe_relative_path(value: str) -> bool:
    pure = PurePosixPath(value)
    return bool(value) and not pure.is_absolute() and ".." not in pure.parts and "\\" not in value and ":" not in value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verification(root: Path, status: str, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    return {"status": status, "package_root": str(root), "errors": errors, "warnings": warnings}
