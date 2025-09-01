# Word Counter Hook for PyLine

A Perl-based hook that replaces PyLine's built-in word counting functionality with a more precise, cross-platform solution using Perl's robust text processing capabilities.
This hook demonstrates PyLine's cross-language capabilities by using Perl for text processing while maintaining full compatibility with the Python-based editor.

## Features

- **Accurate Word Counting**: Uses Perl's regex engine for precise word detection
- **Multi-Platform**: Works on any system with Perl 5+
- **Unicode Support**: Properly handles UTF-8 text
- **WC-Compatible**: Follows standard `wc` command behavior
- **Priority 80**: Overrides built-in counter while allowing higher-priority hooks to take precedence

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
mkdir -p ~/.pyline/hooks/event_handlers/word_count/

# Copy the hook file
cp word_counter__80.pl ~/.pyline/hooks/event_handlers/word_count/

# Set execute permissions
chmod +x ~/.pyline/hooks/event_handlers/word_count/word_counter__80.pl
```

##  Usage

The hook automatically integrates with PyLine's `cw` (count words) command. No additional steps required!

1. Open PyLine
2. Type `cw` in the main menu
3. Select a file to analyze
4. The Perl hook will process and display results instead of the built-in counter

## Output Example

```
************************************************************
example.txt contains (Perl hook):
- 153 words
- 12 lines  
- 842 characters
************************************************************
```

## Uninstallation

```bash
rm ~/.pyline/hooks/event_handlers/word_count/word_counter__80.pl
```

PyLine will automatically fall back to the built-in word counter after removal.

## Requirements

- **Perl 5+** (usually pre-installed on Linux/BSD/macOS)
- **JSON::PP** module (Perl core module, no additional installation needed)
- PyLine 0.9.7+

## Technical Details

**Hook Type**: `event_handlers/word_count`  
**Priority**: 80 (overrides built-in but allows higher-priority hooks)  
**Language**: Perl 5  
**License**: GNU GPL v3+  

### How It Works

1. PyLine calls the `cw` command
2. Hook system executes all `word_count` handlers by priority
3. This hook (priority 80) processes the request and outputs results
4. If hook returns success, built-in counter (lower priority) is skipped

## 🧪 Testing

Test the hook directly:
```bash
echo '{"action":"count_words","filename":"test.txt","file_content":"Hello world\nThis is a test"}' | perl word_counter__80.pl
```

## Troubleshooting

### Hook not loading?
```bash
# Check permissions
chmod +x ~/.pyline/hooks/event_handlers/word_count/word_counter__80.pl

# Test Perl installation
perl -v
```

### No output?
```bash
# Test the hook directly
echo '{"action":"count_words","file_content":"test"}' | perl word_counter__80.pl
```

## License

GNU GPL v3+ - See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) for details.

---
