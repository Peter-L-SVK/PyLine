import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from text_buffer import TextBuffer


class TestSelectionOperations(unittest.TestCase):
    def setUp(self):
        self.tb = TextBuffer()
        # Mock clipboard to avoid system calls
        self.tb.paste_buffer.copy_to_clipboard = MagicMock(return_value=True)

        # Set up buffer content
        self.tb.buffer_manager.lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]

    def test_selection_range(self):
        self.tb.navigation_manager.set_current_line(1, 5)
        self.tb.start_selection()
        self.tb.navigation_manager.set_current_line(3, 5)
        self.tb.end_selection()

        self.assertEqual(self.tb.selection_manager.selection_start, 1)
        self.assertEqual(self.tb.selection_manager.selection_end, 3)

    def test_copy_selection(self):
        self.tb.selection_manager.selection_start = 1
        self.tb.selection_manager.selection_end = 3
        self.tb.selection_manager.in_selection_mode = True

        success = self.tb.copy_selection()
        self.assertTrue(success)
        # Verify clipboard was called with correct text
        self.tb.paste_buffer.copy_to_clipboard.assert_called_with("Line 2\nLine 3\nLine 4")

    def test_delete_selection(self):
        self.tb.selection_manager.selection_start = 1
        self.tb.selection_manager.selection_end = 3
        self.tb.selection_manager.in_selection_mode = True

        self.tb.delete_selected_lines()
        self.assertEqual(self.tb.buffer_manager.lines, ["Line 1", "Line 5"])
        self.assertEqual(self.tb.undo_manager.can_undo(), True)


if __name__ == "__main__":
    unittest.main()
