# ----------------------------------------------------------------
# PyLine 0.9.7 - Syntax Python3 Highlight Engine (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

import re
from typing import Any, Dict, List


class Colors:
    # Colors - ensure they are strings
    KEYWORD = "\033[38;5;90m"  # Dark purple (for keywords)
    STRING = "\033[38;5;28m"  # Dark green (for strings)
    COMMENT = "\033[38;5;66m"  # Desaturated blue
    VARIABLE = "\033[38;5;27m"  # Dark blue (for variables)
    NUMBER = "\033[38;5;94m"  # Brown (for numbers)
    FUNCTION = "\033[38;5;130m"  # Orange (for built-ins)
    CLASS = "\033[38;5;95m"  # Dusty rose (for classes)
    ERROR = "\033[38;5;124m"  # Dark red (for exceptions)
    MODULE = "\033[38;5;54m"  # Purple (for imports)
    DECORATOR = "\033[38;5;92m"  # Dark Purple (for decorators)
    ANNOTATION = "\033[38;5;67m"  # Light blue (for type hints)
    RESET = "\033[0m"  # Reset color

    # Class method to ensure string conversion
    @classmethod
    def get_color(cls, color_attr: str) -> str:
        """Safely get a color attribute as string"""
        color = getattr(cls, color_attr, cls.RESET)
        return str(color) if not isinstance(color, str) else color


class SyntaxHighlighter:
    def __init__(self) -> None:
        self.in_docstring = False

    def _highlight_python(self, line: str) -> str:
        original_line = line
        highlighted_chars = [False] * len(original_line)

        # Define syntax elements to highlight (in order of priority)
        syntax_elements: List[Dict[str, Any]] = [
            # Multi-line docstrings (highest priority)
            {
                "pattern": r"^\s*(\"{3}|\'{3})(.*?)(\"{3}|\'{3})?$",
                "color": lambda m: Colors.get_color("COMMENT") + m.group(0) + Colors.get_color("RESET"),
                "is_docstring": True,
            },
            # Regular strings
            {
                "pattern": r"(\"(?:[^\"\\]|\\.)*\")|(\'(?:[^\'\\]|\\.)*\')",
                "color": Colors.get_color("STRING"),
                "is_string": True,
            },
            # Comments
            {"pattern": r"#.*$", "color": Colors.get_color("COMMENT"), "check_strings": True},
            # Special case for try/except blocks
            {
                "pattern": r"(?<!\w)(except|try|finally)\s+(\w+)\s*:",
                "color": lambda m: (
                    Colors.get_color("KEYWORD")
                    + m.group(1)
                    + Colors.get_color("RESET")
                    + " "
                    + Colors.get_color("ERROR")
                    + m.group(2)
                    + Colors.get_color("RESET")
                    + ":"
                ),
                "check_strings": True,
            },
            # Function definitions
            {
                "pattern": r"^\s*def\s+(\w+)\s*\(",
                "color": lambda m: m.group(0)
                .replace("def", Colors.get_color("KEYWORD") + "def" + Colors.get_color("RESET"))
                .replace(m.group(1), Colors.get_color("FUNCTION") + m.group(1) + Colors.get_color("RESET")),
                "is_declaration": True,
            },
            # Class definitions (only highlight in declarations)
            {
                "pattern": r"^\s*(class)\s+([\w_]+)((?:\s*\([\w\.,\s]*\s*\))?)\s*(?=:)",
                "color": lambda m: (
                    Colors.get_color("KEYWORD")
                    + m.group(1)
                    + Colors.get_color("RESET")
                    + " "
                    + Colors.get_color("CLASS")
                    + m.group(2)
                    + Colors.get_color("RESET")
                    + (m.group(3) or "")
                ),
                "is_declaration": True,
            },
            # Keywords
            {
                "pattern": r"(?<!\w)("
                r"False|None|True|and|as|assert|async|await|break|case|class|continue|def|del|"
                r"elif|else|except|exit|finally|for|from|global|if|import|in|is|lambda|match|"
                r"nonlocal|not|or|pass|raise|return|self|try|while|with|yield"
                r")(?!\w)",
                "color": Colors.get_color("KEYWORD"),
            },
            # Decorators
            {"pattern": r"^\s*@\w+(?:\.\w+)*\s*$", "color": Colors.get_color("DECORATOR"), "check_strings": True},
            # Type annotations (variable: type)
            {
                "pattern": r"\b\w+\s*:\s*[\w\[\], \.]*",
                "color": lambda m: (
                    m.group(0).split(":")[0]
                    + ":"
                    + Colors.get_color("ANNOTATION")
                    + m.group(0).split(":", 1)[1]
                    + Colors.get_color("RESET")
                ),
                "check_strings": True,
            },
            # Return annotations (-> type)
            {"pattern": r"->\s*[\w\[\], \.]*", "color": Colors.get_color("ANNOTATION"), "check_strings": True},
            # Variable declarations
            {
                "pattern": r"^\s*(?P<vars>(?:[a-zA-Z_][a-zA-Z0-9_]*\s*,\s*)*[a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*",
                "color": lambda m: (
                    m.group(0).replace(
                        m.group("vars"),
                        re.sub(
                            r"([a-zA-Z_][a-zA-Z0-9_]*)",
                            lambda x: Colors.get_color("VARIABLE") + x.group(1) + Colors.get_color("RESET"),
                            m.group("vars"),
                        ),
                    )
                ),
                "is_declaration": True,
            },
            # Exceptions pattern
            {
                "pattern": r"(?<!\w)(?!except\s+)(?!try\s+)(?!finally\s+)("
                r"BaseException|BaseExceptionGroup|GeneratorExit|KeyboardInterrupt|SystemExit|"
                r"Exception|ExceptionGroup|"
                r"ArithmeticError|FloatingPointError|OverflowError|ZeroDivisionError|"
                r"AssertionError|AttributeError|BufferError|EOFError|"
                r"ImportError|ModuleNotFoundError|"
                r"LookupError|IndexError|KeyError|"
                r"MemoryError|"
                r"NameError|UnboundLocalError|"
                r"OSError|BlockingIOError|ChildProcessError|"
                r"ConnectionError|BrokenPipeError|ConnectionAbortedError|ConnectionRefusedError|ConnectionResetError|"
                r"FileExistsError|FileNotFoundError|InterruptedError|IsADirectoryError|NotADirectoryError|"
                r"PermissionError|ProcessLookupError|TimeoutError|"
                r"ReferenceError|"
                r"RuntimeError|NotImplementedError|PythonFinalizationError|RecursionError|"
                r"StopAsyncIteration|StopIteration|"
                r"SyntaxError|IndentationError|TabError|"
                r"SystemError|"
                r"TypeError|"
                r"ValueError|UnicodeError|UnicodeDecodeError|UnicodeEncodeError|UnicodeTranslateError|"
                r"Warning|BytesWarning|DeprecationWarning|EncodingWarning|FutureWarning|ImportWarning|"
                r"PendingDeprecationWarning|ResourceWarning|RuntimeWarning|SyntaxWarning|UnicodeWarning|UserWarning"
                r")(?!\w)",
                "color": Colors.get_color("ERROR"),
            },
            # Built-in functions
            {
                "pattern": r"\b("
                r"print|input|open|"
                r"int|float|str|bool|list|dict|set|tuple|frozenset|bytes|bytearray|memoryview|"
                r"complex|bin|hex|oct|chr|ord|"
                r"abs|divmod|pow|round|sum|"
                r"len|range|enumerate|zip|reversed|sorted|iter|next|"
                r"type|isinstance|issubclass|callable|hash|id|"
                r"getattr|setattr|hasattr|delattr|vars|dir|property|super|"
                r"__import__|globals|locals|"
                r"eval|exec|compile|"
                r"staticmethod|classmethod|"
                r"format|repr|ascii|"
                r"breakpoint|slice|any|all|min|max|map|filter|"
                r"help|copyright|credits|license|"
                r"__build_class__|"
                r"match|case"
                r")\b(?!\w)(?=\s*\()",
                "color": Colors.get_color("FUNCTION"),
            },
            # Numbers (all formats)
            {
                "pattern": r"(?<!\w)("
                r"0[xX][0-9a-fA-F]+"  # Hex
                r"|0[oO]?[0-7]+"  # Octal
                r"|0[bB][01]+"  # Binary
                r"|\d+\.?\d*([eE][+-]?\d+)?"  # Float/scientific
                r"|\.\d+([eE][+-]?\d+)?"  # Float starting with .
                r"|\d+"  # Integer
                r")(?!\w)",
                "color": Colors.get_color("NUMBER"),
            },
        ]

        # Handle docstrings
        if self.in_docstring:
            if '"""' in line or "'''" in line:
                self.in_docstring = False
            return Colors.get_color("COMMENT") + line + Colors.get_color("RESET")

        docstring_start = re.match(r"^\s*(\"{3}|\'{3})", original_line)
        if docstring_start:
            quote_type = docstring_start.group(1)
            if original_line.rstrip().endswith(quote_type) and len(original_line.strip()) > 6:
                return Colors.get_color("COMMENT") + original_line + Colors.get_color("RESET")
            else:
                self.in_docstring = True
                return Colors.get_color("COMMENT") + original_line + Colors.get_color("RESET")

        # Process line character by character
        result = []
        i = 0
        n = len(original_line)

        while i < n:
            matched = False

            # Handle f-string expressions (highlight contents of {...})
            if original_line[i] == "{" and 'f"' in original_line[:i]:
                closing_brace = original_line.find("}", i)
                if closing_brace == -1:
                    closing_brace = len(original_line)

                # Extract the expression inside {}
                expr = original_line[i + 1 : closing_brace]
                if expr.strip():
                    # Highlight variables and numbers in the expression
                    highlighted_expr = self._highlight_expr(expr)
                    result.append("{" + highlighted_expr + "}")
                else:
                    result.append("{}")

                i = closing_brace + 1
                continue

            # Skip parentheses, brackets, and braces
            if original_line[i] in "()[]{}":
                result.append(original_line[i])
                i += 1
                continue

            # Check each syntax element
            for element in syntax_elements:
                if element.get("is_docstring"):
                    continue

                pattern = element["pattern"]
                color = element["color"]
                check_strings = element.get("check_strings", False)
                is_string = element.get("is_string", False)

                match = re.match(pattern, original_line[i:])
                if not match:
                    continue

                text = match.group()
                start, end = i, i + len(text)

                # Skip if already highlighted
                if any(highlighted_chars[start:end]):
                    continue

                # Skip if within a string (unless explicitly allowed)
                if check_strings or is_string:
                    in_string = False
                    for j in range(i):
                        if original_line[j] in ('"', "'") and (j == 0 or original_line[j - 1] != "\\"):
                            in_string = not in_string
                    if in_string and not is_string:
                        continue

                if element.get("color") == Colors.KEYWORD:
                    in_string = False
                    for j in range(i):
                        if original_line[j] in ('"', "'") and (j == 0 or original_line[j - 1] != "\\"):
                            in_string = not in_string
                    if in_string:
                        continue

                if callable(color):
                    colored_text = color(match)
                else:
                    colored_text = color + text + Colors.get_color("RESET")

                result.append(colored_text)

                for j in range(start, end):
                    if j < len(highlighted_chars):
                        highlighted_chars[j] = True

                i += len(text)
                matched = True
                break

            if not matched:
                result.append(original_line[i])
                i += 1

        return "".join(result)

    def _highlight_expr(self, expr: str) -> str:
        """Helper to highlight f-string expressions"""
        highlighted = []
        i = 0
        n = len(expr)

        while i < n:
            # Highlight variables
            var_match = re.match(r"[a-zA-Z_][a-zA-Z0-9_]*", expr[i:])
            if var_match:
                var = var_match.group()
                highlighted.append(Colors.get_color("VARIABLE") + var + Colors.get_color("RESET"))
                i += len(var)
                continue

            # Highlight numbers
            num_match = re.match(r"\d+\.?\d*", expr[i:])
            if num_match:
                num = num_match.group()
                highlighted.append(Colors.get_color("NUMBER") + num + Colors.get_color("RESET"))
                i += len(num)
                continue

            highlighted.append(expr[i])
            i += 1

        return "".join(highlighted)
