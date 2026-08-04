# ForgeTUI Roadmap & TODO List

This document tracks planned widgets, enhancements, and roadmap items for the **ForgeTUI** framework.

---

## 1. Input & Form Widgets

- [ ] **`WidgetTextInput`** (Single-line input control)
  - [ ] Cursor position indicator & navigation (`Left`, `Right`, `Home`, `End`).
  - [ ] Text selection, `Backspace`, `Delete`.
  - [ ] Password masking support (`echo='*'` or `echo=False`).
  - [ ] Placeholder text support when empty.
- [ ] **`WidgetTextArea`** (Multi-line text editor)
  - [ ] Word wrapping and horizontal/vertical scrolling.
  - [ ] Line numbering gutter.
  - [ ] Cut, copy, paste handling.
- [ ] **`WidgetCheckBox`**
  - [ ] Toggle state (`[X] Checkbox Option` vs `[ ] Checkbox Option`).
  - [ ] `Space` / `Enter` toggle actions.
- [ ] **`WidgetRadioBox`**
  - [ ] Radio button groups (`(•) Choice A` vs `( ) Choice B`).
  - [ ] Auto-deselect siblings within the same container/group.
- [ ] **`WidgetDropDown` / `ComboBox`**
  - [ ] Collapsible selection list pop-up overlay.
- [ ] **`WidgetItemList` / `ListView`**
  - [ ] Single/multi-selection item list.
  - [ ] Incremental search/filter filtering as user types.
- [ ] **`WidgetSpinner`**
  - [ ] Animated progress/loading indicators (`⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏`).
- [ ] **`WidgetFileSelect`**
  - [ ] File system modal picker dialog with directory navigation.

---

## 2. Container & Data Visualization Widgets

- [x] **`WidgetTree` / `TreeNode` (Prototype Implemented in [`forgetui/widget_container.py`](forgetui/widget_container.py))**
  - [x] Hierarchical tree structure navigation (`Up`, `Down`, `Left`, `Right`, `Enter`, `Space`).
  - [x] Expandable/collapsible folder nodes (`[-]`, `[+]`) and leaf nodes (`•`).
  - [ ] Node drag-and-drop / reordering support.
- [x] **`WidgetMatrix` / Table Grid (Prototype Implemented in [`forgetui/widget_container.py`](forgetui/widget_container.py))**
  - [x] Data grid with dynamic column widths, headers, and separator lines.
  - [x] Row/column cell selection & navigation (`Up`, `Down`, `Left`, `Right`).
  - [ ] Virtualized rendering for large datasets (>10,000 rows).
- [ ] **`WidgetMenuBar`**
  - [ ] Top-level horizontal menu bar (`File`, `Edit`, `View`, `Help`) with drop-down menus.
- [ ] **`WidgetGraph`**
  - [ ] Sparkline charts, bar graphs, and 2D line plots using `libansiscreen` spixel modes.

---

## 3. Focus Engine & Keyboard Navigation

- [ ] **Automatic `Tab` / `Shift+Tab` Focus Traversal**
  - [ ] Implement global depth-first focus ring across all visible widgets with `can_focus = True`.
- [ ] **Shortcut Key Mnemonics (Accelerators)**
  - [ ] Highlight key accents on button captions (e.g. `[O]k`, `[C]ancel`).
  - [ ] `Alt+<Letter>` key dispatching to focus/click corresponding widgets.

---

## 4. Modal Overlays & Z-Index Management

- [ ] **Modal Layer & Backdrop**
  - [ ] Root widget modal stack that captures mouse/keyboard focus and dims background UI when dialogs/popups open.
- [ ] **Tooltips**
  - [ ] Hover tooltips after mouse pause over widgets.
- [ ] **Context Menus**
  - [ ] Right-click pop-up menus anchored to terminal coordinates.

---

## 5. Layout Engine Enhancements

- [ ] **Flexbox Stretch Factors (`flex=1`, `flex=2`)**
  - [ ] Allow child widgets in `WidgetVBox` / `WidgetHBox` to dynamically share remaining screen space.
- [ ] **Padding & Margins**
  - [ ] Standardized `padding` and `margin` properties across all widgets.

---

## 6. System & Graphics Integration

- [ ] **Clipboard Support**
  - [ ] OSC 52 terminal escape sequence copy/paste.
- [ ] **`WidgetImage`**
  - [ ] High-level widget wrapper for inline Kitty and Sixel graphics.
- [ ] **Asyncio Event Loop Integration**
  - [ ] Thread-safe callback dispatching for non-blocking background workers.
