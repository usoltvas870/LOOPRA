import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


RADAR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADAR_ROOT))

import refresh_tiktok_cookies as refresh


class CookieRefreshFileTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.cookie_path = self.root / 'tiktok_cookies.json'
        self.cookie_path.write_text(json.dumps({'cookies': [{'domain': '.tiktok.com'}], 'origins': []}), encoding='utf-8')
        self.pending_path = self.root / 'pending.json'
        self.backup_dir = self.root / 'backups'
        self.pending_patch = patch.object(refresh, 'PENDING_PATH', self.pending_path)
        self.backup_patch = patch.object(refresh, 'BACKUP_DIR', self.backup_dir)
        self.pending_patch.start()
        self.backup_patch.start()

    def tearDown(self):
        self.pending_patch.stop()
        self.backup_patch.stop()
        self.directory.cleanup()

    def test_backup_matches_original(self):
        backup = refresh.create_backup(self.cookie_path)
        self.assertEqual(refresh.file_sha256(backup), refresh.file_sha256(self.cookie_path))

    def test_invalid_pending_is_rejected_without_replacing_cookie(self):
        original = refresh.file_sha256(self.cookie_path)
        self.pending_path.write_text('{}', encoding='utf-8')
        self.assertFalse(refresh.promote_pending(self.cookie_path, True, True))
        self.assertEqual(refresh.file_sha256(self.cookie_path), original)

    def test_failed_first_or_second_check_preserves_cookie(self):
        original = refresh.file_sha256(self.cookie_path)
        refresh.write_storage_state(self.pending_path, {'cookies': [{'domain': '.tiktok.com'}], 'origins': []})
        self.assertFalse(refresh.promote_pending(self.cookie_path, False, True))
        self.assertFalse(refresh.promote_pending(self.cookie_path, True, False))
        self.assertEqual(refresh.file_sha256(self.cookie_path), original)

    def test_valid_pending_is_atomically_promoted_only_after_two_checks(self):
        refresh.write_storage_state(self.pending_path, {'cookies': [{'domain': '.tiktok.com'}, {'domain': '.www.tiktok.com'}], 'origins': []})
        self.assertTrue(refresh.promote_pending(self.cookie_path, True, True))
        self.assertFalse(self.pending_path.exists())
        valid, count = refresh.storage_state_summary(self.cookie_path)
        self.assertTrue(valid)
        self.assertEqual(count, 2)

    def test_validation_does_not_include_cookie_values_in_reason(self):
        valid, reason = refresh.validate_storage_state({'cookies': [{'domain': '.example.com', 'value': 'secret'}], 'origins': []})
        self.assertFalse(valid)
        self.assertNotIn('secret', reason)
