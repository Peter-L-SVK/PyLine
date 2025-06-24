import unittest
import sys
import os

# Add the src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import dirops


class TestDirops(unittest.TestCase):
    def setUp(self):
        # Set up a temporary file for testing
        self.test_filename = "test_file.txt"
        with open(self.test_filename, "w") as f:
            f.write("Hello world!\nThis is a test file.\nNew line here.")

    def tearDown(self):
        # Remove the file after test
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_count_words_in_file(self):
        words, lines, chars = dirops.count_words_in_file(self.test_filename)
        self.assertEqual(words, 10)  # "Hello world! This is a test file. New line here." (10 words)
        self.assertEqual(lines, 3)
        self.assertEqual(chars, len("Hello world!\nThis is a test file.\nNew line here."))

    def test_file_not_found(self):
        words, lines, chars = dirops.count_words_in_file("nonexistent.txt")
        self.assertEqual(words, 'error')
        self.assertEqual(lines, 0)
        self.assertEqual(chars, 0)

if __name__ == "__main__":
    unittest.main()
