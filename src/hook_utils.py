# ----------------------------------------------------------------
# PyLine 1.0 - Hook Utilities (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

from typing import Dict, Any, Optional, List
from hook_manager import HookManager


class HookUtils:
    """Utility class for organized hook execution following the directory structure"""

    def __init__(self, hook_manager: HookManager):
        self.hook_manager = hook_manager

    # Input Handlers -----------------------------------------------------------
    def execute_input_handlers(self, hook_type: str, context: Dict[str, Any]) -> Optional[Any]:
        """Execute input handler hooks"""
        return self.hook_manager.execute_hooks("input_handlers", hook_type, context)

    def execute_edit_line(self, context: Dict[str, Any]) -> Optional[str]:
        """Execute edit line input handlers"""
        return self.execute_input_handlers("edit_line", context)

    # Event Handlers -----------------------------------------------------------
    def execute_event_handlers(self, hook_type: str, context: Dict[str, Any]) -> List[Any]:
        """Execute event handler hooks and return all results"""
        return self.hook_manager.execute_all_hooks("event_handlers", hook_type, context)

    def execute_on_save(self, context: Dict[str, Any]) -> List[Any]:
        """Execute on_save event handlers"""
        return self.execute_event_handlers("on_save", context)

    def execute_on_open(self, context: Dict[str, Any]) -> List[Any]:
        """Execute on_open event handlers"""
        return self.execute_event_handlers("on_open", context)

    def execute_on_close(self, context: Dict[str, Any]) -> List[Any]:
        """Execute on_close event handlers"""
        return self.execute_event_handlers("on_close", context)

    def execute_pre_save(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute pre-save hooks (can modify content)"""
        return self.hook_manager.execute_hooks("event_handlers", "pre_save", context)

    def execute_post_save(self, context: Dict[str, Any]) -> List[Any]:
        """Execute post-save hooks"""
        return self.execute_event_handlers("post_save", context)

    def execute_pre_load(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute pre-load hooks (can modify content)"""
        return self.hook_manager.execute_hooks("event_handlers", "pre_load", context)

    def execute_post_load(self, context: Dict[str, Any]) -> List[Any]:
        """Execute post-load hooks"""
        return self.execute_event_handlers("post_load", context)

    # Syntax Handlers ----------------------------------------------------------
    def execute_syntax_handlers(self, hook_type: str, context: Dict[str, Any]) -> Optional[Any]:
        """Execute syntax handler hooks"""
        return self.hook_manager.execute_hooks("syntax_handlers", hook_type, context)

    def execute_highlight(self, context: Dict[str, Any]) -> Optional[str]:
        """Execute syntax highlighting hooks"""
        return self.execute_syntax_handlers("highlight", context)

    def execute_lint(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute linting hooks"""
        return self.execute_syntax_handlers("lint", context)

    # Editing Operations -------------------------------------------------------
    def execute_editing_handlers(self, hook_type: str, context: Dict[str, Any]) -> Optional[Any]:
        """Execute editing operation hooks"""
        return self.hook_manager.execute_hooks("editing_ops", hook_type, context)

    def execute_pre_insert(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute pre-insert line hooks"""
        return self.execute_editing_handlers("pre_insert", context)

    def execute_post_insert(self, context: Dict[str, Any]) -> List[Any]:
        """Execute post-insert line hooks"""
        return self.hook_manager.execute_all_hooks("editing_ops", "post_insert", context)

    def execute_pre_delete(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute pre-delete hooks"""
        return self.execute_editing_handlers("pre_delete", context)

    def execute_post_delete(self, context: Dict[str, Any]) -> List[Any]:
        """Execute post-delete hooks"""
        return self.hook_manager.execute_all_hooks("editing_ops", "post_delete", context)

    # Clipboard Operations -----------------------------------------------------
    def execute_clipboard_handlers(self, hook_type: str, context: Dict[str, Any]) -> Optional[Any]:
        """Execute clipboard operation hooks"""
        return self.hook_manager.execute_hooks("clipboard_ops", hook_type, context)

    def execute_pre_copy(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute pre-copy hooks (can modify text)"""
        return self.execute_clipboard_handlers("pre_copy", context)

    def execute_post_copy(self, context: Dict[str, Any]) -> List[Any]:
        """Execute post-copy hooks"""
        return self.hook_manager.execute_all_hooks("clipboard_ops", "post_copy", context)

    def execute_pre_paste(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute pre-paste hooks (can modify text)"""
        return self.execute_clipboard_handlers("pre_paste", context)

    def execute_post_paste(self, context: Dict[str, Any]) -> List[Any]:
        """Execute post-paste hooks"""
        return self.hook_manager.execute_all_hooks("clipboard_ops", "post_paste", context)

    # Session Handlers ---------------------------------------------------------
    def execute_session_handlers(self, hook_type: str, context: Dict[str, Any]) -> List[Any]:
        """Execute session handler hooks"""
        return self.hook_manager.execute_all_hooks("session_handlers", hook_type, context)

    def execute_pre_edit(self, context: Dict[str, Any]) -> List[Any]:
        """Execute pre-edit session hooks"""
        return self.execute_session_handlers("pre_edit", context)

    def execute_post_edit(self, context: Dict[str, Any]) -> List[Any]:
        """Execute post-edit session hooks"""
        return self.execute_session_handlers("post_edit", context)

    def execute_and_display(self, category: str, hook_type: str, context: Dict[str, Any]) -> bool:
        """
        Execute hooks and let them handle output directly.
        Returns True if any hook was executed and handled output, False otherwise.
        """
        hook_dir = self.hook_manager.hooks_dir / category / hook_type
        if not hook_dir.exists():
            return False

        # Get sorted hooks
        hooks = []
        for hook_file in hook_dir.iterdir():
            if hook_file.suffix not in [".py", ".js", ".pl", ".rb", ".sh", ".lua", ".php"]:
                continue
            if hook_file.name.startswith("_"):
                continue

            hook_id = self.hook_manager.get_hook_id(hook_file)
            if not self.hook_manager.is_hook_enabled(hook_id):
                continue

            priority = self.hook_manager._get_hook_priority(hook_file)
            hooks.append((priority, hook_id, hook_file))

        hooks.sort(key=lambda x: (-x[0], x[2].name))

        if not hooks:
            return False

        # Execute hooks until one returns True (indicating it handled output)
        for priority, hook_id, hook_file in hooks:
            try:
                result = self.hook_manager._execute_hook(hook_file, context)

                # Check if hook returned a dict with handled_output = 1 OR produced output
                if (
                    result is not None
                    and isinstance(result, dict)
                    and (
                        result.get("handled_output") == 1
                        or (result.get("output") and len(result.get("output", "").strip()) > 0)
                    )
                ):

                    # If the hook produced output, print it
                    if result.get("output"):
                        print(result["output"])

                    return True

            except Exception:
                # Silent fail - if one hook fails, try others
                continue

        return False


# Singleton instance (optional)
_hook_utils_instance = None


def get_hook_utils(hook_manager: Optional[HookManager] = None) -> HookUtils:
    """Get or create HookUtils instance"""
    if hook_manager is not None:
        return HookUtils(hook_manager)
    # Fallback if no hook_manager provided
    return HookUtils(HookManager())
