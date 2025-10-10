# Grammar Checker Hook for PyLine

## Overview

An AI-enhanced grammar checking hook for PyLine that uses advanced natural language processing with LanguageTool, pandas, and numpy for intelligent grammar and style suggestions.

## Features

- **AI-Enhanced Grammar Checking**: Uses LanguageTool with custom rule enhancements
- **Intelligent Pattern Recognition**: Advanced regex patterns for common grammar errors
- **Statistical Analysis**: Uses pandas/numpy for text statistics and readability scoring
- **Context-Aware Suggestions**: Analyzes context to reduce false positives
- **Writing Style Analysis**: Provides feedback on sentence structure, vocabulary, and readability
- **Configurable Rules**: JSON-based configuration for easy customization
- **Line Number Tracking**: Shows exact line numbers for each issue detected

## Installation

### Quick Install (Recommended)
```bash
# Make the install script executable
chmod +x install.sh

# Run the installer
./install.sh
```

### Manual Installation
```bash
# Create the hook directory
mkdir -p ~/.pyline/hooks/editing_ops/search_replace/

# Copy the hook files
cp grammar_checker__70.py ~/.pyline/hooks/editing_ops/search_replace/
cp grammar_config.json ~/.pyline/hooks/editing_ops/search_replace/

# Set execute permissions
chmod +x ~/.pyline/hooks/editing_ops/search_replace/grammar_checker__70.py
```

## Dependencies

### Required Python Packages
```bash
pip install language-tool-python pandas numpy
```

### Optional Dependencies
- **LanguageTool**: Local server for faster processing (optional)
- **Java**: Required for local LanguageTool server

## Usage

The hook automatically integrates with PyLine's content processing. No additional commands required!

1. Open PyLine with any text file
2. The grammar checker runs automatically on content display
3. Review grammar suggestions and statistics in the output

## Output Example

```
============================================================
PYLINE GRAMMAR CHECKER - AI ENHANCED
============================================================

📊 TEXT STATISTICS:
  Words: 46
  Sentences: 9
  Avg. Sentence Length: 5.11 words
  Vocabulary Diversity: 28.3%
  Readability Score: 95.0/100

🔍 GRAMMAR & STYLE ISSUES:
  MEDIUM:
⚠️ Line 6: Possible error: Missing 'is' in greeting phrases like 'Hello this' (62% confidence)
      💡 Suggestion: Hello, is this some text, that I am typing?
⚠️ Line 10: Possible error: Missing 'is' in greeting phrases like 'Hello this' (64% confidence)
      💡 Suggestion: Hello this is some text, that I am typing

  LOW:
💡 Line 1: Short sentences (avg: 5.11 words) can feel choppy (49% confidence)
      💡 Suggestion: Vary sentence length for better flow

📝 WRITING TIPS:
  • Try varying your vocabulary for more engaging writing

💡 Tip: Run this check after writing to catch common errors.
============================================================
```

## Configuration

### Customizing Grammar Rules
Edit `grammar_config.json` to modify:

- **Common Error Patterns**: Add new grammar rules
- **Confidence Levels**: Adjust detection sensitivity
- **Writing Style Rules**: Change readability thresholds
- **Output Settings**: Customize display preferences

### Example Configuration Snippet
```json
{
  "common_errors": {
    "their_there_theyre": [
      {
        "pattern": "\\btheir\\b",
        "suggestion": "they're",
        "explanation": "their (possessive) vs they're (they are)",
        "confidence": 0.7
      }
    ]
  },
  "writing_style_rules": {
    "sentence_length": {
      "too_long_threshold": 25,
      "too_short_threshold": 8
    }
  }
}
```

## Supported Grammar Checks

### Common Errors
- **Their/There/They're** confusion
- **Your/You're** misuse
- **Its/It's** confusion
- **Then/Than** errors
- Missing copula verbs
- Subject-verb agreement
- Question structure issues
- Sentence ending punctuation

### Writing Style Analysis
- Sentence length optimization
- Vocabulary diversity scoring
- Readability assessment (Flesch Reading Ease)
- Passive voice detection
- Repetition analysis

## Technical Details

**Hook Type**: `editing_ops/search_replace`  
**Priority**: 70 (balanced priority for grammar checking)  
**Language**: Python 3.6+  
**AI Components**: LanguageTool, pandas, numpy  

## License and Attribution

This hook is licensed under **GNU GPL v3+**, compatible with PyLine's license.

### Third-Party Components

| Component | License | Notes |
|-----------|---------|-------|
| **LanguageTool** | LGPL 2.1+ | Grammar checking engine |
| **LanguageTool Dictionaries** | Mixed (GPL, BSD, etc.) | Language data files may have various open-source licenses |
| **NumPy** | BSD 3-Clause | Numerical computing library |
| **pandas** | BSD 3-Clause | Data analysis library |

**Important**: While LanguageTool's code is under LGPL, some of its language dictionaries (data files) may be under different licenses like GPL or BSD. When using this hook, you are also subject to the license terms of these dictionary files.

### How It Works

1. **Text Analysis**: Uses pandas/numpy for statistical text analysis
2. **Grammar Checking**: Integrates LanguageTool for comprehensive grammar checking
3. **Pattern Matching**: Applies custom regex patterns for common errors
4. **Context Analysis**: Uses context to improve suggestion accuracy
5. **Confidence Scoring**: AI-powered confidence levels for each suggestion

## Performance

- **Initial Load**: May take 2-3 seconds to load LanguageTool
- **Subsequent Checks**: Fast processing with cached analysis
- **Memory Usage**: Moderate (LanguageTool Java process)
- **CPU**: Low during normal operation

## Troubleshooting

### LanguageTool Not Loading?
```bash
# Install language-tool-python
pip install language-tool-python

# Test installation
python -c "import language_tool_python; print('OK')"
```

### Pandas/Numpy Issues?
```bash
# Install data science packages
pip install pandas numpy

# Test installation
python -c "import pandas, numpy; print('OK')"
```

### Hook Not Working?
```bash
# Check file permissions
chmod +x ~/.pyline/hooks/editing_ops/search_replace/grammar_checker__70.py

# Test the hook directly
python grammar_checker__70.py
```

## Customization

### Adding New Grammar Rules
1. Edit `grammar_config.json`
2. Add patterns to `common_errors` section
3. Define pattern, suggestion, and confidence level
4. Restart PyLine to apply changes

### Modifying Writing Style Preferences
Adjust thresholds in `writing_style_rules`:
- `sentence_length`: Ideal sentence length ranges
- `readability`: Score thresholds for different levels
- `vocabulary`: Diversity and richness targets

## Uninstallation

```bash
# Remove hook files
rm ~/.pyline/hooks/editing_ops/search_replace/grammar_checker__70.py
rm ~/.pyline/hooks/editing_ops/search_replace/grammar_config.json
```

## License

GNU GPL v3+ - See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) for details.

## Compatibility

- **Python**: 3.6+
- **PyLine**: Version 1.1.0
- **Systems**: Cross-platform (WSL, Linux, macOS)
- **Dependencies**: language-tool-python, pandas, numpy

---

*Enhance your writing with AI-powered grammar checking directly in PyLine!*
