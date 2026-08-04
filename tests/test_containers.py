#!/usr/bin/python3
import unittest
from forgetui.widget import Widget
from forgetui.widget_container import (
    WidgetBox, WidgetVBox, WidgetHBox, WidgetScrollArea,
    WidgetWindow, WidgetTabs, WidgetMatrix
)

class TestContainerWidgets(unittest.TestCase):
    def setUp(self):
        self.root = Widget(x=0, y=0, w=100, h=50, name="root")

    def test_widget_box_styles(self):
        """Test WidgetBox initialization across various border styles."""
        styles = ['line', '2line', 'curve', 'wide', 'plot', 'braille', 'octant', 'sextant', 'quadrant']
        for st in styles:
            box = WidgetBox(x=0, y=0, w=20, h=10, style=st, name=f"box_{st}")
            self.assertEqual(box.style, st)
            box.draw()

    def test_vbox_auto_layout(self):
        """Test WidgetVBox vertical stacking and minimum dimensions."""
        vbox = WidgetVBox(x=0, y=0, w=30, h=30, style='plot')
        c1 = vbox.addWidget(Widget(0, 0, w=20, h=5))
        c2 = vbox.addWidget(Widget(0, 0, w=25, h=10))

        vbox.resize()
        self.assertEqual(c1.y, 1)
        self.assertEqual(c2.y, 6)
        self.assertGreaterEqual(vbox.minW, 25)

    def test_hbox_auto_layout(self):
        """Test WidgetHBox horizontal stacking and minimum dimensions."""
        hbox = WidgetHBox(x=0, y=0, w=50, h=20, style='plot')
        c1 = hbox.addWidget(Widget(0, 0, w=15, h=5))
        c2 = hbox.addWidget(Widget(0, 0, w=20, h=5))

        hbox.resize()
        self.assertEqual(c1.x, 2)
        self.assertEqual(c2.x, 17)

    def test_scroll_area_navigation(self):
        """Test WidgetScrollArea scroll offsets and auto-scroll."""
        scroll = WidgetScrollArea(0, 0, w=20, h=10, v_bar=True, h_bar=True)
        scroll.y_can_follow = False # Disable auto-follow for fixed offset assertions
        for i in range(50):
            scroll.feed(f"Line {i}\n")

        scroll.draw()
        scroll.top()
        self.assertEqual(scroll.pos_y, 0)

        scroll.down(lines=5)
        self.assertEqual(scroll.pos_y, 5)

        scroll.up(lines=2)
        self.assertEqual(scroll.pos_y, 3)

        scroll.bottom()
        self.assertGreater(scroll.pos_y, 0)

    def test_window_drag_handlers(self):
        """Test WidgetWindow drag moving and drag resizing methods."""
        win = WidgetWindow(x=10, y=10, w=30, h=15, title="Test Window", parent=self.root)
        self.root.addWidget(win)

        event_move = {
            'action': 'drag',
            'button': 0,
            'drag start': {'x': 5, 'y': 0},
            'drag handle': 'move',
            'drag move': {'x': 5, 'y': 2}
        }
        win.drag_move(event_move)
        self.assertEqual(win.x, 15)
        self.assertEqual(win.y, 12)

        event_resize = {
            'action': 'drag',
            'button': 0,
            'drag start': {'x': win.w - 1, 'y': win.h - 1},
            'drag handle': 'resize',
            'drag move': {'x': 10, 'y': 5}
        }
        win.drag_resize(event_resize)
        self.assertEqual(win.w, 40)
        self.assertEqual(win.h, 20)

    def test_tabs_management(self):
        """Test WidgetTabs tab addition, activation, renaming, and removal."""
        tabs = WidgetTabs(0, 0, w=80, h=24)
        t1_w = Widget(0, 0, w=80, h=20, name="w1")
        t2_w = Widget(0, 0, w=80, h=20, name="w2")

        tabs.add_tab("Tab 1", hotkey="Ctrl 1", widget=t1_w)
        tabs.add_tab("Tab 2", hotkey="Ctrl 2", widget=t2_w)

        self.assertEqual(len(tabs.tab_list), 2)
        self.assertEqual(tabs.active_tab, 0)

        tabs.activate_tab(1)
        self.assertEqual(tabs.active_tab, 1)

        tabs.rename_tab(0, "New Title")
        self.assertEqual(tabs.tab_list[0]['name'], "New Title")

        success = tabs.remove_tab(1)
        self.assertTrue(success)
        self.assertEqual(len(tabs.tab_list), 1)

    def test_matrix_widget(self):
        """Test WidgetMatrix header and row grid data rendering."""
        headers = ["ID", "Name", "Score"]
        rows = [
            [1, "Alice", 95],
            [2, "Bob", 88]
        ]
        matrix = WidgetMatrix(0, 0, w=40, h=10, headers=headers, rows=rows)
        matrix.draw()

        self.assertEqual(matrix.selected_row, 0)
        self.assertEqual(matrix.selected_col, 0)

        matrix.nav_down()
        self.assertEqual(matrix.selected_row, 1)

        matrix.nav_right()
        self.assertEqual(matrix.selected_col, 1)

        matrix.nav_up()
        self.assertEqual(matrix.selected_row, 0)

        matrix.nav_left()
        self.assertEqual(matrix.selected_col, 0)

if __name__ == '__main__':
    unittest.main()
