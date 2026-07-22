from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from core.domain import (
    ComicOverlay,
    ComicTailAnchor,
    ContentFormat,
    ProductionBrief,
    ProductionBriefStatus,
    ProductionOutput,
    ProductionScene,
    ProductionSubtitles,
    PublishingPlatform,
)
from core.projects.loader import validate_project_id
from core.tools.comic import (
    calculate_comic_scene_timing,
    resolve_comic_platform_video_presets,
    validate_comic_frame_layout,
)
from core.tools.comic.platform_presets import SUPPORTED_COMIC_TRANSITIONS
from core.tools.validators import validate_font, validate_image, validate_production_assets


EPISODE_SCHEMA_VERSION = 1
SUPPORTED_IMAGE_EXTENSIONS = frozenset({".jpeg", ".jpg", ".png"})
SUPPORTED_EPISODE_PLATFORMS = frozenset(
    {
        PublishingPlatform.INSTAGRAM,
        PublishingPlatform.TIKTOK,
        PublishingPlatform.YOUTUBE_SHORTS,
        PublishingPlatform.VK,
    }
)
_IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "episode_id",
        "title",
        "workspace_id",
        "project_id",
        "content_format",
        "target_platforms",
        "defaults",
        "font",
        "output",
        "frames",
    }
)
_DEFAULT_FIELDS = frozenset(
    {"duration_sec", "transition_type", "transition_duration_sec"}
)
_FONT_FIELDS = frozenset({"path"})
_OUTPUT_FIELDS = frozenset(
    {"resolution_width", "resolution_height", "fps", "generate_comic_master_video"}
)
_FRAME_FIELDS = frozenset(
    {
        "frame_id",
        "image",
        "speaker",
        "text",
        "position",
        "tail_anchor",
        "duration_sec",
        "transition_type",
        "transition_duration_sec",
    }
)
_ANCHOR_FIELDS = frozenset({"x", "y"})


@dataclass(frozen=True, slots=True)
class EpisodeValidationIssue:
    path: str
    message: str
    value: Any = None
    allowed: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EpisodePackageValidationError(ValueError):
    def __init__(self, manifest_path: Path, issues: list[EpisodeValidationIssue]) -> None:
        self.manifest_path = Path(manifest_path)
        self.issues = issues
        super().__init__(f"Episode package validation failed with {len(issues)} error(s)")


@dataclass(frozen=True, slots=True)
class LoadedEpisodePackage:
    manifest_path: Path
    package_root: Path
    brief: ProductionBrief
    source_paths: tuple[Path, ...]
    font_path: Path

    def source_hashes(self) -> dict[str, str]:
        return {
            path.relative_to(self.package_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in self.source_paths
        }


def _issue(
    issues: list[EpisodeValidationIssue],
    path: str,
    message: str,
    value: Any = None,
    allowed: list[str] | None = None,
) -> None:
    if isinstance(value, str) and len(value) > 200:
        value = value[:197] + "..."
    issues.append(EpisodeValidationIssue(path=path, message=message, value=value, allowed=allowed))


def _reject_unknown_fields(
    value: Any,
    *,
    path: str,
    allowed_fields: frozenset[str],
    issues: list[EpisodeValidationIssue],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        _issue(issues, path, "must be a JSON object", value)
        return {}
    for field in sorted(set(value) - allowed_fields):
        _issue(issues, f"{path}.{field}", "unknown field")
    return value


def _resolve_package_file(
    raw_path: Any,
    *,
    package_root: Path,
    path: str,
    issues: list[EpisodeValidationIssue],
    extensions: frozenset[str] | None = None,
) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path.strip():
        _issue(issues, path, "must be a non-empty relative path", raw_path)
        return None
    candidate = Path(raw_path)
    if candidate.is_absolute():
        _issue(issues, path, "must be relative to the episode package root", raw_path)
        return None
    resolved = (package_root / candidate).resolve()
    try:
        resolved.relative_to(package_root)
    except ValueError:
        _issue(issues, path, "path escapes the episode package root", raw_path)
        return None
    if extensions is not None and resolved.suffix.lower() not in extensions:
        _issue(issues, path, "unsupported file format", raw_path, sorted(extensions))
    if not resolved.exists():
        _issue(issues, path, "file does not exist", raw_path)
        return None
    if not resolved.is_file():
        _issue(issues, path, "path must identify a file", raw_path)
        return None
    return resolved


def _find_system_font() -> Path | None:
    candidates = [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "arial.ttf",
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "calibri.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]
    return next((path.resolve() for path in candidates if path.is_file()), None)


def _parse_font(
    raw: Any,
    *,
    package_root: Path,
    issues: list[EpisodeValidationIssue],
) -> Path | None:
    data = _reject_unknown_fields(
        raw or {}, path="$.font", allowed_fields=_FONT_FIELDS, issues=issues
    )
    raw_path = data.get("path", "system:default")
    if raw_path == "system:default":
        font_path = _find_system_font()
        if font_path is None:
            _issue(
                issues,
                "$.font.path",
                "no supported system font was found; provide a package-relative TTF/OTF",
                raw_path,
            )
            return None
    else:
        font_path = _resolve_package_file(
            raw_path,
            package_root=package_root,
            path="$.font.path",
            issues=issues,
            extensions=frozenset({".otf", ".ttf"}),
        )
        if font_path is None:
            return None
    result = validate_font(font_path)
    if result.get("corrupt"):
        _issue(issues, "$.font.path", "font is missing, empty, or unsupported", raw_path)
        return None
    return font_path


def load_episode_package(manifest_path: Path) -> LoadedEpisodePackage:
    manifest_path = Path(manifest_path).expanduser().resolve()
    if not manifest_path.exists():
        raise EpisodePackageValidationError(
            manifest_path,
            [EpisodeValidationIssue(path="$", message="manifest file does not exist", value=str(manifest_path))],
        )
    if not manifest_path.is_file():
        raise EpisodePackageValidationError(
            manifest_path,
            [EpisodeValidationIssue(path="$", message="manifest path must identify a file", value=str(manifest_path))],
        )
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EpisodePackageValidationError(
            manifest_path,
            [EpisodeValidationIssue(path="$", message=f"invalid JSON: {exc}")],
        ) from exc

    issues: list[EpisodeValidationIssue] = []
    data = _reject_unknown_fields(
        raw, path="$", allowed_fields=_TOP_LEVEL_FIELDS, issues=issues
    )
    package_root = manifest_path.parent.resolve()

    schema_version = data.get("schema_version")
    if schema_version != EPISODE_SCHEMA_VERSION:
        _issue(
            issues,
            "$.schema_version",
            f"unsupported schema version; expected {EPISODE_SCHEMA_VERSION}",
            schema_version,
            [str(EPISODE_SCHEMA_VERSION)],
        )

    episode_id = data.get("episode_id")
    if not isinstance(episode_id, str) or not _IDENTIFIER_PATTERN.fullmatch(episode_id):
        _issue(
            issues,
            "$.episode_id",
            "must match ^[a-z0-9][a-z0-9_-]*$",
            episode_id,
        )
        episode_id = "invalid_episode"
    project_id = data.get("project_id", episode_id)
    try:
        project_id = validate_project_id(project_id)
    except (TypeError, ValueError) as exc:
        _issue(issues, "$.project_id", str(exc), project_id)
        project_id = "invalid_project"
    workspace_id = data.get("workspace_id", "internal")
    if not isinstance(workspace_id, str) or not workspace_id.strip():
        _issue(issues, "$.workspace_id", "must be a non-empty string", workspace_id)
        workspace_id = "internal"
    title = data.get("title", "")
    if not isinstance(title, str):
        _issue(issues, "$.title", "must be a string", title)
        title = ""

    content_format = data.get("content_format")
    if content_format != ContentFormat.DIALOG_MINISERIES.value:
        _issue(
            issues,
            "$.content_format",
            "unsupported content format for Episode Input Package v1",
            content_format,
            [ContentFormat.DIALOG_MINISERIES.value],
        )

    platform_values = data.get(
        "target_platforms",
        [
            PublishingPlatform.INSTAGRAM.value,
            PublishingPlatform.TIKTOK.value,
            PublishingPlatform.YOUTUBE_SHORTS.value,
            PublishingPlatform.VK.value,
        ],
    )
    platforms: list[PublishingPlatform] = []
    if not isinstance(platform_values, list) or not platform_values:
        _issue(issues, "$.target_platforms", "must be a non-empty array", platform_values)
    else:
        for index, value in enumerate(platform_values):
            try:
                platform = PublishingPlatform(value)
            except (TypeError, ValueError):
                platform = None
            if platform not in SUPPORTED_EPISODE_PLATFORMS:
                _issue(
                    issues,
                    f"$.target_platforms[{index}]",
                    "unsupported platform",
                    value,
                    sorted(item.value for item in SUPPORTED_EPISODE_PLATFORMS),
                )
            elif platform in platforms:
                _issue(issues, f"$.target_platforms[{index}]", "duplicate platform", value)
            else:
                platforms.append(platform)

    defaults = _reject_unknown_fields(
        data.get("defaults", {}),
        path="$.defaults",
        allowed_fields=_DEFAULT_FIELDS,
        issues=issues,
    )
    default_duration = defaults.get("duration_sec", 3.0)
    default_transition = defaults.get("transition_type", "dissolve")
    default_transition_duration = defaults.get("transition_duration_sec", 0.0)
    if not isinstance(default_duration, (int, float)) or isinstance(default_duration, bool) or default_duration <= 0:
        _issue(issues, "$.defaults.duration_sec", "must be greater than zero", default_duration)
        default_duration = 3.0
    if default_transition not in SUPPORTED_COMIC_TRANSITIONS:
        _issue(
            issues,
            "$.defaults.transition_type",
            "unsupported transition",
            default_transition,
            sorted(SUPPORTED_COMIC_TRANSITIONS),
        )
        default_transition = "dissolve"
    if not isinstance(default_transition_duration, (int, float)) or isinstance(default_transition_duration, bool) or default_transition_duration < 0:
        _issue(
            issues,
            "$.defaults.transition_duration_sec",
            "must not be negative",
            default_transition_duration,
        )
        default_transition_duration = 0.0

    output_data = _reject_unknown_fields(
        data.get("output", {}),
        path="$.output",
        allowed_fields=_OUTPUT_FIELDS,
        issues=issues,
    )
    width = output_data.get("resolution_width", 1080)
    height = output_data.get("resolution_height", 1920)
    fps = output_data.get("fps", 24)
    for field, value in (("resolution_width", width), ("resolution_height", height)):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0 or value % 2:
            _issue(issues, f"$.output.{field}", "must be a positive even integer for H.264", value)
    if not isinstance(fps, int) or isinstance(fps, bool) or fps <= 0:
        _issue(issues, "$.output.fps", "must be a positive integer", fps)
    generate_master = output_data.get("generate_comic_master_video", False)
    if not isinstance(generate_master, bool):
        _issue(
            issues,
            "$.output.generate_comic_master_video",
            "must be a boolean",
            generate_master,
        )
        generate_master = False

    font_path = _parse_font(data.get("font"), package_root=package_root, issues=issues)
    frames = data.get("frames")
    source_paths: list[Path] = []
    scenes: list[ProductionScene] = []
    frame_ids: set[str] = set()
    if not isinstance(frames, list) or not frames:
        _issue(issues, "$.frames", "must be a non-empty array", frames)
        frames = []
    for index, raw_frame in enumerate(frames):
        frame_path = f"$.frames[{index}]"
        frame = _reject_unknown_fields(
            raw_frame,
            path=frame_path,
            allowed_fields=_FRAME_FIELDS,
            issues=issues,
        )
        frame_id = frame.get("frame_id")
        if not isinstance(frame_id, str) or not _IDENTIFIER_PATTERN.fullmatch(frame_id):
            _issue(issues, f"{frame_path}.frame_id", "must match ^[a-z0-9][a-z0-9_-]*$", frame_id)
            frame_id = f"invalid_{index}"
        elif frame_id in frame_ids:
            _issue(issues, f"{frame_path}.frame_id", "duplicate frame ID", frame_id)
        frame_ids.add(frame_id)

        image_result: dict[str, Any] = {"corrupt": True}
        image_path = _resolve_package_file(
            frame.get("image"),
            package_root=package_root,
            path=f"{frame_path}.image",
            issues=issues,
            extensions=SUPPORTED_IMAGE_EXTENSIONS,
        )
        if image_path is not None:
            image_result = validate_image(image_path)
            if image_result.get("corrupt"):
                _issue(issues, f"{frame_path}.image", "image is empty or unreadable", frame.get("image"))
            else:
                source_paths.append(image_path)

        duration = frame.get("duration_sec", default_duration)
        transition = frame.get("transition_type", default_transition)
        transition_duration = frame.get(
            "transition_duration_sec", default_transition_duration
        )
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
            _issue(issues, f"{frame_path}.duration_sec", "must be greater than zero", duration)
            duration = default_duration
        if transition not in SUPPORTED_COMIC_TRANSITIONS:
            _issue(
                issues,
                f"{frame_path}.transition_type",
                "unsupported transition",
                transition,
                sorted(SUPPORTED_COMIC_TRANSITIONS),
            )
            transition = default_transition
        if not isinstance(transition_duration, (int, float)) or isinstance(transition_duration, bool) or transition_duration < 0:
            _issue(
                issues,
                f"{frame_path}.transition_duration_sec",
                "must not be negative",
                transition_duration,
            )
            transition_duration = default_transition_duration
        if index < len(frames) - 1 and transition_duration >= duration:
            _issue(
                issues,
                f"{frame_path}.transition_duration_sec",
                "must be shorter than frame duration",
                transition_duration,
            )
        for preset in resolve_comic_platform_video_presets(platforms):
            try:
                calculate_comic_scene_timing(
                    duration,
                    preset,
                    is_last=index == len(frames) - 1,
                )
            except ValueError as exc:
                _issue(
                    issues,
                    f"{frame_path}.duration_sec",
                    str(exc),
                    duration,
                )

        anchor = _reject_unknown_fields(
            frame.get("tail_anchor", {}),
            path=f"{frame_path}.tail_anchor",
            allowed_fields=_ANCHOR_FIELDS,
            issues=issues,
        )
        try:
            overlay = ComicOverlay(
                speaker=frame.get("speaker"),
                text=frame.get("text"),
                position=frame.get("position"),
                tail_anchor=ComicTailAnchor(x=anchor.get("x"), y=anchor.get("y")),
            )
            scene = ProductionScene(
                scene_id=frame_id,
                index=index,
                image_source=frame.get("image") or "invalid",
                duration_sec=duration,
                transition_type=transition,
                transition_duration=transition_duration,
                comic_overlay=overlay,
            )
            scenes.append(scene)
            if image_path is not None and font_path is not None and not image_result.get("corrupt"):
                try:
                    validate_comic_frame_layout(image_path, overlay, font_path)
                except ValueError as exc:
                    _issue(issues, frame_path, f"comic layout is not renderable: {exc}")
        except ValidationError as exc:
            for error in exc.errors(include_url=False):
                location = ".".join(str(part) for part in error["loc"])
                if location in _ANCHOR_FIELDS:
                    location = f"tail_anchor.{location}"
                _issue(
                    issues,
                    f"{frame_path}.{location}",
                    error["msg"],
                    error.get("input"),
                )

    brief: ProductionBrief | None = None
    if not issues:
        try:
            brief = ProductionBrief(
                schema_version=EPISODE_SCHEMA_VERSION,
                title=title.strip(),
                workspace_id=workspace_id.strip(),
                project_id=project_id,
                production_brief_id=episode_id,
                scenario_id=f"episode_{episode_id}",
                content_format=ContentFormat.DIALOG_MINISERIES,
                target_platforms=platforms,
                scenes=scenes,
                subtitles=ProductionSubtitles(enabled=False, font_path=str(font_path)),
                output=ProductionOutput(
                    resolution_width=width,
                    resolution_height=height,
                    fps=fps,
                    generate_srt=False,
                    generate_cover=False,
                    generate_audio_only=False,
                    generate_comic_master_video=generate_master,
                ),
            ).transition_to(ProductionBriefStatus.VALIDATED)
        except ValidationError as exc:
            for error in exc.errors(include_url=False):
                location = ".".join(str(part) for part in error["loc"])
                _issue(issues, f"$.{location}", error["msg"], error.get("input"))

    if brief is not None:
        report = validate_production_assets(brief, package_root)
        for value in report.missing_files:
            _issue(issues, "$.frames", value)
        for value in report.corrupt_files:
            _issue(issues, "$.frames", value)
        for value in report.errors:
            _issue(issues, "$", value)
    if issues or brief is None or font_path is None:
        raise EpisodePackageValidationError(manifest_path, issues)
    return LoadedEpisodePackage(
        manifest_path=manifest_path,
        package_root=package_root,
        brief=brief,
        source_paths=tuple(source_paths),
        font_path=font_path,
    )


def stage_episode_package(
    package: LoadedEpisodePackage, runtime_projects_root: Path
) -> ProductionBrief:
    runtime_projects_root = Path(runtime_projects_root).resolve()
    project_dir = runtime_projects_root / package.brief.project_id
    episode_dir = project_dir / "episodes" / package.brief.production_brief_id
    frames_dir = episode_dir / "frames"
    assets_dir = episode_dir / "assets"
    frames_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "project.yaml").write_text(
        json.dumps(
            {
                "workspace_id": package.brief.workspace_id,
                "project_id": package.brief.project_id,
                "project_name": package.brief.title or package.brief.project_id,
                "project_slug": package.brief.project_id,
                "default_language": "ru",
                "status": "active",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    staged = package.brief.model_copy(deep=True)
    for scene, source in zip(staged.scenes, package.source_paths, strict=True):
        destination = frames_dir / f"{scene.scene_id}{source.suffix.lower()}"
        shutil.copy2(source, destination)
        scene.image_source = destination.relative_to(project_dir).as_posix()
    font_destination = assets_dir / package.font_path.name
    shutil.copy2(package.font_path, font_destination)
    staged.subtitles.font_path = font_destination.relative_to(project_dir).as_posix()
    return staged
