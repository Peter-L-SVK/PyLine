# PyLine Editor Contribution Guidelines

## Code Attribution Standards

### File Headers
All Python files must include this header format:
```python
# ----------------------------------------------------------------
# PyLine [version] - Line editor (GPLv3)
# Copyright (C) [year] [original author]
# Contributors: [name1], [name2], [name3]
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------
```

**Rules:**
1. Original author maintains first position in copyright line
2. Contributors added after `Contributors:` in order of contribution significance
3. Update version number with each major release
4. Keep GPLv3 notice unchanged

### Example with Multiple Contributors:
```python
# ----------------------------------------------------------------
# PyLine 0.7 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# Contributors: Jane Smith, John Doe, Alex Chen
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------
```

## Import Style Guide
Follow PEP 8 with these specific rules:

1. **Grouping Order:**
   ```python
   # 1. Standard library imports
   import os
   import sys
   
   # 2. Third-party imports
   import readline
   
   # 3. Local application imports
   from edit_commands import (
       DeleteLineCommand,
       EditCommand,
       MultiDeleteCommand
   )
   ```

2. **Formatting:**
   - Alphabetical order within each group
   - Parentheses for 4+ imports from same module
   - One import per line for 1-3 imports

## Commit Message Standards
```
type(scope): brief description [issue #]

[Detailed explanation if needed]
```

**Types:**
- `feat`: New functionality
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code formatting
- `refactor`: Code restructuring
- `test`: Test-related changes

**Example:**
```
feat(undo): Add atomic multi-line paste support [issue #42]

Implemented MultiPasteCommand class to ensure paste operations
are undoable as single actions. Includes tests for:
- Insert paste
- Overwrite paste
- Cross-platform clipboard handling
```
## Branching Strategy

We use a multi-branch workflow to keep development organized and stable:

- **main**: Always stable and production-ready. Only thoroughly tested changes should be merged here.
- **stage**: Used for integrating, testing, and reviewing new features before they reach `main`. Most pull requests should target this branch.
- **feat/*** (feature branches): Create a new branch from `stage` for each new feature or bugfix. Use clear, descriptive names (e.g., `feat/theme-support` or `fix/undo-history`).

### How to Contribute

1. **Update your local repository:**
   ```bash
   git checkout stage
   git pull
   ```

2. **Create a new feature branch:**
   ```bash
   git checkout -b feat/describe-feature
   ```

3. **Work on your feature or fix.**  
   Commit changes as needed.

4. **Push your branch and open a Pull Request to `stage`:**
   ```bash
   git push -u origin feat/describe-feature
   ```
   Then open a Pull Request targeting the `stage` branch.

5. **After review and testing, your changes will be merged into `stage`.**  
   Periodically, stable changes from `stage` will be merged into `main`.

6. **Delete feature branches after merging** to keep the repository tidy.

---

Please keep your changes focused and well-documented. If you have questions about the workflow, open an issue or ask in Discussions.

## Development Workflow

1. **Branch Naming:**  
   - Use one of the following prefixes for your branch names:  
     - `feat/describe-feature` (new functionality)  
     - `fix/describe-fix` (bug corrections)  
     - `docs/topic` (documentation updates)
   - Please keep branch names short and descriptive.


2. **Testing Requirements:**
   - New features require:
     - Unit tests in `tests/` directory
     - Manual verification of:
       - Undo/redo behavior
       - Cross-platform compatibility
       - Memory usage with large files

3. **Pull Requests:**
   - Must reference related issue
   - Require approval from 1 core maintainer
   - Must pass all CI tests

## Author Recognition Policy

1. **Significant Contributions:**
   - 50+ lines of meaningful code
   - Major bug fixes
   - Core feature implementations

2. **Documentation:**
   - Contributors added to:
     - File headers where they made changes
     - README.md "Contributors" section
     - Release notes

3. **How to Add Yourself:**
   ```python
   # Contributors: Original Author, New Contributor
   ```
   - Append your name alphabetically
   - Never remove existing contributors

## Code Style Enforcement

1. **Formatting:**
   - 4-space indentation
   - Lines may be up to 120 characters long. We do not enforce an 80 character limit, but please keep lines reasonably readable.
   - Google-style docstrings

2. **Tools:**
   Preconfigured in repo. For flake8 toml config: 
   
   ```sh 
   pip install flake8-pyproject 
   ```
   
   ```bash
   # Required pre-commit hooks
   flake8 --max-line-length=120 --ignore=E203,W503,E501
   black --check --diff .
   mypy --strict .
   ```

3. **Exception Cases:**
   - ANSI color codes may exceed line length
   - Import groupings may ignore alphabetical order when logical
   
   ---
