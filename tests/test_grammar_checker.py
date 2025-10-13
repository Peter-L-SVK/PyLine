import sys
import os
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Import the grammar checker components
try:
    from hooks.AI_grammar_check.grammar_checker__70 import GrammarChecker

    GRAMMAR_AVAILABLE = True
except ImportError:
    GRAMMAR_AVAILABLE = False

# Import the main ConfigManager from src
try:
    from config import ConfigManager

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


@unittest.skipUnless(GRAMMAR_AVAILABLE, "Grammar checker hook not available")
class TestGrammarChecker(unittest.TestCase):
    def setUp(self):
        """Set up a grammar checker instance for testing"""
        # Mock config to avoid file dependencies
        with patch("hooks.AI_grammar_check.grammar_checker__70.ConfigManager.load_config") as mock_load:
            mock_load.return_value = {
                "common_errors": {
                    "their_there_theyre": [
                        {
                            "pattern": r"\btheir\b",
                            "suggestion": "they're",
                            "explanation": "their (possessive) vs they're (they are)",
                            "confidence": 0.7,
                        }
                    ],
                    "your_youre": [
                        {
                            "pattern": r"\byour\b",
                            "suggestion": "you're",
                            "explanation": "your (possessive) vs you're (you are)",
                            "confidence": 0.7,
                        }
                    ],
                },
                "writing_style_rules": {"sentence_length": {"too_long_threshold": 25, "too_short_threshold": 5}},
                "content_filters": {"exclude_lines_matching": ["^#", "^```", "^---"]},
            }
            self.gc = GrammarChecker()

    def test_technical_vocabulary_loading(self):
        """Test that technical vocabulary loads correctly"""
        tech_vocab = self.gc.load_technical_vocabulary()
        self.assertIsInstance(tech_vocab, set)
        # Should be able to handle empty config
        self.assertGreaterEqual(len(tech_vocab), 0)

    def test_should_exclude_line(self):
        """Test line exclusion patterns"""
        # Should exclude comment lines
        self.assertTrue(self.gc.should_exclude_line("# This is a comment"))
        self.assertTrue(self.gc.should_exclude_line("```python"))
        self.assertTrue(self.gc.should_exclude_line("---"))

        # Should not exclude regular text
        self.assertFalse(self.gc.should_exclude_line("This is regular text"))
        self.assertFalse(self.gc.should_exclude_line("print('hello')"))

    def test_filter_technical_content(self):
        """Test technical content filtering"""
        text = """# Header
Regular text line
```code block```
Another regular line
--- separator"""

        filtered = self.gc.filter_technical_content(text)
        expected = "Regular text line\nAnother regular line"
        self.assertEqual(filtered.strip(), expected)

    def test_count_syllables_basic(self):
        """Test basic syllable counting"""
        self.assertEqual(self.gc.count_syllables("hello"), 2)
        self.assertEqual(self.gc.count_syllables("world"), 1)
        self.assertEqual(self.gc.count_syllables("syllable"), 3)
        self.assertEqual(self.gc.count_syllables("a"), 1)
        self.assertEqual(self.gc.count_syllables("I"), 1)

    def test_count_syllables_special_cases(self):
        """Test syllable counting with special cases"""
        # Silent 'e'
        self.assertEqual(self.gc.count_syllables("make"), 1)
        self.assertEqual(self.gc.count_syllables("table"), 2)  # exception for 'le'

        # 'es', 'ed' endings
        self.assertEqual(self.gc.count_syllables("boxes"), 2)
        self.assertEqual(self.gc.count_syllables("walked"), 1)

    def test_analyze_text_statistics_basic(self):
        """Test basic text statistics analysis"""
        text = "This is a test. This has multiple sentences. And another one."
        stats = self.gc.analyze_text_statistics(text)

        self.assertEqual(stats["word_count"], 12)
        self.assertEqual(stats["sentence_count"], 3)
        self.assertGreater(stats["avg_sentence_length"], 0)
        self.assertGreater(stats["readability_score"], 0)
        self.assertIn("vocabulary_diversity", stats)

    def test_analyze_text_statistics_empty(self):
        """Test text statistics with empty input"""
        stats = self.gc.analyze_text_statistics("")
        self.assertEqual(stats["word_count"], 0)
        self.assertEqual(stats["sentence_count"], 0)
        self.assertEqual(stats["avg_sentence_length"], 0)

    def test_calculate_readability(self):
        """Test readability score calculation"""
        # Simple text should have decent readability
        simple_text = "The cat sat on the mat. It was happy."
        score_simple = self.gc.calculate_readability(simple_text)
        self.assertGreater(score_simple, 50)  # Should be fairly readable

        # Complex text should have lower readability
        complex_text = "The multifaceted implementation necessitates comprehensive contextualization."
        score_complex = self.gc.calculate_readability(complex_text)
        self.assertLess(score_complex, score_simple)

    @patch("hooks.AI_grammar_check.grammar_checker__70.LT_AVAILABLE", False)
    def test_grammar_check_without_languagetool(self):
        """Test grammar checking when language_tool is not available"""
        text = "Their going to the park. Your welcome."
        issues = self.gc.check_grammar_advanced(text)

        # Should still find pattern-based issues
        their_issues = [issue for issue in issues if "their" in issue.get("message", "").lower()]
        self.assertGreater(len(their_issues), 0)

    def test_fix_their_there(self):
        """Test their/there/they're correction"""
        fixed = self.gc._fix_their_there("their", MagicMock())
        self.assertEqual(fixed, "they're")

        fixed = self.gc._fix_their_there("there", MagicMock())
        self.assertEqual(fixed, "they're")

        # Should return original if no match
        fixed = self.gc._fix_their_there("they're", MagicMock())
        self.assertEqual(fixed, "they're")

    def test_fix_your_youre(self):
        """Test your/you're correction"""
        fixed = self.gc._fix_your_youre("your", MagicMock())
        self.assertEqual(fixed, "you're")

        # Should return original if no match
        fixed = self.gc._fix_your_youre("you're", MagicMock())
        self.assertEqual(fixed, "you're")

    def test_find_line_number(self):
        """Test line number finding from character offset"""
        content = ["Line 1", "Line 2", "Line 3"]

        # First character of first line
        self.assertEqual(self.gc.find_line_number(content, 0), 1)

        # First character of second line (after "Line 1\n")
        self.assertEqual(self.gc.find_line_number(content, 7), 2)

        # Beyond content should return 1
        self.assertEqual(self.gc.find_line_number(content, 100), 1)

    def test_analyze_writing_style_long_sentences(self):
        """Test writing style analysis with long sentences"""
        stats = {
            "avg_sentence_length": 30,  # Very long
            "readability_score": 40,  # Low readability
            "vocabulary_diversity": 0.3,
        }

        suggestions = self.gc.analyze_writing_style(stats)
        self.assertGreater(len(suggestions), 0)

        # Should suggest breaking up long sentences
        long_sentence_suggestions = [s for s in suggestions if "long" in s.get("message", "").lower()]
        self.assertGreater(len(long_sentence_suggestions), 0)

    def test_analyze_writing_style_good(self):
        """Test writing style analysis with good metrics"""
        stats = {
            "avg_sentence_length": 15,  # Ideal
            "readability_score": 80,  # Good readability
            "vocabulary_diversity": 0.6,
        }

        suggestions = self.gc.analyze_writing_style(stats)
        # Should have fewer or no suggestions for good writing
        readability_suggestions = [s for s in suggestions if "readability" in s.get("category", "")]
        self.assertEqual(len(readability_suggestions), 0)


@unittest.skipUnless(CONFIG_AVAILABLE, "Main ConfigManager not available")
class TestConfigManager(unittest.TestCase):
    def setUp(self):
        # Mock ALL file operations to avoid creating actual config files
        self.mock_exists = patch("pathlib.Path.exists").start()
        self.mock_mkdir = patch("pathlib.Path.mkdir").start()

        # Mock the config file to return our test data
        self.mock_file_data = '{"paths": {"source_path": "/test"}}'
        self.mock_open = patch("builtins.open", mock_open(read_data=self.mock_file_data)).start()
        self.mock_print = patch("builtins.print").start()

        self.mock_exists.return_value = True  # Config file exists

        # Create the config manager AFTER all mocks are in place
        self.config_manager = ConfigManager()

    def tearDown(self):
        patch.stopall()

    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "value"}')
    @patch("pathlib.Path.exists")
    def test_load_config_file_exists(self, mock_exists, mock_file):
        """Test loading config when file exists"""
        mock_exists.return_value = True
        config = self.config_manager._load_config()
        self.assertIn("test", config)
        self.assertEqual(config["test"], "value")

    def test_load_config_file_not_exists(self):
        """Test loading config when file doesn't exist"""
        # Test the default config generation directly
        default_config = self.config_manager._get_default_config()
        self.assertIsInstance(default_config, dict)
        self.assertIn("paths", default_config)
        self.assertIn("editor", default_config)
        self.assertIn("hooks", default_config)

    def test_get_set_methods(self):
        """Test get and set methods with dot notation"""
        # Test get with existing key - should return the value from mocked config file
        value = self.config_manager.get("paths.source_path")
        self.assertEqual(value, "/test")  # This should match the mocked data

        # Test get with non-existing key
        value = self.config_manager.get("non.existing.key", "default")
        self.assertEqual(value, "default")

        # Test set
        with patch.object(self.config_manager, "_save_config") as mock_save:
            self.config_manager.set("new.key", "new_value")
            # Verify save was called
            mock_save.assert_called_once()


@unittest.skipUnless(GRAMMAR_AVAILABLE, "Grammar checker hook not available")
class TestGrammarCheckerIntegration(unittest.TestCase):
    """Integration tests for the grammar checker"""

    def setUp(self):
        with patch("hooks.AI_grammar_check.grammar_checker__70.ConfigManager.load_config") as mock_load:
            mock_load.return_value = {
                "common_errors": {
                    "their_there_theyre": [
                        {
                            "pattern": r"\btheir\b",
                            "suggestion": "they're",
                            "explanation": "their (possessive) vs they're (they are)",
                            "confidence": 0.7,
                        }
                    ]
                },
                "content_filters": {"exclude_lines_matching": ["^#"]},
            }
            self.gc = GrammarChecker()

    def test_end_to_end_grammar_check(self):
        """Test complete grammar checking workflow"""
        text = """# This is a comment and should be ignored
Their going to the store. 
This is a very long sentence that should probably be broken up into multiple smaller sentences for better readability and comprehension.
Your welcome for the help."""

        issues = self.gc.check_grammar_advanced(text)

        # Should find "their" error but not in comment line
        their_issues = [issue for issue in issues if "their" in issue.get("message", "").lower()]
        self.assertGreater(len(their_issues), 0)

        # Should find "your" error
        your_issues = [issue for issue in issues if "your" in issue.get("message", "").lower()]
        self.assertGreater(len(your_issues), 0)

    def test_enhanced_suggestions(self):
        """Test AI-enhanced suggestions generation"""
        text = "Their going to the park. Their going to the store."
        basic_issues = self.gc.check_grammar_advanced(text)

        enhanced_issues = self.gc.get_enhanced_suggestions(text, basic_issues)

        # Enhanced issues should include confidence scores
        if enhanced_issues:
            self.assertIn("confidence", enhanced_issues[0])


if __name__ == "__main__":
    # Enhanced test runner for individual file
    loader = unittest.TestLoader()

    # Only add test classes that are available
    suites = []
    if GRAMMAR_AVAILABLE:
        suites.append(loader.loadTestsFromTestCase(TestGrammarChecker))
        suites.append(loader.loadTestsFromTestCase(TestGrammarCheckerIntegration))
    if CONFIG_AVAILABLE:
        suites.append(loader.loadTestsFromTestCase(TestConfigManager))

    if not suites:
        print("❌ No test suites available - required modules not found")
        sys.exit(1)

    suite = unittest.TestSuite(suites)
    runner = unittest.TextTestRunner(verbosity=2)
    print(f"\n🧪 Running {__file__}")
    print("─" * 50)
    result = runner.run(suite)

    if result.wasSuccessful():
        print(f"✅ {result.testsRun} tests passed in {__file__}")
    else:
        print(f"❌ {len(result.failures) + len(result.errors)} tests failed in {__file__}")
        for test, traceback in result.failures + result.errors:
            print(f"   Failed: {test}")
