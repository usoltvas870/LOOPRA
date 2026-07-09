from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_MANIFEST_FIELDS = (
    "package_id",
    "project_id",
    "content_item_id",
    "scenario_id",
    "content_format",
    "target_platform",
    "manual_publication_only",
    "status",
    "files",
)

USAGE = """\
Display the contents of a LOOPRA ExportPackage.

Usage:
  python scripts/inspect_package.py [--help | -h] <export_package_directory>

Arguments:
  export_package_directory    Path to the export package directory

Example:
  python scripts/inspect_package.py storage/smoke_projects/example/exports/export_abc123"""


def _error(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def _error_json(message: str) -> int:
    print(json.dumps({"status": "error", "error_type": "validation_error", "message": message}, indent=2))
    return 1


def _validate_manifest(manifest: object) -> dict[str, object]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest.json must contain a JSON object")

    missing_fields = [field for field in REQUIRED_MANIFEST_FIELDS if field not in manifest]
    if missing_fields:
        raise ValueError(f"manifest.json is missing required fields: {', '.join(missing_fields)}")

    files = manifest["files"]
    if not isinstance(files, list):
        raise ValueError("manifest.json field 'files' must be a list")

    for index, file_info in enumerate(files):
        if not isinstance(file_info, dict):
            raise ValueError(f"manifest.json field 'files[{index}]' must be an object")

        missing_file_fields = [field for field in ("name", "role") if field not in file_info]
        if missing_file_fields:
            raise ValueError(
                f"manifest.json field 'files[{index}]' is missing required fields: {', '.join(missing_file_fields)}"
            )

        name = file_info["name"]
        role = file_info["role"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"manifest.json field 'files[{index}].name' must be a non-empty string")
        if not isinstance(role, str) or not role.strip():
            raise ValueError(f"manifest.json field 'files[{index}].role' must be a non-empty string")

        file_name = Path(name)
        if file_name.is_absolute():
            raise ValueError(f"manifest.json field 'files[{index}].name' must not be an absolute path")
        if file_name.name != name:
            raise ValueError(f"manifest.json field 'files[{index}].name' must be a relative file name")

    return manifest


def _build_summary_lines(manifest: dict[str, object]) -> list[str]:
    lines = [
        f"package_id={manifest['package_id']}",
        f"project_id={manifest['project_id']}",
        f"content_item_id={manifest['content_item_id']}",
        f"scenario_id={manifest['scenario_id']}",
        f"content_format={manifest['content_format']}",
        f"target_platform={manifest['target_platform']}",
        f"status={manifest['status']}",
        f"manual_publication_only={str(manifest['manual_publication_only']).lower()}",
        "files:",
    ]

    for file_info in manifest["files"]:
        lines.append(f"- {file_info['name']} [{file_info['role']}]")

    return lines


def _build_json_success(manifest: dict[str, object]) -> dict[str, object]:
    return {
        "status": "success",
        "package_id": manifest["package_id"],
        "project_id": manifest["project_id"],
        "content_item_id": manifest["content_item_id"],
        "scenario_id": manifest["scenario_id"],
        "content_format": manifest["content_format"],
        "target_platform": manifest["target_platform"],
        "export_package_status": manifest["status"],
        "manual_publication_only": manifest["manual_publication_only"],
        "files": [{"name": f["name"], "role": f["role"]} for f in manifest["files"]],
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if "--help" in args or "-h" in args:
        print(USAGE)
        return 0

    valid_flags = {"--help", "-h", "--json"}
    flags = [a for a in args if a.startswith("-")]
    positional_args = [a for a in args if not a.startswith("-")]
    unknown_flags = [f for f in flags if f not in valid_flags]
    json_mode = "--json" in args

    if unknown_flags:
        message = f"unknown option: {unknown_flags[0]}"
        if json_mode:
            return _error_json(message)
        return _error(message)

    if len(positional_args) != 1:
        if json_mode:
            return _error_json("usage: python scripts/inspect_package.py [--json] <export_package_directory>")
        return _error("usage: python scripts/inspect_package.py <export_package_directory>")

    emit_error = _error_json if json_mode else _error

    export_package_dir = Path(positional_args[0]).expanduser()
    if not export_package_dir.exists():
        return emit_error(f"export package directory does not exist: {export_package_dir}")
    if not export_package_dir.is_dir():
        return emit_error(f"export package directory is not a directory: {export_package_dir}")

    manifest_path = export_package_dir / "manifest.json"
    if not manifest_path.exists():
        return emit_error(f"manifest.json not found in export package directory: {export_package_dir}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return emit_error(f"manifest.json is not valid JSON: {exc}")

    try:
        validated_manifest = _validate_manifest(manifest)
    except ValueError as exc:
        return emit_error(str(exc))

    if json_mode:
        print(json.dumps(_build_json_success(validated_manifest), indent=2))
    else:
        for line in _build_summary_lines(validated_manifest):
            print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
