#!/usr/bin/python3
from __future__ import annotations
import sys, os, fcntl, asyncio, time, re, icat
try:
    from libansiscreen.screen import Screen
except:
    Screen=None
from .termkeymap import gen_keymap
from .widget import widget, boxDraw

class widgetProgressBar(widget):
    pass

class widgetSlider(widget):
    pass

class widgetSlider(widget):
   pass

class widgetScreen(widget):
    def __init__(self, x, y, w, h, fg=7, bg=None, style=None):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg)
        self.style=style
        self.box=None
        if style:
            self.box=boxDraw(style=style, bgColor=self.bg, bg0=self.bg0)
        fw=0
        fh=0
        if(self.box):
            fw=self.box.frame['w']*2
            fh=self.box.frame['h']*2
        self.content=Screen(width=max(1,w-fw), height=max(1,h-fh))
        self.style=style
        self.content.print(self.t.ansicolor(fg=fg,bg=bg))
        self.content.print(self.t.clear())
        self.content.print(self.t.gotoxy(1,1))
        self.scroll_x=0
        self.scroll_y=-1
        self.resize()
        self.scroll_type='cursor' #'eof'
        self.show_x_scrollbar=False
        self.show_y_scrollbar=False

    def resize(self, event=None):
        super().resize()
        fw=0
        fh=0
        if(self.box):
            fw=self.box.frame['w']*2
            fh=self.box.frame['h']*2
        self.content.resize(max(self.screen.width-fw, self.content.width),
                        max(self.screen.height-fh, self.content.height))

    def feed(self, s):
        self.content.print(s)

    def draw(self):
        self.fg0=7
        self.bg0=0
        if self.parent:
            self.fg0=self.parent.fg
            self.bg0=self.parent.bg
        x,y=self.scroll(self.scroll_x, self.scroll_y)
        fw=0
        fh=0
        if(self.box):
            fw=self.box.frame['w']*2
            fh=self.box.frame['h']*2
            self.box.draw(0, 0, self.w, self.h, screen=self.screen)
        scrolled=self.content
        if self.scroll_x==0 and self.scroll_y==0:
            self.screen.paste(self.content,
                box=(fw//2, fh//2, self.screen.width-fw,
                     self.screen.height-fh-1))
        else:
            scrolled=self.content.copy(box=(x,y,
                    self.screen.width-fw,self.screen.height-fh))
            self.screen.paste(scrolled,
                box=(fw//2, fh//2, self.screen.width-fw,
                     self.screen.height-fh-1))
        self.drawChildren(self.screen)
        return self.screen

    def scroll(self, x=0, y=-1):
        fw,fh=0,0
        if self.box:
            fw=self.box.frame['w']*2
            fh=self.box.frame['h']*2
        self.scroll_x=x
        self.scroll_y=y
        if self.scroll_type=='eof':
            x_max=max(0, self.content.width-(self.screen.width-fw))
            y_max=max(0, self.content.height-(self.screen.height-fh))
        if self.scroll_type=='cursor':
            x_max=max(0, self.content.cursor.x-(self.screen.width-1-fw))
            y_max=max(0, self.content.cursor.y-(self.screen.height-1-fh))
        if self.scroll_type=='cursor_center':
            x_max=max(0, self.content.cursor.x-(self.screen.width-1-fw)//2)
            y_max=max(0, self.content.cursor.y-(self.screen.height-1-fh)//2)
        if x<0 or x>x_max:
            x=x_max
            self.scroll_x=-1
        if y<0 or y>y_max:
            y=y_max
            self.scroll_y=-1
        return x,y

    def onFocus(self):
        pass

    def onDeFocus(self):
        pass

    def mouseEvent(self, x, y, buttons):
        pass

    def kbEvent(self, ch):
        pass


