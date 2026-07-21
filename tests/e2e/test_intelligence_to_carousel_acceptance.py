from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.run_intelligence_to_carousel_acceptance import run_acceptance, run_failure_smoke


class IntelligenceToCarouselAcceptanceTests(unittest.TestCase):
    def test_success_path_uses_real_services_renderer_qa_and_repositories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_acceptance(Path(temporary))

        self.assertTrue(result["success"])
        self.assertEqual(result["statuses"], {
            "opportunity": "converted",
            "idea": "scripted",
            "scenario": "approved",
            "production_brief": "validated",
            "render_job": "rendered",
        })
        self.assertEqual(result["rendered_png_count"], 5)
        self.assertEqual(result["output_file_count"], 5)
        self.assertTrue(result["checks"]["qa_passed"])
        self.assertTrue(result["checks"]["all_traceability_links_valid"])
        for output in result["output_files"]:
            self.assertEqual((output["width"], output["height"]), (1080, 1350))
            self.assertEqual(output["mime_type"], "image/png")
            self.assertGreater(output["size_bytes"], 0)
            self.assertEqual(len(output["sha256"]), 64)

    def test_needs_review_scenario_cannot_create_downstream_records(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_failure_smoke(Path(temporary))

        self.assertIn("must be approved", result["error"])
        self.assertEqual(result["scenario_status"], "needs_review")
        self.assertEqual(result["production_brief_count"], 0)
        self.assertEqual(result["render_job_count"], 0)
        self.assertEqual(result["output_file_count"], 0)
