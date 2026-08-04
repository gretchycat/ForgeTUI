# Widget Types & Reference

ForgeTUI provides an extensible component hierarchy. All components inherit from the base `Widget` class.

---

## 1. Base Class: `Widget`

File: [`forgetui/widget.py`](../forgetui/widget.py)

The `Widget` class provides standard attributes and lifecycle methods for all UI elements.

```python
Widget(x=0, y=0, w=1.0, h=1.0, fg=None, bg=None, parent=None, name='uuid')
```

### Key Attributes
- **`x`, `y`, `w`, `h`**: Current dimensions and position in terminal columns/rows.
- **`fg`, `bg`**: Foreground and background colors.
- **`focus`**: Boolean or `'parent'` indicating current focus status.
- **`hidden`**: Controls widget visibility.
- **`dirty`**: Flags if the widget frame buffer requires redrawing.
- **`background`**: Function callback or multi-line string pattern rendered on the widget background canvas.
- **`widgetList`**: Ordered list of child widgets.
- **`eventList`**: Dictionary of registered event handlers.

### Key Methods
- `addWidget(widget, focus=True)`: Adds a child widget to this widget.
- `remove_child(widget)`: Removes a child widget from the hierarchy.
- `get_widget_by_name(name)`: Searches the widget tree for a child matching `name`.
- `set_focus()`: Sets focus to this widget and updates parent focus chains.
- `hide(next='parent')` / `unhide(focus=True)`: Toggles widget visibility.
- `feed(text)`: Writes ANSI text directly to the widget frame buffer.
- `clear()`: Clears the widget frame buffer.
- `makeDirty(recurse=True)`: Marks the widget and its parents for redrawing.
- `quit()`: Signals the application main loop to exit cleanly.

---

## 2. Container Widgets

File: [`forgetui/widget_container.py`](../forgetui/widget_container.py)

### `WidgetBox`
Draws a bordered container frame around its children using configurable box styles.
```python
WidgetBox(x=0, y=0, w=1.0, h=1.0, fg=7, bg=None, style='plot', box_name='box')
```

### `WidgetVBox`
Automatically arranges child widgets in a vertical sequence.
```python
vbox = WidgetVBox(x=-20, y=0, w=20, h=1.0, name='buttonbox')
vbox.addWidget(WidgetButton(0, 0, w=20, h=3, caption="Option 1"))
vbox.addWidget(WidgetButton(0, 0, w=20, h=3, caption="Option 2"))
```

### `WidgetHBox`
Automatically arranges child widgets in a horizontal sequence.
```python
hbox = WidgetHBox(x=0, y=0, w=1.0, h=3)
```

### `WidgetScrollArea`
Contains a scrollable frame buffer with optional vertical (`v_bar`) and horizontal (`h_bar`) scrollbars. Supports mouse wheel scrolling, arrow keys, and page navigation (`PgUp`/`PgDn`/`Home`/`End`).
```python
scroll = WidgetScrollArea(10, 5, w=0.5, h=0.5, bg=65, fg=16, v_bar=True, h_bar=True)
for i in range(100):
    scroll.feed(f"Line {i}\n")
```

### `WidgetWindow`
A draggable and resizable window with a title bar. Clicking and dragging the title bar moves the window; dragging the bottom-right corner resizes the window.
```python
window = WidgetWindow(
    x=-0.95, y=0.5, w=0.9, h=0.5,
    style='w', bg=75, fg=0, title='Interactive Window',
    content=WidgetScrollArea(...)
)
```

### `WidgetTabs`
A tabbed container with header selection buttons and keybinding shortcuts.
```python
tabs = WidgetTabs(0, 0, 1.0, 1.0, bg=0, fg=7)

# Add tabs with title, content widget, and shortcut key:
main_tab = tabs.add_tab('Main', widget=Widget(bg=8, fg=15), hotkey='Ctrl Home')
next_tab = tabs.add_tab('Next', widget=Widget(fg=9, bg=1), hotkey='Ctrl End')

# Tab switching methods:
tabs.activate_tab(0)       # Switch by tab index
tabs.rename_tab(0, 'Home') # Rename tab header
tabs.remove_tab(1)         # Remove tab by index
```

### `WidgetTree` & `TreeNode`
Hierarchical tree view widget for displaying nested folder structures, JSON data, or file trees with expandable/collapsible nodes.
```python
tree = main_tab.addWidget(WidgetTree(0, 0, w=0.4, h=1.0))

# Build tree hierarchy:
root_dir = tree.add_node("Projects", expanded=True)
src_folder = tree.add_node("src", parent_node=root_dir, expanded=True)
tree.add_node("main.py", parent_node=src_folder)
tree.add_node("utils.py", parent_node=src_folder)
tree.add_node("README.md", parent_node=root_dir)
```
- **Navigation Keys**: `Up`/`Down` (navigate selection), `Right` (expand node), `Left` (collapse node / select parent), `Enter`/`Space` (toggle collapse state).

### `WidgetMatrix`
Two-dimensional table grid widget with column headers, separator lines, and cell navigation.
```python
matrix = main_tab.addWidget(
    WidgetMatrix(
        0.4, 0, w=0.6, h=1.0,
        headers=["ID", "Name", "Status", "RAM (MB)"],
        rows=[
            [1, "MainProcess", "Running", 42.5],
            [2, "Worker-1", "Idle", 18.2],
            [3, "Logger", "Running", 8.4]
        ]
    )
)
```
- **Navigation Keys**: `Up`/`Down`/`Left`/`Right` (cell selection navigation).

---


## 3. Input Widgets

File: [`forgetui/widget_input.py`](../forgetui/widget_input.py)

### `WidgetButton`
Interactive push button with visual active/focus states, caption text, and click callbacks.
```python
button = WidgetButton(
    x=5, y=3, w=20, h=3,
    style='plot', box_name='box', bg=248, fg=0,
    caption='Click Me', name='btn1'
)
button.addEvent('click', callback_function)
```

### `WidgetSlider`
Numeric range slider or discrete selection control. Configurable for horizontal (`w > 1, h = 1`) or vertical (`w = 1, h > 1`) orientation.
```python
# Continuous numeric slider:
slider = WidgetSlider(x=0, y=0, w=30, h=1, minimum=0.0, maximum=100.0, value=50.0)

# Discrete custom selection slider:
discrete_slider = WidgetSlider(
    x=0.1, y=20, w=-0.2, h=1,
    discreet=['Option A', 'Option B', 'Option C']
)
```
- **Methods**: `set_value(val)`, `lock()`, `unlock()`.

---

## 4. Output Widgets

File: [`forgetui/widget_output.py`](../forgetui/widget_output.py)

### `WidgetLabel`
Static text display with alignment controls.
```python
label = WidgetLabel(
    x=0, y=0, w=20, h=1,
    text='Header Text', align='center', valign='middle'
)
```
- **`align`**: `'left'`, `'center'`, `'right'`
- **`valign`**: `'top'`, `'middle'`, `'bottom'`

### `WidgetMarquee`
Scrolling text label for news tickers or status displays.
```python
marquee = WidgetMarquee(
    x=0.1, y=5, w=-0.2, h=1,
    text='Scrolling Announcement', direction='ltr', speed=0.05
)
```
- **`direction`**:
  - `'ltr'`: Left to right.
  - `'rtl'`: Right to left.
  - `'pingpong'`: Bounces back and forth when reaching borders.

### `WidgetProgressBar`
Visual progress indicator bar showing `0%` to `100%`.
```python
pb = WidgetProgressBar(x=0.1, y=15, w=-0.2, h=1, total=100)
pb.set_progress(45)  # Sets progress to 45%
```

---

## 5. Terminal & Logging Widgets

File: [`forgetui/widget_terminal.py`](../forgetui/widget_terminal.py)

### `WidgetLog`
Monitors and tails a local file in real-time inside a scrollable area. Automatically detects log truncation or rotation.
```python
log_widget = WidgetLog(
    x=0, y=0, w=1.0, h=1.0,
    fg=15, bg=None, filename='output.log'
)
```

### `WidgetTerminal`
Base class for custom interactive terminal emulators and command queues.
