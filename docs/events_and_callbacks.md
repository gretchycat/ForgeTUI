# Events and Callback Functions

ForgeTUI features a powerful, reactive event dispatching system that routes keyboard, mouse, timer, and system triggers to registered callback functions.

---

## 1. Registering Events

To attach an event handler to a widget, call `addEvent()`:

```python
widget.addEvent(trigger, func, persist=False, target='__focus__', data=None)
```

### Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| **`trigger`** | `str \| float` | Key sequence string, mouse action name, timer float, or `''` for catch-all. |
| **`func`** | `callable` | Function, method, or callable object to execute when the trigger fires. |
| **`persist`** | `bool` | If `True`, the event fires regardless of whether the widget currently holds focus. Defaults to `False`. |
| **`target`** | `str \| Widget` | Target widget for focus routing (`'__focus__'`, widget instance, or widget name string). |
| **`data`** | `any` | Optional custom payload passed to the callback function. |

---

## 2. Event Triggers

ForgeTUI supports four primary categories of event triggers:

### Keyboard Triggers
Key strings are decoded by `termkeymap.gen_keymap()`:
- **Standard Navigation**: `'Up'`, `'Down'`, `'Left'`, `'Right'`, `'Home'`, `'End'`, `'PgUp'`, `'PgDn'`, `'Tab'`, `'Backspace'`, `'Esc'`, `'Enter'`.
- **Modifier Combos**: `'Ctrl Q'`, `'Ctrl R'`, `'Ctrl D'`, `'Ctrl Home'`, `'Ctrl End'`, `'Alt R'`, `'Shift Tab'`, `'Ctrl Shift Esc'`.

```python
# Save application state on Ctrl+S
s.addEvent('Ctrl S', save_handler, persist=True)
```

### Mouse Triggers
Mouse event strings are recognized automatically during mouse clicks and motion:
- **Button Actions**: `'click'`, `'button down'`, `'button up'`.
- **Drag Motion**: `'drag'`.
- **Mouse Wheel**: `'scroll up'`, `'scroll down'`, `'scroll left'`, `'scroll right'`.

```python
# Trigger corrupt function on click
button.addEvent('click', corrupt_callback)
```

### Timer Triggers
Passing a floating-point number specifies a recurring timer interval in seconds:

```python
# Execute progress bar cycle function every 0.1 seconds (100ms)
pb.addEvent(0.1, pb_cycle, persist=True)

# Watch output log file every 0.25 seconds (250ms)
log_widget.addEvent(0.25, watch_file, persist=True)
```

### Catch-All Trigger (`''`)
An empty string `''` fires on **every iteration** of the main loop:

```python
# Log all incoming events
s.addEvent('', event_logger_callback)
```

---

## 3. Callback Signatures & Parameter Injection

ForgeTUI inspects callback function signatures at runtime (`inspect.signature`) and dynamically injects only the parameters requested by the callback.

### Supported Parameters

1. **`self`**: The widget instance that owns or handles the event.
2. **`event`**: The event payload (key string, float timestamp, or mouse event dictionary).
3. **`data`**: The custom payload passed when calling `addEvent()`.

### Examples

```python
# 1. Simple callback taking no parameters
def handle_quit():
    s.quit()

button.addEvent('click', handle_quit)

# 2. Callback requesting widget self instance
def draw_ruler(self):
    self.feed(self.t.drawRuler(self.w, self.h))

main_screen.addEvent('Alt R', draw_ruler)

# 3. Callback inspecting mouse event details
def handle_click(self, event):
    if isinstance(event, dict):
        self.log(f"Clicked at X={event['x']}, Y={event['y']}")

widget.addEvent('click', handle_click)

# 4. Callback using custom data payload
def select_tab(self, event=None, data=None):
    if data:
        self.activate_tab(data['index'])

tab_button.addEvent('click', select_tab, data={'index': 2})
```

---

## 4. Event Persistence & Focus Scoping

- **`persist=False` (Default)**: The event fires only when the widget (or one of its child widgets) holds focus.
- **`persist=True`**: The event is registered globally and executes regardless of focus state. Ideal for application hotkeys (e.g. `Ctrl Q` to quit, `F1` for help, `Ctrl 1-9` for tab switching).

```python
# App-wide quit keybinding (Persists even when nested buttons have focus)
tabs.addEvent('Ctrl Q', s.quit, persist=True)
```

---

## 5. Mouse Dragging & Relative Coordinates

Mouse event dictionaries pass relative widget coordinates automatically via `rel_event(event)`:

```python
# Mouse event dictionary structure:
{
    'button': 0,               # 0 = Left click, 1 = Middle, 2 = Right
    'x': 12,                   # Relative X coordinate within widget
    'y': 4,                    # Relative Y coordinate within widget
    'abs': {'x': 45, 'y': 15}, # Absolute screen coordinates
    'action': 'drag',          # 'button down', 'button up', 'drag', 'scroll up'
    'drag start': {'x': 10, 'y': 4},
    'drag move': {'x': 2, 'y': 0, 'button': 0, 'action': 'drag'}
}
```

### Window Drag & Resize Handlers

`WidgetWindow` uses drag event payloads to enable interactive moving and resizing:

```python
def drag_move(self, event=None):
    if isinstance(event, dict) and event['action'] == 'drag':
        if event.get('drag start') and event['drag start']['y'] == 0:
            m = event['drag move']
            self.move(self.x + m['x'], self.y + m['y'])
```
