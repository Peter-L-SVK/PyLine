# PyLine Color Scheme Reference

## Overview
This document lists all the color codes used throughout PyLine's theme system, organized by category and usage. Includes both "Black on White" and "White on Black" themes.

## ANSI Color Code Format
- `\033[38;5;{code}m` - Set foreground color (256-color mode)
- `\033[48;5;{code}m` - Set background color (256-color mode)  
- `\033[1;{code}m` - Set bold foreground color (16-color mode)
- `\033[0m` - Reset all attributes

## Color Categories

### 1. Base Colors
| Color Name | Black on White | White on Black | Usage | Description |
|------------|----------------|----------------|-------|-------------|
| `background` | `\033[47m` | `\033[40m` | Main background | White/Black background |
| `foreground` | `\033[30m` | `\033[37m` | Main text | Black/White foreground |
| `reset` | `\033[0m` | `\033[0m` | Reset colors | Reset all attributes |

### 2. Directory Listing Colors
| Color Name | Black on White | White on Black | Usage | Description |
|------------|----------------|----------------|-------|-------------|
| `directory` | `\033[1;94m` | `\033[1;94m` | Directories | Bold bright blue |
| `executable` | `\033[38;5;28m` | `\033[38;5;82m` | Executable files | Dark/Bright green |
| `symlink` | `\033[95m` | `\033[95m` | Symbolic links | Bright magenta |

### 3. Syntax Highlighting Colors
| Color Name | Black on White | White on Black | Usage | Description |
|------------|----------------|----------------|-------|-------------|
| `keyword` | `\033[38;5;90m` | `\033[38;5;213m` | Python keywords | Dark purple/Light pink |
| `string` | `\033[38;5;28m` | `\033[38;5;118m` | String literals | Dark green/Bright green |
| `comment` | `\033[38;5;66m` | `\033[38;5;244m` | Comments | Desaturated blue/Gray |
| `variable` | `\033[38;5;27m` | `\033[38;5;111m` | Variables | Dark blue/Light blue |
| `number` | `\033[38;5;94m` | `\033[38;5;179m` | Numbers | Brown/Gold |
| `function` | `\033[38;5;130m` | `\033[38;5;214m` | Built-in functions | Orange/Bright orange |
| `class` | `\033[38;5;95m` | `\033[38;5;205m` | Class names | Dusty rose/Pink |
| `error` | `\033[38;5;124m` | `\033[38;5;196m` | Exceptions/errors | Dark red/Bright red |
| `module` | `\033[38;5;54m` | `\033[38;5;129m` | Imported modules | Purple/Bright purple |
| `decorator` | `\033[38;5;92m` | `\033[38;5;165m` | Decorators | Dark purple/Purple-pink |
| `annotation` | `\033[38;5;67m` | `\033[38;5;117m` | Type annotations | Light blue/Bright blue |

### 4. Editor UI Colors
| Color Name | Black on White | White on Black | Usage | Description |
|------------|----------------|----------------|-------|-------------|
| `current_line` | `\033[1;37m\033[47m` | `\033[1;37m\033[100m` | Current line highlight | Bold white on white/gray background |
| `selection` | `\033[1;31m` | `\033[1;91m` | Selected text | Bold red/Bright red |
| `status_bar` | `\033[1;30m\033[47m` | `\033[1;37m\033[100m` | Status bar | Bold black/white on white/gray background |
| `line_numbers` | `\033[90m` | `\033[90m` | Line numbers | Gray |

### 5. Menu and Interface Colors
| Color Name | Black on White | White on Black | Usage | Description |
|------------|----------------|----------------|-------|-------------|
| `menu_title` | `\033[1;30m` | `\033[1;37m` | Menu titles | Bold black/white |
| `menu_item` | `\033[30m` | `\033[37m` | Menu items | Black/White |
| `menu_highlight` | `\033[1;37m\033[44m` | `\033[1;37m\033[44m` | Selected menu item | Bold white on blue background |

### 6. Hook Manager Colors
| Color Name | Black on White | White on Black | Usage | Description |
|------------|----------------|----------------|-------|-------------|
| `hook_enabled` | `\033[1;32m` | `\033[1;32m` | Enabled hooks | Bold green |
| `hook_disabled` | `\033[1;31m` | `\033[1;31m` | Disabled hooks | Bold red |
| `hook_category` | `\033[1;36m` | `\033[1;36m` | Hook categories | Bold cyan |
| `hook_type` | `\033[1;33m` | `\033[1;33m` | Hook types | Bold yellow |

## Color Palette Reference

### 256-Color Mode Codes - Black on White Theme
| Color | Code | RGB Equivalent | Usage |
|-------|------|----------------|-------|
| Dark Green | 28 | #008700 | Executables, Strings |
| Dark Blue | 27 | #005fff | Variables |
| Dark Purple | 90 | #8700ff | Keywords |
| Brown | 94 | #875f00 | Numbers |
| Orange | 130 | #af5f00 | Functions |
| Dusty Rose | 95 | #875f5f | Classes |
| Dark Red | 124 | #af0000 | Errors |
| Purple | 54 | #5f005f | Modules |
| Dark Purple 2 | 92 | #8700d7 | Decorators |
| Light Blue | 67 | #5f87af | Annotations |
| Desaturated Blue | 66 | #5f8787 | Comments |

### 256-Color Mode Codes - White on Black Theme
| Color | Code | RGB Equivalent | Usage |
|-------|------|----------------|-------|
| Bright Green | 82 | #5fff00 | Executables |
| Light Pink | 213 | #ff87ff | Keywords |
| Bright Green 2 | 118 | #87ff00 | Strings |
| Gray | 244 | #808080 | Comments |
| Light Blue | 111 | #87afff | Variables |
| Gold | 179 | #d7af5f | Numbers |
| Bright Orange | 214 | #ffaf00 | Functions |
| Pink | 205 | #ff5faf | Classes |
| Bright Red | 196 | #ff0000 | Errors |
| Bright Purple | 129 | #af00ff | Modules |
| Purple-Pink | 165 | #d700ff | Decorators |
| Bright Blue | 117 | #87d7ff | Annotations |

### 16-Color Mode Codes
| Color | Code | Usage |
|-------|------|-------|
| Black | 30 | Foreground (Black on White) |
| Red | 31 | Selection (Black on White) |
| Green | 32 | Enabled hooks |
| Yellow | 33 | Hook types |
| Blue | 34 | Menu highlight background |
| Magenta | 35 | Symlinks |
| Cyan | 36 | Hook categories |
| White | 37 | Foreground (White on Black) |
| Bright Black | 90 | Line numbers |
| Bright Red | 91 | Selection (White on Black) |
| Bright Green | 92 | - |
| Bright Yellow | 93 | - |
| Bright Blue | 94 | Directories |
| Bright Magenta | 95 | Symlinks |
| Bright Cyan | 96 | - |
| Bright White | 97 | - |

## Extended Background Colors
| Background | Code | Usage |
|------------|------|-------|
| Black | 40 | Background (White on Black) |
| White | 47 | Background (Black on White) |
| Gray | 100 | Current line (White on Black) |

## Theme Files Location
Themes are stored as JSON files in: `~/.pyline/themes/`

### Example Theme Structure
```json
{
    "name": "Theme Name",
    "description": "Theme description",
    "colors": {
        "background": "\\033[40m",
        "foreground": "\\033[37m",
        "reset": "\\033[0m",
        "directory": "\\033[1;94m",
        "...": "..."
    }
}
```

## Usage in Code
Colors are accessed through the theme manager:

```python
from theme_manager import theme_manager

# Get a specific color
color = theme_manager.get_color("keyword")

# Use in text
print(f"{color}This is keyword colored text{theme_manager.get_color('reset')}")
```

## Customization
To create a custom theme:
1. Copy an existing theme file from `~/.pyline/themes/`
2. Modify the color values
3. Save with a new name (e.g., `my-theme.theme`)
4. Use the theme manager to switch themes

## Notes
- All color codes should include the reset code (`\033[0m`) after colored text
- The theme system supports both 16-color and 256-color modes
- Colors are automatically applied throughout the editor interface
- Invalid color codes will fall back to default terminal colors
---
