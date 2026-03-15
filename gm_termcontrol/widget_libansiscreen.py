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
        if style:
            self.box=boxDraw(style=style, bgColor=self.bg, bg0=self.bg0)
            self.content=Screen(width=max(1,w-4), height=max(1,h-2))
        else:
            self.box=None
            self.content=self.screen
        self.style=style
        if bg is not None:
            self.content.print(self.t.ansicolor(bg=bg))
            self.content.print(self.t.clear())
        self.scroll=-1;
        self.resize()

    def resize(self):
        super().resize()
        if self.box:
            self.content.resize(max(self.screen.width-4, self.content.width),
                        max(self.screen.height-2, self.content.height))
        else:
            pass

    def feed(self, s):
        self.content.print(s)

    def draw(self):
        self.fg0=7
        self.bg0=0
        if self.parent:
            self.fg0=self.parent.fg
            self.bg0=self.parent.bg
        if(self.box):
            self.box.draw(0, 0, self.w-1, self.h-1, screen=self.screen)
            dy=0
            dx=0
            if self.scroll==-1:
                s=3
                if self.style==None:
                    s=1
                dy=self.content.height-(self.screen.height-s)
                pass
            scrolled=self.content.copy(box=(dx,dy,self.screen.width-4,self.screen.height-3))
            self.screen.paste(scrolled,
                    box=(2, 1, self.screen.width-5, self.screen.height-3))
        self.drawChildren(self.screen)
        return self.screen

    def onFocus(self):
        pass

    def onDeFocus(self):
        pass

    def mouseEvent(self, x, y, buttons):
        pass

    def kbEvent(self, ch):
        pass


