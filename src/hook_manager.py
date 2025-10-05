# ----------------------------------------------------------------
# PyLine 1.0 - Hook Manager Core (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

import importlib.util

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Set
from utils import LanguageHookExecutor


class HookManager:
    def __init__(self, config_manager: Optional[Any] = None) -> None:
        self.hooks_dir = Path.home() / ".pyline" / "hooks"
        self.hooks_dir.mkdir(parents=True, exist_ok=True)
        self.disabled_hooks: Set[str] = set()
        self.config_manager = config_manager
        self._load_disabled_hooks()

    def _load_disabled_hooks(self) -> None:
        """Load disabled hooks from config and filesystem with config taking priority"""
        self.disabled_hooks.clear()

        # Load from filesystem (files starting with underscore)
        fs_disabled = set()
        for hook_file in self.hooks_dir.rglob("*"):
            if not hook_file.is_file():
                continue
            if hook_file.suffix not in [".py", ".js", ".pl", ".rb", ".sh", ".lua", ".php"]:
                continue

            # If file starts with underscore, add to filesystem disabled set
            if hook_file.name.startswith("_"):
                rel_path = hook_file.relative_to(self.hooks_dir)
                hook_id = str(rel_path).replace(".py", "").lstrip("_")
                fs_disabled.add(hook_id)

        # Load from config (if config manager is available)
        config_disabled = set()
        if self.config_manager:
            try:
                hook_configs = self.config_manager.get_all_hook_configs()
                if isinstance(hook_configs, dict):
                    for hook_id, config in hook_configs.items():
                        if isinstance(config, dict) and not config.get("enabled", True):
                            config_disabled.add(hook_id)
            except Exception as e:
                print(f"Error loading hook configs: {e}")
                # Fall back to filesystem only
                self.disabled_hooks = fs_disabled
                return

        # CONFIG TAKES PRIORITY: If hook is disabled in config, it's disabled regardless of filesystem
        # If no config manager, use filesystem state
        if self.config_manager:
            self.disabled_hooks = config_disabled
            # Also sync filesystem to match config for hooks that exist
            self._sync_filesystem_to_config(config_disabled, fs_disabled)
        else:
            self.disabled_hooks = fs_disabled

    def _sync_filesystem_to_config(self, config_disabled: Set[str], fs_disabled: Set[str]) -> None:
        """Sync filesystem state to match config state"""
        try:
            # Enable hooks that are in config enabled but filesystem disabled
            for hook_id in fs_disabled - config_disabled:
                hook_file = self.find_hook_file_by_id(hook_id)
                if hook_file and hook_file.name.startswith("_"):
                    new_name = hook_file.name.lstrip("_")
                    new_path = hook_file.parent / new_name
                    hook_file.rename(new_path)

            # Disable hooks that are in config disabled but filesystem enabled
            for hook_id in config_disabled - fs_disabled:
                hook_file = self.find_hook_file_by_id(hook_id)
                if hook_file and not hook_file.name.startswith("_"):
                    new_name = f"_{hook_file.name}"
                    new_path = hook_file.parent / new_name
                    hook_file.rename(new_path)

        except Exception as e:
            print(f"Warning: Could not sync filesystem to config: {e}")

    def is_hook_enabled(self, hook_id: str) -> Any:
        """Check if a hook is enabled - CONFIG TAKES PRIORITY"""
        # Config manager takes priority if available
        if self.config_manager:
            return self.config_manager.get_hook_enabled(hook_id)

        # Fall back to runtime state if no config manager
        return hook_id not in self.disabled_hooks

    def find_hook_file_by_id(self, hook_id: str) -> Optional[Path]:
        """Find the actual file for a hook ID"""
        # First try the exact ID
        potential_path = self.hooks_dir / f"{hook_id}.py"
        if potential_path.exists():
            return potential_path

        # Search for other file extensions
        for ext in [".js", ".pl", ".rb", ".sh", ".lua", ".php"]:
            potential_path = self.hooks_dir / f"{hook_id}{ext}"
            if potential_path.exists():
                return potential_path

        # Fall back to recursive search for complex paths
        for hook_file in self.hooks_dir.rglob("*"):
            if not hook_file.is_file():
                continue
            if hook_file.suffix not in [".py", ".js", ".pl", ".rb", ".sh", ".lua", ".php"]:
                continue
            if self.get_hook_id(hook_file) == hook_id:
                return hook_file
        return None

    def enable_hook(self, hook_id: str) -> bool:
        """Enable a hook in both config and filesystem"""
        try:
            # Update config first (if available)
            if self.config_manager:
                self.config_manager.set_hook_enabled(hook_id, True)

            # Then update filesystem
            hook_file = self.find_hook_file_by_id(hook_id)
            if hook_file and hook_file.name.startswith("_"):
                new_name = hook_file.name.lstrip("_")
                new_path = hook_file.parent / new_name
                hook_file.rename(new_path)

            # Update runtime state
            if hook_id in self.disabled_hooks:
                self.disabled_hooks.remove(hook_id)

            return True

        except Exception as e:
            print(f"Error enabling hook {hook_id}: {e}")
            return False

    def disable_hook(self, hook_id: str) -> bool:
        """Disable a hook in both config and filesystem"""
        try:
            # Update config first (if available)
            if self.config_manager:
                self.config_manager.set_hook_enabled(hook_id, False)

            # Then update filesystem
            hook_file = self.find_hook_file_by_id(hook_id)
            if hook_file and not hook_file.name.startswith("_"):
                new_name = f"_{hook_file.name}"
                new_path = hook_file.parent / new_name
                hook_file.rename(new_path)

            # Update runtime state
            self.disabled_hooks.add(hook_id)

            return True

        except Exception as e:
            print(f"Error disabling hook {hook_id}: {e}")
            return False

    def get_hook_id(self, hook_file: Path) -> str:
        """Generate a unique ID for a hook file based on its relative path"""
        rel_path = hook_file.relative_to(self.hooks_dir)
        hook_id = str(rel_path).replace(".py", "").lstrip("_")

        # Remove priority suffix for ID purposes
        if "__" in hook_id:
            base_id = "__".join(hook_id.split("__")[:-1])
            # Check if the last part is a number (priority)
            try:
                int(hook_id.split("__")[-1])
                return base_id
            except ValueError:
                pass

        return hook_id

    def _get_hook_priority(self, hook_file: Path) -> int:
        """
        Extract priority from filename (e.g., handler__90.py -> priority 90)
        """
        name = hook_file.stem.lstrip("_")  # Remove leading underscore for disabled hooks
        if "__" in name:
            try:
                # Extract the part after the last __
                priority_str = name.split("__")[-1]
                return int(priority_str)
            except ValueError:
                # If the part after __ isn't a number, use default
                pass
        return 50  # Default priority

    def _get_sorted_hooks(self, hook_dir: Path) -> List[Tuple[str, Path]]:
        """Get hooks sorted by priority, excluding disabled hooks - returns (hook_id, path)"""
        hooks = []
        for hook_file in hook_dir.iterdir():
            # ONLY include supported file types
            if hook_file.suffix not in [".py", ".js", ".pl", ".rb", ".sh", ".lua", ".php"]:
                continue

            # Skip disabled hooks (those starting with underscore)
            if hook_file.name.startswith("_"):
                continue

            # Check if hook is disabled in config/runtime
            hook_id = self.get_hook_id(hook_file)
            if not self.is_hook_enabled(hook_id):
                continue

            priority = self._get_hook_priority(hook_file)
            hooks.append((priority, hook_id, hook_file))

        # Sort by priority (higher first), then by filename
        hooks.sort(key=lambda x: (-x[0], x[2].name))
        return [(hook_id, hook_file) for priority, hook_id, hook_file in hooks]

    def _execute_hook(self, hook_file: Path, context: Dict[str, Any]) -> Optional[Any]:
        """Execute a single hook file"""
        if hook_file.suffix == ".py":
            # Python hook execution
            try:
                # Load the Python module
                spec = importlib.util.spec_from_file_location(hook_file.stem, hook_file)
                if spec is None:
                    print(f"Warning: Could not create module spec for {hook_file.name}")
                    return None

                module = importlib.util.module_from_spec(spec)
                if spec.loader is None:
                    print(f"Warning: No loader found for {hook_file.name}")
                    return None

                spec.loader.exec_module(module)

                # Call the main function if it exists
                if hasattr(module, "main"):
                    return module.main(context)
                else:
                    print(f"Warning: Hook {hook_file.name} has no main() function")
                    return None

            except Exception as e:
                print(f"Error executing Python hook {hook_file.name}: {e}")
                return None
        else:
            # Non-Python hook execution
            return LanguageHookExecutor.execute_script(hook_file, context)

    def execute_hooks(self, hook_category: str, hook_type: str, context: Dict[str, Any]) -> Optional[Any]:
        """
        Execute all hooks in a category/type and return the first hook that
        returns handled_output=1 or produces actual output
        """
        hook_dir = self.hooks_dir / hook_category / hook_type
        if not hook_dir.exists():
            return None

        for hook_id, hook_file in self._get_sorted_hooks(hook_dir):
            try:
                result = self._execute_hook(hook_file, context)

                # Check if this hook actually handled the output
                if result is not None:
                    # If it's a dict with handled_output=1, use it
                    if isinstance(result, dict) and result.get("handled_output") == 1:
                        return result

                    # If it's a string with content, use it (assume it handled it)
                    elif isinstance(result, str) and result.strip():
                        return result

                    # If it's a dict with handled_output=0, CONTINUE to next hook
                    elif isinstance(result, dict) and result.get("handled_output") == 0:
                        continue  # Try next hook

                    # For any other non-None result, use it
                    else:
                        return result

            except Exception as e:
                print(f"Hook {hook_id} failed: {e}")

        return None

    def execute_all_hooks(self, hook_category: str, hook_type: str, context: Dict[str, Any]) -> List[Any]:
        """
        Execute all hooks in a category/type and return all results
        """
        hook_dir = self.hooks_dir / hook_category / hook_type
        if not hook_dir.exists():
            return []

        results = []
        for hook_id, hook_file in self._get_sorted_hooks(hook_dir):
            try:
                result = self._execute_hook(hook_file, context)
                if result is not None:
                    results.append(result)
            except Exception as e:
                print(f"Hook {hook_id} failed: {e}")

        return results

    def list_all_hooks(self) -> List[Dict[str, Any]]:
        """Get all hooks with their status"""
        all_hooks = []

        # Use rglob to search recursively through all subdirectories
        for hook_file in self.hooks_dir.rglob("*"):
            if not hook_file.is_file():
                continue

            # ONLY include supported file types
            if hook_file.suffix not in [".py", ".js", ".pl", ".rb", ".sh", ".lua", ".php"]:
                continue

            hook_id = self.get_hook_id(hook_file)
            enabled = self.is_hook_enabled(hook_id)

            # Determine category and type based on directory structure
            rel_path = hook_file.relative_to(self.hooks_dir)
            parts = rel_path.parts

            if len(parts) > 1:
                category = parts[0]
                hook_type = parts[1] if len(parts) > 1 else "root"
            else:
                category = "root"
                hook_type = "root"

            all_hooks.append(
                {
                    "id": hook_id,
                    "path": str(hook_file),
                    "enabled": enabled,
                    "name": hook_file.stem.lstrip("_"),
                    "category": category,
                    "type": hook_type,
                }
            )

        return all_hooks
