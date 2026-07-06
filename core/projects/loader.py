from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


CONTENT_PLANT_ROOT = Path(__file__).resolve().parents[2]
PROJECTS_ROOT = CONTENT_PLANT_ROOT / "projects"


class BrandConfig(BaseModel):
    colors: dict[str, str] = Field(default_factory=dict)
    fonts: dict[str, str] = Field(default_factory=dict)
    tone: str = ""


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
    id: str
    name: str
    language: str = "ru"
    timezone: str = "UTC"
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


def load_project(project_id: str, projects_root: Path | None = None) -> ProjectConfig:
    root = projects_root or PROJECTS_ROOT
    project_dir = root / project_id
    config_path = project_dir / "project.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Project config not found: {config_path}")

    raw = _load_config(config_path)
    raw.setdefault("id", project_id)
    raw.setdefault("name", project_id)
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
