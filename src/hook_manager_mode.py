# ----------------------------------------------------------------
# PyLine 0.9.7 - Hook Manager Mode (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

import os

from hook_ui import hook_ui
import utils


def handle_hook_manager() -> None:
    """Handle hook management interface"""
    os.system("clear")

    choice = None
    while choice != "q":
        utils.hook_manager_menu()

        try:
            choice = input("\nHook Manager Command: ").lower().strip()

            if choice == "ls":
                detailed = input("Show detailed info? (y/n): ").lower() == "y"
                os.system("clear")
                hook_ui.list_all_hooks(detailed=detailed)
                utils.prompt_continue()

            elif choice == "info":
                search_term = input("Enter hook name or ID to search: ").strip()
                if search_term:
                    found_hooks = hook_ui.find_hook(search_term)
                    if found_hooks:
                        print(f"\nFound {len(found_hooks)} hooks:")
                        for hook in found_hooks:
                            status = hook_ui.get_hook_status(hook["id"])
                            status_str = "\033[1;32mENABLED\033[0m" if status else "\033[1;31mDISABLED\033[0m"
                            print(f"  {hook['name']} ({status_str})")
                            print(f"    ID: {hook['id']}")
                            print(f"    Description: {hook['description']}")
                    else:
                        print("No hooks found matching search term.")
                utils.prompt_continue()

            elif choice == "enable":
                hook_id = input("Enter hook ID to enable: ").strip()
                if hook_id:
                    # Try to find the hook by ID
                    hook_found = False
                    for hook in hook_ui.hook_mgr.list_all_hooks():
                        if hook["id"] == hook_id:
                            if not hook_ui.get_hook_status(hook_id):
                                hook_ui.toggle_hook(hook_id, enable=True)
                            else:
                                print(f"Hook {hook_id} is already enabled")
                            hook_found = True
                            break

                    if not hook_found:
                        print("Hook ID not found. Use 'info' to find correct IDs.")
                hook_ui.refresh_hook_list()
                utils.prompt_continue()

            elif choice == "disable":
                hook_id = input("Enter hook ID to disable: ").strip()
                if hook_id:
                    # Try to find the hook by ID
                    hook_found = False
                    for hook in hook_ui.hook_mgr.list_all_hooks():
                        if hook["id"] == hook_id:
                            if hook_ui.get_hook_status(hook_id):
                                hook_ui.toggle_hook(hook_id, enable=False)
                            else:
                                print(f"Hook {hook_id} is already disabled")
                            hook_found = True
                            break

                    if not hook_found:
                        print("Hook ID not found. Use 'info' to find correct IDs.")
                hook_ui.refresh_hook_list()
                utils.prompt_continue()

            elif choice == "reload":
                hook_ui.reload_all_hooks()
                print("Hook system reloaded from filesystem")
                utils.prompt_continue()

            elif choice == "cls":
                os.system("clear")

            elif choice == "q":
                os.system("clear")
                print("Exited hook manager.\n")
                break

            else:
                print("Invalid command. Please choose from the menu.")
                utils.prompt_continue()

        except EOFError:
            os.system("clear")
            print("\nExited hook manager.\n")
            break

        except KeyboardInterrupt:
            os.system("clear")
            print("\nExited hook manager.\n")
            break
