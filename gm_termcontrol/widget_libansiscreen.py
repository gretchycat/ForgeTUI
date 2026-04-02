#!/usr/bin/python3
from __future__ import annotations
import sys, os, fcntl, asyncio, time, re, icat
from libansiscreen.screen import Screen
from libansiscreen.color.palette import Palette, create_ansi_256_palette
from .termkeymap import gen_keymap
from .widget import Widget, boxDraw

p=create_ansi_256_palette().get_colors()

class frameDraw(boxDraw):
    def __init__(self, bgColor=0,
                bg0=0, fg0=7,
                chars="",
                frameColors=[],
                mode='auto', charset='utf8',
                style='inside',
                scrollbar_bg=7,
                scrollbar_fg=0,
                widget=None,
                ):
        super().__init__(bgColor=bgColor,bg0=bg0,fg0=fg0,
                         chars=chars,frameColors=frameColors,
                         mode=mode,charset=charset,style=style)
        self.widget=widget
        self.scrollbar_bg=scrollbar_bg
        self.scrollbar_fg=scrollbar_fg
        #TODO add scrollbar mouse controls

    def draw(self, x=0, y=0, w=0, h=0,
             fill=True,  invert=False,
             screen=None,
             show_vsb=False,
             show_hsb=False,
             sx=0,sx_max=0,
             sy=0,sy_max=0,
             ):
        frame=super().draw(x=x, y=y, w=w, h=h,
                           fill=fill, invert=invert, screen=screen)
        c=[ '↑', '|', '↓']
        sh,sv=0,0
        if self.widget.x_max>0:
            sh=int((w-5)*(self.widget.sx/self.widget.x_max))
        if self.widget.y_max>0:
            sv=int((h-5)*(self.widget.sy/self.widget.y_max))
        if(screen):
            if show_vsb:
                screen.put_cell(w-1,1,char=self.chars[9],
                        fg=p[self.scrollbar_fg], bg=p[self.scrollbar_bg])
                for y in range(2,h-2):
                    screen.put_cell(w-1,y,char=self.chars[13],
                            fg=p[self.scrollbar_fg], bg=p[self.scrollbar_bg])
                screen.put_cell(w-1,2+sv,char=self.chars[15],
                        fg=p[self.scrollbar_fg], bg=p[self.scrollbar_bg])
                screen.put_cell(w-1,h-2,char=self.chars[10],
                        fg=p[self.scrollbar_fg], bg=p[self.scrollbar_bg])
            if show_hsb:
                pass
                screen.put_cell(1,h-1,char=self.chars[11],
                        fg=p[self.scrollbar_fg], bg=p[self.scrollbar_bg])
                for x in range(2,w-2):
                    screen.put_cell(x,h-1,char=self.chars[14],
                            fg=p[self.scrollbar_fg], bg=p[self.scrollbar_bg])
                screen.put_cell(w-2,h-1,char=self.chars[12],
                        fg=p[self.scrollbar_fg], bg=p[self.scrollbar_bg])
                screen.put_cell(2+sh,h-1,char=self.chars[15],
                        fg=p[self.scrollbar_fg], bg=p[self.scrollbar_bg])
        return frame

class widgetProgressBar(Widget):
    pass

class widgetSlider(Widget):
    pass

class widgetButton(Widget):
   pass

class widgetScreen(Widget):
    def __init__(self, x, y, w, h, fg=7, bg=None, style=None, title=''):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg)
        self.show_x_scrollbar=True
        self.show_y_scrollbar=True
        self.title=title
        self.style=style
        self.reorder=True
        self.frame=None
        if style:
            self.frame=frameDraw(style=style, bgColor=self.bg,
                                 bg0=self.bg0, widget=self)
        fw=0
        fh=0
        if(self.frame):
            fw=self.frame.frame['w']*2
            fh=self.frame.frame['h']*2
        self.content=Screen(width=max(1,w-fw), height=max(1,h-fh))
        self.style=style
        self.content.print(self.t.ansicolor(fg=fg,bg=bg))
        self.content.print(self.t.clear())
        self.scroll_x=0
        self.scroll_y=-1
        self.resize()
        self.scroll_type='cursor'

    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.title})"

    def resize(self, event=None):
        super().resize()
        fw=0
        fh=0
        if(self.frame):
            fw=self.frame.frame['w']*2
            fh=self.frame.frame['h']*2
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
        if(self.frame):
            fw=self.frame.frame['w']*2
            fh=self.frame.frame['h']*2
            self.frame.draw(0, 0, self.w, self.h, screen=self.screen,
                            show_vsb=self.show_y_scrollbar,
                            show_hsb=self.show_x_scrollbar)
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
        if self.frame:
            fw=self.frame.frame['w']*2
            fh=self.frame.frame['h']*2
        self.scroll_x=x
        self.scroll_y=y
        if self.scroll_type=='cursor':
            self.x_max=max(0, self.content.cursor.x-(self.screen.width-1-fw))
            self.y_max=max(0, self.content.cursor.y-(self.screen.height-1-fh))
        if self.scroll_type=='cursor_center':
            self.x_max=max(0, self.content.cursor.x-(self.screen.width-1-fw)//2)
            self.y_max=max(0, self.content.cursor.y-(self.screen.height-1-fh)//2)
        if x<0 or x>self.x_max:
            x=self.x_max
            self.scroll_x=-1
        if y<0 or y>self.y_max:
            y=self.y_max
            self.scroll_y=-1
        self.sx=x
        self.sy=y
        return x, y

    def onFocus(self):
        pass

    def onDeFocus(self):
        pass

    def mouseEvent(self, x, y, buttons):
        pass

    def kbEvent(self, ch):
        pass


