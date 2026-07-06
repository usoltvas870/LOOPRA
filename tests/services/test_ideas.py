from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.domain import ContentFormat, IdeaStatus, PublishingPlatform, ScenarioStatus
from core.services import (
    BrandProfileService,
    FileSystemIdeaRepository,
    FileSystemProjectRepository,
    FileSystemScenarioRepository,
    IdeaBankValidationError,
    IdeaService,
    ProjectService,
    ScenarioService,
    ScenarioStudioValidationError,
)


class IdeaAndScenarioServicesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name)
        self._write_project_fixture("example")
        self._write_project_fixture("second", project_name="Second Project")

        self.project_repository = FileSystemProjectRepository(self.projects_root)
        self.idea_repository = FileSystemIdeaRepository(self.projects_root)
        self.scenario_repository = FileSystemScenarioRepository(self.projects_root)
        self.project_service = ProjectService(self.project_repository)
        self.brand_profile_service = BrandProfileService(self.project_repository)
        self.idea_service = IdeaService(self.idea_repository, self.project_service)
        self.scenario_service = ScenarioService(
            self.scenario_repository,
            self.project_repository,
            self.project_service,
            self.brand_profile_service,
            self.idea_service,
            self.idea_repository,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_idea_persists_project_scoped_records(self) -> None:
        created = self.idea_service.create_idea(
            "example",
            title="Explain the workflow clearly",
            description="Use one concrete pain point and one practical next step.",
            funnel_stage="trust",
            tags=["workflow", "clarity"],
        )
        self.idea_service.create_idea(
            "second",
            title="Separate project scope",
            description="Should not appear in the first project list.",
        )

        ideas = self.idea_service.list_ideas("example")

        self.assertEqual(len(ideas), 1)
        self.assertEqual(ideas[0].idea_id, created.idea_id)
        self.assertEqual(ideas[0].status, IdeaStatus.RAW)
        self.assertEqual(self.idea_service.next_action_for(ideas[0]), "approve_or_reject")

    def test_invalid_funnel_stage_is_rejected(self) -> None:
        with self.assertRaises(IdeaBankValidationError):
            self.idea_service.create_idea(
                "example",
                title="Broken idea",
                funnel_stage="awareness",
            )

    def test_approved_idea_can_generate_text_social_post_scenario(self) -> None:
        idea = self.idea_service.create_idea(
            "example",
            title="Turn one idea into three platform posts",
            description="Show how one idea can become Telegram, Threads and VK content.",
            funnel_stage="conversion",
            content_format=ContentFormat.TEXT_SOCIAL_POST,
        )
        approved = self.idea_service.approve_idea("example", idea.idea_id)

        scenario = self.scenario_service.create_from_idea("example", approved.idea_id)
        updated_idea = self.idea_service.get_idea("example", approved.idea_id)

        self.assertEqual(scenario.idea_id, idea.idea_id)
        self.assertEqual(scenario.source_type, "idea")
        self.assertEqual(scenario.source_id, idea.idea_id)
        self.assertEqual(scenario.status, ScenarioStatus.NEEDS_REVIEW)
        self.assertEqual(updated_idea.status, IdeaStatus.SCRIPTED)
        self.assertEqual(
            scenario.target_platforms,
            [PublishingPlatform.TELEGRAM, PublishingPlatform.THREADS, PublishingPlatform.VK],
        )
        self.assertEqual(len(scenario.blocks), 3)
        self.assertIn("post_subtype", scenario.metadata)
        self.assertIn("telegram", scenario.caption_drafts)

    def test_raw_idea_cannot_generate_scenario(self) -> None:
        idea = self.idea_service.create_idea(
            "example",
            title="Needs approval first",
        )

        with self.assertRaises(ScenarioStudioValidationError):
            self.scenario_service.create_from_idea("example", idea.idea_id)

    def test_generated_scenario_can_be_approved(self) -> None:
        idea = self.idea_service.create_idea(
            "example",
            title="Review-ready draft",
            description="Generate a structured text post draft.",
            funnel_stage="trust",
        )
        approved_idea = self.idea_service.approve_idea("example", idea.idea_id)
        scenario = self.scenario_service.create_from_idea("example", approved_idea.idea_id)

        approved_scenario = self.scenario_service.approve_scenario("example", scenario.scenario_id)

        self.assertEqual(approved_scenario.status, ScenarioStatus.APPROVED)

    def test_task_3_files_do_not_contain_project_specific_branching_markers(self) -> None:
        task_3_files = [
            Path("core/domain/enums.py"),
            Path("core/domain/models.py"),
            Path("core/services/ideas.py"),
        ]
        forbidden_markers = ["if project_id ==", "if project_id==", "project_id =="]

        for file_path in task_3_files:
            with self.subTest(file_path=file_path):
                content = file_path.read_text(encoding="utf-8").lower()
                for marker in forbidden_markers:
                    with self.subTest(file_path=file_path, marker=marker):
                        self.assertNotIn(marker, content)

    def _write_project_fixture(self, project_id: str, *, project_name: str | None = None) -> None:
        payload = json.loads(Path("projects/example/project.yaml").read_text(encoding="utf-8"))
        payload["project_id"] = project_id
        payload["project_name"] = project_name or f"{project_id.title()} Project"
        payload["project_slug"] = f"{project_id}_project"
        payload["brand"]["brand_name"] = f"{project_id.title()} Brand"

        project_dir = self.projects_root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "project.yaml").write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
