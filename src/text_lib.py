#----------------------------------------------------------------
# PyLine 0.7 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

import fcntl
import os
import sys
import termios
import time
import tty

import readline

from typing import List, Tuple, Optional

class TextLib:
    @staticmethod
    def get_key_input() -> str:
        """Read a single key press, including arrow keys"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)

            if ch == '\x02': return 'undo'  # Ctrl+B
            if ch == '\x06': return 'redo'  # Ctrl+F

            if ch == '\x1b':  # Possible arrow key
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
                try:
                    ch2 = sys.stdin.read(2)
                    if len(ch2) == 2 and ch2[0] == '[':
                        if ch2[1] in 'AB': return ch + ch2  # Arrows
                        if ch2[1] == '5' and sys.stdin.read(1) == '~': return '\x1b[5~'  # PgUp
                        if ch2[1] == '6' and sys.stdin.read(1) == '~': return '\x1b[6~'  # PgDn
                        if ch2[1] == 'F': return '\x1b[F'  # End
                finally:
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl)
                return ch
            return ch.lower() if ch else ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    @staticmethod
    def show_status_message(message: str) -> None:
        """Display status messages consistently"""
        print(f"\n{message}", end='')
        time.sleep(0.455)
        sys.stdout.flush()
        sys.stdout.write("\033[F\033[K")  # Move up and clear line

    @staticmethod
    def init_color_support() -> bool:
        """Initialize terminal color support"""
        if not (hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()):
            return False
        if os.environ.get('TERM', '') == 'dumb':
            return False
        return True

    @staticmethod
    def display_buffer(
        lines: List[str],
        filename: Optional[str],
        current_line: int,
        display_start: int,
        display_lines: int,
        selection_start: Optional[int],
        selection_end: Optional[int],
        syntax_highlighter,
        is_python: bool
    ) -> None:
        """Display the buffer contents with formatting"""
        os.system('clear')
        sys.stdout.write("\033[?25h\033[0m")  # Ensure cursor visible and reset
        
        print(f"\033[0mEditing: {filename or 'New file'}")
        print("""\033[0mCommands: ↑/↓, PgUp/PgDn/End - Navigate, Enter - Edit, Ctrl+B/F - Undo/Redo,
        C - Copy, V - Paste, O - Overwrite lines, W - Write changes, S - Select,  Q - Quit""")
        print("\033[0m" + "-" * 92)

        for idx in range(display_start, min(display_start + display_lines, len(lines))):
            line_num = idx + 1
            if (selection_start is not None and selection_end is not None and 
                idx >= min(selection_start, selection_end) and 
                idx <= max(selection_start, selection_end)):
                prefix = "\033[1;31m=\033[0m"  # Selected
            elif idx == current_line:
                prefix = ">"  # Current line
            else:
                prefix = " "
                
            line_text = lines[idx]
            if is_python and filename and filename.endswith('.py'):
                line_text = syntax_highlighter._highlight_python(line_text)
                    
            print(f"\033[0m{prefix}{line_num:4d}: {line_text}\033[0m")
        sys.stdout.flush()

    @staticmethod
    def edit_line(line_num: int, old_text: str) -> str:
        """Edit a single line with readline support."""
        readline.set_startup_hook(lambda: readline.insert_text(old_text))
        try:
            print()
            prompt = f"{line_num:4d} [edit]: "
            # Get input and preserve trailing newline if original had one
            new_text = input(prompt)
            if old_text.endswith('\n'):
                return new_text + '\n'
            
            return new_text.rstrip('\n')
        
        finally:
            readline.set_startup_hook(None)
