from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.projects.loader import PROJECTS_ROOT
from core.services import build_content_intelligence_service


def resolve_projects_root() -> Path:
    override = (os.environ.get("LOOPRA_PROJECTS_ROOT") or os.environ.get("CONTENT_PLANT_PROJECTS_ROOT") or "").strip()
    return Path(override).expanduser().resolve() if override else PROJECTS_ROOT


def parse_common(argv: list[str], usage: str, positional_count: int | None = None) -> tuple[bool, list[str]] | int:
    if "--help" in argv or "-h" in argv:
        print(usage)
        return 0
    valid_flags = {"--help", "-h", "--json"}
    unknown = [arg for arg in argv if arg.startswith("-") and arg not in valid_flags]
    json_mode = "--json" in argv
    if unknown:
        return error(f"unknown option: {unknown[0]}", json_mode)
    positional = [arg for arg in argv if not arg.startswith("-")]
    if positional_count is not None and len(positional) != positional_count:
        return error(f"expected {positional_count} argument(s), got {len(positional)}", json_mode)
    return json_mode, positional


def load_json_arg(raw: str) -> dict[str, object]:
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("JSON argument must be an object")
    return value


def dump_success(payload: dict[str, object], json_mode: bool, human_lines: list[str]) -> int:
    if json_mode:
        print(json.dumps({"status": "success", **payload}, indent=2, ensure_ascii=False))
    else:
        for line in human_lines:
            print(line)
    return 0


def error(message: str, json_mode: bool, error_type: str = "validation_error") -> int:
    if json_mode:
        print(json.dumps({"status": "error", "error_type": error_type, "message": message}, indent=2))
    else:
        print(f"ERROR: {message}", file=sys.stderr)
    return 1


def service():
    return build_content_intelligence_service(resolve_projects_root())
