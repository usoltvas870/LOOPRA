from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from core.domain import (
    ContentOpportunityStatus,
    IdeaStatus,
    MarketSignalStatus,
    ScenarioStatus,
    TrendPatternStatus,
)
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

    def test_market_signal_get_list_filter_review_and_project_isolation(self) -> None:
        first = self._create_signal("example", title="First signal")
        second = self._create_signal("example", title="Second signal")
        other_project = self._create_signal("second", title="Other project signal")

        reviewed = self.service.review_market_signal("example", first.market_signal_id)

        self.assertEqual(reviewed.status, MarketSignalStatus.REVIEWED)
        self.assertEqual(
            self.service.get_market_signal("example", first.market_signal_id),
            reviewed,
        )
        self.assertEqual(
            {signal.market_signal_id for signal in self.service.list_market_signals("example")},
            {first.market_signal_id, second.market_signal_id},
        )
        self.assertEqual(
            [signal.market_signal_id for signal in self.service.list_market_signals(
                "example", status=MarketSignalStatus.REVIEWED
            )],
            [first.market_signal_id],
        )
        self.assertEqual(
            [signal.market_signal_id for signal in self.service.list_market_signals(
                "example", status=MarketSignalStatus.NEW
            )],
            [second.market_signal_id],
        )
        with self.assertRaises(FileNotFoundError):
            self.service.get_market_signal("example", "signal_missing")
        with self.assertRaises(FileNotFoundError):
            self.service.get_market_signal("example", other_project.market_signal_id)

    def test_trend_pattern_get_list_filter_activation_and_project_isolation(self) -> None:
        first_signal = self._create_signal("example", title="First signal")
        second_signal = self._create_signal("example", title="Second signal")
        first = self._create_pattern("example", first_signal.market_signal_id, title="First pattern")
        second = self._create_pattern("example", second_signal.market_signal_id, title="Second pattern")
        other_signal = self._create_signal("second", title="Other project signal")
        other_project = self._create_pattern(
            "second",
            other_signal.market_signal_id,
            title="Other project pattern",
        )

        active = self.service.activate_trend_pattern("example", first.trend_pattern_id)

        self.assertEqual(active.status, TrendPatternStatus.ACTIVE)
        self.assertEqual(
            self.service.get_trend_pattern("example", first.trend_pattern_id),
            active,
        )
        self.assertEqual(
            {pattern.trend_pattern_id for pattern in self.service.list_trend_patterns("example")},
            {first.trend_pattern_id, second.trend_pattern_id},
        )
        self.assertEqual(
            [pattern.trend_pattern_id for pattern in self.service.list_trend_patterns(
                "example", status=TrendPatternStatus.ACTIVE
            )],
            [first.trend_pattern_id],
        )
        self.assertEqual(
            [pattern.trend_pattern_id for pattern in self.service.list_trend_patterns(
                "example", status=TrendPatternStatus.DRAFT
            )],
            [second.trend_pattern_id],
        )
        with self.assertRaises(FileNotFoundError):
            self.service.get_trend_pattern("example", "trend_missing")
        with self.assertRaises(FileNotFoundError):
            self.service.get_trend_pattern("example", other_project.trend_pattern_id)

    def test_content_opportunity_get_list_filter_and_project_isolation(self) -> None:
        _, pattern, first = self._create_flow("example")
        second = self._create_opportunity(
            "example",
            pattern.trend_pattern_id,
            title="Second opportunity",
        )
        _, _, other_project = self._create_flow("second")

        approved = self.service.approve_content_opportunity("example", first.content_opportunity_id)

        self.assertEqual(
            self.service.get_content_opportunity("example", first.content_opportunity_id),
            approved,
        )
        self.assertEqual(
            {item.content_opportunity_id for item in self.service.list_content_opportunities("example")},
            {first.content_opportunity_id, second.content_opportunity_id},
        )
        self.assertEqual(
            [item.content_opportunity_id for item in self.service.list_content_opportunities(
                "example", status=ContentOpportunityStatus.APPROVED
            )],
            [first.content_opportunity_id],
        )
        self.assertEqual(
            [item.content_opportunity_id for item in self.service.list_content_opportunities(
                "example", status=ContentOpportunityStatus.DRAFT
            )],
            [second.content_opportunity_id],
        )
        with self.assertRaises(FileNotFoundError):
            self.service.get_content_opportunity("example", "opportunity_missing")
        with self.assertRaises(FileNotFoundError):
            self.service.get_content_opportunity("example", other_project.content_opportunity_id)

    def test_reject_defer_and_archive_content_opportunities(self) -> None:
        _, pattern, rejected_source = self._create_flow("example")
        deferred_source = self._create_opportunity(
            "example",
            pattern.trend_pattern_id,
            title="Deferred opportunity",
        )
        archived_source = self._create_opportunity(
            "example",
            pattern.trend_pattern_id,
            title="Archived opportunity",
        )

        rejected = self.service.reject_content_opportunity(
            "example", rejected_source.content_opportunity_id
        )
        deferred = self.service.defer_content_opportunity(
            "example", deferred_source.content_opportunity_id
        )
        archived = self.service.archive_content_opportunity(
            "example", archived_source.content_opportunity_id
        )

        self.assertEqual(rejected.status, ContentOpportunityStatus.REJECTED)
        self.assertEqual(deferred.status, ContentOpportunityStatus.DEFERRED)
        self.assertEqual(archived.status, ContentOpportunityStatus.ARCHIVED)

    def test_duplicate_opportunity_conversion_is_rejected(self) -> None:
        _, _, opportunity = self._create_flow("example")
        approved = self.service.approve_content_opportunity("example", opportunity.content_opportunity_id)
        first_idea = self.service.create_idea_from_opportunity("example", approved.content_opportunity_id)

        with self.assertRaisesRegex(
            ContentIntelligenceValidationError,
            "must be approved before conversion",
        ):
            self.service.create_idea_from_opportunity("example", approved.content_opportunity_id)

        self.assertEqual(len(self.idea_service.list_ideas("example")), 1)
        self.assertEqual(self.idea_service.list_ideas("example")[0].idea_id, first_idea.idea_id)

    def test_nura_validation_flow_is_project_scoped_without_core_branching(self) -> None:
        signal, pattern, opportunity = self._create_flow("nura")
        self.assertEqual(signal.project_id, "nura")
        self.assertEqual(pattern.project_id, "nura")
        self.assertEqual(opportunity.project_id, "nura")
        core_text = Path("core/services/intelligence.py").read_text(encoding="utf-8").lower()
        self.assertNotIn('project_id == "nura"', core_text)
        self.assertNotIn("project_id == 'nura'", core_text)

    def _create_flow(self, project_id: str):
        signal = self._create_signal(project_id)
        pattern = self._create_pattern(project_id, signal.market_signal_id)
        opportunity = self._create_opportunity(
            project_id,
            pattern.trend_pattern_id,
            evidence=[signal.market_signal_id, pattern.trend_pattern_id],
        )
        return signal, pattern, opportunity

    def _create_signal(self, project_id: str, *, title: str = "Short reflective posts are getting saves"):
        return self.service.create_market_signal(
            project_id,
            title=title,
            description="Manual operator observation; no scraping involved.",
            source_type="manual",
            audience_hint="self-development audience",
            platform_hint="telegram",
            content_format_hint="text_social_post",
            tags=["manual", "reflection"],
            confidence=0.7,
        )

    def _create_pattern(
        self,
        project_id: str,
        market_signal_id: str,
        *,
        title: str = "Reflective educational micro-posts",
    ):
        return self.service.create_trend_pattern(
            project_id,
            title=title,
            summary="Audience responds to calm explanatory reflection prompts.",
            market_signal_ids=[market_signal_id],
            affected_audience="self-development audience",
            related_platforms=["telegram"],
            related_formats=["text_social_post"],
            relevance_score=0.8,
            confidence=0.7,
        )

    def _create_opportunity(
        self,
        project_id: str,
        trend_pattern_id: str,
        *,
        title: str = "Explain one repeating pattern gently",
        evidence: list[str] | None = None,
    ):
        return self.service.create_content_opportunity(
            project_id,
            trend_pattern_id=trend_pattern_id,
            title=title,
            summary="Recommend a calm post angle based on the pattern.",
            target_audience="self-development audience",
            content_format="text_social_post",
            funnel_stage="trust",
            content_pillar="self-understanding",
            strategic_goal="increase saves",
            recommended_angle="Frame as reflection, not prediction.",
            evidence=evidence or [trend_pattern_id],
            confidence=0.7,
            score=0.82,
        )

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
