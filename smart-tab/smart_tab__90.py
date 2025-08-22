#----------------------------------------------------------------
# Simple Tab-to-Spaces Handler for PyLine
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# No external dependencies - uses built-in readline
#----------------------------------------------------------------

import os
import re
import readline
import signal
import sys
import time

def handle_input(context):
    """
    Simple and reliable tab-to-spaces conversion using readline
    """
    # Extract context values
    line_number = context.get('line_number', 1)
    current_text = context.get('current_text', '')
    filename = context.get('filename', '')
    previous_text = context.get('previous_text', '')
    
    # Move prompt one line down to avoid display overlap
    print()  # Add blank line to move prompt down
    
    prompt_text = f"{line_number:4d} [edit]: "
    
    # Monkey-patch readline to convert tabs to spaces
    original_insert_text = readline.insert_text
    original_sigint_handler = signal.getsignal(signal.SIGINT)
    
    def tab_aware_insert_text(text):
        """Convert tabs to spaces before inserting"""
        if '\t' in text:
            # Convert tabs to appropriate number of spaces
            indent_size = get_indentation_size(filename)
            text = text.replace('\t', ' ' * indent_size)
        original_insert_text(text)
    
    def handle_sigint(signum, frame):
        """Handle Ctrl-C gracefully during input"""
        # Restore original handlers first
        signal.signal(signal.SIGINT, original_sigint_handler)
        readline.insert_text = original_insert_text
        readline.set_startup_hook(None)
        
        # Clear the input line and show cancelled message
        sys.stdout.write("\r\033[K")  # Clear current line
        print("^C")  # Show Ctrl-C was pressed
        time.sleep(0.3)  # Brief pause to see the ^C
        sys.stdout.write("\033[F\033[K")  # Move up and clear the ^C line
        
        # Raise KeyboardInterrupt to be caught by our except block
        raise KeyboardInterrupt()
    
    # Set up our signal handler temporarily
    signal.signal(signal.SIGINT, handle_sigint)
    
    # Set up readline with our tab handler
    readline.insert_text = tab_aware_insert_text
    readline.set_startup_hook(lambda: readline.insert_text(current_text))
    
    try:
        # Get input using standard input (but with our tab handler)
        result = input(prompt_text)
        
        # Convert any remaining tabs (safety net)
        if '\t' in result:
            indent_size = get_indentation_size(filename)
            result = result.replace('\t', ' ' * indent_size)
        
        return result
    
    except KeyboardInterrupt:
        # Ctrl-C was pressed - return original text (cancel edit)
        return current_text
    
    finally:
        # Restore original signal handler
        signal.signal(signal.SIGINT, original_sigint_handler)
        
        # Restore original readline behavior
        readline.insert_text = original_insert_text
        readline.set_startup_hook(None)
        
        # Clear the extra line after input to clean up display
        sys.stdout.write("\033[F\033[K")  # Move up and clear line

def get_indentation_size(filename):
    """Get indentation size based on file type"""
    if not filename:
        return 4
        
    file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    indent_rules = {
        'py': 4, 'python': 4, 'c': 2, 'h': 2, 'cpp': 2, 'java': 4,
        'js': 2, 'ts': 2, 'html': 2, 'css': 2, 'json': 2,
        'yml': 2, 'yaml': 2, 'xml': 2, 'rb': 2, 'php': 4,
        'go': 4, 'rs': 4, 'sh': 4, 'bash': 4
    }
    
    return indent_rules.get(file_extension, 4)

def get_suggested_indent(filename, current_line, previous_line=""):
    """Get suggested indentation for the current line"""
    indent_size = get_indentation_size(filename)
    current_indent_match = re.match(r'^(\s*)', current_line)
    current_indent = current_indent_match.group(1) if current_indent_match else ""
    
    # Increase indentation patterns
    increase_patterns = [
        r':\s*$', r'\{\s*$', r'\(\s*$', r'\[\s*$', r'\\\s*$'
    ]
    
    # Decrease indentation patterns  
    decrease_patterns = [
        r'^\s*\}', r'^\s*\)', r'^\s*\]', r'^\s*else\b', r'^\s*elif\b',
        r'^\s*except\b', r'^\s*finally\b'
    ]
    
    # Check for increase
    if previous_line and previous_line.strip():
        for pattern in increase_patterns:
            if re.search(pattern, previous_line.strip()):
                return ' ' * (len(current_indent) + indent_size)
    
    # Check for decrease
    if current_line.strip():
        for pattern in decrease_patterns:
            if re.search(pattern, current_line.strip()):
                return ' ' * max(0, len(current_indent) - indent_size)
    
    return current_indent
