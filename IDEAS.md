# PyLine - Feature Ideas and Wishlist

This document collects potential features and ideas for future PyLine development.   
Items here are not guaranteed to be implemented, but serve as a planning resource.

---

## Feature Ideas

- **Advanced Text Input in Edit Mode**
  - Smarter handling of tabs and indentation when editing lines
  - Automatically insert spaces instead of tab characters, using 4 spaces for `.py` files, 2 for C/C++ files, or a custom value from config
  - Make tab width and behavior fully configurable per filetype
  - Ensure editing “feels” natural and seamless for the user, regardless of underlying tab/space logic

- **Theme Config**
  - Support for user-editable theme files (JSON/YAML/INI)
  - Allow changing syntax colors, UI colors, keybindings
  - Load theme at startup or switch at runtime

- **Hooks/Scripts (Python 3 & Perl 5)**
  - Allow user-defined scripts to be run on editor events (e.g., on_save, on_open)
  - Support both Python 3 and Perl 5 for hooks
  - Specify hook directories (e.g., `~/.pyline/hooks/`)
  - Pass file/buffer/context info to scripts via env or stdin

- **Custom Commands**
  - Users can define new commands/mappings in a config file
  - Support macros (record/replay sequences of actions)
  - Optionally allow custom commands to invoke hooks/scripts

- **Predone Themes**
  - Ship with several built-in themes (e.g., black on white, white on black, solarized, high-contrast)
  - Let users choose/browse built-in themes
  - Document how to create and contribute new themes

---
