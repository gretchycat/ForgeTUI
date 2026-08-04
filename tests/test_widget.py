#!/usr/bin/python3
import unittest
from forgetui.widget import Widget

class TestBaseWidget(unittest.TestCase):
    def setUp(self):
        self.root = Widget(x=0, y=0, w=80, h=24, name="root")
        self.child1 = Widget(x=10, y=5, w=20, h=10, name="child1")
        self.child2 = Widget(x=0, y=0, w=10, h=5, name="child2")

    def test_add_and_remove_child(self):
        """Test adding and removing children from widget hierarchy."""
        ret = self.root.addWidget(self.child1)
        self.assertIn(self.child1, self.root.widgetList)
        self.assertEqual(self.child1.parent, self.root)
        self.assertEqual(ret, self.child1)

        success = self.root.remove_child(self.child1)
        self.assertTrue(success)
        self.assertNotIn(self.child1, self.root.widgetList)

        # Removing non-existent child returns False
        self.assertFalse(self.root.remove_child(self.child2))

    def test_root_traversal(self):
        """Test root() method traverses up to the top ancestor."""
        self.root.addWidget(self.child1)
        self.child1.addWidget(self.child2)
        self.assertEqual(self.child2.root(), self.root)
        self.assertEqual(self.child1.root(), self.root)
        self.assertEqual(self.root.root(), self.root)

    def test_get_widget_by_name(self):
        """Test searching widget tree by string name."""
        self.root.addWidget(self.child1)
        self.child1.addWidget(self.child2)

        found = self.root.get_widget_by_name("child2")
        self.assertEqual(found, self.child2)

        found_root = self.child2.get_widget_by_name("root")
        self.assertEqual(found_root, self.root)

        self.assertIsNone(self.root.get_widget_by_name("non_existent"))

    def test_focus_management(self):
        """Test set_focus and get_focused across widget tree."""
        self.root.addWidget(self.child1)
        self.root.addWidget(self.child2)

        self.child1.set_focus()
        self.assertTrue(self.child1.focus)
        self.assertEqual(self.root.get_focused(), self.child1)

        # Focus child2 should defocus child1
        self.child2.set_focus()
        self.assertTrue(self.child2.focus)
        self.assertFalse(self.child1.focus)
        self.assertEqual(self.root.get_focused(), self.child2)

    def test_hide_and_unhide(self):
        """Test hide() and unhide() visibility toggling."""
        self.root.addWidget(self.child1)
        self.child1.set_focus()

        self.child1.hide()
        self.assertTrue(self.child1.hidden)

        self.child1.unhide(focus=True)
        self.assertFalse(self.child1.hidden)
        self.assertTrue(self.child1.focus)

    def test_offset_and_coordinate_checks(self):
        """Test cumulative coordinate offset calculation."""
        self.root.addWidget(self.child1) # x=10, y=5
        self.child1.addWidget(self.child2) # x=0, y=0 inside child1

        ox, oy = self.child2.offset()
        self.assertEqual(ox, 10)
        self.assertEqual(oy, 5)

        self.assertTrue(self.child1.coordinate_in_widget(15, 8))
        self.assertFalse(self.child1.coordinate_in_widget(5, 2))

        widgets_at = self.root.widgets_at_coordinate(15, 8)
        self.assertIn(self.child1, widgets_at)
        self.assertIn(self.child2, widgets_at)

    def test_feed_and_clear(self):
        """Test writing string content to frame buffer."""
        w = Widget(x=0, y=0, w=20, h=5)
        w.feed("Hello World")
        self.assertTrue(w.dirty)

        w.clear()
        self.assertTrue(w.dirty)

    def test_set_colors_supported_types(self):
        """Test setColors with ANSI integers, names, and hex strings."""
        w = Widget(x=0, y=0, w=10, h=5)

        # ANSI 16 integers
        w.setColors(7, 0)
        self.assertEqual(w.fg, 7)
        self.assertEqual(w.bg, 0)

        # Color names / strings
        w.setColors('red', 'blue')
        self.assertEqual(w.fg, 'red')
        self.assertEqual(w.bg, 'blue')

        # Hex strings
        w.setColors('#FF0000', '#0000FF')
        self.assertEqual(w.fg, '#FF0000')
        self.assertEqual(w.bg, '#0000FF')

if __name__ == '__main__':
    unittest.main()
