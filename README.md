# ForgeTUI (`forgetui`)

A lightweight, reactive, high-performance Python Terminal User Interface framework and terminal control library built on top of `libansiscreen`.

---

## Key Features

- **Double-Buffered Rendering**: Flicker-free terminal UI updates via frame diffing (`emit_diff`).
- **Resolution-Independent Geometry**: Supports absolute integer positioning, relative percentage dimensions (`w=0.5, h=0.5`), subtractive fractions (`w=-0.2`), and auto-sizing (`'min'`).
- **Mouse & Keyboard Event Engine**: Built-in support for mouse clicks, drag-and-drop, resizable windows, scrolling, hotkeys, and timer events.
- **Rich Component Library**: Tabs, windows, scroll areas, progress bars, marquees, interactive buttons, range sliders, log viewers, 2D matrix tables, and tree views.
- **Advanced Sub-Pixel Graphics**: Micro-border rendering using Braille, Octant, Sextant, and Quadrants via `libansiscreen`.

---

## Documentation & Resources

- 📖 **[Documentation Suite](docs/README.md)**:
  - [Main Loop & Relative Geometry](docs/main_loop_and_geometry.md)
  - [Widget Types & Reference](docs/widget_types.md)
  - [Events & Callbacks Guide](docs/events_and_callbacks.md)
  - [Themes & Border Styles](docs/themes_and_styles.md)
- 📌 **[Development Roadmap & TODO List](TODO.md)**

---

## Running Unit Tests

To run the complete test suite (40 tests across all widgets, geometries, events, and themes):

```bash
./test.sh
```

Or using `unittest` directly:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

---

## Quick Example

```python
from forgetui.widget import Widget
from forgetui.widget_container import WidgetTabs, WidgetWindow, WidgetScrollArea
from forgetui.widget_input import WidgetButton

tabs = WidgetTabs(0, 0, 1.0, 1.0, bg=0, fg=7)
main_tab = tabs.add_tab('Main', widget=Widget(bg=8, fg=15), hotkey='Ctrl Home')

win = main_tab.addWidget(
    WidgetWindow(0.1, 0.1, 0.8, 0.8, title="Interactive Window")
)
win.feed("Hello from ForgeTUI!\n")

tabs.addEvent('Ctrl Q', main_tab.quit, persist=True)
tabs.mainLoop()
```
