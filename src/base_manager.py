# ----------------------------------------------------------------
# PyLine 0.9.7 - Base Manager (GPLv3)
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# ----------------------------------------------------------------

from hook_utils import HookUtils


class BaseManager:
    """Base class for all managers with hook integration."""

    def __init__(self, hook_utils: HookUtils):
        self.hook_utils = hook_utils
