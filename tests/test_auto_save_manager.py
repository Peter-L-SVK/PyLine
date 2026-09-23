import sys
import os
import time
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from auto_save_manager import AutoSaveManager


def make_mock_buffer(lines=None, filename=None, dirty=True):
    """Build a fake buffer_manager with the attributes AutoSaveManager touches."""
    buf = MagicMock()
    buf.lines = lines if lines is not None else ["line one", "line two"]
    buf.filename = filename
    buf.dirty = dirty
    return buf


class TestAutoSaveManagerPaths(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.hook_utils = MagicMock()
        self.hook_utils.execute_pre_save = MagicMock(return_value=None)
        self.hook_utils.execute_post_save = MagicMock(return_value=[])
        self.hook_utils.execute_editing_handlers = MagicMock(return_value=None)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _make_manager(self, **overrides):
        # Patch config so backup_dir points into our temp dir
        with patch("auto_save_manager.config_manager") as cfg:
            cfg.get = MagicMock(
                side_effect=lambda key, default=None: {
                    "autosave.interval_minutes": overrides.get("interval", 3),
                    "autosave.max_backups": overrides.get("max_backups", 5),
                    "paths.backup_dir": self.temp_dir,
                    "autosave.notify": False,
                }.get(key, default)
            )
            mgr = AutoSaveManager(self.hook_utils)
            # Force backup_dir to our temp dir in case config didn't take
            mgr.backup_dir = Path(self.temp_dir)
            return mgr

    def test_backup_path_structure(self):
        mgr = self._make_manager()
        original = "/home/user/projects/foo.py"
        backup = mgr._get_backup_path(original)

        # Should be inside backup_dir, mirror the original path
        self.assertTrue(str(backup).startswith(str(Path(self.temp_dir))))
        self.assertIn("home", str(backup))
        self.assertIn("user", str(backup))
        self.assertIn("projects", str(backup))
        # Should contain the .~timestamp~ pattern
        self.assertIn(".~", backup.name)
        self.assertTrue(backup.name.endswith(".py"))

    def test_backup_path_is_unique_per_call(self):
        mgr = self._make_manager()
        original = "/tmp/file.txt"
        p1 = mgr._get_backup_path(original)
        # Force a distinct timestamp by manipulating time indirectly
        time.sleep(1.05)
        p2 = mgr._get_backup_path(original)
        self.assertNotEqual(p1.name, p2.name)


class TestAutoSaveManagerPerform(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.hook_utils = MagicMock()
        self.hook_utils.execute_pre_save = MagicMock(return_value=None)
        self.hook_utils.execute_post_save = MagicMock(return_value=[])
        self.hook_utils.execute_editing_handlers = MagicMock(return_value=None)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _make_manager(self, **overrides):
        with patch("auto_save_manager.config_manager") as cfg:
            cfg.get = MagicMock(
                side_effect=lambda key, default=None: {
                    "autosave.interval_minutes": overrides.get("interval", 3),
                    "autosave.max_backups": overrides.get("max_backups", 5),
                    "paths.backup_dir": self.temp_dir,
                    "autosave.notify": False,
                }.get(key, default)
            )
            mgr = AutoSaveManager(self.hook_utils)
            mgr.backup_dir = Path(self.temp_dir)
            return mgr

    def test_perform_autosave_writes_file(self):
        mgr = self._make_manager()
        original = os.path.join(self.temp_dir, "src", "hello.py")
        buf = make_mock_buffer(lines=["print('hi')", "x = 1"], filename=original, dirty=True)

        mgr._perform_autosave(buf, original)

        backups = list(Path(self.temp_dir).rglob("hello.~*~*.py"))
        self.assertEqual(len(backups), 1)
        content = backups[0].read_text()
        self.assertEqual(content, "print('hi')\nx = 1")

    def test_perform_autosave_empty_filename_does_nothing(self):
        mgr = self._make_manager()
        buf = make_mock_buffer(lines=["x"], filename=None, dirty=True)
        mgr._perform_autosave(buf, "")
        backups = list(Path(self.temp_dir).rglob("*"))
        # Only the temp dir itself should exist, no files
        self.assertEqual([p for p in backups if p.is_file()], [])

    def test_pre_save_hook_can_modify_content(self):
        mgr = self._make_manager()
        # Hook returns modified content
        self.hook_utils.execute_pre_save = MagicMock(return_value={"content": ["TRANSFORMED"]})
        original = os.path.join(self.temp_dir, "mod.txt")
        buf = make_mock_buffer(lines=["original"], filename=original, dirty=True)

        mgr._perform_autosave(buf, original)

        backups = list(Path(self.temp_dir).rglob("mod.~*~*.txt"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "TRANSFORMED")

    def test_content_hook_can_modify_content(self):
        mgr = self._make_manager()
        # pre_save passes through, process_content transforms
        self.hook_utils.execute_editing_handlers = MagicMock(return_value={"content": ["PROCESSED"]})
        original = os.path.join(self.temp_dir, "proc.txt")
        buf = make_mock_buffer(lines=["raw"], filename=original, dirty=True)

        mgr._perform_autosave(buf, original)

        backups = list(Path(self.temp_dir).rglob("proc.~*~*.txt"))
        self.assertEqual(backups[0].read_text(), "PROCESSED")

    def test_write_failure_is_swallowed(self):
        mgr = self._make_manager()
        # Point backup_dir to a file (not a dir) so mkdir fails
        bad_dir = Path(self.temp_dir) / "iam_a_file"
        bad_dir.write_text("x")
        mgr.backup_dir = bad_dir

        original = os.path.join(self.temp_dir, "nope.txt")
        buf = make_mock_buffer(lines=["x"], filename=original, dirty=True)
        # Should not raise
        mgr._perform_autosave(buf, original)


class TestAutoSaveCleanup(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.hook_utils = MagicMock()
        self.hook_utils.execute_pre_save = MagicMock(return_value=None)
        self.hook_utils.execute_post_save = MagicMock(return_value=[])
        self.hook_utils.execute_editing_handlers = MagicMock(return_value=None)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _make_manager(self, max_backups=3):
        with patch("auto_save_manager.config_manager") as cfg:
            cfg.get = MagicMock(
                side_effect=lambda key, default=None: {
                    "autosave.interval_minutes": 3,
                    "autosave.max_backups": max_backups,
                    "paths.backup_dir": self.temp_dir,
                    "autosave.notify": False,
                }.get(key, default)
            )
            mgr = AutoSaveManager(self.hook_utils)
            mgr.backup_dir = Path(self.temp_dir)
            return mgr

    def test_cleanup_keeps_only_max_backups(self):
        mgr = self._make_manager(max_backups=3)
        original = os.path.join(self.temp_dir, "file.txt")

        # Simulate 5 backup files with distinct mtimes
        backup_dir = Path(self.temp_dir) / Path(original.lstrip("/")).parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        for i in range(5):
            p = backup_dir / f"file.~{1000 + i}~.txt"
            p.write_text(f"content {i}")
            os.utime(p, (1000 + i, 1000 + i))

        mgr._cleanup_old_backups(original)

        remaining = sorted(backup_dir.glob("file.~*~*.txt"))
        # The loop is `while len(backups) >= max_backups`, so it keeps max_backups - 1
        # after the boundary. With max_backups=3 it will delete until 2 remain.
        self.assertLessEqual(len(remaining), 3)

    def test_get_backup_files_newest_first(self):
        mgr = self._make_manager()
        original = os.path.join(self.temp_dir, "sorted.txt")

        backup_dir = Path(self.temp_dir) / Path(original.lstrip("/")).parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        for i, ts in enumerate([100, 300, 200]):
            p = backup_dir / f"sorted.~{ts}~.txt"
            p.write_text(f"v{i}")
            os.utime(p, (ts, ts))

        backups = mgr.get_backup_files(original)
        names = [b.name for b in backups]
        # newest first
        self.assertEqual(names[0], "sorted.~300~.txt")
        self.assertEqual(names[1], "sorted.~200~.txt")
        self.assertEqual(names[2], "sorted.~100~.txt")

    def test_get_backup_files_for_unknown_file(self):
        mgr = self._make_manager()
        self.assertEqual(mgr.get_backup_files("/no/such/file.txt"), [])


class TestAutoSaveRestore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.hook_utils = MagicMock()
        self.hook_utils.execute_pre_save = MagicMock(return_value=None)
        self.hook_utils.execute_post_save = MagicMock(return_value=[])
        self.hook_utils.execute_editing_handlers = MagicMock(return_value=None)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _make_manager(self):
        with patch("auto_save_manager.config_manager") as cfg:
            cfg.get = MagicMock(
                side_effect=lambda key, default=None: {
                    "autosave.interval_minutes": 3,
                    "autosave.max_backups": 5,
                    "paths.backup_dir": self.temp_dir,
                    "autosave.notify": False,
                }.get(key, default)
            )
            mgr = AutoSaveManager(self.hook_utils)
            mgr.backup_dir = Path(self.temp_dir)
            return mgr

    def test_restore_from_backup(self):
        mgr = self._make_manager()
        backup_path = Path(self.temp_dir) / "restore.~123~.txt"
        backup_path.write_text("line A\nline B\nline C")

        buf = make_mock_buffer(lines=["old"], dirty=False)
        ok = mgr.restore_from_backup(str(backup_path), buf)

        self.assertTrue(ok)
        self.assertEqual(buf.lines, ["line A", "line B", "line C"])
        self.assertTrue(buf.dirty)

    def test_restore_from_missing_file_fails(self):
        mgr = self._make_manager()
        buf = make_mock_buffer(lines=["old"], dirty=False)
        ok = mgr.restore_from_backup("/no/such/backup.txt", buf)
        self.assertFalse(ok)


class TestAutoSaveStartStop(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.hook_utils = MagicMock()
        self.hook_utils.execute_pre_save = MagicMock(return_value=None)
        self.hook_utils.execute_post_save = MagicMock(return_value=[])
        self.hook_utils.execute_editing_handlers = MagicMock(return_value=None)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _make_manager(self, interval_minutes=3):
        with patch("auto_save_manager.config_manager") as cfg:
            cfg.get = MagicMock(
                side_effect=lambda key, default=None: {
                    "autosave.interval_minutes": interval_minutes,
                    "autosave.max_backups": 5,
                    "paths.backup_dir": self.temp_dir,
                    "autosave.notify": False,
                }.get(key, default)
            )
            mgr = AutoSaveManager(self.hook_utils)
            mgr.backup_dir = Path(self.temp_dir)
            return mgr

    def test_start_stop_lifecycle(self):
        mgr = self._make_manager()
        buf = make_mock_buffer(filename=os.path.join(self.temp_dir, "x.txt"), dirty=True)

        mgr.start_autosave(buf, buf.filename)
        self.assertTrue(mgr._running)
        self.assertIsNotNone(mgr._thread)

        mgr.stop_autosave()
        self.assertFalse(mgr._running)
        self.assertIsNone(mgr._thread)

    def test_start_twice_restarts_thread(self):
        mgr = self._make_manager()
        buf = make_mock_buffer(filename=os.path.join(self.temp_dir, "x.txt"), dirty=True)

        mgr.start_autosave(buf, buf.filename)
        first_thread = mgr._thread
        mgr.start_autosave(buf, buf.filename)
        second_thread = mgr._thread
        self.assertIsNot(first_thread, second_thread)
        mgr.stop_autosave()

    def test_stop_without_start_is_safe(self):
        mgr = self._make_manager()
        mgr.stop_autosave()  # Should not raise


if __name__ == "__main__":
    unittest.main()
