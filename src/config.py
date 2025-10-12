# ----------------------------------------------------------------
# PyLine 1.1 - Configuration Manager (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    def __init__(self) -> None:
        self.config_dir = Path.home() / ".pyline"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self._source_path = str(Path(__file__).parent.resolve())  # Store source path directly
        self._ensure_config_file()

    def _ensure_config_file(self) -> None:
        """Create default config file if it doesn't exist"""
        if not self.config_file.exists():
            default_config = self._get_default_config()
            self._save_config(default_config)
        else:
            # If config exists, ensure current theme is valid
            self.refresh_available_themes()
            # Ensure hooks section has proper structure
            self._ensure_hooks_structure()

    def _load_config(self) -> Any:
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default config if file is corrupted
            return self._get_default_config()

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration WITHOUT recursive calls"""
        # Dynamically discover available themes
        themes_dir = Path.home() / ".pyline" / "themes"
        available_themes = ["black-on-white", "white-on-black"]  # Always include built-ins

        if themes_dir.exists():
            for theme_file in themes_dir.glob("*.theme"):
                theme_name = theme_file.stem
                if theme_name not in available_themes:
                    available_themes.append(theme_name)

        # Use the stored source_path directly - no recursive calls!
        source_path = self._source_path

        return {
            "paths": {"source_path": source_path, "default_path": str(Path.home()), "original_path": str(Path.home())},
            "editor": {
                "theme": "black-on-white",  # Keep this for backward compatibility
            },
            "hooks": {
                "enabled": True,
                "auto_reload": False,
            },
            "theme": {"current": "black-on-white", "available_themes": available_themes},
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        config = self._load_config()
        keys = key.split(".")
        value = config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        config = self._load_config()
        keys = key.split(".")
        current = config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the value
        current[keys[-1]] = value
        self._save_config(config)

    def get_path(self, path_type: Optional[str] = None) -> str:
        """Get a path from configuration"""
        if path_type is None:
            # Return a default path if no specific type requested
            return str(Path.home())

        path = self.get(f"paths.{path_type}")
        return str(path) if path is not None else str(Path.home())

    def set_path(self, path_type: str, path: str) -> None:
        """Set a path in configuration"""
        self.set(f"paths.{path_type}", path)

    def get_theme(self) -> Any:
        """Get the current theme name, ensuring it's valid"""
        current_theme = self.get("theme.current", "black-on-white")

        # Check if the current theme still exists
        available_themes = self.get("theme.available_themes", [])
        if current_theme not in available_themes:
            # Fall back to default if current theme is invalid
            current_theme = "black-on-white"
            self.set("theme.current", current_theme)

        return current_theme

    def set_theme(self, theme_name: str) -> None:
        """Set the current theme, ensuring it's available"""
        # First refresh available themes to ensure we have the latest list
        self.refresh_available_themes()

        available_themes = self.get("theme.available_themes", [])

        if theme_name in available_themes:
            self.set("theme.current", theme_name)
            # Also update the editor theme for backward compatibility
            self.set("editor.theme", theme_name)
        else:
            print(f"Theme '{theme_name}' is not available. Available themes: {', '.join(available_themes)}")

    def refresh_available_themes(self) -> None:
        """Refresh the list of available themes from the filesystem"""
        themes_dir = Path.home() / ".pyline" / "themes"
        available_themes = ["black-on-white", "white-on-black"]  # Always include built-ins

        if themes_dir.exists():
            for theme_file in themes_dir.glob("*.theme"):
                theme_name = theme_file.stem
                if theme_name not in available_themes:
                    available_themes.append(theme_name)

        self.set("theme.available_themes", available_themes)

        # Ensure current theme is still valid after refresh
        current_theme = self.get("theme.current", "black-on-white")
        if current_theme not in available_themes:
            # Fall back to default if current theme is no longer available
            self.set("theme.current", "black-on-white")
            self.set("editor.theme", "black-on-white")

    def add_available_theme(self, theme_name: str) -> None:
        """Add a theme to the available themes list if it doesn't exist"""
        available_themes = self.get("theme.available_themes")
        if theme_name not in available_themes:
            available_themes.append(theme_name)
            self.set("theme.available_themes", available_themes)

    def remove_available_theme(self, theme_name: str) -> None:
        """Remove a theme from the available themes list"""
        available_themes = self.get("theme.available_themes")
        if theme_name in available_themes:
            available_themes.remove(theme_name)
            self.set("theme.available_themes", available_themes)

    def get_available_themes(self) -> Any:
        """Get list of available themes"""
        return self.get("theme.available_themes")

    def validate_themes(self) -> None:
        """Validate that all configured themes actually exist"""
        self.refresh_available_themes()
        # This will automatically fix any invalid current theme
        self.get_theme()

    def get_hook_config(self, hook_id: str, key: str, default: Any = None) -> Any:
        """Get configuration for a specific hook"""
        # Ensure the hook configuration exists
        self._ensure_hook_exists(hook_id)
        return self.get(f"hooks.{hook_id}.{key}", default)

    def set_hook_config(self, hook_id: str, key: str, value: Any) -> None:
        """Set configuration for a specific hook"""
        # Ensure the hook configuration exists
        self._ensure_hook_exists(hook_id)
        self.set(f"hooks.{hook_id}.{key}", value)

    def get_hook_enabled(self, hook_id: str) -> Any:
        """Check if a hook is enabled in configuration"""
        # Ensure the hook configuration exists
        self._ensure_hook_exists(hook_id)
        return self.get(f"hooks.{hook_id}.enabled", True)

    def set_hook_enabled(self, hook_id: str, enabled: bool) -> None:
        """Set whether a hook is enabled in configuration"""
        # Ensure the hook configuration exists
        self._ensure_hook_exists(hook_id)
        self.set(f"hooks.{hook_id}.enabled", enabled)

    def get_all_hook_configs(self) -> Any:
        """Get all hook configurations, excluding global settings"""
        config = self._load_config()
        hook_configs = {}

        if "hooks" in config:
            for hook_id, hook_config in config["hooks"].items():
                # Skip global settings
                if hook_id not in ["enabled", "auto_reload"]:
                    hook_configs[hook_id] = hook_config

        return hook_configs

    def _ensure_hooks_structure(self) -> None:
        """Ensure the hooks section has the proper structure"""
        config = self._load_config()

        # Ensure hooks section exists with proper structure
        if "hooks" not in config:
            config["hooks"] = {"enabled": True, "auto_reload": False}
        else:
            # Ensure required global hook settings exist
            if "enabled" not in config["hooks"]:
                config["hooks"]["enabled"] = True
            if "auto_reload" not in config["hooks"]:
                config["hooks"]["auto_reload"] = False

        self._save_config(config)

    def _ensure_hook_exists(self, hook_id: str) -> None:
        """Ensure a hook configuration section exists"""
        config = self._load_config()

        if hook_id not in config["hooks"]:
            config["hooks"][hook_id] = {"enabled": True}
            self._save_config(config)


# Singleton instance
config_manager: ConfigManager = ConfigManager()
