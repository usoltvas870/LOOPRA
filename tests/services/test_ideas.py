from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.domain import (
    ContentFormat,
    IdeaStatus,
    PublishingPlatform,
    Scenario,
    ScenarioStatus,
    ScenarioTextBlock,
)
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

_UNSET = object()


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

    def test_approved_carousel_idea_creates_sorted_traceable_scenario(self) -> None:
        idea = self._create_approved_carousel_idea()
        blocks = [
            ScenarioTextBlock(block_id="cta", order=3, role="cta", text="Save this guide."),
            ScenarioTextBlock(block_id="quote", order=1, role="quote", text="A useful quote."),
            ScenarioTextBlock(block_id="body", order=2, role="body", text="A practical explanation."),
        ]
        original_blocks = [block.model_dump(mode="json") for block in blocks]

        scenario = self.scenario_service.create_from_idea(
            "example",
            idea.idea_id,
            content_format=ContentFormat.INSTAGRAM_CAROUSEL,
            target_platforms=[PublishingPlatform.INSTAGRAM],
            blocks=blocks,
        )

        self.assertEqual(scenario.status, ScenarioStatus.NEEDS_REVIEW)
        self.assertEqual(self.idea_service.get_idea("example", idea.idea_id).status, IdeaStatus.SCRIPTED)
        self.assertEqual(scenario.idea_id, idea.idea_id)
        self.assertEqual(scenario.source_type, "idea")
        self.assertEqual(scenario.source_id, idea.idea_id)
        self.assertEqual(scenario.brand_profile_id, "brand_example")
        self.assertEqual(scenario.title, idea.title)
        self.assertEqual(scenario.content_format, ContentFormat.INSTAGRAM_CAROUSEL)
        self.assertEqual(scenario.target_platforms, [PublishingPlatform.INSTAGRAM])
        self.assertEqual([block.block_id for block in scenario.blocks], ["quote", "body", "cta"])
        self.assertEqual([block.text for block in scenario.blocks], [
            "A useful quote.", "A practical explanation.", "Save this guide."
        ])
        self.assertEqual([block.model_dump(mode="json") for block in blocks], original_blocks)
        reloaded = self.scenario_service.get_scenario("example", scenario.scenario_id)
        self.assertEqual(reloaded, scenario)

    def test_carousel_idea_lifecycle_accepts_approved_and_scripted_only(self) -> None:
        raw = self.idea_service.create_idea(
            "example", title="Raw carousel", content_format=ContentFormat.INSTAGRAM_CAROUSEL
        )
        rejected = self.idea_service.reject_idea("example", raw.idea_id)
        archived = self.idea_service.archive_idea("example", rejected.idea_id)

        for idea in (raw, rejected, archived):
            with self.subTest(status=idea.status):
                with self.assertRaises(ScenarioStudioValidationError):
                    self._create_carousel_scenario(idea.idea_id)

        scripted = self._create_approved_carousel_idea()
        self.idea_repository.save_idea(scripted.transition_to(IdeaStatus.SCRIPTED))
        scenario = self._create_carousel_scenario(scripted.idea_id)
        self.assertEqual(scenario.status, ScenarioStatus.NEEDS_REVIEW)
        self.assertEqual(self.idea_service.get_idea("example", scripted.idea_id).status, IdeaStatus.SCRIPTED)

    def test_carousel_format_and_platform_guards_are_atomic(self) -> None:
        text_idea = self.idea_service.approve_idea(
            "example",
            self.idea_service.create_idea(
                "example", title="Text idea", content_format=ContentFormat.TEXT_SOCIAL_POST
            ).idea_id,
        )
        with self.assertRaises(ScenarioStudioValidationError):
            self.scenario_service.create_from_idea(
                "example",
                text_idea.idea_id,
                content_format=ContentFormat.INSTAGRAM_CAROUSEL,
                target_platforms=[PublishingPlatform.INSTAGRAM],
                blocks=self._carousel_blocks(),
            )

        carousel_idea = self._create_approved_carousel_idea()
        invalid_platforms = (
            None,
            [],
            [PublishingPlatform.TIKTOK],
            [PublishingPlatform.YOUTUBE_SHORTS],
            [PublishingPlatform.VK],
            [PublishingPlatform.INSTAGRAM, PublishingPlatform.TIKTOK],
        )
        for platforms in invalid_platforms:
            with self.subTest(platforms=platforms):
                with self.assertRaises(ScenarioStudioValidationError):
                    self._create_carousel_scenario(carousel_idea.idea_id, target_platforms=platforms)
                self.assertEqual(self.scenario_repository.list_scenarios("example"), [])
                self.assertEqual(
                    self.idea_service.get_idea("example", carousel_idea.idea_id).status,
                    IdeaStatus.APPROVED,
                )

        with self.assertRaises(ScenarioStudioValidationError):
            self.scenario_service.create_from_idea(
                "example",
                carousel_idea.idea_id,
                content_format=ContentFormat.TEXT_SOCIAL_POST,
                target_platforms=[PublishingPlatform.INSTAGRAM],
                blocks=self._carousel_blocks(),
            )

    def test_carousel_block_validation_is_atomic_and_allows_downstream_roles(self) -> None:
        invalid_cases = {
            "missing": None,
            "empty": [],
            "duplicate_id": self._carousel_blocks() + [
                ScenarioTextBlock(block_id="body", order=4, role="body", text="Duplicate id.")
            ],
            "duplicate_order": self._carousel_blocks() + [
                ScenarioTextBlock(block_id="later", order=1, role="body", text="Duplicate order.")
            ],
            "empty_text": [ScenarioTextBlock(block_id="body", order=1, role="body", text="   ")],
            "unsupported_role": [ScenarioTextBlock(block_id="cover", order=1, role="cover", text="No cover.")],
            "wrong_platform": [
                ScenarioTextBlock(
                    block_id="body", order=1, role="body", text="Wrong platform.",
                    platform=PublishingPlatform.TIKTOK,
                )
            ],
            "invalid_input": [{"block_id": "body"}],
        }
        for name, blocks in invalid_cases.items():
            idea = self._create_approved_carousel_idea()
            with self.subTest(case=name):
                with self.assertRaises(ScenarioStudioValidationError):
                    self._create_carousel_scenario(idea.idea_id, blocks=blocks)
                self.assertEqual(self.scenario_repository.list_scenarios("example"), [])
                self.assertEqual(
                    self.idea_service.get_idea("example", idea.idea_id).status,
                    IdeaStatus.APPROVED,
                )

        for role in ("body", "quote", "list", "cta"):
            idea = self._create_approved_carousel_idea()
            with self.subTest(role=role):
                scenario = self._create_carousel_scenario(
                    idea.idea_id,
                    blocks=[ScenarioTextBlock(block_id=role, order=1, role=role, text=role)],
                )
                self.assertEqual(scenario.blocks[0].role, role)

    def test_carousel_duplicate_is_project_scoped_and_does_not_mutate_records(self) -> None:
        idea = self._create_approved_carousel_idea()
        scenario = self._create_carousel_scenario(idea.idea_id)
        scenario_before = scenario.model_dump(mode="json")
        with self.assertRaises(ScenarioStudioValidationError):
            self._create_carousel_scenario(idea.idea_id)
        self.assertEqual(len(self.scenario_repository.list_scenarios("example")), 1)
        self.assertEqual(
            self.scenario_service.get_scenario("example", scenario.scenario_id).model_dump(mode="json"),
            scenario_before,
        )
        self.assertEqual(self.idea_service.get_idea("example", idea.idea_id).status, IdeaStatus.SCRIPTED)

        other_scenario = Scenario(
            scenario_id="scenario_other_project",
            workspace_id="workspace_default",
            project_id="second",
            idea_id=idea.idea_id,
            brand_profile_id="brand_second",
            title="Other project scenario",
            content_format=ContentFormat.INSTAGRAM_CAROUSEL,
        )
        self.scenario_repository.save_scenario(other_scenario)
        isolated_idea = self._create_approved_carousel_idea(project_id="second")
        created = self._create_carousel_scenario(isolated_idea.idea_id, project_id="second")
        self.assertEqual(created.project_id, "second")

    def _create_approved_carousel_idea(self, *, project_id: str = "example"):
        idea = self.idea_service.create_idea(
            project_id,
            title="A carousel title",
            description="This description must not become carousel blocks.",
            content_format=ContentFormat.INSTAGRAM_CAROUSEL,
        )
        return self.idea_service.approve_idea(project_id, idea.idea_id)

    @staticmethod
    def _carousel_blocks() -> list[ScenarioTextBlock]:
        return [
            ScenarioTextBlock(block_id="body", order=2, role="body", text="Body text."),
            ScenarioTextBlock(block_id="quote", order=1, role="quote", text="Quote text."),
        ]

    def _create_carousel_scenario(
        self,
        idea_id: str,
        *,
        project_id: str = "example",
        target_platforms: object = _UNSET,
        blocks: object = _UNSET,
    ) -> Scenario:
        return self.scenario_service.create_from_idea(
            project_id,
            idea_id,
            target_platforms=(
                [PublishingPlatform.INSTAGRAM]
                if target_platforms is _UNSET
                else target_platforms
            ),
            blocks=self._carousel_blocks() if blocks is _UNSET else blocks,
        )

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
