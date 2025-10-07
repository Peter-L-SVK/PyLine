# PyLine - Feature Ideas and Wishlist

This document collects potential features and ideas for future PyLine development.   
Items here are not guaranteed to be implemented, but serve as a planning resource.

## Feature Ideas

---

### Implemented

- **Advanced Text Input in Edit Mode** [IMPLEMENTED]
  - Smarter handling of tabs and indentation when editing lines
  - Automatically insert spaces instead of tab characters, using 4 spaces for .py files, 2 for C/C++ files, or a custom value from config
  - Make tab width and behavior fully configurable per filetype
  - Ensure editing "feels" natural and seamless for the user, regardless of underlying tab/space logic
  - Smart indentation with language-specific rules for Python, C/C++, Java, Shell, JavaScript, Perl, HTML/XML

- **Theme Config** [IMPLEMENTED]
  - Support for user-editable theme files (JSON)
  - Allow changing syntax colors, UI colors
  - Load theme at startup or switch at runtime
  - Built-in theme manager with create/edit/delete functionality

- **Hooks/Scripts (Multi-language Support)** [IMPLEMENTED]
  - Allow user-defined scripts to be run on editor events (e.g., on_save, on_open, pre_load, post_save)
  - Support for Python 3, JavaScript, Perl 5, Ruby, Lua, PHP, Shell scripts
  - Specify hook directories (~/.pyline/hooks/) with organized structure
  - Pass file/buffer/context info to scripts via JSON stdin
  - Priority-based execution system (90 → 10)
  - Runtime enable/disable without restart

- **Predone Themes** [PARTIALLY IMPLEMENTED]
  - Ship with several built-in themes (black-on-white, white-on-black)
  - Let users choose/browse built-in themes
  - Document how to create and contribute new themes
  - Bg/fg iare still from terminal theme setting(WIP)

- **Custom Commands** [PARTIALLY IMPLEMENTED]
  - Users can define new commands/mappings in a config file [PLANNED]
  - Support macros (record/replay sequences of actions) [PLANNED]
  - Optionally allow custom commands to invoke hooks/scripts [PLANNED]
  - Extensive built-in keyboard shortcuts and commands [IMPLEMENTED]

- **Advanced Search and Navigation** [PARTIALLY IMPLEMENTED]
  - Basic search and incremental search implemented [IMPLEMENTED]
  - Literal search and replace with whole-word option
  - Regex search with capture groups and replacements [PLANNED]
  - Block selection across multiple lines [IMPLEMENTED]

---

### Planned

- **Extended Hook Language Support** [PLANNED]
  - Add Rust script support for hooks
  - Evaluate Cython support for performance-critical operations [MAYBE]
  - Maintain backward compatibility with existing hook system

- **User-Definable Keybindings** [PLANNED]
  - Allow users to customize keyboard shortcuts via config file
  - Support for command aliases and custom shortcuts
  - Maintain default keybindings as fallback

- **Performance Enhancements** [PLANNED]
  - Large file optimization for better handling of big files
  - Async operations for non-blocking file operations
  - Memory efficiency improvements

- **Integration Features** [PLANNED]
  - Version control integration (Git status, commit hooks)
  - External tool integration (linters, formatters, compilers)
  - Session management with save/restore functionality

---

## Technical Notes

### Rust Hook Support
- Would extend existing LanguageHookExecutor to support .rs files
- Use rust-script for interpretation or cargo run for compiled hooks
- Maintain same JSON context passing as other languages

### Cython Support Evaluation
- Pros: Significant performance benefits for CPU-intensive hooks
- Cons: Adds compilation dependency, more complex deployment
- Recommendation: Consider as optional advanced feature for far future

### User Commands Implementation
- Extend config.json with user_commands section
- Support for custom keybindings and macro definitions
- Backward compatibility with existing command system

---

*Based on current PyLine 1.0 implementation status*
