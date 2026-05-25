#!/usr/bin/python3
from __future__ import annotations
from .theme import make_theme
import uuid
from gm_termcontrol.widget import Widget
#output widgets
class WidgetBox(Widget): #Draws a box the size of the widget
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=0, style=None, title='', box_name='box', name='Box'+str(uuid.uuid4())):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, name=name)
        self.title=title
        self.style=style
        self.box_name=box_name
        self.fg0, self.bg0=fg, bg
        self.style=style
        self.box_type='focus'
        self.frame={'w':0, 'h':0}
        if style is not None:
            self.frame={'w':2, 'h':1}
        self.theme=make_theme(style, bg=bg, fg=fg)

    def draw(self):
        screen=self.screen
        x=self.x
        y=self.y
        fill=True
        box_name=self.box_name
        w=self.w
        h=self.h
        bn=self.box_name
        if screen is None:
            return
        t=self.theme.get(self.box_type)
        if not t:
            t=self.theme.get('focus')
        if self.style in ['plot']:
            if fill:
                for y in range(1, screen.height-2):
                    for x in range(1, screen.width-1):
                        screen.set_cell(x,y,t[f'{bn}.middle_center'])
            screen.plot(0,0,t[f'{bn}.top_left'].fg)
            screen.plot(screen.width-1,0,t[f'{bn}.top_right'].fg)
            for x in range(1,screen.width-1):
                screen.plot(x,0,t[f'{bn}.top_center'].fg)
                screen.plot(x,1,t[f'{bn}.middle_center'].bg)
                screen.plot(x,screen.height*2-4,t[f'{bn}.middle_center'].bg)
                screen.plot(x,screen.height*2-3,t[f'{bn}.bottom_center'].fg)
            for y in range(1, screen.height*2-3):
                screen.plot(0,y,t[f'{bn}.middle_left'].fg)
                screen.plot(1,y,t[f'{bn}.middle_center'].bg)
                screen.plot(screen.width-2,y,t[f'{bn}.middle_center'].bg)
                screen.plot(screen.width-1,y,t[f'{bn}.middle_right'].fg)
            screen.plot(0,screen.height*2-3,t[f'{bn}.bottom_left'].fg)
            screen.plot(screen.width-1,screen.height*2-3,t[f'{bn}.bottom_right'].fg)
        else:
            screen.set_cell(0,0,t[f'{bn}.top_left'])
            screen.set_cell(screen.width-1,0,t[f'{bn}.top_right'])
            for x in range(1, screen.width-1):
                screen.set_cell(x,0,t[f'{bn}.top_center'])
                screen.set_cell(x,screen.height-2,t[f'{bn}.bottom_center'])
            for y in range(1, screen.height-2):
                screen.set_cell(0,y,t[f'{bn}.middle_left'])
                screen.set_cell(screen.width-1,y,t[f'{bn}.middle_right'])
                if fill:
                    for x in range(1, screen.width-1):
                        screen.set_cell(x,y,t[f'{bn}.middle_center'])
            screen.set_cell(0,screen.height-2,t[f'{bn}.bottom_left'])
            screen.set_cell(screen.width-1,screen.height-2,t[f'{bn}.bottom_right'])
        super().draw()
        return screen

class WidgetLabel(Widget): #a blurb of text made into a widget.it can be justified, have text attributes and colored
    pass

class WidgetList(Widget): #one dimensional list of data arranged vertically
    pass

class WidgetMatrix(Widget): #a two-dimensional Matrix of data
    pass

class WidgetProgressBar(Widget): #a bar going from 0 to 100%
    pass
