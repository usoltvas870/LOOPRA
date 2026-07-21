from __future__ import annotations

import hashlib
import json
import mimetypes
import re
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Mapping

from PIL import Image

from core.domain import ContentFormat, ProductionBrief, PublishingPlatform, RenderJob


COMIC_PACKAGE_SCHEMA_VERSION = "1.0"
_PLATFORM_ORDER = (
    PublishingPlatform.INSTAGRAM,
    PublishingPlatform.TIKTOK,
    PublishingPlatform.YOUTUBE_SHORTS,
    PublishingPlatform.VK,
)


class ComicPackageError(ValueError):
    """Raised when a comic package manifest cannot be built safely."""


@dataclass(frozen=True, slots=True)
class ComicPackageArtifact:
    relative_path: str
    kind: str
    mime_type: str
    size_bytes: int
    sha256: str
    platform: str | None = None
    index: int | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    duration_sec: float | None = None

    def __post_init__(self) -> None:
        _validate_relative_path(self.relative_path)
        if self.size_bytes <= 0 or len(self.sha256) != 64:
            raise ComicPackageError("Comic package artifact size and sha256 must be valid")


@dataclass(frozen=True, slots=True)
class ComicPackageManifest:
    schema_version: str
    project_id: str
    production_brief_id: str
    render_job_id: str
    content_type: str
    scene_count: int
    requested_platforms: tuple[str, ...]
    generated_platforms: tuple[str, ...]
    status: str
    intermediates: tuple[ComicPackageArtifact, ...]
    deliverables: tuple[ComicPackageArtifact, ...]

    def __post_init__(self) -> None:
        if self.schema_version != COMIC_PACKAGE_SCHEMA_VERSION:
            raise ComicPackageError("Unsupported comic package schema version")
        paths = [artifact.relative_path for artifact in (*self.intermediates, *self.deliverables)]
        if len(paths) != len(set(paths)):
            raise ComicPackageError("Comic package artifact paths must be unique")
        if any(path == "manifest.json" for path in paths):
            raise ComicPackageError("Comic package manifest must not hash itself")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "project_id": self.project_id,
            "production_brief_id": self.production_brief_id,
            "render_job_id": self.render_job_id,
            "content_type": self.content_type,
            "scene_count": self.scene_count,
            "requested_platforms": list(self.requested_platforms),
            "generated_platforms": list(self.generated_platforms),
            "status": self.status,
            "artifacts": {
                "intermediates": [_without_none(asdict(item)) for item in self.intermediates],
                "deliverables": [_without_none(asdict(item)) for item in self.deliverables],
            },
        }


def canonical_comic_platforms(platforms: Iterable[PublishingPlatform]) -> tuple[PublishingPlatform, ...]:
    requested = set(platforms)
    return tuple(platform for platform in _PLATFORM_ORDER if platform in requested)


def build_comic_package_manifest(
    brief: ProductionBrief,
    render_job: RenderJob,
    comic_root: Path,
    *,
    comic_frames: Iterable[Path],
    instagram_slides: Iterable[Path] = (),
    master_artifacts: Iterable[tuple[str, Path]] = (),
    platform_videos: Mapping[PublishingPlatform, Path] | None = None,
    video_metadata: Mapping[Path, object] | None = None,
) -> ComicPackageManifest:
    if brief.content_format != ContentFormat.DIALOG_MINISERIES:
        raise ComicPackageError("Comic package requires dialog_miniseries content")
    comic_root = Path(comic_root).resolve()
    metadata = {Path(path).resolve(): value for path, value in (video_metadata or {}).items()}
    intermediates = tuple(
        _artifact(path, comic_root, kind="comic_frame", index=index)
        for index, path in enumerate(comic_frames, start=1)
    )
    deliverables: list[ComicPackageArtifact] = [
        _artifact(
            path,
            comic_root,
            kind="instagram_slide",
            platform=PublishingPlatform.INSTAGRAM.value,
            index=index,
        )
        for index, path in enumerate(instagram_slides, start=1)
    ]
    for kind, path in master_artifacts:
        deliverables.append(_artifact(path, comic_root, kind=kind, video_qa=metadata.get(Path(path).resolve())))
    platform_videos = platform_videos or {}
    for platform in _PLATFORM_ORDER[1:]:
        path = platform_videos.get(platform)
        if path is not None:
            deliverables.append(
                _artifact(
                    path,
                    comic_root,
                    kind="platform_video",
                    platform=platform.value,
                    video_qa=metadata.get(Path(path).resolve()),
                )
            )
    requested = canonical_comic_platforms(brief.target_platforms)
    generated = tuple(
        platform
        for platform in requested
        if any(artifact.platform == platform.value for artifact in deliverables)
    )
    return ComicPackageManifest(
        schema_version=COMIC_PACKAGE_SCHEMA_VERSION,
        project_id=brief.project_id,
        production_brief_id=brief.production_brief_id,
        render_job_id=render_job.render_job_id,
        content_type=brief.content_format.value,
        scene_count=len(brief.scenes),
        requested_platforms=tuple(platform.value for platform in requested),
        generated_platforms=tuple(platform.value for platform in generated),
        status="ready",
        intermediates=intermediates,
        deliverables=tuple(deliverables),
    )


def write_comic_package_manifest(manifest: ComicPackageManifest, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_text(
            json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
        return path
    except Exception:
        temporary.unlink(missing_ok=True)
        path.unlink(missing_ok=True)
        raise


def _artifact(
    path: Path,
    comic_root: Path,
    *,
    kind: str,
    platform: str | None = None,
    index: int | None = None,
    video_qa: object | None = None,
) -> ComicPackageArtifact:
    path = Path(path).resolve()
    try:
        relative_path = path.relative_to(comic_root).as_posix()
    except ValueError as exc:
        raise ComicPackageError(f"Comic artifact escapes package root: {path}") from exc
    if not path.is_file() or path.stat().st_size == 0:
        raise ComicPackageError(f"Comic artifact is missing or empty: {path}")
    mime_type = mimetypes.guess_type(path.name)[0]
    if mime_type not in {"image/png", "video/mp4", "audio/mpeg"}:
        raise ComicPackageError(f"Unsupported comic artifact MIME for {path.name}")
    width = height = None
    fps = duration = None
    if mime_type == "image/png":
        with Image.open(path) as image:
            if image.format != "PNG":
                raise ComicPackageError(f"Comic image artifact is not PNG: {path}")
            width, height = image.size
    elif video_qa is not None:
        resolution = getattr(video_qa, "resolution", "")
        if resolution and "x" in resolution:
            width, height = (int(value) for value in resolution.split("x", maxsplit=1))
        fps = float(getattr(video_qa, "fps", 0.0)) or None
        duration = float(getattr(video_qa, "duration_sec", 0.0)) or None
    return ComicPackageArtifact(
        relative_path=relative_path,
        kind=kind,
        platform=platform,
        index=index,
        mime_type=mime_type,
        size_bytes=path.stat().st_size,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        width=width,
        height=height,
        fps=fps,
        duration_sec=duration,
    )


def _validate_relative_path(value: str) -> None:
    pure = PurePosixPath(value)
    if (
        not value
        or pure.is_absolute()
        or re.match(r"^[A-Za-z]:/", value)
        or ".." in pure.parts
        or "\\" in value
    ):
        raise ComicPackageError(f"Unsafe comic package relative path: {value}")


def _without_none(value: dict[str, object]) -> dict[str, object]:
    return {key: item for key, item in value.items() if item is not None}
