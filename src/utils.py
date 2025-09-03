# ----------------------------------------------------------------
# PyLine 0.9 - Utils (GPLv3)
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
    print("      hm - Hook manager    x - Exec mode (file operations)\n")


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


def prompt_continue() -> None:
    os.system('read -p "Press enter to continue..."')
    os.system("clear")


def handle_sigint(signum: int, frame: Any) -> NoReturn:
    sys.stdout.write("\nProgram interrupted. Exiting gracefully...\n")
    sys.stdout.flush()
    sys.exit(128 + signum)  # In case of Ctrl+C, 128+2 as defined by POSIX


def clean_exit_wop() -> NoReturn:
    exit(0)


def clean_exit() -> NoReturn:
    os.system("clear")
    print("\nProgram closed.\n")
    prompt_continue()
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
