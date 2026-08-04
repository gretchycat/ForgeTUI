#!/usr/bin/python3
import unittest
from forgetui.widget_output import WidgetLabel, WidgetMarquee, WidgetProgressBar

class TestOutputWidgets(unittest.TestCase):
    def test_label_text_alignment(self):
        """Test WidgetLabel text alignment and vertical alignment settings."""
        lbl_left = WidgetLabel(x=0, y=0, w=20, h=1, text="Left", align='left')
        lbl_left.draw()

        lbl_center = WidgetLabel(x=0, y=0, w=20, h=3, text="Center", align='center', valign='middle')
        lbl_center.draw()

        lbl_right = WidgetLabel(x=0, y=0, w=20, h=1, text="Right", align='right')
        lbl_right.draw()

        self.assertEqual(lbl_left.text, "Left")
        self.assertEqual(lbl_center.align, 'center')
        self.assertEqual(lbl_right.align, 'right')

    def test_marquee_directions_and_shifting(self):
        """Test WidgetMarquee direction modes and text shift steps."""
        # LTR direction
        mq_ltr = WidgetMarquee(x=0, y=0, w=10, h=1, text="Hello", direction='ltr')
        mq_ltr.draw()
        mq_ltr.shift()

        # RTL direction
        mq_rtl = WidgetMarquee(x=0, y=0, w=10, h=1, text="World", direction='rtl')
        mq_rtl.draw()
        mq_rtl.shift()

        # Pingpong direction
        mq_pingpong = WidgetMarquee(x=0, y=0, w=10, h=1, text="Demo", direction='pingpong')
        mq_pingpong.draw()
        mq_pingpong.shift()

        self.assertIsNotNone(mq_ltr.text_line)
        self.assertIsNotNone(mq_rtl.text_line)
        self.assertIsNotNone(mq_pingpong.text_line)

    def test_progress_bar(self):
        """Test WidgetProgressBar progress calculation and total setting."""
        pb = WidgetProgressBar(x=0, y=0, w=20, h=1, total=100)
        self.assertEqual(pb.progress, 0)

        pb.set_progress(50)
        self.assertEqual(pb.progress, 50)

        pb.set_total(200)
        self.assertEqual(pb.total, 200)

        # Drawing progress bar renders frame buffer without exceptions
        pb.draw()

if __name__ == '__main__':
    unittest.main()
