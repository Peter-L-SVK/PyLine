# ----------------------------------------------------------------
# PyLine 0.9.8 - Theme Manager Mode (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

import os
from pathlib import Path

from config import ConfigManager
from theme_manager import ThemeManager
import utils


def handle_theme_manager() -> None:
    """Handle theme management interface"""
    os.system("clear")
    theme_manager = ThemeManager()
    config_manager = ConfigManager()
    config_manager.refresh_available_themes()
    choice = None
    while choice != "q":
        print("Theme Manager - Manage PyLine Themes:\n")
        print("  ls - List all themes")
        print("  use <theme> - Switch to theme")
        print("  info <theme> - Show theme details")
        print("  create <name> - Create new theme based on current")
        print("  delete <name> - Delete a theme (cannot delete built-in)")
        print("  edit <name> - Show theme file location for editing")
        print("  cls - Clear screen")
        print("  q - Exit theme manager\n")

        try:
            choice = input("Theme Manager Command: ").lower().strip()
            os.system("clear")
            if choice == "ls":
                os
                themes = theme_manager.list_themes()
                current_theme = theme_manager.current_theme

                print("\nAvailable Themes:")
                print("=" * 50)
                for theme in themes:
                    status = " (current)" if theme["name"] == current_theme else ""
                    print(f"{theme['display_name']}{status}")
                    print(f"  Description: {theme['description']}")
                    print(f"  File: {theme['file_path']}")
                    print()
                utils.prompt_continue()

            elif choice.startswith("use "):
                theme_name = choice[4:].strip()
                if theme_manager.set_theme(theme_name):
                    print(f"Theme changed to: {theme_name}")
                    print("Restart the editor for changes to take full effect.")
                utils.prompt_continue()

            elif choice.startswith("info "):
                theme_name = choice[5:].strip()
                theme_data = theme_manager.get_theme(theme_name)

                if theme_data:
                    print(f"\nTheme: {theme_data.get('name', theme_name)}")
                    print(f"Description: {theme_data.get('description', 'No description')}")
                    print("\nAvailable colors:")
                    colors = theme_data.get("colors", {})
                    for color_name, color_code in colors.items():
                        # Display the color with its actual color
                        color_demo = f"{color_code}■■■■{theme_manager.get_color('reset')}"
                        print(f"  {color_name:20} {color_demo} {color_code}")
                else:
                    print(f"Theme not found: {theme_name}")
                utils.prompt_continue()

            elif choice.startswith("create "):
                theme_name = choice[7:].strip()
                if theme_manager.create_theme(theme_name, theme_manager.current_theme):
                    print(f"Theme '{theme_name}' created based on '{theme_manager.current_theme}'")
                    print(f"Edit ~/.pyline/themes/{theme_name}.theme to customize it.")
                utils.prompt_continue()

            elif choice.startswith("delete "):
                theme_name = choice[7:].strip()
                if theme_manager.delete_theme(theme_name):
                    print(f"Theme '{theme_name}' deleted")
                utils.prompt_continue()

            elif choice.startswith("edit "):
                theme_name = choice[5:].strip()
                if theme_manager.edit_theme(theme_name):
                    # Offer to open the file if possible
                    open_file = input("Open file in default editor? (y/n): ").lower()
                    if open_file == "y":
                        theme_file = Path.home() / ".pyline" / "themes" / f"{theme_name}.theme"
                        try:
                            import subprocess

                            subprocess.run([os.environ.get("EDITOR", "nano"), str(theme_file)])
                        except Exception as e:
                            print(f"Could not open editor: {e}")
                utils.prompt_continue()

            elif choice == "cls":
                os.system("clear")

            elif choice == "q":
                os.system("clear")
                print("Exited theme manager.\n")
                break

            else:
                print("Invalid command. Please choose from the menu.")
                utils.prompt_continue()

        except EOFError:
            os.system("clear")
            print("\nExited theme manager.\n")
            break

        except KeyboardInterrupt:
            os.system("clear")
            print("\nExited theme manager.\n")
            break
