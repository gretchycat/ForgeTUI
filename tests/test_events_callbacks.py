#!/usr/bin/python3
import unittest
from forgetui.widget import Widget

class TestEventsAndCallbacks(unittest.TestCase):
    def setUp(self):
        self.root = Widget(x=0, y=0, w=100, h=50, name="root")
        self.child = Widget(x=10, y=5, w=30, h=15, name="child")
        self.child2 = Widget(x=50, y=5, w=30, h=15, name="child2")
        self.root.addWidget(self.child)
        self.root.addWidget(self.child2) # child2 now has active focus

    def test_add_event_registration(self):
        """Test registering key, mouse, and timer events."""
        dummy_func = lambda: None
        self.child.addEvent('Ctrl Q', dummy_func, persist=True)
        self.assertIn('Ctrl Q', self.child.eventList)
        self.assertTrue(self.child.eventList['Ctrl Q']['persist'])

    def test_run_callback_parameter_filtering(self):
        """Test run_callback signature inspection with various callback signatures."""
        received_self = None
        received_event = None

        def cb_sig1(self, event):
            nonlocal received_self, received_event
            received_self = self
            received_event = event

        self.child.run_callback(cb_sig1, {'self': self.child, 'event': 'Ctrl A', 'data': 'extra'})
        self.assertEqual(received_self, self.child)
        self.assertEqual(received_event, 'Ctrl A')

        called = False
        def cb_no_params():
            nonlocal called
            called = True

        self.child.run_callback(cb_no_params, {'self': self.child, 'event': 'Ctrl B', 'data': 123})
        self.assertTrue(called)

        kwargs_rec = {}
        def cb_kwargs(**kwargs):
            nonlocal kwargs_rec
            kwargs_rec = kwargs

        self.child.run_callback(cb_kwargs, {'self': self.child, 'event': 'Ctrl C', 'data': 'test'})
        self.assertEqual(kwargs_rec.get('data'), 'test')

    def test_event_persistence_and_routing(self):
        """Test persist=True vs persist=False event execution."""
        executed_non_persistent = False
        executed_persistent = False

        def handler_non_pers():
            nonlocal executed_non_persistent
            executed_non_persistent = True

        def handler_pers():
            nonlocal executed_persistent
            executed_persistent = True

        # Non-persistent event on unfocused child should not run
        self.child.addEvent('Ctrl X', handler_non_pers, persist=False)
        self.root.runEvent('Ctrl X')
        self.assertFalse(executed_non_persistent)

        # Persistent event on unfocused child should run
        self.child.addEvent('Ctrl Y', handler_pers, persist=True)
        self.root.runEvent('Ctrl Y')
        self.assertTrue(executed_persistent)

    def test_mouse_relative_event_conversion(self):
        """Test rel_event converting screen coordinates to widget relative coordinates."""
        abs_mouse_event = {'button': 0, 'x': 15, 'y': 8, 'action': 'button down'}
        rel = self.child.rel_event(abs_mouse_event)

        self.assertEqual(rel['x'], 5)
        self.assertEqual(rel['y'], 3)
        self.assertEqual(rel['abs']['x'], 15)
        self.assertEqual(rel['abs']['y'], 8)

if __name__ == '__main__':
    unittest.main()
