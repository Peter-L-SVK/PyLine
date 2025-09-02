import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from text_buffer import TextBuffer


class TestUndoRedo(unittest.TestCase):
    def setUp(self):
        self.tb = TextBuffer()
        # Mock hook system
        self.tb.hook_utils.execute_pre_insert = MagicMock(return_value=None)
        self.tb.hook_utils.execute_post_insert = MagicMock(return_value=[])
        self.tb.hook_utils.execute_pre_delete = MagicMock(return_value=None)
        self.tb.hook_utils.execute_post_delete = MagicMock(return_value=[])

        # Set up initial content
        self.tb.buffer_manager.lines = ["Alpha", "Bravo", "Charlie"]
        self.tb.navigation_manager.set_current_line(1, 3)  # "Bravo"

    def test_undo_redo_insert_line(self):
        # Insert a blank line after "Bravo" (index 1)
        self.tb.navigation_manager.set_current_line(1, 3)
        self.tb.insert_line()  # Blank line inserted at index 2

        # Edit the new line (simulate user input)
        self.tb.buffer_manager.set_line(2, "Delta")

        self.assertEqual(self.tb.buffer_manager.lines, ["Alpha", "Bravo", "Delta", "Charlie"])

        # Undo should remove the inserted line
        self.tb.undo()
        self.assertEqual(self.tb.buffer_manager.lines, ["Alpha", "Bravo", "Charlie"])

        # Redo should restore the blank line
        self.tb.redo()
        self.assertEqual(self.tb.buffer_manager.lines, ["Alpha", "Bravo", "", "Charlie"])

    def test_undo_redo_delete_line(self):
        self.tb.navigation_manager.set_current_line(1, 3)
        self.tb.delete_current_line()
        self.assertEqual(self.tb.buffer_manager.lines, ["Alpha", "Charlie"])

        # Undo the deletion
        self.tb.undo()
        self.assertEqual(self.tb.buffer_manager.lines, ["Alpha", "Bravo", "Charlie"])

        # Redo the deletion
        self.tb.redo()
        self.assertEqual(self.tb.buffer_manager.lines, ["Alpha", "Charlie"])


if __name__ == "__main__":
    unittest.main()
