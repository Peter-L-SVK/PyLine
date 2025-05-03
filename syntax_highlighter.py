#----------------------------------------------------------------
# PyLine 0.1 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

import re

class Colors:
    # Colors
    KEYWORD = '\033[38;5;90m'     # Dark purple (for keywords)
    STRING = '\033[38;5;28m'      # Dark green (for strings)
    COMMENT = '\033[38;5;66m'     # Desaturated blue
    VARIABLE = '\033[38;5;27m'    # Dark blue (for variables)
    NUMBER = '\033[38;5;94m'      # Brown (for numbers)
    FUNCTION = '\033[38;5;130m'   # Orange (for built-ins)
    CLASS = '\033[38;5;95m'       # Dusty rose  (for classes)
    ERROR = '\033[38;5;124m'      # Dark red (for exceptions)
    MODULE = '\033[38;5;54m'      # Purple (for imports)
    RESET = '\033[0m'             # Reset color

class SyntaxHighlighter:
    def __init__(self):
        self.in_docstring = False

    def _highlight_python(self, line):
        # Store original line for reference
        original_line = line
        highlighted_chars = [False] * len(original_line)  # Track original character positions

        # Define syntax elements to highlight (in order of priority)
        syntax_elements = [
            # Multi-line docstrings (highest priority)
            {
                'pattern': r'^\s*(\"{3}|\'{3})(.*?)(\"{3}|\'{3})?$',
                'color': lambda m: Colors.COMMENT + m.group(0) + Colors.RESET,
                'is_docstring': True
            },
            # Regular strings
            {
                'pattern': r'(\"(?:[^\"\\]|\\.)*\")|(\'(?:[^\'\\]|\\.)*\')',
                'color': Colors.STRING,
                'is_string': True
            },
            # Comments
            {
                'pattern': r'#.*$',
                'color': Colors.COMMENT,
                'check_strings': True
            },
            # Variable declarations
            {
                'pattern': r'^\s*(\w+)\s*=\s*',
                'color': lambda m: m.group(0).replace(m.group(1), Colors.VARIABLE + m.group(1) + Colors.RESET),
                'is_declaration': True
            },
            # Function definitions
            {
                'pattern': r'^\s*def\s+(\w+)\s*\(',
                'color': lambda m: m.group(0).replace('def', Colors.KEYWORD + 'def' + Colors.RESET)
                              .replace(m.group(1), Colors.FUNCTION + m.group(1) + Colors.RESET),
                'is_declaration': True
            },
            # Class definitions
            {
                'pattern': r'^\s*class\s+(\w+)',
                'color': lambda m: m.group(0).replace('class', Colors.KEYWORD + 'class' + Colors.RESET)
                          .replace(m.group(1), Colors.CLASS + m.group(1) + Colors.RESET),
                'is_declaration': True
            },
            # Exceptions
            {
                'pattern': r'(?<!\w)('
                           r'Exception|ArithmeticError|FloatingPointError|OverflowError|ZeroDivisionError|'
                           r'AssertionError|AttributeError|BufferError|EOFError|ExceptionGroup|BaseExceptionGroup|'
                           r'ImportError|ModuleNotFoundError|LookupError|IndexError|KeyError|MemoryError|'
                           r'NameError|UnboundLocalError|OSError|BlockingIOError|ChildProcessError|'
                           r'ConnectionError|BrokenPipeError|ConnectionAbortedError|ConnectionRefusedError|'
                           r'ConnectionResetError|FileExistsError|FileNotFoundError|InterruptedError|'
                           r'IsADirectoryError|NotADirectoryError|PermissionError|ProcessLookupError|'
                           r'TimeoutError|ReferenceError|RuntimeError|NotImplementedError|'
                           r'PythonFinalizationError|RecursionError|StopAsyncIteration|StopIteration|'
                           r'SyntaxError|IndentationError|TabError|SystemError|TypeError|ValueError|'
                           r'UnicodeError|UnicodeDecodeError|UnicodeEncodeError|UnicodeTranslateError'
                           r')(?!\w)',
                'color': Colors.ERROR
            },
            # Keywords - only match whole words
            {
                'pattern': r'(?<!\w)('
                           r'False|None|True|and|as|assert|async|await|break|case|class|continue|def|del|'
                           r'elif|else|except|finally|for|from|global|if|import|in|is|lambda|match|'
                           r'nonlocal|not|or|pass|raise|return|self|try|while|with|yield'
                           r')(?!\w)',
                'color': Colors.KEYWORD
            },
            # Built-in functions
            {
                'pattern': r'\b('
                           # I/O and printing
                           r'print|input|open|'
                           
                           # Type conversion
                           r'int|float|str|bool|list|dict|set|tuple|frozenset|bytes|bytearray|memoryview|'
                           r'complex|bin|hex|oct|chr|ord|'
                           
                           # Math and numbers
                           r'abs|divmod|pow|round|sum|'
                           
                           # Sequences and iteration
                           r'len|range|enumerate|zip|reversed|sorted|iter|next|'
                           
                           # Object introspection
                           r'type|isinstance|issubclass|callable|hash|id|'
                           
                           # Attributes and reflection
                           r'getattr|setattr|hasattr|delattr|vars|dir|property|super|'
                           
                           # Modules and imports
                           r'__import__|globals|locals|'
                           
                           # Code evaluation
                           r'eval|exec|compile|'
                           
                           # Decorators
                           r'staticmethod|classmethod|'
                           
                           # Files and I/O
                           r'format|repr|ascii|'
                           
                           # Misc
                           r'breakpoint|slice|any|all|min|max|map|filter|'
                           r'help|copyright|credits|license|'
                           
                           # Python 3.8+ (walrus operator support)
                           r'__build_class__|'
                           
                           # Python 3.10+ (pattern matching)
                           r'match|case'
                           r')\b(?!\w)(?=\s*\()',
                           'color': Colors.FUNCTION
            },
            # Numbers - only whole numbers
            {
                'pattern': r'(?<!\w)\d+(?!\w)',
                'color': Colors.NUMBER
            }
        ]

        # If we're in a multiline docstring, highlight the line as a comment
        if self.in_docstring:
            if '"""' in line or "'''" in line:  # Check if the docstring ends on this line
                self.in_docstring = False
                return Colors.COMMENT + line + Colors.RESET
            else:
                return Colors.COMMENT + line + Colors.RESET

        # Check if this line starts a multiline docstring
        docstring_start = re.match(r'^\s*(\"{3}|\'{3})', original_line)
        if docstring_start:
            quote_type = docstring_start.group(1)
            if original_line.rstrip().endswith(quote_type) and len(original_line.strip()) > 6:
                # Single-line docstring
                return Colors.COMMENT + original_line + Colors.RESET
            else:
                # Multiline docstring starts
                self.in_docstring = True
                return Colors.COMMENT + original_line + Colors.RESET
        
        # We'll build the highlighted line incrementally
        result = []
        i = 0
        n = len(original_line)

        # Process line character by character
        while i < n:
            matched = False
            
            # Handle f-string variables - skip coloring anything between { } in f-strings
            if original_line[i] == '{' and 'f"' in original_line[:i]:
                closing_brace = original_line.find('}', i)
                if closing_brace == -1:
                    closing_brace = len(original_line)
                    result.append(original_line[i:closing_brace + 1])
                    i = closing_brace + 1
                    continue

            # Skip parentheses, brackets, and braces (keep them black)
            if original_line[i] in '()[]{}':
                result.append(original_line[i])
                i += 1
                continue

            # Check each syntax element in priority order
            for element in syntax_elements:
                if element.get('is_docstring'):
                    continue

                pattern = element['pattern']
                color = element['color']
                check_strings = element.get('check_strings', False)
                is_string = element.get('is_string', False)
                
                # Check for matches at current position
                match = re.match(pattern, original_line[i:])
                if not match:
                    continue

                text = match.group()
                start, end = i, i + len(text)

                # Skip if within a string (unless explicitly allowed)
                if check_strings or is_string:
                    in_string = False
                    for j in range(i):
                        if original_line[j] in ('"', "'") and (j == 0 or original_line[j - 1] != '\\'):
                            in_string = not in_string
                    if in_string and not is_string:
                        continue
                
                # Refine keyword highlighting
                if element.get('color') == Colors.KEYWORD:
                    # Ensure the match is not part of a string
                    in_string = False
                    for j in range(i):
                        if original_line[j] in ('"', "'") and (j == 0 or original_line[j - 1] != '\\'):
                            in_string = not in_string
                    if in_string:  # Skip if inside a string
                        continue

                # Skip if any of these characters are already highlighted
                if any(highlighted_chars[i:i + len(text)]):
                    continue
                
                # Apply the color
                if callable(color):
                    colored_text = color(match)
                else:
                    colored_text = color + text + Colors.RESET

                result.append(colored_text)

                # Mark these positions as highlighted
                for j in range(i, i + len(text)):
                    if j < len(highlighted_chars):
                       highlighted_chars[j] = True

                # Move position forward
                i += len(text)
                matched = True
                break

            if not matched:
                # No syntax element matched at this position - keep it black
                result.append(original_line[i])
                i += 1

        return ''.join(result)
