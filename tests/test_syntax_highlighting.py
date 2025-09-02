import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from syntax_highlighter import SyntaxHighlighter


class TestSyntaxHighlighting(unittest.TestCase):
    def setUp(self):
        self.hl = SyntaxHighlighter()

    def test_keyword_highlighting(self):
        line = "def function():"
        highlighted = self.hl._highlight_python(line)
        self.assertIn("\033[38;5;90mdef\033[0m", highlighted)  # Keyword color
        self.assertIn("\033[38;5;130mfunction\033[0m", highlighted)  # Function color

    def test_string_highlighting(self):
        line = 'msg = "Hello World"'
        highlighted = self.hl._highlight_python(line)
        self.assertIn('\033[38;5;28m"Hello World"\033[0m', highlighted)

    def test_comment_highlighting(self):
        line = "# This is a comment"
        highlighted = self.hl._highlight_python(line)
        self.assertTrue(highlighted.startswith("\033[38;5;66m#"))

    def test_multiline_docstring(self):
        line1 = '"""This is a docstring'
        line2 = 'with multiple lines"""'
        # First line should start docstring mode
        highlighted1 = self.hl._highlight_python(line1)
        self.assertTrue(highlighted1.startswith("\033[38;5;66m"))
        # Second line should still be in docstring
        highlighted2 = self.hl._highlight_python(line2)
        self.assertTrue(highlighted2.startswith("\033[38;5;66m"))


if __name__ == "__main__":
    unittest.main()
