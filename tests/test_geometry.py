#!/usr/bin/python3
import unittest
from forgetui.widget import Widget

class TestWidgetGeometry(unittest.TestCase):
    def setUp(self):
        self.root = Widget(x=0, y=0, w=100, h=50, name="root_test")

    def test_absolute_integer_geometry(self):
        """Test absolute integer positioning and dimensions."""
        w = Widget(x=10, y=5, w=30, h=15, parent=self.root)
        self.assertEqual(w.x, 10)
        self.assertEqual(w.y, 5)
        self.assertEqual(w.w, 30)
        self.assertEqual(w.h, 15)
        self.assertEqual(w.fb.width, 30)
        self.assertEqual(w.fb.height, 15)

    def test_relative_float_percentage_geometry(self):
        """Test floating point percentage dimensions relative to parent."""
        w = Widget(x=0.1, y=0.2, w=0.5, h=0.5, parent=self.root)
        # Parent dimensions are 100 x 50
        # x = 0.1 * 100 = 10
        # y = 0.2 * 50 = 10
        # w = 0.5 * 100 = 50
        # h = 0.5 * 50 = 25
        self.assertEqual(w.x, 10)
        self.assertEqual(w.y, 10)
        self.assertEqual(w.w, 50)
        self.assertEqual(w.h, 25)
        self.assertEqual(w.fb.width, 50)
        self.assertEqual(w.fb.height, 25)

    def test_negative_integer_geometry(self):
        """Test negative integer parameter handling."""
        w = Widget(x=-10, y=-5, w=-20, h=-10, parent=self.root)
        self.assertEqual(w._x, -10)
        self.assertEqual(w._y, -5)
        self.assertGreater(w.w, 0)
        self.assertGreater(w.h, 0)

    def test_string_min_geometry(self):
        """Test 'min' string geometry parameter handling."""
        w = Widget(x='min', y='min', w='min', h='min', parent=self.root)
        self.assertEqual(w.x, 0)
        self.assertEqual(w.y, 0)
        self.assertEqual(w.w, w.minW)
        self.assertEqual(w.h, w.minH)

    def test_zero_and_fallback_dimensions(self):
        """Test w=0 and h=0 fallbacks to parent dimensions."""
        w = Widget(x=0, y=0, w=0, h=0, parent=self.root)
        self.assertEqual(w.w, self.root.w)
        self.assertEqual(w.h, self.root.h)

    def test_frame_buffer_resize(self):
        """Test explicit resize() calls updating screen frame buffer."""
        w = Widget(x=0, y=0, w=20, h=10, parent=self.root)
        self.assertEqual(w.fb.width, 20)
        self.assertEqual(w.fb.height, 10)

        w.resize(40, 20)
        self.assertEqual(w.w, 40)
        self.assertEqual(w.h, 20)
        self.assertEqual(w.fb.width, 40)
        self.assertEqual(w.fb.height, 20)

    def test_move_bounds_clamping(self):
        """Test moving widget clamped inside parent boundaries."""
        self.root.addWidget(Widget(0, 0, 10, 10, name="child"))
        child = self.root.widgetList[0]

        # Move to valid coordinate
        child.move(15, 10)
        self.assertEqual(child.x, 15)
        self.assertEqual(child.y, 10)

        # Move beyond right/bottom parent edge should clamp
        child.move(200, 200)
        self.assertEqual(child.x, self.root.w - 1 - child.w)
        self.assertEqual(child.y, self.root.h - 1 - child.h)

        # Move negative coordinates should clamp to 0
        child.move(-10, -10)
        self.assertEqual(child.x, 0)
        self.assertEqual(child.y, 0)

if __name__ == '__main__':
    unittest.main()
