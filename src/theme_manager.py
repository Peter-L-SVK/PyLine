# ----------------------------------------------------------------
# PyLine 0.9.8 - Theme Manager (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from config import config_manager


class ThemeManager:
    def __init__(self) -> None:
        self.themes_dir = Path.home() / ".pyline" / "themes"
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        config_manager.validate_themes()
        self.current_theme = config_manager.get_theme()  # Get theme from config

    def _parse_color_code(self, color_str: str) -> str:
        """Convert string escape sequences to actual escape characters"""
        if not color_str:
            return ""

        # Replace \033 with actual escape character
        color_str = color_str.replace("\\033", "\033")
        # Replace other common escape sequences
        color_str = color_str.replace("\\x1b", "\x1b")
        color_str = color_str.replace("\\e", r"\e")
        return color_str

    def _save_theme(self, theme_name: str, theme_data: Dict[str, Any]) -> None:
        """Save theme to .theme file"""
        theme_file = self.themes_dir / f"{theme_name}.theme"
        try:
            with open(theme_file, "w") as f:
                json.dump(theme_data, f, indent=4)
                # Add to available themes in config
                config_manager.add_available_theme(theme_name)
                # Refresh the available themes list
                config_manager.refresh_available_themes()
        except IOError as e:
            print(f"Error saving theme {theme_name}: {e}")

    def _load_theme(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Load theme from .theme file"""
        theme_file = self.themes_dir / f"{theme_name}.theme"
        try:
            with open(theme_file, "r") as f:
                loaded_data = json.load(f)
                # Ensure we return the correct type
                if isinstance(loaded_data, dict):
                    return loaded_data
                else:
                    print(f"Invalid theme data format in {theme_file}")
                    return None
        except FileNotFoundError:
            print(f"Theme file not found: {theme_file}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing theme file {theme_file}: {e}")
            return None
        except IOError as e:
            print(f"Error reading theme file {theme_file}: {e}")
            return None

    def get_theme(self, theme_name: Optional[str] = None) -> Dict[str, Any]:
        """Get theme data by name (defaults to current theme)"""
        theme_name = theme_name or self.current_theme
        theme_data = self._load_theme(theme_name)

        return theme_data or {}

    def get_background_color(self, theme_name: Optional[str] = None) -> str:
        """Get the background color from the theme"""
        theme = self.get_theme(theme_name)
        bg_color = theme.get("background", "")
        return self._parse_color_code(bg_color)

    def get_color(self, color_name: str, theme_name: Optional[str] = None) -> str:
        """Get a specific color from the theme"""
        theme = self.get_theme(theme_name)
        color_value = theme.get("colors", {}).get(color_name, "\033[0m")
        return self._parse_color_code(color_value)

    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme"""
        # First refresh available themes to ensure we have the latest list
        config_manager.refresh_available_themes()

        available_themes = config_manager.get("theme.available_themes", [])

        if theme_name in available_themes:
            config_manager.set("theme.current", theme_name)
            # Also update the editor theme for backward compatibility
            config_manager.set("editor.theme", theme_name)
            self.current_theme = theme_name
            return True
        else:
            print(f"Theme '{theme_name}' is not available.\n Available themes: {', '.join(available_themes)}")
            return False

    def list_themes(self) -> List[Dict[str, Any]]:
        """List all available .theme files"""
        themes = []
        for theme_file in self.themes_dir.glob("*.theme"):
            theme_name = theme_file.stem
            theme_data = self._load_theme(theme_name)
            if theme_data:
                themes.append(
                    {
                        "name": theme_name,
                        "display_name": theme_data.get("name", theme_name),
                        "description": theme_data.get("description", "No description"),
                        "file_path": str(theme_file),
                    }
                )
            else:
                # Skip invalid theme files
                print(f"Warning: Skipping invalid theme file {theme_file}")

        return themes

    def create_theme(self, theme_name: str, base_theme: str = "black-on-white") -> bool:
        """Create a new theme based on an existing one"""
        if not theme_name.replace("-", "").replace("_", "").isalnum():
            print("Theme name can only contain letters, numbers, hyphens, and underscores")
            return False

        base_data = self.get_theme(base_theme)
        if not base_data:
            print(f"Base theme '{base_theme}' not found")
            return False

        new_theme = base_data.copy()
        new_theme["name"] = theme_name.replace("-", " ").replace("_", " ").title()
        new_theme["description"] = f"Custom theme based on {base_theme}"

        self._save_theme(theme_name, new_theme)
        print(f"Theme '{theme_name}' created successfully")
        return True

    def delete_theme(self, theme_name: str) -> bool:
        """Delete a theme file"""
        if theme_name in ["black-on-white", "white-on-black"]:
            print("Cannot delete built-in themes")
            return False

        theme_file = self.themes_dir / f"{theme_name}.theme"
        if theme_file.exists():
            try:
                theme_file.unlink()
                config_manager.remove_available_theme(theme_name)
                # Refresh the available themes list
                config_manager.refresh_available_themes()
                print(f"Theme '{theme_name}' deleted")
                return True
            except IOError as e:
                print(f"Error deleting theme: {e}")
                return False
        else:
            print(f"Theme '{theme_name}' not found")
            return False

    def edit_theme(self, theme_name: str) -> bool:
        """Open theme file for editing"""
        theme_file = self.themes_dir / f"{theme_name}.theme"
        if not theme_file.exists():
            print(f"Theme '{theme_name}' not found")
            return False

        print(f"Theme file: {theme_file}")
        print("You can edit this file with any text editor to modify the theme.")
        return True


# Singleton instance
theme_manager: ThemeManager = ThemeManager()
