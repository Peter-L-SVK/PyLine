# PyLine Hook Development Guide

## Standardized Hook Structure

### Header Template (All Languages)
```perl/php/python/javascript/etc
#!/usr/bin/env [interpreter]

#-----------------------------------------------------------------------
# [Language] [Hook Name] Hook
# Description: [Brief description of hook functionality]
# Priority: [10-90]
# Category: [input_handlers|event_handlers|syntax_handlers|editing_ops|clipboard_ops|session_handlers]
# Type: [specific_type e.g., edit_line|pre_save|highlight|etc.]
# Copyright (C) [Year] [Your Name]
# License: [License Name] <[License URL]>
# This is free software with NO WARRANTY.
#-----------------------------------------------------------------------
```

### Why This Format Matters:
1. **Shebang Line**: Ensures correct interpreter execution
2. **Clear Metadata**: Helps PyLine's hook manager categorize and prioritize
3. **License Information**: Required for legal compliance
4. **NO WARRANTY**: Protects developers from liability claims

## Supported Languages & Requirements

### Python Hooks (.py)
**Requirements**: Python 3.6+
```python
def main(context):
    """
    Main function called by PyLine hook system
    
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
eval {
    require JSON::PP;
    my $decoder = JSON::PP->new->utf8;
    my $data = $decoder->decode($json_input);
};
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
**Purpose**: Modify user input during editing
```python
# Example: Smart tab handler
def main(context):
    current_text = context.get('current_text', '')
    # Transform input
    transformed = current_text.replace('\t', '    ')
    return transformed
```

### 2. Event Handlers (`event_handlers/`)
**Purpose**: Respond to file operations
```perl
# Example: Pre-save formatter
sub main {
    my $context = shift;
    if ($context->{action} eq 'pre_save') {
        my $content = $context->{content};
        # Format content
        return { content => $formatted_content };
    }
    return undef;
}
```

### 3. Syntax Handlers (`syntax_handlers/`)
**Purpose**: Code highlighting and analysis
```javascript
function main(context) {
    if (context.action === 'highlight') {
        const line = context.line;
        // Apply syntax highlighting
        return highlighted_line;
    }
}
```

## Priority System Explained

- **90-100**: Critical system hooks (tab conversion, basic formatting)
- **70-89**: Important functionality (syntax highlighting, auto-completion)
- **50-69**: Standard utilities (word count, basic transformations)
- **30-49**: Enhancement hooks (themes, minor formatting)
- **10-29**: Experimental/optional features

## License Best Practices
- When usig third party libs, check license and use same one, if not possible to use different.
- In case of different than GPL v3+ license hook need to be placed in different repo
- These separate repos should be public and will be linked in docs

### Recommended Licenses:

1. **GPLv3+** (Recommended for PyLine integration):
   ```text
   License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
   This is free software with NO WARRANTY.
   ```

2. **MIT License** (Permissive):
   ```text
   License: MIT <https://opensource.org/licenses/MIT>
   ```

3. **BSD-3-Clause** (Permissive):
   ```text
   License: BSD 3-Clause <https://opensource.org/licenses/BSD-3-Clause>
   ```

## Error Handling Best Practices

### Python Example:
```python
def main(context):
    try:
        # Your hook logic
        return result
    except Exception as e:
        # Return original content on error
        return context.get('current_text', '')
```

### Perl Example:
```perl
sub main {
    eval {
        my $context = shift;
        # Your hook logic
        return $result;
    };
    if ($@) {
        return undef; # Silent failure
    }
}
```

## Performance Considerations

1. **Keep Hooks Lightweight**: Avoid heavy computations
2. **Cache Expensive Operations**: Store results when possible
3. **Early Exit**: Return quickly if hook doesn't apply
4. **Memory Efficiency**: Process streams, not entire files

## Testing Your Hooks

### Test Structure:
```bash
# Test your hook directly
echo '{"action":"test","filename":"test.txt"}' | python3 my_hook.py

# Test with PyLine's hook manager
python3 -m hook_manager test my_hook.py
```

### Debug Mode:
```python
# Add debug output (will be visible in PyLine debug mode)
import sys
if os.environ.get('PYLINE_DEBUG'):
    print(f"Debug: {context}", file=sys.stderr)
```

## Distribution & Sharing

### Package Your Hook:
```
my_smart_hook/
├── hook.py
├── README.md
├── LICENSE
└── test_input.json
```

### README Template:
```markdown
# [Hook Name] for PyLine

## Description
[What your hook does]

## Installation
Copy to `~/.pyline/hooks/[category]/[type]/`

## Dependencies
- [Required packages]

## License
[Your chosen license]
```

## Common Pitfalls to Avoid

1. **❌ No error handling** → Use try/catch blocks
2. **❌ Heavy computations** → Optimize for performance
3. **❌ No license** → Always include a clear license
4. **❌ Changing hook signature** → Maintain expected input/output format
5. **❌ Not testing** → Test with various input scenarios

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
# Copyright (C) 2025 Your Name
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# -----------------------------------------------------------------------

def main(context):
    try:
        current_text = context.get('current_text', '')
        previous_text = context.get('previous_text', '')
        
        # Smart indentation logic
        indent = calculate_indent(previous_text)
        return indent + current_text.lstrip()
        
    except Exception:
        return context.get('current_text', '')

def calculate_indent(previous_line):
    # Your indentation logic here
    return '    '  # 4 spaces
```
Run tools Flake8, MyPy and Black (alredy preconfigured in repo).
By following these guidelines, your hooks will be:
- ✅ Compatible with PyLine's hook system
- ✅ Legally compliant and properly licensed
- ✅ Performant and reliable
- ✅ Easy to maintain and share
- ✅ Consistent with community standards

## Write an install script

Install script will make it easier for user to apply hooks

### Using the Install Script
1. Save the script as `install_hook.sh`
2. Make it executable: `chmod +x install_hook.sh`
3. Run it: `./install_hook.sh`
4. The hook will be automatically placed in the correct location

### Customizing for Your Hook
Change these variables in the script:
- `HOOK_DIR`: The category/type path for your hook
- `HOOK_FILE`: Your hook filename
- The echo messages to describe your hook's functionality

Place the ``install.sh`` in same deirectory as hook itself.

Exampe of installation script(incuded with hook):
```bash
#!/usr/bin/env sh

echo "Installing Lowercase To Uppercase changer for PyLine..."
echo "This hook script will convert all lower-case letters to upper-case in opened files"

HOOK_DIR="$HOME/.pyline/hooks/event_handlers/pre_load"
HOOK_FILE="lowercase_to_uppercase__80.pl"

# Create directory structure
mkdir -p "$HOOK_DIR"

# Copy the handler
cp "$HOOK_FILE" "$HOOK_DIR/"

# Set execute permissions
chmod +x "$HOOK_DIR/$HOOK_FILE"

echo "Lowercase to uppercase handler installed successfully!"
echo "Location: $HOOK_DIR/$HOOK_FILE"
echo ""
echo "PyLine will now convert all lower-case letters to upper-case in opened files"
exit 0
```
