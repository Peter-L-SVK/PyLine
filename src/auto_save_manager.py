# ----------------------------------------------------------------
# PyLine 1.2 - AutoSave Manager (GPLv3)
# Copyright (C) 2025-2026 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# Feel free to distribute and modify.
# ----------------------------------------------------------------

import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any

from config import config_manager
from status_manager import status_manager


class AutoSaveManager:
    """Manages automatic backup saves with configurable intervals"""

    def __init__(self, hook_utils, interval_minutes: int = None, max_backups: int = None):
        self.hook_utils = hook_utils

        # Use config values if provided, otherwise defaults
        self.interval = (interval_minutes or config_manager.get("autosave.interval_minutes", 3)) * 60
        self.max_backups = max_backups or config_manager.get("autosave.max_backups", 5)

        # Get backup directory from config - Unix path
        self.backup_dir = Path(config_manager.get("paths.backup_dir", str(Path.home() / ".pyline" / "backups")))
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._last_save_time = 0

    def start_autosave(self, buffer_manager, filename: str) -> None:
        """Start the auto-save loop for a file"""
        if self._running:
            self.stop_autosave()

        self._running = True
        self._thread = threading.Thread(target=self._autosave_loop, args=(buffer_manager, filename), daemon=True)
        self._thread.start()

    def stop_autosave(self) -> None:
        """Stop the auto-save loop"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None

    def _autosave_loop(self, buffer_manager, filename: str) -> None:
        """Main auto-save loop"""
        while self._running:
            time.sleep(self.interval)

            if not self._running:
                break

            # Only save if buffer is dirty and has content
            if buffer_manager.dirty and buffer_manager.lines and any(line.strip() for line in buffer_manager.lines):
                self._perform_autosave(buffer_manager, filename)

    def _get_backup_path(self, original_filename: str) -> Path:
        """Generate backup file path in centralized directory"""
        original_path = Path(original_filename).resolve()

        # Create a safe path structure within backup_dir
        # For Unix: /home/user/file.txt -> backups/home/user/file.txt
        # Remove the leading slash and create the path structure
        relative_path = str(original_path).lstrip("/")
        backup_path = self.backup_dir / relative_path

        # Millisecond timestamp so rapid autosaves don't collide
        timestamp = int(time.time() * 1000)
        backup_filename = f"{backup_path.stem}.~{timestamp}~{backup_path.suffix}"

        # Return path with timestamp inserted
        return backup_path.parent / backup_filename

    def _perform_autosave(self, buffer_manager, original_filename: str) -> None:
        """Perform the actual auto-save operation"""
        if not original_filename:
            return

        # Generate backup filename (pure computation, safe to do outside try)
        backup_path = self._get_backup_path(original_filename)

        # Pre-save hooks (may modify content)
        pre_save_context = {
            "filename": str(backup_path),
            "original_filename": original_filename,
            "lines": buffer_manager.lines,
            "action": "pre_autosave",
            "operation": "file_autosave",
        }
        pre_save_result = self.hook_utils.execute_pre_save(pre_save_context)

        lines_to_save = buffer_manager.lines
        if pre_save_result and "content" in pre_save_result:
            lines_to_save = pre_save_result["content"]

        # Content processing hooks
        content_context = {
            "filename": str(backup_path),
            "content": lines_to_save,
            "action": "process_content",
            "operation": "file_autosave",
        }
        content_result = self.hook_utils.execute_editing_handlers("process_content", content_context)

        if content_result and "content" in content_result:
            lines_to_save = content_result["content"]

        # ---- Filesystem work is inside the try ----
        try:
            # Create parent directories if needed (may fail on unwritable paths)
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Write backup file
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines_to_save))

            self._last_save_time = time.time()

            # Clean up old backups (best-effort, already swallows its own errors)
            self._cleanup_old_backups(original_filename)

            # Post-save hooks
            post_save_context = {
                "filename": str(backup_path),
                "original_filename": original_filename,
                "lines": lines_to_save,
                "line_count": len(lines_to_save),
                "action": "post_autosave",
                "operation": "file_autosave",
            }
            self.hook_utils.execute_post_save(post_save_context)

            if config_manager.get("autosave.notify", True):
                status_manager.show_message(f"Auto-saved: {backup_path.name}")

        except OSError as e:
            # Filesystem-level failure (mkdir, open, write, disk full, ...)
            # Swallow so the autosave thread keeps running for the next tick.
            status_manager.show_message(f"Auto-save failed: {str(e)[:50]}")

        except Exception as e:
            # Any other unexpected error — still don't kill the thread.
            status_manager.show_message(f"Auto-save error: {str(e)[:50]}")

    def _cleanup_old_backups(self, original_filename: str) -> None:
        """Remove old backup files beyond max_backups limit"""
        original_path = Path(original_filename).resolve()

        # Get the backup directory for this file
        relative_path = str(original_path).lstrip("/")
        backup_dir = self.backup_dir / Path(relative_path).parent
        base_name = original_path.stem

        if backup_dir.exists():
            # Find all backups for this file
            backup_pattern = f"{base_name}.~*~*"
            backups = list(backup_dir.glob(backup_pattern))

            # Filter to only backups of this specific file (not same name in different dirs)
            backups = [b for b in backups if b.stem.startswith(f"{base_name}.~")]

            # Sort by modification time (oldest first)
            backups.sort(key=lambda x: x.stat().st_mtime)

            # Remove oldest backups beyond our limit
            removed_count = 0
            while len(backups) >= self.max_backups:
                oldest = backups.pop(0)
                try:
                    oldest.unlink()
                    removed_count += 1
                except OSError:
                    # Silent fail for cleanup - don't bother user with old backup removal errors
                    pass

            # Optional: Show notification when cleaning up (only if more than 1 removed)
            if removed_count > 1 and config_manager.get("autosave.notify", True):
                status_manager.show_message(f"Cleaned up {removed_count} old backups")

    def get_backup_files(self, original_filename: str) -> list[Path]:
        """Get list of existing backup files for a file, newest first"""
        original_path = Path(original_filename).resolve()

        # Get the backup directory for this file
        relative_path = str(original_path).lstrip("/")
        backup_dir = self.backup_dir / Path(relative_path).parent
        base_name = original_path.stem

        if not backup_dir.exists():
            return []

        # Find all backups for this file
        backup_pattern = f"{base_name}.~*~*"
        backups = list(backup_dir.glob(backup_pattern))

        # Filter to only backups of this specific file
        backups = [b for b in backups if b.stem.startswith(f"{base_name}.~")]

        # Return sorted newest first
        return sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True)

    def restore_from_backup(self, backup_filename: str, buffer_manager) -> bool:
        """Restore content from a backup file"""
        try:
            with open(backup_filename, "r", encoding="utf-8") as f:
                content = [line.rstrip("\n") for line in f]

            buffer_manager.lines = content
            buffer_manager.dirty = True

            # Show success in status bar
            status_manager.show_message(f"Restored from: {Path(backup_filename).name}")
            return True

        except Exception as e:
            status_manager.show_message(f"Restore failed: {str(e)[:50]}")
            return False
