#!/usr/bin/python3
from __future__ import annotations
from libansiscreen.screen import Screen
import uuid
from gm_termcontrol.widget import Widget
from gm_termcontrol.widget_output import WidgetBox
#container widgets
class WidgetVBox(WidgetBox): #a structure that automatically places widgets in a vertical sequence
    def addWidget(self, widget):
        widget=super().addWidget(widget)
        self.resize()
        self.log(f'add {widget}')
        return widget

    def resize(self, w=None, h=None):
        if w==None: w=self.w
        if h==None: h=self.h
        self.set_geometry(self.x,self.y,self.w,self.h)
        max_w=self.w-self.frame['w']*2
        max_h=self.w-self.frame['h']*2
        wc=len(self.widgetList)
        total_h=0
        for wd in self.widgetList:
            wd.x=self.frame['w']
            wd.y=total_h+self.frame['h']
            total_h+=wd.h
            self.log(wd)

class WidgetHBox(WidgetBox): #a structure that automatically places widgets in a horizontal sequence
    def addWidget(self, widget):
        widget=super().addWidget(widget)
        self.resize()
        return widget

    def resize(self, w=None, h=None):
        if w==None: w=self.w
        if h==None: h=self.h
        self.set_geometry(self.x,self.y,self.w,self.h)
        max_w=self.w-self.frame['w']*2
        max_h=self.w-self.frame['h']*2
        wc=len(self.widgetList)
        total_w=0
        for wd in self.widgetList:
            wd.x=total_w+self.frame['w']
            wd.y=self.frame['h']
            total_h+=wd.h
            self.log(wd)

class WidgetWindow(WidgetBox): #A movable/resizable/dragable box with a titlebar
    pass

class WidgetTabController(Widget): #Houses multiple Screens in a tab Interface
    pass

class WidgetScrollArea(Widget): #Houses a Screen larger than the printable area, and allows you to scroll.
    pass
