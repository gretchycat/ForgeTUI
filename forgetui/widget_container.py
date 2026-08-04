#!/usr/bin/python3
from __future__ import annotations
from typing import MutableMapping
import uuid,types
from .widget import Widget
from .widget_output import WidgetBox, WidgetLabel
from .widget_input import WidgetButton, WidgetSlider

#container widgets
class WidgetVBox(WidgetBox): #a structure that automatically places widgets in a vertical sequence
    def __init__(self, x=0, y=0, w='min', h='min', fg=7, bg=None,\
                 style=None, box_name='box',\
                 name='VBox'+str(uuid.uuid4()), parent=None):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, style=style,\
                         box_name=box_name, name=name, parent=parent)
        self.can_focus=False

    def addWidget(self, widget, focus=False):
        widget.reorder=False
        widget=super().addWidget(widget, focus=focus)
        self.resize()
        return widget

    def resize(self, w=None, h=None):
        if w==None: w=self.w
        if h==None: h=self.h
        self.set_geometry(self.x,self.y,self.w,self.h)
        w=len(self.widgetList)
        total_h=0
        max_w=0
        for wd in self.widgetList:
            wd.x=self.frame['w']
            wd.y=total_h+self.frame['h']
            total_h+=wd.h
            max_w=max(max_w,wd.w)
        self.minW=self.frame['w']*2+max_w
        self.minH=self.frame['h']*2+total_h
        super().resize()

class WidgetHBox(WidgetBox): #a structure that automatically places widgets in a horizontal sequence
    def __init__(self, x=0, y=0, w='min', h='min', fg=7, bg=None,\
                 style=None, box_name='box',\
                 name='HBox'+str(uuid.uuid4()), parent=None):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, style=style,\
                         box_name=box_name, name=name, parent=parent)
        self.can_focus=False

    def addWidget(self, widget, focus=False):
        widget.reorder=False
        widget=super().addWidget(widget, focus=focus)
        self.resize()
        return widget

    def resize(self, w=None, h=None):
        if w==None: w=self.w
        if h==None: h=self.h
        self.set_geometry(self.x,self.y,self.w,self.h)
        total_w=0
        max_h=0
        for wd in self.widgetList:
            wd.x=total_w+self.frame['w']
            wd.y=self.frame['h']
            total_w+=wd.w
            max_h=max(max_h,wd.h)
        self.minW=self.frame['w']*2+total_w
        self.minH=self.frame['h']*2+max_h
        super().resize()

class WidgetScrollArea(Widget): #Houses a Screen larger than the printable area, and allows you to scroll.
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=None, \
            parent=None, name='ScrollArea'+str(uuid.uuid4()), \
            v_bar=True, h_bar=True, content_events=True):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, \
                parent=parent, name=name)
        c_w=1.0
        c_h=1.0
        self.v_bar=None
        self.h_bar=None
        if v_bar:
            if h_bar: c_h=-1
            c_w=-1
            self.v_bar=super().addWidget( \
                    WidgetSlider(-1,0,h=c_h, \
                        bar_name='scroll', name=name+'v_bar'))
            self.v_bar.on_update=self.v_bar_on_update
        if h_bar:
            if v_bar:c_w=-1
            c_h=-1
            self.h_bar=super().addWidget( \
                    WidgetSlider(0,-1,w=c_w, \
                        bar_name='scroll', name=name+'h_bar'))
            self.h_bar.on_update=self.h_bar_on_update
        self.content=super().addWidget( \
                Widget(0,0,w=c_w, h=c_h, fg=fg, bg=bg, \
                    parent=parent, name=self.name+'.content'))
        self.content.fb_resize=False #'grow'
        if content_events:
            self.addContentEvents()
        self.pos_x=0
        self.pos_y='follow'
        self.x_can_follow=False
        self.y_can_follow=True

    def v_bar_on_update(self):
        self.v_update(val=self.v_bar.value)

    def h_bar_on_update(self):
        self.h_update(val=self.h_bar.value)

    def addContentEvents(self):
        self.content.addEvent('scroll up', self.up, target=self)
        self.content.addEvent('scroll down', self.down, target=self)
        self.content.addEvent('scroll left', self.left, target=self)
        self.content.addEvent('scroll right', self.right, target=self)
        self.content.addEvent('Up', self.up, target=self)
        self.content.addEvent('Down', self.down, target=self)
        self.content.addEvent('Left', self.left, target=self)
        self.content.addEvent('Right', self.right, target=self)

        self.content.addEvent('PgUp', self.page_up, target=self)
        self.content.addEvent('PgDn', self.page_down, target=self)
        self.content.addEvent('Ctrl Up', self.page_up, target=self)
        self.content.addEvent('Ctrl Down', self.page_down, target=self)
        self.content.addEvent('Ctrl Left', self.page_left, target=self)
        self.content.addEvent('Ctrl Right', self.page_right, target=self)

        self.content.addEvent('Ctrl PgUp', self.top, target=self)
        self.content.addEvent('Ctrl PgDn', self.bottom, target=self)
        self.content.addEvent('Ctrl Home', self.top, target=self)
        self.content.addEvent('Ctrl End', self.bottom, target=self)
        self.content.addEvent('Home', self.home, target=self)
        self.content.addEvent('End', self.end, target=self)

    def addWidget(self, widget, focus=True):
        return self.content.addWidget(widget, focus=focus)

    def feed(self, s):
        self.content.feed(s)

    def draw(self):
        self.auto_scroll()
        super().draw()

    def auto_scroll(self):
        self.max_y=max(0,self.content.fb.height-self.content.h)
        self.cursor_y=max(0,self.content.fb.cursor.y-self.content.h)
        if self.v_bar:
            self.v_bar.max=self.max_y-1
            if self.pos_y=='follow':
                self.v_update(self.pos_y)
                self.v_bar.set_value(max(0,self.cursor_y))
                self.v_bar.unlock()
            else:
                self.v_bar.set_value(max(0,self.pos_y))
                self.v_bar.lock()
        self.max_x=max(0,self.content.fb.width-self.content.w)
        self.cursor_x=max(0,self.content.fb.cursor.x-self.content.w)
        if self.h_bar:
            self.h_bar.max=self.max_x
            if self.pos_x=='follow':
                self.h_update(self.pos_x)
                self.h_bar.set_value(max(0,self.cursor_x))
                self.h_bar.unlock()
            else:
                self.h_bar.set_value(max(0,self.pos_x))
                self.h_bar.lock()

    def h_update(self, val:int|str='follow'):
        if val=='follow': val=self.cursor_x
        self.pos_x=max(0,val)
        if int(val) >= self.max_x-1:
            val=self.max_x
        if self.x_can_follow and int(val)>=self.cursor_x:
            self.pos_x='follow'
        self.content.fb_x_offset=val
        self.on_update()
        return val

    def v_update(self, val:int|str='follow'):
        if val=='follow': val=self.cursor_y
        self.pos_y=max(0,val)
        if int(val) >= self.max_y:
            val=self.max_y
        if self.y_can_follow and int(val)>=self.cursor_y:
            self.pos_y='follow'
        self.content.fb_y_offset=val
        self.on_update()
        return val

    def up(self, lines=1):
        y=self.pos_y
        if y=='follow': y=self.cursor_y
        return self.v_update(int(y)-lines)

    def down(self, lines=1):
        y=self.pos_y
        if y=='follow': y=self.cursor_y
        return self.v_update(int(y)+lines)

    def left(self, lines=1):
        x=self.pos_x
        if x=='follow': x=self.cursor_x
        return self.h_update(int(x)-lines)

    def right(self, lines=1):
        x=self.pos_x
        if x=='follow': x=self.cursor_x
        return self.h_update(int(x)+lines)

    def page_up(self):
        self.up(lines=self.h//2)

    def page_down(self):
        self.down(lines=self.h//2)

    def page_left(self):
        self.left(lines=self.w//2)

    def page_right(self):
        self.right(lines=self.w//2)

    def home(self):
        return self.h_update(0)

    def end(self):
        return self.h_update(self.max_x)

    def top(self):
        return self.v_update(0)

    def bottom(self):
        return self.v_update(self.max_y)

class WidgetWindow(WidgetBox): #A movable/resizable/dragable box with a titlebar
    def __init__(self, x, y, w, h, fg=None, bg=None, style='plot',\
                 title='Untitled Window', content=None,\
                 name='Window'+str(uuid.uuid4()), parent=None):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg,\
                         name=name, style=style,parent=parent)
        if not content:
            content=Widget(parent=self)
        cx=max(0,self.frame['w'])
        cy=max(1,self.frame['h'])
        cw=cx*-2
        ch=-1*(cy+self.frame['h'])
        if isinstance(content,WidgetScrollArea):
            if content.v_bar:
                cw=-cx
            if content.h_bar:
                ch=-cy
        self.content=super().addWidget(content)
        self.content.set_geometry(cx,cy,cw,ch, force=True)
        title_bar_space=4
        self.title_bar=super().addWidget(\
            WidgetHBox(x=title_bar_space,w=-2*title_bar_space, h=1, \
                       name='__title_bar__', parent=self))
        self.title_label=self.title_bar.addWidget(\
            WidgetLabel(text=title, align='center', name='__title_label__',\
                        bg=4, fg=15, parent=self.title_bar))
        self.addEvent('drag', self.drag_handler)
        self.title_label.addEvent('drag', self.drag_handler)

    def __repr__(self):
        return f"Window: (title={self.title})"

    def addWidget(self, widget, focus=True):
        return self.content.addWidget(widget, focus=focus)

    def feed(self, s):
        self.content.feed(s)

    def drag_handler(self, event=None):
        win=self
        if self.name=='__title_label__':
            win=self.parent.parent
        if self.name=='__title_bar__':
            win=self.parent
        win.drag_move(event)
        win.drag_resize(event)

    def drag_move(self, event=None):
        if not self.parent: return
        if type(event)==dict and \
                event['action']=='drag' and \
                event.get('drag start') and \
                event.get('drag move'):
            pos=event['drag start']['y']==0
            if event['button']==0 and \
                    ( pos or \
                    event.get('drag handle')=='move'):
                if pos:
                    self.drag_handle='move'
                m = event['drag move']
                self.move(self.x+m['x'], self.y+m['y'])
            self.on_update()

    def drag_resize(self, event=None):
        if not self.parent: return
        if type(event)==dict and \
                event['action']=='drag' and \
                event.get('drag start') and \
                event.get('drag move'):
            pos=event['drag start']['y']==self.h-1 and \
                    event['drag start']['x']==self.w-1
            if event['button']==0 and \
                    (pos or event.get('drag handle')=='resize' ):
                if pos:
                    self.drag_handle='resize'
                m= event['drag move']
                self.resize(self.w+m['x'], self.h+m['y'])

            self.on_update()

class WidgetTabs(Widget): #Houses multiple containers in tabs
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=None, \
            parent=None, name='Tabs.'+str(uuid.uuid4())):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, \
                parent=parent, name=name)
        self.can_focus=False
        self.tab_list=[]
        self.active_tab=None
        self.hbox=super().addWidget(WidgetHBox(x=0,y=0,w=1.0, h=3,parent=self))

    def activate_tab(self, index):
        if not self.tab_list:
            self.active_tab=None
            return False
        resolved_index = index % len(self.tab_list)
        for i,t in enumerate(self.tab_list):
            if i!=resolved_index:
                t['widget'].hide()
        self.tab_list[resolved_index]['widget'].set_focus()
        self.active_tab=resolved_index
        self.makeDirty()
        self.fix_tab_size()
        self.fix_tab_colors()

    def rename_tab(self, index, name):
        if not self.tab_list:
            return False
        resolved_index = index % len(self.tab_list)
        self.tab_list[resolved_index]['name']=name
        self.fix_tab_size()
        self.makeDirty()

    def remove_tab(self, index):
        if not self.tab_list:
            return False
        resolved_index = index % len(self.tab_list)
        t=self.tab_list[resolved_index]
        self.remove_child(t['widget'])
        self.hbox.remove_child(t['tab_button'])
        self.tab_list.pop(resolved_index)
        if resolved_index<len(self.tab_list):
            self.activate_tab(resolved_index)
        else:
             self.activate_tab(resolved_index-1)
        self.fix_tab_size()
        self.makeDirty()
        return True

    def fix_tab_size(self):
        if not self.tab_list:
            return False
        self.makeDirty()

    def fix_tab_colors(self):
        if not self.tab_list:
            return False
        for k,t in enumerate(self.tab_list):
            t['tab_button'].active=k==self.active_tab
        self.makeDirty()

    def select_tab(self, event=None, data=None):
        if not self.tab_list:
            return False
        for k,t in enumerate(self.tab_list):
            if t['hotkey']==event or data==t:
                #type(event)==dict and self event['x'], event['y']
                self.activate_tab(k)
                self.makeDirty()
                self.log(f'activating tab {k}')

    def add_tab(self, tab_name, hotkey,widget:Widget):
        b=self.hbox.addWidget(WidgetButton(x=0,y=0,w='min', h=3,\
                            caption=tab_name,parent=self.hbox,\
                            box_name='box',fg=self.fg, bg=self.bg, style='2line',\
                            name=f'Tab{str(uuid.uuid4())}'), focus=not self.tab_list)
        self.tab_list.append({'tab_button':b, 'widget':widget, 'hotkey':hotkey})
        b.addEvent('click', self.select_tab, data=self.tab_list[-1])
        b.addEvent(hotkey, self.select_tab, persist=True)
        self.fix_tab_size()
        super().addWidget(widget)
        widget.set_geometry(0,b.h,1.0,-b.h)
        if len(self.tab_list)==1:
            self.activate_tab(len(self.tab_list)-1)
        else:
            widget.hide()
            self.makeDirty()
        return widget

    def addWidget(self, widget, focus=True):
        if not self.tab_list:
            return None
        return self.tab_list[self.active_tab]['widget'].addWidget(widget, focus)

class WidgetMatrix(WidgetScrollArea): # Prototype two-dimensional Matrix/Table grid data widget
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=None,
                 parent=None, name=None, headers=None, rows=None):
        if name is None:
            name = 'Matrix' + str(uuid.uuid4())
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, parent=parent,
                         name=name, v_bar=True, h_bar=True, content_events=True)
        self.headers = headers or []
        self.rows = rows or []
        self.selected_row = 0
        self.selected_col = 0

        self.content.addEvent('Up', self.nav_up, target=self)
        self.content.addEvent('Down', self.nav_down, target=self)
        self.content.addEvent('Left', self.nav_left, target=self)
        self.content.addEvent('Right', self.nav_right, target=self)

    def nav_up(self):
        if self.selected_row > 0:
            self.selected_row -= 1
            self.makeDirty()

    def nav_down(self):
        if self.selected_row < len(self.rows) - 1:
            self.selected_row += 1
            self.makeDirty()

    def nav_left(self):
        if self.selected_col > 0:
            self.selected_col -= 1
            self.makeDirty()

    def nav_right(self):
        num_cols = len(self.headers) if self.headers else (len(self.rows[0]) if self.rows else 0)
        if self.selected_col < num_cols - 1:
            self.selected_col += 1
            self.makeDirty()

    def draw(self):
        self.content.fb.cls()
        if not self.rows and not self.headers:
            return super().draw()

        num_cols = max(len(self.headers), max((len(r) for r in self.rows), default=0))
        col_widths = []
        for c in range(num_cols):
            w_h = len(str(self.headers[c])) if c < len(self.headers) else 0
            w_r = max((len(str(r[c])) for r in self.rows if c < len(r)), default=0)
            col_widths.append(max(w_h, w_r, 4))

        if self.headers:
            header_str = " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(self.headers))
            self.content.feed(f"\x1b[1m{header_str}\x1b[22m\n")
            separator = "-+-".join("-" * col_widths[i] for i in range(num_cols))
            self.content.feed(f"{separator}\n")

        for r_idx, row in enumerate(self.rows):
            cells = []
            for c_idx in range(num_cols):
                val = str(row[c_idx]) if c_idx < len(row) else ""
                cell_text = val.ljust(col_widths[c_idx])
                if r_idx == self.selected_row and c_idx == self.selected_col:
                    cell_text = f"\x1b[7m{cell_text}\x1b[27m"
                cells.append(cell_text)
            self.content.feed(" | ".join(cells) + "\n")

        return super().draw()


class TreeNode:
    """Represents a single node in a WidgetTree hierarchy."""
    def __init__(self, label: str, data: any = None, expanded: bool = False, parent: TreeNode | None = None):
        self.label = label
        self.data = data
        self.expanded = expanded
        self.parent = parent
        self.children: list[TreeNode] = []

    def add_child(self, label: str, data: any = None, expanded: bool = False) -> TreeNode:
        node = TreeNode(label=label, data=data, expanded=expanded, parent=self)
        self.children.append(node)
        return node

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def toggle(self):
        if not self.is_leaf():
            self.expanded = not self.expanded

    def expand(self):
        if not self.is_leaf():
            self.expanded = True

    def collapse(self):
        if not self.is_leaf():
            self.expanded = False


class WidgetTree(WidgetScrollArea):
    """Hierarchical Tree View widget for displaying nested structures."""
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=None,
                 parent=None, name=None, v_bar=True, h_bar=True,
                 icon_expanded='[-] ', icon_collapsed='[+] ', icon_leaf='  • '):
        if name is None:
            name = 'Tree' + str(uuid.uuid4())
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, parent=parent,
                         name=name, v_bar=v_bar, h_bar=h_bar, content_events=True)
        self.root_nodes: list[TreeNode] = []
        self.selected_index: int = 0
        self.visible_nodes: list[tuple[TreeNode, int]] = []
        self.icon_expanded = icon_expanded
        self.icon_collapsed = icon_collapsed
        self.icon_leaf = icon_leaf

        self.content.addEvent('Up', self.nav_up, target=self)
        self.content.addEvent('Down', self.nav_down, target=self)
        self.content.addEvent('Right', self.expand_or_nav_down, target=self)
        self.content.addEvent('Left', self.collapse_or_nav_up, target=self)
        self.content.addEvent('Enter', self.toggle_selected, target=self)
        self.content.addEvent('Space', self.toggle_selected, target=self)
        self.content.addEvent('click', self.on_tree_click, target=self)

    def add_node(self, label: str, data: any = None, expanded: bool = False, parent_node: TreeNode | None = None) -> TreeNode:
        if parent_node is None:
            node = TreeNode(label=label, data=data, expanded=expanded)
            self.root_nodes.append(node)
        else:
            node = parent_node.add_child(label=label, data=data, expanded=expanded)
        self.rebuild_visible()
        return node

    def rebuild_visible(self):
        self.visible_nodes.clear()
        def traverse(node: TreeNode, depth: int):
            self.visible_nodes.append((node, depth))
            if node.expanded and not node.is_leaf():
                for child in node.children:
                    traverse(child, depth + 1)

        for root in self.root_nodes:
            traverse(root, 0)

        if self.selected_index >= len(self.visible_nodes):
            self.selected_index = max(0, len(self.visible_nodes) - 1)
        self.makeDirty()

    def get_selected() -> tuple[TreeNode | None, any]:
        if 0 <= self.selected_index < len(self.visible_nodes):
            node, _ = self.visible_nodes[self.selected_index]
            return node, node.data
        return None, None

    def nav_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            self.makeDirty()

    def nav_down(self):
        if self.selected_index < len(self.visible_nodes) - 1:
            self.selected_index += 1
            self.makeDirty()

    def toggle_selected(self):
        if 0 <= self.selected_index < len(self.visible_nodes):
            node, _ = self.visible_nodes[self.selected_index]
            node.toggle()
            self.rebuild_visible()

    def expand_or_nav_down(self):
        if 0 <= self.selected_index < len(self.visible_nodes):
            node, _ = self.visible_nodes[self.selected_index]
            if not node.is_leaf() and not node.expanded:
                node.expand()
                self.rebuild_visible()
            else:
                self.nav_down()

    def collapse_or_nav_up(self):
        if 0 <= self.selected_index < len(self.visible_nodes):
            node, _ = self.visible_nodes[self.selected_index]
            if not node.is_leaf() and node.expanded:
                node.collapse()
                self.rebuild_visible()
            elif node.parent:
                for idx, (vnode, _) in enumerate(self.visible_nodes):
                    if vnode == node.parent:
                        self.selected_index = idx
                        break
                self.makeDirty()

    def on_tree_click(self, event=None):
        if isinstance(event, dict) and event.get('y') is not None:
            click_y = event['y']
            if 0 <= click_y < len(self.visible_nodes):
                if self.selected_index == click_y:
                    self.toggle_selected()
                else:
                    self.selected_index = click_y
                    self.makeDirty()

    def draw(self):
        self.rebuild_visible()
        self.content.fb.cls()
        for idx, (node, depth) in enumerate(self.visible_nodes):
            indent = "  " * depth
            if node.is_leaf():
                prefix = self.icon_leaf
            elif node.expanded:
                prefix = self.icon_expanded
            else:
                prefix = self.icon_collapsed

            line_text = f"{indent}{prefix}{node.label}"

            if idx == self.selected_index:
                line_str = f"\x1b[7m{line_text}\x1b[27m\n"
            else:
                line_str = f"{line_text}\n"
            self.content.feed(line_str)

        return super().draw()

