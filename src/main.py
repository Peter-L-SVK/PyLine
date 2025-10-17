#!/usr/bin/env python3

# ----------------------------------------------------------------
# PyLine 1.1 - Line Editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

# Standard library imports
import os
import signal
from typing import Any, NoReturn

# Local application imports
from config import config_manager
import dirops
import execmode
from hook_manager import HookManager
import hook_manager_mode
from hook_ui import hook_ui
from hook_utils import get_hook_utils
from text_buffer import TextBuffer
import theme_manager_mode
import utils


def scan_and_initialize_hooks() -> None:
    """Initialize and scan all hooks at startup"""
    print("Initializing hook system...")

    # Create hook manager with config integration
    hook_manager = HookManager(config_manager=config_manager)

    # Scan and load all hooks
    hook_manager._load_disabled_hooks()

    # Get hook statistics
    all_hooks = hook_manager.list_all_hooks()
    enabled_count = sum(1 for hook in all_hooks if hook["enabled"])

    print(f"Hook system ready: {len(all_hooks)} hooks found ({enabled_count} enabled)\n")

    return None


def main() -> NoReturn:
    # Register signal handler (for OS-level interrupts)
    signal.signal(signal.SIGINT, utils.handle_sigint)

    # Initialize configuration and themes
    src_path = config_manager.get_path("source_path")
    config_manager.validate_themes()
    utils.clear_screen()
    # Initialize directory system
    original_dir = dirops.currentdir()
    dirops.original_path(original_dir)
    original_destination = dirops.original_destination()
    dirops.default_path(original_destination)
    current_dir = dirops.cd(config_manager.get_path("original_path"))

    # Initialize hook system with scanning
    scan_and_initialize_hooks()

    # Parse command line arguments
    args = utils.parse_arguments()
    if args:
        buffer = TextBuffer()
    try:
        if args.info:
            utils.show_info(src_path)
            utils.clean_exit_wop()

        if args.filename:  # File specified via command line
            filepath = os.path.abspath(args.filename)
            if os.path.exists(filepath):
                if buffer.load_file(filepath):
                    buffer.edit_interactive()
                else:
                    print(f"Error: Could not load {filepath}")
            else:
                # Create directory structure if needed
                if dirops.ensure_directory_exists(filepath):
                    print(f"Creating new file: {filepath}")
                    buffer.filename = filepath
                    buffer.edit_interactive()
                else:
                    print("Failed to create directory structure")
            utils.clean_exit()

        print("PyLine 1.1 - (GPLv3) for Linux/BSD  Copyright (C) 2018-2025  Peter Leukanič")
        print("This program comes with ABSOLUTELY NO WARRANTY; for details type 'i'.\n")

        utils.history_manager.set_context("main")

        choice = None
        while choice != "q":
            buffer = TextBuffer()
            print(f"Current working directory: {current_dir}\n")
            utils.editor_menu()

            try:
                choice = utils.smart_input("Your choice: ").lower()

                if choice == "1":
                    handle_existing_file(buffer)
                elif choice == "2":
                    handle_new_file(buffer)
                elif choice == "3":
                    handle_truncate_file(buffer)
                elif choice == "cw":
                    count_words()
                elif choice == "hm":
                    hook_manager_mode.handle_hook_manager()
                elif choice == "hs":
                    handle_hook_status()
                elif choice == "tm":
                    theme_manager_mode.handle_theme_manager()
                elif choice == "x":
                    current_dir = execmode.execmode(original_destination)
                elif choice == "cls":
                    os.system("clear")
                elif choice == "i":
                    utils.show_info(src_path)
                elif choice == "q":
                    break
                else:
                    os.system("clear")
                    print("Only choices from the menu!\n")

            except EOFError:
                os.system("clear")
                print("\nTo quit, enter Q !\n")
                continue

    except KeyboardInterrupt:
        pass  # Passing the interupt signal

    utils.clean_exit()


def count_words() -> None:
    """Count words using hook system - universal approach"""
    os.system("clear")

    # Initialize hook utilities
    hook_manager = HookManager(config_manager)
    hook_utils = get_hook_utils(hook_manager)

    answer = None
    while answer != "y":
        answer = input("Would you like to count words in the file? [Y/N]: ").lower()
        if answer == "y":
            while True:
                dirops.contentdir()
                name_of_file = input("\nEnter the name of file to count words: ")
                if not name_of_file:
                    os.system("clear")
                    print("Error, file must have a name!\n")
                    continue

                # Try to read the file
                try:
                    with open(name_of_file, "r") as f:
                        file_content = f.read()
                except IOError:
                    print(f"Error: Could not read file {name_of_file}")
                    break

                # Prepare context for word count hooks
                context = {
                    "action": "count_words",
                    "filename": name_of_file,
                    "file_content": file_content,
                    "command": "count",
                }

                # Use universal approach - hooks handle output directly
                os.system("clear")
                hook_handled = hook_utils.execute_and_display("event_handlers", "word_count", context)

                # If no hooks handled it, fall back to built-in
                if not hook_handled:
                    num_of_words, num_of_lines, num_of_chars = dirops.count_words_in_file(name_of_file)
                    if num_of_words != "error":
                        print("************************************************************")
                        print(f"{name_of_file} contains (built-in):")
                        print(f"- {num_of_words} words")
                        print(f"- {num_of_lines} lines")
                        print(f"- {num_of_chars} characters")
                        print("************************************************************\n")
                break

        elif answer == "n":
            print("Ok, won't count anything.\n")
            utils.prompt_continue()
            break

        else:
            print("Only Y/N!\n")


def handle_existing_file(buffer: Any) -> None:
    os.system("clear")
    utils.history_manager.set_context("editing")
    answer = None
    while answer != "y":
        answer = input("Would you like to edit the file? [Y/N]: ").lower()
        if answer == "y":
            while True:
                dirops.contentdir()
                name_of_file = input("\nEnter the name of file to edit: ")
                if not name_of_file:
                    os.system("clear")
                    print("Error, file must have a name!\n")
                    continue

                if buffer.load_file(name_of_file):
                    buffer.edit_interactive()
                    utils.prompt_continue()
                    break

                else:
                    os.system("clear")
                    print(f"No file with name: {name_of_file}!\n")
                    continue

        elif answer == "n":
            print("Ok, won't edit anything.\n")
            utils.prompt_continue()
            break

        else:
            print("Only Y/N!\n")


def handle_new_file(buffer: Any) -> None:
    os.system("clear")
    utils.history_manager.set_context("editing")
    answer = None
    while answer != "y":
        answer = input("Would you like to create the new file? [Y/N]: ").lower()
        if answer == "y":
            while True:
                dirops.contentdir()
                name_of_file = input("Enter the name of file to create: ")
                os.system("clear")
                if not name_of_file:
                    print("Error, file must have a name!\n")
                    continue

                buffer.buffer_manager.filename = name_of_file
                # Get save status from editor
                save_status = buffer.edit_interactive()

                # Only show additional message if editor didn't handle saving
                if save_status is None and buffer.dirty:
                    if buffer.save():
                        print("File edited and saved.")
                    else:
                        print("Error: Failed to save file!")
                elif save_status is None:
                    print("No changes made to file.")

                utils.prompt_continue()
                break

        elif answer == "n":
            print("Ok, won't create anything.\n")
            utils.prompt_continue()
            break

        else:
            print("Only Y/N!\n")


def handle_truncate_file(buffer: Any) -> None:
    os.system("clear")
    utils.history_manager.set_context("editing")
    answer = None
    while answer != "y":
        answer = input("Would you like to create/truncate the file? [Y/N]: ").lower()
        if answer == "y":
            while True:
                dirops.contentdir()
                name_of_file = input("Enter the name of file to create or to truncate: ")
                if not name_of_file:
                    os.system("clear")
                    print("Error, file must have a name!\n")
                    continue

                buffer.buffer_manager.filename = name_of_file
                buffer.lines = []  # Truncate by clearing buffer
                buffer.dirty = True  # Mark as dirty immediately after truncation

                # Get save status from editor
                save_status = buffer.edit_interactive()

                # Only show additional message if editor didn't handle saving
                if save_status is None and buffer.dirty:
                    if buffer.save():
                        print("File truncated/edited and saved.")
                    else:
                        print("Error: Failed to save file!")
                elif save_status is None:
                    print("No changes made to file.")

                utils.prompt_continue()
                break

        elif answer == "n":
            print("Ok, won't create anything.\n")
            utils.prompt_continue()
            break

        else:
            print("Only Y/N!\n")


def handle_hook_status() -> None:
    utils.clear_screen()
    print("Current Hook Status:")
    print("=" * 50)

    hooks = hook_ui.hook_mgr.list_all_hooks()
    if not hooks:
        print("No hooks installed.")
    else:
        enabled_count = sum(1 for hook in hooks if hook["enabled"])
        print(f"Total Hooks: {len(hooks)} | Active: {enabled_count} | Disabled: {len(hooks) - enabled_count}")
        print("-" * 50)

        for hook in hooks:
            status = "ENABLED" if hook["enabled"] else "DISABLED"
            print(f"{hook['name']}: {status}")
    print("")  # Insert empty line
    utils.prompt_continue()


# ----------------------------------------------
#             main() execution
# ----------------------------------------------
if __name__ == "__main__":
    main()
