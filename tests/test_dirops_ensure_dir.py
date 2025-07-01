# test_dirops_ensure_dir.py
import sys
import os
import unittest
import tempfile
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import dirops

class TestEnsureDirectoryExists(unittest.TestCase):
    def setUp(self):
        # Create a temp directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_base = self.temp_dir.name
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def test_existing_directory(self):
        """Test with already existing directory"""
        test_path = os.path.join(self.test_base, "existing_dir")
        os.makedirs(test_path)
        filepath = os.path.join(test_path, "file.txt")
        
        # Should return True without creating anything
        with patch('builtins.print') as mock_print:
            result = dirops.ensure_directory_exists(filepath)
            self.assertTrue(result)
            mock_print.assert_not_called()
            
    def test_new_directory_creation(self):
        """Test creating new directory structure"""
        test_path = os.path.join(self.test_base, "new_dir/subdir")
        filepath = os.path.join(test_path, "file.txt")
        
        # Should create directories and return True
        with patch('builtins.print') as mock_print:
            result = dirops.ensure_directory_exists(filepath)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(test_path))
            mock_print.assert_called_once_with(f"Created directory: {test_path}")
            
    def test_directory_creation_failure(self):
        """Test permission errors"""
        test_path = "/root/protected_dir"  # Should fail unless run as root
        filepath = os.path.join(test_path, "file.txt")
        
        # Should catch OSError and return False
        with patch('builtins.print') as mock_print:
            result = dirops.ensure_directory_exists(filepath)
            self.assertFalse(result)
            mock_print.assert_called_once()
            self.assertIn("Error creating directory", mock_print.call_args[0][0])
            
    def test_empty_filename(self):
        """Test with filename only (no directory)"""
        with patch('builtins.print') as mock_print:
            result = dirops.ensure_directory_exists("file.txt")
            self.assertTrue(result)  # Should return True for files in current dir
            mock_print.assert_not_called()
            
    def test_relative_paths(self):
        """Test with relative paths"""
        rel_path = "test_dir/subdir"
        filepath = os.path.join(rel_path, "file.txt")
        
        try:
            result = dirops.ensure_directory_exists(filepath)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(rel_path))
            
            # Cleanup created dirs
            os.removedirs(rel_path)
        except:
            if os.path.exists(rel_path):
                os.removedirs(rel_path)
            raise

if __name__ == "__main__":
    unittest.main()
