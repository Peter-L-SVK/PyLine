import sys
import os
import time
import threading
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from status_manager import StatusManager


class TestStatusManager(unittest.TestCase):
    def setUp(self):
        # Fresh instance per test, not the global singleton
        self.sm = StatusManager()
        self.sm.display_duration = 0.15  # shorter for tests

    def test_initial_state_is_empty(self):
        self.assertIsNone(self.sm.current_message)
        self.assertIsNone(self.sm.message_timer)

    def test_show_message_sets_current(self):
        self.sm.show_message("hello")
        self.assertEqual(self.sm.current_message, "hello")

    def test_show_message_calls_refresh_callback(self):
        callback = MagicMock()
        self.sm.set_refresh_callback(callback)
        self.sm.show_message("hello")
        callback.assert_called_once()

    def test_show_message_with_refresh_false_skips_callback(self):
        callback = MagicMock()
        self.sm.set_refresh_callback(callback)
        self.sm.show_message("hello", refresh=False)
        callback.assert_not_called()

    def test_message_auto_clears_after_duration(self):
        self.sm.show_message("bye", duration=0.1)
        self.assertEqual(self.sm.current_message, "bye")
        time.sleep(0.25)
        self.assertIsNone(self.sm.current_message)

    def test_new_message_cancels_previous_timer(self):
        self.sm.show_message("first", duration=5.0)
        self.sm.show_message("second", duration=0.1)
        self.assertEqual(self.sm.current_message, "second")
        time.sleep(0.25)
        # "first" timer must not have fired (would have cleared to None early)
        self.assertIsNone(self.sm.current_message)

    def test_clear_message_immediately(self):
        self.sm.show_message("temporary", duration=10.0)
        self.sm.clear_message(refresh=False)
        self.assertIsNone(self.sm.current_message)
        self.assertIsNone(self.sm.message_timer)

    def test_get_status_bar_empty(self):
        bar = self.sm.get_status_bar(width=20)
        self.assertEqual(bar, " " * 20)

    def test_get_status_bar_centers_message(self):
        self.sm.show_message("hi", refresh=False)
        bar = self.sm.get_status_bar(width=10)
        self.assertEqual(len(bar), 10)
        self.assertIn("hi", bar)
        # message should be roughly centered
        left = bar.index("hi")
        right = len(bar) - (left + len("hi"))
        self.assertLessEqual(abs(left - right), 1)

    def test_get_status_bar_truncates_long_message(self):
        self.sm.show_message("x" * 200, refresh=False)
        bar = self.sm.get_status_bar(width=20)
        self.assertEqual(len(bar), 20)
        self.assertTrue(bar.strip().endswith("..."))

    def test_render_lock_acquire_release(self):
        # Should not deadlock
        self.sm.acquire_render_lock()
        self.sm.release_render_lock()

    def test_render_lock_is_reentrant(self):
        # RLock: same thread can acquire twice
        self.sm.acquire_render_lock()
        self.sm.acquire_render_lock()
        self.sm.release_render_lock()
        self.sm.release_render_lock()

    def test_timer_thread_blocks_on_render_lock(self):
        """While render lock is held, timer-thread redraw must wait."""
        order = []

        def callback():
            order.append("callback")

        self.sm.set_refresh_callback(callback)
        self.sm.display_duration = 0.05

        # Hold the render lock like edit_interactive does
        self.sm.acquire_render_lock()
        try:
            self.sm.show_message("x", duration=0.05, refresh=False)
            # Give timer a chance to fire
            time.sleep(0.2)
            # Callback should NOT have run yet because lock is held
            # (only the initial show_message(false) skipped it, timer is blocked)
            self.assertEqual(order, [])
        finally:
            self.sm.release_render_lock()

        # After releasing, the timer thread should eventually run the callback
        time.sleep(0.2)
        self.assertEqual(order, ["callback"])


class TestStatusManagerConcurrency(unittest.TestCase):
    def test_many_messages_no_crash(self):
        sm = StatusManager()
        sm.display_duration = 0.02
        sm.set_refresh_callback(lambda: None)

        for i in range(50):
            sm.show_message(f"msg {i}")
        time.sleep(0.3)
        self.assertIsNone(sm.current_message)


if __name__ == "__main__":
    unittest.main()
