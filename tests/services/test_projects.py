from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.domain import BrandProfileStatus, ProjectStatus
from core.projects.loader import InvalidProjectIdError, load_project
from core.services import (
    BrandProfileService,
    FileSystemProjectRepository,
    ProjectConfigValidationError,
    ProjectService,
    WorkspaceService,
)


class ProjectServicesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.projects_root = Path("projects")
        self.repository = FileSystemProjectRepository(self.projects_root)
        self.workspace_service = WorkspaceService()
        self.project_service = ProjectService(self.repository, self.workspace_service)
        self.brand_profile_service = BrandProfileService(self.repository, self.workspace_service)

    def test_project_can_be_loaded_from_example_project_config(self) -> None:
        config = load_project("example", projects_root=self.projects_root)
        project = self.project_service.get_project("example")

        self.assertEqual(config.id, "example")
        self.assertEqual(project.project_id, "example")
        self.assertEqual(project.slug, "example_project")
        self.assertEqual(project.status, ProjectStatus.ACTIVE)

    def test_list_projects_returns_example_project(self) -> None:
        projects = self.project_service.list_projects()
        project_ids = [p.project_id for p in projects]

        self.assertGreaterEqual(len(projects), 1)
        self.assertIn("example", project_ids)

    def test_brand_profile_can_be_built_from_project_config(self) -> None:
        brand_profile = self.brand_profile_service.get_brand_profile("example")

        self.assertEqual(brand_profile.project_id, "example")
        self.assertEqual(brand_profile.name, "Example Brand")
        self.assertEqual(brand_profile.status, BrandProfileStatus.ACTIVE)
        self.assertIn("clarity", brand_profile.brand_values)
        self.assertEqual(brand_profile.tone_of_voice.tone_summary, "Clear, warm and practical.")

    def test_missing_project_raises_clear_error(self) -> None:
        with self.assertRaises(FileNotFoundError) as context:
            self.project_service.get_project("missing")

        self.assertIn("project_id 'missing'", str(context.exception))

    def test_invalid_project_id_is_rejected(self) -> None:
        invalid_project_ids = ["../example", "example/child", "", "Example", "demo project"]

        for project_id in invalid_project_ids:
            with self.subTest(project_id=project_id):
                with self.assertRaises(InvalidProjectIdError):
                    self.project_service.get_project(project_id)

    def test_required_project_fields_are_validated(self) -> None:
        project_payload = {
            "project_id": "broken",
            "project_name": "Broken Project",
            "default_language": "en",
            "status": "active",
            "brand": {
                "brand_name": "Broken Brand",
                "positioning": "Missing slug demo.",
                "audience_summary": "Readers validating error handling.",
            },
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_root = Path(tmp_dir)
            self._write_project_config(projects_root, "broken", project_payload)
            project_service = ProjectService(FileSystemProjectRepository(projects_root))

            with self.assertRaises(ProjectConfigValidationError) as context:
                project_service.get_project("broken")

        self.assertIn("project_slug", str(context.exception))

    def test_required_brand_profile_fields_are_validated(self) -> None:
        project_payload = {
            "project_id": "broken_brand",
            "project_name": "Broken Brand Project",
            "project_slug": "broken_brand_project",
            "default_language": "en",
            "status": "active",
            "brand": {
                "brand_name": "Broken Brand",
                "positioning": "",
                "audience_summary": "Audience exists but positioning is blank.",
            },
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_root = Path(tmp_dir)
            self._write_project_config(projects_root, "broken_brand", project_payload)
            brand_profile_service = BrandProfileService(FileSystemProjectRepository(projects_root))

            with self.assertRaises(ProjectConfigValidationError) as context:
                brand_profile_service.get_brand_profile("broken_brand")

        self.assertIn("brand.positioning", str(context.exception))

    def test_task_2_files_do_not_contain_project_specific_branching_markers(self) -> None:
        task_2_files = [
            Path("core/projects/loader.py"),
            Path("core/services/__init__.py"),
            Path("core/services/projects.py"),
            Path("projects/example/project.yaml"),
        ]
        forbidden_markers = ["if project_id ==", "if project_id==", "project_id =="]

        for file_path in task_2_files:
            with self.subTest(file_path=file_path):
                content = file_path.read_text(encoding="utf-8").lower()
                for marker in forbidden_markers:
                    with self.subTest(file_path=file_path, marker=marker):
                        self.assertNotIn(marker, content)

    @staticmethod
    def _write_project_config(projects_root: Path, project_id: str, payload: dict[str, object]) -> None:
        project_dir = projects_root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "project.yaml").write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
