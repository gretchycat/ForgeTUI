# Themes and Styling Guide

ForgeTUI features a flexible styling and theme system supporting ANSI 16-color, 256-color, 24-bit RGB colors, customizable box frames, sub-pixel border rendering, and custom background pattern generators.

---

## 1. Color System

ForgeTUI handles colors via `libansiscreen` and `termcontrol.color()`.

### Supported Color Formats

| Format | Syntax Example | Description |
| :--- | :--- | :--- |
| **ANSI 16 Integers** | `0` to `15` | Standard terminal palette colors (`0`=Black, `1`=Red, `2`=Green, `4`=Blue, `7`=White, `8`-`15`=Bright variants). |
| **ANSI 16 Strings** | `'red'`, `'blue'`, `'brightgreen'` | Named string aliases for ANSI 16 palette indices. |
| **ANSI 256 Integers** | `16` to `255` | 256-color extended terminal palette values. |
| **RGB Hex Strings** | `'#FF5733'`, `'#F57'`, `'FF5733'` | Truecolor 24-bit hex specifications. |
| **RGB Dictionaries** | `{'red': 255, 'green': 87, 'blue': 51}` | Truecolor 24-bit RGB dictionary structures. |

```python
# Setting colors on a widget:
widget.setColors(fg='#FFFFFF', bg=24)
widget = Widget(0, 0, 1.0, 1.0, fg='brightwhite', bg='blue')
```

---

## 2. Border Box Styles

File: [`forgetui/widget_output.py`](../forgetui/widget_output.py) & [`forgetui/theme.py`](../forgetui/theme.py)

Widgets derived from `WidgetBox` (`WidgetButton`, `WidgetWindow`, `WidgetVBox`, `WidgetHBox`) support border styles:

| Style Name | Frame Description | Visual Character Types |
| :--- | :--- | :--- |
| **`'line'`** | Single thin Unicode box lines. | `┌ ─ ┐ │ └ ┘` |
| **`'2line'`** | Double Unicode box lines. | `╔ ═ ╗ ║ ╚ ╝` |
| **`'curve'`** | Rounded corner Unicode box lines. | `╭ ─ ╮ │ ╰ ╯` |
| **`'wide'`** | Thick heavy Unicode lines. | `┏ ━ ┓ ┃ ┗ ┛` |
| **`'inside'`** | Solid block inside borders. | Block shade fill characters (`█ ▀ ▄`) |
| **`'outside'`** | Solid block outside borders. | Block shade outline characters |
| **`'plot'`** | Sub-pixel high-resolution line borders. | Half-character plotting pixels |
| **`'braille'`** | 2x4 sub-pixel Braille dot matrix borders. | Unicode Braille patterns (`⣿ ⠋ ⠙`) |
| **`'quadrant'`** | 2x2 sub-pixel quadrant block borders. | Unicode Quadrants (`▘ ▝ ▖ ▗`) |
| **`'sextant'`** | 2x3 sub-pixel sextant block borders. | Unicode Sextants |
| **`'octant'`** | 2x4 sub-pixel octant block borders. | Unicode Octants |

### Usage Example

```python
# Rounded box button
b1 = vbox.addWidget(WidgetButton(0, 0, w=20, h=3, style='curve', caption="Curve"))

# Double line box button
b2 = vbox.addWidget(WidgetButton(0, 0, w=20, h=3, style='2line', caption="2Line"))

# High-resolution Braille border window
win = main_screen.addWidget(WidgetWindow(0, 0, 0.5, 0.5, style='braille', title="Braille Frame"))
```

---

## 3. Theme Engine (`make_theme` & `shift_theme`)

File: [`forgetui/theme.py`](../forgetui/theme.py)

Themes control the glyphs, foreground colors, background colors, and cell attributes of widget components across four interactive states:

1. **`'focus'`**: Rendered when the widget has active user focus.
2. **`'off'`**: Rendered when the widget is inactive/defocused.
3. **`'parent'`**: Rendered when a child of the widget has focus.
4. **`'active'`**: Rendered when a control (e.g. `WidgetButton`) is currently pressed/clicked.

### Theme Creation

```python
from forgetui.theme import make_theme

# Create a theme mapping dictionary
custom_theme = make_theme(
    style='curve',
    fg='#FFFFFF',
    bg='#000000',
    inactive={'h': 0, 's': 0.0, 'v': -0.2}, # Shift HSV brightness down for inactive
    active={'h': 0, 's': 0.0, 'v': 0.33}     # Shift HSV brightness up for active
)
```

---

## 4. Custom Background Rendering (`Widget.background`)

Every widget supports a dynamic `background` attribute. Assigning a string pattern or a drawing callback to `widget.background` automatically renders background patterns whenever the widget redraws.

### Pattern String Backgrounds

Assigning a multi-line string tiles that pattern across the widget canvas:

```python
# Tile a decorative block pattern:
screen.background = '██ \n▄▄°\n▀▀.'
```

### Function Callback Backgrounds

Assigning a function callback allows dynamic procedural graphics rendering:

```python
# Procedural maze generator background
import random

def maze_background(self, width, height):
    random.seed(42)
    for _ in range(height):
        for _ in range(width):
            self.feed(chr(0x2571 + random.randint(0, 1))) # Diagonal slash characters
        self.feed('\n')

screen.background = maze_background
```

```python
# Dynamic grid ruler background
def ruler_background(self, width, height):
    self.feed(self.t.drawRuler(width, height))

screen.background = ruler_background
```
