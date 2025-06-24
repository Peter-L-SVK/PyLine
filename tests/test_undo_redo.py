import sys
import os
import unittest

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from text_buffer import TextBuffer

class TestUndoRedo(unittest.TestCase):
    def setUp(self):
        self.tb = TextBuffer()
        self.tb.lines = [
            "Alpha",
            "Bravo",
            "Charlie"
        ]
        self.tb.current_line = 1  # "Bravo"

    def test_undo_redo_insert_line(self):
        # Insert a blank line after "Bravo" (index 1)
        self.tb.current_line = 1
        self.tb.insert_line()  # Blank line inserted at index 2
        self.tb.lines[2] = "Delta"  # Simulate user editing the new line
        
        self.assertEqual(self.tb.lines, ["Alpha", "Bravo", "Delta", "Charlie"])
        
        # Undo should remove the inserted line
        self.tb.undo()
        self.assertEqual(self.tb.lines, ["Alpha", "Bravo", "Charlie"])
        
        # Redo should restore the blank line (not "Delta")
        self.tb.redo()
        self.assertEqual(self.tb.lines, ["Alpha", "Bravo", "", "Charlie"])
    
    def test_undo_redo_delete_line(self):
        self.tb.current_line = 1
        self.tb.delete_line()
        self.assertEqual(self.tb.lines, ["Alpha", "Charlie"])

        # Undo the deletion
        self.tb.undo()
        self.assertEqual(self.tb.lines, ["Alpha", "Bravo", "Charlie"])

        # Redo the deletion
        self.tb.redo()
        self.assertEqual(self.tb.lines, ["Alpha", "Charlie"])

if __name__ == "__main__":
    result = unittest.main(exit=False)
    if result.result.wasSuccessful():
        print("\nAll undo/redo tests passed successfully!")
