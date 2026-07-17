from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from core.domain import ContentFormat, ProductionBrief, ProductionBriefStatus
from core.services.production_pipeline import FileSystemProductionBriefRepository


class ProductionBriefRepoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name)
        self.repo = FileSystemProductionBriefRepository(projects_root=self.projects_root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_repo_save_and_load_brief(self) -> None:
        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id="brief_001",
            scenario_id="scenario_001",
        )
        self.repo.save_brief(brief)
        loaded = self.repo.load_brief("nura", "brief_001")

        self.assertEqual(loaded.production_brief_id, brief.production_brief_id)
        self.assertEqual(loaded.scenario_id, brief.scenario_id)
        self.assertEqual(loaded.project_id, brief.project_id)
        self.assertEqual(loaded.status, ProductionBriefStatus.DRAFT)

    def test_repo_list_briefs(self) -> None:
        brief1 = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id="brief_1",
            scenario_id="scenario_1",
            created_at=datetime(2026, 1, 10, tzinfo=timezone.utc),
        )
        brief2 = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id="brief_2",
            scenario_id="scenario_2",
            created_at=datetime(2026, 1, 20, tzinfo=timezone.utc),
        )
        brief3 = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id="brief_3",
            scenario_id="scenario_3",
            created_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
        )

        self.repo.save_brief(brief1)
        self.repo.save_brief(brief2)
        self.repo.save_brief(brief3)

        briefs = self.repo.list_briefs("nura")
        self.assertEqual(len(briefs), 3)
        self.assertEqual(briefs[0].production_brief_id, "brief_2")
        self.assertEqual(briefs[1].production_brief_id, "brief_3")
        self.assertEqual(briefs[2].production_brief_id, "brief_1")

    def test_repo_load_nonexistent(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.repo.load_brief("nura", "nonexistent_id")

    def test_repo_save_updates_existing(self) -> None:
        brief = ProductionBrief(
            workspace_id="internal",
            project_id="nura",
            production_brief_id="brief_001",
            scenario_id="scenario_001",
        )
        self.repo.save_brief(brief)

        loaded = self.repo.load_brief("nura", "brief_001")
        updated = ProductionBrief.model_validate({
            **loaded.model_dump(),
            "scenario_id": "scenario_updated",
            "status": "validated",
        })
        self.repo.save_brief(updated)

        reloaded = self.repo.load_brief("nura", "brief_001")
        self.assertEqual(reloaded.scenario_id, "scenario_updated")
        self.assertEqual(reloaded.status, ProductionBriefStatus.VALIDATED)
