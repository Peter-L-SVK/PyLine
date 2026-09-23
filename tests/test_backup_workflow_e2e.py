import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from text_buffer import TextBuffer


class TestBackupWorkflowE2E(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        # Point autosave's backup_dir at our temp dir
        self.cfg_patch = patch("auto_save_manager.config_manager")
        self.mock_cfg = self.cfg_patch.start()
        self.mock_cfg.get = MagicMock(
            side_effect=lambda key, default=None: {
                "autosave.interval_minutes": 3,
                "autosave.max_backups": 5,
                "paths.backup_dir": self.temp_dir,
                "autosave.notify": False,
            }.get(key, default)
        )

    def tearDown(self):
        self.cfg_patch.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_round_trip(self):
        # 1. Write an initial file on disk
        original = Path(self.temp_dir) / "project" / "main.py"
        original.parent.mkdir(parents=True, exist_ok=True)
        original.write_text("v1\nv2\nv3")

        # 2. Load it
        tb = TextBuffer()
        tb.hook_utils.execute_pre_load = MagicMock(return_value=None)
        tb.hook_utils.execute_post_load = MagicMock(return_value=[])
        tb.hook_utils.execute_editing_handlers = MagicMock(return_value=None)
        tb.auto_save_manager.backup_dir = Path(self.temp_dir)

        self.assertTrue(tb.load_file(str(original)))
        # Autosave should now be running
        self.assertTrue(tb.auto_save_manager._running)

        # 3. Modify the buffer, force an autosave
        tb.buffer_manager.lines = ["v1", "CHANGED", "v3"]
        tb.buffer_manager.dirty = True
        tb.auto_save_manager._perform_autosave(tb.buffer_manager, str(original))

        # 4. List backups — should have exactly one
        backups = tb.get_available_backups()
        self.assertEqual(len(backups), 1)
        self.assertIn(".~", backups[0].name)

        # 5. Modify again, force a second autosave
        tb.buffer_manager.lines = ["v1", "CHANGED", "v3", "v4"]
        tb.auto_save_manager._perform_autosave(tb.buffer_manager, str(original))

        # 6. Now two backups, newest first
        backups = tb.get_available_backups()
        self.assertEqual(len(backups), 2)
        # The newest backup should contain "v4"
        newest = backups[0].read_text()
        self.assertIn("v4", newest)

        # 7. Restore from the OLDER backup
        older = backups[1]
        self.assertTrue(tb.restore_from_backup(str(older)))
        self.assertNotIn("v4", tb.buffer_manager.lines)
        self.assertEqual(tb.buffer_manager.lines, ["v1", "CHANGED", "v3"])

        # 8. Stop autosave cleanly
        tb.auto_save_manager.stop_autosave()
        self.assertFalse(tb.auto_save_manager._running)


if __name__ == "__main__":
    unittest.main()
