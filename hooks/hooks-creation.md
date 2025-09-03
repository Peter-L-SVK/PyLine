# PyLine Hook Development Guide

This guide covers the creation, licensing, and distribution of hooks for the PyLine text editor. Adhering to these standards ensures compatibility, performance, and legal compliance.

## Standardized Hook Structure

### Header Template (All Languages)
Every hook file must begin with a standardized header for metadata and interpreter directive.

```perl/php/python/javascript/etc
#!/usr/bin/env [interpreter]

# -----------------------------------------------------------------------
# [Language] [Hook Name] Hook
# Description: [Brief description of hook functionality]
# Priority: [10-90]
# Category: [input_handlers|event_handlers|syntax_handlers|editing_ops|clipboard_ops|session_handlers]
# Type: [specific_type e.g., edit_line|pre_save|highlight|etc.]
# Copyright (C) [Year] [Your Name]
# License: [License Name] <[License URL]>
# This is free software with NO WARRANTY.
# -----------------------------------------------------------------------
```

### Why This Format Matters:
1.  **Shebang Line**: Ensures correct interpreter execution.
2.  **Clear Metadata**: Helps PyLine's hook manager categorize, prioritize, and load hooks correctly.
3.  **License Information**: Required for legal compliance and distribution.
4.  **NO WARRANTY**: Protects developers from liability claims.

## Supported Languages & Requirements

### Python Hooks (.py)
**Requirements**: Python 3.6+
```python
def main(context):
    """
    Main function called by PyLine hook system.
    
    Args:
        context (dict): Hook execution context containing:
            - action: The hook action being performed
            - filename: Current filename (if available)
            - operation: Type of operation
            - Additional context-specific fields
    
    Returns:
        Varies by hook type - can be modified text, status dict, or None
    """
    # Your hook logic here
    return result
```

### Perl Hooks (.pl)
**Requirements**: Perl 5+
```perl
sub main {
    my $context = shift;
    # Your hook logic here
    return $result;
}

# JSON handling example
use JSON::PP;
my $decoder = JSON::PP->new->utf8;
my $data = $decoder->decode($json_input);
```

### JavaScript Hooks (.js)
**Requirements**: Node.js
```javascript
function main(context) {
    // Your hook logic here
    return result;
}

// For JSON input
const data = JSON.parse(process.argv[2] || process.stdin.read());
```

### Shell Hooks (.sh)
**Requirements**: Bash 4+
```bash
#!/bin/bash

main() {
    # Read JSON from stdin
    context_json=$(cat)
    # Parse with jq or basic string manipulation
    # Your hook logic here
    echo "$result"
}
```

### Ruby Hooks (.rb)
**Requirements**: Ruby 2.0+
```ruby
def main(context)
  # Your hook logic here
  return result
end

# JSON parsing
require 'json'
data = JSON.parse(ARGF.read)
```

## Hook Categories & Best Practices

### 1. Input Handlers (`input_handlers/`)
**Purpose**: Modify user input during editing.
```python
# Example: Smart tab handler
def main(context):
    current_text = context.get('current_text', '')
    # Transform input
    transformed = current_text.replace('\t', '    ')
    return transformed
```

### 2. Event Handlers (`event_handlers/`)
**Purpose**: Respond to file operations (load, save, etc.).
```perl
# Example: Pre-save formatter
sub main {
    my $context = shift;
    if ($context->{action} eq 'pre_save') {
        my $content = $context->{content};
        # Format content
        return { content => $formatted_content };
    }
    return undef; # Return undef for events you don't handle
}
```

### 3. Syntax Handlers (`syntax_handlers/`)
**Purpose**: Code highlighting and analysis.
```javascript
function main(context) {
    if (context.action === 'highlight') {
        const line = context.line;
        // Apply syntax highlighting rules
        return highlighted_line;
    }
}
```

## Priority System Explained

Hooks are executed in order of priority (high to low). Choose a priority that reflects your hook's importance and relation to others.

-   **90-100**: Critical system hooks (e.g., tab conversion, basic sanitization).
-   **70-89**: Important functionality (e.g., syntax highlighting, auto-completion).
-   **50-69**: Standard utilities (e.g., word count, basic text transformations).
-   **30-49**: Enhancement hooks (e.g., themes, minor formatting adjustments).
-   **10-29**: Experimental or optional features.

## License Best Practices

Choosing the correct license is crucial for your hook's adoption and distribution.

### License Compatibility and Distribution

| License       | When to Use                                           | Compatible with PyLine GPLv3+? | How to Contribute/Use                               |
| :------------ | :---------------------------------------------------- | :----------------------------- | :-------------------------------------------------- |
| **GPLv3+**    | PyLine integration (recommended), Copyleft projects   | Yes                            | Directly in `~/.pyline/hooks`                       |
| **Apache 2.0**| Permissive, patent protection, enterprise/clustering  | Yes                            | Separate repo, link in docs. Include full header.   |
| **MIT**       | Simple permissive, 3rd-party code, maximum adoption   | Yes                            | Separate repo, link in docs. Include license text.  |
| **BSD-3**     | Permissive, enterprise/fork, avoid patent implications| Yes                            | Separate repo, link in docs. Include license text.  |

### Key Differentiator for Apache 2.0:
The Apache 2.0 license is similar to MIT/BSD in being permissive but includes an explicit grant of patent rights from contributors and a clause to prevent patent litigation. This makes it a strong choice for projects where patent concerns are important, which is common in larger corporations or foundational technologies.

### General Licensing Rules:
-   **Use GPLv3+** if you want your hook to be included directly in the main PyLine repository.
-   If you are integrating **third-party libraries**, check its license. Use the same license if possible. If not, you must use a different, compatible license.
-   Hooks with licenses **other than GPLv3+** cannot be bundled in the main PyLine repo and must be distributed in a **separate public repository**, which will be linked in the official documentation.
-   **Always** include the full license header in your hook file.

### Recommended License Headers:

1.  **GPLv3+** (Recommended for PyLine integration):
    ```text
    License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
    This is free software with NO WARRANTY.
    ```

2.  **Apache 2.0** (Permissive with patent protection):
    ```text
    License: Apache 2.0 <https://www.apache.org/licenses/LICENSE-2.0.txt>
    ```

3.  **MIT License** (Simple permissive):
    ```text
    License: MIT <https://opensource.org/licenses/MIT>
    ```

4.  **BSD-3-Clause** (Permissive):
    ```text
    License: BSD 3-Clause <https://opensource.org/licenses/BSD-3-Clause>
    ```

**Note:** If you submit a hook under Apache 2.0, MIT, or BSD, you must retain the original license header and any NOTICE file. When distributed with PyLine, the overall work is covered by GPLv3+, but your hook retains its original permissive license terms.

## Error Handling Best Practices

Always handle errors gracefully to prevent hook failures from crashing the editor.

### Python Example:
```python
def main(context):
    try:
        # Your hook logic
        return result
    except Exception as e:
        # Return original content on error to maintain workflow
        return context.get('current_text', '')
```

### Perl Example:
```perl
sub main {
    my $context = shift;
    eval {
        # Your hook logic
        return $result;
    };
    if ($@) {
        # Log error in debug mode, fail silently otherwise
        warn "Hook error: $@" if $ENV{PYLINE_DEBUG};
        return undef;
    }
}
```

## Performance Considerations

1.  **Keep Hooks Lightweight**: Avoid heavy computations or blocking calls.
2.  **Cache Expensive Operations**: Store results for repeated operations when possible.
3.  **Early Exit**: Return quickly (e.g., `return None` or original input) if the hook doesn't apply to the current context.
4.  **Memory Efficiency**: Process streams or lines, not entire files, when possible.

## Testing Your Hooks

### Test Structure:
Test your hook independently before integrating it with PyLine.

```bash
# Test your hook directly by piping JSON context
echo '{"action":"test","current_text":"test input"}' | python3 my_hook.py

# Test with PyLine's hook manager (if available)
python3 -m pyline.hook_manager test my_hook.py
```

### Debug Mode:
Add debug output to help with development.

```python
import os
import sys

if os.environ.get('PYLINE_DEBUG'):
    print(f"Debug: Received context {context}", file=sys.stderr)
```

## Distribution & Sharing

### Package Your Hook:
Create a well-structured package for users to download and install.

```
my_awesome_hook/
├── hook.py              # The main hook file
├── README.md            # Documentation
├── LICENSE              # Full license text
├── install.sh           # Installation script (highly recommended)
└── test_input.json      # Example input for testing
```

### README Template:
```markdown
# [Hook Name] for PyLine

## Description
[What your hook does and what problem it solves]

## Installation
1.  Run the install script: `./install.sh`
    *Or*
2.  Manually copy `hook.py` to `~/.pyline/hooks/[category]/[type]/`

## Dependencies
- [List any required external packages or tools]

## License
[Your chosen license name], see the LICENSE file for details.
```

## Write an Install Script

An install script automates the process for users, ensuring the hook is placed in the correct directory with the right permissions.

### Example Installation Script (`install.sh`):
Place this script in the same directory as your hook.

```bash
#!/usr/bin/env sh

echo "Installing 'Lowercase to Uppercase' Hook for PyLine..."
echo "This hook converts all lower-case letters to upper-case in opened files."

# Define the target directory and hook filename
HOOK_DIR="$HOME/.pyline/hooks/event_handlers/pre_load"
HOOK_FILE="lowercase_to_uppercase__80.pl" # Your hook's filename

# Create the necessary directory structure
mkdir -p "$HOOK_DIR"

# Copy the hook file to the target directory
cp "./$HOOK_FILE" "$HOOK_DIR/"

# Set execute permissions on the hook
chmod +x "$HOOK_DIR/$HOOK_FILE"

echo "Hook installed successfully!"
echo "Location: $HOOK_DIR/$HOOK_FILE"
echo ""
echo "Restart PyLine for the changes to take effect."
exit 0
```

### Using the Install Script:
1.  Save the script as `install.sh` in your hook's directory.
2.  Make it executable: `chmod +x install.sh`
3.  Run it: `./install.sh`

## Common Pitfalls to Avoid

1.  **❌ No Error Handling**: Always use try/catch blocks.
2.  **❌ Heavy Computations**: Optimize for performance; hooks should be fast.
3.  **❌ Missing License**: Always include a clear license to avoid legal issues.
4.  **❌ Changing Hook Signature**: Maintain the expected `main(context)` input/output format.
5.  **❌ Not Testing**: Test with various input scenarios to ensure reliability.

## Example Complete Hook

### Python - Auto-indenter:
```python
#!/usr/bin/env python3

# -----------------------------------------------------------------------
# Python Auto-Indent Hook
# Description: Provides smart indentation based on previous line context
# Priority: 85
# Category: input_handlers
# Type: edit_line
# Copyright (C) 2025 Jane Developer
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# -----------------------------------------------------------------------

def main(context):
    try:
        current_text = context.get('current_text', '')
        previous_text = context.get('previous_text', '')
        
        # Defer to existing indentation logic if present
        indent = calculate_indent(previous_text)
        return indent + current_text.lstrip()
        
    except Exception as e:
        # Fail gracefully by returning the original input
        return context.get('current_text', '')

def calculate_indent(previous_line):
    """
    Simple logic: increase indent after an opening brace.
    """
    if previous_line.strip().endswith('{'):
        return '    '  # 4 spaces
    return '' # No extra indent
```

**Code Quality:** Before contributing, run these tools (pre-configured in the PyLine repo):
-   `flake8` for style guide enforcement
-   `mypy` for static type checking (if using type hints)
-   `black` for code formatting

By following these guidelines, your hooks will be:
-   ✅ Compatible with PyLine's hook system
-   ✅ Legally compliant and properly licensed
-   ✅ Performant and reliable
-   ✅ Easy to maintain, share, and install
-   ✅ Consistent with community standards

---
