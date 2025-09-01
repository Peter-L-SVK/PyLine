#----------------------------------------------------------------
# PyLine 0.9.7 - Selection Manager (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

from typing import Optional, Tuple, List, Dict, Any
from base_manager import BaseManager

class SelectionManager(BaseManager):
    """Manages text selection operations with hook integration."""
    
    def __init__(self, hook_utils):
        super().__init__(hook_utils)
        self.selection_start: Optional[int] = None
        self.selection_end: Optional[int] = None
        self.in_selection_mode: bool = False
    
    def start_selection(self, line_number: int, filename: str = None) -> None:
        """Begin selection at line number with hooks."""
        # Pre-selection hooks
        pre_select_context = {
            'line_number': line_number,
            'filename': filename,
            'action': 'pre_selection_start',
            'operation': 'selection'
        }
        pre_select_result = self.hook_utils.execute_editing_handlers('pre_selection', pre_select_context)
        
        if pre_select_result and 'cancel' in pre_select_result:
            return  # Selection cancelled
        
        self.selection_start = line_number
        self.in_selection_mode = True
        
        # Post-selection hooks
        post_select_context = {
            'line_number': line_number,
            'filename': filename,
            'action': 'post_selection_start',
            'operation': 'selection'
        }
        self.hook_utils.execute_editing_handlers('post_selection', post_select_context)
    
    def end_selection(self, line_number: int, filename: str = None) -> None:
        """End selection at line number with hooks."""
        if not self.in_selection_mode:
            return
        
        # Pre-selection-end hooks
        pre_end_context = {
            'start_line': self.selection_start,
            'end_line': line_number,
            'filename': filename,
            'action': 'pre_selection_end',
            'operation': 'selection'
        }
        pre_end_result = self.hook_utils.execute_editing_handlers('pre_selection', pre_end_context)
        
        if pre_end_result and 'cancel' in pre_end_result:
            return  # Selection end cancelled
        
        self.selection_end = line_number
        if self.selection_start > self.selection_end:
            self.selection_start, self.selection_end = self.selection_end, self.selection_start
        
        # Post-selection-end hooks
        post_end_context = {
            'start_line': self.selection_start,
            'end_line': self.selection_end,
            'filename': filename,
            'action': 'post_selection_end',
            'operation': 'selection'
        }
        self.hook_utils.execute_editing_handlers('post_selection', post_end_context)
    
    def get_selected_text(self, lines: List[str], filename: str = None) -> str:
        """Get selected text with hook integration."""
        range = self.get_selection_range()
        if not range:
            return ""
        
        start, end = range
        selected_lines = lines[start:end+1]
        selected_text = '\n'.join(selected_lines)
        
        # Process selected text through hooks
        selection_context = {
            'start_line': start,
            'end_line': end,
            'text': selected_text,
            'filename': filename,
            'action': 'process_selection',
            'operation': 'selection'
        }
        selection_result = self.hook_utils.execute_clipboard_handlers('process_selection', selection_context)
        
        if selection_result and 'text' in selection_result:
            return selection_result['text']
        
        return selected_text
    
    def get_selection_range(self) -> Optional[Tuple[int, int]]:
        """Get selection range as (start, end)."""
        if self.selection_start is not None and self.selection_end is not None:
            return (min(self.selection_start, self.selection_end),
                   max(self.selection_start, self.selection_end))
        return None
    
    def get_selected_lines(self, lines: List[str]) -> List[str]:
        """Get selected lines from buffer."""
        range = self.get_selection_range()
        if range:
            start, end = range
            return lines[start:end+1]
        return []
    
    def has_selection(self) -> bool:
        """Check if there's an active selection."""
        return self.selection_start is not None and self.selection_end is not None
    
    def is_in_selection_mode(self) -> bool:
        """Check if in selection mode."""
        return self.in_selection_mode
    
    def clear_selection(self) -> None:
        """Clear current selection."""
        self.selection_start = None
        self.selection_end = None
        self.in_selection_mode = False
