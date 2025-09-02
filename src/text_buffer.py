# ----------------------------------------------------------------
# PyLine 0.9.7 - Text Buffer (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

import os
import sys
import readline

from typing import Any, List, Optional, Union
from buffer_manager import BufferManager
from undo_manager import UndoManager
from selection_manager import SelectionManager
from navigation_manager import NavigationManager
from hook_manager import HookManager
from hook_utils import HookUtils
from paste_buffer import PasteBuffer
from syntax_highlighter import SyntaxHighlighter
from text_lib import TextLib
from edit_commands import DeleteLineCommand, InsertLineCommand, LineEditCommand, MultiDeleteCommand


class TextBuffer:
    """Coordinator class with comprehensive hook integration."""

    def __init__(self) -> None:
        # Initialize hook system first
        self.hook_manager = HookManager()
        self.hook_utils = HookUtils(self.hook_manager)

        # Initialize managers with hook integration
        self.buffer_manager = BufferManager(self.hook_utils)
        self.undo_manager = UndoManager()
        self.selection_manager = SelectionManager(self.hook_utils)
        self.navigation_manager = NavigationManager(self.hook_utils)

        # Other dependencies
        self.paste_buffer = PasteBuffer()
        self.syntax_highlighter = SyntaxHighlighter()
        self.syntax_highlighting = TextLib.init_color_support()

        # Session hooks
        self._execute_session_hooks("session_start")

    def _execute_session_hooks(self, action: str) -> None:
        """Execute session-level hooks."""
        session_context = {
            "filename": self.buffer_manager.filename,
            "action": action,
            "operation": "session_management",
        }
        if action == "session_start":
            self.hook_utils.execute_pre_edit(session_context)
        else:
            self.hook_utils.execute_post_edit(session_context)

    def __del__(self) -> None:
        """Cleanup with session end hooks."""
        self._execute_session_hooks("session_end")

    # File operations ----------------------------------------------------------
    def load_file(self, filename: str) -> bool:
        """Load file contents into buffer."""
        return self.buffer_manager.load_file(filename)

    def save(self) -> bool:
        """Save buffer contents to file."""
        success = self.buffer_manager.save()
        if success:
            TextLib.show_status_message(f"File saved successfully: {self.buffer_manager.filename}\n")
        else:
            print(f"\nError: Could not save {self.buffer_manager.filename}\n")
        return success

    # Navigation ---------------------------------------------------------------
    def navigate(self, direction: str) -> None:
        """Move cursor up/down with viewport adjustment."""
        filename_str = self.buffer_manager.filename or ""
        self.navigation_manager.navigate(direction, self.buffer_manager.get_line_count(), filename_str)

    def jump_to_end(self) -> None:
        """Jump to end of buffer."""
        filename_str = self.buffer_manager.filename or ""
        self.navigation_manager.jump_to_end(self.buffer_manager.get_line_count(), filename_str)

    def page_up(self) -> None:
        """Move page up."""
        filename_str = self.buffer_manager.filename or ""
        self.navigation_manager.page_up(self.buffer_manager.get_line_count(), filename_str)

    def page_down(self) -> None:
        """Move page down."""
        filename_str = self.buffer_manager.filename or ""
        self.navigation_manager.page_down(self.buffer_manager.get_line_count(), filename_str)

    # Undo/redo system ---------------------------------------------------------
    def push_undo_command(self, command: Any) -> None:
        """Record a command for potential undo."""
        self.undo_manager.push_command(command)

    def undo(self) -> None:
        """Undo the last operation."""
        command = self.undo_manager.undo()
        if command:
            command.undo(self.buffer_manager)
            self.buffer_manager.dirty = True
            TextLib.show_status_message("Undo completed")
        else:
            TextLib.show_status_message("Nothing to undo")

    def redo(self) -> None:
        """Redo the last undone operation."""
        command = self.undo_manager.redo()
        if command:
            command.execute(self.buffer_manager)
            self.buffer_manager.dirty = True
            TextLib.show_status_message("Redo completed")
        else:
            TextLib.show_status_message("Nothing to redo")

    # Editing operations -------------------------------------------------------
    def edit_current_line(self) -> None:
        """Edit the current line using hook-based input system."""
        current_line = self.navigation_manager.get_current_line()

        if self.buffer_manager.get_line_count() == 0:
            self.buffer_manager.lines = [""]
            self.navigation_manager.set_current_line(0, self.buffer_manager.get_line_count())
            self.buffer_manager.dirty = True

        old_text = self.buffer_manager.get_line(current_line)

        # Prepare context for input handlers
        context = {
            "line_number": current_line + 1,
            "current_text": old_text,
            "previous_text": self.buffer_manager.get_line(current_line - 1) if current_line > 0 else "",
            "filename": self.buffer_manager.filename,
            "buffer_lines": self.buffer_manager.lines,
            "current_line_index": current_line,
            "action": "edit_line",
            "operation": "line_edit",
        }

        # Try to use hook-based input handler
        new_text = self.hook_utils.execute_edit_line(context)

        # Handle JSON wrapper from hooks
        if isinstance(new_text, dict):
            if new_text.get("success") and isinstance(new_text.get("output"), str):
                new_text = new_text["output"]
            else:
                new_text = None
        elif not isinstance(new_text, str):
            new_text = None

        # Fallback to standard readline if no valid result from hook
        if new_text is None:
            readline.set_startup_hook(lambda: readline.insert_text(old_text))
            try:
                print()
                prompt = f"{current_line + 1:4d} [edit]: "
                new_text = input(prompt)
            finally:
                readline.set_startup_hook(None)

        # Process the result
        if new_text is not None:
            # Remove any trailing newlines from input() and preserve the original newline status
            new_text = new_text.rstrip("\n\r")

            # If the original text had a newline, preserve it
            if old_text.endswith("\n"):
                new_text = new_text + "\n"

            if new_text != old_text:
                cmd = LineEditCommand(current_line, old_text, new_text)
                self.push_undo_command(cmd)
                cmd.execute(self.buffer_manager)
                self.buffer_manager.dirty = True

        # Clear the input line and redisplay the buffer
        TextLib.clear_line()
        TextLib.move_up(1)  # Move up one line to clear the input prompt
        self.display()  # Refresh the display to show the updated content

    def insert_line(self) -> None:
        """Insert a new line after current position."""
        current_line = self.navigation_manager.get_current_line()

        # Use buffer manager's hook-integrated insert
        inserted_text = self.buffer_manager.insert_line(current_line + 1, "")

        if inserted_text is not None:  # Not cancelled by hooks
            cmd: Union[InsertLineCommand, LineEditCommand] = InsertLineCommand(current_line + 1, inserted_text)
            self.push_undo_command(cmd)
            self.navigation_manager.set_current_line(current_line + 1, self.buffer_manager.get_line_count())

    def delete_current_line(self) -> bool:
        """Delete current single line."""
        current_line = self.navigation_manager.get_current_line()

        if self.buffer_manager.get_line_count() == 0 or current_line >= self.buffer_manager.get_line_count():
            return False

        # Use buffer manager's hook-integrated delete
        deleted_text = self.buffer_manager.delete_line(current_line)

        if deleted_text:  # Not cancelled by hooks
            cmd = DeleteLineCommand(current_line, deleted_text)
            self.push_undo_command(cmd)

            if current_line >= self.buffer_manager.get_line_count() and current_line > 0:
                self.navigation_manager.set_current_line(current_line - 1, self.buffer_manager.get_line_count())

            return True
        return False

    # Selection operations -----------------------------------------------------
    def start_selection(self) -> None:
        """Begin line selection at current position."""
        current_line = self.navigation_manager.get_current_line()
        filename_str = self.buffer_manager.filename or ""
        self.selection_manager.start_selection(current_line, filename_str)
        TextLib.show_status_message(f"Selection started at line {current_line + 1}")
        TextLib.clear_line()
        TextLib.move_up(1)

    def end_selection(self) -> None:
        """End selection at current position."""
        if not self.selection_manager.in_selection_mode:
            TextLib.show_status_message("No selection started - use 's' first")
            TextLib.clear_line()
            TextLib.move_up(1)
            return

        current_line = self.navigation_manager.get_current_line()
        filename_str = self.buffer_manager.filename or ""
        self.selection_manager.end_selection(current_line, filename_str)

        if self.selection_manager.has_selection():
            start, end = self.selection_manager.get_selection_range()
            if start is not None and end is not None:
                TextLib.show_status_message(f"Selected lines {start + 1}-{end + 1}")
        else:
            TextLib.show_status_message("Selection cleared")
        TextLib.clear_line()
        TextLib.move_up(1)

    def clear_selection(self) -> None:
        """Clear current selection."""
        self.selection_manager.clear_selection()
        current_line = self.navigation_manager.get_current_line()
        self.navigation_manager.set_current_line(current_line, self.buffer_manager.get_line_count())

    # Clipboard operations -----------------------------------------------------
    def copy_line(self) -> bool:
        """Copy current single line to clipboard."""
        if self.buffer_manager.get_line_count() == 0:
            TextLib.show_status_message("Buffer is empty")
            return False

        current_line = self.navigation_manager.get_current_line()
         # Null check for lines
        if not self.buffer_manager.lines or current_line >= len(self.buffer_manager.lines):
            TextLib.show_status_message("Invalid line")
            return False
        line_text = self.buffer_manager.get_line(current_line)

        # Validate the line text itself isn't empty
        if not line_text or line_text.strip() == "":
            TextLib.show_status_message("Line is empty - nothing to copy")
            return False

        # Try to get text through selection manager (with hooks)
        filename_str = self.buffer_manager.filename or ""
        text_to_copy = self.selection_manager.get_selected_text([line_text], filename_str)

        # Fallback: If selection manager returns empty/None/invalid, use the raw line text
        if not text_to_copy or text_to_copy.strip() == "" or not isinstance(text_to_copy, str):
            text_to_copy = line_text

        if self.paste_buffer.copy_to_clipboard(text_to_copy):
            TextLib.show_status_message("Copied line to clipboard")
            TextLib.clear_line()
            TextLib.move_up(1)
            return True

        TextLib.show_status_message("Failed to copy to clipboard")
        return False

    def copy_selection(self) -> bool:
        """Copy selected lines to clipboard."""
        if not self.selection_manager.has_selection():
            TextLib.show_status_message("No selection to copy")
            return False

        # Null check for lines
        if not self.buffer_manager.lines:
            TextLib.show_status_message("Buffer is empty")
            return False
        
        # Get selected text through selection manager (with hooks)
        filename_str = self.buffer_manager.filename or ""
        selected_text = self.selection_manager.get_selected_text(self.buffer_manager.lines, filename_str)

        # Check if selected_text is valid before copying
        if selected_text is None or not isinstance(selected_text, str):
            TextLib.show_status_message("No valid text to copy")
            return False

        if self.paste_buffer.copy_to_clipboard(selected_text):
            start, end = self.selection_manager.get_selection_range()
            if start is not None and end is not None:
                TextLib.show_status_message(f"Copied {end - start + 1} lines to clipboard")
            TextLib.clear_line()
            TextLib.move_up(1)
            self.clear_selection()
            return True

        return False

    def paste_line(self, mode: str = "insert") -> bool:
        """Paste clipboard content - handles both single and multi-line."""
        if not self.paste_buffer.load_from_clipboard():
            TextLib.show_status_message("Clipboard empty - copy something first")
            return False

        current_line = self.navigation_manager.get_current_line()

        # Check if buffer exists and has content - more defensive approach
        if (
            self.paste_buffer.buffer is None
            or not isinstance(self.paste_buffer.buffer, list)
            or len(self.paste_buffer.buffer) == 0
        ):
            TextLib.show_status_message("Clipboard empty - copy something first")
            return False

        paste_buffer_content = self.paste_buffer.buffer
        paste_text = paste_buffer_content[0]

        # If clipboard has only one line, use single-line paste logic
        if len(paste_buffer_content) == 1:
            paste_text = paste_buffer_content[0]

            # Pre-paste hooks
            paste_context = {
                "text": paste_text,
                "mode": mode,
                "line_number": current_line,
                "filename": self.buffer_manager.filename,
                "action": "pre_paste",
                "operation": "clipboard",
            }
            paste_result = self.hook_utils.execute_pre_paste(paste_context)

            text_to_paste = paste_text
            if paste_result and "text" in paste_result:
                text_to_paste = paste_result["text"]

            if mode == "insert":
                # Use buffer manager's hook-integrated insert
                inserted_text = self.buffer_manager.insert_line(current_line + 1, text_to_paste)
                if inserted_text is not None:
                    cmd: Union[InsertLineCommand, LineEditCommand] = InsertLineCommand(current_line + 1, inserted_text)
                    self.push_undo_command(cmd)
                    self.navigation_manager.set_current_line(current_line + 1, self.buffer_manager.get_line_count())
            else:  # overwrite
                if current_line >= self.buffer_manager.get_line_count():
                    self.buffer_manager.lines.append(text_to_paste)
                else:
                    old_text = self.buffer_manager.get_line(current_line)
                    # Use buffer manager's hook-integrated set_line
                    new_text = self.buffer_manager.set_line(current_line, text_to_paste)
                    if new_text != old_text:
                        cmd = LineEditCommand(current_line, old_text, new_text)
                        self.push_undo_command(cmd)

            # Post-paste hooks
            post_paste_context = {
                "text": text_to_paste,
                "mode": mode,
                "line_number": current_line,
                "filename": self.buffer_manager.filename,
                "action": "post_paste",
                "operation": "clipboard",
            }
            self.hook_utils.execute_post_paste(post_paste_context)
            TextLib.show_status_message("Pasting 1 line")
            TextLib.clear_line()
            TextLib.move_up(1)

        else:
            # Multi-line paste - use the existing multi-line logic
            if mode == "insert":
                lines_pasted = self.paste_buffer.paste_into(self, current_line)
                if lines_pasted > 0:
                    # Update navigation to the first pasted line
                    self.navigation_manager.set_current_line(current_line, self.buffer_manager.get_line_count())
                    TextLib.show_status_message(f"Pasting {lines_pasted} lines")
                    TextLib.clear_line()
                    TextLib.move_up(1)
                    return True
                return False
            else:
                lines_pasted = self.paste_buffer.paste_over(self, current_line)
                return lines_pasted > 0

        self.buffer_manager.dirty = True
        return True

    def delete_selected_lines(self) -> bool:
        """Delete all lines in the current selection range."""
        if not self.selection_manager.has_selection():
            TextLib.show_status_message("No selection to delete")
            return False

        start, end = self.selection_manager.get_selection_range()
        if start is None or end is None:
            TextLib.show_status_message("Invalid selection range")
            return False

        # Null check for lines
        if not self.buffer_manager.lines:
            TextLib.show_status_message("Buffer is empty")
            return False

        # Store deleted lines for undo (in reverse order)
        deleted_lines = []
        for line_num in range(end, start - 1, -1):
            if line_num < self.buffer_manager.get_line_count():
                line_text = self.buffer_manager.get_line(line_num)
                deleted_lines.append((line_num, line_text))

        if deleted_lines:
            # Use buffer manager's hook-integrated delete for each line
            for line_num, line_text in deleted_lines:
                deleted = self.buffer_manager.delete_line(line_num)
                if not deleted:  # Cancelled by hooks
                    TextLib.show_status_message(f"Deletion cancelled at line {line_num + 1}")
                    return False

            cmd = MultiDeleteCommand(deleted_lines)
            self.push_undo_command(cmd)

            self.clear_selection()
            TextLib.show_status_message(f"Deleted {end - start + 1} lines")
            return True

        return False

    # Display ------------------------------------------------------------------
    def display(self) -> None:
        """Render current buffer state using TextLib."""

        # Pre-display hooks
        display_context = {
            "filename": self.buffer_manager.filename,
            "line_count": self.buffer_manager.get_line_count(),
            "current_line": self.navigation_manager.get_current_line(),
            "action": "pre_display",
            "operation": "rendering",
        }
        self.hook_utils.execute_pre_edit(display_context)

        TextLib.display_buffer(
            lines=self.buffer_manager.lines,
            filename=self.buffer_manager.filename,
            current_line=self.navigation_manager.get_current_line(),
            display_start=self.navigation_manager.display_start,
            display_lines=self.navigation_manager.display_lines,
            selection_start=self.selection_manager.selection_start,
            selection_end=self.selection_manager.selection_end,
            syntax_highlighter=self.syntax_highlighter,
            is_python=bool(self.buffer_manager.filename and self.buffer_manager.filename.endswith(".py")),
        )

        # Post-display hooks
        post_display_context = {
            "filename": self.buffer_manager.filename,
            "line_count": self.buffer_manager.get_line_count(),
            "current_line": self.navigation_manager.get_current_line(),
            "action": "post_display",
            "operation": "rendering",
        }
        self.hook_utils.execute_post_edit(post_display_context)

    # Interactive editing ------------------------------------------------------
    def edit_interactive(self) -> Optional[bool]:
        """Main editing interface."""
        try:
            while True:
                self.display()
                sys.stdout.write(
                    "Command [↑↓, PgUp/PgDn/End, E(dit), I(nsert), D(el), S(elect),\
 C(opy), V(paste), O(verwrite), W(rite), Q(uit)]: "
                )
                sys.stdout.flush()
                cmd = TextLib.get_key_input()

                if not cmd:
                    continue

                # Handle navigation commands
                if cmd == "\x1b[A":  # Up arrow
                    self.navigate("up")
                elif cmd == "\x1b[B":  # Down arrow
                    self.navigate("down")
                elif cmd == "\x1b[5~":  # Page Up
                    self.page_up()
                elif cmd == "\x1b[6~":  # Page Down
                    self.page_down()
                elif cmd in ("\x04", "\x1b[F"):  # Ctrl+D or End
                    self.jump_to_end()

                # Handle editing commands
                elif cmd in ("", "e", "\r", "\n"):
                    self.edit_current_line()
                elif cmd == "i":
                    self.insert_line()
                elif cmd == "d":  # Delete
                    if self.selection_manager.has_selection():
                        self.delete_selected_lines()
                    else:
                        self.delete_current_line()
                elif cmd == "s":
                    if not self.selection_manager.in_selection_mode:
                        self.start_selection()
                    else:
                        self.end_selection()
                elif cmd == "c":  # Copy
                    if self.selection_manager.has_selection():
                        self.copy_selection()
                    else:
                        self.copy_line()
                elif cmd == "v":  # Paste
                    self.paste_line(mode="insert")
                elif cmd == "o":  # Overwrite paste
                    self.paste_line(mode="overwrite")
                elif cmd == "undo":
                    self.undo()
                elif cmd == "redo":
                    self.redo()
                elif cmd == "w":
                    if self.save():
                        continue
                    else:
                        TextLib.show_status_message("Save failed!")
                elif cmd == "q" or cmd == "\x1b":
                    return self._handle_quit()
                else:
                    # Handle invalid key press
                    print("\nInvalid key. Please use: ↑, ↓, PgUp, PgDn, End, E, Enter,Esc, I, C, D, E, O, Q, S, W")
                    os.system('read -p "Press enter to continue..."')

        finally:
            # Ensure session end hooks are called
            self._execute_session_hooks("session_end")
        return None  # Add explicit return for the missing return statement

    def _handle_quit(self) -> Optional[bool]:
        """Handle quit command with save prompt."""
        if not self.buffer_manager.dirty:
            print()
            return None

        while True:
            save = input("\nSave changes? (y/n): ").lower()
            if save == "y":
                TextLib.move_up()
                if self.save():
                    return True
                print("Error saving file!")
                break
            elif save == "n":
                return False
            else:
                TextLib.move_up()
                TextLib.show_status_message("Only Y/N!")
                TextLib.move_up()
        return None

    # Property accessors for compatibility
    @property
    def lines(self) -> List[str]:
        return self.buffer_manager.lines

    @property
    def filename(self) -> Optional[str]:
        return self.buffer_manager.filename

    @filename.setter
    def filename(self, value: str) -> None:
        self.buffer_manager.filename = value

    @property
    def dirty(self) -> bool:
        return self.buffer_manager.dirty

    @property
    def current_line(self) -> int:
        return self.navigation_manager.get_current_line()

    @property
    def display_start(self) -> int:
        return self.navigation_manager.display_start

    @property
    def selection_start(self) -> Optional[int]:
        return self.selection_manager.selection_start

    @property
    def selection_end(self) -> Optional[int]:
        return self.selection_manager.selection_end

    @property
    def in_selection_mode(self) -> bool:
        return self.selection_manager.in_selection_mode
