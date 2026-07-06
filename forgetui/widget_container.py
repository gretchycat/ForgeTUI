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
        wc=len(self.widgetList)
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
            total_w+=wd.h
            max_h=max(max_h,wd.h)
        self.minW=self.frame['w']*2+total_w
        self.minH=self.frame['h']*2+max_h
        super().resize()

class WidgetScrollArea(Widget): #Houses a Screen larger than the printable area, and allows you to scroll.
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=None, \
            parent=None, name='ScrollArea'+str(uuid.uuid4()), \
            v_bar=True, h_bar=True):
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
        self.pos_x=0
        self.pos_y='auto'

    def v_bar_on_update(self):
        return
        self.parent.v_update(val=self.value)

    def h_bar_on_update(self):
        return
        self.parent.h_update(val=self.value)

    def addWidget(self, widget, focus=True):
        return self.content.addWidget(widget, focus=focus)

    def feed(self, s):
        self.content.feed(s)

    def draw(self):
        self.auto_scroll()
        super().draw()

    def auto_scroll(self):
        self.max_y=max(0,self.content.fb.height-self.content.h)
        self.auto_y=self.content.fb.cursor.y-self.content.h
        self.v_update(self.pos_y)
        if self.v_bar:
            self.v_bar.max=self.max_y
            if self.pos_y=='auto':
                self.v_bar.set_value(max(0,self.auto_y))
            else:
                self.v_bar.set_value(max(0,self.pos_y))
        self.max_x=max(0,self.content.fb.width-self.content.w)
        self.auto_x=self.content.fb.cursor.x-self.content.w
        self.h_update(self.pos_x)
        if self.h_bar:
            self.h_bar.max=self.max_x
            if self.pos_x=='auto':
                self.h_bar.set_value(max(0,self.auto_x))
            else:
                self.h_bar.set_value(max(0,self.pos_x))

    def h_update(self, val:int|str='auto'):
        if val=='auto': val=self.auto_x
        self.pos_x=max(0,val)
        if int(val) >= self.max_x:
            val=self.max_x
        if val==self.auto_x:
            self.pos_x='auto'
        self.content.fb_x_offset=val
        self.on_update()
        return val

    def v_update(self, val:int|str='auto'):
        if val=='auto': val=self.auto_y
        self.pos_y=max(0,val)
        if int(val) >= self.max_y:
            val=self.max_y
        if val==self.auto_y:
            self.pos_y='auto'
        self.content.fb_y_offset=val
        self.on_update()
        return val

    def up(self, lines=1):
        y=self.pos_y
        if y=='auto':
            y=self.max_y
        return self.v_update(y-lines)

    def down(self, lines=1):
        y=self.pos_y
        if y=='auto':
            y=self.max_y
        return self.v_update(y+lines)

    def left(self, lines=1):
        x=self.pos_x
        if x=='auto':
            x=self.max_x
        return self.h_update(x-lines)

    def right(self, lines=1):
        x=self.pos_x
        if x=='auto':
            x=self.max_x
        return self.h_update(x+lines)

    def home(self):
        return self.h_update(0)

    def end(self):
        return self.h_update(self.max_x)

    def top(self):
        return self.v_update(0)

    def bottom(self):
        return self.v_update(self.max_y)

class WidgetTabController(Widget): #Houses multiple containers in a tabs
    pass

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
        if type(content)==WidgetScrollArea:
            if content.v_bar:
                cw=-cx
            if content.h_bar:
                ch=-cy
        content.set_geometry(cx,cy,cw,ch)
        self.content=content
        self.title=title
        title_bar_space=4
        self.title_bar=super().addWidget(\
            WidgetHBox(x=title_bar_space,w=-2*title_bar_space, h=1, \
                       name='__title_bar__', parent=self))
        self.title_label=self.title_bar.addWidget(\
            WidgetLabel(text=title, align='center', name='__title_label__',\
                        bg=4, fg=15, parent=self.title_bar))
        self.addEvent('drag', self.drag_handler)
        self.title_label.addEvent('drag', self.drag_handler)
        super().addWidget(content)

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
