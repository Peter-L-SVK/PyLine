import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from text_buffer import TextBuffer


class TestCopyPaste(unittest.TestCase):
    def setUp(self):
        # Setup a buffer with sample lines
        self.tb = TextBuffer()
        # Mock the hook system to avoid side effects
        self.tb.hook_utils.execute_pre_paste = MagicMock(return_value=None)
        self.tb.hook_utils.execute_post_paste = MagicMock(return_value=[])

        # Set up buffer content directly
        self.tb.buffer_manager.lines = ["First line", "Second line", "Third line"]
        self.tb.navigation_manager.set_current_line(1, 3)  # Point to "Second line"

    def test_copy_and_paste_line(self):
        # Simulate copying the current line
        current_text = self.tb.buffer_manager.get_line(1)
        self.tb.paste_buffer.set_text(current_text)

        # Move cursor to end and paste
        self.tb.navigation_manager.set_current_line(3, 3)
        self.tb.paste_buffer.paste_into(self.tb, at_line=3, adjust_indent=False)  # Pass self.tb

        # Now buffer should have a duplicate of "Second line" at the end
        self.assertEqual(self.tb.buffer_manager.lines[-1], "Second line")
        self.assertEqual(len(self.tb.buffer_manager.lines), 4)

    def test_copy_and_paste_multiple_lines(self):
        # Simulate copying multiple lines
        text = "\n".join(self.tb.buffer_manager.lines[0:2])  # Copy first two lines
        self.tb.paste_buffer.set_text(text)

        # Paste at the end
        self.tb.navigation_manager.set_current_line(3, 3)
        self.tb.paste_buffer.paste_into(self.tb, at_line=3, adjust_indent=False)  # Pass self.tb

        # Buffer should have two new lines appended
        self.assertEqual(self.tb.buffer_manager.lines[-2], "First line")
        self.assertEqual(self.tb.buffer_manager.lines[-1], "Second line")
        self.assertEqual(len(self.tb.buffer_manager.lines), 5)

    def test_paste_overwrite(self):
        # Copy a line
        self.tb.paste_buffer.set_text("Replacement line")

        # Overwrite the second line
        self.tb.paste_buffer.paste_over(self.tb, at_line=1)  # Pass self.tb
        self.assertEqual(self.tb.buffer_manager.lines[1], "Replacement line")


if __name__ == "__main__":
    unittest.main()
