# ----------------------------------------------------------------
# Simple Tab-to-Spaces Handler for PyLine in Python3
# Description: Converts tab characters to appropriate spaces based on file type, with intelligent indentation and Ctrl-C handling.
# Priority: 90
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# No external dependencies - uses built-in readline
# ----------------------------------------------------------------

import re
import readline
import signal
import sys
import time
from typing import Any, Dict, NoReturn


def handle_input(context: Dict[str, Any]) -> str:
    """
    Simple and reliable tab-to-spaces conversion using readline
    """
    # Extract context values
    line_number = context.get("line_number", 1)
    current_text = context.get("current_text", "")
    filename = context.get("filename", "")
    previous_text = context.get("previous_text", "")

    # Move prompt one line down to avoid display overlap
    print()  # Add blank line to move prompt down

    prompt_text = f"{line_number:4d} [edit]: "

    # Calculate suggested indentation
    suggested = get_suggested_indent(filename, current_text, previous_text)

    # Monkey-patch readline to convert tabs to spaces
    original_insert_text = readline.insert_text
    original_sigint_handler = signal.getsignal(signal.SIGINT)

    def tab_aware_insert_text(text: str) -> None:
        """Convert tabs to spaces using SMART indentation"""
        if "\t" in text:
            # Use the pre-calculated suggested indentation instead of basic tab conversion
            text = text.replace("\t", suggested)
        original_insert_text(text)
        return None

    def handle_sigint(signum: int, frame: Any) -> NoReturn:
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
        if "\t" in result:
            # Use the suggested indentation for any remaining tabs
            result = result.replace("\t", suggested)

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


def get_indentation_size(filename: str) -> int:
    """Get indentation size based on file type"""
    if not filename:
        return 4

    file_extension = filename.lower().split(".")[-1] if "." in filename else ""

    indent_rules: Dict[str, int] = {
        # Python
        "py": 4,
        "python": 4,
        # C/C++/Rust
        "c": 4,
        "h": 4,
        "cpp": 4,
        "cc": 4,
        "cxx": 4,
        "hpp": 4,
        "hh": 4,
        "rs": 4,
        # Java/C#
        "java": 4,
        "cs": 4,
        # Web
        "js": 2,
        "ts": 2,
        "jsx": 2,
        "tsx": 2,
        "html": 2,
        "htm": 2,
        "css": 2,
        "scss": 2,
        "sass": 2,
        "less": 2,
        # Data/Config
        "json": 2,
        "yml": 2,
        "yaml": 2,
        "xml": 2,
        "toml": 4,
        # Scripting
        "rb": 2,
        "php": 4,
        "pl": 4,
        "pm": 4,
        "t": 4,
        # Shell - STANDARD 4 spaces
        "sh": 4,
        "bash": 4,
        "zsh": 4,
        "fish": 4,
        "ksh": 4,
        # Go
        "go": 4,
        # Other
        "sql": 4,
        "lua": 4,
        "swift": 4,
        "kt": 4,
        "scala": 4,
    }

    return indent_rules.get(file_extension, 4)


def get_suggested_indent(filename: str, current_line: str, previous_line: str = "") -> str:
    """Smart indentation for all supported languages with nested context"""
    indent_size = get_indentation_size(filename)
    current_indent_match = re.match(r"^(\s*)", current_line)
    current_indent = current_indent_match.group(1) if current_indent_match else ""

    # Get file extension for language-specific rules
    file_extension = filename.lower().split(".")[-1] if filename else ""

    # If no previous line, maintain current indentation
    if not previous_line or not previous_line.strip():
        return current_indent

    # Get previous line's indentation and content
    prev_indent_match = re.match(r"^(\s*)", previous_line)
    prev_indent = prev_indent_match.group(1) if prev_indent_match else ""
    prev_indent_len = len(prev_indent)
    prev_stripped = previous_line.strip()

    # ===== LANGUAGE-SPECIFIC INDENTATION RULES =====

    # C/C++/RUST/JAVA/C# ---------------------------------------------------------------------
    if file_extension in ["c", "h", "cpp", "cc", "cxx", "hpp", "hh", "rs", "java", "cs"]:
        # INCREASE INDENT after:
        if (
            re.search(r"{\s*$", prev_stripped)  # Opening brace {
            or re.search(r"\(\s*$", prev_stripped)  # Opening parenthesis (
            or re.search(r"\[\s*$", prev_stripped)  # Opening bracket [
            or re.search(r"^\s*(if|for|while|switch)\s*\([^)]*$", prev_stripped)  # Control structures without closing )
            or re.search(r"else\s*$", prev_stripped)  # else statement
            or re.search(r"try\s*$", prev_stripped)  # try block
            or re.search(r"catch\s*\([^)]*$", prev_stripped)  # catch without closing )
            or re.search(r"finally\s*$", prev_stripped)  # finally block
        ):
            return " " * (prev_indent_len + indent_size)

        # DECREASE INDENT for:
        elif (
            re.search(r"^\s*}\s*$", prev_stripped)  # Closing brace }
            or re.search(r"^\s*\);?\s*$", prev_stripped)  # Closing parenthesis with optional semicolon
            or re.search(r"^\s*\];?\s*$", prev_stripped)  # Closing bracket with optional semicolon
            or re.search(r"^\s*\)\s*{", prev_stripped)  # Closing ) followed by {
        ):
            return " " * max(0, prev_indent_len - indent_size)

    # SHELL/BASH/ZSH -------------------------------------------------------------------------
    elif file_extension in ["sh", "bash", "zsh", "fish", "ksh"]:
        # INCREASE INDENT after:
        if (
            re.search(r"\b(do|then)\s*$", prev_stripped)  # do/then keywords
            or re.search(r"{\s*$", prev_stripped)  # Opening brace {
            or re.search(r"\(\s*$", prev_stripped)  # Subshell opening
            or re.search(r"\b(if|for|while|until|case)\b.*\s*$", prev_stripped)  # Control structures
            or re.search(r"else\s*$", prev_stripped)  # else clause
            or re.search(r"elif.*\s*$", prev_stripped)  # elif clause
        ):
            return " " * (prev_indent_len + indent_size)

        # DECREASE INDENT for:
        elif (
            re.search(r"^\s*\b(fi|done|esac)\b\s*$", prev_stripped)  # fi, done, esac
            or re.search(r"^\s*}\s*$", prev_stripped)  # Closing brace }
            or re.search(r"^\s*\)\s*$", prev_stripped)  # Closing subshell
            or re.search(r"^\s*;;\s*$", prev_stripped)  # Case statement terminator
            or re.search(r"^\s*else\b", prev_stripped)  # else at beginning
            or re.search(r"^\s*elif\b", prev_stripped)  # elif at beginning
        ):
            return " " * max(0, prev_indent_len - indent_size)

    # PYTHON -----------------------------------------------------------------
    elif file_extension in ["py", "python"]:
        # Increase after these patterns (previous line ends with):
        if (
            re.search(r":\s*$", prev_stripped)  # Colon (if, for, while, def, class)
            or re.search(r"\\\s*$", prev_stripped)  # Line continuation
            or re.search(r"\(\s*$", prev_stripped)  # Opening parenthesis
            or re.search(r"\[\s*$", prev_stripped)  # Opening bracket
            or re.search(r"\{\s*$", prev_stripped)  # Opening brace (rare)
        ):
            return " " * (prev_indent_len + indent_size)

        # Decrease for these patterns (previous line starts with):
        elif (
            re.search(r"^\s*else\b", prev_stripped)  # else
            or re.search(r"^\s*elif\b", prev_stripped)  # elif
            or re.search(r"^\s*except\b", prev_stripped)  # except
            or re.search(r"^\s*finally\b", prev_stripped)  # finally
        ):
            return " " * max(0, prev_indent_len - indent_size)

    # JAVASCRIPT/TYPESCRIPT -------------------------------------------------
    elif file_extension in ["js", "ts", "jsx", "tsx"]:
        # Increase after opening braces/brackets/parentheses or arrow functions
        if (
            re.search(r"\{\s*$", prev_stripped)  # Opening brace {
            or re.search(r"\(\s*$", prev_stripped)  # Opening parenthesis (
            or re.search(r"\[\s*$", prev_stripped)  # Opening bracket [
            or re.search(r"=>\s*$", prev_stripped)  # Arrow function
        ):
            return " " * (prev_indent_len + indent_size)

        # Decrease for closing braces/brackets/parentheses
        elif (
            re.search(r"^\s*\}\s*$", prev_stripped)  # Closing brace }
            or re.search(r"^\s*\)\s*$", prev_stripped)  # Closing parenthesis )
            or re.search(r"^\s*\]\s*$", prev_stripped)  # Closing bracket ]
        ):
            return " " * max(0, prev_indent_len - indent_size)

    # PERL ------------------------------------------------------------------
    elif file_extension in ["pl", "pm", "t"]:
        # Increase after opening braces/brackets/parentheses or keywords
        if (
            re.search(r"\{\s*$", prev_stripped)  # Opening brace {
            or re.search(r"\(\s*$", prev_stripped)  # Opening parenthesis (
            or re.search(r"\[\s*$", prev_stripped)  # Opening bracket [
            or re.search(r"sub\s*$", prev_stripped)  # sub definition
            or re.search(r"do\s*$", prev_stripped)  # do block
        ):
            return " " * (prev_indent_len + indent_size)

        # Decrease for closing braces/brackets/parentheses
        elif (
            re.search(r"^\s*\}\s*$", prev_stripped)  # Closing brace }
            or re.search(r"^\s*\)\s*$", prev_stripped)  # Closing parenthesis )
            or re.search(r"^\s*\]\s*$", prev_stripped)  # Closing bracket ]
        ):
            return " " * max(0, prev_indent_len - indent_size)

    # HTML/XML --------------------------------------------------------------
    elif file_extension in ["html", "htm", "xml"]:
        # Increase after opening tags
        if re.search(r"<\w[^>]*>\s*$", prev_stripped):  # Opening tag
            return " " * (prev_indent_len + indent_size)

        # Decrease for closing tags
        elif re.search(r"^\s*</\w", prev_stripped):  # Closing tag
            return " " * max(0, prev_indent_len - indent_size)

    # ===== DEFAULT: MAINTAIN PREVIOUS INDENTATION =====
    # For all other cases, maintain the same indentation as previous line
    return prev_indent


def main(context: Dict[str, Any]) -> str:
    """
    Main function that will be called by the hook system
    """
    return handle_input(context)
