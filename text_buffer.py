#----------------------------------------------------------------
# PyLine 0.6 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

# Standard library imports
import fcntl
import os
import readline
import sys
import termios
import time
import tty

# Local application imports
from edit_commands import (
    DeleteLineCommand,
    EditCommand,
    InsertLineCommand,
    LineEditCommand,
    MultiDeleteCommand,
    MultiPasteInsertCommand,
    MultiPasteOverwriteCommand
)
from paste_buffer import PasteBuffer
from syntax_highlighter import SyntaxHighlighter

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
        self.syntax_highlighter = SyntaxHighlighter()
        self._init_color_support()
        self.paste_buffer = PasteBuffer()
        self.selection_start = None  # Line number where selection starts
        self.selection_end = None    # Line number where selection ends
        self.in_selection_mode = False  # Whether we're in selection mode

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
        return self.syntax_highlighter._highlight_python(line)

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

    def start_selection(self):
        """Start selection at current line"""
        self.selection_start = self.current_line
        self.in_selection_mode = True
        self._show_status_message(f"Selection started at line {self.current_line + 1}")

    def end_selection(self):
        """End selection at current line"""
        if not self.in_selection_mode:
            self._show_status_message("No selection started - use 's' first")
            return
            
        self.selection_end = self.current_line
        self._show_status_message(f"Selection ended at line {self.current_line + 1}")

    def clear_selection(self):
        """Clear current selection"""
        self.selection_start = None
        self.selection_end = None
        self.in_selection_mode = False

    def copy_selection(self):
        """Copy selected lines to both paste buffer and system clipboard"""
        if self.selection_start is None or self.selection_end is None:
            self._show_status_message("No selection to copy - use 's' to start/end selection")
            return False
        
        # Ensure start is before end
        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)
        
        # Get the selected lines
        selected_lines = self.lines[start:end+1]
        text_to_copy = '\n'.join(selected_lines)
        
        # Copy  system clipboard
        if self.paste_buffer.copy_to_clipboard(text_to_copy):
            self._show_status_message(f"Copied {end-start+1} lines to clipboard.")
        
        # Clear selection after copy
        self.clear_selection()
        return True

    def delete_selected_lines(self):
        """Delete all lines in the current selection range."""
        if self.selection_start is None or self.selection_end is None:
            self._show_status_message("No selection to delete - use 's' to start/end selection")
            return False

        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)

        # Store deleted lines for undo (in reverse order for correct deletion sequencing)
        deleted_lines = [
            (line_num, self.lines[line_num])
            for line_num in range(end, start - 1, -1)
            if line_num < len(self.lines)
        ]

        if deleted_lines:
            cmd = MultiDeleteCommand(deleted_lines)
            self.push_undo_command(cmd)
            cmd.execute(self)

            self.dirty = True
            self.clear_selection()
            self._show_status_message(f"Deleted {end - start + 1} lines")
            return True
    
        return False
    
    def _show_status_message(self, message):
        #Helper method to display status messages consistently.
        print(f"\n{message}", end='')
        time.sleep(0.455)  # Brief pause so user can read the message
        sys.stdout.flush()
        # Move cursor back up to overwrite the status message
        sys.stdout.write("\033[F")  # Move up one line
        sys.stdout.write("\033[K")  # Clear the line


    def copy_to_clipboard(self, start_line=None, end_line=None):
        """Copy selected lines to system clipboard"""
        if start_line is None:
            start_line = self.current_line
        if end_line is None:
            end_line = self.current_line
                
        lines = self.lines[start_line:end_line+1]
        text_to_copy = '\n'.join(lines)
        if self.paste_buffer.copy_to_clipboard(text_to_copy):
            self._show_status_message(f"Copied {end_line-start_line+1} lines to clipboard")
            return True
        else:
            self._show_status_message("Failed to copy to clipboard")
            return False

    def paste_from_buffer(self, mode='insert'):
        #Paste from buffer with specified mode
        if mode == 'insert':
            return self.paste_buffer.paste_into(self)

        else:    
            return self.paste_buffer.paste_over(self)

    def paste_from_clipboard(self, mode='insert'):
        """Paste from system clipboard with proper formatting"""
        if not self.paste_buffer.load_from_clipboard():
            self._show_status_message("Clipboard empty or inaccessible")
            return False
        
        if mode == 'insert':
            lines_pasted = self.paste_buffer.paste_into(self)
        else:
            lines_pasted = self.paste_buffer.paste_over(self)
            
        self._show_status_message(f"Pasted {lines_pasted} lines from clipboard")
        return True
            
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
        print("""\033[0mCommands: ↑/↓, PgUp/PgDn/End - Navigate, Enter - Edit, Ctrl+B/F - Undo/Redo,
        C - Copy, V - Paste, O - Overwrite lines, W - Write changes, S - Select,  Q - Quit""")
        print("\033[0m" + "-" * 92)  # Reset before line

        for idx in range(self.display_start,
                         min(self.display_start + self.display_lines, len(self.lines))):
            line_num = idx + 1
            # Determine prefix based on selection and current line
            if (self.selection_start is not None and self.selection_end is not None and 
                idx >= min(self.selection_start, self.selection_end) and 
                idx <= max(self.selection_start, self.selection_end)):
                prefix = "\033[1;31m=\033[0m"  # Bold red =
            elif idx == self.current_line:
                prefix = ">"
            else:
                prefix = " "
                
            line_text = self.lines[idx]
                
            if self.filename and self.filename.endswith('.py'):
                line_text = self._highlight_python(line_text)
                    
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
                sys.stdout.write("Command [↑↓, PgUp/PgDn/End, E(dit), I(nsert), D(el), S(elect), C(opy), V(paste), O(verwrite), W(rite), Q(uit)]: ")
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
                elif cmd == 's':  # Start/end selection
                    if not self.in_selection_mode:
                        self.start_selection()
                    else:
                        self.end_selection()
                elif cmd == 'c':  # Copy
                    if self.selection_start is not None and self.selection_end is not None:
                        self.copy_selection()
                    else:
                        if self.copy_to_clipboard():
                            self._show_status_message("Copied current line to clipboard")
                elif cmd == 'v':  # Paste insert mode
                    # Try internal buffer first, then clipboard
                    if hasattr(self, 'paste_buffer') and self.paste_buffer.buffer:
                        lines_pasted = self.paste_buffer.paste_into(self)
                        self._show_status_message(f"Pasted {lines_pasted} lines from buffer")
                    elif self.paste_from_clipboard(mode='insert'):
                        pass  # Message already shown by paste_from_clipboard
                    else:
                        self._show_status_message("Nothing to paste - copy first")
                        
                elif cmd == 'o':  # Paste overwrite mode
                    # Try internal buffer first, then clipboard
                    if hasattr(self, 'paste_buffer') and self.paste_buffer.buffer:
                        lines_pasted = self.paste_buffer.paste_over(self)
                        self._show_status_message(f"Overwrote with {lines_pasted} lines from buffer")
                    elif self.paste_from_clipboard(mode='overwrite'):
                        pass  # Message already shown by paste_from_clipboard
                    else:
                        self._show_status_message("Nothing to paste - copy first")
                elif cmd == 'd':
                    if self.selection_start is not None and self.selection_end is not None:
                        self.delete_selected_lines()
                    else:
                        self.delete_line()
                elif cmd == 'w':
                    if self.save():
                        print("Changes written.")
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
                    print("Invalid key. Please use: ↑, ↓, PgUp, PgDn, End, E, Enter, I, C, D, E, O, Q, S, W")
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
