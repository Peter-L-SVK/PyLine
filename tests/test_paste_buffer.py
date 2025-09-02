import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from paste_buffer import PasteBuffer
from text_buffer import TextBuffer


class TestPasteBuffer(unittest.TestCase):
    def setUp(self):
        self.pb = PasteBuffer()
        self.tb = TextBuffer()
        self.tb.buffer_manager.lines = ["Line 1", "Line 2", "Line 3"]

    def test_set_text(self):
        self.pb.set_text("Test\nContent")
        self.assertEqual(self.pb.buffer, ["Test", "Content"])

    def test_paste_into(self):
        self.pb.set_text("Inserted\nLines")
        lines_pasted = self.pb.paste_into(self.tb, at_line=1)  # Pass TextBuffer, not BufferManager
        self.assertEqual(lines_pasted, 2)
        self.assertEqual(self.tb.buffer_manager.lines, ["Line 1", "Inserted", "Lines", "Line 2", "Line 3"])

    def test_paste_over(self):
        self.pb.set_text("New\nContent")
        lines_pasted = self.pb.paste_over(self.tb, at_line=1)  # Pass TextBuffer, not BufferManager
        self.assertEqual(lines_pasted, 2)
        self.assertEqual(self.tb.buffer_manager.lines, ["Line 1", "New", "Content"])

    def test_indentation_preservation(self):
        self.pb.set_text("  Indented\n    More")
        self.tb.buffer_manager.lines = ["Start", "  Target", "End"]
        lines_pasted = self.pb.paste_into(self.tb, at_line=1)  # Pass TextBuffer
        self.assertEqual(self.tb.buffer_manager.lines[2], "    More")  # Should preserve relative indentation


if __name__ == "__main__":
    unittest.main()
