import json
import sys
import tempfile
import unittest
from pathlib import Path


RADAR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADAR_ROOT))

import run_acceptance


class AcceptanceRunnerTests(unittest.TestCase):
    def test_security_scan_detects_secret_markers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'safe.json').write_text('{"result":"success"}', encoding='utf-8')
            self.assertEqual(run_acceptance._scan_evidence(root, []), [])
            (root / 'bad.txt').write_text('Authorization: secret', encoding='utf-8')
            self.assertTrue(run_acceptance._scan_evidence(root, []))

    def test_validation_rejects_missing_result_and_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'stdout.log').write_text('', encoding='utf-8')
            (root / 'journal').mkdir()
            (root / 'reports').mkdir()
            failures, summary = run_acceptance.validate_success_artifacts(
                root,
                {'exit_code': 1, 'timeout': False, 'termination_reason': 'normal_exit'},
            )
            self.assertTrue(failures)
            self.assertEqual(summary, {})

    def test_json_writer_produces_valid_utf8_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'result.json'
            run_acceptance._write_json(path, {'source': 'матрицасудьбы'})
            self.assertEqual(json.loads(path.read_text(encoding='utf-8'))['source'], 'матрицасудьбы')
