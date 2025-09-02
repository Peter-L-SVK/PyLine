# ----------------------------------------------------------------
# PyLine 0.9.7 - Buffer Manager (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

from typing import List, Optional
from base_manager import BaseManager
from hook_utils import HookUtils


class BufferManager(BaseManager):
    """Manages text buffer content and file operations with full hook integration."""

    def __init__(self, hook_utils: HookUtils):
        super().__init__(hook_utils)
        self.lines: List[str] = [""]
        self.filename: Optional[str] = None
        self.dirty: bool = False

    def load_file(self, filename: str) -> bool:
        """Load file contents into buffer with hook integration."""
        try:
            # Pre-load hooks
            pre_load_context = {"filename": filename, "action": "pre_load", "operation": "file_load"}
            pre_load_result = self.hook_utils.execute_pre_load(pre_load_context)

            content = None

            # Handle the JSON wrapper from LanguageHookExecutor
            if isinstance(pre_load_result, dict):
                # Try multiple possible content fields
                for field in ["content", "output", "text", "data"]:
                    if field in pre_load_result:
                        content = pre_load_result[field]
                        break

                # If no content field found but hook succeeded, assume content was transformed
                if content is None and pre_load_result.get("success"):
                    content = None

            elif isinstance(pre_load_result, str):
                # Hook returned plain text directly
                content = pre_load_result

            # If hooks didn't provide valid content or returned failure, load from file
            if content is None or content == "":
                # Normal file loading with UTF-8 encoding
                with open(filename, "r", encoding="utf-8") as f:
                    content = [line.rstrip("\n") for line in f]

            # Convert string content to list of lines if needed
            if isinstance(content, str):
                content = content.split("\n")

            # Process content through content hooks
            content_context = {
                "filename": filename,
                "content": content,
                "action": "process_content",
                "operation": "file_load",
            }
            content_result = self.hook_utils.execute_editing_handlers("process_content", content_context)

            if content_result and isinstance(content_result, dict) and "content" in content_result:
                self.lines = content_result["content"]
            else:
                self.lines = content

            self.filename = filename
            self.dirty = False

            # Post-load hooks
            post_load_context = {
                "filename": filename,
                "lines": self.lines,
                "line_count": len(self.lines),
                "action": "post_load",
                "operation": "file_load",
            }
            self.hook_utils.execute_post_load(post_load_context)

            return True

        except Exception as e:
            # Error handling
            error_context = {"filename": filename, "error": str(e), "action": "load_error", "operation": "file_load"}
            self.hook_utils.execute_event_handlers("error", error_context)
            return False

    def save(self) -> bool:
        """Save buffer contents to file with hook integration."""
        if not self.filename:
            return False

        try:
            # Pre-save hooks
            pre_save_context = {
                "filename": self.filename,
                "lines": self.lines,
                "action": "pre_save",
                "operation": "file_save",
            }
            pre_save_result = self.hook_utils.execute_pre_save(pre_save_context)

            lines_to_save = self.lines
            if pre_save_result and "content" in pre_save_result:
                # Hook modified the content
                lines_to_save = pre_save_result["content"]

            # Content processing hooks
            content_context = {
                "filename": self.filename,
                "content": lines_to_save,
                "action": "process_content",
                "operation": "file_save",
            }
            content_result = self.hook_utils.execute_editing_handlers("process_content", content_context)

            if content_result and "content" in content_result:
                lines_to_save = content_result["content"]

            # Actual file saving
            with open(self.filename, "w") as f:
                f.write("\n".join(lines_to_save))

            self.dirty = False

            # Post-save hooks
            post_save_context = {
                "filename": self.filename,
                "lines": lines_to_save,
                "line_count": len(lines_to_save),
                "action": "post_save",
                "operation": "file_save",
            }
            self.hook_utils.execute_post_save(post_save_context)

            return True

        except Exception as e:
            # Error hooks
            error_context = {
                "filename": self.filename,
                "error": str(e),
                "action": "save_error",
                "operation": "file_save",
            }
            self.hook_utils.execute_event_handlers("error", error_context)
            return False

    def insert_line(self, index: int, text: str) -> str:
        """Insert line at index with hook integration."""
        # Pre-insert hooks
        pre_insert_context = {
            "line_number": index,
            "text": text,
            "filename": self.filename,
            "action": "pre_insert",
            "operation": "line_insert",
        }
        pre_insert_result = self.hook_utils.execute_pre_insert(pre_insert_context)

        text_to_insert = text
        if pre_insert_result and "text" in pre_insert_result:
            text_to_insert = pre_insert_result["text"]
        if pre_insert_result and "cancel" in pre_insert_result:
            return text_to_insert  # Insertion cancelled

        # Actual insertion
        self.lines.insert(index, text_to_insert)
        self.dirty = True

        # Post-insert hooks
        post_insert_context = {
            "line_number": index,
            "text": text_to_insert,
            "filename": self.filename,
            "action": "post_insert",
            "operation": "line_insert",
        }
        self.hook_utils.execute_post_insert(post_insert_context)

        return text_to_insert

    def delete_line(self, index: int) -> str:
        """Delete line at index with hook integration."""
        if not (0 <= index < len(self.lines)):
            return ""

        line_text = self.lines[index]

        # Pre-delete hooks
        pre_delete_context = {
            "line_number": index,
            "text": line_text,
            "filename": self.filename,
            "action": "pre_delete",
            "operation": "line_delete",
        }
        pre_delete_result = self.hook_utils.execute_pre_delete(pre_delete_context)

        if pre_delete_result and "cancel" in pre_delete_result:
            return ""  # Deletion cancelled

        # Actual deletion
        deleted = self.lines.pop(index)
        self.dirty = True

        # Post-delete hooks
        post_delete_context = {
            "line_number": index,
            "text": deleted,
            "filename": self.filename,
            "action": "post_delete",
            "operation": "line_delete",
        }
        self.hook_utils.execute_post_delete(post_delete_context)

        return deleted

    def set_line(self, index: int, text: str) -> str:
        """Set line at index with hook integration."""
        if not (0 <= index < len(self.lines)):
            return ""

        old_text = self.lines[index]

        # Pre-edit hooks
        pre_edit_context = {
            "line_number": index,
            "old_text": old_text,
            "new_text": text,
            "filename": self.filename,
            "action": "pre_edit",
            "operation": "line_edit",
        }
        pre_edit_result = self.hook_utils.execute_editing_handlers("pre_edit", pre_edit_context)

        text_to_set = text
        if pre_edit_result and "new_text" in pre_edit_result:
            text_to_set = pre_edit_result["new_text"]
        if pre_edit_result and "cancel" in pre_edit_result:
            return old_text  # Edit cancelled

        # Actual edit
        self.lines[index] = text_to_set
        self.dirty = True

        # Post-edit hooks
        post_edit_context = {
            "line_number": index,
            "old_text": old_text,
            "new_text": text_to_set,
            "filename": self.filename,
            "action": "post_edit",
            "operation": "line_edit",
        }
        self.hook_utils.execute_editing_handlers("post_edit", post_edit_context)

        return text_to_set

    # Helper methods for compatibility
    def get_line(self, index: int) -> str:
        """Get line at index with bounds checking."""
        if 0 <= index < len(self.lines):
            return self.lines[index]
        return ""

    def get_line_count(self) -> int:
        """Get total number of lines."""
        return len(self.lines)
