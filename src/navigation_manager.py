# ----------------------------------------------------------------
# PyLine 1.1 - Navigation Manager (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

from typing import Any, Tuple, Optional
from base_manager import BaseManager


class NavigationManager(BaseManager):
    """Manages cursor navigation and viewport with hook integration."""

    def __init__(self, hook_utils: Any, display_lines: int = 52) -> None:
        super().__init__(hook_utils)
        self.current_line: int = 0
        self.display_start: int = 0
        self.display_lines: int = display_lines

    def navigate(self, direction: str, line_count: int, filename: Optional[str] = None) -> bool:
        """Move cursor with hook integration."""
        # Handle empty buffer
        if line_count == 0:
            return False

        # Pre-navigation hooks
        pre_nav_context = {
            "current_line": self.current_line,
            "direction": direction,
            "filename": filename,
            "action": "pre_navigation",
            "operation": "navigation",
        }
        pre_nav_result = self.hook_utils.execute_session_handlers("pre_navigation", pre_nav_context)

        if pre_nav_result and "cancel" in pre_nav_result:
            return False  # Navigation cancelled

        # Perform navigation
        old_line = self.current_line

        if direction == "up" and self.current_line > 0:
            self.current_line -= 1
        elif direction == "down" and self.current_line < line_count - 1:
            self.current_line += 1

        self._adjust_viewport(line_count)

        # Post-navigation hooks
        post_nav_context = {
            "old_line": old_line,
            "new_line": self.current_line,
            "direction": direction,
            "filename": filename,
            "action": "post_navigation",
            "operation": "navigation",
        }
        self.hook_utils.execute_session_handlers("post_navigation", post_nav_context)

        return True

    def jump_to_line(self, line_number: int, line_count: int, filename: Optional[str] = None) -> bool:
        """Jump to specific line with hook integration."""
        # Handle empty buffer
        if line_count == 0:
            return False

        # Pre-jump hooks
        pre_jump_context = {
            "current_line": self.current_line,
            "target_line": line_number,
            "filename": filename,
            "action": "pre_navigation",
            "operation": "jump",
        }
        pre_jump_result = self.hook_utils.execute_session_handlers("pre_navigation", pre_jump_context)

        if pre_jump_result and "cancel" in pre_jump_result:
            return False  # Jump cancelled

        # Perform jump
        old_line = self.current_line
        self.current_line = max(0, min(line_number, line_count - 1))
        self._adjust_viewport(line_count)

        # Post-jump hooks
        post_jump_context = {
            "old_line": old_line,
            "new_line": self.current_line,
            "filename": filename,
            "action": "post_navigation",
            "operation": "jump",
        }
        self.hook_utils.execute_session_handlers("post_navigation", post_jump_context)

        return True

    def jump_to_beginning(self, line_count: int, filename: Optional[str] = None) -> bool:
        """Jump to beginning of buffer with hook integration."""
        # Handle empty buffer
        if line_count == 0:
            return False

        # Pre-jump hooks
        pre_jump_context = {
            "current_line": self.current_line,
            "target_line": 0,
            "filename": filename,
            "action": "pre_navigation",
            "operation": "jump_beginning",
        }
        pre_jump_result = self.hook_utils.execute_session_handlers("pre_navigation", pre_jump_context)

        if pre_jump_result and "cancel" in pre_jump_result:
            return False  # Jump cancelled

        # Perform jump
        old_line = self.current_line
        self.current_line = 0
        self.display_start = 0

        # Post-jump hooks
        post_jump_context = {
            "old_line": old_line,
            "new_line": self.current_line,
            "filename": filename,
            "action": "post_navigation",
            "operation": "jump_beginning",
        }
        self.hook_utils.execute_session_handlers("post_navigation", post_jump_context)

        return True

    def jump_to_end(self, line_count: int, filename: Optional[str] = None) -> bool:
        """Jump to end of buffer with hook integration."""
        # Handle empty buffer
        if line_count == 0:
            return False

        # Pre-jump hooks
        pre_jump_context = {
            "current_line": self.current_line,
            "target_line": line_count - 1,
            "filename": filename,
            "action": "pre_navigation",
            "operation": "jump_end",
        }
        pre_jump_result = self.hook_utils.execute_session_handlers("pre_navigation", pre_jump_context)

        if pre_jump_result and "cancel" in pre_jump_result:
            return False  # Jump cancelled

        # Perform jump
        old_line = self.current_line
        if line_count > 0:
            self.current_line = line_count - 1
            self.display_start = max(0, line_count - self.display_lines)

        # Post-jump hooks
        post_jump_context = {
            "old_line": old_line,
            "new_line": self.current_line,
            "filename": filename,
            "action": "post_navigation",
            "operation": "jump_end",
        }
        self.hook_utils.execute_session_handlers("post_navigation", post_jump_context)

        return True

    def page_up(self, line_count: int, filename: Optional[str] = None) -> bool:
        """Move page up with hook integration."""
        # Handle empty buffer
        if line_count == 0:
            return False

        # Pre-page hooks
        pre_page_context = {
            "current_line": self.current_line,
            "display_start": self.display_start,
            "filename": filename,
            "action": "pre_navigation",
            "operation": "page_up",
        }
        pre_page_result = self.hook_utils.execute_session_handlers("pre_navigation", pre_page_context)

        if pre_page_result and "cancel" in pre_page_result:
            return False  # Page operation cancelled

        # Perform page up
        old_line = self.current_line
        self.display_start = max(0, self.display_start - self.display_lines)
        self.current_line = max(0, self.current_line - self.display_lines)
        self._adjust_viewport(line_count)

        # Post-page hooks
        post_page_context = {
            "old_line": old_line,
            "new_line": self.current_line,
            "filename": filename,
            "action": "post_navigation",
            "operation": "page_up",
        }
        self.hook_utils.execute_session_handlers("post_navigation", post_page_context)

        return True

    def page_down(self, line_count: int, filename: Optional[str] = None) -> bool:
        """Move page down with hook integration."""
        # Handle empty buffer
        if line_count == 0:
            return False

        # Pre-page hooks
        pre_page_context = {
            "current_line": self.current_line,
            "display_start": self.display_start,
            "filename": filename,
            "action": "pre_navigation",
            "operation": "page_down",
        }
        pre_page_result = self.hook_utils.execute_session_handlers("pre_navigation", pre_page_context)

        if pre_page_result and "cancel" in pre_page_result:
            return False  # Page operation cancelled

        # Perform page down
        old_line = self.current_line
        new_start = min(line_count - self.display_lines, self.display_start + self.display_lines)
        self.display_start = max(0, new_start)
        self.current_line = min(line_count - 1, self.current_line + self.display_lines)
        self._adjust_viewport(line_count)

        # Post-page hooks
        post_page_context = {
            "old_line": old_line,
            "new_line": self.current_line,
            "filename": filename,
            "action": "post_navigation",
            "operation": "page_down",
        }
        self.hook_utils.execute_session_handlers("post_navigation", post_page_context)

        return True

    def _adjust_viewport(self, line_count: int) -> None:
        """Adjust viewport to keep current line visible."""
        if line_count == 0:
            # Handle empty buffer
            self.display_start = 0
            self.current_line = 0
            return

        # Ensure current line is within bounds
        self.current_line = max(0, min(self.current_line, line_count - 1))

        # If current line is above viewport, scroll up
        if self.current_line < self.display_start:
            self.display_start = self.current_line

        # If current line is below viewport, scroll down
        elif self.current_line >= self.display_start + self.display_lines:
            self.display_start = self.current_line - self.display_lines + 1

        # Ensure we don't scroll past the end of the buffer
        max_display_start = max(0, line_count - self.display_lines)
        if self.display_start > max_display_start:
            self.display_start = max_display_start

        # Ensure we don't have negative display start
        self.display_start = max(0, self.display_start)

    def get_viewport_range(self, line_count: int) -> Tuple[int, int]:
        """Get visible lines range."""
        end = min(self.display_start + self.display_lines, line_count)
        return (self.display_start, end)

    def set_current_line(self, line_number: int, line_count: int) -> None:
        """Set current line number."""
        if line_count == 0:
            self.current_line = 0
            self.display_start = 0
        else:
            self.current_line = max(0, min(line_number, line_count - 1))
            self._adjust_viewport(line_count)

    # Add getter method for current_line
    def get_current_line(self) -> int:
        """Get current line number."""
        return self.current_line

    def ensure_line_visible(self, line_number: int, line_count: int) -> None:
        """Ensure a specific line is visible in the viewport."""
        if line_number < self.display_start:
            self.display_start = line_number
        elif line_number >= self.display_start + self.display_lines:
            self.display_start = line_number - self.display_lines + 1
        self._adjust_viewport(line_count)
