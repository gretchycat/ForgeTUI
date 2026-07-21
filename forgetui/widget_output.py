#!/usr/bin/python3
from __future__ import annotations
import uuid, math
from .theme import make_theme
from .widget import Widget

#output widgets
class WidgetBox(Widget): #Draws a box the size of the widget
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=None, \
                 style='plot', box_name='box', \
                 name='Box'+str(uuid.uuid4()), parent=None):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg,\
                         name=name, parent=parent)
        self.style=style
        self.box_name=box_name
        self.fg0, self.bg0=fg, bg
        self.box_type='focus'
        self.frame={'w':0, 'h':0}
        if style is not None:
            self.frame={'w':2, 'h':1}
        self.theme=make_theme(style, bg=bg, fg=fg)

    def draw(self):
        fb=self.fb
        x=self.x
        y=self.y
        fill=True
        box_name=self.box_name
        w=self.w
        h=self.h
        bn=self.box_name
        t=self.theme.get(self.box_type)
        if not t:
            t=self.theme.get('focus')
        if self.style is not None:
            if self.style in ['plot']:
                if fill:
                    for y in range(1, fb.height-1):
                        for x in range(1, fb.width-1):
                            fb.set_cell(x,y,t[f'{bn}.middle_center'])
                fb.plot(0,0,t[f'{bn}.top_left'].fg)
                fb.plot(fb.width-1,0,t[f'{bn}.top_right'].fg)
                for x in range(1,fb.width-1):
                    fb.plot(x,0,t[f'{bn}.top_center'].fg)
                    fb.plot(x,1,t[f'{bn}.middle_center'].bg)
                    fb.plot(x,fb.height*2-3,t[f'{bn}.bottom_center'].fg)
                for y in range(1, (fb.height-1)*2-1):
                    fb.plot(0,y,t[f'{bn}.middle_left'].fg)
                    fb.plot(1,y,t[f'{bn}.middle_center'].bg)
                    fb.plot(fb.width-2,y,t[f'{bn}.middle_center'].bg)
                    fb.plot(fb.width-1,y,t[f'{bn}.middle_right'].fg)
                fb.plot(0,(fb.height-1)*2-1,t[f'{bn}.bottom_left'].fg)
                fb.plot(fb.width-1,(fb.height-1)*2-1,t[f'{bn}.bottom_right'].fg)
            else:
                fb.set_cell(0,0,t[f'{bn}.top_left'])
                fb.set_cell(fb.width-1,0,t[f'{bn}.top_right'])
                for x in range(1, fb.width-1):
                    fb.set_cell(x,0,t[f'{bn}.top_center'])
                    fb.set_cell(x,fb.height-2,t[f'{bn}.bottom_center'])
                for y in range(1, fb.height-2):
                    fb.set_cell(0,y,t[f'{bn}.middle_left'])
                    fb.set_cell(fb.width-1,y,t[f'{bn}.middle_right'])
                    if fill:
                        for x in range(1, fb.width-1):
                            fb.set_cell(x,y,t[f'{bn}.middle_center'])
                fb.set_cell(0,fb.height-2,t[f'{bn}.bottom_left'])
                fb.set_cell(fb.width-1,fb.height-2,t[f'{bn}.bottom_right'])
        #else: fb.cls()
        return super().draw()

class WidgetLabel(Widget): #a blurb of text made into a widget.it can be justified, have text attributes and colored
    def __init__(self, x=0, y=0, w=1.0, h=1, fg=7, bg=None, style='', \
                  name='label'+str(uuid.uuid4()), parent=None, \
                  text='Label', align='left', valign='top'):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg,\
                         name=name, parent=parent)
        self.align=align
        self.valign=valign
        self.text=text

    def draw(self):
        x, y = 0,0
        text=self.text[:self.w]
        if self.align in [ 'center' ]:
            x=int(self.w/2-len(text)/2)
        if self.align in [ 'right' ]:
            x=self.w-len(text)
        if self.valign in [ 'middle', 'center' ]:
            y=self.h//2
        if self.valign in [ 'bottom' ]:
            y=self.h-1
        self.setColors(self.fg,self.bg)
        self.fb.cls()
        self.fb.cursor_goto(x,y)
        self.feed(self.text)

class WidgetMarquee(WidgetLabel): # a scrolling blurb of text made a widget.it can be justified, have text attributes and colored
    def __init__(self, x=0, y=0, w=1.0, h=1, fg=7, bg=None, style='', \
                  name='Marquee '+str(uuid.uuid4()), parent=None,\
                  text='marquee', direction='ltr', speed=0.1):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg,\
                         name=name, parent=parent, text=text)
        self.o_text=text
        self.text_offset=0
        self.color_offset=0
        self.direction=direction
        self.resize()
        self.addEvent(float(speed), self.shift, persist=True)

    def shift(self):
        if self.direction.lower()=='pingpong':
                if self.text_offset<=0:
                    self.dir=1
                if self.text_offset>=len(self.text_line)-self.right-len(self.o_text):
                    self.dir=-1
        self.text=self.text_line[self.text_offset:]
        self.text_offset=(self.text_offset+self.dir)%(len(self.text_line))

    def resize(self, w=None, h=None):
        ret = super().resize(w, h)
        match self.direction.lower():
            case 'ltr':
                self.left=self.w
                self.right=0
                self.dir=-1
            case 'rtl':
                self.left=self.w
                self.right=0
                self.dir=1
            case 'pingpong':
                self.left=self.w-len(self.o_text)
                self.right=self.w-len(self.o_text)
        self.text_line=' '*self.left+self.o_text+' '*self.right
        return ret

class WidgetProgressBar(Widget): #TODO:a bar going from 0 to 100%
    pass

class WidgetGraph(Widget): #TODO: different graph types
    pass
