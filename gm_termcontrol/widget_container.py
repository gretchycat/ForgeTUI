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
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=0, parent=None, name='ScrollArea'+str(uuid.uuid4()), v_bar=True, h_bar=True):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, parent=parent, name=name)
        c_w=1.0
        c_h=1.0
        self.h_bar,self.v_bar=None,None
        if v_bar:
            c_w=-1.1
            self.v_bar=super().addWidget(WidgetSlider(-1.1,0,h=-1.1, bar_name='scroll', name=name+'v_bar'))
        if h_bar:
            c_h=-1.1
            self.h_bar=super().addWidget(WidgetSlider(0,-1.1,w=-1.1, bar_name='scroll', name=name+'h_bar'))
        self.content=super().addWidget(Widget(0,0,w=c_w, h=c_h, fg=fg, bg=bg, parent=parent, name=self.name+'.content'))
        self.scroll_pos_x=0
        self.scroll_pos_y='auto'
        self.v_bar=None
        self.h_bar=None

    def addWidget(self, widget, focus=True):
        self.content.addWidget(widget, focus=focus)

    def feed(self, s):
        self.content.feed(s)

class WidgetTabController(Widget): #Houses multiple Screens in a tab Interface
    pass

class WidgetWindow(WidgetBox): #A movable/resizable/dragable box with a titlebar
    pass

