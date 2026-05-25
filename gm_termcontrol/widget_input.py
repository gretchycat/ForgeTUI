#!/usr/bin/python3
from __future__ import annotations
import uuid
from gm_termcontrol.widget import Widget
from gm_termcontrol.widget_output import WidgetBox
#input widgets
class WidgetButton(WidgetBox): #a button for interaction
    def __init__(self, x, y, w=0, h=1, fg=7, bg=None, style='curve', box_name='button', caption='Button', toggle=False,name='Button'+str(uuid.uuid4())):
        minw=len(caption)+4
        if w<minw:
            w=minw
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, style=style, box_name=box_name, name=name)
        self.active=False
        self.active_disp=False
        self.style=style
        self.caption=caption
        self.title=caption
        self.resize()
        self.addEvent('button down', self.b_down)
        self.addEvent('button up', self.b_up)

    def __repr__(self):
        return f"{self.__class__.__name__}(caption={self.caption})({self.x}, {self.y})"

    def b_down(self, event=None):
        if event['button']==0:
            if 0<=event['x']<self.w and 0<=event['y']<self.h:
                self.active=True
                self.active_disp=True

    def b_up(self, event=None):
        if event['button']==0:
            if 0<=event['x']<self.w and 0<=event['y']<self.h:
                self.active=False

    def draw(self):
        self.fg0=7
        self.bg0=0
        if self.parent:
            self.fg0=self.parent.fg
            self.bg0=self.parent.bg
        fw=0
        fh=0
        box_type='focus'
        if self.active or self.active_disp:
            box_type='active'
            if self.active_disp:
                self.active_disp=False
        self.box_type=box_type
        fw=self.frame['w']*2
        fh=self.frame['h']*2
        cap_x=int(self.w/2-len(self.caption)/2)
        cap_y=int((self.h-fh)/2+fh/2)
        super().draw()
        self.screen.cursor_goto(cap_x, cap_y)
        c=self.theme[box_type][f'{self.box_name}.middle_center']
        if c:
            self.screen.set_foreground(c.fg)
            self.screen.set_background(c.bg)
        self.screen.print(self.caption)

class WidgetSlider(Widget): #a numeric value display or selector widget
    pass

class WidgetMenuBar(Widget):
    pass

class WidgetTextInput(Widget):
    pass

class WidgetTextArea(Widget):
    pass

class WidgetCheckBox(Widget):
    pass

class WidgetRadioBox(Widget):
    pass

class WidgetDropDown(Widget):
    pass

class WidgetSpinner(Widget):
    pass

