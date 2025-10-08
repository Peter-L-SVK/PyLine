# PyLine - Lightweight Terminal Text Editor

![PyLine Demo](scrshots/demo.png) 

PyLine is a minimalist command-line text editor designed for Linux/BSD systems, written in Python 3 with use of systems calls. Originally created in 2018 and modernized after long pause in 2025, it combines improved text management with a simple, line-by-line workflow. 
(*Note: This is a hobby project, not a professional application.*)

## Features
- **Theme System**: 
  - Customizable color schemes with only coloring syntax and listing, adjustable for dark and light themes
  - basic text and bacground still from terminal theme (for now)
  - Inhouse solution for editing themes in theme manager
- **Configuration Management**: 
  - Persistent settings with JSON-based configuration
  - Run time config modifying and checking
- **Lightweight & Fast**: Runs entirely in terminal with minimal dependencies
- **Advanced Hook System**: 
  - Extensible plugin architecture with support for multiple languages (Python, JavaScript, Perl, Ruby, Lua, PHP, Shell)
  - Fully interconnected Hook manager with Config manager
  - Incudes core hook utils for search and replace, smart tab, shell syntax highligting and more
- **File Operations**:
  - Edit existing files with full hook integration
  - Create new files with directory structure creation
  - Truncate existing files
  - Count words, lines and characters with hookable word counting
- **Navigation**:
  - Move between lines and scroll file with arrow keys
  - Scroll file by keys PageUp and PageDown
  - Jump to specified line number by J
  - Jump to end of file (Ctrl+D for EOF)
  - Smart viewport management
  - Stylized helpscreen
  - Search and replace functionality provided by core util hook
- **Editing**:
  - Line-by-line editing with hook-integrated input handling
  - Preserves existing text when modifying lines
  - Insert/delete line operations with pre/post hooks
  - Comprehensive Undo/Redo system (history limit set to 120)
  - Multi-line text selection with visual indicators
  - Cross-platform clipboard support (X11, Wayland, macOS, Windows)
  - Smart indentation preservation during paste operations
  - Syntax highlighting for Python with advanced token recognition
  - Aditional syntax highlighting for shells and JSON via core hooks
- **File Browser**:
  - Colorized directory listings
  - Change working directories with path persistence
  - Make new directories
  - Remove files and directories
  - Rename files and directories
- **Hook Management**:
  - Visual hook manager interface (`hm` command)
  - Priority-based hook execution (90 → 10)
  - Runtime enable/disable without restart
  - Support for multiple scripting languages
  - Hook categories: input handlers, event handlers, syntax handlers, editing operations, clipboard operations, session handlers

## Example screens

Complete screenshot example galery in [screenshot-gallery](https://github.com/Peter-L-SVK/PyLine/blob/main/scrshots/README.md)

PyLine after the initialization:  
![PyLine Init](scrshots/init-scr.png) 

Open file option screen:  
![PyLine Open File](scrshots/edit-file.png)

Example of line selection:  
![PyLine Copy Selected](scrshots/copy-selected.png)

After pasting the selection from clipboard:
![PyLine v-Paste Selected](scrshots/paste-lines.png)

Editing  text:  
![Text Editing2](scrshots/editing.png)

Execmode(Filemanager):  
![PyLine Execmode](scrshots/exec.png)
  
Hook manager:  
![PyLine Hm](scrshots/hook-mgr.png)
  
![PyLine Hm-ls](scrshots/hook-mgr-ls.png)
  
![PyLine Hm-ls-list](scrshots/hook-mgr-ls2.png)

## Installation

1st method: Manual run
```bash
git clone https://github.com/Peter-L-SVK/PyLine.git
cd PyLine/src/
chmod +x main.py
#Run pwd and copy result path
pwd
#add to your shell config file to run from everywhere
alias pyline='<result of pwd>/main.py'
#run separate install-all.sh in hooks directory
../hooks/install-all.sh
#copy themes to editor's config directory
cp -r $(pwd)/../themes ~/.pyline/
#restart terminal
```
2nd method (script will run sudo command):
```bash
git clone https://github.com/Peter-L-SVK/PyLine.git
cd PyLine/
./install.sh
```

## Configuration

PyLine stores configuration in `~/.pyline/config.json` with the following structure:

```json
{
    "paths": {
		"source_path": "/home/<path-to-pyline>/PyLine/src"
        "original_path": "<current_path_in_terminal>"
		"default_path": "/home/<username>",
    },
    "editor": {
        "theme": "black-on-white"
    },
    "hooks": {
        "enabled": true,
        "auto_reload": false
    },
    "theme": {
        "current": "black-on-white",
        "available_themes": [
            "black-on-white",
            "white-on-black"
        ]
    }
}
```

## Detailed Structure

### 1. Root Directory (`~/.pyline/`)
```
~/.pyline/
├── config.json          # Main JSON configuration
├── themes/              # Color theme definitions
└── hooks/               # Extension hook system
```

## Usage

In case of manual run:
```bash
./main.py
```

If you used install script:
```bash
pyline  #works from anywhere
```
Editor accpets input arguments:
```bash
# Edit existing file
./main.py existing_file.txt # pyline existing_file.txt

# Create new file
./main.py new_file.txt  # pyline new_file.txt
```

The editor will:
1. For existing files:
   - Load the file
   - Enter edit mode immediately
2. For new files:
   - Create new buffer with specified filename
   - Create new directory in file path if doesn't exist already
   - Enter edit mode
3. With no arguments:
   - Show the original interactive menu

4. -i, --info   Show program information and exit

5. -h, --help   show help message and exit

To unninstall the program:
```bash
./install.sh -u
```
## Core Hook System Structure with all possible features and hooks in mind
**Advanced Hook System**

More about hooks in: [hooks-creation](https://github.com/Peter-L-SVK/PyLine/blob/main/hooks/hooks-creation.md) and [hooks-overview](https://github.com/Peter-L-SVK/PyLine/blob/main/hooks/hooks-overview.md)  
Manual on how to perform various types of search and replace within core hook in [serach-replace manual](https://github.com/Peter-L-SVK/PyLine/blob/main/hooks/search_replace/readme.md)  
  
PyLine features a comprehensive hook system that allows extending functionality through plugins. The hook system supports multiple programming languages and follows a structured directory hierarchy:

```
~/.pyline/hooks/
├── input_handlers/           # Input processing hooks
│   └── edit_line/           # Line editing handlers
│       ├── smart_tab__90.py  # Priority 90 (high)
│       └── auto_complete.py
├── event_handlers/           # Event-based hooks  
│   ├── pre_save/            # Before saving
│   ├── post_save/           # After saving
│   ├── pre_load/            # Before loading
│   ├── post_load/           # After loading
│   └── on_error/            # Error handling
├── syntax_handlers/         # Syntax processing
│   ├── highlight/           # Syntax highlighting
│   └── lint/               # Code linting
├── editing_ops/            # Editing operations
│   ├── pre_insert/         # Before line insertion
│   ├── post_insert/        # After line insertion  
│   ├── pre_delete/         # Before line deletion
│   └── post_delete/        # After line deletion
├── clipboard_ops/          # Clipboard operations
│   ├── pre_copy/           # Before copying
│   ├── post_copy/          # After copying
│   ├── pre_paste/          # Before pasting
│   └── post_paste/         # After pasting
└── session_handlers/       # Session management
    ├── pre_edit/          # Before editing session
    └── post_edit/         # After editing session
```
## Theme System

### Built-in Themes

- **black-on-white**: Classic black text on white background
- **white-on-black**: White text on black background (dark mode)

### Custom Themes

Create custom themes in `~/.pyline/themes/`:

More about themes in: [themes-reference](https://github.com/Peter-L-SVK/PyLine/blob/main/themes/ColorReference.md)

```bash
# Create a new theme based on existing one
pyline
# Then type 'tm' for theme manager
# Then 'create my-theme' to create a new theme
```

Theme file structure (`~/.pyline/themes/my-theme.json`):
```json
{
  "name": "My Custom Theme",
  "description": "A custom color scheme",
  "background": "\\033[48;5;COLORm",
  "setterm_background": "color-name",
  "setterm_foreground": "color-name",
  "colors": {
    "reset": "\\033[0m",
    "menu_title": "\\033[1;30m",
    "menu_item": "\\033[34m",
    "line_numbers": "\\033[90m",
    "selection": "\\033[47m\\033[30m",
    "keyword": "\\033[34m",
    "string": "\\033[31m",
    "comment": "\\033[32m",
    "variable": "\\033[33m",
    "number": "\\033[35m",
    "function": "\\033[36m",
    "class": "\\033[1;35m",
    "error": "\\033[1;31m",
    "module": "\\033[1;34m",
    "decorator": "\\033[1;36m",
    "annotation": "\\033[1;33m",
    "directory": "\\033[1;34m",
    "executable": "\\033[1;32m",
    "symlink": "\\033[1;36m",
    "hook_category": "\\033[1;35m",
    "hook_type": "\\033[1;36m",
    "hook_enabled": "\\033[1;32m",
    "hook_disabled": "\\033[1;31m"
  }
}
```

### Editor Menu

|Command|Action|
|---|---|
|`1`|Edit existing file|
|`2`|Create new file|
|`3`|Truncate existing or create new file|
|`cls`|Clear screen|
|`cw`|Count words in the file|
|`hm`|Hook manager|
|`hs`|Hook status|
|`tm`|Theme manager|
|`x`|Enter file management mode (exec mode)|
|`i`|Info|
|`q`|Exit program|
|`Ctrl+D`|Escape from function|
|`Ctrl+C`|Interupt the program|

### Hook Management Commands

| Command | Action |
|---|---|
| `hm` | Enter hook manager interface |
| `ls` | List all available hooks |
| `info` | Show detailed hook information |
| `enable` | Enable a specific hook |
| `disable` | Disable a specific hook |
| `reload` | Reload hook system from filesystem |

### Editor Controls

|Command|Action|
|---|---|
|`↑`/`↓`|Navigate between lines / Scroll by lines|
|`PgUp` / `PgDn`|Scroll by 52 lines buffer|
|`Ctrl+B` / `F`|Undo/Redo|
|`Ctrl+D` / `End`|Jump to end of the file|
|`Ctrl+Alt+f`|Search for text|
|`Ctrl+Alt+r`|Search and replace|
|`c`|Copy current line or multiple selected|
|`d`|Delete current line or multiple selected|
|`Enter`/`e`|Edit current line|
|`h`|Help screen|
|`Home`|Jump to beginning of the file|
|`i`|Insert new line|
|`j`|Jump to user specified line|
|`v`|Paste from clipboard|
|`o`|Overwrite lines|
|`s`|Start / End of selection|
|`q` /`Esc`|Quit editor|
|`w`|Write/save changes|

### File Management Mode

| Command   | Action                               |
|-----------|--------------------------------------|
| `af`      | List all files                       |
| `cwd`     | Change working directory             |
| `cdp`     | Change the default path              |
| `mkdir`   | Create new directory                 |
| `rename`  | Rename a file/directory              |
| `rmdir`   | Remove a non empty/empty directory   |
| `rmfile`  | Remove a file                        |
| `cls`     | Clear screen                         |
| `q`       | Exit file management                 |
| `Ctrl+D`  | Escape from function                 |

### Theme Manager Commands

| Command | Action |
|---------|--------|
| `tm` | Enter theme manager |
| `ls` | List all available themes |
| `use <theme>` | Switch to specified theme |
| `info <theme>` | Show theme details |
| `create <name>` | Create new theme based on current |
| `delete <name>` | Delete a theme (cannot delete built-in) |
| `edit <name>` | Show theme file location for editing |


## Requirements

- **Hook Language Support**:
  - Python: Built-in
  - JavaScript: `node` runtime
  - Perl: `perl` interpreter
  - Ruby: `ruby` interpreter
  - Lua: `lua` interpreter
  - PHP: `php` interpreter
  - Shell: `bash` or `zsh` interpreter
- Python 3.6+   
- Linux(or WSL)/FreeBSD/MacOS system (tested on Fedora 27 MATE, 40/42 Cinnmanon)
- Bash or Zsh shell
- Clipboard: xclip (X11) or wl-clipboard (Wayland) for copy/paste (Comes with GUI/DE)

## Known Limitations

- **Forground Colors**: Only partialy applied for now, when editor colors the syntax of when listing.
- **Background Colors**: For now not implemeted but counted for in themes and code.

## License

GNU GPL v3 - See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html) file for details.

## Testing

To run all tests:

```bash
cd PyLine/tests/
python -m unittest discover
```

Or run a specific test file:

```bash
python -m unittest test_dirops.py
```

All tests require only Python’s built-in `unittest` module.

## Contributing

Contributions are welcome!  
See [CONTRIBUTING](https://github.com/Peter-L-SVK/PyLine/blob/main/CONTRIBUTING.md) file for details.  

For contact please see my email in profile info or use GitHub’s built-in communication tools.

Please open an issue or pull request for any:  

- Bug fixes
    
- Feature suggestions
    
- Documentation improvements
    

---

_Created by Peter Leukanič in 2018 - A simple editor for when you need to edit text files quickly without leaving the terminal._
