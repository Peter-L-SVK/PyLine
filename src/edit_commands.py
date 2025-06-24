#----------------------------------------------------------------
# PyLine 0.6 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

class EditCommand:
    """Base class for all editable commands."""
    def execute(self, buffer):
         raise NotImplementedError

    def undo(self, buffer):
         raise NotImplementedError

class LineEditCommand(EditCommand):
    """Tracks changes to a single line."""
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
    """Tracks line insertion."""
    def __init__(self, line_num, text):
        self.line_num = line_num
        self.text = text  # Store the actual content

    def execute(self, buffer):
        buffer.lines.insert(self.line_num, self.text)  # Insert with content

    def undo(self, buffer):
        if self.line_num < len(buffer.lines):
            del buffer.lines[self.line_num]

class DeleteLineCommand(EditCommand):
    """Tracks line deletion."""
    def __init__(self, line_num, text):
        self.line_num = line_num
        self.text = text

    def execute(self, buffer):
        if self.line_num < len(buffer.lines):
            del buffer.lines[self.line_num]

    def undo(self, buffer):
        buffer.lines.insert(self.line_num, self.text)
            
class MultiPasteInsertCommand(EditCommand):
    """Atomic operation for inserting multiple lines"""
    def __init__(self, at_line, lines):
        self.at_line = at_line  # Insertion point
        self.lines = lines      # List of lines to insert

    def execute(self, buffer):
        # Insert in reverse order to maintain correct line numbers
        for line in reversed(self.lines):
            buffer.lines.insert(self.at_line, line)

    def undo(self, buffer):
        # Remove all inserted lines
        for _ in range(len(self.lines)):
            if self.at_line < len(buffer.lines):
                del buffer.lines[self.at_line]

class MultiPasteOverwriteCommand(EditCommand):
    """Atomic operation for overwriting multiple lines""" 
    def __init__(self, changes):
        # changes: List of (line_num, old_text, new_text)
        self.changes = changes  

    def execute(self, buffer):
        for line_num, _, new_text in self.changes:
            if line_num < len(buffer.lines):
                buffer.lines[line_num] = new_text

    def undo(self, buffer):
        for line_num, old_text, _ in self.changes:
            if line_num < len(buffer.lines):
                buffer.lines[line_num] = old_text
                
class MultiDeleteCommand(EditCommand):
    """Handles deletion of multiple lines as one atomic operation"""
    def __init__(self, lines):
        # lines: List of (line_num, text) tuples in reverse order
        self.lines = lines  

    def execute(self, buffer):
        # Delete lines in reverse-sorted order to maintain correct indices
        for line_num, _ in sorted(self.lines, reverse=True, key=lambda x: x[0]):
            if line_num < len(buffer.lines):
                del buffer.lines[line_num]

    def undo(self, buffer):
        # Re-insert lines in original order
        for line_num, text in sorted(self.lines, key=lambda x: x[0]):
            buffer.lines.insert(line_num, text)
