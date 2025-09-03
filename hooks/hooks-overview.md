# PyLine Hooks Overview

PyLine 0.9.7 introduces a fully modular, microkernel-style hooks system.

## What Are Hooks?

Hooks are small pluggable scripts—written in Python, Perl, Bash, or other supported languages—that extend PyLine's functionality.

## Example: Smart Tab Handler

- File: `smart_tab__90.py` (Python)
- Converts tab characters to spaces based on file type, intelligently suggests indentation, and handles Ctrl-C gracefully.
- Now defines `main(context)` for the new architecture.

## Example: Perl Word Counter

- File: `counter__80.pl` (Perl)
- Demonstrates a cross-language hook for word/line/character counting.
- Integrated with the `cw` command, outputs results directly using Perl’s regex/text strengths.

## How to Add Your Own Hook

1. Drop your script in `~/.pyline/hooks/{category}/{type}/`.
2. Name your file `hookname__priority.{ext}` (e.g., `smart_tab__90.py`, `counter__80.pl`).
3. Ensure your script defines a `main(context)` function.
4. PyLine will automatically detect, prioritize, and run your hook as needed.

## Supported Languages

- Python (.py)
- Perl (.pl)
- Bash (.sh)
- Node.js (.js)
- Ruby (.rb)
- Lua (.lua)
- PHP (.php)

## Installation Locations

Hooks should be placed in: `~/.pyline/hooks/{category}/{type}/`

### Quick Permission Fix
```bash
# Make all hooks executable
chmod +x ~/.pyline/hooks/**/*.py
chmod +x ~/.pyline/hooks/**/*.pl
chmod +x ~/.pyline/hooks/**/*.sh
```

Examples:
- Input handlers: `~/.pyline/hooks/input_handlers/edit_line/`
- Event handlers: `~/.pyline/hooks/event_handlers/pre_save/`
- Syntax handlers: `~/.pyline/hooks/syntax_handlers/highlight/`

Complete structure:
```
~/.pyline/hooks/
├── input_handlers/           # Input processing hooks
│   └── edit_line/           # Line editing handlers
│       ├── smart_tab__90.py  # Priority 90 (high)
│       └── auto_complete.py
├── event_handlers/           # Event-based hooks  
│   ├── pre_save/            # Before saving
│   ├── post_save/           # After saving
│   ├── pre_load/            # Before loading
│   ├── post_load/           # After loading
│   └── on_error/            # Error handling
├── syntax_handlers/         # Syntax processing
│   ├── highlight/           # Syntax highlighting
│   └── lint/               # Code linting
├── editing_ops/            # Editing operations
│   ├── pre_insert/         # Before line insertion
│   ├── post_insert/        # After line insertion  
│   ├── pre_delete/         # Before line deletion
│   └── post_delete/        # After line deletion
├── clipboard_ops/          # Clipboard operations
│   ├── pre_copy/           # Before copying
│   ├── post_copy/          # After copying
│   ├── pre_paste/          # Before pasting
│   └── post_paste/         # After pasting
└── session_handlers/       # Session management
    ├── pre_edit/          # Before editing session
    └── post_edit/         # After editing session
```

## 5-Minute Hook Creation

1. **Choose location**: `mkdir -p ~/.pyline/hooks/input_handlers/edit_line/`
2. **Create hook**: `nano ~/.pyline/hooks/input_handlers/edit_line/my_hook__50.py`
3. **Add code**:
```python
#!/usr/bin/env python3
# -----------------------------------------------------------------------
# Python Example Hook
# Description: Converts text to uppercase
# Priority: 50
# Category: input_handlers
# Type: edit_line
# Copyright (C) 2025 Your Name
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# -----------------------------------------------------------------------

def main(context):
    return context.get('current_text', '').upper()
```
### Common Issues:
- **Hook not loading**: Check file permissions (`chmod +x hook.py`)
- **Wrong category**: Verify directory structure
- **JSON errors**: Ensure proper JSON handling in non-Python hooks

## Context Object Reference

| Field | Type | Description | Available In |
|-------|------|-------------|-------------|
| `action` | string | Hook action type | All hooks |
| `filename` | string | Current file name | Most hooks |
| `operation` | string | Operation type | All hooks |
| `current_text` | string | Text being edited | Input handlers |
| `line_number` | int | Current line number | Input handlers |
| `content` | string/list | File content | Event handlers |
| `lines` | list | All buffer lines | Many hooks |

## Frequently Asked Questions

### Q: Why isn't my hook loading?
**A**: Check:
- File has execute permission (`chmod +x hook.py`)
- Correct directory structure
- Valid shebang line
- No syntax errors

### Q: How do I override built-in functionality?
**A**: Use higher priority (90+) and return non-Null values

### Q: Can hooks access PyLine's internal state?
**A**: No - hooks only receive the context object for security

### Q: How to handle different file types?
**A**: Check `context['filename']` extension and act accordingly

