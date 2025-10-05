# ----------------------------------------------------------------
# PyLine 1.0 - Hook Manager UI (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

from pathlib import Path
from typing import Any, Dict, List, Optional

from config import config_manager
from hook_manager import HookManager
from theme_manager import theme_manager


class HookManagerUI:
    def __init__(self, config_manager: Optional[Any] = None) -> None:
        # Use provided config_manager or fall back to singleton
        self.config_manager = config_manager or config_manager
        self.hook_mgr = HookManager(config_manager=self.config_manager)  # Pass config_manager instance
        self.hooks_dir = Path.home() / ".pyline" / "hooks"

    def list_all_hooks(self, detailed: bool = False) -> None:
        """List all available hooks with their status - COMPLETELY GENERIC"""
        print("=" * 80)
        print("PyLine Hook Manager - All Hooks")
        print("=" * 80)
        self.refresh_hook_list()

        CATEGORY_COLOR = theme_manager.get_color("hook_category")
        TYPE_COLOR = theme_manager.get_color("hook_type")
        ENABLED_COLOR = theme_manager.get_color("hook_enabled")
        DISABLED_COLOR = theme_manager.get_color("hook_disabled")
        NAME_COLOR = theme_manager.get_color("menu_item")
        RESET_COLOR = theme_manager.get_color("reset")

        if not self.hooks_dir.exists():
            print("No hooks directory found. Creating basic structure...")
            self.hooks_dir.mkdir(parents=True, exist_ok=True)
            print("Created hooks directory:", self.hooks_dir)
            return

        # FIXED: Remove the undefined hook_id parameter
        hooks = self.hook_mgr.list_all_hooks()

        if not hooks:
            print("No hooks installed.")
            return

        # Group by category
        hooks_by_category: Dict[str, List[Dict[str, Any]]] = {}
        for hook in hooks:
            category = hook["category"]
            if category not in hooks_by_category:
                hooks_by_category[category] = []
            hooks_by_category[category].append(hook)

        # Display summary
        enabled_count = sum(1 for hook in hooks if hook["enabled"])
        print(f"Hooks Directory: {self.hooks_dir}")
        print(f"Total Hooks: {len(hooks)} | Active: {enabled_count} | Disabled: {len(hooks) - enabled_count}")
        print("-" * 80)

        # Display hooks by category
        for category, category_hooks in hooks_by_category.items():
            print(f"\n{CATEGORY_COLOR}{category.upper()}:{RESET_COLOR}")

            # Group by type within category
            hooks_by_type: Dict[str, List[Dict[str, Any]]] = {}
            for hook in category_hooks:
                hook_type = hook["type"]
                if hook_type not in hooks_by_type:
                    hooks_by_type[hook_type] = []
                hooks_by_type[hook_type].append(hook)

            for hook_type, type_hooks in hooks_by_type.items():
                if hook_type != "root":  # Don't show 'root' type if it's the same as category
                    print(f"  {TYPE_COLOR}{hook_type}:{RESET_COLOR}")

                for hook in sorted(type_hooks, key=lambda x: x["name"]):
                    status = (
                        f"{ENABLED_COLOR}ENABLED{RESET_COLOR}"
                        if hook["enabled"]
                        else f"{DISABLED_COLOR}DISABLED{RESET_COLOR}"
                    )
                    priority = self.hook_mgr._get_hook_priority(Path(hook["path"]))

                    print(f"    {NAME_COLOR}{hook['name']}{RESET_COLOR} (Priority: {priority})")
                    print(f"      Status: {status} | ID: {hook['id']}")

                    if detailed:
                        hook_info = self._get_hook_info(Path(hook["path"]))
                        description = hook_info.get("description", "No description")
                        print(f"      Description: {description}")
                        print(f"      Path: {hook['path']}")
                    print()

    def toggle_hook(self, hook_id: str, enable: bool = True) -> bool:
        """Enable or disable a hook at runtime AND rename the file - GENERIC"""
        # Find the actual hook file by ID
        hook_file = None
        # Search for all supported file types, not just .py
        for potential_file in self.hooks_dir.rglob("*"):
            if not potential_file.is_file():
                continue

            # Only check supported file types (match what HookManager supports)
            if potential_file.suffix not in [".py", ".js", ".pl", ".rb", ".sh", ".lua", ".php"]:
                continue

            potential_id = self.hook_mgr.get_hook_id(potential_file)
            if potential_id == hook_id:
                hook_file = potential_file
                break

        if not hook_file or not hook_file.exists():
            print(f"Error: Hook not found: {hook_id}")
            return False

        # File system enable/disable (rename) FIRST
        try:
            if enable:
                # Remove leading underscore to enable
                new_name = hook_file.name.lstrip("_")
                if new_name != hook_file.name:
                    new_path = hook_file.parent / new_name
                    hook_file.rename(new_path)
                    hook_file = new_path  # Update reference to new path
            else:
                # Add leading underscore to disable
                if not hook_file.name.startswith("_"):
                    new_name = f"_{hook_file.name}"
                    new_path = hook_file.parent / new_name
                    hook_file.rename(new_path)
                    hook_file = new_path  # Update reference to new path

        except Exception as e:
            print(f"Error toggling hook file: {e}")
            return False

        # THEN update runtime state
        if enable:
            self.hook_mgr.enable_hook(hook_id)
        else:
            self.hook_mgr.disable_hook(hook_id)

        # Refresh the hook manager's disabled hooks list
        self.hook_mgr.disabled_hooks.clear()
        self.hook_mgr._load_disabled_hooks()

        display_name = self.get_hook_display_name(hook_id)
        status = "enabled" if enable else "disabled"
        print(f"Hook '{display_name}' {status} successfully!")
        return True

    def find_hook(self, search_term: str) -> List[Dict[str, Any]]:
        """Find hooks by name, ID, or description - GENERIC"""
        found_hooks: List[Dict[str, Any]] = []

        for hook in self.hook_mgr.list_all_hooks():
            search_lower = search_term.lower()
            hook_info = self._get_hook_info(Path(hook["path"]))

            if (
                search_lower in hook["name"].lower()
                or search_lower in hook["id"].lower()
                or search_lower in hook_info.get("description", "").lower()
            ):
                found_hooks.append({**hook, "description": hook_info.get("description", "No description")})

        return found_hooks

    def _get_hook_info(self, hook_file: Path) -> Dict[str, Any]:
        """Extract information from a hook file"""
        info: Dict[str, Any] = {
            "name": hook_file.stem.lstrip("_"),
            "path": str(hook_file),
            "enabled": not hook_file.name.startswith("_"),
            "priority": self.hook_mgr._get_hook_priority(hook_file),
            "description": "No description available",
        }

        # Try to read description from file
        try:
            with open(hook_file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith('"""') or line.startswith("'''"):
                        # Extract first docstring line
                        info["description"] = line[3:].strip().rstrip('"""').rstrip("'''")
                        break

                    elif line.startswith("# Description:"):
                        info["description"] = line[14:].strip()
                        break

        except Exception:
            pass

        return info

    def get_hook_display_name(self, hook_id: str) -> Any:
        """Get a user-friendly name for a hook ID"""
        for hook in self.hook_mgr.list_all_hooks():
            if hook["id"] == hook_id:
                return hook["name"]

        return hook_id  # Fallback to ID if not found

    def get_hook_status(self, hook_id: str) -> Any:
        """Get current status of a hook by ID"""
        return self.hook_mgr.is_hook_enabled(hook_id)

    def reload_all_hooks(self) -> None:
        """Reload the disabled hooks list from filesystem"""
        self.hook_mgr.disabled_hooks.clear()
        self.hook_mgr._load_disabled_hooks()
        print("Hook system reloaded from filesystem")

    def refresh_hook_list(self) -> None:
        """Refresh the hook list from the filesystem and runtime state"""
        # Reload the hook manager's disabled hooks list
        self.hook_mgr.disabled_hooks.clear()
        self.hook_mgr._load_disabled_hooks()

        # Also clear any cached hook lists if you have them
        if hasattr(self, "_cached_hooks"):
            delattr(self, "_cached_hooks")


# Singleton instance - FIXED: pass the config_manager instance, not the class
hook_ui = HookManagerUI(config_manager=config_manager)
