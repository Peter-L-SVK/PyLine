import sys
import os
import unittest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from text_buffer import TextBuffer

class TestCopyPaste(unittest.TestCase):
    def setUp(self):
        # Setup a buffer with sample lines
        self.tb = TextBuffer()
        self.tb.lines = [
            "First line",
            "Second line",
            "Third line"
        ]
        self.tb.current_line = 1  # Point to "Second line"

    def test_copy_and_paste_line(self):
        # Simulate copying the current line
        self.tb.paste_buffer.set_text(self.tb.lines[self.tb.current_line])
        # Move cursor to end and paste
        self.tb.current_line = len(self.tb.lines)
        self.tb.paste_buffer.paste_into(self.tb, at_line=self.tb.current_line, adjust_indent=False)
        # Now buffer should have a duplicate of "Second line" at the end
        self.assertEqual(self.tb.lines[-1], "Second line")
        self.assertEqual(len(self.tb.lines), 4)

    def test_copy_and_paste_multiple_lines(self):
        # Simulate copying multiple lines
        text = '\n'.join(self.tb.lines[0:2])  # Copy first two lines
        self.tb.paste_buffer.set_text(text)
        # Paste at the end
        self.tb.current_line = len(self.tb.lines)
        self.tb.paste_buffer.paste_into(self.tb, at_line=self.tb.current_line, adjust_indent=False)
        # Buffer should have two new lines appended
        self.assertEqual(self.tb.lines[-2], "First line")
        self.assertEqual(self.tb.lines[-1], "Second line")
        self.assertEqual(len(self.tb.lines), 5)

    def test_paste_overwrite(self):
        # Copy a line
        self.tb.paste_buffer.set_text("Replacement line")
        # Overwrite the second line
        self.tb.paste_buffer.paste_over(self.tb, at_line=1)
        self.assertEqual(self.tb.lines[1], "Replacement line")

if __name__ == "__main__":
    unittest.main()
