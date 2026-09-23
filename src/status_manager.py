# ----------------------------------------------------------------
# PyLine 1.2 - Status Manager (GPLv3)
# Copyright (C) 2025-2026 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# Feel free to distribute and modify.
# ----------------------------------------------------------------

import time
import threading
from typing import Optional, List, Callable


class StatusManager:
    """Manages status messages with timed display and auto-dismiss.

    Uses a dedicated render lock so that:
      - The timer thread can safely request a redraw when the message
        expires (Option B behaviour).
      - The main thread, while it is inside raw-mode key reading, can
        take the same lock to prevent the timer thread from writing
        to the terminal at the wrong moment.
    """

    def __init__(self):
        self.current_message: Optional[str] = None
        self.message_timer: Optional[threading.Timer] = None
        self.message_queue: List[str] = []
        self.display_duration = 3.0  # seconds

        # Lazy theme manager (kept from original)
        self._theme_manager = None
        self._theme_lock = threading.Lock()

        # Callback to request an editor redraw
        self._refresh_callback: Optional[Callable[[], None]] = None

        # Render lock — held while the terminal is being written to.
        # The main thread holds this while in raw mode; the timer thread
        # acquires it before calling _safe_display().
        self._render_lock = threading.RLock()

        # Guard access to current_message / message_timer
        self._state_lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Theme manager (unchanged)
    # ------------------------------------------------------------------ #
    def _get_theme_manager(self):
        """Thread-safe lazy load theme manager to avoid circular imports"""
        if self._theme_manager is None:
            with self._theme_lock:
                if self._theme_manager is None:
                    try:
                        from theme_manager import theme_manager

                        self._theme_manager = theme_manager
                    except ImportError:

                        class DummyTheme:
                            def get_color(self, name, default=None):
                                return default or ""

                        self._theme_manager = DummyTheme()
        return self._theme_manager

    # ------------------------------------------------------------------ #
    # Refresh callback plumbing
    # ------------------------------------------------------------------ #
    def set_refresh_callback(self, callback: Callable[[], None]) -> None:
        """Set callback to refresh display when status changes"""
        self._refresh_callback = callback

    def _safe_display(self) -> None:
        """Trigger display refresh safely, holding the render lock."""
        if not self._refresh_callback:
            return
        with self._render_lock:
            try:
                self._refresh_callback()
            except Exception:
                # Never let a status refresh crash the editor
                pass

    # ------------------------------------------------------------------ #
    # Render-lock helpers — called by the editor while in raw mode
    # ------------------------------------------------------------------ #
    def acquire_render_lock(self) -> None:
        """Called by the editor before entering raw-mode key reading."""
        self._render_lock.acquire()

    def release_render_lock(self) -> None:
        """Called by the editor after leaving raw-mode key reading."""
        try:
            self._render_lock.release()
        except RuntimeError:
            pass  # already released

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def show_message(
        self,
        message: str,
        duration: Optional[float] = None,
        refresh: bool = True,
    ) -> None:
        """Show a status message for the specified duration.

        Args:
            message:  The text to display.
            duration: Seconds to keep the message (default = display_duration).
            refresh:  Whether to redraw the editor immediately.
        """
        if duration is None:
            duration = self.display_duration

        # Cancel any existing timer
        with self._state_lock:
            if self.message_timer and self.message_timer.is_alive():
                self.message_timer.cancel()
            self.current_message = message

        # Immediate redraw (main thread) — safe because we're in normal
        # (non-raw) mode when show_message is called from editing code.
        if refresh:
            self._safe_display()

        # Schedule clear. Option B: the timer thread IS allowed to refresh.
        timer = threading.Timer(duration, self._timed_clear)
        timer.daemon = True
        with self._state_lock:
            self.message_timer = timer
        timer.start()

    def _timed_clear(self) -> None:
        """Runs on the timer thread: clear message, then redraw safely."""
        with self._state_lock:
            self.current_message = None
            self.message_timer = None

        # Option B: redraw from timer thread, guarded by render lock.
        # If the main thread is currently in raw mode, this will block
        # until the key reader releases the lock — which is exactly
        # what we want.
        self._safe_display()

    def clear_message(self, refresh: bool = True) -> None:
        """Clear the current status message.

        Kept for API compatibility. When refresh=True, the caller's
        thread performs the redraw (guarded by the render lock).
        """
        with self._state_lock:
            self.current_message = None
            if self.message_timer and self.message_timer.is_alive():
                self.message_timer.cancel()
            self.message_timer = None

        if refresh:
            self._safe_display()

    # ------------------------------------------------------------------ #
    # Status bar rendering
    # ------------------------------------------------------------------ #
    def get_status_bar(self, width: int = 115) -> str:
        """Get formatted status bar content"""
        with self._state_lock:
            msg = self.current_message

        if not msg:
            return " " * width

        max_content_width = width
        if len(msg) > max_content_width:
            msg = msg[: max_content_width - 3] + "..."

        padding_needed = width - len(msg)
        if padding_needed <= 0:
            return msg

        left_padding = padding_needed // 2
        right_padding = padding_needed - left_padding
        return " " * left_padding + msg + " " * right_padding


# Global status manager instance
status_manager = StatusManager()
