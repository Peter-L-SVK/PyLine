#----------------------------------------------------------------
# PyLine 0.5 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

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
