from __future__ import annotations

import unittest

from pydantic import ValidationError

from core.domain import (
    ContentOpportunity,
    ContentOpportunityStatus,
    DomainModule,
    InvalidStatusTransitionError,
    MarketSignal,
    MarketSignalStatus,
    TrendPattern,
    TrendPatternStatus,
)


class IntelligenceDomainModelTests(unittest.TestCase):
    def test_market_signal_requires_project_scope_and_valid_confidence(self) -> None:
        signal = MarketSignal(
            market_signal_id="signal_1",
            workspace_id="internal",
            project_id="example",
            title="Reflective reels are saved",
            description="Manual observation from operator review.",
            confidence=0.8,
        )
        self.assertEqual(signal.owner_module, DomainModule.CONTENT_INTELLIGENCE)
        self.assertEqual(signal.status, MarketSignalStatus.NEW)

        with self.assertRaises(ValidationError):
            MarketSignal(
                market_signal_id="signal_2",
                workspace_id="internal",
                project_id="",
                title="Broken",
                description="Missing project.",
            )
        with self.assertRaises(ValidationError):
            MarketSignal(
                market_signal_id="signal_3",
                workspace_id="internal",
                project_id="example",
                title="Broken",
                description="Bad confidence.",
                confidence=1.1,
            )

    def test_trend_pattern_status_transitions_are_bounded(self) -> None:
        pattern = TrendPattern(
            trend_pattern_id="trend_1",
            workspace_id="internal",
            project_id="example",
            title="Soft educational short posts",
            summary="Manual interpretation of one signal.",
            market_signal_ids=["signal_1"],
        )
        active = pattern.transition_to(TrendPatternStatus.ACTIVE)
        self.assertEqual(active.status, TrendPatternStatus.ACTIVE)
        with self.assertRaises(InvalidStatusTransitionError):
            active.transition_to(TrendPatternStatus.DRAFT)

    def test_content_opportunity_status_transitions_and_scores_are_bounded(self) -> None:
        opportunity = ContentOpportunity(
            content_opportunity_id="opportunity_1",
            workspace_id="internal",
            project_id="example",
            trend_pattern_id="trend_1",
            title="Create a reflective explanation post",
            summary="Use trend evidence as a recommendation only.",
            score=0.75,
        )
        approved = opportunity.transition_to(ContentOpportunityStatus.APPROVED)
        converted = approved.transition_to(ContentOpportunityStatus.CONVERTED, idea_id="idea_1")
        self.assertEqual(converted.idea_id, "idea_1")
        with self.assertRaises(InvalidStatusTransitionError):
            converted.transition_to(ContentOpportunityStatus.APPROVED)
        with self.assertRaises(ValidationError):
            ContentOpportunity(
                content_opportunity_id="opportunity_2",
                workspace_id="internal",
                project_id="example",
                trend_pattern_id="trend_1",
                title="Broken",
                summary="Bad score.",
                score=-0.1,
            )

    def test_converted_content_opportunity_requires_non_empty_idea_id(self) -> None:
        opportunity = ContentOpportunity(
            content_opportunity_id="opportunity_1",
            workspace_id="internal",
            project_id="example",
            trend_pattern_id="trend_1",
            title="Create a reflective explanation post",
            summary="Use trend evidence as a recommendation only.",
        ).transition_to(ContentOpportunityStatus.APPROVED)

        for idea_id in (None, "", "   "):
            with self.subTest(idea_id=idea_id):
                with self.assertRaisesRegex(ValueError, "requires a non-empty idea_id"):
                    opportunity.transition_to(ContentOpportunityStatus.CONVERTED, idea_id=idea_id)

        converted = opportunity.transition_to(ContentOpportunityStatus.CONVERTED, idea_id="  idea_1  ")
        self.assertEqual(converted.idea_id, "idea_1")


if __name__ == "__main__":
    unittest.main()
