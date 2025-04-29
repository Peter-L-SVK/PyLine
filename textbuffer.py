import os
import readline
import sys
import tty
import termios
import fcntl
import time
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

class EditCommand:
    #Base class for all editable commands.
    def execute(self, buffer):
         raise NotImplementedError

    def undo(self, buffer):
         raise NotImplementedError

class LineEditCommand(EditCommand):
    #Tracks changes to a single line.
    def __init__(self, line_num, old_text, new_text):
        self.line_num = line_num
        self.old_text = old_text
        self.new_text = new_text

    def execute(self, buffer):
        if self.line_num < len(buffer.lines):
            buffer.lines[self.line_num] = self.new_text

    def undo(self, buffer):
        if self.line_num < len(buffer.lines):
            buffer.lines[self.line_num] = self.old_text

class InsertLineCommand(EditCommand):
    #Tracks line insertion.
    def __init__(self, line_num, text):
        self.line_num = line_num
        self.text = text

    def execute(self, buffer):
        buffer.lines.insert(self.line_num, self.text)

    def undo(self, buffer):
        if self.line_num < len(buffer.lines):
            del buffer.lines[self.line_num]

class DeleteLineCommand(EditCommand):
    #Tracks line deletion.
    def __init__(self, line_num, text):
        self.line_num = line_num
        self.text = text

    def execute(self, buffer):
        if self.line_num < len(buffer.lines):
            del buffer.lines[self.line_num]

    def undo(self, buffer):
        buffer.lines.insert(self.line_num, self.text)

class TextBuffer:
    def __init__(self):
        self.lines = []
        self.filename = None
        self.dirty = False
        self.current_line = 0
        self.current_col = 0
        self.display_start = 0
        self.display_lines = 40
        self.edit_history = {}
        self.undo_stack = []  # Stack for undo commands
        self.redo_stack = []  # Stack for redo commands
        self.syntax_highlighting = False
        self._init_color_support()

    def _init_color_support(self):
        #Initialize color support with more thorough checks
        self.syntax_highlighting = False

        # Check basic terminal support
        if not (hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()):  # Fixed this line
            return

        # Check TERM environment variable
        term = os.environ.get('TERM', '')
        if term == 'dumb':
            return

        # Force color support for testing (comment this out after testing)
        self.syntax_highlighting = True

    def _highlight_python(self, line):
        if not self.syntax_highlighting:
            return line

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
                'pattern': r'(?<!\w)('
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
                           r')(?!\w)(?=\s*\()',
                           'color': Colors.FUNCTION
            },
            # Numbers - only whole numbers
            {
                'pattern': r'(?<!\w)\d+(?!\w)',
                'color': Colors.NUMBER
            }
        ]

        # If we're in a multiline docstring, highlight the line as a comment
        if getattr(self, "in_docstring", False):
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
        in_docstring = False
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

    def push_undo_command(self, command):
        #Push a command to the undo stack and clear redo stack.
        self.undo_stack.append(command)
        if len(self.undo_stack) > 120:  # Limit history
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        """Undo the last action with user-friendly feedback."""
        if not self.undo_stack:
            self._show_status_message("Nothing to undo")
            return

        command_type = type(self.undo_stack[-1]).__name__
        action_map = {
            'LineEditCommand': 'edit',
            'InsertLineCommand': 'insertion',
            'DeleteLineCommand': 'deletion'
        }
        action = action_map.get(command_type, 'change')

        self._show_status_message(f"Undoing last {action}")
        command = self.undo_stack.pop()
        command.undo(self)
        self.redo_stack.append(command)
        self.dirty = True

    def redo(self):
        #Redo the last undone action with user-friendly feedback.
        if not self.redo_stack:
            self._show_status_message("Nothing to redo")
            return

        command_type = type(self.redo_stack[-1]).__name__
        action_map = {
            'LineEditCommand': 'edit',
            'InsertLineCommand': 'insertion',
            'DeleteLineCommand': 'deletion'
        }
        action = action_map.get(command_type, 'change')

        self._show_status_message(f"Redoing last {action}")
        command = self.redo_stack.pop()
        command.execute(self)
        self.undo_stack.append(command)
        self.dirty = True

    def _show_status_message(self, message):
        #Helper method to display status messages consistently.
        print(f"\n{message}", end='')
        time.sleep(0.355)  # Brief pause so user can read the message
        sys.stdout.flush()
        # Move cursor back up to overwrite the status message
        sys.stdout.write("\033[F")  # Move up one line
        sys.stdout.write("\033[K")  # Clear the line


    def load_file(self, filename):
        # Load file contents into buffer
        try:
            with open(filename, 'r') as f:
                self.lines = [line.rstrip('\n') for line in f.readlines()]
            self.filename = filename
            self.dirty = False
            self.current_line = 0
            self.current_col = 0
            return True
        except IOError:
            return False

    def save(self):
        # Save buffer contents to file
        if not self.filename:
            return False

        try:
            with open(self.filename, 'w') as f:
                f.write('\n'.join(self.lines))
            self.dirty = False
            return True
        except IOError:
            return False


    def display(self):
        os.system('clear')
        # Force enable color for testing
        sys.stdout.write("\033[?25h")  # Ensure cursor is visible
        sys.stdout.write("\033[0m")    # Reset all attributes

        # Print header with forced color reset
        print(f"\033[0mEditing: {self.filename or 'New file'}")
        print("\033[0mCommands: ↑/↓, PgUp/PgDn/End - Navigate, Enter - Edit,")
        print("\t   Ctrl+B/F - Undo/Redo, S - Save, Q - Quit")
        print("\033[0m" + "-" * 80)  # Reset before line

        for idx in range(self.display_start,
                         min(self.display_start + self.display_lines, len(self.lines))):
            line_num = idx + 1
            prefix = ">" if idx == self.current_line else " "
            line_text = self.lines[idx]

            if self.filename and self.filename.endswith('.py'):
                line_text = self._highlight_python(line_text)

                # Ensure RESET at end of each line
                print(f"\033[0m{prefix}{line_num:4d}: {line_text}\033[0m")

        sys.stdout.flush()

    def navigate(self, direction):
        # Move cursor up/down
        if direction == 'up' and self.current_line > 0:
            self.current_line -= 1
        elif direction == 'down' and self.current_line < len(self.lines) - 1:
            self.current_line += 1

        # Adjust scroll position if needed
        if self.current_line < self.display_start:
            self.display_start = self.current_line
        elif self.current_line >= self.display_start + self.display_lines:
            self.display_start = self.current_line - self.display_lines + 1

    def edit_current_line(self):
        # Edit the current line with previous text available
        if not self.lines:  # If buffer is completely empty
            self.lines.append("")
            self.current_line = 0

        # Ensure current_line is within bounds
        if self.current_line >= len(self.lines):
            self.current_line = len(self.lines) - 1

        # Store original line for undo
        old_text = self.lines[self.current_line]

        # Set up readline with existing line content
        readline.set_startup_hook(lambda: readline.insert_text(old_text))
        try:
            # Show prompt with line number and previous text
            prompt = f"{self.current_line+1:4d} [edit]: "
            new_text = input(prompt).rstrip('\n')

            if new_text != old_text:
                # Create and execute an undoable command (using class-based approach)
                cmd = LineEditCommand(self.current_line, old_text, new_text)
                self.push_undo_command(cmd)
                cmd.execute(self)
                self.dirty = True
        finally:
            # Clean up readline hook
            readline.set_startup_hook(None)

    def insert_line(self):
        # Create and execute an undoable command (using class-based approach)
        cmd = InsertLineCommand(self.current_line + 1, "")
        self.push_undo_command(cmd)
        cmd.execute(self)

        # Original logic
        self.current_line += 1
        if self.current_line >= len(self.lines):
            self.current_line = len(self.lines) - 1
        self.dirty = True

    def delete_line(self):
        if self.lines:
            # Create and execute an undoable command (using class-based approach)
            cmd = DeleteLineCommand(self.current_line, self.lines[self.current_line])
            self.push_undo_command(cmd)
            cmd.execute(self)

            # Original logic
            if self.current_line >= len(self.lines) and self.current_line > 0:
                self.current_line -= 1
            self.dirty = True

    def get_key_input(self):
        # Read a single key press, including arrow keys
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)

            # First check for undo/redo shortcuts (Ctrl+B and Ctrl+F)
            if ch == '\x02':  # Ctrl+B for undo
                return 'undo'
            elif ch == '\x06':  # Ctrl+F for redo
                return 'redo'

            if ch == '\x1b':  # Possible arrow key or other special key
                # Set non-blocking mode temporarily
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
                try:
                    ch2 = sys.stdin.read(2)  # Try to read 2 more characters
                    if len(ch2) == 2:
                        if ch2[0] == '[':
                            if ch2[1] in 'AB':  # Arrow keys
                                return ch + ch2
                            elif ch2[1] == '5':  # PgUp
                                ch3 = sys.stdin.read(1)
                                if ch3 == '~':
                                    return '\x1b[5~'
                            elif ch2[1] == '6':  # PgDn
                                ch3 = sys.stdin.read(1)
                                if ch3 == '~':
                                    return '\x1b[6~'
                            elif ch2[1] == 'F':  # End key
                                return '\x1b[F'

                except:
                    pass
                finally:
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl)
                return ch  # Return just ESC if not special key

            return ch.lower() if ch else ''  # Return regular key as lowercase or empty string if no input

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def edit_interactive(self):
        # Main editing interface with proper key handling
        while True:
            self.display()
            try:
                sys.stdout.write("Command [↑↓, PgUp/PgDn/End, E(dit), I(nsert), D(el), S(ave), Q(uit)]: ")
                sys.stdout.flush()

                cmd = self.get_key_input()
                if not cmd:  # Skip if no command received
                    continue

                if cmd == 'undo':   # Ctrl+B for undo
                    self.undo()
                    continue
                elif cmd == 'redo':   # Ctrl+F for redo
                    self.redo()
                    continue

                # Handle arrow keys
                if cmd in ('\x1b[A', '\x1b[B'):
                    sys.stdout.write('\n')
                    if cmd == '\x1b[A':
                        self.navigate('up')
                    elif cmd == '\x1b[B':
                        self.navigate('down')
                    continue

                # Handle PgUp/PgDn
                if cmd in ('\x1b[5~', '\x1b[6~'):
                    sys.stdout.write('\n')
                    if cmd == '\x1b[5~':  # PgUp
                        self.display_start = max(0, self.display_start - self.display_lines)
                        self.current_line = max(0, self.current_line - self.display_lines)
                    elif cmd == '\x1b[6~':  # PgDn
                        sys.stdout.write('\n')
                        new_start = min(
                            len(self.lines) - self.display_lines,  # Don't overshoot
                            self.display_start + self.display_lines  # Normal jump
                        )
                        self.display_start = max(0, new_start)  # Clamp to 0
                        self.current_line = min(
                            len(self.lines) - 1,
                            self.current_line + self.display_lines
                        )
                    continue

                # Handle Ctrl+D (EOF), End and Ctrl+C first before other commands
                if cmd in ('\x04', '\x1b[F', '\x03'):
                    if cmd == '\x04' or cmd == '\x1b[F':
                        if self.lines:
                            self.current_line = len(self.lines) - 1
                            self.display_start = max(0, len(self.lines) - self.display_lines)
                        continue

                    elif cmd == '\x03':  # ASCII code for Ctrl+C
                        # Show a message and continue editing
                        print()
                        print("^C - Use 'Q' to quit or continue editing")
                        os.system('read -p "Press enter to continue..."')
                        continue

                # Echo and process other commands
                sys.stdout.write(cmd + '\n')

                if cmd in ('', 'e', '\r', '\n'):
                    self.edit_current_line()
                elif cmd == 'i':
                    self.insert_line()
                elif cmd == 'd':
                    self.delete_line()
                elif cmd == 's':
                    if self.save():
                        print("File saved.")
                        self.edit_history.clear()
                    else:
                        print("Error saving file!")
                    os.system('read -p "Press enter to continue..."')
                elif cmd == 'q':
                    if self.dirty:
                        while True:
                            save = input("Save changes? (y/n): ").lower()
                            if save == 'y':
                                if self.save():
                                    print("Changes saved.")
                                    self.edit_history.clear()
                                    self.dirty = False
                                    return True  # Indicate save was performed
                                else:
                                    print("Error saving file!")
                                    continue
                            elif save == 'n':
                                print("Changes not saved.")
                                return False  # Indicate no save was performed
                            else:
                                print("Only Y/N!")
                    return None  # Indicate no changes needed saving
                else:
                    # Handle invalid key press
                    print("Invalid key. Please use: ↑, ↓, PgUp, PgDn, End, E, Enter, I, D, S, Q")
                    os.system('read -p "Press enter to continue..."')

            except EOFError:
                # Secondary handling of Ctrl+D if it wasn't caught as '\x04'
                if self.lines:
                    self.current_line = len(self.lines) - 1
                    self.display_start = max(0, len(self.lines) - self.display_lines)
                continue

            except KeyboardInterrupt:
                # Show a message and continue editing
                print()
                print("^C - Use 'Q' to quit or continue editing")
                os.system('read -p "Press enter to continue..."')
                continue
