import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from backup_mode import BackupMode


class TestBackupMode(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        # Build a fake TextBuffer that BackupMode expects
        self.tb = MagicMock()
        self.tb.buffer_manager.filename = os.path.join(self.temp_dir, "target.txt")
        self.tb.buffer_manager.lines = ["current line 1", "current line 2"]
        self.tb.auto_save_manager.backup_dir = Path(self.temp_dir)

        self.bm = BackupMode(self.tb)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_refresh_backups_delegates_to_textbuffer(self):
        fake_paths = [Path(self.temp_dir) / "a.~1~.txt", Path(self.temp_dir) / "a.~2~.txt"]
        self.tb.get_available_backups = MagicMock(return_value=fake_paths)

        self.bm._refresh_backups()
        self.assertEqual(self.bm.backups, fake_paths)
        self.tb.get_available_backups.assert_called_once()

    def test_restore_delegates_to_textbuffer(self):
        backup_path = Path(self.temp_dir) / "target.~123~.txt"
        backup_path.write_text("old content")
        self.bm.backups = [backup_path]

        self.tb.restore_from_backup = MagicMock(return_value=True)

        with patch("builtins.input", side_effect=["1", "y"]):
            self.bm._restore_backup()

        self.tb.restore_from_backup.assert_called_once_with(str(backup_path))

    def test_restore_cancelled_by_user(self):
        backup_path = Path(self.temp_dir) / "target.~123~.txt"
        backup_path.write_text("old content")
        self.bm.backups = [backup_path]

        self.tb.restore_from_backup = MagicMock(return_value=True)

        with patch("builtins.input", side_effect=["1", "n"]):
            self.bm._restore_backup()

        self.tb.restore_from_backup.assert_not_called()

    def test_clean_old_backups_keeps_first_three(self):
        paths = []
        for i in range(5):
            p = Path(self.temp_dir) / f"target.~{i}~.txt"
            p.write_text(f"content {i}")
            paths.append(p)
        self.bm.backups = paths

        with patch("builtins.input", return_value="y"):
            self.bm._clean_old_backups()

        # Latest 3 (indices 0,1,2) should remain
        for p in paths[:3]:
            self.assertTrue(p.exists())
        # The rest should be gone
        for p in paths[3:]:
            self.assertFalse(p.exists())

    def test_clean_old_backups_skips_when_three_or_fewer(self):
        paths = [Path(self.temp_dir) / f"target.~{i}~.txt" for i in range(2)]
        for p in paths:
            p.write_text("x")
        self.bm.backups = paths

        with patch("builtins.input") as mock_input:
            self.bm._clean_old_backups()

        # No confirmation prompt should have been issued
        mock_input.assert_not_called()
        for p in paths:
            self.assertTrue(p.exists())

    def test_clean_all_backups_removes_everything(self):
        paths = []
        for i in range(4):
            p = Path(self.temp_dir) / f"target.~{i}~.txt"
            p.write_text(f"content {i}")
            paths.append(p)
        self.bm.backups = paths

        self.tb.get_available_backups = MagicMock(return_value=[])

        with patch("builtins.input", return_value="y"):
            self.bm._clean_all_backups()

        for p in paths:
            self.assertFalse(p.exists())


if __name__ == "__main__":
    unittest.main()
