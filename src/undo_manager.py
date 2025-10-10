# ----------------------------------------------------------------
# PyLine 1.1 - Undo Manager (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

from typing import Deque, Optional
from collections import deque
from edit_commands import EditCommand


class UndoManager:
    """Manages undo/redo functionality."""

    def __init__(self, max_history: int = 120):
        self.undo_stack: Deque[EditCommand] = deque(maxlen=max_history)
        self.redo_stack: Deque[EditCommand] = deque(maxlen=max_history)

    def push_command(self, command: EditCommand) -> None:
        """Record a command for potential undo."""
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def undo(self) -> Optional[EditCommand]:
        """Undo the last operation."""
        if not self.undo_stack:
            return None
        command = self.undo_stack.pop()
        self.redo_stack.append(command)
        return command

    def redo(self) -> Optional[EditCommand]:
        """Redo the last undone operation."""
        if not self.redo_stack:
            return None
        command = self.redo_stack.pop()
        self.undo_stack.append(command)
        return command

    def clear(self) -> None:
        """Clear all history."""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return len(self.redo_stack) > 0
