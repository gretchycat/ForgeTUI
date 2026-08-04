#!/usr/bin/python3
import unittest
from forgetui.widget_input import WidgetButton, WidgetSlider

class TestInputWidgets(unittest.TestCase):
    def test_button_states_and_clicks(self):
        """Test WidgetButton active press state transitions and event callbacks."""
        clicked = False

        def click_callback():
            nonlocal clicked
            clicked = True

        btn = WidgetButton(x=0, y=0, w=15, h=3, caption="Submit")
        btn.on_click = click_callback

        # Simulate button down event inside button boundaries
        event_down = {'button': 0, 'x': 5, 'y': 1, 'action': 'button down'}
        btn.b_down(event_down)
        self.assertTrue(btn.active)
        self.assertTrue(btn.active_disp)

        # Simulate button up event
        event_up = {'button': 0, 'x': 5, 'y': 1, 'action': 'button up'}
        btn.b_up(event_up)
        self.assertFalse(btn.active)
        self.assertTrue(clicked)

        # Out-of-bounds mouse press should be ignored
        event_oob = {'button': 0, 'x': 100, 'y': 100, 'action': 'button down'}
        btn.b_down(event_oob)
        self.assertFalse(btn.active)

    def test_slider_numeric_values_and_clamping(self):
        """Test WidgetSlider numeric value setting, minimum/maximum bounds, and stepping."""
        slider = WidgetSlider(x=0, y=0, w=20, h=1, minimum=0.0, maximum=100.0, value=25.0)
        self.assertEqual(slider.value, 25.0)

        # Value within bounds
        slider.set_value(75.0)
        self.assertEqual(slider.value, 75.0)

        # Clamp above maximum
        slider.set_value(150.0)
        self.assertEqual(slider.value, 100.0)

        # Clamp below minimum
        slider.set_value(-50.0)
        self.assertEqual(slider.value, 0.0)

    def test_slider_discrete_options(self):
        """Test WidgetSlider with discrete item array."""
        discreet_options = ["Small", "Medium", "Large", "Extra Large"]
        slider = WidgetSlider(x=0, y=0, w=20, h=1, discreet=discreet_options)

        self.assertEqual(slider.min, 0)
        self.assertEqual(slider.max, len(discreet_options) - 1)
        self.assertEqual(slider.step, 1)

        slider.set_value(2)
        self.assertEqual(slider.value, 2)
        self.assertEqual(discreet_options[slider.value], "Large")

    def test_slider_keyboard_stepping(self):
        """Test WidgetSlider arrow keys and Home/End navigation."""
        slider = WidgetSlider(x=0, y=0, w=10, h=1, minimum=0.0, maximum=10.0, step=1.0, value=5.0)

        slider.right()
        self.assertEqual(slider.value, 6.0)

        slider.left()
        self.assertEqual(slider.value, 5.0)

        slider.home()
        self.assertEqual(slider.value, 0.0)

        slider.end()
        self.assertEqual(slider.value, 10.0)

    def test_slider_lock_and_unlock(self):
        """Test locking and unlocking WidgetSlider handle states."""
        slider = WidgetSlider(x=0, y=0, w=10, h=1, lock=False)
        self.assertFalse(slider.is_locked)

        slider.lock()
        self.assertTrue(slider.is_locked)

        slider.unlock()
        self.assertFalse(slider.is_locked)

if __name__ == '__main__':
    unittest.main()
