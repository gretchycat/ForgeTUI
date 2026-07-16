#!/usr/bin/python3
from __future__ import annotations
import uuid
from .widget import Widget
from .widget_output import WidgetBox
from .theme import make_theme

#input widgets
class WidgetButton(WidgetBox): #a button for interaction
    def __init__(self, x:int|float, y:int|float, w:int|float|str=0, h:int|float|str=1, fg=7, bg=None,\
                 style='curve', box_name='button',\
                 caption='Button', toggle=False,\
                 name='Button'+str(uuid.uuid4()),parent=None):
        minw=len(caption)+4
        if w<minw:
            w=minw
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, style=style, box_name=box_name, name=name, parent=parent)
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

    def b_down(self, event:dict|None=None):
        if event is not None:
            if event['button']==0:
                if 0<=event['x']<self.w and 0<=event['y']<self.h:
                    self.active=True
                    self.active_disp=True #make sure that at least one frame has the Pressed button
                    self.makeDirty()
                    self.pre_click()

    def b_up(self, event:dict|None=None):
        if event is not None:
            if event['button']==0:
                if 0<=event['x']<self.w and 0<=event['y']<self.h:
                    self.active=False
                    self.makeDirty()
                    self.on_click()

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
            self.active_disp=False
        self.box_type=box_type
        fw=self.frame['w']*2
        fh=self.frame['h']*2
        cap_x=int(self.w/2-len(self.caption)/2)
        cap_y=int((self.h-fh)/2+fh/2)
        super().draw()
        self.fb.cursor_goto(cap_x, cap_y)
        c=self.theme[box_type][f'{self.box_name}.middle_center']
        if c: self.setColors(c.fg, c.bg)
        self.feed(self.caption)

    def pre_click(self):
        self.makeDirty()
        pass

    def on_click(self):
        self.makeDirty()
        pass

class WidgetSlider(Widget): #a numeric value display or selector widget
    def __init__(self, x=0, y=0, w=1, h=1, fg=7, bg=None, style='', \
                 bar_name='slider', name='slider'+str(uuid.uuid4()), \
                 value=0.0, minimum=0.0, maximum=1.0, step=None, \
                 page_steps=10, lock=False):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, name=name)
        w,h=self.w,self.h
        if w==1 and h==1:
            self.log(f'invalid Slider. only one of w/h may be 1.')
        if w>1 and w>1:
            self.log(f'invalid Slider. one of w/h must be 1.')
        if w<1 or w<1:
            self.log(f'invalid Slider. w/h cannot be 0 or less.')
        self.theme=make_theme(style, bg=bg, fg=fg)
        self.bar_name=bar_name
        self.min=minimum
        self.max=maximum
        self.step=step
        self.page_steps=page_steps
        self.set_value(value)
        self.is_locked=lock
        self.box_type='focus'
        if w==1 and h>1:
            self.addEvent('Up', self.up)
            self.addEvent('scroll up', self.up)
            self.addEvent('Down', self.down)
            self.addEvent('scroll down', self.down)
            self.addEvent('Ctrl Up', self.v_pgup)
            self.addEvent('Ctrl Down', self.v_pgdn)
            self.addEvent('PgUp', self.v_pgup)
            self.addEvent('PgDn', self.v_pgdn)
            self.addEvent('Home', self.home)
            self.addEvent('End', self.end)
            self.addEvent('button down', self.v_move)
            self.addEvent('drag', self.v_move)
            pass #vertical callbacks
        if h==1 and w>1:
            self.addEvent('Left', self.left)
            self.addEvent('scroll left', self.left)
            self.addEvent('Right', self.right)
            self.addEvent('scroll right', self.right)
            self.addEvent('Ctrl Left', self.h_pgup)
            self.addEvent('Ctrl Down', self.h_pgdn)
            self.addEvent('PgUp', self.h_pgup)
            self.addEvent('PgDn', self.h_pgdn)
            self.addEvent('Home', self.home)
            self.addEvent('End', self.end)
            self.addEvent('button down', self.h_move)
            self.addEvent('drag', self.h_move)
            pass #horizontal callback

    def lock(self):
        self.is_locked=True

    def unlock(self):
        self.is_locked=False
    
    def set_value(self, value):
        reverse=False
        minimum=self.min
        maximum=self.max
        if self.min>self.max:
            minimum=self.max
            maximum=self.min
            reverse=True
        if value<minimum:
            self.value=minimum
        elif value>maximum:
            self.value=maximum
        else:
            self.value=value
        self.on_update()

    def draw(self):
        orientation=''
        reverse=False
        minimum=self.min
        maximum=self.max
        if self.min>self.max:
            minimum=self.max
            maximum=self.min
            reverse=True
        span=maximum-minimum
        value=minimum
        if span!=0:
            value=(self.value-minimum)/span # normalized to 0.0 < value < 1.0
        bn=self.bar_name
        t=self.theme.get(self.box_type)
        if not t:
            t=self.theme.get('focus')
        handle=t[f'{bn}.handle'] # handle cell
        if self.is_locked:
            handle=t[f'{bn}.handle_lock'] # locked handle cell
        if self.w==1 and self.h>1: # vertical
            # draw verticsl bar
            self.fb.set_cell(0,0,t[f'{bn}.up'])
            self.fb.set_cell(0,self.h-1,t[f'{bn}.down'])
            for y in range(1,self.h-1):
                self.fb.set_cell(0,y,t[f'{bn}.v'])
            if reverse:
                # draw handle at 1.0-value
                self.fb.set_cell(0,int((self.h-3)*(1-value))+1,handle) 
            else:
                # draw handle at value
                self.fb.set_cell(0,int((self.h-3)*value)+1,handle) 
        if self.h==1 and self.w>1: # horizontal
            # draw horizontal bar
            self.fb.set_cell(0,0,t[f'{bn}.left'])
            self.fb.set_cell(self.w-1,0,t[f'{bn}.right'])
            for x in range(1,self.w-1):
                self.fb.set_cell(x,0,t[f'{bn}.h'])
            if reverse:
                # draw handle at 1.0-value
                self.fb.set_cell(int((self.w-3)*(1-value))+1,0,handle) 
            else:
                # draw handle at value
                self.fb.set_cell(int((self.w-3)*value)+1,0,handle) 

    def up(self, event=None):
        step=self.step
        if not step:
            step=(self.max-self.min)/(self.h-2)
        self.set_value(self.value-step)
        pass

    def down(self, event=None):
        step=self.step
        if not step:
            step=(self.max-self.min)/(self.h-2)
        self.set_value(self.value+step)
        pass

    def left(self, event=None):
        step=self.step
        if not step:
            step=(self.max-self.min)/(self.w-2)
        self.set_value(self.value-step)
        pass

    def right(self, event=None):
        step=self.step
        if not step:
            step=(self.max-self.min)/(self.w-2)
        self.set_value(self.value+step)
        pass

    def v_pgup(self, event=None):
        for _ in range(self.page_steps):
            self.up(event=event)

    def v_pgdn(self, event=None):
        for _ in range(self.page_steps):
            self.down(event=event)

    def v_move(self, event=None):
        if type(event)==dict:
            if event['y']==0:
                self.up()
                return
            elif event['y']==self.h-1:
                self.down()
                return
            v=(event['y']-1)/(self.h-3)
            reverse=False
            minimum=self.min
            maximum=self.max
            if self.min>self.max:
                minimum=self.max
                maximum=self.min
                reverse=True
            span=maximum-minimum
            if reverse:
                self.set_value((1-v)*span+minimum)
            else:
                self.set_value(v*span+minimum)

    def h_pgup(self, event=None):
        for _ in range(self.page_steps):
            self.left(event=event)

    def h_pgdn(self, event=None):
        for _ in range(self.page_steps):
            self.right(event=event)

    def h_move(self, event=None):
        if type(event)==dict:
            if event['x']==0:
                self.left()
                return
            elif event['x']==self.w-1:
                self.right()
                return
            v=(event['x']-1)/(self.w-3)
            reverse=False
            minimum=self.min
            maximum=self.max
            if self.min>self.max:
                minimum=self.max
                maximum=self.min
                reverse=True
            span=maximum-minimum
            if reverse:
                self.set_value((1-v)*span+minimum)
            else:
                self.set_value(v*span+minimum)

    def home(self, event=None):
        self.set_value(self.min)

    def end(self, event=None):
        self.set_value(self.max)

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

