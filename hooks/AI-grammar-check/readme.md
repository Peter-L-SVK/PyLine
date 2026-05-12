# Grammar Checker Hook for PyLine

## Overview

A statistical AI-assisted grammar and spell checking hook for PyLine that leverages the built-in NLP models in LanguageTool and statistical algorithms in pyspellchecker for accurate grammar and spelling detection.

## Features

- **Professional Grammar Checking**: Uses LanguageTool's built-in AI/statistical models for comprehensive grammar, style, and confused word detection
- **Multi-Layer Spell Checking**: LanguageTool + pyspellchecker for thorough spell checking with no duplicates
- **Readability Statistics**: Flesch Reading Ease, Flesch-Kincaid Grade Level, Gunning Fog Index via textstat
- **Line Number Tracking**: Shows exact line numbers and highlighted context for each issue
- **Configurable Rules**: JSON-based configuration for disabled rules, technical vocabulary, and output preferences
- **Technical Content Filtering**: Automatically skips code blocks, markdown headers, and technical content
- **Zero False Positives on Technical Terms**: Custom vocabulary support for programming terms, abbreviations, and technical jargon

## Installation

### Quick Install
```bash
# Install dependencies
pip install language-tool-python pyspellchecker textstat

# Create the hook directory
mkdir -p ~/.pyline/hooks/editing_ops/process_content/

# Copy the hook files
cp grammar_checker__70.py ~/.pyline/hooks/editing_ops/process_content/
cp grammar_config.json ~/.pyline/hooks/editing_ops/process_content/

# Set execute permissions
chmod +x ~/.pyline/hooks/editing_ops/process_content/grammar_checker__70.py
```

## Dependencies

### Required Python Packages
```bash
pip install language-tool-python pyspellchecker textstat
```

| Package | Purpose | License |
|---------|---------|---------|
| **language-tool-python** | Primary grammar + spelling checker with built-in AI/statistical models | LGPL 2.1+ |
| **pyspellchecker** | Secondary spell checker using edit distance and word frequency algorithms | MIT |
| **textstat** | Readability statistics using established statistical formulas | MIT |

## Usage

The hook automatically integrates with PyLine's content processing. Press `g` in the editor to run grammar check on the current file.

## Output Example

```
============================================================
PYLINE GRAMMAR & SPELL CHECKER
============================================================

📊 TEXT STATISTICS:
  Words: 227
  Sentences: 17
  Avg. Sentence Length: 13.4 words
  Readability (Flesch): 64.0/100
  Grade Level: 7.7

🔍 ISSUES FOUND: 13 total (6 grammar + 7 spelling)

📝 GRAMMAR ISSUES:
  Line 2: Did you mean "there"?
    📍 "...World of Berry Fruits **Their** are many different types of berry..."
    💡 There
  Line 2: Use "an" instead of 'a'
    📍 "...true berry but a aggregate fruit. **Its** interesting to learn..."
    💡 an
  Line 4: Did you mean "your"?
    📍 "...very good for **you're** health. They contain many antioxidants..."
    💡 your
  Line 5: Comparison requires "than", not 'then'
    📍 "...taste of fresh, ripe berrys more **then** anything else..."
    💡 than

🔤 SPELLING ISSUES:
  Line 2: Spelling: 'bery' → 'very'
    📍 "...My favorite type of **bery** is the strawberry, which are actually..."
    💡 very
  Line 2: Spelling: 'berrys' → 'berries'
    📍 "...to learn about how **berrys** grow and their nutritional benefits..."
    💡 berries

📝 WRITING TIPS:
  • Average sentence length (13.4) is short. Consider combining some sentences.
============================================================
```

## Configuration

### Customizing via `grammar_config.json`

```json
{
  "language_tool": {
    "disabled_rules": [
      "EN_QUOTES",
      "COMMA_PARENTHESIS_WHITESPACE",
      "WHITESPACE_RULE",
      "EN_UNPAIRED_BRACKETS",
      "UPPERCASE_SENTENCE_START"
    ],
    "language": "en-US"
  },
  
  "content_filters": {
    "exclude_lines_matching": [
      "^#", "^##", "^###",
      "^```", "^    ", "^\\t",
      "^//", "^<!--",
      "\\[IMPLEMENTED\\]",
      "^\\s*$"
    ]
  },
  
  "technical_vocabulary": [
    "PyLine", "JSON", "XML", "HTML", "API", "CLI", "GUI",
    "Python", "JavaScript", "Java", "C++", "regex", "config"
  ],
  
  "spellcheck": {
    "enabled": true,
    "max_suggestions": 5,
    "distance": 2,
    "ignore_patterns": [
      "^[A-Z]{2,}$",
      "^[A-Z][a-z]+[A-Z]\\w*$",
      "^\\d+$"
    ]
  },
  
  "output_settings": {
    "max_issues": 30,
    "show_statistics": true,
    "show_readability": true,
    "show_spelling": true,
    "show_writing_tips": true
  },
  
  "writing_tips": {
    "readability_threshold": 60,
    "sentence_length_ideal": [15, 20]
  }
}
```

### Configuration Options

| Section | Key | Description |
|---------|-----|-------------|
| `language_tool` | `disabled_rules` | LanguageTool rules to skip |
| `language_tool` | `language` | Language code (e.g., "en-US") |
| `content_filters` | `exclude_lines_matching` | Regex patterns for lines to skip |
| `technical_vocabulary` | - | Words to ignore in spell checking |
| `spellcheck` | `enabled` | Enable/disable pyspellchecker |
| `spellcheck` | `max_suggestions` | Number of spelling suggestions |
| `spellcheck` | `distance` | Edit distance for spell checking (1-3) |
| `output_settings` | `max_issues` | Maximum issues to display |
| `output_settings` | `show_statistics` | Show word/sentence counts |
| `output_settings` | `show_readability` | Show readability scores |
| `output_settings` | `show_spelling` | Show spelling issues |
| `output_settings` | `show_writing_tips` | Show writing improvement tips |
| `writing_tips` | `readability_threshold` | Score below which to suggest improvements |
| `writing_tips` | `sentence_length_ideal` | Ideal sentence length range [min, max] |

## Supported Checks

### Grammar & Style (via LanguageTool's AI/statistical models)
- Article usage (a/an/the)
- Confused words (their/there/they're, your/you're, its/it's, then/than, etc.)
- Subject-verb agreement
- Punctuation errors
- Redundant phrases
- Style suggestions
- And hundreds more built-in rules

### Spelling
- **Primary**: LanguageTool's MORFOLOGIK rule
- **Secondary**: pyspellchecker's edit distance and word frequency algorithms
- **Automatic deduplication** between checkers

### Readability (via textstat's statistical formulas)
- Flesch Reading Ease
- Flesch-Kincaid Grade Level
- Gunning Fog Index
- Difficult word count
- Average sentence length

## Technical Details

**Hook Type**: `editing_ops/process_content`  
**Priority**: 75  
**Language**: Python 3.8+  
**Modules**: language-tool-python, pyspellchecker, textstat

### How It Works

1. **Content Filtering**: Technical content (code, headers, comments) is filtered out
2. **Grammar Checking**: LanguageTool analyzes text using its built-in statistical NLP models and rule-based engine
3. **Spell Checking**: pyspellchecker uses edit distance algorithms and word frequency analysis for additional coverage
4. **Deduplication**: Words flagged by LanguageTool are skipped by pyspellchecker to avoid duplicates
5. **Readability Analysis**: textstat calculates established readability formulas
6. **Output Formatting**: Issues are sorted by line number with highlighted context

## Performance

- **First Run**: 2-3 seconds to download LanguageTool data (one-time)
- **Subsequent Runs**: Fast processing
- **Memory**: ~50MB (LanguageTool)
- **No Java Required**: Uses LanguageTool's Python server

## Troubleshooting

### Missing Dependencies
```bash
pip install language-tool-python pyspellchecker textstat
```

### LanguageTool First-Run Download
```bash
# First run downloads language data (~200MB)
python -c "import language_tool_python; language_tool_python.LanguageTool('en-US')"
```

### Config File Issues
```bash
# Validate JSON config
python -c "import json; json.load(open('grammar_config.json')); print('Valid JSON')"
```

### Hook Not Running
```bash
# Test the hook directly
cd ~/.pyline/hooks/editing_ops/process_content/
python grammar_checker__70.py

# Check permissions
chmod +x grammar_checker__70.py
```

## Uninstallation

```bash
rm ~/.pyline/hooks/editing_ops/process_content/grammar_checker__70.py
rm ~/.pyline/hooks/editing_ops/process_content/grammar_config.json
```

## License

GNU GPL v3+ - See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) for details.

### Third-Party Components

| Component | License | Usage |
|-----------|---------|-------|
| **LanguageTool** | LGPL 2.1+ | Grammar checking engine with built-in AI/statistical models |
| **pyspellchecker** | MIT | Secondary spell checker (edit distance + frequency analysis) |
| **textstat** | MIT | Readability analysis (established statistical formulas) |

## Compatibility

- **Python**: 3.8+
- **PyLine**: Version 1.1.0+
- **Systems**: Cross-platform (Linux, BSD, macOS, WSL)

---

*Professional grammar checking for PyLine - simple, universal, configurable.*
