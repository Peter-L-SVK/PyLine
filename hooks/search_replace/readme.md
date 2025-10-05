# PyLine Search & Replace Hook

A powerful Perl-based search and replace hook for PyLine that provides incremental search with highlighting, whole word matching, and sed-style batch replacement.

## Overview

This hook replaces PyLine's built-in search functionality with enhanced features including line-numbered results, match highlighting, whole word matching, context display, and batch replacement capabilities. It demonstrates PyLine's cross-language capabilities by using Perl for robust text processing.

## Features

### 🔍 Search Mode
- **Incremental Search**: Real-time results as you type
- **Line Numbering**: Shows exact line numbers for all matches
- **Match Highlighting**: Blue background highlighting for search terms
- **Whole Word Matching**: Option to match only complete words
- **Context Display**: Shows full lines with matches in context
- **Match Statistics**: Counts total matches and affected lines
- **Clean Formatting**: Professional output with separators

### 🔄 Replace Mode  
- **Batch Replacement**: Replace all occurrences in one operation
- **Sed-Style Syntax**: Familiar `s/search/replace/g` behavior
- **Whole Word Replacement**: Replace only complete words, not partial matches
- **Match Counting**: Shows matches found vs replacements made
- **Safe Operation**: Returns modified content without altering original files
- **Undo Support**: Works with PyLine's undo system

### 🎯 Smart Features
- **Literal String Matching**: No regex surprises by default
- **Whole Word Detection**: Automatic word boundary detection
- **Cross-Platform**: Works anywhere Perl 5+ is available
- **Priority 75**: Overrides built-in search while allowing customization
- **JSON Integration**: Seamless communication with PyLine core

## Installation

### Quick Install (Recommended)
```bash
# Run the master installer from the directory containing all hook files
./install-all-hooks.sh
```

### Manual Installation
```bash
# Create search_replace directory
mkdir -p ~/.pyline/hooks/event_handlers/search_replace/

# Copy the hook file
cp search_replace__75.pl ~/.pyline/hooks/event_handlers/search_replace/

# Set execute permissions
chmod +x ~/.pyline/hooks/event_handlers/search_replace/search_replace__75.pl
```

## Usage

### Search-Only Mode
1. **Start Search**: Press `Ctrl+Alt+F` in PyLine
2. **Enter Pattern**: Type your search term (use `\b` prefix for whole words)
3. **View Results**: All matching lines displayed with highlighting

**Example Output:**
```
Search results for: function
================================================================================
Line   12: def my_function(args):
Line   25:     function_result = process_data()
Line   33:     return function_result
Line   47: function cleanup():
================================================================================
4 matches for 'function' found in 4 lines.
```

**Whole Word Example:**
```
Search results for whole word: function
================================================================================
Line   47: function cleanup():
================================================================================
1 whole word matches for 'function' found in 1 lines.
```

### Search & Replace Mode
1. **Start Replace**: Press `Ctrl+Alt+R` in PyLine  
2. **Enter Search**: Type text to find (use `\b` prefix for whole words)
3. **Enter Replacement**: Type replacement text
4. **Execute**: All occurrences are replaced

**Example Output:**
After replacement, PyLine shows:
```
"15 occurrences of 'colour' replaced out of 15 matches."
```

**Whole Word Example:**
```
"3 occurrences of whole word 'ham' replaced out of 3 matches."
```

## Whole Word Matching

### Syntax
Prefix your search term with `\b` to enable whole word matching:

- **`ham`** - Matches ALL occurrences: "ham", "hamster", "hamburger"
- **`\bham`** - Matches ONLY whole words: "ham" but NOT "hamster" or "hamburger"

### Examples

#### Basic Search Examples:
```
Search: cat
Matches: "cat", "category", "concatenate", "catastrophe"

Search: \bcat
Matches: "cat" but NOT "category", "concatenate", "catastrophe"
```

#### Real-World Use Cases:
```
Search: \bham
- ✅ Matches: "I eat ham", "ham sandwich", "the ham is good"
- ❌ Does NOT match: "hamster", "hamburger", "shaman", "tham"

Search: \berror
- ✅ Matches: "error occurred", "fix the error", "error:"
- ❌ Does NOT match: "error_count", "terror", "errors", "error_404"

Search: \bfunction
- ✅ Matches: "function main()", "the function returns"
- ❌ Does NOT match: "my_function", "functional", "defunctionalize"
```

## Examples

### Basic Search
```
Search for: error
────────────────────────────────────────────────────────────────────────────────
Line   45: if error_count > 0:
Line   89:     log_error("Operation failed")
Line   92:     raise RuntimeError("Critical failure")
────────────────────────────────────────────────────────────────────────────────
3 matches for 'error' found in 3 lines.
```

### Whole Word Search
```
Search for whole word: error
────────────────────────────────────────────────────────────────────────────────
Line  156:     print("error: invalid input")
Line  189:     return error
────────────────────────────────────────────────────────────────────────────────
2 whole word matches for 'error' found in 2 lines.
```

### Case Conversion with Whole Words
```
Search: \busername  
Replace: USERNAME

"5 occurrences of whole word 'username' replaced out of 5 matches."
```

### Multi-line Replacement
```
Search: \bdef old_function
Replace: def new_function

"3 occurrences of whole word 'def old_function' replaced out of 3 matches."
```

## Technical Details

### Hook Configuration
- **Type**: `event_handlers/search_replace`
- **Priority**: 75 (overrides built-in search)
- **Language**: Perl 5
- **Dependencies**: JSON::PP (Perl core module)

### How It Works

#### Search Mode:
1. PyLine sends search request as JSON
2. Hook detects `\b` prefix for whole word matching
3. Processes all lines with appropriate pattern
4. Returns formatted results directly to STDOUT
5. PyLine displays the pre-formatted output

#### Replace Mode:
1. PyLine sends search/replace request as JSON  
2. Hook detects `\b` prefix and uses word boundaries
3. Performs global replacement on all lines
4. Returns modified content as JSON
5. PyLine updates buffer and provides undo support

### Match Algorithm
```perl
# Normal matching (all occurrences)
$search_pattern = qr/\Q$search\E/;

# Whole word matching (with \b prefix)
$search_pattern = qr/\b\Q$actual_search\E\b/;

# Match counting
my $matches = () = $line =~ /$search_pattern/g;
```

### Word Boundary Logic
The hook automatically detects when to use word boundaries:
- **Search starts with `\b`**: Enables whole word matching
- **Removes the `\b` prefix** from the actual search term
- **Uses `\b...\b`** in the regex pattern for word boundaries
- **Works with any search term** that doesn't contain regex metacharacters

## Advanced Usage

### Testing the Hook Directly
```bash
# Test normal search mode
echo '{"search":"test","lines":["test line","testing","contest"]}' | \
perl search_replace__75.pl

# Test whole word search mode
echo '{"search":"\\btest","lines":["test line","testing","contest"]}' | \
perl search_replace__75.pl

# Test replace mode with whole words
echo '{"search":"\\bham","replace":"HAM","lines":["ham","hamster","hamburger"]}' | \
perl search_replace__75.pl
```

### Integration with Other Tools
The hook can be used standalone for batch processing:
```bash
# Similar functionality using Perl one-liner
cat file.txt | perl -pe 's/\bham\b/HAM/g'
```

## Customization

### Modifying Highlight Colors
Edit the `ansi_highlight` subroutine:
```perl
# Current: blue background, white text
return "\033[44m\033[97m$text\033[0m";

# Change to red background, yellow text
return "\033[41m\033[93m$text\033[0m";

# Change to green background, black text  
return "\033[42m\033[30m$text\033[0m";
```

### Adding Additional Matching Modes
You can extend the prefix system for other modes:
```perl
# Add case-insensitive matching with \i prefix
if ($search =~ s/^\\i//) {
    $search_pattern = qr/\Q$actual_search\E/i;
}

# Add regex mode with \r prefix  
if ($search =~ s/^\\r//) {
    $search_pattern = qr/$actual_search/;
}
```

## Performance

- **Optimized**: Processes typical files (≤10,000 lines) instantly
- **Memory Efficient**: Processes lines sequentially
- **Word Boundaries**: Minimal performance impact
- **Large Files**: May slow with files >50,000 lines
- **Binary Safe**: Handles any text content safely

## Troubleshooting

### Hook Not Loading
```bash
# Check installation
ls -la ~/.pyline/hooks/event_handlers/search_replace/

# Verify permissions
chmod +x ~/.pyline/hooks/event_handlers/search_replace/search_replace__75.pl

# Test Perl
perl -v
```

### Whole Word Matching Not Working
- Ensure you use the `\b` prefix exactly
- Check that your search term doesn't contain spaces
- Verify the word exists as a standalone term in your text
- Whole word matching uses `\b` which matches word boundaries (alphanumeric transitions)

### No Results Found
- Search is case-sensitive
- Whole word matching requires exact word boundaries
- Check for trailing spaces in search term
- Verify file contains the search text as complete words

### Replacement Not Working
- Hook returns modified content to PyLine
- PyLine must apply the changes to buffer
- Check PyLine's undo stack for changes
- Verify hook returns `handled_output => 1`

### Colors Not Displaying
- Terminal must support ANSI colors
- Check `TERM` environment variable
- Verify PyLine isn't stripping ANSI codes

## Uninstallation

### Remove Hook
```bash
rm ~/.pyline/hooks/event_handlers/search_replace/search_replace__75.pl
```

PyLine will automatically fall back to built-in search functionality.

### Using Master Uninstaller
```bash
./uninstall-all-hooks.sh
```

## Compatibility

- **PyLine**: 0.9.7+
- **Perl**: 5.8+ (JSON::PP required)
- **Systems**: Linux, macOS, BSD, WSL (with Perl)
- **Terminals**: Any supporting ANSI color codes

## Dependencies

- **Perl 5**: Usually pre-installed on Unix-like systems
- **JSON::PP**: Core Perl module (no additional installation)
- **No external CPAN modules required**

## License

GNU GPL v3+ - Same as PyLine

## Source Code

The hook is a single self-contained Perl file with:
- No external dependencies
- Comprehensive error handling
- JSON input/output processing
- ANSI color support
- Whole word matching via `\b` prefix
- Cross-platform compatibility

---

**Pro Tip**: Use whole word matching (`\b` prefix) for refactoring tasks to avoid accidentally replacing parts of larger words. Perfect for renaming variables, functions, or standardizing terminology without affecting similar-looking words.
