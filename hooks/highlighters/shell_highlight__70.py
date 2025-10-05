# ----------------------------------------------------------------
# Shell Syntax Highlighter for PyLine
# Description: Supports bash, zsh, ksh, sh, fish with proper variable and function declaration highlighting
# Priority: 70
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

import fnmatch
import re
from typing import Dict, Any, List, Tuple, Optional


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Shell syntax highlighter for bash/zsh/ksh/sh files
    Uses theme manager for colors
    """
    line = context.get("line", "")
    filename = context.get("filename", "")

    if not filename:
        return {"output": line, "handled_output": 0}

    # Shell file patterns to EXCLUDE
    shell_patterns = ["*.sh", "*.bash", "*.zsh", "*.ksh", "*.fish"]

    # Check if it's a shell file
    is_shell_file = any(fnmatch.fnmatch(filename.lower(), pattern) for pattern in shell_patterns)

    # Check if it has ANY extension (contains a dot)
    has_extension = "." in filename

    # Process if it has an extension AND is NOT a shell file
    if has_extension and not is_shell_file:
        # This is a non-shell file with extension - handle it
        return {"output": line, "handled_output": 0}

    # Get colors from theme manager
    try:
        from theme_manager import theme_manager

        RESET = theme_manager.get_color("reset")
        KEYWORD = theme_manager.get_color("keyword")
        STRING = theme_manager.get_color("string")
        COMMENT = theme_manager.get_color("comment")
        FUNCTION = theme_manager.get_color("function")
        VARIABLE = theme_manager.get_color("variable")
        DECLARATION = theme_manager.get_color("class")  # For variable declarations

    except ImportError:
        # Fallback colors if theme manager not available
        RESET = "\033[0m"
        KEYWORD = "\033[1;34m"
        STRING = "\033[0;32m"
        COMMENT = "\033[0;36m"
        FUNCTION = "\033[1;35m"
        VARIABLE = "\033[0;33m"
        DECLARATION = "\033[1;36m"  # Cyan for declarations

    # Start with original line
    highlighted = line

    # PHASE 1: Highlight FULL-LINE comments first (including shebang)
    if line.strip().startswith("#") or line.startswith("#!/"):
        return {"output": COMMENT + line + RESET, "handled_output": 1}

    # PHASE 2: Highlight function declarations FIRST (before anything else)
    function_patterns = [
        # Style 1: function_name() {
        (r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*\(\s*\)\s*\{)", FUNCTION),
        # Style 2: function function_name {
        (r"^(\s*function\s+)([A-Za-z_][A-Za-z0-9_]*)(\s*\{)", FUNCTION),
        # Style 3: function function_name() {
        (r"^(\s*function\s+)([A-Za-z_][A-Za-z0-9_]*)(\s*\(\s*\)\s*\{)", FUNCTION),
    ]

    for pattern, color in function_patterns:
        match = re.match(pattern, line)
        if match:
            groups = match.groups()
            func_name = groups[1]  # The function name is in the second group

            # Find the position of the function name
            start_pos = match.start(2)
            end_pos = match.end(2)

            # Apply function color to the function name
            before = highlighted[:start_pos]
            after = highlighted[end_pos:]
            highlighted = before + color + func_name + RESET + after

    # PHASE 3: Highlight variable declarations and assignments
    declaration_patterns = [
        # Standard assignment: VAR=value
        (r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*)=", DECLARATION),
        # Export with assignment: export VAR=value
        (r"^(\s*export\s+)([A-Za-z_][A-Za-z0-9_]*)(\s*)=", DECLARATION),
        # Local declaration: local VAR=value
        (r"^(\s*local\s+)([A-Za-z_][A-Za-z0-9_]*)(\s*)=", DECLARATION),
        # Readonly declaration: readonly VAR=value
        (r"^(\s*readonly\s+)([A-Za-z_][A-Za-z0-9_]*)(\s*)=", DECLARATION),
        # Declare with assignment: declare VAR=value
        (r"^(\s*declare\s+)([A-Za-z_][A-Za-z0-9_]*)(\s*)=", DECLARATION),
        # Typeset with assignment: typeset VAR=value
        (r"^(\s*typeset\s+)([A-Za-z_][A-Za-z0-9_]*)(\s*)=", DECLARATION),
    ]

    for pattern, color in declaration_patterns:
        match = re.match(pattern, line)
        if match:
            groups = match.groups()
            var_name = groups[1]  # The variable name is in the second group

            # Find the position of the variable name
            start_pos = match.start(2)
            end_pos = match.end(2)

            # Apply declaration color to the variable name
            before = highlighted[:start_pos]
            after = highlighted[end_pos:]
            highlighted = before + color + var_name + RESET + after

    # PHASE 4: Highlight PARTIAL comments (comments after code)
    if "#" in highlighted:
        # Split on the first # that's not inside quotes
        in_single_quote = False
        in_double_quote = False
        escape_next = False
        comment_start = -1

        for i, char in enumerate(highlighted):
            if escape_next:
                escape_next = False
                continue

            if char == "\\":
                escape_next = True
            elif char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
            elif char == "#" and not in_single_quote and not in_double_quote:
                comment_start = i
                break

        if comment_start != -1:
            highlighted = highlighted[:comment_start] + COMMENT + highlighted[comment_start:] + RESET

    # PHASE 5: String highlighting - process both single and double quotes
    def highlight_quotes_in_text(text: str) -> str:
        """Highlight both single and double quoted strings"""
        result_parts: List[str] = []
        i = 0
        n = len(text)

        while i < n:
            char = text[i]

            # Check for double quoted string
            if char == '"' and (i == 0 or text[i - 1] != "\\"):
                j = i + 1
                while j < n:
                    if text[j] == "\\":
                        j += 2  # Skip escaped character
                    elif text[j] == '"':
                        j += 1
                        break
                    else:
                        j += 1
                # Add the double quoted string with string color
                result_parts.append(STRING + text[i:j] + RESET)
                i = j

            # Check for single quoted string
            elif char == "'" and (i == 0 or text[i - 1] != "\\"):
                j = i + 1
                while j < n:
                    if text[j] == "'":
                        j += 1
                        break
                    else:
                        j += 1
                # Add the single quoted string with string color
                result_parts.append(STRING + text[i:j] + RESET)
                i = j

            # Regular character
            else:
                result_parts.append(char)
                i += 1

        return "".join(result_parts)

    # Apply string highlighting
    highlighted = highlight_quotes_in_text(highlighted)

    # PHASE 6: Variable usage highlighting (only outside of strings)
    # We need to check the ORIGINAL line to determine string positions
    original_string_ranges: List[Tuple[int, Optional[int]]] = []
    in_single_quote = False
    in_double_quote = False
    escape_next = False

    for i, char in enumerate(line):
        if escape_next:
            escape_next = False
            continue

        if char == "\\":
            escape_next = True
        elif char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif in_single_quote or in_double_quote:
            if not original_string_ranges or original_string_ranges[-1][1] is not None:
                original_string_ranges.append((i, None))
        else:
            if original_string_ranges and original_string_ranges[-1][1] is None:
                original_string_ranges[-1] = (original_string_ranges[-1][0], i)

    # Close any open string ranges and convert to list of tuples with non-None end positions
    processed_ranges: List[Tuple[int, int]] = []
    for start, end in original_string_ranges:
        if end is None:
            processed_ranges.append((start, len(line)))
        else:
            processed_ranges.append((start, end))

    # Now highlight variable USAGE that are NOT in strings
    var_usage_patterns = [
        (r"\$[A-Za-z_][A-Za-z0-9_]*", VARIABLE),  # $VAR
        (r"\$\{[A-Za-z_][A-Za-z0-9_]*\}", VARIABLE),  # ${VAR}
        (r"\$\?", VARIABLE),  # $?
        (r"\$\$", VARIABLE),  # $$
        (r"\$!", VARIABLE),  # $!
    ]

    for pattern, color in var_usage_patterns:
        matches = list(re.finditer(pattern, line))
        for match in reversed(matches):
            var_text = match.group()
            start_pos = match.start()
            end_pos = match.end()

            # Check if this position is inside any string
            in_string = False
            for str_start, str_end in processed_ranges:
                if str_start <= start_pos < str_end:
                    in_string = True
                    break

            if not in_string:
                # Find and replace in highlighted text, avoiding color codes
                temp_highlighted = highlighted
                pos = 0
                found = False

                while not found and pos < len(temp_highlighted):
                    idx = temp_highlighted.find(var_text, pos)
                    if idx == -1:
                        break

                    # Check if we're not inside ANSI color codes
                    if (idx == 0 or temp_highlighted[idx - 1] != "\033") and not (
                        idx + len(var_text) < len(temp_highlighted) and temp_highlighted[idx + len(var_text)] == "m"
                    ):

                        before = temp_highlighted[:idx]
                        after = temp_highlighted[idx + len(var_text) :]
                        highlighted = before + color + var_text + RESET + after
                        found = True
                        break

                    pos = idx + 1

    # PHASE 7: Keyword and builtin highlighting (do this last)
    shell_keywords = [
        "if",
        "then",
        "else",
        "elif",
        "fi",
        "case",
        "esac",
        "for",
        "while",
        "until",
        "do",
        "done",
        "select",
        "function",
        "time",
        "in",
    ]

    shell_builtins = [
        "alias",
        "bg",
        "bind",
        "break",
        "builtin",
        "cd",
        "command",
        "continue",
        "declare",
        "echo",
        "eval",
        "exec",
        "exit",
        "export",
        "false",
        "fg",
        "hash",
        "jobs",
        "kill",
        "local",
        "logout",
        "popd",
        "printf",
        "pushd",
        "pwd",
        "read",
        "readonly",
        "return",
        "set",
        "shift",
        "source",
        "test",
        "trap",
        "true",
        "type",
        "umask",
        "unalias",
        "unset",
        "wait",
    ]

    # Highlight keywords and builtins, but avoid highlighting inside strings
    def highlight_words(text: str, words: List[str], color: str) -> str:
        for word in words:
            pattern = r"\b" + re.escape(word) + r"\b"
            # Find all matches in original line to check string context
            matches = list(re.finditer(pattern, line))
            for match in reversed(matches):
                start_pos = match.start()

                # Check if this position is inside any string
                in_string = False
                for str_start, str_end in processed_ranges:
                    if str_start <= start_pos < str_end:
                        in_string = True
                        break

                if not in_string:
                    # Replace in highlighted text
                    text = re.sub(r"\b" + re.escape(word) + r"\b", color + word + RESET, text)
        return text

    highlighted = highlight_words(highlighted, shell_keywords, KEYWORD)
    highlighted = highlight_words(highlighted, shell_builtins, FUNCTION)

    return {"output": highlighted, "handled_output": 1}
