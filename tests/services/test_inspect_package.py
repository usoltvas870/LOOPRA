from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "inspect_package.py"


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


class InspectPackageScriptTests(unittest.TestCase):
    def _run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_inspects_valid_export_package_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            (export_dir / "manifest.json").write_text(
                json.dumps(_build_manifest(), indent=2),
                encoding="utf-8",
            )

            completed = self._run_script(str(export_dir))

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                completed.stdout.splitlines(),
                [
                    "package_id=export_001",
                    "project_id=example",
                    "content_item_id=content_001",
                    "scenario_id=scenario_001",
                    "content_format=text_social_post",
                    "target_platform=telegram",
                    "status=ready",
                    "manual_publication_only=true",
                    "files:",
                    "- title.txt [title]",
                    "- body.txt [body]",
                    "- caption_telegram.txt [caption]",
                    "- manual_publication_checklist.txt [manual_publication_checklist]",
                    "- metadata.json [metadata]",
                    "- manifest.json [manifest]",
                ],
            )
            self.assertEqual(completed.stderr, "")

    def test_returns_clear_error_when_argument_is_missing(self) -> None:
        completed = self._run_script()

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("usage: python scripts/inspect_package.py <export_package_directory>", completed.stderr)

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

    def test_returns_clear_error_when_required_fields_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            manifest = _build_manifest()
            del manifest["scenario_id"]
            (export_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("manifest.json is missing required fields: scenario_id", completed.stderr)

    def test_rejects_absolute_paths_in_manifest_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "export_001"
            export_dir.mkdir()
            manifest = _build_manifest(files=[{"name": str((export_dir / "title.txt").resolve()), "role": "title"}])
            (export_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            completed = self._run_script(str(export_dir))

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("must not be an absolute path", completed.stderr)

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
