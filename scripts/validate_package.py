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
READY_EXPORT_PACKAGE_STATUSES = ("ready",)

USAGE = """\
Validate a LOOPRA ExportPackage structure and required files.

Usage:
  python scripts/validate_package.py [--help | -h] <export_package_directory>

Arguments:
  export_package_directory    Path to the export package directory

Example:
  python scripts/validate_package.py storage/smoke_projects/example/exports/export_abc123"""


def _error(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def _validate_manifest(manifest: object) -> dict[str, object]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest.json must contain a JSON object")

    missing_fields = [field for field in REQUIRED_MANIFEST_FIELDS if field not in manifest]
    if missing_fields:
        raise ValueError(f"manifest.json is missing required fields: {', '.join(missing_fields)}")

    for field in (
        "package_id",
        "project_id",
        "content_item_id",
        "scenario_id",
        "content_format",
        "target_platform",
        "status",
    ):
        value = manifest[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"manifest.json field '{field}' must be a non-empty string")

    if manifest["manual_publication_only"] is not True:
        raise ValueError("manifest.json field 'manual_publication_only' must be true")

    status = manifest["status"]
    if status not in READY_EXPORT_PACKAGE_STATUSES:
        raise ValueError(
            "manifest.json field 'status' must be one of: "
            + ", ".join(READY_EXPORT_PACKAGE_STATUSES)
        )

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


def _ensure_file_exists(path: Path, message: str) -> None:
    if not path.exists() or not path.is_file():
        raise ValueError(message)


def _validate_package_directory(export_package_dir: Path, manifest: dict[str, object]) -> None:
    target_platform = str(manifest["target_platform"])

    metadata_path = export_package_dir / "metadata.json"
    _ensure_file_exists(
        metadata_path,
        f"metadata.json not found in export package directory: {export_package_dir}",
    )

    checklist_path = export_package_dir / "manual_publication_checklist.txt"
    _ensure_file_exists(
        checklist_path,
        f"manual_publication_checklist.txt not found in export package directory: {export_package_dir}",
    )

    for file_name in ("title.txt", "body.txt", f"caption_{target_platform}.txt"):
        _ensure_file_exists(export_package_dir / file_name, f"expected package file not found: {file_name}")

    try:
        json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"metadata.json is not valid JSON: {exc}") from exc

    for file_info in manifest["files"]:
        file_name = file_info["name"]
        _ensure_file_exists(
            export_package_dir / file_name,
            f"package file listed in manifest.json is missing on disk: {file_name}",
        )


def _build_summary_lines(manifest: dict[str, object]) -> list[str]:
    return [
        "validation_status=ok",
        f"package_id={manifest['package_id']}",
        f"project_id={manifest['project_id']}",
        f"target_platform={manifest['target_platform']}",
        f"files_checked={len(manifest['files'])}",
        "ready_for_manual_publication=true",
    ]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--help" in args or "-h" in args:
        print(USAGE)
        return 0

    if len(args) != 1:
        return _error("usage: python scripts/validate_package.py <export_package_directory>")

    export_package_dir = Path(args[0]).expanduser()
    if not export_package_dir.exists():
        return _error(f"export package directory does not exist: {export_package_dir}")
    if not export_package_dir.is_dir():
        return _error(f"export package directory is not a directory: {export_package_dir}")

    manifest_path = export_package_dir / "manifest.json"
    if not manifest_path.exists():
        return _error(f"manifest.json not found in export package directory: {export_package_dir}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return _error(f"manifest.json is not valid JSON: {exc}")

    try:
        validated_manifest = _validate_manifest(manifest)
        _validate_package_directory(export_package_dir, validated_manifest)
    except ValueError as exc:
        return _error(str(exc))

    for line in _build_summary_lines(validated_manifest):
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
