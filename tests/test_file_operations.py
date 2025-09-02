import sys
import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from text_buffer import TextBuffer


class TestFileOperations(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.temp_dir.name, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_file(self):
        tb = TextBuffer()
        # Mock the hook utils methods
        tb.hook_utils.execute_pre_load = MagicMock(return_value=None)
        tb.hook_utils.execute_post_load = MagicMock(return_value=[])

        self.assertTrue(tb.load_file(self.test_file))
        self.assertEqual(tb.buffer_manager.lines, ["Line 1", "Line 2", "Line 3"])
        self.assertEqual(tb.buffer_manager.filename, self.test_file)
        self.assertFalse(tb.buffer_manager.dirty)

    def test_save_file(self):
        tb = TextBuffer()
        # Mock the hook utils methods
        tb.hook_utils.execute_pre_load = MagicMock(return_value=None)
        tb.hook_utils.execute_post_load = MagicMock(return_value=[])
        tb.hook_utils.execute_pre_save = MagicMock(return_value=None)
        tb.hook_utils.execute_post_save = MagicMock(return_value=[])

        tb.load_file(self.test_file)
        tb.buffer_manager.lines.append("Line 4")
        tb.buffer_manager.dirty = True
        self.assertTrue(tb.save())

        with open(self.test_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "Line 1\nLine 2\nLine 3\nLine 4")

    def test_save_new_file(self):
        tb = TextBuffer()
        tb.buffer_manager.lines = ["New", "Content"]
        tb.buffer_manager.filename = os.path.join(self.temp_dir.name, "new.txt")
        self.assertTrue(tb.save())
        self.assertTrue(os.path.exists(tb.buffer_manager.filename))


if __name__ == "__main__":
    unittest.main()
