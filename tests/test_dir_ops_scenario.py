import sys
import os
import unittest
import tempfile
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import dirops


class TestDirOpsScenario(unittest.TestCase):
    def setUp(self):
        # Create a temp directory and switch to it
        self.temp_dir = tempfile.TemporaryDirectory()
        self.orig_dir = os.getcwd()
        os.chdir(self.temp_dir.name)

    def tearDown(self):
        os.chdir(self.orig_dir)
        self.temp_dir.cleanup()

    def test_mkdir_cd_and_rmdir(self):
        dirname = "somedir"

        # mkdir somedir
        result = dirops.mkdir(dirname)
        self.assertIsNone(result, "mkdir should succeed if directory did not exist")
        self.assertTrue(os.path.isdir(dirname))

        # cd somedir
        dirops.cd(dirname)
        self.assertEqual(os.getcwd(), str(Path(self.temp_dir.name) / dirname))

        # cd ..
        dirops.cd("..")
        self.assertEqual(os.getcwd(), self.temp_dir.name)

        # rmdir somedir
        result = dirops.rmdir(dirname)
        self.assertIsNone(result, "rmdir should succeed if directory existed")
        self.assertFalse(os.path.exists(dirname))


if __name__ == "__main__":
    unittest.main()
