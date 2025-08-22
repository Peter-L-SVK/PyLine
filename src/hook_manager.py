#----------------------------------------------------------------
# PyLine 0.9 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

import os
import importlib.util
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

class HookManager:
    def __init__(self):
        self.hooks_dir = Path.home() / ".pyline" / "hooks"
        self.hooks_dir.mkdir(parents=True, exist_ok=True)
    
    def has_hooks(self, hook_category: str, hook_type: str = None) -> bool:
        """Check if any hooks exist for a category/type"""
        if hook_type:
            hook_dir = self.hooks_dir / hook_category / hook_type
        else:
            hook_dir = self.hooks_dir / hook_category
        
        return hook_dir.exists() and any(hook_dir.iterdir())
    
    def execute_hooks(self, hook_category: str, hook_type: str, context: Dict[str, Any]) -> Optional[Any]:
        """
        Execute all hooks in a category/type and return the first non-None result
        """
        hook_dir = self.hooks_dir / hook_category / hook_type
        if not hook_dir.exists():
            return None
            
        for hook_file in self._get_sorted_hooks(hook_dir):
            try:
                result = self._execute_hook(hook_file, context)
                if result is not None:
                    return result
            except Exception as e:
                print(f"Hook {hook_file.name} failed: {e}")
        
        return None
    
    def execute_all_hooks(self, hook_category: str, hook_type: str, context: Dict[str, Any]) -> List[Any]:
        """
        Execute all hooks in a category/type and return all results
        """
        hook_dir = self.hooks_dir / hook_category / hook_type
        if not hook_dir.exists():
            return []
            
        results = []
        for hook_file in self._get_sorted_hooks(hook_dir):
            try:
                result = self._execute_hook(hook_file, context)
                if result is not None:
                    results.append(result)
            except Exception as e:
                print(f"Hook {hook_file.name} failed: {e}")
        
        return results
    
    def _get_sorted_hooks(self, hook_dir: Path) -> List[Path]:
        """Get hooks sorted by priority (filename__priority.py) or alphabetically"""
        hooks = []
        for hook_file in hook_dir.iterdir():
            if hook_file.is_file() and hook_file.suffix == '.py':
                priority = self._get_hook_priority(hook_file)
                hooks.append((priority, hook_file))
        
        # Sort by priority (higher first), then by filename
        hooks.sort(key=lambda x: (-x[0], x[1].name))
        return [hook_file for priority, hook_file in hooks]
    
    def _get_hook_priority(self, hook_file: Path) -> int:
        """Extract priority from filename (e.g., handler__99.py -> priority 99)"""
        name = hook_file.stem
        if '__' in name:
            try:
                return int(name.split('__')[-1])
            except ValueError:
                pass
        return 50  # Default priority
    
    def _execute_hook(self, hook_file: Path, context: Dict[str, Any]) -> Optional[Any]:
        """Execute a single hook file"""
        spec = importlib.util.spec_from_file_location(hook_file.stem, hook_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[hook_file.stem] = module
        spec.loader.exec_module(module)
        
        # Look for standard hook function
        if hasattr(module, 'handle_input'):
            return module.handle_input(context)
        
        # Alternative function names
        if hasattr(module, 'main'):
            return module.main(context)
        
        if hasattr(module, 'execute'):
            return module.execute(context)
        
        return None
    
    def list_hooks(self, hook_category: str = None, hook_type: str = None) -> List[Path]:
        """List available hooks"""
        if hook_category and hook_type:
            hook_dir = self.hooks_dir / hook_category / hook_type
            return list(hook_dir.iterdir()) if hook_dir.exists() else []
        elif hook_category:
            hook_dir = self.hooks_dir / hook_category
            return list(hook_dir.iterdir()) if hook_dir.exists() else []
        return list(self.hooks_dir.iterdir())
