import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from text_buffer import TextBuffer

class TestFileOperations(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.temp_dir.name, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("Line 1\nLine 2\nLine 3")
            
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def test_load_file(self):
        tb = TextBuffer()
        self.assertTrue(tb.load_file(self.test_file))
        self.assertEqual(tb.lines, ["Line 1", "Line 2", "Line 3"])
        self.assertEqual(tb.filename, self.test_file)
        self.assertFalse(tb.dirty)
        
    def test_save_file(self):
        tb = TextBuffer()
        tb.load_file(self.test_file)
        tb.lines.append("Line 4")
        tb.dirty = True
        self.assertTrue(tb.save())
        
        with open(self.test_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, "Line 1\nLine 2\nLine 3\nLine 4")
        
    def test_save_new_file(self):
        tb = TextBuffer()
        tb.lines = ["New", "Content"]
        tb.filename = os.path.join(self.temp_dir.name, "new.txt")
        self.assertTrue(tb.save())
        self.assertTrue(os.path.exists(tb.filename))

if __name__ == "__main__":
    unittest.main()
