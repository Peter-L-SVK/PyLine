# ----------------------------------------------------------------
# PyLine 1.1 - TextBuffer Library (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

import fcntl
import os
import sys
import termios
import time
import tty

import readline

from typing import Any, List, Optional
from theme_manager import theme_manager
import utils


class TextLib:
    @staticmethod
    def get_key_input() -> str:
        """Read a single key press, including arrow keys"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)

            if ch == "\x02":
                return "undo"  # Ctrl+B
            if ch == "\x06":
                return "redo"  # Ctrl+F

            if ch == "\x1b":  # Possible arrow key
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
                try:
                    ch2 = sys.stdin.read(2)
                    if len(ch2) == 2 and ch2[0] == "[":
                        if ch2[1] in "AB":
                            return ch + ch2  # Arrows
                        if ch2[1] == "5" and sys.stdin.read(1) == "~":
                            return "\x1b[5~"  # PgUp
                        if ch2[1] == "6" and sys.stdin.read(1) == "~":
                            return "\x1b[6~"  # PgDn
                        if ch2[1] == "H":
                            return "\x1b[H"  # Home
                        if ch2[1] == "F":
                            return "\x1b[F"  # End
                    elif ch2 == "\x06":  # Ctrl+Alt+F
                        return "\x1b\x06"
                    elif ch2 == "\x12":  # Ctrl+Alt+R
                        return "\x1b\x12"
                finally:
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl)
                return ch

            return ch.lower() if ch else ""

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    @staticmethod
    def show_status_message(message: str) -> None:
        """Display status messages consistently"""
        print(f"\n{message}", end="")
        time.sleep(0.455)
        sys.stdout.flush()
        sys.stdout.write("\033[F\033[K")  # Move up and clear line

    @staticmethod
    def init_color_support() -> bool:
        """Initialize terminal color support"""
        if not (hasattr(sys.stdout, "isatty") and sys.stdout.isatty()):
            return False

        if os.environ.get("TERM", "") == "dumb":
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
        syntax_highlighter: Any,
        is_python: bool,
    ) -> None:
        """Display the buffer contents with UTF-8 support"""
        utils.clear_screen()

        # Get colors from theme manager
        RESET = theme_manager.get_color("reset")
        SELECTION_COLOR = theme_manager.get_color("selection")
        HEADER_COLOR = theme_manager.get_color("menu_title")
        BORDER_COLOR = theme_manager.get_color("line_numbers")

        sys.stdout.write(f"\033[?25h{RESET}")  # Ensure cursor visible and reset

        # Handle empty buffer - ensure we always have at least one line
        if not lines:
            lines = [""]

        # Safe UTF-8 output without breaking stdout
        try:
            # Header lines
            header = f"{HEADER_COLOR}Editing: {filename or 'New file'}{RESET}\n"
            header += f"""{HEADER_COLOR}Commands: ↑/↓, PgUp/PgDn/Home/End - Navigate, Enter - Edit, Ctrl+B/F - Undo/Redo,
          C - Copy, V - Paste, O - Overwrite lines, W - Write changes, J - Jump, S - Select, H - Help,  Q - Quit{RESET}\n"""
            header += f"{BORDER_COLOR}" + "-" * 115 + f"{RESET}\n"

            sys.stdout.buffer.write(header.encode("utf-8", errors="replace"))

            # Ensure display_start is within bounds
            display_start = max(0, min(display_start, len(lines) - 1))
            end_index = min(display_start + display_lines, len(lines))

            for idx in range(display_start, end_index):
                line_num = idx + 1
                if (
                    selection_start is not None
                    and selection_end is not None
                    and idx >= min(selection_start, selection_end)
                    and idx <= max(selection_start, selection_end)
                ):
                    prefix = f"{SELECTION_COLOR}={RESET}"  # Selected
                elif idx == current_line:
                    prefix = ">"  # Current line (no special color)
                else:
                    prefix = " "

                original_line_text = lines[idx]  # Keep original for display
                display_line_text = original_line_text  # Start with original

                # Use hook-based syntax highlighting for DISPLAY only (not storage)
                try:
                    from hook_utils import get_hook_utils

                    hook_utils = get_hook_utils()

                    highlight_context = {
                        "line": original_line_text,  # Pass original line without colors
                        "line_number": idx + 1,
                        "filename": filename,
                        "total_lines": len(lines),
                        "action": "highlight",
                        "operation": "syntax_highlighting",
                    }

                    # Execute syntax highlighting hooks for DISPLAY purposes only
                    highlighted_result = hook_utils.execute_highlight(highlight_context)

                    if highlighted_result and isinstance(highlighted_result, str):
                        # Use the highlighted version for display only
                        display_line_text = highlighted_result
                    elif highlighted_result and isinstance(highlighted_result, dict) and "output" in highlighted_result:
                        display_line_text = highlighted_result["output"]
                    else:
                        # Fallback to Python highlighter for .py files only
                        if is_python and filename and filename.endswith(".py"):
                            display_line_text = syntax_highlighter._highlight_python(original_line_text)

                except ImportError:
                    # Fallback if hook system not available
                    if is_python and filename and filename.endswith(".py"):
                        display_line_text = syntax_highlighter._highlight_python(original_line_text)

                # Safe UTF-8 output - use display_line_text (with colors) for output only
                line_display = f"{RESET}{prefix}{line_num:4d}: {display_line_text}{RESET}\n"
                sys.stdout.buffer.write(line_display.encode("utf-8", errors="replace"))

            sys.stdout.flush()

        except (OSError, UnicodeEncodeError):
            # Fallback to basic output (without colors)
            sys.stdout = sys.__stdout__
            print(f"Editing: {filename or 'New file'}")
            print("Command [↑↓, PgUp/PgDn, Home/End, J(ump), E(dit), I(nsert), D(el), S(elect), H(elp), G(ramar)")
            print("C(opy), V(paste), O(verwrite), W(rite), Q(uit)]:")
            print("-" * 115)

            # Handle empty buffer in fallback
            if not lines:
                print(">   1: ")
            else:
                for idx in range(display_start, min(display_start + display_lines, len(lines))):
                    line_num = idx + 1
                    if idx == current_line:
                        prefix = ">"
                    else:
                        prefix = " "
                    # Use original lines (without color codes) in fallback mode
                    print(f"{prefix}{line_num:4d}: {lines[idx]}")

    @staticmethod
    def edit_line(line_num: int, old_text: str) -> str:
        """Edit a single line with readline support."""
        # Skip history tracking for line editing to avoid conflicts
        from utils import history_manager

        history_manager.skip_next_add()

        readline.set_startup_hook(lambda: readline.insert_text(old_text))
        try:
            print()
            prompt = f"{line_num:4d} [edit]: "
            # Get input and preserve trailing newline if original had one
            new_text = input(prompt)
            if old_text.endswith("\n"):
                return new_text + "\n"

            return new_text.rstrip("\n")

        finally:
            readline.set_startup_hook(None)
            TextLib.clear_line()
            TextLib.move_up(1)

    @staticmethod
    def clear_line() -> None:
        """Clear the current terminal line"""
        sys.stdout.write("\033[K")
        sys.stdout.flush()

    @staticmethod
    def move_up(lines: int = 1) -> None:
        """Move cursor up specified number of lines"""
        sys.stdout.write(f"\033[{lines}F")
        sys.stdout.flush()
