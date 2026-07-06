from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


CONTENT_PLANT_ROOT = Path(__file__).resolve().parents[2]
PROJECTS_ROOT = CONTENT_PLANT_ROOT / "projects"
PROJECT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


class InvalidProjectIdError(ValueError):
    """Raised when a project identifier is invalid or unsafe for filesystem use."""


class BrandConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = ""
    description: str = ""
    positioning: str = ""
    audience_summary: str = ""
    language: str = ""
    status: str = ""
    brand_values: list[str] = Field(default_factory=list)
    tone_of_voice: dict[str, Any] = Field(default_factory=dict)
    content_rules: dict[str, Any] = Field(default_factory=dict)
    colors: dict[str, str] = Field(default_factory=dict)
    fonts: dict[str, str] = Field(default_factory=dict)
    tone: str = ""

    @model_validator(mode="before")
    @classmethod
    def normalize_brand_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        normalized = dict(data)
        alias_map = {
            "brand_name": "name",
            "brand_description": "description",
        }
        for source_key, target_key in alias_map.items():
            if source_key in normalized and target_key not in normalized:
                normalized[target_key] = normalized[source_key]
        return normalized


class AssetsConfig(BaseModel):
    avatar_video: str | None = None
    stock_dir: str = "assets/video"
    audio_dir: str = "assets/audio"
    image_dir: str = "assets/images"


class PromptsConfig(BaseModel):
    trend_analysis: str | None = None
    brief_parser: str | None = None
    video_scenario: str | None = None


class TemplatesConfig(BaseModel):
    hyperframes: dict[str, str] = Field(default_factory=dict)
    video: dict[str, str] = Field(default_factory=dict)


class VideoConfig(BaseModel):
    default_format: str = "9:16"
    fps: int = 24
    supported_types: list[str] = Field(default_factory=lambda: ["voice", "text", "avatar"])
    default_type: str = "voice"


class ProjectConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    workspace_id: str = "internal"
    id: str
    name: str = ""
    slug: str = ""
    description: str = ""
    status: str = "active"
    language: str = "ru"
    timezone: str = "UTC"
    primary_url: str = ""
    target_platforms: list[str] = Field(default_factory=list)
    project_dir: Path
    brand: BrandConfig = BrandConfig()
    audience: dict[str, Any] = Field(default_factory=dict)
    cta: dict[str, Any] = Field(default_factory=dict)
    video: VideoConfig = VideoConfig()
    assets: AssetsConfig = AssetsConfig()
    prompts: PromptsConfig = PromptsConfig()
    templates: TemplatesConfig = TemplatesConfig()
    video_formats: dict[str, Any] = Field(default_factory=dict)
    style: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_project_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        normalized = dict(data)
        alias_map = {
            "project_id": "id",
            "project_name": "name",
            "project_slug": "slug",
            "default_language": "language",
        }
        for source_key, target_key in alias_map.items():
            if source_key in normalized and target_key not in normalized:
                normalized[target_key] = normalized[source_key]
        return normalized

    def resolve(self, relative_path: str | None) -> Path | None:
        if not relative_path:
            return None
        path = Path(relative_path)
        if path.is_absolute():
            return path
        return self.project_dir / path

    def read_prompt(self, key: str) -> str:
        prompt_path = getattr(self.prompts, key)
        resolved = self.resolve(prompt_path)
        if not resolved or not resolved.exists():
            raise FileNotFoundError(f"Prompt '{key}' not found for project '{self.id}'")
        return resolved.read_text(encoding="utf-8")


def validate_project_id(project_id: str) -> str:
    if not isinstance(project_id, str):
        raise InvalidProjectIdError("project_id must be a string")

    normalized = project_id.strip()
    if not normalized:
        raise InvalidProjectIdError("project_id must not be empty")
    if not PROJECT_ID_PATTERN.fullmatch(normalized):
        raise InvalidProjectIdError(
            "project_id must match ^[a-z0-9][a-z0-9_-]*$ and must not contain path separators"
        )
    return normalized


def resolve_project_dir(project_id: str, projects_root: Path | None = None) -> Path:
    root = (projects_root or PROJECTS_ROOT).resolve()
    safe_project_id = validate_project_id(project_id)
    project_dir = (root / safe_project_id).resolve()

    try:
        project_dir.relative_to(root)
    except ValueError as exc:
        raise InvalidProjectIdError(f"project_id '{safe_project_id}' resolves outside projects root") from exc

    return project_dir


def load_project(project_id: str, projects_root: Path | None = None) -> ProjectConfig:
    project_dir = resolve_project_dir(project_id, projects_root)
    config_path = project_dir / "project.yaml"
    if not config_path.exists():
        raise FileNotFoundError(
            f"Project config not found for project_id '{project_dir.name}': {config_path}"
        )

    raw = _load_config(config_path)
    raw.setdefault("id", project_dir.name)
    raw["project_dir"] = project_dir
    return ProjectConfig.model_validate(raw)


def _load_config(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml
    except ImportError:
        return _parse_simple_yaml(text)
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"Project config must be a mapping: {path}")
    return data


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Small fallback parser for the simple project.yaml shape used here."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    lines: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        line = _strip_yaml_comment(raw_line).rstrip()
        if line.strip():
            lines.append((len(line) - len(line.lstrip(" ")), line.strip()))

    def parse_mapping(index: int, indent: int) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        while index < len(lines):
            line_indent, stripped = lines[index]
            if line_indent < indent:
                break
            if line_indent > indent:
                raise ValueError(f"Unexpected indentation near: {stripped}")
            if stripped.startswith("- "):
                break

            key, sep, value = stripped.partition(":")
            if not sep:
                raise ValueError(f"Invalid YAML line: {stripped}")
            key = key.strip()
            value = value.strip()
            index += 1

            if value:
                result[key] = _coerce_scalar(value)
                continue

            if index >= len(lines) or lines[index][0] <= line_indent:
                result[key] = {}
                continue

            child_indent, child = lines[index]
            if child.startswith("- "):
                result[key], index = parse_list(index, child_indent)
            else:
                result[key], index = parse_mapping(index, child_indent)
        return result, index

    def parse_list(index: int, indent: int) -> tuple[list[Any], int]:
        result: list[Any] = []
        while index < len(lines):
            line_indent, stripped = lines[index]
            if line_indent < indent:
                break
            if line_indent != indent or not stripped.startswith("- "):
                break
            result.append(_coerce_scalar(stripped[2:].strip()))
            index += 1
        return result, index

    parsed, _ = parse_mapping(0, lines[0][0] if lines else 0)
    return parsed


def _coerce_scalar(value: str) -> Any:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        return value


def _strip_yaml_comment(line: str) -> str:
    in_single = False
    in_double = False
    for i, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:i]
    return line
