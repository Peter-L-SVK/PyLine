# ----------------------------------------------------------------
# PyLine 1.1 - Theme Manager Mode (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

import os

from config import ConfigManager
from theme_manager import ThemeManager
import utils


def handle_theme_manager() -> None:
    """Handle theme management interface"""
    utils.clear_screen()
    theme_manager = ThemeManager()
    config_manager = ConfigManager()
    config_manager.refresh_available_themes()
    utils.history_manager.set_context("theme_manager")
    choice = None
    while choice != "q":
        utils.theme_manager_menu()

        try:
            choice = input("Theme Manager Command: ").lower().strip()
            utils.clear_screen()
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

                    # Test with hardcoded colors first
                    print("\nTest with hardcoded colors:")
                    test_colors = [("Red", "\033[91m"), ("Green", "\033[92m"), ("Blue", "\033[94m")]
                    for name, code in test_colors:
                        print(f"  {code}{name}\033[0m")

                    print("\nNow with theme colors:")
                    colors = theme_data.get("colors", {})
                    for color_name, color_code in colors.items():
                        color_code = theme_manager.get_color(color_name, theme_name)
                        # Display the color with its actual color
                        encoded_color = color_code.encode("utf-8").decode("unicode_escape")
                        if color_code.startswith("\033[4") or "48" in color_code:
                            # It's a background color - use theme's foreground color
                            foreground = theme_manager.get_color("foreground")
                            print(
                                f"  {color_name:20}   {encoded_color}{foreground}■■■■{theme_manager.get_color('reset')} ",
                                {color_code},
                            )
                        else:
                            # It's a foreground color - use default background
                            print(
                                f"  {color_name:20} {encoded_color}■■■■{theme_manager.get_color('reset')}", {color_code}
                            )
                    print(f"\nTotal: {len(colors)} colors defined")
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
                if theme_manager.edit_theme_in_editor(theme_name):
                    print(f"Theme '{theme_name}' updated successfully")
                utils.prompt_continue()

            elif choice == "cls":
                utils.clear_screen()

            elif choice == "q":
                utils.clear_screen()
                print("Exited theme manager.\n")
                break

            else:
                print("Invalid command. Please choose from the menu.")
                utils.prompt_continue()

        except EOFError:
            utils.clear_screen()
            print("\nExited theme manager.\n")
            break

        except KeyboardInterrupt:
            utils.clear_screen()
            print("\nExited theme manager.\n")
            break
