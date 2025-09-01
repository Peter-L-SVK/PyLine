# Lowercase to Uppercase Conversion Hook for PyLine

A Perl-based hook that automatically converts all lowercase letters to uppercase when files are opened in PyLine. Perfect for creating consistent uppercase content or working with systems that require uppercase text.
This hook demonstrates PyLine's powerful file preprocessing capabilities. Since it operates at the `pre_load` stage, it can transform content before the user ever sees it, making it perfect for automatic content normalization tasks.

## Features

- **Automatic Conversion**: Converts all lowercase to uppercase on file load
- **UTF-8 Support**: Properly handles Unicode characters
- **Smart File Handling**: Works with both new and existing files
- **Priority 80**: Balanced priority that allows override by specialized hooks
- **Cross-Platform**: Works on any system with Perl 5+

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
mkdir -p ~/.pyline/hooks/event_handlers/pre_load/

# Copy the hook file
cp lowercase_to_uppercase__80.pl ~/.pyline/hooks/event_handlers/pre_load/

# Set execute permissions
chmod +x ~/.pyline/hooks/event_handlers/pre_load/lowercase_to_uppercase__80.pl
```

## Usage

The hook works automatically! Once installed:

1. Open any file in PyLine using:
   - Menu option `1` (Edit existing file)
   - Command line: `pyline filename.txt`
   - Or any other file loading method

2. The file content will be automatically converted to uppercase
3. Edit and save as normal - the uppercase conversion happens only on load

## How It Works

**Trigger**: `pre_load` event (before file content is displayed)  
**Action**: Converts all lowercase characters to uppercase  
**Scope**: Affects all files opened in PyLine  

### Example Transformation
**Input**:
```
hello world
this is a test
123 mixed CASE Example
```

**Output**:
```
HELLO WORLD
THIS IS A TEST
123 MIXED CASE EXAMPLE
```
## Uninstallation

```bash
rm ~/.pyline/hooks/event_handlers/pre_load/lowercase_to_uppercase__80.pl
```

PyLine will immediately stop converting text to uppercase after removal.


## Requirements

- **Perl 5+** (usually pre-installed on Linux/BSD/macOS)
- **JSON module** (Perl core module, no additional installation needed)
- PyLine 0.9.7+

## Technical Details

**Hook Type**: `event_handlers/pre_load`  
**Priority**: 80 (can be overridden by higher-priority hooks)  
**Language**: Perl 5  
**License**: GNU GPL v3+  

## Testing

Test the hook directly with sample content:
```bash
echo '{"action":"pre_load","filename":"test.txt","content":"hello world"}' | perl lowercase_to_uppercase__80.pl
```

Expected output: `HELLO WORLD`

## Important Notes

- **This affects ALL files opened in PyLine** - use selectively
- **Conversion happens on LOAD only** - saving preserves your edited case
- **Original files are not modified** - only the in-memory content is changed
- **Works with new files** - affects files created within PyLine too

## Troubleshooting

### Hook not working?
```bash
# Check permissions
chmod +x ~/.pyline/hooks/event_handlers/pre_load/lowercase_to_uppercase__80.pl

# Test Perl installation
perl -v

# Test the hook directly
echo '{"action":"pre_load","content":"test"}' | perl lowercase_to_uppercase__80.pl
```

### Want to disable temporarily?
```bash
# Rename with underscore prefix to disable
mv ~/.pyline/hooks/event_handlers/pre_load/lowercase_to_uppercase__80.pl \
   ~/.pyline/hooks/event_handlers/pre_load/_lowercase_to_uppercase__80.pl
```

### Want to enable again?
```bash
# Remove underscore prefix to enable
mv ~/.pyline/hooks/event_handlers/pre_load/_lowercase_to_uppercase__80.pl \
   ~/.pyline/hooks/event_handlers/pre_load/lowercase_to_uppercase__80.pl
```
Or use Hook Manager directly in PyLine for enabling and disabling hooks

## License

GNU GPL v3+ - See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) for details.

---
