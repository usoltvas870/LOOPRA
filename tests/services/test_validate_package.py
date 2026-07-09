from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_package.py"


def _build_manifest(**overrides: object) -> dict[str, object]:
    manifest = {
        "package_id": "export_001",
        "project_id": "example",
        "content_item_id": "content_001",
        "scenario_id": "scenario_001",
        "content_format": "text_social_post",
        "target_platform": "telegram",
        "manual_publication_only": True,
        "status": "ready",
        "files": [
            {"name": "title.txt", "role": "title"},
            {"name": "body.txt", "role": "body"},
            {"name": "caption_telegram.txt", "role": "caption"},
            {"name": "manual_publication_checklist.txt", "role": "manual_publication_checklist"},
            {"name": "metadata.json", "role": "metadata"},
            {"name": "manifest.json", "role": "manifest"},
        ],
    }
    manifest.update(overrides)
    return manifest


def _build_metadata(**overrides: object) -> dict[str, object]:
    metadata = {
        "project_id": "example",
        "content_item_id": "content_001",
        "scenario_id": "scenario_001",
        "content_format": "text_social_post",
        "target_platform": "telegram",
        "manual_publication_only": True,
        "prepared_at": "2026-07-07T00:00:00+00:00",
    }
    metadata.update(overrides)
    return metadata


class ValidatePackageScriptTests(unittest.TestCase):
    def _run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def _write_valid_export_package(
        self,
        export_dir: Path,
        *,
        raw_manifest: dict[str, object] | None = None,
        manifest_overrides: dict[str, object] | None = None,
        metadata_overrides: dict[str, object] | None = None,
        missing_files: set[str] | None = None,
        invalid_metadata_text: str | None = None,
    ) -> None:
        manifest = raw_manifest or _build_manifest(**(manifest_overrides or {}))
        metadata = _build_metadata(**(metadata_overrides or {}))
        missing_files = missing_files or set()

        files_to_write: dict[str, str] = {
            "title.txt": "Example title",
            "body.txt": "Example body",
            f"caption_{manifest['target_platform']}.txt": "Example caption",
            "manual_publication_checklist.txt": "Manual publication checklist",
            "metadata.json": (
                invalid_metadata_text
                if invalid_metadata_text is not None
                else json.dumps(metadata, indent=2)
            ),
            "manifest.json": json.dumps(manifest, indent=2),
        }

        manifest_files = manifest.get("files")
        if isinstance(manifest_files, list):
            for file_info in manifest_files:
                if not isinstance(file_info, dict) or "name" not in file_info:
                    continue
                name = file_info["name"]
                if name not in files_to_write:
                    files_to_write[name] = f"placeholder for {name}"

        for name, contents in files_to_write.items():
            if name in missing_files:
                continue
            (export_dir / name).write_text(contents, encoding="utf-8")

    def test_validates_complete_export_package_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            self._write_valid_export_package(export_dir)

            completed = self._run_script(str(export_dir))

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                completed.stdout.splitlines(),
                [
                    "validation_status=ok",
                    "package_id=export_001",
                    "project_id=example",
                    "target_platform=telegram",
                    "files_checked=6",
                    "ready_for_manual_publication=true",
                ],
            )
            self.assertEqual(completed.stderr, "")

    def test_returns_clear_error_when_argument_is_missing(self) -> None:
        completed = self._run_script()

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("usage: python scripts/validate_package.py <export_package_directory>", completed.stderr)

    def test_returns_clear_error_when_directory_is_missing(self) -> None:
        completed = self._run_script("does-not-exist")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("export package directory does not exist", completed.stderr)

    def test_returns_clear_error_when_manifest_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("manifest.json not found", completed.stderr)

    def test_returns_clear_error_when_manifest_json_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            (export_dir / "manifest.json").write_text("{not-json", encoding="utf-8")

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("manifest.json is not valid JSON", completed.stderr)

    def test_returns_clear_error_when_required_manifest_field_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            manifest = _build_manifest()
            del manifest["scenario_id"]
            self._write_valid_export_package(export_dir, raw_manifest=manifest)

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("manifest.json is missing required fields: scenario_id", completed.stderr)

    def test_returns_clear_error_when_files_field_is_not_a_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            self._write_valid_export_package(export_dir, manifest_overrides={"files": "not-a-list"})

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("manifest.json field 'files' must be a list", completed.stderr)

    def test_returns_clear_error_when_file_entry_is_missing_name_or_role(self) -> None:
        cases = (
            ([{"role": "title"}], "manifest.json field 'files[0]' is missing required fields: name"),
            ([{"name": "title.txt"}], "manifest.json field 'files[0]' is missing required fields: role"),
        )

        for files, expected_error in cases:
            with self.subTest(expected_error=expected_error):
                with tempfile.TemporaryDirectory() as temp_dir:
                    export_dir = Path(temp_dir) / "export_001"
                    export_dir.mkdir()
                    self._write_valid_export_package(export_dir, manifest_overrides={"files": files})

                    completed = self._run_script(str(export_dir))

                    self.assertNotEqual(completed.returncode, 0)
                    self.assertIn(expected_error, completed.stderr)

    def test_rejects_absolute_paths_in_manifest_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            absolute_title_path = str((export_dir / "title.txt").resolve())
            self._write_valid_export_package(
                export_dir,
                manifest_overrides={"files": [{"name": absolute_title_path, "role": "title"}]},
            )

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("must not be an absolute path", completed.stderr)

    def test_returns_clear_error_when_manifest_lists_file_missing_on_disk(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            manifest = _build_manifest(
                files=[
                    *_build_manifest()["files"],
                    {"name": "extra_notes.txt", "role": "notes"},
                ]
            )
            self._write_valid_export_package(
                export_dir,
                raw_manifest=manifest,
                missing_files={"extra_notes.txt"},
            )

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("package file listed in manifest.json is missing on disk: extra_notes.txt", completed.stderr)

    def test_returns_clear_error_when_metadata_json_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            self._write_valid_export_package(export_dir, missing_files={"metadata.json"})

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("metadata.json not found", completed.stderr)

    def test_returns_clear_error_when_metadata_json_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            self._write_valid_export_package(export_dir, invalid_metadata_text="{not-json")

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("metadata.json is not valid JSON", completed.stderr)

    def test_returns_clear_error_when_manual_publication_checklist_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            self._write_valid_export_package(export_dir, missing_files={"manual_publication_checklist.txt"})

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("manual_publication_checklist.txt not found", completed.stderr)

    def test_returns_clear_error_when_expected_caption_file_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            self._write_valid_export_package(export_dir, missing_files={"caption_telegram.txt"})

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("expected package file not found: caption_telegram.txt", completed.stderr)

    def test_returns_clear_error_when_manual_publication_only_is_not_true(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            self._write_valid_export_package(export_dir, manifest_overrides={"manual_publication_only": False})

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("manifest.json field 'manual_publication_only' must be true", completed.stderr)

    def test_returns_clear_error_when_status_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            self._write_valid_export_package(export_dir, manifest_overrides={"status": "draft"})

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("manifest.json field 'status' must be one of: ready", completed.stderr)

    def test_script_files_do_not_contain_project_specific_strings(self) -> None:
        forbidden_project_marker = "n" + "u" + "r" + "a"
        forbidden_brand_variant = forbidden_project_marker + "-" + "ai"
        for file_path in (SCRIPT_PATH, Path(__file__)):
            with self.subTest(file_path=str(file_path)):
                content = file_path.read_text(encoding="utf-8").lower()
                self.assertNotIn(forbidden_project_marker, content)
                self.assertNotIn(forbidden_brand_variant, content)

    def test_help_flag_prints_usage_and_exits_zero(self) -> None:
        completed = self._run_script("--help")
        self.assertEqual(completed.returncode, 0)
        self.assertIn("Usage", completed.stdout)

    def test_short_help_flag_prints_usage_and_exits_zero(self) -> None:
        completed = self._run_script("-h")
        self.assertEqual(completed.returncode, 0)
        self.assertIn("Usage", completed.stdout)


if __name__ == "__main__":
    unittest.main()
