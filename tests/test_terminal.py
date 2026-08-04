#!/usr/bin/python3
import unittest, os, tempfile
from forgetui.widget_terminal import WidgetLog, WidgetTerminal

class TestTerminalWidgets(unittest.TestCase):
    def test_log_file_watching_and_rotation(self):
        """Test WidgetLog watching a local file and appending data."""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            tmp_name = tmp.name
            tmp.write("Initial log line 1\n")
            tmp.flush()

        try:
            log_widget = WidgetLog(x=0, y=0, w=40, h=10, filename=tmp_name)
            log_widget.watch_file()
            self.assertIsNotNone(log_widget.handle)

            # Append new line
            with open(tmp_name, 'a') as f:
                f.write("Log line 2\n")

            log_widget.watch_file()
            self.assertGreater(log_widget._last_size, 0)
        finally:
            if log_widget.handle:
                log_widget.handle.close()
            if os.path.exists(tmp_name):
                os.remove(tmp_name)

    def test_widget_terminal_event_queueing(self):
        """Test WidgetTerminal queue_event and get_event methods."""
        term = WidgetTerminal(x=0, y=0, w=40, h=10)
        self.assertIsNone(term.get_event())

        term.queue_event("Ctrl A")
        term.queue_event({"action": "click", "x": 5, "y": 2})

        self.assertEqual(term.get_event(), "Ctrl A")
        self.assertEqual(term.get_event(), {"action": "click", "x": 5, "y": 2})
        self.assertIsNone(term.get_event())

if __name__ == '__main__':
    unittest.main()
