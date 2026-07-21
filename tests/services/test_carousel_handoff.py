from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.domain import ContentFormat, Idea, IdeaStatus, Scenario, ScenarioStatus
from core.services import (
    FileSystemIdeaRepository,
    FileSystemProductionBriefRepository,
    ScenarioToCarouselBriefValidationError,
    build_scenario_to_carousel_brief_service,
)


class ScenarioToCarouselBriefServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name)
        self._write_project("example", colors={"primary": "#123456", "accent": "#abcdef"}, fonts={"heading": "Heading", "body": "Body"})
        self._write_project("other")
        self.service = build_scenario_to_carousel_brief_service(self.projects_root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_creates_validated_deterministic_persisted_brief_without_mutating_scenario(self) -> None:
        scenario = self._write_scenario("example", blocks=[
            {"block_id": "body", "order": 2, "role": "body", "text": "Body text"},
            {"block_id": "cta", "order": 3, "role": "cta", "text": "Save this post"},
            {"block_id": "quote", "order": 1, "role": "quote", "text": "Quote text"},
        ])
        original = scenario.model_dump(mode="json")

        brief = self.service.create_brief("example", scenario.scenario_id)
        persisted = FileSystemProductionBriefRepository(self.projects_root).load_brief("example", brief.production_brief_id)

        self.assertEqual(brief.status.value, "validated")
        self.assertEqual(brief.scenario_id, scenario.scenario_id)
        self.assertEqual(FileSystemIdeaRepository(self.projects_root).load_idea("example", scenario.idea_id).source_id, "opportunity_example")
        self.assertEqual((brief.workspace_id, brief.project_id), (scenario.workspace_id, scenario.project_id))
        self.assertEqual(brief.content_format, ContentFormat.INSTAGRAM_CAROUSEL)
        self.assertEqual(brief.production_variant, "scenario_carousel_v1")
        self.assertEqual([platform.value for platform in brief.target_platforms], ["instagram"])
        self.assertEqual((brief.output.aspect_ratio, brief.output.resolution_width, brief.output.resolution_height), ("4:5", 1080, 1350))
        self.assertEqual([(slide.slide_number, slide.template, slide.body, slide.cta) for slide in brief.slides], [
            (1, "cover", "", ""), (2, "quote", "Quote text", ""),
            (3, "text_image", "Body text", ""), (4, "cta", "", "Save this post"),
        ])
        self.assertEqual(brief.slides[0].heading, scenario.title)
        self.assertEqual(brief.brand.colors_primary, "#123456")
        self.assertEqual(brief.brand.colors_accent, "#abcdef")
        self.assertEqual(brief.brand.fonts_heading, "Heading")
        self.assertEqual(persisted, brief)
        self.assertEqual(self._load_scenario("example", scenario.scenario_id).model_dump(mode="json"), original)

    def test_rejects_non_approved_scenarios(self) -> None:
        for status in (ScenarioStatus.DRAFT, ScenarioStatus.NEEDS_REVIEW, ScenarioStatus.REJECTED):
            scenario = self._write_scenario("example", status=status)
            with self.subTest(status=status.value), self.assertRaisesRegex(ScenarioToCarouselBriefValidationError, "must be approved"):
                self.service.create_brief("example", scenario.scenario_id)

    def test_rejects_non_carousel_format(self) -> None:
        for content_format in (ContentFormat.TEXT_SOCIAL_POST, ContentFormat.SHORT_VERTICAL_VIDEO):
            scenario = self._write_scenario("example", content_format=content_format)
            with self.subTest(content_format=content_format.value), self.assertRaisesRegex(ScenarioToCarouselBriefValidationError, "instagram_carousel"):
                self.service.create_brief("example", scenario.scenario_id)

    def test_rejects_incompatible_blocks(self) -> None:
        cases = {
            "empty": [],
            "empty_text": [{"block_id": "one", "order": 1, "role": "body", "text": " "}],
            "duplicate_order": [{"block_id": "one", "order": 1, "role": "body", "text": "One"}, {"block_id": "two", "order": 1, "role": "body", "text": "Two"}],
            "duplicate_id": [{"block_id": "one", "order": 1, "role": "body", "text": "One"}, {"block_id": "one", "order": 2, "role": "body", "text": "Two"}],
            "unsupported_role": [{"block_id": "one", "order": 1, "role": "post_body", "text": "One"}],
        }
        for name, blocks in cases.items():
            scenario = self._write_scenario("example", blocks=blocks)
            with self.subTest(case=name), self.assertRaises(ScenarioToCarouselBriefValidationError):
                self.service.create_brief("example", scenario.scenario_id)

    def test_duplicate_handoff_is_rejected_without_second_record(self) -> None:
        scenario = self._write_scenario("example")
        self.service.create_brief("example", scenario.scenario_id)
        with self.assertRaisesRegex(ScenarioToCarouselBriefValidationError, "already has carousel brief"):
            self.service.create_brief("example", scenario.scenario_id)
        self.assertEqual(len(FileSystemProductionBriefRepository(self.projects_root).list_briefs("example")), 1)

    def test_project_isolation_for_scenario_and_duplicate_detection(self) -> None:
        foreign = self._write_scenario("other")
        with self.assertRaises(FileNotFoundError):
            self.service.create_brief("example", foreign.scenario_id)
        current = self._write_scenario("example", scenario_id="scenario_shared")
        self._write_scenario("other", scenario_id="scenario_shared")
        build_scenario_to_carousel_brief_service(self.projects_root).create_brief("other", "scenario_shared")
        self.assertEqual(self.service.create_brief("example", current.scenario_id).project_id, "example")

    def test_missing_required_brand_profile_data_is_rejected(self) -> None:
        self._write_project("incomplete", positioning="")
        scenario = self._write_scenario("incomplete")
        with self.assertRaisesRegex(ValueError, "brand.positioning"):
            self.service.create_brief("incomplete", scenario.scenario_id)

    def _write_project(self, project_id: str, *, positioning: str = "Useful positioning.", colors: dict[str, str] | None = None, fonts: dict[str, str] | None = None) -> None:
        project_dir = self.projects_root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "workspace_id": "workspace_test", "project_id": project_id, "project_name": f"{project_id} project", "project_slug": project_id,
            "status": "active", "primary_url": "https://brand.test",
            "brand": {"brand_name": f"{project_id} brand", "positioning": positioning, "audience_summary": "A defined audience.", "language": "en", "tone_of_voice": {"tone_summary": "Clear and calm."}, "colors": colors or {}, "fonts": fonts or {}},
        }
        (project_dir / "project.yaml").write_text(json.dumps(payload), encoding="utf-8")

    def _write_scenario(self, project_id: str, *, scenario_id: str | None = None, status: ScenarioStatus = ScenarioStatus.APPROVED, content_format: ContentFormat = ContentFormat.INSTAGRAM_CAROUSEL, blocks: list[dict[str, object]] | None = None) -> Scenario:
        scenario_dir = self.projects_root / project_id / "data" / "scenarios"
        scenario_dir.mkdir(parents=True, exist_ok=True)
        idea_id = f"idea_{project_id}"
        idea_repository = FileSystemIdeaRepository(self.projects_root)
        if not idea_repository.list_ideas(project_id):
            idea_repository.save_idea(Idea(
                idea_id=idea_id,
                workspace_id="workspace_test",
                project_id=project_id,
                title="Traceable idea",
                source_type="trend",
                source_id=f"opportunity_{project_id}",
                status=IdeaStatus.APPROVED,
            ))
        scenario = Scenario(
            scenario_id=scenario_id or f"scenario_{project_id}_{len(list(scenario_dir.glob('*.json')))}", workspace_id="workspace_test", project_id=project_id,
            idea_id=idea_id, brand_profile_id=f"brand_{project_id}", source_type="idea", source_id=idea_id,
            title="Exact carousel title", content_format=content_format, target_platforms=["instagram"],
            blocks=blocks if blocks is not None else [{"block_id": "body", "order": 1, "role": "body", "text": "Exact block text"}], status=status,
        )
        (scenario_dir / f"{scenario.scenario_id}.json").write_text(json.dumps(scenario.model_dump(mode="json")), encoding="utf-8")
        return scenario

    def _load_scenario(self, project_id: str, scenario_id: str) -> Scenario:
        payload = json.loads((self.projects_root / project_id / "data" / "scenarios" / f"{scenario_id}.json").read_text(encoding="utf-8"))
        return Scenario.model_validate(payload)
