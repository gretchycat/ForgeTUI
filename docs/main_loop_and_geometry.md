# Main Loop and Geometry System

This document explains how **ForgeTUI** manages terminal raw mode, signal handling, the event-driven main render loop, and the resolution-independent relative geometry layout system.

---

## 1. Terminal Management & Main Loop

The main entry point for running a ForgeTUI application is `Widget.mainLoop()`, called on the root widget (or container widget like `WidgetTabs`).

```python
tabs.mainLoop()
```

### Terminal Initialization & Modes

When `mainLoop()` starts:
1. **Termios Attributes**: Saves the original standard input `termios` settings (`old_settings`).
2. **Alternate Screen Buffer**: Switches terminal output to the alternate screen buffer (`\x1b[?1049h`), preventing interference with the host shell scrollback.
3. **Cursor & Mouse Control**:
   - Hides the cursor (`\x1b[?25l`).
   - Enables mouse reporting (`\x1b[?1006h` SGR decimal coordinates and `\x1b[?1002h` button-event/drag tracking).
4. **Non-blocking Input**: Configures `sys.stdin` for non-blocking raw input reads using `termios.setraw()` and file flags (`os.O_NONBLOCK`).

---

## 2. Signal Handling (SIGINT, SIGTSTP, SIGCONT)

ForgeTUI catches system signals to ensure terminal settings are always cleanly restored:

| Signal | Action Taken |
| :--- | :--- |
| `SIGTSTP` (Ctrl+Z) | Disables mouse reporting, shows cursor, restores normal screen buffer and standard `termios` shell settings, then issues `SIGSTOP` to suspend process cleanly. |
| `SIGCONT` | On process resume, re-applies raw terminal mode, re-enables mouse tracking, restores alt screen, and forces full frame refresh (`self.refresh()`). |
| `SIGINT` / `SIGTERM` | Restores normal screen buffer and `termios` attributes, then calls `widget.quit()` to exit cleanly. |

---

## 3. The Main Execution & Render Loop

The main loop runs continuously while `root().go == True`:

```python
while self.go:
    # 1. Terminal resize check
    sz = self.t.get_terminal_size()
    if sz['columns'] != self.w or sz['rows'] != self.h:
        self.set_geometry(0, 0, 0, 0)
        self.resize()

    # 2. Draw frame buffer
    self.fb = self.draw()

    # 3. Diff rendering (Flicker-free output)
    if self.force_refresh:
        self.t.output(s_start + home + self.fb.emit(raw=True) + s_end)
    else:
        self.t.output(s_start + home + self.fb.emit_diff(pbuffer, raw=True) + s_end)

    # 4. Timer event generation
    timer = time.time()
    self.event_buffer.append(EventTrigger(timer, EventSource.TIMER))

    # 5. Non-blocking input read
    for inp in self.input.read_input():
        if isinstance(inp, str):
            self.event_buffer.append(EventTrigger(inp, EventSource.KEYBOARD))
        elif isinstance(inp, dict):
            self.event_buffer.append(EventTrigger(inp, EventSource.MOUSE))

    # 6. Event buffer processing
    while self.event_buffer:
        inp = self.event_buffer.pop(0)
        if inp.source == EventSource.MOUSE:
            self.check_mouse_focus_change(inp.event)
            self.check_captured(inp.event)
        self.runEvent(inp.event)
```

### Frame Buffer Diffing
Instead of redrawing the entire screen every iteration, ForgeTUI maintains a copy of the previous frame buffer (`pbuffer`) and outputs only the changed terminal cells via `fb.emit_diff()`. This dramatically reduces terminal write overhead and eliminates UI flickering.

### Quitting the Application
To terminate the main loop programmatically from any callback or keybinding, call `quit()` on any widget:

```python
widget.quit()  # Sets root().go = False
```

---

## 4. Geometry & Relative Layout System

ForgeTUI features a flexible geometry engine (`set_geometry(x, y, w, h)`) that supports absolute coordinates, percentages, relative sizing, and string keywords.

### Coordinate Parameter Types

| Parameter Format | Description | Example |
| :--- | :--- | :--- |
| **Integer (`int > 0`)** | Absolute character offset or dimension in columns/rows. | `x=10, y=5, w=20, h=3` |
| **Integer (`int < 0`)** | Relative offset or dimension measured from the right/bottom edge. | `w=-20` (20 cols less than parent width) |
| **Float (`0.0 <= val <= 1.0`)** | Percentage fraction of parent width/height. | `w=0.5, h=0.5` (50% width and 50% height) |
| **Float (`-1.0 <= val < 0.0`)** | Percentage fraction subtractive calculation. | `w=-0.2, h=-0.1` |
| **String (`'min'`)** | Sizes the widget according to its minimum required width (`minW`) or height (`minH`). | `w='min', h='min'` |

### Geometry Conversion Rules

When evaluating geometry relative to parent dimensions (`parent.w` and `parent.h`):

```python
# Sizing relative to parent container
if isinstance(w, float) and abs(w) <= 1.0:
    w = int(w * parent.w)

if w == 'min':
    w = self.minW

# Bounds clamp
self.w = int(w) % parent.w
```

### Auto-Sizing Container Layouts

1. **`WidgetVBox`**: Automatically calculates cumulative height `minH` and max child width `minW`, stacking widgets vertically line-by-line.
2. **`WidgetHBox`**: Automatically calculates cumulative width `minW` and max child height `minH`, laying out widgets side-by-side.
3. **`WidgetWindow`**: Supports dragging (`move(x, y)`) and corner drag-resizing (`resize(w, h)`), automatically enforcing screen boundary clamping.
