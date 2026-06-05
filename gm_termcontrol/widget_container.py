#!/usr/bin/python3
from __future__ import annotations
import uuid
from libansiscreen.screen import Screen
from .widget import Widget
from .widget_output import WidgetBox, WidgetLabel
from .widget_input import WidgetButton, WidgetSlider

#container widgets
class WidgetVBox(WidgetBox): #a structure that automatically places widgets in a vertical sequence
    def __init__(self, x=0, y=0, w='min', h='min', fg=7, bg=None, style=None, title='', box_name='box', name='VBox'+str(uuid.uuid4())):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, style=style, title=title, box_name=box_name, name=name)

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
            c_w=-1.1
            self.v_bar=super().addWidget( \
                    WidgetSlider(-1.1,0,h=-1.1, \
                        bar_name='scroll', name=name+'v_bar'))
        if h_bar:
            c_h=-1.1
            self.h_bar=super().addWidget( \
                    WidgetSlider(0,-1.1,w=-1.1, \
                        bar_name='scroll', name=name+'h_bar'))
        self.content=super().addWidget( \
                Widget(0,0,w=c_w, h=c_h, fg=fg, bg=bg, \
                    parent=parent, name=self.name+'.content'))
        self.scroll_pos_x=0
        self.scroll_pos_y='auto'

    def addWidget(self, widget, focus=True):
        self.content.addWidget(widget, focus=focus)

    def feed(self, s):
        self.content.feed(s)

    def draw(self):
        self.scroll()
        super().draw()

    def scroll(self):
        v,h=0,0
        if self.h_bar is not None: h=1
        if self.v_bar is not None: v=1
        #self.content.h=self.content.screen.height
        #self.content.w=self.content.screen.width
        if self.scroll_pos_y=='auto':
            self.content.y=min(0,(self.h-1-h)-self.content.h)
            if self.v_bar:
                self.v_bar.max=max(0,self.content.h-self.h)
                self.v_bar.set_value(self.v_bar.max)
        else:
            self.content.y=min(0,(self.h-1-h)-int(self.scroll_pos_y))
            if self.v_bar:
                self.v_bar.max=max(0,self.content.h-self.h)
                self.h_bar.set_value(self.scroll_pos_y)
        if self.scroll_pos_x=='auto':
            self.content.x=min(0,(self.w-1-v)-self.content.w)
            if self.h_bar:
                self.h_bar.max=max(0,self.content.w-self.w)
                self.h_bar.set_value(self.h_bar.max)
        else:
            self.content.x=min(0,(self.w-1-v)-int(self.scroll_pos_x))
            if self.h_bar:
                self.h_bar.max=max(0,self.content.w-self.w)
                self.h_bar.set_value(self.scroll_pos_x)

    def h_update(self, val):
        self.scroll_pos_x=val
        if self.h_bar.max==val:
            self.scroll_pos_x='auto'

    def v_update(self, val):
        self.scroll_pos_y=val
        if self.v_bar.max==val:
            self.scroll_pos_y='auto'

    def resize(self, w=None, h=None):
        if w==None: w=self.w
        if h==None: h=self.h
        self.set_geometry(self.x,self.y,w,h)
        for wd in [ self.v_bar, self.h_bar]:
            if wd:
                wd.resize(wd.w,wd.h)
        c=self.content
        c.resize(max(c.w,w), max(c.h,h))

class WidgetTabController(Widget): #Houses multiple containers in a tabs
    pass

class WidgetWindow(WidgetBox): #A movable/resizable/dragable box with a titlebar
    pass

