# ----------------------------------------------------------------
# PyLine 1.0 - Utils (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

# Standard library imports
import argparse
import json
import os
from pathlib import Path
import sys
import subprocess
from typing import Any, Dict, List, NoReturn

# Local application imports
import info


def editor_menu() -> None:
    print("PyLine Editor Commands:\n")
    print("  Basic:")
    print("       1 - Edit existing file  2 - Create new file   3 - Truncate/new file")
    print("     cls - Clear screen       cw - Count words       i - Program info")
    print("      hs - Hook status         q - Quit\n")
    print("  Advanced:")
    print("      hm - Hook manager    x - Exec mode (file operations)")
    print("      tm - Theme manager\n")


def exec_menu() -> None:
    print("Executable Mode - File Operations:\n")
    print("  Navigation:")
    print("     af - List all files         cwd - Change working directory")
    print("    cdp - Change default path\n")
    print("  File Operations:")
    print("    mkdir - Create directory     rmfile - Delete file")
    print("    rmdir - Remove directory     rename - Rename file/dir\n")
    print("  Utilities:")
    print("     cls - Clear screen          q - Exit exec mode\n")


def hook_manager_menu() -> None:
    print("Hook Manager - Manage PyLine Extensions:\n")
    print("  Navigation:")
    print("    ls - List all hooks          info - Show hook info")
    print("    enable - Enable hook         disable - Disable hook")
    print("    reload - Reload all hooks    cls - Clear screen")
    print("    q - Exit hook manager\n")


def theme_manager_menu() -> None:
    print("Theme Manager - Manage PyLine Themes:\n")
    print("  ls - List all themes")
    print("  use <theme> - Switch to theme")
    print("  info <theme> - Show theme details")
    print("  create <name> - Create new theme based on current")
    print("  delete <name> - Delete a theme (cannot delete built-in)")
    print("  edit <name> - Show theme file location for editing")
    print("  cls - Clear screen")
    print("  q - Exit theme manager\n")


def parse_arguments() -> argparse.Namespace:
    """Handle command-line arguments"""
    parser = argparse.ArgumentParser(description="PyLine Text Editor")
    parser.add_argument("filename", nargs="?", help="File to edit")
    parser.add_argument("-i", "--info", action="store_true", help="Show program information and exit")
    return parser.parse_args()


def show_info(original_destination: str) -> None:
    os.system("clear")
    info.print_info()
    info.print_license_parts(original_destination)
    print("\n")
    prompt_continue()


def prompt_continue_woc() -> None:
    os.system('read -p "Press enter to continue..."')


def prompt_continue() -> None:
    os.system('read -p "Press enter to continue..."')
    os.system("clear")


def handle_sigint(signum: int, frame: Any) -> NoReturn:
    sys.stdout.write("\nProgram interrupted. Exiting gracefully...\n")
    print("\033[0m", end="")
    sys.stdout.flush()
    sys.exit(128 + signum)  # In case of Ctrl+C, 128+2 as defined by POSIX


def clean_exit_wop() -> NoReturn:
    print("\033[0m", end="")
    sys.stdout.flush()
    sys.exit(0)


def clean_exit() -> NoReturn:
    os.system("clear")
    print("\nProgram closed.\n")
    prompt_continue()
    print("\033[0m", end="")
    sys.stdout.flush()
    sys.exit(0)


class LanguageHookExecutor:
    """Generic executor for any language hook"""

    # Map file extensions to their interpreters
    LANGUAGE_MAP: Dict[str, List[str]] = {
        "pl": ["perl"],
        "js": ["node"],
        "lua": ["lua"],
        "rb": ["ruby"],
        "py": [sys.executable],  # Use current Python
        "sh": ["bash"],
        "php": ["php"],
        # Add more as needed
    }

    @classmethod
    def execute_script(cls, script_path: Path, context: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """Execute any script based on its file extension"""
        script_path = Path(script_path)
        ext = script_path.suffix.lower()[1:]  # Remove dot

        if ext not in cls.LANGUAGE_MAP:
            raise ValueError(f"Unsupported script language: {ext}")

        try:
            cmd = cls.LANGUAGE_MAP[ext] + [str(script_path)]
            result = subprocess.run(cmd, input=json.dumps(context), capture_output=True, text=True, timeout=timeout)

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout exceeded"}

        except FileNotFoundError:
            return {"success": False, "error": f"Interpreter not found: {cls.LANGUAGE_MAP[ext][0]}"}


def help_scr_prepare() -> str:
    from theme_manager import ThemeManager

    theme_manager = ThemeManager()

    # Get colors from theme manager
    RESET = theme_manager.get_color("reset")
    TITLE_COLOR = theme_manager.get_color("menu_title")
    HEADER_COLOR = theme_manager.get_color("selection")
    COMMAND_COLOR = theme_manager.get_color("line_numbers")
    DESCRIPTION_COLOR = theme_manager.get_color("reset")
    help_text = f"""
    {TITLE_COLOR}╔══════════════════════════════════════════════════════════════════════════════╗
    ║                         PyLine Editor - Help Screen                          ║
    ╚══════════════════════════════════════════════════════════════════════════════╝{RESET}

    {HEADER_COLOR}Navigation Commands:{RESET}
    {COMMAND_COLOR}  ↑ / ↓{DESCRIPTION_COLOR}          - Move cursor up/down line by line
    {COMMAND_COLOR}  PgUp / PgDn{DESCRIPTION_COLOR}     - Move page up/down
    {COMMAND_COLOR}  Home / End{DESCRIPTION_COLOR}      - Jump to beginning/end of file
    {COMMAND_COLOR}  J{DESCRIPTION_COLOR}               - Jump to specific line number
    {COMMAND_COLOR}  Ctrl+Alt+F{DESCRIPTION_COLOR}      - Incremental search

    {HEADER_COLOR}Editing Commands:{RESET}
    {COMMAND_COLOR}  Enter / E{DESCRIPTION_COLOR}       - Edit current line
    {COMMAND_COLOR}  I{DESCRIPTION_COLOR}               - Insert new line after current position
    {COMMAND_COLOR}  D{DESCRIPTION_COLOR}               - Delete current line (or selection)
    {COMMAND_COLOR}  Ctrl+B{DESCRIPTION_COLOR}          - Undo last operation
    {COMMAND_COLOR}  Ctrl+F{DESCRIPTION_COLOR}          - Redo last undone operation

    {HEADER_COLOR}Selection & Clipboard:{RESET}
    {COMMAND_COLOR}  S{DESCRIPTION_COLOR}               - Start/end selection mode
    {COMMAND_COLOR}  C{DESCRIPTION_COLOR}               - Copy current line or selection
    {COMMAND_COLOR}  V{DESCRIPTION_COLOR}               - Paste from clipboard (insert mode)
    {COMMAND_COLOR}  O{DESCRIPTION_COLOR}               - Overwrite with clipboard content

    {HEADER_COLOR}Search & Replace:{RESET}
    {COMMAND_COLOR}  Ctrl+Alt+F{DESCRIPTION_COLOR}      - Search for text
    {COMMAND_COLOR}  Ctrl+Alt+R{DESCRIPTION_COLOR}      - Search and replace

    {HEADER_COLOR}File Operations:{RESET}
    {COMMAND_COLOR}  W{DESCRIPTION_COLOR}               - Write/save file
    {COMMAND_COLOR}  Q / Esc{DESCRIPTION_COLOR}         - Quit (with save prompt if modified)

    {HEADER_COLOR}Other Commands:{RESET}
    {COMMAND_COLOR}  H{DESCRIPTION_COLOR}               - This help screen

    {TITLE_COLOR}╔══════════════════════════════════════════════════════════════════════════════╗
    ║                    Press   Enter   to return to editor...                    ║
    ╚══════════════════════════════════════════════════════════════════════════════╝{RESET}
    """

    return help_text


def show_help() -> None:
    """Display help screen using the theme manager."""
    # Clear screen and display help
    os.system("clear")

    # Display help text
    print(help_scr_prepare())

    # Wait for any key press
    prompt_continue_woc()
