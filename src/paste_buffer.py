#----------------------------------------------------------------
# PyLine 0.9 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

# Standard library imports
import os
import re
import subprocess
import sys

# Local application imports
from edit_commands import (
    InsertLineCommand,
    LineEditCommand,
    MultiPasteInsertCommand,
    MultiPasteOverwriteCommand
)

class PasteBuffer:
    def __init__(self):
        self.buffer = []
        self.original_indents = []
        self.common_prefix = ""
        self._lock = False 
        
    def set_text(self, text):
        """Load text into the paste buffer from any source"""
        self.buffer = []  # Clear first

        # Handle empty text case
        if not text.strip():
            self.buffer = [""]
            self._analyze_indentation()
            return
        
        # Normalize line endings and split
        lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        self.buffer = lines
        self._analyze_indentation()
        
    def _analyze_indentation(self):
        """Analyze indentation patterns in the buffer"""
        self.original_indents = []
        for line in self.buffer:
            indent = re.match(r'^(\s*)', line)
            self.original_indents.append(indent.group(1)) if indent else ""
        
        self._calculate_common_prefix()
        
    def _calculate_common_prefix(self):
        """Find the longest common whitespace prefix across non-empty lines"""
        if not self.buffer:
            self.common_prefix = ""
            return
            
        # Get all non-empty lines with actual content
        candidate_lines = [indent for indent in self.original_indents 
                          if indent or any(line.strip() for line in self.buffer)]
        
        if not candidate_lines:
            self.common_prefix = ""
            return
            
        self.common_prefix = candidate_lines[0]
        
        for indent in candidate_lines[1:]:
            if not indent.startswith(self.common_prefix):
                # Find the longest common prefix
                min_len = min(len(self.common_prefix), len(indent))
                new_prefix = ""
                for i in range(min_len):
                    if self.common_prefix[i] == indent[i]:
                        new_prefix += self.common_prefix[i]
                    else:
                        break
                    
                self.common_prefix = new_prefix
                if not self.common_prefix:
                    break

    def get_system_clipboard(self):
        """Universal clipboard getter with X11/Wayland/macOS/Windows support"""
        try:
            # 1. First try Wayland (newer systems)
            if 'WAYLAND_DISPLAY' in os.environ:
                try:
                    result = subprocess.run(
                        ['wl-paste'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        return result.stdout
                    
                except (subprocess.SubprocessError, FileNotFoundError):
                    pass

            
            # 2. Try X11 (traditional Linux/BSD)
            if 'DISPLAY' in os.environ:  # X11 session exists
                try:
                    result = subprocess.run(
                        ['xclip', '-selection', 'clipboard', '-o'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        return result.stdout
                    
                except (subprocess.SubprocessError, FileNotFoundError):
                    pass

            # 3. Try MATE's native clipboard (GTK)
            try:
                import gi
                gi.require_version('Gtk', '3.0')
                from gi.repository import Gtk, Gdk
                clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
                text = clipboard.wait_for_text()
                if text:
                    return text
                
            except (ImportError, AttributeError) as e:
                pass  # Fall through to other methods
                
            # 4. Try macOS (pbpaste)
            if sys.platform == 'darwin':
                try:
                    return subprocess.check_output(
                        ['pbpaste'],
                        text=True,
                        timeout=2
                    )
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
                
            # 5. Try Windows (win32clipboard or WSL)
            if sys.platform == 'win32':
                try:
                    import win32clipboard
                    win32clipboard.OpenClipboard()
                    data = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                    return data
                
                except (ImportError, RuntimeError):
                    # Fallback to win32yank in WSL
                    try:
                        return subprocess.check_output(
                            ['win32yank.exe', '-o'],
                            text=True,
                            timeout=2
                        )
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        pass
                    
        except Exception as e:
            print(f"Clipboard warning: {str(e)}")
        return ""

    def load_from_clipboard(self):
        """Load content from system clipboard"""
        clipboard_text = self.get_system_clipboard()
        if clipboard_text:
            self.set_text(clipboard_text)
            return True
        
        return False

    def paste_into(self, text_buffer, at_line=None, adjust_indent=True):
        """
        Paste content into text buffer with smart indentation handling
        
        Args:
            text_buffer: Target TextBuffer instance
            at_line: Line number to paste at (None for current position)
            adjust_indent: Whether to adjust indentation to target context
        Returns:
            Number of lines pasted
        """
        if not self.buffer and not self.load_from_clipboard():
            return 0

        at_line = at_line or text_buffer.current_line
        adjusted_lines = [
            self._adjust_line_indent(line, self._get_context_indent(text_buffer, at_line))
            for line in self.buffer
        ] if adjust_indent else self.buffer.copy()
        
        cmd = MultiPasteInsertCommand(at_line, adjusted_lines)
        text_buffer.push_undo_command(cmd)
        cmd.execute(text_buffer)
        
        text_buffer.dirty = True
        return len(adjusted_lines)

    def paste_over(self, text_buffer, at_line=None):
        """
        Paste content over existing lines in text buffer, preserving target indentation
        
        Args:
            text_buffer: Target TextBuffer instance
            at_line: Starting line number (None for current position)
        Returns:
            Number of lines affected
        """
        if not self.buffer and not self.load_from_clipboard():
            return 0
        
        at_line = at_line or text_buffer.current_line
        changes = []
        
        for i, line in enumerate(self.buffer):
            target_line = at_line + i
            if target_line >= len(text_buffer.lines):
                break
            
            # Preserve original indentation
            indent = re.match(r'^\s*', text_buffer.lines[target_line]).group()
            old_text = text_buffer.lines[target_line]
            new_text = indent + line.lstrip()
            changes.append((target_line, old_text, new_text))
            
        if changes:
            cmd = MultiPasteOverwriteCommand(changes)
            text_buffer.push_undo_command(cmd)
            cmd.execute(text_buffer)
            text_buffer.dirty = True
            
        return len(changes)

    def _get_context_indent(self, text_buffer, at_line):
        """Determine appropriate indentation for paste location"""
        # Check current line's indentation
        if at_line < len(text_buffer.lines):
            indent_match = re.match(r'^(\s*)', text_buffer.lines[at_line])
            if indent_match:
                return indent_match.group(1)
        
        # Check previous line's indentation if current line doesn't exist
        if at_line > 0 and at_line - 1 < len(text_buffer.lines):
            indent_match = re.match(r'^(\s*)', text_buffer.lines[at_line - 1])
            if indent_match:
                return indent_match.group(1)
                
        return ""

    def _adjust_line_indent(self, line, target_indent):
        """Adjust a line's indentation while preserving relative indentation"""
        if not self.common_prefix:
            return target_indent + line.lstrip()
            
        original_indent = re.match(r'^(\s*)', line).group(1) if re.match(r'^(\s*)', line) else ""
        
        # Calculate relative indentation
        if original_indent.startswith(self.common_prefix):
            extra_indent = original_indent[len(self.common_prefix):]
            return target_indent + extra_indent + line.lstrip()
        else:
            return target_indent + line.lstrip()

    def set_system_clipboard(self, text):
        """Attempt to set text to system clipboard with Wayland/X11/macOS/Windows support."""
        try:
            # Normalize line endings and encode
            text = text.replace('\r\n', '\n').replace('\r', '\n')
            text_bytes = text.encode('utf-8')

            # Detect Wayland first (modern Linux/BSD)
            if os.environ.get('WAYLAND_DISPLAY'):
                try:
                    p = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
                    p.communicate(input=text.encode('utf-8'))
                    return True
                
                except (subprocess.SubprocessError, FileNotFoundError):
                    pass  # Fall through to other methods
                
            # Try X11 (Linux/BSD)
            if sys.platform.startswith(('linux', 'freebsd', 'openbsd')):
                try:
                    p = subprocess.Popen(
                        ['xclip', '-selection', 'clipboard'],
                        stdin=subprocess.PIPE
                    )
                    p.communicate(input=text.encode('utf-8'))
                    return True

                except (subprocess.SubprocessError, FileNotFoundError):
                    pass

            # Try macOS
            if sys.platform == 'darwin':
                try:
                    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                    p.communicate(input=text.encode('utf-8'))
                    return True

                except (subprocess.SubprocessError, FileNotFoundError):
                    pass

             #Try MATE's native clipboard
            try:
                import gi
                gi.require_version('Gtk', '3.0')
                from gi.repository import Gtk, Gdk
                clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
                clipboard.set_text(text, -1)
                clipboard.store()
                return True
            
            except (ImportError, AttributeError):
                pass  # Fall back to other methods
                
            # Try Windows (native or WSL with win32yank)
            if sys.platform == 'win32':
                try:
                    import win32clipboard
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(text)
                    win32clipboard.CloseClipboard()
                    return True

                except (ImportError, RuntimeError):
                    # Fallback to win32yank in WSL
                    try:
                        p = subprocess.Popen(['win32yank.exe', '-i'], stdin=subprocess.PIPE)
                        p.communicate(input=text.encode('utf-8'))
                        return True

                    except (subprocess.SubprocessError, FileNotFoundError):
                        pass

            return False  # All methods failed

        except Exception as e:
            print(f"Clipboard error: {str(e)}")
            return False  # Catch-all for unexpected errors
        
    def copy_to_clipboard(self, text):
        """Copy text to system clipboard"""
        return self.set_system_clipboard(text)
