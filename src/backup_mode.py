# ----------------------------------------------------------------
# PyLine 1.2 - Backup Mode (GPLv3)
# Copyright (C) 2025-2026 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# Feel free to distribute and modify.
# ----------------------------------------------------------------

from pathlib import Path
import time
from typing import List, Optional

import utils


class BackupMode:
    def __init__(self, text_buffer):
        self.text_buffer = text_buffer
        self.backups: List[Path] = []

    def show_backup_menu(self) -> None:
        """Main backup management interface"""
        utils.clear_screen()
        utils.history_manager.set_context("backup_mode")

        # Refresh backups first
        self._refresh_backups()

        # Check if there are any backups
        if not self.backups:
            print("No backup files found for this file.")
            print("Backups are created automatically when you edit and save files.")
            utils.prompt_continue()
            return

        choice = None
        while choice != "q":
            self._refresh_backups()
            utils.clear_screen()
            utils.display_backup_menu(self)

            try:
                choice = utils.smart_input("\nBackup Command: ").lower().strip()

                if choice == "ls":
                    self._list_backups(detailed=True)
                    utils.prompt_continue()

                elif choice == "info":
                    self._show_backup_info()
                    utils.prompt_continue()

                elif choice == "restore":
                    self._restore_backup()
                    utils.prompt_continue()

                elif choice == "clean":
                    self._clean_old_backups()
                    utils.prompt_continue()

                elif choice == "cleanall":
                    self._clean_all_backups()
                    utils.prompt_continue()

                elif choice == "diff":
                    self._show_diff_with_current()
                    utils.prompt_continue()

                elif choice == "cls":
                    utils.clear_screen()

                elif choice == "q":
                    utils.clear_screen()
                    print("Returned to editor.\n")
                    break

                else:
                    print("Invalid command. Please choose from the menu.")
                    utils.prompt_continue()

            except EOFError:
                utils.clear_screen()
                print("\nExited backup mode.\n")
                break

            except KeyboardInterrupt:
                utils.clear_screen()
                print("\nExited backup mode.\n")
                break

        # Redraw editor exactly once when we leave backup mode
        self.text_buffer.display()

    def _refresh_backups(self) -> None:
        """Refresh the list of available backups"""
        self.backups = self.text_buffer.get_available_backups()

    def _list_backups(self, detailed: bool = False) -> None:
        """List all available backups"""
        if not self.backups:
            print("No backup files found.")
            return

        from theme_manager import theme_manager

        FILE_COLOR = theme_manager.get_color("menu_item")
        SIZE_COLOR = theme_manager.get_color("line_numbers")
        RESET_COLOR = theme_manager.get_color("reset")

        print(f"\nBackup files for: {self.text_buffer.buffer_manager.filename}")
        print("─" * 70)

        for i, backup in enumerate(self.backups, 1):
            stat = backup.stat()
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
            size_kb = stat.st_size / 1024

            status = "🟢" if i == 1 else "🟡"

            print(f"{status} {i:2d}. {FILE_COLOR}{backup.name}{RESET_COLOR}")

            if detailed:
                print(f"      Time: {time_str}")
                print(f"      Size: {SIZE_COLOR}{size_kb:.1f} KB{RESET_COLOR}")
                print(f"      Path: {backup}")

                if stat.st_size < 100 * 1024:
                    try:
                        with open(backup, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                        print(f"      Lines: {len(lines)}")
                    except Exception:
                        print(f"      Lines: (unreadable)")
                print()

    def _show_backup_info(self) -> None:
        """Show detailed information about a specific backup"""
        if not self.backups:
            print("No backups available.")
            return

        self._list_backups(detailed=False)

        try:
            backup_num = int(input("\nEnter backup number: ")) - 1
            if 0 <= backup_num < len(self.backups):
                backup = self.backups[backup_num]
                self._display_backup_details(backup)
            else:
                print("Invalid backup number.")
        except ValueError:
            print("Please enter a valid number.")

    def _display_backup_details(self, backup: Path) -> None:
        """Display detailed information about a backup file"""
        stat = backup.stat()

        print(f"\n📄 Backup Details:")
        print(f"   Name: {backup.name}")

        try:
            rel_path = backup.relative_to(self.text_buffer.auto_save_manager.backup_dir)
            print(f"   Path: ~/.pyline/backups/{rel_path}")
        except ValueError:
            print(f"   Path: {backup}")

        # These were incorrectly nested inside the except ValueError —
        # they should always print.
        print(f"   Size: {stat.st_size} bytes ({stat.st_size / 1024:.1f} KB)")
        print(f"   Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))}")

        if ".~" in backup.name:
            original_name = backup.name.split(".~")[0]
            try:
                rel_path = backup.relative_to(self.text_buffer.auto_save_manager.backup_dir)
                original_path = Path("/") / rel_path.parent / original_name
                print(f"   Original: {original_path}")
            except Exception:
                print(f"   Original: {original_name}")

        try:
            with open(backup, "r", encoding="utf-8") as f:
                lines = f.readlines()

                print(f"   Lines: {len(lines)}")
                if lines:
                    first_line = lines[0][:60].strip()
                    print(f"   First line: {first_line if first_line else '(empty)'}")

                    if len(lines) > 1:
                        last_line = lines[-1][:60].strip()
                        print(f"   Last line: {last_line if last_line else '(empty)'}")

        except Exception:
            print(f"   Content: Unable to read")
            print()

    def _restore_backup(self) -> None:
        """Restore from a backup file"""
        if not self.backups:
            print("No backups available to restore.")
            return

        self._list_backups(detailed=False)

        try:
            backup_num = int(input("\nEnter backup number to restore: ")) - 1
            if 0 <= backup_num < len(self.backups):
                backup = self.backups[backup_num]

                confirm = input(f"Restore from {backup.name}? This will replace current content. (y/N): ")
                if confirm.lower() == "y":
                    if self.text_buffer.restore_from_backup(str(backup)):
                        print("✅ Backup restored successfully!")
                        print("Don't forget to save the file to make changes permanent.")
                    else:
                        print("❌ Failed to restore backup.")
                else:
                    print("Restoration cancelled.")
            else:
                print("Invalid backup number.")
        except ValueError:
            print("Please enter a valid number.")

    def _clean_old_backups(self) -> None:
        """Remove old backups, keeping only the latest ones"""
        if len(self.backups) <= 3:
            print("No old backups to clean (keeping all 3 or fewer backups).")
            return

        to_remove = self.backups[3:]

        print(f"Will remove {len(to_remove)} old backups:")
        for backup in to_remove:
            print(f"  - {backup.name}")

        confirm = input("\nProceed with cleanup? (y/N): ")
        if confirm.lower() == "y":
            removed_count = 0
            for backup in to_remove:
                try:
                    backup.unlink()
                    print(f"✅ Removed: {backup.name}")
                    removed_count += 1
                except OSError as e:
                    print(f"❌ Failed to remove {backup.name}: {e}")

            print(f"\nCleaned up {removed_count} backup files.")
            self._refresh_backups()
        else:
            print("Cleanup cancelled.")

    def _clean_all_backups(self) -> None:
        """Remove all backup files"""
        if not self.backups:
            print("No backups to remove.")
            return

        print("Will remove ALL backup files:")
        for backup in self.backups:
            print(f"  - {backup.name}")

        confirm = input("\nDelete ALL backups? This cannot be undone! (y/N): ")
        if confirm.lower() == "y":
            removed_count = 0
            for backup in self.backups:
                try:
                    backup.unlink()
                    print(f"✅ Removed: {backup.name}")
                    removed_count += 1
                except OSError as e:
                    print(f"❌ Failed to remove {backup.name}: {e}")

            print(f"\nRemoved {removed_count} backup files.")
            self._refresh_backups()
        else:
            print("Cleanup cancelled.")

    def _show_diff_with_current(self) -> None:
        """Show differences between backup and current file"""
        if not self.backups:
            print("No backups available for comparison.")
            return

        self._list_backups(detailed=False)

        try:
            backup_num = int(input("\nEnter backup number to compare: ")) - 1
            if 0 <= backup_num < len(self.backups):
                backup = self.backups[backup_num]
                self._display_diff(backup)
            else:
                print("Invalid backup number.")
        except ValueError:
            print("Please enter a valid number.")

    def _display_diff(self, backup: Path) -> None:
        """Display differences between backup and current content"""
        try:
            with open(backup, "r", encoding="utf-8") as f:
                backup_lines = [line.rstrip("\n") for line in f]
        except Exception as e:
            print(f"❌ Could not read backup file: {e}")
            return

        current_lines = self.text_buffer.buffer_manager.lines

        print(f"\n📊 Comparison: Current vs {backup.name}")
        print("─" * 50)
        print(f"Current lines: {len(current_lines)}")
        print(f"Backup lines:  {len(backup_lines)}")

        if current_lines == backup_lines:
            print("✅ Files are identical.")
            return

        max_lines = min(len(current_lines), len(backup_lines))
        differences = 0

        for i in range(max_lines):
            if current_lines[i] != backup_lines[i]:
                differences += 1
                if differences <= 5:
                    print(f"\nLine {i + 1}:")
                    print(f"  Current: {current_lines[i][:60]}")
                    print(f"  Backup:  {backup_lines[i][:60]}")

        if len(current_lines) != len(backup_lines):
            print(f"\nDifferent line count: current has {len(current_lines)}, backup has {len(backup_lines)}")

        if differences > 5:
            print(f"\n... and {differences - 5} more differences.")
