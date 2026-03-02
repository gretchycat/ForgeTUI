#!/usr/bin/python3
from __future__ import annotations
import sys, os, fcntl, select, asyncio, time, termios, tty, logging, pyte, re, icat
try:
    from libansiscreen.screen import Screen
    from libansiscreen.renderer.ansi_emitter import ANSIEmitter, Box
except:
    Screen=None
from .widget import widget
from .termcontrol import termcontrol
from .box_glyphs import grchr, theme

class widgetProgressBar(widget):
    def __init__(self, x, y, w, h, fg=7, bg=0, p0='\u2591', p1='\u2588', note=''):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg)
        self.p0, self.p1=p0,p1
        self.note=note

    def draw(self, progress, total):
        buffer=self.t.gotoxy(self.x, self.y)
        buffer+=self.t.ansicolor(self.fg, self.bg)
        buffer+=self.note
        pct=0
        if total>0:
            pct=progress/total
        w=self.w-len(self.note)
        buffer +=self.p1*int((pct)*w)
        buffer +=self.p0*int(w-((pct)*w))
        buffer +=f'{self.t.gotoxy(self.x+len(self.note)+int(w/2)-5,self.y)}{progress}/{total}'
        return buffer

class widgetSlider(widget):
    def __init__(self, x, y, w, min=0, max=100, bg=233, barColor=238, labelColor=244, labelType="int", sliderColor=27, key=None, action=None):
        super().__init__(x=x, y=y, w=w, h=1, bg=bg, key=key, action=action)
        self.slider='\u2561\u2592\u255e'
        self.bar='\u2560\u2550\u2563'
        self.pos=min
        self.min=min
        self.max=max
        self.barColor=barColor
        self.labelColor=labelColor
        self.labelType=labelType
        self.sliderColor=sliderColor

    def draw(self):
        def hmsf(s):
            s = int(s)
            minutes = s / 60
            seconds = s % 60
            return f"{int(minutes):02d}:{int(seconds):02d}"
        if self.parent:
            self.fg0=self.parent.fg
            self.bg0=self.parent.bg
        LLabel=""
        RLabel=""
        if self.labelType=='int':
            LLabel=f'{self.min}'
            RLabel=f'{self.max}'
        elif self.labelType=='time':
            LLabel=f'{hmsf(self.min)}'
            RLabel=f'{hmsf(self.max)}'
        else:
            pass
        barw=self.w-len(LLabel)-len(RLabel)-2-len(self.slider)-2
        pos=0
        if (self.max-self.min)>0:
            pos=self.pos/(self.max-self.min)
        spos=int((barw)*pos)
        buffer=self.t.gotoxy(self.x, self.y)
        buffer+=self.t.ansicolor(self.labelColor, self.bg0)
        buffer+=LLabel
        buffer+=self.t.ansicolor(self.barColor)
        buffer+=self.bar[0]
        buffer+=self.bar[1]*(spos)
        buffer+=self.t.ansicolor(self.sliderColor)
        buffer+=self.slider
        buffer+=self.t.ansicolor(self.barColor)
        buffer+=self.bar[1]*((barw-spos))
        buffer+=self.bar[2]
        buffer+=self.t.ansicolor(self.labelColor)
        buffer+=RLabel
        if self.outstream:
            self.outstream.write(buffer)
        return buffer

    def setValue(self, value):
        if value>=self.min and value<=self.max:
            self.pos=value
        if value>self.max:
            self.pos=self.max
        if value<self.min:
            self.pos=self.min

    def setMin(self, value):
        self.min=value
        self.setValue(self.pos)

    def setMax(self, value):
        self.max=value
        self.setValue(self.pos)

class widgetButton(widget):
    def __init__(self, x, y, w, h, fg=7, bg=None, style='curve', caption='Button', key=None, action=None, toggle=None):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, key=key, action=action)
        self.bg0=0
        self.fg0=7
        self.invert=False
        if theme:
            if style:
                self.box=boxDraw(style=style, bgColor=self.bg, bg0=self.bg0)
        else:
            self.box=None
        self.tint=None
        self.style=style
        self.caption=caption

    def draw(self):
        if self.parent:
            self.fg0=self.parent.fg
            self.bg0=self.parent.bg
        buffer=""
        if self.box:
            self.box.bg0=self.bg0
            self.box.tintFrame(self.tint)
            buffer+=self.box.draw(self.x, self.y, self.w, self.h, invert=self.invert)
        self.invert=False
        buffer+=self.t.gotoxy(self.x+self.w//2-(len(self.caption)//2), self.y+1)
        buffer+=self.t.ansicolor(self.fg, self.bg)
        buffer+=self.caption
        if self.key:
            buffer +=self.t.gotoxy(self.x+self.w//2-((len(self.key)+2)//2), self.y+2)
            buffer+=f'[{self.key}]'
        return buffer

class pyteLogger(logging.Logger):
    def __init__(self, refresh_class=None):
        logging.__init__('pyte')
        self.refresh_class=refresh_class

    def debug(self, msg, *args, **kwargs):
        logging.debug(clean(msg), *args, **kwargs)
        if self.refresh_class: self.refresh_class.refresh()

    def info(self, msg, *args, **kwargs):
        logging.info(clean(msg), *args, **kwargs)
        if self.refresh_class: self.refresh_class.refresh()

    def warning(self, msg, *args, **kwargs):
        logging.warning(clean(msg), *args, **kwargs)
        if self.refresh_class: self.refresh_class.refresh()

    def error(self, msg, *args, **kwargs):
        logging.error(clean(msg), *args, **kwargs)
        if self.refresh_class: self.refresh_class.refresh()

    def critical(self, msg, *args, **kwargs):
        logging.critical(clean(msg), *args, **kwargs)
        if self.refresh_class: self.refresh_class.refresh()
        exit()

class boxDraw:
    def __init__(self, bgColor=24,
                bg0=0, fg0=7,
                chars="",
                frameColors=[],
                title="", statusBar='',
                mode='auto', charset='utf8',
                style='inside',
                ):
        self.term=termcontrol()
        self.fg0, self.bg0=fg0, bg0
        self.bgColor=bgColor
        if len(chars)!=9:
            cd=grchr['utf8']
            if charset.lower() in ['utf8', 'utf-8']:
                cd=grchr['utf8']
            else:
                cd=grchr['ascii']
            self.chars=f'{cd[theme[style]["TL"]]}{cd[theme[style]["TC"]]}{cd[theme[style]["TR"]]}'\
                        f'{cd[theme[style]["ML"]]}{cd[theme[style]["MC"]]}{cd[theme[style]["MR"]]}'\
                        f'{cd[theme[style]["BL"]]}{cd[theme[style]["BC"]]}{cd[theme[style]["BR"]]}'
        else:
            self.chars=chars
        fr=False
        if len(frameColors)!=9:
            fr=True
        if mode in ['sixel', 'kitty', '24bit', '24-bit', 'auto']:
            if fr:
                self.frameColors=['#FFF', '#AAA','#777','#AAA', 0, '#555', '#777','#555','#333']
            if type(bgColor)==int and bgColor>255:
                self.bgColor=0
            else:
                self.bgColor=bgColor
        elif mode in ['8bit', '8-bit', '256color', '8bitgrey', 'grey', '8bitbright']:
            if fr:
                self.frameColors=[255, 245, 240, 245, 0, 237, 240, 237, 235]
            if type(bgColor)!=int or bgColor>255:
                self.bgColor=0
            else:
                self.bgColor=bgColor
        elif mode in ['4bit', '4-bit', '16color', '4bitgrey']:
            if fr:
                self.frameColors=[15, 7, 8, 7, 0, 8, 7, 8, 0]
            if type(bgColor)!=int or bgColor>15:
                self.bgColor=0
            else:
                self.bgColor=bgColor
        else:
            if fr:
                self.frameColors=[7, 7, 7, 7, 0, 7, 7, 7, 7]
            self.bgColor=0
        self.tinted=None
        self.title=title
        self.statusBar=statusBar

    def setColors(self, bgcolor, frameColors):
        self.bgColor=bgColor
        self.frameColors=frameColors

    def tintFrame(self, color):
        if color==None:
            self.tinted=None
            return
        c=self.term.getRGB(color)
        r, g, b=c['red'], c['green'], c['blue']
        r=r/255.0
        g=g/255.0
        b=b/255.0
        self.tinted=[]
        for i in range(0, len(self.frameColors)):
            c=self.term.getRGB(i)
            fr,fg,fb=c['red'], c['green'], c['blue']
            fr=int(fr/16*r)
            fg=int(fg/16*g)
            fb=int(fb/16*b)
            self.tinted.append(F"#{fr:X}{fg:X}{fb:X}")

    def unTintFrame(self):
        self.tinted=None

    def setCharacters(self):
        self.chars=chars

    def invert(self, cl):
        c=cl.copy()
        for i in range(0, len(cl)):
            c[i]=cl[8-i]
        return c

    def draw(self, x, y, w, h, fill=True, invert=False):
        if(w<3): w=3
        if(h<3): h=3
        colors=self.frameColors
        if(self.tinted):
            colors=self.tinted
        if invert:
            colors=self.invert(colors)
            pass
        buff=self.term.gotoxy(x,y)
        buff+=self.term.ansicolor(colors[0], self.bg0)+self.chars[0]
        buff+=self.term.ansicolor(colors[1], self.bg0)+self.chars[1]*(w-2)
        buff+=self.term.ansicolor(colors[2], self.bg0)+self.chars[2]
        buff+=self.term.ansicolor(self.fg0, self.bg0)
        for i in range(1,h-1):
            buff+=self.term.gotoxy(x,y+i)+\
                self.term.ansicolor(colors[3], self.bg0)+self.chars[3]
            if(fill):
                buff+=self.term.ansicolor(colors[4], self.bgColor)+self.chars[4]*(w-2)
            else:
                buff+=self.term.ansicolor(colors[4], self.bgColor)
                buff+=F"\x1b[{w-2}C"

            buff+=self.term.ansicolor(self.fg0, self.bg0)
            buff+=self.term.ansicolor(colors[5], self.bg0)+self.chars[5]
            buff+=self.term.ansicolor(self.fg0, self.bg0)
        buff+=self.term.gotoxy(x,y+h-1)
        buff+=self.term.ansicolor(colors[6], self.bg0)+self.chars[6]
        buff+=self.term.ansicolor(colors[7], self.bg0)+self.chars[7]*(w-2)
        buff+=self.term.ansicolor(colors[8], self.bg0)+self.chars[8]
        buff+=self.term.ansicolor(self.fg0, self.bg0)
        if self.title!='':
            desc=self.title
            descX=int(x+(w/2)-(len(desc)/2))+1
            descY=int(y)
            descPos=self.move(descX, descY)
            descColor=self.term.ansicolor(16, colors[1])
            buff+=f'{descPos}{descColor}{desc}'
            buff+=self.term.ansicolor(self.fg0, self.bg0)
        if self.statusBar!='':
            pass
        return buff

class widgetScreen(widget):
    def __init__(self, x, y, w, h, fg=7, bg=None, style=None):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg)
        if style:
            self.box=boxDraw(style=style, bgColor=self.bg, bg0=self.bg0)
        else:
            self.box=None
        self.style=style
        self.resize()
        self.feed=self.stream.feed

    def resize(self):
        super().resize()
        self.minW=5
        self.minH=5
        if self.box:
            self.pscreen = pyte.Screen(self.w-4, self.h-2)
            self.pscreen.screen_lines=self.h-2
        else:
            self.pscreen = pyte.Screen(self.w, self.h)
            self.pscreen.screen_lines=self.h
        self.pscreen.mode.add(pyte.modes.LNM)
        self.pscreen.encoding='utf-8'
        self.stream = pyte.Stream(self.pscreen)
        self.stream.write=self.stream.feed

    def draw(self):
        self.fg0=7
        self.bg0=0
        if self.parent:
            self.fg0=self.parent.fg
            self.bg0=self.parent.bg
        if self.style in [ 'outside' ]:
            self.bg0=self.bg
        if self.style in [ 'inside' ]:
            self.box.chars=self.box.chars[:4]+' '+self.box.chars[5:]
        buffer=''
        if(self.box):
            self.box.bg0=self.bg0
            buffer+=self.box.draw(self.x, self.y, self.w, self.h)
        self.stream.feed(self.t.ansicolor(self.fg, self.bg))
        self.stream.feed(super().drawChildren())
        self.stream.feed(self.t.gotoxy(1, self.pscreen.screen_lines))
        if self.box:
            buffer+=self.t.pyte_render(self.x+2, self.y+1, self.pscreen, fg=self.fg, bg=self.bg)
        else:
            buffer+=self.t.pyte_render(self.x, self.y, self.pscreen, fg=self.fg, bg=self.bg)
        if self.outstream:
            self.outstream.write(buffer)
        return buffer

    def input(self, str, maxlen=50):
        if maxlen < 1:
            maxlen=1
        if self.box:
            buffer = self.t.gotoxy(self.pscreen.cursor.x+self.x+2, self.pscreen.cursor.y+self.y+1)
        else:
            buffer = self.t.gotoxy(self.pscreen.cursor.x+self.x, self.pscreen.cursor.y+self.y)
        buffer+=str
        buffer +=self.t.reset()+' '*maxlen+self.t.left(maxlen)
        return input(buffer) #, maxlen=maxlen)

    def onFocus(self):
        pass

    def onDeFocus(self):
        pass

    def mouseEvent(self, x, y, buttons):
        pass

    def kbEvent(self, ch):
        pass


