from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from core.domain import ContentOpportunityStatus, IdeaStatus, ScenarioStatus
from core.services import (
    BrandProfileService,
    ContentIntelligenceValidationError,
    FileSystemContentOpportunityRepository,
    FileSystemIdeaRepository,
    FileSystemMarketSignalRepository,
    FileSystemProjectRepository,
    FileSystemScenarioRepository,
    FileSystemTrendPatternRepository,
    IdeaService,
    ProjectService,
    ScenarioService,
    ContentIntelligenceService,
)


class ContentIntelligenceServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name)
        self._write_project_fixture("example")
        self._write_project_fixture("second")
        self._write_real_project_fixture("nura")
        project_repo = FileSystemProjectRepository(self.projects_root)
        self.project_service = ProjectService(project_repo)
        self.idea_repo = FileSystemIdeaRepository(self.projects_root)
        self.idea_service = IdeaService(self.idea_repo, self.project_service)
        self.service = ContentIntelligenceService(
            FileSystemMarketSignalRepository(self.projects_root),
            FileSystemTrendPatternRepository(self.projects_root),
            FileSystemContentOpportunityRepository(self.projects_root),
            self.project_service,
            self.idea_service,
        )
        self.scenario_service = ScenarioService(
            FileSystemScenarioRepository(self.projects_root),
            project_repo,
            self.project_service,
            BrandProfileService(project_repo),
            self.idea_service,
            self.idea_repo,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_full_stage_2_slice_flow_converts_approved_opportunity_to_idea(self) -> None:
        signal, pattern, opportunity = self._create_flow("example")
        approved = self.service.approve_content_opportunity("example", opportunity.content_opportunity_id)
        idea = self.service.create_idea_from_opportunity("example", approved.content_opportunity_id)
        stored = self.service.get_content_opportunity("example", opportunity.content_opportunity_id)

        self.assertEqual(stored.status, ContentOpportunityStatus.CONVERTED)
        self.assertEqual(stored.idea_id, idea.idea_id)
        self.assertEqual(idea.source_type, "trend")
        self.assertEqual(idea.source_id, opportunity.content_opportunity_id)
        self.assertEqual(idea.status, IdeaStatus.RAW)
        approved_idea = self.idea_service.approve_idea("example", idea.idea_id)
        scenario = self.scenario_service.create_from_idea("example", approved_idea.idea_id)
        self.assertEqual(scenario.status, ScenarioStatus.NEEDS_REVIEW)
        self.assertEqual(signal.project_id, pattern.project_id)

    def test_rejects_missing_or_cross_project_signal_references(self) -> None:
        signal = self.service.create_market_signal(
            "second",
            title="Signal in second project",
            description="Should not be available in example.",
        )
        with self.assertRaises(FileNotFoundError):
            self.service.create_trend_pattern(
                "example",
                title="Cross project",
                summary="Invalid reference.",
                market_signal_ids=[signal.market_signal_id],
            )
        with self.assertRaises(ContentIntelligenceValidationError):
            self.service.create_trend_pattern("example", title="Missing", summary="No signals.", market_signal_ids=[])

    def test_unapproved_opportunity_cannot_convert_to_idea(self) -> None:
        _, _, opportunity = self._create_flow("example")
        with self.assertRaises(ContentIntelligenceValidationError):
            self.service.create_idea_from_opportunity("example", opportunity.content_opportunity_id)

    def test_nura_validation_flow_is_project_scoped_without_core_branching(self) -> None:
        signal, pattern, opportunity = self._create_flow("nura")
        self.assertEqual(signal.project_id, "nura")
        self.assertEqual(pattern.project_id, "nura")
        self.assertEqual(opportunity.project_id, "nura")
        core_text = Path("core/services/intelligence.py").read_text(encoding="utf-8").lower()
        self.assertNotIn('project_id == "nura"', core_text)
        self.assertNotIn("project_id == 'nura'", core_text)

    def _create_flow(self, project_id: str):
        signal = self.service.create_market_signal(
            project_id,
            title="Short reflective posts are getting saves",
            description="Manual operator observation; no scraping involved.",
            source_type="manual",
            audience_hint="self-development audience",
            platform_hint="telegram",
            content_format_hint="text_social_post",
            tags=["manual", "reflection"],
            confidence=0.7,
        )
        pattern = self.service.create_trend_pattern(
            project_id,
            title="Reflective educational micro-posts",
            summary="Audience responds to calm explanatory reflection prompts.",
            market_signal_ids=[signal.market_signal_id],
            affected_audience="self-development audience",
            related_platforms=["telegram"],
            related_formats=["text_social_post"],
            relevance_score=0.8,
            confidence=0.7,
        )
        opportunity = self.service.create_content_opportunity(
            project_id,
            trend_pattern_id=pattern.trend_pattern_id,
            title="Explain one repeating pattern gently",
            summary="Recommend a calm post angle based on the pattern.",
            target_audience="self-development audience",
            content_format="text_social_post",
            funnel_stage="trust",
            content_pillar="self-understanding",
            strategic_goal="increase saves",
            recommended_angle="Frame as reflection, not prediction.",
            evidence=[signal.market_signal_id, pattern.trend_pattern_id],
            confidence=0.7,
            score=0.82,
        )
        return signal, pattern, opportunity

    def _write_project_fixture(self, project_id: str) -> None:
        payload = json.loads(Path("projects/example/project.yaml").read_text(encoding="utf-8"))
        payload["project_id"] = project_id
        payload["project_name"] = f"{project_id.title()} Project"
        payload["project_slug"] = project_id
        payload["brand"]["brand_name"] = f"{project_id.title()} Brand"
        project_dir = self.projects_root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "project.yaml").write_text(json.dumps(payload), encoding="utf-8")

    def _write_real_project_fixture(self, project_id: str) -> None:
        project_dir = self.projects_root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path("projects") / project_id / "project.yaml", project_dir / "project.yaml")


if __name__ == "__main__":
    unittest.main()
