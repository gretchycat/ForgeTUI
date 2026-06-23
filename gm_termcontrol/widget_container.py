#!/usr/bin/python3
from __future__ import annotations
import uuid,types
from libansiscreen.screen import Screen
from .widget import Widget
from .widget_output import WidgetBox, WidgetLabel
from .widget_input import WidgetButton, WidgetSlider

#container widgets
class WidgetVBox(WidgetBox): #a structure that automatically places widgets in a vertical sequence
    def __init__(self, x=0, y=0, w='min', h='min', fg=7, bg=None, style=None, title='', box_name='box', name='VBox'+str(uuid.uuid4())):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, style=style, title=title, box_name=box_name, name=name)
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
    def __init__(self, x=0, y=0, w='min', h='min', fg=7, bg=None, style=None, title='', box_name='box', name='HBox'+str(uuid.uuid4())):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, style=style, title=title, box_name=box_name, name=name)
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
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=0, \
            parent=None, name='ScrollArea'+str(uuid.uuid4()), \
            v_bar=True, h_bar=True):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, \
                parent=parent, name=name)
        c_w=1.0
        c_h=1.0
        self.v_bar=None
        self.h_bar=None
        if v_bar:
            c_w=-1
            self.v_bar=super().addWidget( \
                    WidgetSlider(-1,0,h=-1, \
                        bar_name='scroll', name=name+'v_bar'))
            def u(self): self.parent.v_update(val='auto')
            self.v_bar.on_update=types.MethodType(u,self.v_bar)
        if h_bar:
            c_h=-1
            self.h_bar=super().addWidget( \
                    WidgetSlider(0,-1,w=-1, \
                        bar_name='scroll', name=name+'h_bar'))
            def u(self): self.parent.h_update(val='auto')
            self.h_bar.on_update=types.MethodType(u,self.h_bar)
        self.content=super().addWidget( \
                Widget(0,0,w=c_w, h=c_h, fg=fg, bg=bg, \
                    parent=parent, name=self.name+'.content'))
        self.content.screen_resize=False #'grow'
        self.pos_x=0
        self.pos_y='auto'

    def addWidget(self, widget, focus=True):
        self.content.addWidget(widget, focus=focus)

    def feed(self, s):
        self.content.feed(s)

    def draw(self):
        self.auto_scroll()
        super().draw()

    def auto_scroll(self):
        if self.v_bar:
            if self.pos_y=='auto':
                self.v_bar.max=max(0,self.content.screen.height-self.content.h)
                self.v_bar.set_value(self.v_bar.max)
        if self.h_bar:
            if self.pos_x=='auto':
                self.h_bar.max=max(0,self.content.screen.width-self.content.w)
                self.h_bar.set_value(self.h_bar.max)

    def h_update(self, val='auto'):
        if val=='auto': val=self.h_bar.value
        val=max(0,min(val,self.content.screen.width-self.content.w))
        self.pos_x=val
        if val >= self.content.screen.width-self.content.w:
            self.pos_x='auto'
        self.content.screen_x_offset=val
        #self.on_update()
        return val

    def v_update(self, val='auto'):
        if val=='auto': val=self.v_bar.value
        val=max(0,min(val,self.content.screen.height-self.content.h))
        self.pos_y=val
        if val >= self.content.screen.height-self.content.h:
            self.pos_y='auto'
        self.content.screen_y_offset=val
        #self.on_update()
        return val

    def up(self, lines=1):
        return self.v_update(self.pos_y-lines)

    def down(self, lines=1):
        return self.v_update(self.pos_y+lines)

    def left(self, lines=1):
        return self.h_update(self.pos_x-lines)

    def right(self, lines=1):
        return self.h_update(self.pos_x+lines)

    def home(self):
        return self.h_update(0)

    def end(self):
        return self.h_update(self.content.screen.width-self.content.w)

    def top(self):
        return self.v_update(0)

    def bottom(self):
        return self.v_update(self.content.screen.height-self.content.h)

class WidgetTabController(Widget): #Houses multiple containers in a tabs
    pass

class WidgetWindow(WidgetBox): #A movable/resizable/dragable box with a titlebar
    pass

