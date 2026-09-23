# ----------------------------------------------------------------
# PyLine 1.2 - Text Buffer (GPLv3)
# Copyright (C) 2025-2026 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# Feel free to distribute and modify.
# ----------------------------------------------------------------

import json
import readline
import sys

from pathlib import Path
from typing import Any, List, Optional, Union

import utils
from auto_save_manager import AutoSaveManager
from backup_mode import BackupMode
from buffer_manager import BufferManager
from config import config_manager
from edit_commands import (
    DeleteLineCommand,
    InsertLineCommand,
    LineEditCommand,
    MultiDeleteCommand,
    MultiLineEditCommand,
    MultiPasteInsertCommand,
    MultiPasteOverwriteCommand,
)
from hook_manager import HookManager
from hook_utils import HookUtils
from navigation_manager import NavigationManager
from paste_buffer import PasteBuffer
from selection_manager import SelectionManager
from status_manager import status_manager
from syntax_highlighter import SyntaxHighlighter
from text_lib import TextLib
from undo_manager import UndoManager

class TextBuffer:
    """Coordinator class with comprehensive hook integration."""

    def __init__(self) -> None:
        # Initialize hook system with config integration
        self.hook_manager = HookManager(config_manager=config_manager)
        self.hook_utils = HookUtils(self.hook_manager)

        # Initialize managers with hook integration
        self.buffer_manager = BufferManager(self.hook_utils)
        self.undo_manager = UndoManager()
        self.selection_manager = SelectionManager(self.hook_utils)
        self.navigation_manager = NavigationManager(self.hook_utils)

        # Auto-save manager
        self.auto_save_manager = AutoSaveManager(self.hook_utils)

        # Register status manager refresh callback so the status bar can
        # trigger a redraw when messages appear/disappear.
        status_manager.set_refresh_callback(self._refresh_display)

        # Search state
        self.current_search = ""
        self.search_results: List[Any] = []

        # Other dependencies
        self.paste_buffer = PasteBuffer()
        self.syntax_highlighter = SyntaxHighlighter()
        self.syntax_highlighting = TextLib.init_color_support()

        # Backup mode (lazy-initialized)
        self._backup_mode: Optional[BackupMode] = None

        # Session hooks
        self._execute_session_hooks("session_start")

    # ------------------------------------------------------------------ #
    # Status / refresh helpers
    # ------------------------------------------------------------------ #
    def _refresh_display(self) -> None:
        """Callback used by StatusManager to redraw the editor."""
        try:
            self.display()
        except Exception:
            # Never let a status refresh break the editor
            pass

    # ------------------------------------------------------------------ #
    # Backup mode
    # ------------------------------------------------------------------ #
    @property
    def backup_mode(self) -> "BackupMode":
        """Lazy-initialize BackupMode (avoids circular import at module load)."""
        if not hasattr(self, "_backup_mode") or self._backup_mode is None:
            self._backup_mode = BackupMode(self)
        return self._backup_mode

    def open_backup_mode(self) -> None:
        """Enter the backup manager UI (uses auto_save_manager under the hood)."""
        # Make sure autosave is running so there's something to browse
        self._start_autosave_for_current_file()
        self.backup_mode.show_backup_menu()
        # Redraw the editor after we come back
        self.display()

    # ------------------------------------------------------------------ #
    # Auto-save / backup helpers
    # ------------------------------------------------------------------ #
    def _start_autosave_for_current_file(self) -> None:
        """Start auto-save for the currently loaded file."""
        if self.buffer_manager.filename:
            self.auto_save_manager.start_autosave(self.buffer_manager, self.buffer_manager.filename)

    def set_filename(self, name: str) -> None:
        """Set the buffer filename and (re)start auto-save."""
        self.buffer_manager.filename = name
        self._start_autosave_for_current_file()

    def get_available_backups(self) -> List[Path]:
        """Get list of available backup files for the current file (newest first)."""
        if not self.buffer_manager.filename:
            return []
        return self.auto_save_manager.get_backup_files(self.buffer_manager.filename)

    def restore_from_backup(self, backup_filename: str) -> bool:
        """Restore buffer content from a backup file."""
        return self.auto_save_manager.restore_from_backup(backup_filename, self.buffer_manager)

    # ------------------------------------------------------------------ #
    # Session hooks
    # ------------------------------------------------------------------ #
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
        try:
            self.auto_save_manager.stop_autosave()
            self._execute_session_hooks("session_end")
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # File operations
    # ------------------------------------------------------------------ #
    def load_file(self, filename: str) -> bool:
        """Load file contents into buffer and (re)start auto-save."""
        # Stop any existing autosave before loading a new file
        self.auto_save_manager.stop_autosave()

        success = self.buffer_manager.load_file(filename)

        if success:
            self._start_autosave_for_current_file()
            status_manager.show_message(f"Loaded: {Path(filename).name}")

        return success

    def save(self) -> bool:
        """Save buffer contents to file."""
        success = self.buffer_manager.save()
        if success:
            status_manager.show_message(f"File saved: {Path(self.buffer_manager.filename or '').name}")
            # Restart autosave for the current file
            self._start_autosave_for_current_file()
        else:
            status_manager.show_message("Save failed!")
        return success

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def navigate(self, direction: str) -> None:
        """Move cursor up/down with viewport adjustment."""
        filename_str = self.buffer_manager.filename or ""
        self.navigation_manager.navigate(direction, self.buffer_manager.get_line_count(), filename_str)

    def jump_to_line(self) -> bool:
        """Jump to a specific line number with readline support."""
        if self.buffer_manager.get_line_count() == 0:
            status_manager.show_message("Buffer is empty")
            return False

        current_line = self.navigation_manager.get_current_line()
        total_lines = self.buffer_manager.get_line_count()

        # Skip history for jump input
        utils.history_manager.skip_next_add()

        readline.set_startup_hook(lambda: readline.insert_text(str(current_line + 1)))
        try:
            print()
            line_input = input(f"Jump to line (1-{total_lines}): ")

            if not line_input:
                status_manager.show_message("Jump cancelled")
                return False

            target_line = int(line_input) - 1

            if target_line < 0 or target_line >= total_lines:
                status_manager.show_message(f"Invalid line number. Must be between 1 and {total_lines}")
                return False

            filename_str = self.buffer_manager.filename or ""
            success = self.navigation_manager.jump_to_line(target_line, total_lines, filename_str)

            if success:
                status_manager.show_message(f"Jumped to line {target_line + 1}")
            else:
                status_manager.show_message("Jump cancelled by hooks")

            return success

        except ValueError:
            status_manager.show_message("Invalid input - please enter a number")
            return False

        finally:
            readline.set_startup_hook(None)

    def jump_to_beginning(self) -> None:
        """Jump to beginning of buffer."""
        filename_str = self.buffer_manager.filename or ""
        self.navigation_manager.jump_to_beginning(self.buffer_manager.get_line_count(), filename_str)

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

    # ------------------------------------------------------------------ #
    # Undo / redo
    # ------------------------------------------------------------------ #
    def push_undo_command(self, command: Any) -> None:
        """Record a command for potential undo."""
        self.undo_manager.push_command(command)

    def undo(self) -> None:
        """Undo the last operation."""
        command = self.undo_manager.undo()
        if command:
            command.undo(self.buffer_manager)
            self.buffer_manager.dirty = True
            status_manager.show_message("Undo completed")
        else:
            status_manager.show_message("Nothing to undo")
        self.display()

    def redo(self) -> None:
        """Redo the last undone operation."""
        command = self.undo_manager.redo()
        if command:
            command.execute(self.buffer_manager)
            self.buffer_manager.dirty = True
            status_manager.show_message("Redo completed")
        else:
            status_manager.show_message("Nothing to redo")
        self.display()

    # ------------------------------------------------------------------ #
    # Editing operations
    # ------------------------------------------------------------------ #
    def edit_current_line(self) -> None:
        """Edit the current line using hook-based input system."""
        current_line = self.navigation_manager.get_current_line()

        if self.buffer_manager.get_line_count() == 0:
            self.buffer_manager.lines = [""]
            self.navigation_manager.set_current_line(0, self.buffer_manager.get_line_count())
            self.buffer_manager.dirty = True

        old_text = self.buffer_manager.get_line(current_line)

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

        new_text = self.hook_utils.execute_edit_line(context)

        # Handle JSON wrapper from hooks
        if isinstance(new_text, dict):
            if new_text.get("success") and isinstance(new_text.get("output"), str):
                new_text = new_text["output"]
            else:
                new_text = None
        elif not isinstance(new_text, str):
            new_text = None

        # Fallback to standard readline
        if new_text is None:
            new_text = TextLib.edit_line(current_line + 1, old_text)

        if new_text is not None:
            new_text = new_text.rstrip("\n\r")

            if old_text.endswith("\n"):
                new_text = new_text + "\n"

            post_edit_context = {
                "line_number": current_line + 1,
                "old_text": old_text,
                "new_text": new_text,
                "filename": self.buffer_manager.filename,
                "buffer_lines": self.buffer_manager.lines,
                "current_line_index": current_line,
                "action": "post_edit",
                "operation": "line_edit",
            }

            post_edit_result = self.hook_utils.execute_post_line_edit(post_edit_context)

            final_text = new_text
            if post_edit_result and isinstance(post_edit_result, dict) and "new_text" in post_edit_result:
                final_text = post_edit_result["new_text"]

            if final_text != old_text:
                cmd = LineEditCommand(current_line, old_text, final_text)
                self.push_undo_command(cmd)
                cmd.execute(self.buffer_manager)
                self.buffer_manager.dirty = True

        self.display()

    def insert_line(self) -> None:
        """Insert a new line after current position."""
        current_line = self.navigation_manager.get_current_line()

        inserted_text = self.buffer_manager.insert_line(current_line + 1, "")

        if inserted_text is not None:
            cmd: Union[InsertLineCommand, LineEditCommand] = InsertLineCommand(current_line + 1, inserted_text)
            self.push_undo_command(cmd)
            self.navigation_manager.set_current_line(current_line + 1, self.buffer_manager.get_line_count())

    def delete_current_line(self) -> bool:
        """Delete current single line."""
        current_line = self.navigation_manager.get_current_line()
        line_count_before = self.buffer_manager.get_line_count()

        if line_count_before == 0 or current_line >= line_count_before:
            return False

        deleted_text = self.buffer_manager.delete_line(current_line)

        if deleted_text:
            cmd = DeleteLineCommand(current_line, deleted_text)
            self.push_undo_command(cmd)

            line_count_after = self.buffer_manager.get_line_count()

            if current_line == line_count_before - 1:
                if line_count_after > 0:
                    new_position = line_count_after - 1
                    self.navigation_manager.set_current_line(new_position, line_count_after)
                    self.navigation_manager.display_start = max(
                        0, line_count_after - self.navigation_manager.display_lines
                    )
                else:
                    self.navigation_manager.set_current_line(0, 0)
                    self.navigation_manager.display_start = 0
            else:
                self.navigation_manager.set_current_line(current_line, line_count_after)

            self.display()
            return True
        return False

    # ------------------------------------------------------------------ #
    # Selection
    # ------------------------------------------------------------------ #
    def start_selection(self) -> None:
        """Begin line selection at current position."""
        current_line = self.navigation_manager.get_current_line()
        filename_str = self.buffer_manager.filename or ""
        self.selection_manager.start_selection(current_line, filename_str)
        status_manager.show_message(f"Selection started at line {current_line + 1}")

    def end_selection(self) -> None:
        """End selection at current position."""
        if not self.selection_manager.in_selection_mode:
            status_manager.show_message("No selection started - use 's' first")
            return

        current_line = self.navigation_manager.get_current_line()
        filename_str = self.buffer_manager.filename or ""
        self.selection_manager.end_selection(current_line, filename_str)

        if self.selection_manager.has_selection():
            start, end = self.selection_manager.get_selection_range()
            if start is not None and end is not None:
                status_manager.show_message(f"Selected lines {start + 1}-{end + 1}")
        else:
            status_manager.show_message("Selection cleared")

    def clear_selection(self) -> None:
        """Clear current selection."""
        self.selection_manager.clear_selection()
        current_line = self.navigation_manager.get_current_line()
        self.navigation_manager.set_current_line(current_line, self.buffer_manager.get_line_count())

    # ------------------------------------------------------------------ #
    # Clipboard
    # ------------------------------------------------------------------ #
    def copy_line(self) -> bool:
        """Copy current single line to clipboard."""
        if self.buffer_manager.get_line_count() == 0:
            status_manager.show_message("Buffer is empty")
            return False

        current_line = self.navigation_manager.get_current_line()
        if not self.buffer_manager.lines or current_line >= len(self.buffer_manager.lines):
            status_manager.show_message("Invalid line")
            return False
        line_text = self.buffer_manager.get_line(current_line)

        if not line_text or line_text.strip() == "":
            status_manager.show_message("Line is empty - nothing to copy")
            return False

        filename_str = self.buffer_manager.filename or ""
        text_to_copy = self.selection_manager.get_selected_text([line_text], filename_str)

        if not text_to_copy or text_to_copy.strip() == "" or not isinstance(text_to_copy, str):
            text_to_copy = line_text

        if self.paste_buffer.copy_to_clipboard(text_to_copy):
            status_manager.show_message("Copied line to clipboard")
            return True

        status_manager.show_message("Failed to copy to clipboard")
        return False

    def copy_selection(self) -> bool:
        """Copy selected lines to clipboard."""
        if not self.selection_manager.has_selection():
            status_manager.show_message("No selection to copy")
            return False

        if not self.buffer_manager.lines:
            status_manager.show_message("Buffer is empty")
            return False

        filename_str = self.buffer_manager.filename or ""
        selected_text = self.selection_manager.get_selected_text(self.buffer_manager.lines, filename_str)

        if selected_text is None or not isinstance(selected_text, str):
            status_manager.show_message("No valid text to copy")
            return False

        if self.paste_buffer.copy_to_clipboard(selected_text):
            start, end = self.selection_manager.get_selection_range()
            if start is not None and end is not None:
                status_manager.show_message(f"Copied {end - start + 1} lines to clipboard")
            self.clear_selection()
            return True

        return False

    def paste_line(self, mode: str = "insert") -> bool:
        """Paste clipboard content - handles both single and multi-line with atomic undo."""
        if not self.paste_buffer.load_from_clipboard():
            status_manager.show_message("Clipboard empty - copy something first")
            return False

        current_line = self.navigation_manager.get_current_line()

        if (
            self.paste_buffer.buffer is None
            or not isinstance(self.paste_buffer.buffer, list)
            or len(self.paste_buffer.buffer) == 0
        ):
            status_manager.show_message("Clipboard empty - copy something first")
            return False

        paste_buffer_content = self.paste_buffer.buffer

        paste_context = {
            "text": paste_buffer_content[0] if paste_buffer_content else "",
            "mode": mode,
            "line_number": current_line,
            "filename": self.buffer_manager.filename,
            "action": "pre_paste",
            "operation": "clipboard",
        }
        paste_result = self.hook_utils.execute_pre_paste(paste_context)

        if paste_result and "text" in paste_result and len(paste_buffer_content) == 1:
            paste_buffer_content = [paste_result["text"]]
        elif paste_result and "lines" in paste_result and isinstance(paste_result["lines"], list):
            paste_buffer_content = paste_result["lines"]

        if len(paste_buffer_content) == 1:
            text_to_paste = paste_buffer_content[0]

            if mode == "insert":
                inserted_text = self.buffer_manager.insert_line(current_line + 1, text_to_paste)
                if inserted_text is not None:
                    cmd = InsertLineCommand(current_line + 1, inserted_text)
                    self.push_undo_command(cmd)
                    cmd.execute(self.buffer_manager)
                    self.navigation_manager.set_current_line(current_line + 1, self.buffer_manager.get_line_count())
            else:
                if current_line >= self.buffer_manager.get_line_count():
                    old_lines = self.buffer_manager.lines.copy()
                    self.buffer_manager.lines.append(text_to_paste)
                    cmd = MultiLineEditCommand(old_lines, self.buffer_manager.lines.copy())  # type: ignore
                    self.push_undo_command(cmd)
                else:
                    old_text = self.buffer_manager.get_line(current_line)
                    new_text = self.buffer_manager.set_line(current_line, text_to_paste)
                    if new_text != old_text:
                        cmd = LineEditCommand(current_line, old_text, new_text)  # type: ignore
                        self.push_undo_command(cmd)
                        cmd.execute(self.buffer_manager)

        else:
            if mode == "insert":
                cmd = MultiPasteInsertCommand(current_line, paste_buffer_content)  # type: ignore
                self.push_undo_command(cmd)
                cmd.execute(self.buffer_manager)
            else:
                changes = []
                lines_to_append = []

                for i, line_text in enumerate(paste_buffer_content):
                    line_num = current_line + i
                    if line_num < self.buffer_manager.get_line_count():
                        old_text = self.buffer_manager.get_line(line_num)
                        changes.append((line_num, old_text, line_text))
                    else:
                        lines_to_append.append(line_text)

                if changes:
                    cmd = MultiPasteOverwriteCommand(changes)  # type: ignore
                    self.push_undo_command(cmd)
                    cmd.execute(self.buffer_manager)

                if lines_to_append:
                    old_lines = self.buffer_manager.lines.copy()
                    self.buffer_manager.lines.extend(lines_to_append)
                    append_cmd = MultiLineEditCommand(old_lines, self.buffer_manager.lines.copy())
                    self.push_undo_command(append_cmd)

                status_manager.show_message(f"Overwriting with {len(paste_buffer_content)} lines")

        self.buffer_manager.dirty = True
        self.display()
        return True

    def delete_selected_lines(self) -> bool:
        """Delete all lines in the current selection range as one atomic operation."""
        if not self.selection_manager.has_selection():
            status_manager.show_message("No selection to delete")
            return False

        start, end = self.selection_manager.get_selection_range()
        if start is None or end is None:
            status_manager.show_message("Invalid selection range")
            return False

        if not self.buffer_manager.lines:
            status_manager.show_message("Buffer is empty")
            return False

        current_line_before = self.navigation_manager.get_current_line()

        deleted_lines = []
        for line_num in range(end, start - 1, -1):
            if line_num < self.buffer_manager.get_line_count():
                line_text = self.buffer_manager.get_line(line_num)
                deleted_lines.append((line_num, line_text))

        if deleted_lines:
            self.selection_manager.clear_selection()

            cmd = MultiDeleteCommand(deleted_lines)
            cmd.execute(self.buffer_manager)
            self.push_undo_command(cmd)

            self.buffer_manager.dirty = True

            line_count_after = self.buffer_manager.get_line_count()

            if start <= current_line_before <= end:
                if start > 0:
                    new_position = start - 1
                    self.navigation_manager.set_current_line(new_position, line_count_after)
                    self.navigation_manager.display_start = max(
                        0, new_position - self.navigation_manager.display_lines + 1
                    )
                else:
                    self.navigation_manager.set_current_line(0, line_count_after)
                    self.navigation_manager.display_start = 0
            elif current_line_before > end:
                lines_deleted = end - start + 1
                new_position = current_line_before - lines_deleted
                self.navigation_manager.set_current_line(new_position, line_count_after)
                self.navigation_manager.ensure_line_visible(new_position, line_count_after)
            else:
                self.navigation_manager.set_current_line(current_line_before, line_count_after)
                self.navigation_manager.ensure_line_visible(current_line_before, line_count_after)

            status_manager.show_message(f"Deleted {end - start + 1} lines")
            self.display()
            return True
        return False

    # ------------------------------------------------------------------ #
    # Search / replace
    # ------------------------------------------------------------------ #
    def start_incremental_search(self) -> None:
        """Start incremental search mode."""
        search = self.current_search

        readline.set_startup_hook(lambda: readline.insert_text(search))
        try:
            print()
            search_input = input("Search for: ")
        finally:
            readline.set_startup_hook(None)

        if search_input is not None:
            self.current_search = search_input
            self.execute_search_hook(self.current_search, None)

    def start_replace_mode(self) -> None:
        """Start search and replace mode."""
        search = self.current_search

        if not search:
            readline.set_startup_hook(lambda: readline.insert_text(""))
            try:
                print()
                search_input = input("Search for: ")
            finally:
                readline.set_startup_hook(None)

            if not search_input:
                return
            search = search_input
            self.current_search = search_input

        readline.set_startup_hook(lambda: readline.insert_text(""))
        try:
            print()
            replace_input = input(f"Replace '{search}' with: ")
        finally:
            readline.set_startup_hook(None)

        if replace_input is not None:
            self.execute_search_hook(search, replace_input)

    def execute_search_hook(self, search: str, replace: Optional[str] = None) -> None:
        """Execute the search/replace hook and wait for key press."""
        context = {
            "search": search,
            "replace": replace,
            "lines": self.buffer_manager.lines,
            "filename": self.buffer_manager.filename,
            "action": "search_replace",
            "operation": "editing",
        }

        if replace is None:
            utils.clear_screen()
            display_handled = self.hook_utils.execute_and_display("event_handlers", "search_replace", context)
            if display_handled:
                utils.prompt_continue_woc()
            else:
                status_manager.show_message(f"No matches found for: {search}")
        else:
            hook_response = self.hook_manager.execute_hooks("event_handlers", "search_replace", context)

            hook_result = None

            if hook_response is not None:
                if isinstance(hook_response, dict) and hook_response.get("success") and "output" in hook_response:
                    try:
                        hook_result = json.loads(hook_response["output"])
                    except (json.JSONDecodeError, KeyError):
                        hook_result = None
                else:
                    hook_result = hook_response

            if hook_result and isinstance(hook_result, dict) and hook_result.get("handled_output") == 1:
                if "content" in hook_result:
                    old_lines = self.buffer_manager.lines.copy()
                    self.buffer_manager.lines = hook_result["content"]
                    self.buffer_manager.dirty = True

                    cmd = MultiLineEditCommand(old_lines, hook_result["content"])
                    self.push_undo_command(cmd)

                    if "message" in hook_result:
                        status_manager.show_message(hook_result["message"])
                    else:
                        matches = hook_result.get("matches", 0)
                        replaced = hook_result.get("replaced", 0)
                        status_manager.show_message(f"Replaced {replaced} out of {matches} matches")

                    self.display()
                    return

                status_manager.show_message(f"Replace operation completed for: {search}")
                self.display()

    def check_grammar(self) -> None:
        """Manually trigger grammar check on current buffer."""
        if not self.buffer_manager.lines:
            status_manager.show_message("Buffer is empty - nothing to check")
            return

        grammar_context = {
            "action": "process_content",
            "content": self.buffer_manager.lines,
            "filename": self.buffer_manager.filename,
            "operation": "manual_grammar_check",
        }

        result = self.hook_utils.execute_editing_handlers("process_content", grammar_context)

        if result is None:
            status_manager.show_message(
                "No grammar checker hook found - install hook in ~/.pyline/hooks/editing_ops/"
            )
            self.display()
            return

        if not isinstance(result, dict):
            status_manager.show_message("Grammar checker returned invalid response")
            self.display()
            return

        if result.get("handled_output") == 1:
            output = result.get("output", "")
            if output:
                utils.clear_screen()
                print(output)
                utils.prompt_continue_woc()
                self.display()
            else:
                status_manager.show_message("Grammar checker ran but produced no output")
                self.display()
        else:
            error_msg = result.get("error", "")
            if error_msg:
                status_manager.show_message(f"Grammar checker error: {error_msg}")
                self.display()
            else:
                status_manager.show_message("Grammar checker found no issues in your text")
                self.display()

    # ------------------------------------------------------------------ #
    # Display
    # ------------------------------------------------------------------ #
    def display(self) -> None:
        """Render current buffer state using TextLib."""
        line_count = self.buffer_manager.get_line_count()
        current_line = self.navigation_manager.get_current_line()

        if line_count == 0:
            self.navigation_manager.set_current_line(0, 0)
            self.navigation_manager.display_start = 0
        elif current_line >= line_count:
            self.navigation_manager.set_current_line(line_count - 1, line_count)

        display_context = {
            "filename": self.buffer_manager.filename,
            "line_count": line_count,
            "current_line": self.navigation_manager.get_current_line(),
            "action": "pre_display",
            "operation": "rendering",
        }
        self.hook_utils.execute_pre_edit(display_context)

        # Pull the current status message so TextLib can render it
        # as an integrated status bar line (not a tacked-on line).
        status_bar_text = status_manager.get_status_bar()

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
            status_bar=status_bar_text,
        )

        post_display_context = {
            "filename": self.buffer_manager.filename,
            "line_count": line_count,
            "current_line": self.navigation_manager.get_current_line(),
            "action": "post_display",
            "operation": "rendering",
        }
        self.hook_utils.execute_post_edit(post_display_context)

    # ------------------------------------------------------------------ #
    # Interactive editing
    # ------------------------------------------------------------------ #
    def edit_interactive(self) -> Optional[bool]:
        """Main editing interface."""
        try:
            while True:
                self.display()
                sys.stdout.write(
                    "Command [↑↓, PgUp/PgDn, Home/End, J(ump), E(dit), I(nsert), D(el), S(elect), H(elp), G(ramar),"
                    " B(ackups), C(opy), V(paste), O(verwrite), W(rite), Q(uit)]: "
                )
                sys.stdout.flush()

                # ---- Render lock while reading a key in raw mode ----
                status_manager.acquire_render_lock()
                try:
                    cmd = TextLib.get_key_input()
                finally:
                    status_manager.release_render_lock()
                # -----------------------------------------------------

                if not cmd:
                    continue

                if cmd == "\x1b[A":
                    self.navigate("up")
                elif cmd == "\x1b[B":
                    self.navigate("down")
                elif cmd == "\x1b[5~":
                    self.page_up()
                elif cmd == "\x1b[6~":
                    self.page_down()
                elif cmd == "\x1b[H":
                    self.jump_to_beginning()
                elif cmd in ("\x04", "\x1b[F"):
                    self.jump_to_end()

                elif cmd in ("", "e", "\r", "\n"):
                    self.edit_current_line()
                elif cmd == "b":
                    self.open_backup_mode()
                elif cmd == "g":
                    self.check_grammar()
                elif cmd == "h":
                    utils.show_help()
                elif cmd == "i":
                    self.insert_line()
                elif cmd == "j":
                    self.jump_to_line()
                elif cmd == "d":
                    if self.selection_manager.has_selection():
                        self.delete_selected_lines()
                    else:
                        self.delete_current_line()
                elif cmd == "s":
                    if not self.selection_manager.in_selection_mode:
                        self.start_selection()
                    else:
                        self.end_selection()
                elif cmd == "c":
                    if self.selection_manager.has_selection():
                        self.copy_selection()
                    else:
                        self.copy_line()
                elif cmd == "v":
                    self.paste_line(mode="insert")
                elif cmd == "o":
                    self.paste_line(mode="overwrite")
                elif cmd == "undo":
                    self.undo()
                elif cmd == "redo":
                    self.redo()
                elif cmd == "\x1b\x06":
                    self.start_incremental_search()
                elif cmd == "\x1b\x12":
                    self.start_replace_mode()
                elif cmd == "w":
                    if self.save():
                        self.display()
                        continue
                    else:
                        status_manager.show_message("Save failed!")
                        self.display()
                elif cmd == "q" or cmd == "\x1b":
                    return self._handle_quit()
                else:
                    status_manager.show_message(
                        "Invalid key. Use: ↑↓ PgUp PgDn Home End E Enter I C D O Q S W B"
                    )

        finally:
            self._execute_session_hooks("session_end")

    def _handle_quit(self) -> Optional[bool]:
        """Handle quit command with save prompt."""
        if not self.buffer_manager.dirty:
            self.auto_save_manager.stop_autosave()
            utils.history_manager._clear_editing_history()
            return None

        while True:
            choice = input("\nSave changes? (y/n): ").lower()
            if choice == "y":
                if self.save():
                    self.auto_save_manager.stop_autosave()
                    utils.history_manager._clear_editing_history()
                    return True

                status_manager.show_message("Error saving file!")
                break

            elif choice == "n":
                self.auto_save_manager.stop_autosave()
                utils.history_manager._clear_editing_history()
                return False

            else:
                status_manager.show_message("Only Y/N!")
        return None

    # ------------------------------------------------------------------ #
    # Property accessors for compatibility
    # ------------------------------------------------------------------ #
    @property
    def lines(self) -> List[str]:
        return self.buffer_manager.lines

    @property
    def filename(self) -> Optional[str]:
        return self.buffer_manager.filename

    @filename.setter
    def filename(self, value: str) -> None:
        self.buffer_manager.filename = value
        self._start_autosave_for_current_file()

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
