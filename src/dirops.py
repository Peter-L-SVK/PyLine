# ----------------------------------------------------------------
# PyLine 0.9.8 - Directories And Files Opertions Library (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

# Standard Library imports
import os
from shutil import rmtree
from pathlib import Path
from typing import Optional, Tuple, Union

# Local imports
from config import config_manager
from theme_manager import theme_manager

path_to_config = Path.home() / ".pyline"
path_to_config.mkdir(exist_ok=True)


def currentdir() -> str:
    # Get the current working directory.
    return os.getcwd()


def contentdir() -> None:
    """List directory contents with enhanced formatting and colored output"""
    print("\nCurrent directory contents:\n")

    # Get colors from theme
    DIR_COLOR = theme_manager.get_color("directory")
    EXEC_COLOR = theme_manager.get_color("executable")
    SYM_COLOR = theme_manager.get_color("symlink")
    RESET_COLOR = theme_manager.get_color("reset")

    # Column formatting
    COLUMN_WIDTH = 28
    ITEMS_PER_ROW = 3

    with os.scandir() as entries:
        # Sort directories first, then alphabetically
        sorted_entries = sorted(entries, key=lambda e: (not e.is_dir(), e.name.lower()))

        entries_with_length = []
        for entry in sorted_entries:
            name = entry.name
            if entry.is_symlink():
                target = os.readlink(entry.path)
                colored = f"{SYM_COLOR}{name} → {target}{RESET_COLOR}"
                raw_length = len(name) + len(target) + 2  # +2 for arrow/spaces
            elif entry.is_dir():
                colored = f"{DIR_COLOR}{name}{RESET_COLOR}"
                raw_length = len(name)
            elif os.access(entry.path, os.X_OK):
                colored = f"{EXEC_COLOR}{name}{RESET_COLOR}"
                raw_length = len(name)
            else:
                colored = name
                raw_length = len(name)

            entries_with_length.append((colored, raw_length))

        # Calculate padding for each entry
        formatted_entries = []
        for text, length in entries_with_length:
            padding = " " * (COLUMN_WIDTH - length) if length < COLUMN_WIDTH else ""
            formatted_entries.append(f"{text}{padding}")

        # Print in columns
        for i in range(0, len(formatted_entries), ITEMS_PER_ROW):
            row = formatted_entries[i : i + ITEMS_PER_ROW]
            print("  ".join(row))

    print()  # Extra newline for spacing


def cd(new_dir: str) -> str:
    # Change the current working directory.
    os.chdir(new_dir)
    return currentdir()


def mkdir(dir_name: str) -> Optional[int]:
    # Create a new directory.
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
        print("Directory", dir_name, "created.\n")
        return None
    else:
        print("Directory named", dir_name, "already exists!\n")
        return 1


def rmfile(file_name: str) -> Optional[int]:
    # Remove a file.
    if os.path.isfile(file_name):
        os.remove(file_name)
        print("File", file_name, "deleted.\n")
        return None
    else:
        print("File", file_name, "doesn't exists!\n")
        return 1


def rmdir(dir_name: str) -> Optional[int]:
    # Remove a directory.
    if os.path.isdir(dir_name):
        rmtree(dir_name)
        print("Directory", dir_name, "deleted.\n")
        return None
    else:
        print("Directory named", dir_name, "doesn't exists!\n")
        return 1


def original_path(original_dir: str) -> Optional[int]:
    """Save the original directory path to config."""
    try:
        config_manager.set_path("original_path", original_dir)
        return None
    except Exception as e:
        print(f"Error saving path: {e}")
        return 1


def original_destination() -> str:
    """Retrieve the original directory path from config."""
    path = config_manager.get_path("original_path")
    if path and os.path.exists(path):
        return path
    return os.getcwd()  # Return current dir if path doesn't exist


def safe_path(current_path: str) -> bool:
    """Save the current directory path to config."""
    try:
        config_manager.set_path("default_path", current_path)
        return True
    except Exception as e:
        print(f"Error saving path: {e}")
        return False


def default_path(original_destination: str) -> bool:
    """Set the default directory path from config."""
    default_path = config_manager.get_path("default_path")

    if not default_path or not os.path.exists(default_path):
        # Fallback to original destination if default path is invalid
        default_path = original_destination
        safe_path(default_path)

    try:
        cd(default_path)
        return True
    except OSError:
        # If default path is invalid, use original destination
        cd(original_destination)
        safe_path(original_destination)
        return False


def change_default_path(original_destination: str) -> int:
    """Change the default directory path in config."""
    try:
        new_default_path = input("Enter the new path (or 0 to reset): ").strip()

        if new_default_path == "0":
            target_path = original_destination
        else:
            target_path = new_default_path

        if not os.path.exists(target_path):
            print(f"Error: Path '{target_path}' doesn't exist")
            return 1

        os.chdir(target_path)
        safe_path(target_path)
        print(f"Default path set to: {target_path}\n")
        return 0

    except EOFError:
        os.system("clear")
        return 1

    except Exception as e:
        print(f"Error changing path: {e}")
        return 1


def ensure_directory_exists(filepath: str) -> bool:
    """Create parent directories if they don't exist"""
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"Created directory: {directory}")
            return True

        except OSError as e:
            print(f"Error creating directory: {e}")
            return False

    return True  # Directory already exists


def count_words_in_file(filename: str) -> Tuple[Union[int, str], int, int]:
    """
    Count the number of words in a text file with improved punctuation handling.

    Args:
        filename (str): Path to the file to be read.

    Returns:
        tuple: (word_count, line_count, char_count) or (error, 0, 0) on error
    """
    try:
        with open(filename, "r") as file:
            line_count = 0
            word_count = 0
            char_count = 0

            for line in file:
                line_count += 1
                char_count += len(line)
                # Split on whitespace and filter out empty strings
                words = [word.strip(",.!?;:\"'()[]") for word in line.split() if word]
                word_count += len(words)
            os.system("clear")
            return word_count, line_count, char_count

    except FileNotFoundError:
        os.system("clear")
        print(f"Error: File '{filename}' not found.")
        return "error", 0, 0

    except Exception as e:
        os.system("clear")
        print(f"An error occurred: {e}")
        return "error", 0, 0
