# Emoji Replacer Hook for PyLine

A Perl-based hook that automatically replaces letters with emojis during text editing in PyLine. Perfect for adding visual flair to your text or creating fun, expressive content.

This hook demonstrates PyLine's powerful post-edit processing capabilities by transforming text immediately after editing, providing real-time visual feedback.

## Features

- **Real-time Replacement**: Converts letters to emojis as you type
- **Case-Insensitive**: Works with both uppercase and lowercase letters
- **UTF-8 Support**: Full emoji and Unicode character support
- **Non-Destructive**: Only affects displayed text, original files remain unchanged
- **Priority 80**: Balanced priority that allows customization
- **Cross-Platform**: Works on any system with Perl 5+

## Emoji Mappings

- `g` / `G` → 🦒 (giraffe)
- `h` / `H` → 🐹 (hamster)

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
mkdir -p ~/.pyline/hooks/editing_ops/post_edit/

# Copy the hook file
cp emoji_replacer__80.pl ~/.pyline/hooks/editing_ops/post_edit/

# Set execute permissions
chmod +x ~/.pyline/hooks/editing_ops/post_edit/emoji_replacer__80.pl
```

## Usage

The hook works automatically! Once installed:

1. Open any file in PyLine
2. Edit any line (press Enter on a line to edit)
3. Press Enter again to finish editing
4. The hook will automatically replace letters with emojis

### Example Transformation
**Before editing**:
```
Hello world
This is a test
ghost hunter
```

**After editing** (just press Enter without changes):
```
🐹ello world
T🐹is is a test
🦒🐹ost 🐹unter
```

## How It Works

**Trigger**: `post_edit` event (after line editing is complete)  
**Action**: Replaces specific letters with corresponding emojis  
**Scope**: Affects all lines edited in PyLine  

## Uninstallation

```bash
rm ~/.pyline/hooks/editing_ops/post_edit/emoji_replacer__80.pl
```

PyLine will immediately stop replacing letters with emojis after removal.

## Requirements

- **Perl 5+** (usually pre-installed on Linux/BSD/macOS)
- **JSON::PP module** (Perl core module, no additional installation needed)
- PyLine 1.1+

## Technical Details

**Hook Type**: `editing_ops/post_edit`  
**Priority**: 80 (can be overridden by higher-priority hooks)  
**Language**: Perl 5  
**License**: GNU GPL v3+  

## Testing

Test the hook directly with sample content:
```bash
echo '{"action":"post_edit","new_text":"test gh","line_number":1,"filename":"test.txt"}' | perl emoji_replacer__80.pl
```

Expected output: `{"new_text":"test 🦒🐹"}`

## Customization

Want different emoji mappings? Edit the Perl script:

```perl
# Change these lines in the script:
$text =~ s/g/🦒/gi;  # Change 🦒 to your preferred emoji
$text =~ s/h/🐹/gi;  # Change 🐹 to your preferred emoji
```

## Important Notes

- **Only affects edited lines** - lines you don't edit remain unchanged
- **Real-time transformation** - happens immediately after editing
- **Undo support** - use Ctrl+B to undo changes if needed
- **Works with all file types** - affects any text you edit in PyLine

## Troubleshooting

### Hook not working?
```bash
# Check permissions
chmod +x ~/.pyline/hooks/editing_ops/post_edit/emoji_replacer__80.pl

# Test Perl installation
perl -v

# Test the hook directly
echo '{"action":"post_edit","new_text":"test gh"}' | perl emoji_replacer__80.pl
```

### Want to disable temporarily?
```bash
# Rename with underscore prefix to disable
mv ~/.pyline/hooks/editing_ops/post_edit/emoji_replacer__80.pl \
   ~/.pyline/hooks/editing_ops/post_edit/_emoji_replacer__80.pl
```

### Want to enable again?
```bash
# Remove underscore prefix to enable
mv ~/.pyline/hooks/editing_ops/post_edit/_emoji_replacer__80.pl \
   ~/.pyline/hooks/editing_ops/post_edit/emoji_replacer__80.pl
```

Or use Hook Manager directly in PyLine for enabling and disabling hooks.

## License

GNU GPL v3+ - See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) for details.

---
