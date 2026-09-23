import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from text_buffer import TextBuffer


class TestTextBufferAutosaveWiring(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        # Patch auto_save_manager's config so backups go to temp_dir
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

    def test_textbuffer_has_auto_save_manager(self):
        tb = TextBuffer()
        self.assertTrue(hasattr(tb, "auto_save_manager"))
        self.assertIsNotNone(tb.auto_save_manager)

    def test_set_filename_starts_autosave(self):
        tb = TextBuffer()
        tb.auto_save_manager.start_autosave = MagicMock()

        tb.set_filename("/tmp/some_file.txt")

        self.assertEqual(tb.buffer_manager.filename, "/tmp/some_file.txt")
        tb.auto_save_manager.start_autosave.assert_called_once()

    def test_load_file_starts_autosave(self):
        f = Path(self.temp_dir) / "load_me.txt"
        f.write_text("hello\nworld")

        tb = TextBuffer()
        # Silence hook side-effects
        tb.hook_utils.execute_pre_load = MagicMock(return_value=None)
        tb.hook_utils.execute_post_load = MagicMock(return_value=[])
        tb.hook_utils.execute_editing_handlers = MagicMock(return_value=None)
        tb.auto_save_manager.start_autosave = MagicMock()

        ok = tb.load_file(str(f))

        self.assertTrue(ok)
        tb.auto_save_manager.start_autosave.assert_called_once()

    def test_save_restarts_autosave(self):
        tb = TextBuffer()
        tb.hook_utils.execute_pre_save = MagicMock(return_value=None)
        tb.hook_utils.execute_post_save = MagicMock(return_value=[])
        tb.hook_utils.execute_editing_handlers = MagicMock(return_value=None)

        f = Path(self.temp_dir) / "save_me.txt"
        tb.buffer_manager.filename = str(f)
        tb.buffer_manager.lines = ["a", "b"]
        tb.buffer_manager.dirty = True

        tb.auto_save_manager.start_autosave = MagicMock()
        ok = tb.save()

        self.assertTrue(ok)
        tb.auto_save_manager.start_autosave.assert_called_once()

    def test_get_available_backups_no_filename(self):
        tb = TextBuffer()
        tb.buffer_manager.filename = None
        self.assertEqual(tb.get_available_backups(), [])

    def test_get_available_backups_delegates(self):
        tb = TextBuffer()
        tb.buffer_manager.filename = "/tmp/x.txt"
        tb.auto_save_manager.get_backup_files = MagicMock(return_value=["a", "b"])
        result = tb.get_available_backups()
        self.assertEqual(result, ["a", "b"])

    def test_restore_from_backup_delegates(self):
        tb = TextBuffer()
        tb.auto_save_manager.restore_from_backup = MagicMock(return_value=True)
        ok = tb.restore_from_backup("/tmp/backup.txt")
        self.assertTrue(ok)
        tb.auto_save_manager.restore_from_backup.assert_called_once_with(
            "/tmp/backup.txt", tb.buffer_manager
        )

    def test_open_backup_mode_instantiates_and_shows(self):
        tb = TextBuffer()
        tb._start_autosave_for_current_file = MagicMock()
        tb.display = MagicMock()

        # Replace the lazy BackupMode with a mock
        fake_bm = MagicMock()
        tb._backup_mode = fake_bm

        tb.open_backup_mode()

        tb._start_autosave_for_current_file.assert_called_once()
        fake_bm.show_backup_menu.assert_called_once()
        tb.display.assert_called_once()

    def test_b_key_triggers_open_backup_mode(self):
        """Pressing 'b' in edit_interactive should call open_backup_mode and then quit."""
        tb = TextBuffer()
        tb.display = MagicMock()
        tb.open_backup_mode = MagicMock()

        # Sequence: press 'b', then 'q' to quit (dirty=False, so quit short-circuits)
        with patch("text_buffer.TextLib.get_key_input", side_effect=["b", "q"]):
            tb.edit_interactive()

        tb.open_backup_mode.assert_called_once()


if __name__ == "__main__":
    unittest.main()
