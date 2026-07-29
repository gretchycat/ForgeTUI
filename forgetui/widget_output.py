#!/usr/bin/python3
from __future__ import annotations
import uuid, math

from libansiscreen.screen_ops.spixel import MODE_BRAILLE, MODE_OCTANT, MODE_QUADRANT, MODE_SEXTANT
from .theme import make_theme
from libansiscreen.color.rgb import Color
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
        bn=self.box_name
        t=self.theme.get(self.box_type)
        if not t:
            t=self.theme.get('focus')
        if isinstance(t, dict) and self.style is not None:
            tl=t[f'{bn}.top_left']
            tc=t[f'{bn}.top_center']
            tr=t[f'{bn}.top_right']
            ml=t[f'{bn}.middle_left']
            mc=t[f'{bn}.middle_center']
            mr=t[f'{bn}.middle_right']
            bl=t[f'{bn}.bottom_left']
            bc=t[f'{bn}.bottom_center']
            br=t[f'{bn}.bottom_right']
            if self.style in ['plot', MODE_BRAILLE,MODE_QUADRANT,MODE_SEXTANT,MODE_OCTANT]:
                if fill:
                    for y in range(1, fb.height):
                        for x in range(1, fb.width):
                            fb.set_cell(x,y,mc)
                if self.style=='plot':
                    for x in range(1,fb.width-1):
                        fb.plot(x,0,tc.fg)
                        fb.plot(x,1,mc.bg)
                        fb.plot(x,fb.height*2-1,bc.fg)
                    for y in range(1, (fb.height)*2-1):
                        fb.plot(0,y,ml.fg)
                        fb.plot(1,y,mc.bg)
                        fb.plot(fb.width-2,y,mc.bg)
                        fb.plot(fb.width-1,y,mr.fg)
                    fb.plot(0,0,tl.fg)
                    fb.plot(fb.width-1,0,tr.fg)
                    fb.plot(0,(fb.height)*2-1,bl.fg)
                    fb.plot(fb.width-1,(fb.height)*2-1,br.fg)
                else:
                    for x in range(1,fb.width-1):
                        fb.put_cell(x,0,fg=tc.fg, bg=mc.bg)
                        fb.put_cell(x,fb.height-1,fg=bc.fg, bg=mc.bg)
                    for y in range(1, (fb.height)-1):
                        fb.put_cell(0,y,fg=ml.fg, bg=mc.bg)
                        fb.put_cell(fb.width-1,y,fg=mr.fg, bg=mc.bg)
                    fb.put_cell(0,0,fg=tl.fg, bg=mc.bg)
                    fb.put_cell(fb.width-1,0,fg=tr.fg, bg=mc.bg)
                    fb.put_cell(0,(fb.height)-1,fg=bl.fg, bg=mc.bg)
                    fb.put_cell(fb.width-1,(fb.height)-1,fg=br.fg, bg=mc.bg)
                    y_mul=2
                    x_mul=2
                    match self.style:
                        case 'braille' | 'octant':
                            y_mul=4
                        case 'sextant':
                            y_mul=3
                        case 'quadrant':
                            pass
                    for x in range(1,fb.width*x_mul-1):
                        fb.plot(x,0,True,mode=self.style)
                        fb.plot(x,fb.height*y_mul-1,True,mode=self.style)
                    for y in range(0, (fb.height)*y_mul):
                        fb.plot(0,y,True,mode=self.style)
                        fb.plot(fb.width*x_mul-1,y,True,mode=self.style)
            else:
                fb.set_cell(0,0,tl)
                fb.set_cell(fb.width-1,0,tr)
                for x in range(1, fb.width-1):
                    fb.set_cell(x,0,tc)
                    fb.set_cell(x,fb.height-1,bc)
                for y in range(1, fb.height-1):
                    fb.set_cell(0,y,ml)
                    fb.set_cell(fb.width-1,y,mr)
                    if fill:
                        for x in range(1, fb.width-1):
                            fb.set_cell(x,y,mc)
                fb.set_cell(0,fb.height-1,bl)
                fb.set_cell(fb.width-1,fb.height-1,br)
        return super().draw()

class WidgetLabel(Widget): #a blurb of text made into a widget.it can be justified, have text attributes and colored
    def __init__(self, x=0, y=0, w=1.0, h=1, fg=7, bg=None, \
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
    def __init__(self, x=0, y=0, w=1.0, h=1, fg=7, bg=None, \
                name='Marquee '+str(uuid.uuid4()), parent=None,\
                text='marquee', direction='ltr', speed=0.05):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg,\
                name=name, parent=parent, text=text, align='left')
        self.o_text=text
        self.text_offset=0
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
        self.makeDirty()

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

class WidgetProgressBar(Widget): #a bar going from 0% to 100%
    def __init__(self, x=0, y=0, w=1.0, h=1, fg=4, bg=15, \
                 name='Progress Bar '+str(uuid.uuid4()), parent=None, total=1.0):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg,\
                         name=name, parent=parent)
        self.progress=0
        self.total=total
        pass

    def set_progress(self, p):
        self.progress=p
        self.makeDirty()

    def set_total(self, t):
        self.total=t
        self.makeDirty()

    def draw(self):
        pct=self.progress/self.total
        for y in range(self.h):
            for x in range(self.w):
                bg=self.bg
                fg=self.fg
                if pct<=(x/(self.w)):
                    bg=self.fg
                    fg=self.bg
                self.fb.put_cell(x,y,char=' ',fg=fg,bg=bg)
        pctstr=f'{int(pct*100)}%'
        px=int(self.w/2-len(pctstr)/2)
        py=self.h//2
        self.fb.cursor.set(px,py)
        self.fb.put_text(pctstr, raw=True)

class WidgetGraph(Widget): #TODO: different graph types
    pass
