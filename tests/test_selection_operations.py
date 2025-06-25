import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from text_buffer import TextBuffer

class TestSelectionOperations(unittest.TestCase):
    def setUp(self):
        self.tb = TextBuffer()
        self.tb.lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
        
    def test_selection_range(self):
        self.tb.current_line = 1
        self.tb.start_selection()
        self.tb.current_line = 3
        self.tb.end_selection()
        self.assertEqual(self.tb.selection_start, 1)
        self.assertEqual(self.tb.selection_end, 3)
        
    def test_copy_selection(self):
        self.tb.selection_start = 1
        self.tb.selection_end = 3
        self.assertTrue(self.tb.copy_selection())
        # Would verify clipboard content if we could mock it
        
    def test_delete_selection(self):
        self.tb.selection_start = 1
        self.tb.selection_end = 3
        self.tb.delete_selected_lines()
        self.assertEqual(self.tb.lines, ["Line 1", "Line 5"])
        self.assertEqual(len(self.tb.undo_stack), 1)  # Should be one atomic operation

    def test_reverse_selection(self):
        self.tb.current_line = 3
        self.tb.start_selection()
        self.tb.current_line = 1
        self.tb.end_selection()
        self.assertEqual(self.tb.selection_start, 1)
        self.assertEqual(self.tb.selection_end, 3)

if __name__ == "__main__":
    unittest.main()
