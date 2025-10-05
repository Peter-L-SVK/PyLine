# ----------------------------------------------------------------
# JSON syntax highlighting in Python 3
# Description: JSON Syntax Highlighter for PyLine with key/value distinction
# Priority: 60
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

import re
from typing import Dict, Any


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced JSON syntax highlighter with key/value color distinction
    """
    line = context.get("line", "")
    filename = context.get("filename", "")

    # Check if this is a JSON file
    if not filename or not filename.lower().endswith(".json"):
        return {"output": line, "handled_output": 0}

    # Get colors from theme manager
    try:
        from theme_manager import theme_manager

        RESET = theme_manager.get_color("reset")
        KEY_COLOR = theme_manager.get_color("keyword")  # JSON keys
        VALUE_KEYWORD = theme_manager.get_color("variable")  # null, true, false
        STRING = theme_manager.get_color("string")  # String values
        NUMBER = theme_manager.get_color("number")  # Numbers
        BRACE = theme_manager.get_color("class")  # Braces and brackets
        COLON = theme_manager.get_color("decorator")  # Colon separator
        COMMA = theme_manager.get_color("annotation")  # Commas

    except ImportError:
        # Fallback colors if theme manager not available
        RESET = "\033[0m"
        KEY_COLOR = "\033[1;34m"  # Bright Blue for keys
        VALUE_KEYWORD = "\033[0;34m"  # Regular Blue for null/true/false
        STRING = "\033[0;32m"  # Green for string values
        NUMBER = "\033[0;35m"  # Magenta for numbers
        BRACE = "\033[1;36m"  # Cyan for braces
        COLON = "\033[0;33m"  # Yellow for colon
        COMMA = "\033[0;90m"  # Gray for commas

    # Build the highlighted line step by step
    result_parts = []
    i = 0
    n = len(line)

    # Track if we're expecting a key or value
    expecting_key = True  # Start expecting a key at object beginning

    while i < n:
        char = line[i]

        # Check if we're at the start of a string
        if char == '"':
            # Find the end of the string
            j = i + 1
            escape = False
            while j < n:
                if escape:
                    escape = False
                elif line[j] == "\\":
                    escape = True
                elif line[j] == '"':
                    break
                j += 1

            # Include the closing quote
            if j < n:
                j += 1

            string_content = line[i:j]

            # Determine if this is a key or value string
            if expecting_key:
                # This is a key - look ahead for colon
                remaining = line[j:]
                if re.match(r"^\s*:", remaining):
                    result_parts.append(KEY_COLOR + string_content + RESET)
                    expecting_key = False  # Next will be a value
                else:
                    # This is a value string that happens to be where we expected a key
                    result_parts.append(STRING + string_content + RESET)
                    expecting_key = True  # Reset expectation
            else:
                # This is a value string
                result_parts.append(STRING + string_content + RESET)
                # After a value, we expect either comma (then key) or end
                expecting_key = False

            i = j

        # Check if we're at a number (only values can be numbers)
        elif char in "-0123456789" and not expecting_key:
            j = i
            # Simple number detection
            if char == "-":
                j += 1
            while j < n and line[j] in "0123456789":
                j += 1
            # Decimal part
            if j < n and line[j] == ".":
                j += 1
                while j < n and line[j] in "0123456789":
                    j += 1
            # Exponent part
            if j < n and line[j] in "eE":
                j += 1
                if j < n and line[j] in "+-":
                    j += 1
                while j < n and line[j] in "0123456789":
                    j += 1

            # Verify it's actually a number
            if (i == 0 or line[i - 1] in " :,[]{") and (j == n or line[j] in " ,}\n"):
                result_parts.append(NUMBER + line[i:j] + RESET)
                i = j
                expecting_key = False  # Just processed a value
            else:
                result_parts.append(char)
                i += 1

        # Check for JSON keywords (only values can be keywords)
        elif char in "ntf" and not expecting_key:  # null, true, false
            if line[i : i + 4] == "null" and (i + 4 == n or line[i + 4] in " ,}\n"):
                result_parts.append(VALUE_KEYWORD + "null" + RESET)
                i += 4
                expecting_key = False
            elif line[i : i + 4] == "true" and (i + 4 == n or line[i + 4] in " ,}\n"):
                result_parts.append(VALUE_KEYWORD + "true" + RESET)
                i += 4
                expecting_key = False
            elif line[i : i + 5] == "false" and (i + 5 == n or line[i + 5] in " ,}\n"):
                result_parts.append(VALUE_KEYWORD + "false" + RESET)
                i += 5
                expecting_key = False
            else:
                result_parts.append(char)
                i += 1

        # Structure characters
        elif char in "{[":
            result_parts.append(BRACE + char + RESET)
            expecting_key = True  # After { or [, we expect keys
            i += 1
        elif char in "}]":
            result_parts.append(BRACE + char + RESET)
            expecting_key = False  # After } or ], context depends on what comes next
            i += 1
        elif char == ":":
            result_parts.append(COLON + char + RESET)
            expecting_key = False  # After colon, we expect a value
            i += 1
        elif char == ",":
            result_parts.append(COMMA + char + RESET)
            expecting_key = True  # After comma, we expect a key
            i += 1

        # Whitespace - just copy it
        elif char in " \t":
            result_parts.append(char)
            i += 1

        # Regular character
        else:
            result_parts.append(char)
            i += 1

    highlighted = "".join(result_parts)
    return {"output": highlighted, "handled_output": 1}
