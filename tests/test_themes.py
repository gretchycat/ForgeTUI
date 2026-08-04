#!/usr/bin/python3
import unittest
from forgetui.theme import make_theme, shift_theme
from forgetui.termcontrol import termcontrol

class TestThemesAndColors(unittest.TestCase):
    def setUp(self):
        self.tc = termcontrol()

    def test_termcontrol_color_parsing(self):
        """Test color parsing for integers, hex strings, and color names."""
        # ANSI integers
        self.assertEqual(self.tc.color(5), 5)

        # Standard color names
        self.assertEqual(self.tc.color('black'), 0)
        self.assertEqual(self.tc.color('red'), 1)
        self.assertEqual(self.tc.color('green'), 2)
        self.assertEqual(self.tc.color('blue'), 4)
        self.assertEqual(self.tc.color('white'), 7)

        # Hex strings #RRGGBB
        rgb = self.tc.color('#FF5733')
        self.assertEqual(rgb['red'], 255)
        self.assertEqual(rgb['green'], 87)
        self.assertEqual(rgb['blue'], 51)

        # Short hex strings #RGB
        rgb_short = self.tc.color('#F53')
        self.assertEqual(rgb_short['red'], 255)
        self.assertEqual(rgb_short['green'], 85)
        self.assertEqual(rgb_short['blue'], 51)

    def test_make_theme_generation(self):
        """Test make_theme producing focus, off, parent, and active state dictionaries."""
        thm = make_theme(style='curve', fg='#FFFFFF', bg='#000000')
        self.assertIn('focus', thm)
        self.assertIn('off', thm)
        self.assertIn('parent', thm)
        self.assertIn('active', thm)

        focus_dict = thm['focus']
        self.assertIn('box.top_left', focus_dict)

    def test_shift_theme(self):
        """Test shift_theme HSV/RGB adjustments."""
        thm = make_theme(style='line')
        shifted = shift_theme(thm['focus'], change={'v': 0.1})
        self.assertIsNotNone(shifted)

if __name__ == '__main__':
    unittest.main()
