# ----------------------------------------------------------------
# PyLine 0.9.8 - Line editor (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

from typing import List, Tuple, Any


class EditCommand:
    """Base class for all editable commands."""

    def execute(self, buffer_manager: Any) -> None:
        raise NotImplementedError

    def undo(self, buffer_manager: Any) -> None:
        raise NotImplementedError


class LineEditCommand(EditCommand):
    """Tracks changes to a single line."""

    def __init__(self, line_num: int, old_text: str, new_text: str) -> None:
        self.line_num = line_num
        self.old_text = old_text
        self.new_text = new_text

    def execute(self, buffer_manager: Any) -> None:
        if self.line_num < len(buffer_manager.lines):
            buffer_manager.lines[self.line_num] = self.new_text

    def undo(self, buffer_manager: Any) -> None:
        if self.line_num < len(buffer_manager.lines):
            buffer_manager.lines[self.line_num] = self.old_text


class InsertLineCommand(EditCommand):
    """Tracks line insertion."""

    def __init__(self, line_num: int, text: str) -> None:
        self.line_num = line_num
        self.text = text  # Store the actual content

    def execute(self, buffer_manager: Any) -> None:
        buffer_manager.lines.insert(self.line_num, self.text)  # Insert with content

    def undo(self, buffer_manager: Any) -> None:
        if self.line_num < len(buffer_manager.lines):
            del buffer_manager.lines[self.line_num]


class DeleteLineCommand(EditCommand):
    """Tracks line deletion."""

    def __init__(self, line_num: int, text: str) -> None:
        self.line_num = line_num
        self.text = text

    def execute(self, buffer_manager: Any) -> None:
        if self.line_num < len(buffer_manager.lines):
            del buffer_manager.lines[self.line_num]

    def undo(self, buffer_manager: Any) -> None:
        buffer_manager.lines.insert(self.line_num, self.text)


class MultiPasteInsertCommand(EditCommand):
    """Atomic operation for inserting multiple lines"""

    def __init__(self, at_line: int, lines: List[str]) -> None:
        self.at_line = at_line  # Insertion point
        self.lines = lines  # List of lines to insert

    def execute(self, buffer_manager: Any) -> None:
        # Insert in reverse order to maintain correct line numbers
        for line in reversed(self.lines):
            buffer_manager.lines.insert(self.at_line, line)

    def undo(self, buffer_manager: Any) -> None:
        # Remove all inserted lines
        for _ in range(len(self.lines)):
            if self.at_line < len(buffer_manager.lines):
                del buffer_manager.lines[self.at_line]


class MultiPasteOverwriteCommand(EditCommand):
    """Atomic operation for overwriting multiple lines"""

    def __init__(self, changes: List[Tuple[int, str, str]]) -> None:
        # changes: List of (line_num, old_text, new_text)
        self.changes = changes

    def execute(self, buffer_manager: Any) -> None:
        for line_num, _, new_text in self.changes:
            if line_num < len(buffer_manager.lines):
                buffer_manager.lines[line_num] = new_text

    def undo(self, buffer_manager: Any) -> None:
        for line_num, old_text, _ in self.changes:
            if line_num < len(buffer_manager.lines):
                buffer_manager.lines[line_num] = old_text


class MultiDeleteCommand(EditCommand):
    """Handles deletion of multiple lines as one atomic operation"""

    def __init__(self, lines: List[Tuple[int, str]]) -> None:
        # lines: List of (line_num, text) tuples in reverse order
        self.lines = lines

    def execute(self, buffer_manager: Any) -> None:
        # Delete lines in reverse-sorted order to maintain correct indices
        for line_num, _ in sorted(self.lines, reverse=True, key=lambda x: x[0]):
            if line_num < len(buffer_manager.lines):
                del buffer_manager.lines[line_num]

    def undo(self, buffer_manager: Any) -> None:
        # Re-insert lines in original order
        for line_num, text in sorted(self.lines, key=lambda x: x[0]):
            buffer_manager.lines.insert(line_num, text)
