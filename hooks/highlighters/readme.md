# PyLine Syntax Highlighters

Enhanced syntax highlighting for JSON and Shell scripts in PyLine editor.

## Overview

Two powerful syntax highlighters that provide rich, color-coded display for JSON configuration files and shell scripts (bash, zsh, ksh, sh, fish). These hooks integrate seamlessly with PyLine's theme system and provide language-aware highlighting.

## Features

### JSON Highlighter (`json_highlight__60.py`)

- **Key/Value Distinction**: Different colors for JSON keys vs values
- **Type-Aware Coloring**: 
  - Strings (green)
  - Numbers (magenta) 
  - Boolean values (blue)
  - Null values (blue)
- **Structure Highlighting**:
  - Braces and brackets (cyan)
  - Colons (yellow)
  - Commas (gray)
- **Smart Context Detection**: Knows when to expect keys vs values
- **Priority 60**: Runs before most other highlighters

### Shell Highlighter (`shell_highlight__70.py`)

- **Multi-Shell Support**: bash, zsh, ksh, sh, fish
- **Comprehensive Syntax Coverage**:
  - Function declarations (purple)
  - Variable declarations (cyan)
  - Variable usage (yellow)
  - Shell keywords (blue)
  - Built-in commands (purple)
  - Strings (green)
  - Comments (cyan)
- **Smart Detection**:
  - Avoids highlighting variables inside strings
  - Handles quoted strings and escapes properly
  - Recognizes multiple function declaration styles
- **Priority 70**: Balanced priority for shell files

## Installation

### Quick Install (Recommended)
```bash
# Run the master installer from the directory containing all hook files
./install-all-hooks.sh
```

### Manual Installation
```bash
# Create syntax handlers directory
mkdir -p ~/.pyline/hooks/syntax_handlers/highlight/

# Copy highlighters
cp json_highlight__60.py shell_highlight__70.py ~/.pyline/hooks/syntax_handlers/highlight/

# Set execute permissions
chmod +x ~/.pyline/hooks/syntax_handlers/highlight/*.py
```

## Usage

The highlighters work automatically! Once installed:

### JSON Files
Open any `.json` file in PyLine:
```bash
pyline config.json
```

**Example Output:**
```
{
  "name": "John Doe",
  "age": 30,
  "active": true,
  "tags": ["developer", "python"],
  "address": {
    "street": "123 Main St",
    "city": "Boston"
  }
}
```

*Keys are blue, strings are green, numbers are magenta, booleans are blue, structure is cyan*

### Shell Files
Open any shell script in PyLine:
```bash
pyline script.sh
```

**Example Output:**
```bash
#!/bin/bash
# This is a comment

NAME="John"
AGE=30

function greet() {
    echo "Hello $NAME, you are $AGE years old"
}

if [ $AGE -gt 18 ]; then
    greet
else
    echo "Too young"
fi
```

*Functions are purple, variables are cyan/yellow, keywords are blue, strings are green, comments are cyan*

## Supported File Types

### JSON Highlighter
- `.json` files only

### Shell Highlighter
- `.sh` - Bash scripts
- `.bash` - Bash scripts  
- `.zsh` - Zsh scripts
- `.ksh` - Korn shell scripts
- `.fish` - Fish shell scripts
- **Also works on files without extensions** that have shell shebangs

## Customization

### Theme Integration
Both highlighters integrate with PyLine's theme manager. They use the following color mappings:

**JSON Highlighter:**
- `keyword` → JSON keys
- `string` → String values
- `number` → Numeric values  
- `variable` → Boolean and null values
- `class` → Braces and brackets
- `decorator` → Colon separator
- `annotation` → Commas

**Shell Highlighter:**
- `keyword` → Shell keywords (if, then, for, while, etc.)
- `string` → Quoted strings
- `comment` → Comments and shebangs
- `function` → Function names and built-in commands
- `variable` → Variable usage ($VAR, ${VAR})
- `class` → Variable declarations

### Fallback Colors
If theme manager is unavailable, both highlighters provide sensible fallback ANSI colors.

## Technical Details

### JSON Highlighter Algorithm
1. **String Detection**: Finds quoted strings and determines if they're keys or values
2. **Number Detection**: Identifies integers, floats, and scientific notation
3. **Keyword Detection**: Finds `true`, `false`, and `null` values
4. **Context Tracking**: Maintains state to know when to expect keys vs values
5. **Structure Highlighting**: Colors braces, brackets, colons, and commas

### Shell Highlighter Phases
1. **Full-line comments** (including shebangs)
2. **Function declarations** (3 different styles)
3. **Variable declarations** (6 declaration types)
4. **Partial comments** (comments after code)
5. **String highlighting** (single and double quotes)
6. **Variable usage** (outside of strings)
7. **Keywords and builtins** (avoiding string contexts)

## Troubleshooting

### Highlighting Not Working
```bash
# Check if hooks are installed
ls ~/.pyline/hooks/syntax_handlers/highlight/

# Verify permissions
chmod +x ~/.pyline/hooks/syntax_handlers/highlight/*.py

# Test Python environment
python3 --version
```

### Colors Not Appearing
- Ensure your terminal supports 256 colors
- Check if PyLine theme manager is functioning
- Verify the file has the correct extension

### Performance Issues
- Both highlighters are optimized for performance
- Complex files with many nested structures may be slightly slower
- Consider disabling if editing very large files (>10,000 lines)

## Uninstallation

### Remove Specific Highlighter
```bash
# Remove JSON highlighter
rm ~/.pyline/hooks/syntax_handlers/highlight/json_highlight__60.py

# Remove Shell highlighter  
rm ~/.pyline/hooks/syntax_handlers/highlight/shell_highlight__70.py
```

### Remove All Highlighters
```bash
# Use the master uninstaller
./uninstall-all-hooks.sh

# Or manually remove the directory
rm -rf ~/.pyline/hooks/syntax_handlers/highlight/
```

## Testing

### Test JSON Highlighter
```bash
# Create a test JSON file
echo '{"name": "test", "value": 42, "active": true}' > test.json
pyline test.json
```

### Test Shell Highlighter  
```bash
# Create a test shell script
cat > test.sh << 'EOF'
#!/bin/bash
NAME="test"
echo "Hello $NAME"
EOF
pyline test.sh
```

## Compatibility

- **PyLine**: Version 0.9.7+
- **Python**: 3.6+ (for both highlighters)
- **Systems**: Linux, macOS, BSD, WSL
- **Terminals**: Any terminal with ANSI color support

## License

GNU GPL v3+ - Same as PyLine

## Source Code

Both highlighters are self-contained Python files with no external dependencies, making them easy to audit and modify.

---

**Note**: These highlighters work alongside PyLine's built-in syntax highlighting system. If both are enabled, the hook-based highlighting takes precedence based on priority settings.
