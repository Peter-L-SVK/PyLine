#----------------------------------------------------------------
# PyLine 0.8 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

import os
import sys
import time

from typing import List, Optional, Tuple
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
from text_lib import TextLib

class TextBuffer:
    """Core text buffer handling all editing operations and state management."""
    
    def __init__(self):
        # Core buffer state
        self.lines: List[str] = [""]
        self.filename: Optional[str] = None
        self.dirty: bool = False
        
        # Navigation state
        self.current_line: int = 0
        self.display_start: int = 0
        self.display_lines: int = 40
        
        # Undo/redo system
        self.undo_stack: List[EditCommand] = []
        self.redo_stack: List[EditCommand] = []
        
        # Selection system
        self.selection_start: Optional[int] = None
        self.selection_end: Optional[int] = None
        self.in_selection_mode: bool = False
        
        # Dependencies
        self.paste_buffer = PasteBuffer()
        self.syntax_highlighter = SyntaxHighlighter()
        self.syntax_highlighting = TextLib.init_color_support()

    # File operations ----------------------------------------------------------
    def load_file(self, filename: str) -> bool:
        """Load file contents into buffer."""
        try:
            with open(filename, 'r') as f:
                self.lines = [line.rstrip('\n') for line in f]
            self.filename = filename
            self.dirty = False
            self.current_line = 0
            return True
        
        except IOError:
            print(f"\nError: Could not load {filename}\n")
            return False
        
    def save(self) -> bool:
        """Save buffer contents to file."""
        if not self.filename:
            print("\nError: No filename specified\n")
            return False

        try:
            with open(self.filename, 'w') as f:
                f.write('\n'.join(self.lines))  # Add trailing newline
            self.dirty = False
            TextLib.show_status_message(f"File saved successfully: {self.filename}\n")
            return True
        
        except IOError:
            print(f"\nError: Could not save {self.filename}\n")
            return False


    # Navigation ---------------------------------------------------------------
    def navigate(self, direction: str) -> None:
        """Move cursor up/down with viewport adjustment."""
        if direction == 'up' and self.current_line > 0:
            self.current_line -= 1
        elif direction == 'down' and self.current_line < len(self.lines) - 1:
            self.current_line += 1

        # Adjust viewport if needed
        if self.current_line < self.display_start:
            self.display_start = self.current_line
        elif self.current_line >= self.display_start + self.display_lines:
            self.display_start = self.current_line - self.display_lines + 1

    def jump_to_end(self) -> None:
        """Jump to end of buffer."""
        if self.lines:
            self.current_line = len(self.lines) - 1
            self.display_start = max(0, len(self.lines) - self.display_lines)

    # Undo/redo system ---------------------------------------------------------
    def push_undo_command(self, command: EditCommand) -> None:
        """Record a command for potential undo."""
        self.undo_stack.append(command)
        if len(self.undo_stack) > 120:  # Limit history
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self) -> None:
        """Undo the last operation."""
        if not self.undo_stack:
            TextLib.show_status_message(f"Nothing to undo")
            return
        command = self.undo_stack.pop()
        command.undo(self)
        self.redo_stack.append(command)
        self.dirty = True

    def redo(self) -> None:
        """Redo the last undone operation."""
        if not self.redo_stack:
            TextLib.show_status_message(f"Nothing to redo")
            return
        command = self.redo_stack.pop()
        command.execute(self)
        self.undo_stack.append(command)
        self.dirty = True

    # Editing operations -------------------------------------------------------
    def edit_current_line(self) -> None:
        """Edit the current line with readline support."""
        if not self.lines:
            self.lines = [""]
            self.current_line = 0
            self.dirty = True

        old_text = self.lines[self.current_line]
        new_text = TextLib.edit_line(self.current_line + 1, old_text)
        
        if new_text != old_text:
            cmd = LineEditCommand(self.current_line, old_text, new_text)
            self.push_undo_command(cmd)
            cmd.execute(self)
            self.dirty = True

    def insert_line(self) -> None:
        """Insert a new line after current position."""
        # Ensure buffer isn't empty
        if not self.lines:
            self.lines = [""]
            self.current_line = 0
            self.dirty = True
            return
        
        cmd = InsertLineCommand(self.current_line + 1, "")
        self.push_undo_command(cmd)
        cmd.execute(self)
        self.current_line += 1
        self.dirty = True

    def copy_line(self) -> bool:
        """Copy current single line to clipboard."""
        if not self.lines:
            TextLib.show_status_message("Buffer is empty")
            return False
        
        line_text = self.lines[self.current_line]
        if self.paste_buffer.copy_to_clipboard(line_text):
            TextLib.show_status_message("Copied line to clipboard")
            return True
        return False
    
    def paste_line(self, mode: str = 'insert') -> bool:
        """Paste current clipboard content as single line."""
        if not self.paste_buffer.load_from_clipboard():
            TextLib.show_status_message("Clipboard empty or inaccessible")
            return False
        
        # Get first line of clipboard content
        paste_text = self.paste_buffer.buffer[0] if self.paste_buffer.buffer else ""
        
        if mode == 'insert':
            cmd = InsertLineCommand(self.current_line + 1, paste_text)
            self.push_undo_command(cmd)
            cmd.execute(self)
            self.current_line += 1
        else:  # overwrite
            if self.current_line >= len(self.lines):
                self.lines.append(paste_text)
            else:
                old_text = self.lines[self.current_line]
                cmd = LineEditCommand(self.current_line, old_text, paste_text)
                self.push_undo_command(cmd)
                cmd.execute(self)
                
        self.dirty = True
        return True
        
    def delete_current_line(self) -> bool:
        """Delete current single line."""
        if not self.lines or self.current_line >= len(self.lines):
            return False
        
        cmd = DeleteLineCommand(self.current_line, self.lines[self.current_line])
        self.push_undo_command(cmd)
        cmd.execute(self)
        
        if self.current_line >= len(self.lines) and self.current_line > 0:
            self.current_line -= 1
            
        self.dirty = True
        return True

    # Selection operations -----------------------------------------------------
    def start_selection(self) -> None:
        """Begin line selection at current position."""
        self.selection_start = self.current_line
        self.in_selection_mode = True
        TextLib.show_status_message(f"Selection started at line {self.current_line + 1}")

    def end_selection(self) -> None:
        """End selection at current position."""
        if not self.in_selection_mode:
            TextLib.show_status_message("No selection started - use 's' first")
            return
            
        self.selection_end = self.current_line
        if self.selection_start > self.selection_end:
            self.selection_start, self.selection_end = self.selection_end, self.selection_start
        TextLib.show_status_message(f"Selected lines {self.selection_start + 1}-{self.selection_end + 1}")

    def clear_selection(self) -> None:
        """Clear current selection."""
        self.selection_start = None
        self.selection_end = None
        self.in_selection_mode = False
        self.current_line = max(0, min(self.current_line, len(self.lines)-1))

    # Clipboard operations -----------------------------------------------------
    def copy_selection(self) -> bool:
        """Copy selected lines to clipboard."""
        if self.selection_start is None or self.selection_end is None:
            TextLib.show_status_message("No selection to copy")
            return False
            
        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)
        selected_lines = self.lines[start:end+1]
        
        if self.paste_buffer.copy_to_clipboard('\n'.join(selected_lines)):
            TextLib.show_status_message(f"Copied {end-start+1} lines to clipboard")
            self.clear_selection()
            return True

        return False

    def paste_from_clipboard(self, mode: str = 'insert') -> bool:
        """Paste from clipboard with specified mode (insert/overwrite)."""
        if not self.paste_buffer.load_from_clipboard():
            TextLib.show_status_message("Clipboard empty or inaccessible")
            return False
            
        lines_pasted = (self.paste_buffer.paste_into(self) if mode == 'insert'
                       else self.paste_buffer.paste_over(self))
                       
        if lines_pasted > 0:
            TextLib.show_status_message(f"Pasted {lines_pasted} lines")
            return True

        return False

    def delete_selected_lines(self) -> bool:
        """Delete all lines in the current selection range."""
        if self.selection_start is None or self.selection_end is None:
            TextLib.show_status_message("No selection to delete")
            return False

        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)

        # Store deleted lines for undo (in reverse order)
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
            TextLib.show_status_message(f"Deleted {end - start + 1} lines")
            return True
    
        return False
    
    # Display ------------------------------------------------------------------
    def display(self) -> None:
        """Render current buffer state using TextLib."""
        TextLib.display_buffer(
            lines=self.lines,
            filename=self.filename,
            current_line=self.current_line,
            display_start=self.display_start,
            display_lines=self.display_lines,
            selection_start=self.selection_start,
            selection_end=self.selection_end,
            syntax_highlighter=self.syntax_highlighter,
            is_python=bool(self.filename and self.filename.endswith('.py'))
        )

    # Interactive editing ------------------------------------------------------
    def edit_interactive(self) -> Optional[bool]:
        """Main editing interface."""
        while True:
            self.display()
            sys.stdout.write("Command [↑↓, PgUp/PgDn/End, E(dit), I(nsert), D(el), S(elect), \
C(opy), V(paste), O(verwrite), W(rite), Q(uit)]: ")
            sys.stdout.flush()
            cmd = TextLib.get_key_input()
            
            if not cmd:
                continue
                # Handle navigation commands
            if cmd == '\x1b[A':  # Up arrow
                self.navigate('up')
            elif cmd == '\x1b[B':  # Down arrow
                self.navigate('down')
            elif cmd == '\x1b[5~':  # Page Up
                self.display_start = max(0, self.display_start - self.display_lines)
                self.current_line = max(0, self.current_line - self.display_lines)
            elif cmd == '\x1b[6~':  # Page Down
                new_start = min(len(self.lines) - self.display_lines, 
                              self.display_start + self.display_lines)
                self.display_start = max(0, new_start)
                self.current_line = min(len(self.lines) - 1,
                                      self.current_line + self.display_lines)
            elif cmd in ('\x04', '\x1b[F'):  # Ctrl+D or End
                self.jump_to_end()
                
            # Handle editing commands
            elif cmd in ('', 'e', '\r', '\n'):
                self.edit_current_line()
            elif cmd == 'i':
                self.insert_line()
            elif cmd == 'd':  # Delete
                if self.selection_start is not None and self.selection_end is not None:
                    self.delete_selected_lines()
                else:
                    self.delete_current_line()
            elif cmd == 's':
                self.start_selection() if not self.in_selection_mode else self.end_selection()
            elif cmd == 'c':  # Copy
                if self.selection_start is not None and self.selection_end is not None:
                    self.copy_selection()
                else:
                    self.copy_line()
            elif cmd == 'v':  # Paste
                self.paste_from_clipboard(mode='insert')
            elif cmd == 'o':  # Overwrite paste
                self.paste_from_clipboard(mode='overwrite')
            elif cmd == 'undo':
                self.undo()
            elif cmd == 'redo':
                self.redo()
            elif cmd == 'w':
                self.save()
                continue 

            elif cmd == 'q':
                return self._handle_quit()

            else:
                # Handle invalid key press
                print("\nInvalid key. Please use: ↑, ↓, PgUp, PgDn, End, E, Enter, I, C, D, E, O, Q, S, W")
                os.system('read -p "Press enter to continue..."')
                
    def _handle_quit(self) -> Optional[bool]:
        """Handle quit command with save prompt."""
        if not self.dirty:
            print() 
            return None
        
        while True:
            save = input("\nSave changes? (y/n): ").lower()
            
            if save == 'y':
                if self.save():
                    return True

                print("Error saving file!")
                break

            elif save == 'n':
                return False

            else:
                TextLib.move_up()
                TextLib.show_status_message("Only Y/N!")
                TextLib.move_up()
