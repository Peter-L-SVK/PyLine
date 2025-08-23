# PyLine - Lightweight Terminal Text Editor

![PyLine Demo](scrshots/demo.png) 

PyLine is a minimalist command-line text editor designed for Linux/BSD systems, written in Python 3 with use of systems calls. Originally created in 2018 and modernized in 2025, it combines improved text management with a simple, line-by-line workflow. 
(*Note: This is a hobby project, not a professional application.*)

## Features

- **Lightweight & Fast**: Runs entirely in terminal with minimal dependencies
- **File Operations**:
  - Edit existing files
  - Create new files
  - Truncate existing files
  - Count words, lines and characters
- **Navigation**:
  - Move between lines and scroll file with arrow keys
  - Scroll file by keys PageUp and PageDown
  - Jump to end of file (Ctrl+D for EOF)
- **Editing**:
  - Line-by-line editing with syntax
  - Preserves existing text when modifying lines
  - Insert/delete line operations
  - Undo/Redo changes (history limit set to 120)
  - Multi line text selection
  - Copy and Paste text
  - Syntax highlighting for Python
- **File Browser**:
  - List directory contents
  - Change working directories
  - Make new directories
  - Remove files and directories
  - Rename files and directories
- **Hookups manager with support for custom hookups**:
  - Supports custom hookup scripts in python or perl
  - Priority Sorting: Sort hooks by priority (90 → 10)
  - Execution: Try each hook until one returns non-None
  - Comes with smart-tab indender within box
- **Cross-Platform**: Works on Linux and BSD systems

## Example screens

PyLine after the initialization:
![PyLine Init](scrshots/init-scr.png) 

Open file option screen:
![PyLine Open File](scrshots/edit-file.png)

Example of line selection:
![PyLine Copy Selected](scrshots/copy-selected.png)

After pasting the selection from clipboard:
![PyLine v-Paste Selected](scrshots/paste-lines.png)

## Installation

1st method: Manual run
```bash
git clone https://github.com/Peter-L-SVK/PyLine.git
cd PyLine/src/
chmod +x editor.py
```
2nd method (script will run sudo command):
```bash
git clone https://github.com/Peter-L-SVK/PyLine.git
cd PyLine/
./install.sh
```

## Usage

In case of manual run:
```bash
./editor.py
```

If you used install script:
```bash
pyline  #works from anywhere
```
Editor accpets input arguments:
```bash
# Edit existing file
./editor.py existing_file.txt # pyline existing_file.txt

# Create new file
./editor.py new_file.txt  # pyline new_file.txt
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

Example of how hooks can be placed:
```
~/.pyline/
├── hooks/                          # Root hooks directory
│   ├── input_handlers/             # Category: Input handling hooks
│   │   └── edit_line/              # Type: Line editing handlers
│   │       └── smart_tab__90.py     # High priority (90)
│   ├── event_handlers/             # Category: Event-based hooks
│   │   ├── on_save/                # Type: Save event handlers
│   │   │   ├── auto_formatter.py
│   │   │   ├── backup_creator.py
│   │   │   └── perl-linter.pl
│   │   ├── on_open/                # Type: Open event handlers  
│   │   │   └── file_validator.py
│   │   └── on_close/               # Type: Close event handlers
│   │       └── cleanup_hook.py
│   └── syntax_handlers/            # Category: Syntax processing hooks
│       └── highlight/              # Type: Syntax highlighting
│           ├── python_highlighter.py
│           └── javascript_highlighter.py
├── themes/                         # Themes directory (not implemented yet)
│   └── solarized.json
└── config.ini                    # Main configuration file(not implemented yet)
```

### Editor Menu

|Command|Action|
|---|---|
|`1`|Edit existing file|
|`2`|Create new file|
|`3`|Truncate existing or create new file|
|`cls`|Clear screen|
|`cw`|Count words in the file|
|`x`|Enter file management mode (exec mode)|
|`i`|Info|
|`q`|Exit program|
|`Ctrl+D`|Escape from function|
|`Ctrl+C`|Interupt the program|

### Editor Controls
|Command|Action|
|---|---|
|`↑`/`↓`|Navigate between lines / Scroll by lines|
| `PgUp` / `PgDn` | Scroll by 52 lines buffer|
|`Ctrl+B` / `F` | Undo/Redo 
|`Enter`/`e`|Edit current line|
|`i`|Insert new line|
|`d`|Delete current line or multiple selected|
|`c`|Copy current line or multiple selected|
|`v`|Paste from clipboard|
|`o`|Overwrite lines|
|`s`|Start / End of selection|
|`q`|Quit editor|
|`w`|Write changes|
|`Ctrl+D` / `End`|Jump to end of file|

### File Management Mode

|Command|Action|
|---|---|
|`af`|List all files|
|`cwd`|Change working directory|
|`cdp`|Change the default path|
|`mkdir`|Create new directory|
|`rename`|Rename a file/directory|
|`rmdir`|Remove a non empty/empty directory|
|`rmfile`|Remove a file|
|`cls`|Clear screen|
|`q`|Exit file management|
|`Ctrl+D`|Escape from function|

## Requirements

- Python 3.6+   
- Linux(or WSL)/FreeBSD/MacOS system (tested on Fedora 27 MATE, 40/42 Cinnmanon)
- Bash or Zsh shell
- Clipboard: xclip (X11) or wl-clipboard (Wayland) for copy/paste (Comes with GUI/DE)
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
