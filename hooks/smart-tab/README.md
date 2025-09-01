# Smart Tab Hook for PyLine

## Overview

A smart tab handling hook for PyLine that converts tab characters to appropriate spaces based on file type, with intelligent indentation suggestions and graceful Ctrl-C handling.

## Features

- **Smart Tab Conversion**: Converts `\t` to appropriate number of spaces (4 for Python, 2 for JS/HTML, etc.)
- **Intelligent Indentation**: Suggests proper indentation based on code context
- **Graceful Ctrl-C Handling**: Clean exit with visual feedback when cancelling edits
- **File Type Awareness**: Different indentation rules for different file extensions
- **No External Dependencies**: Uses built-in Python modules only

## Installation

**Install the hook**:
 ```bash
 ./install.sh
 ```

## File Location

```
~/.pyline/hooks/input_handlers/edit_line/smart_tab__90.py
```

## Supported File Types and Indentation (can be changed manually)

| File Type | Extensions | Spaces |
|-----------|------------|--------|
| Python | `.py`, `.python` | 4 |
| C/C++ | `.c`, `.h`, `.cpp` | 2 |
| Java | `.java` | 4 |
| JavaScript/TypeScript | `.js`, `.ts` | 2 |
| Web | `.html`, `.css` | 2 |
| Data | `.json` | 2 |
| Config | `.yml`, `.yaml` | 2 |
| XML | `.xml` | 2 |
| Ruby | `.rb` | 2 |
| PHP | `.php` | 4 |
| Go | `.go` | 4 |
| Rust | `.rs` | 4 |
| Shell | `.sh`, `.bash` | 4 |
| Default | (all others) | 4 |

## Intelligent Indentation Rules

### Increase Indentation (after these patterns):
- `:` at line end (Python: if, for, while, def, class, etc.)
- `{` at line end (opening brace)
- `(` at line end (opening parenthesis)
- `[` at line end (opening bracket)
- `\` at line end (line continuation)

### Decrease Indentation (before these patterns):
- `}` at line start (closing brace)
- `)` at line start (closing parenthesis)
- `]` at line start (closing bracket)
- `else` statement
- `elif` statement
- `except` clause
- `finally` clause

## Usage

1. **Open a file with PyLine**:
   ```bash
   pyline filename.py
   ```

2. **Edit a line** by pressing `E` or `Enter`

3. **Press Tab** to insert appropriate indentation:
   - In Python files: 4 spaces
   - In JavaScript files: 2 spaces
   - etc.

4. **Cancel editing** with `Ctrl+C` - returns to editor without changes

## Behavior Examples

### Normal Editing:
```
  10 [edit]: def example():    # Press Tab here
  10 [edit]: def example():    # Becomes 4 spaces
```

### Ctrl-C Handling:
```
  10 [edit]: def example():    # Press Ctrl+C
^C                             # Briefly shows ^C
                               # Returns to editor, no changes made
```

## Technical Details

### Hook Priority: 90
The `__90` in the filename gives this hook high priority (90/100), ensuring it runs before other potential input handlers.

### Dependencies
- **None** - uses only Python standard library modules:
  - `readline` for input handling
  - `signal` for Ctrl-C handling
  - `re` for pattern matching
  - `sys`, `os` for system operations

### Signal Handling
- Catches `SIGINT` (Ctrl-C) gracefully
- Provides visual feedback (`^C`)
- Restores original line content
- Cleans up display properly

## Customization

### Modify Indentation Rules
Edit the `get_indentation_size()` function to change spacing for specific file types.

### Add New File Types
Extend the `indent_rules` dictionary with new extensions and desired spacing.

### Adjust Indentation Logic
Modify `get_suggested_indent()` to change the smart indentation behavior.

## Troubleshooting

### Tab Not Working
- Ensure the hook is in the correct directory
- Check file permissions are executable

### Wrong Indentation Size
- Verify the file extension is in the `indent_rules` dictionary
- Check for typos in filename extensions

### Ctrl-C Not Working
- The hook uses POSIX signal handling, should work on Unix-like systems

## License

GNU GPL v3+ - Same as PyLine

## Compatibility

- **Python**: 3.6+
- **Systems**: Unix-like systems (Linux, macOS) with readline support
- **PyLine**: Version 0.9+

## Source Code

The hook is self-contained in a single file with no external dependencies, making it easy to audit and modify.
