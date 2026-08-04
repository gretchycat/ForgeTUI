# ForgeTUI Documentation

Welcome to the **ForgeTUI** documentation. ForgeTUI is a lightweight, feature-rich Python Terminal User Interface library built on top of `libansiscreen`. It provides a reactive, double-buffered frame-rendering engine with full mouse interaction, flexible relative geometry layouts, event handling, customizable theme systems, and specialized sub-pixel terminal graphics.

---

## Table of Contents

1. [Architecture & Quickstart](README.md#architecture--quickstart)
2. [Main Loop & Geometry](main_loop_and_geometry.md)
3. [Widget Types & Components](widget_types.md)
4. [Events & Callbacks](events_and_callbacks.md)
5. [Themes & Box Styles](themes_and_styles.md)

---

## Architecture & Quickstart

ForgeTUI follows a hierarchical tree structure of widgets. Every ForgeTUI application has a **root widget** that owns the screen frame buffer, manages event queues, handles terminal signals, and runs the application main loop.

### Key Concepts

- **Widget Tree**: Top-level containers hold child widgets. Parent widgets automatically route layout geometries, focus state changes, and draw calls to their children.
- **Double-Buffered Rendering**: ForgeTUI renders frame changes by calculating differences between the previous frame buffer and the current frame buffer (`emit_diff`), ensuring flicker-free UI updates at up to 60 FPS.
- **Flexible Geometry**: Widget positions and dimensions support fixed integer coordinates, relative floating-point percentages (e.g., `0.5` = 50% width), or automatic `'min'` sizing.
- **Event Dispatcher**: Keypresses, mouse clicks, drags, scrolls, and timer triggers pass through a flexible event routing engine with optional parameter filtering and event persistence.

---

## Quickstart Example

The following example is adapted from `termguitest.py` demonstrating how to build a tabbed terminal layout with windows, buttons, sliders, progress bars, scroll areas, and log viewers:

```python
#!/usr/bin/python3
from forgetui.widget import Widget
from forgetui.widget_input import WidgetButton, WidgetSlider
from forgetui.widget_output import WidgetMarquee, WidgetProgressBar
from forgetui.widget_container import WidgetTabs, WidgetWindow, WidgetVBox, WidgetScrollArea
from forgetui.widget_terminal import WidgetLog

# 1. Create top-level tab container
tabs = WidgetTabs(0, 0, 1.0, 1.0, bg=0, fg=7)

# 2. Create main screen root widget and add to tabs
main_screen = Widget(0, 0, 1.0, 1.0, bg=8, fg=15, name='root')
tabs.add_tab('Main', widget=main_screen, hotkey='Ctrl Home')

# 3. Create a secondary tab with controls
next_tab = tabs.add_tab('Next', widget=Widget(fg=9, bg=1), hotkey='Ctrl End')
next_tab.addWidget(WidgetMarquee(0.1, 5, -0.2, 1, text='ForgeTUI Marquee Demo', direction='ltr'))

pb = next_tab.addWidget(WidgetProgressBar(0.1, 15, -0.2, 1))
def pb_cycle(self):
    p = self.progress + self.total / 100
    if p > self.total:
        p = 0
    self.set_progress(p)
pb.addEvent(0.1, pb_cycle, persist=True) # Timer event every 100ms

# 4. Create a window with a log viewer inside the main tab
log_win = main_screen.addWidget(
    WidgetWindow(
        -0.95, 0.5, 0.9, 0.5, style='w', bg=75, fg=0,
        title='System Log Window', name='log_window',
        content=WidgetLog(fg=15, bg=None, name='system_log', filename='output.log')
    )
)
log_win.feed("ForgeTUI Initialized...\n")

# 5. Register global key bindings
tabs.addEvent('r', main_screen.refresh, persist=True)
tabs.addEvent('Ctrl Q', main_screen.quit, persist=True)

# 6. Start the Main Loop
tabs.mainLoop()
```

---

## Directory Sitemap

- **[`main_loop_and_geometry.md`](main_loop_and_geometry.md)**: Deep dive into `mainLoop()`, signal handling (SIGTSTP/SIGCONT/SIGINT), terminal raw mode management, coordinates, and percentage geometry.
- **[`widget_types.md`](widget_types.md)**: Complete reference of all base, container, input, output, and terminal widgets.
- **[`events_and_callbacks.md`](events_and_callbacks.md)**: Full guide to mouse, keyboard, timer, custom events, parameter injection, drag handlers, and persistence.
- **[`themes_and_styles.md`](themes_and_styles.md)**: Comprehensive look at color options, border box styles (line, curve, plot, braille, octant, etc.), themes (`make_theme`), and custom background patterns.
