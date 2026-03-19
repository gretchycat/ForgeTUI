#!/usr/bin/python3
from __future__ import annotations
import sys, os, fcntl, select, asyncio, time, termios, tty, logging, pyte, re, icat
try:
    from libansiscreen.screen import Screen
    from libansiscreen.renderer.ansi_emitter import ANSIEmitter, Box
    from libansiscreen.color.palette import Palette, create_ansi_256_palette
except:
    Screen=None
from .termcontrol import termcontrol
from .terminput import termInput
from .box_glyphs import grchr, theme

rgb_file_path = '/usr/share/X11/rgb.txt'
CHUNK_SIZE = 4096  # safe per-write chunk
#

p=create_ansi_256_palette().get_colors()

def output(data, fd=sys.stdout.fileno()):
    """Queue a string or bytes for non-blocking terminal output."""
    outbuf = bytearray()  # persistent buffer
    if isinstance(data, str):
        data = data.encode()
    outbuf.extend(data)
    # drain in chunks
    while outbuf:
        chunk = outbuf[:CHUNK_SIZE]
        try:
            n = os.write(fd, chunk)
            del outbuf[:n]
        except BlockingIOError:
            # wait until fd is writable
            select.select([], [fd], [])

class boxDraw:
    def __init__(self, bgColor=24,
                bg0=0, fg0=7,
                chars="",
                frameColors=[],
                title="", statusBar='',
                mode='auto', charset='utf8',
                style='inside',
                ):
        self.screen=None
        self.style=style
        self.term=termcontrol()
        self.fg0, self.bg0=fg0, bg0
        self.bgColor=bgColor
        self.frame={'w':2, 'h':1}
        if len(chars)!=9:
            if style in theme.keys():
                cd=grchr['utf8']
                if charset.lower() in ['utf8', 'utf-8']:
                    cd=grchr['utf8']
                else:
                    cd=grchr['ascii']
                self.chars= f'{cd[theme[style]["TL"]]}{cd[theme[style]["TC"]]}{cd[theme[style]["TR"]]}'\
                            f'{cd[theme[style]["ML"]]}{cd[theme[style]["MC"]]}{cd[theme[style]["MR"]]}'\
                            f'{cd[theme[style]["BL"]]}{cd[theme[style]["BC"]]}{cd[theme[style]["BR"]]}'
            else:
                self.chars="         "
                pass
        else:
            self.chars=chars
        fr=False
        if len(frameColors)!=9:
            fr=True
        if mode in ['sixel', 'kitty', '24bit', '24-bit', 'auto']:
            if fr:
                self.frameColors=['#FFF', '#AAA','#777','#AAA', 0, '#555', '#777','#555','#333']
                self.frameColors=[255, 245, 240, 245, 0, 237, 240, 237, 235]
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

    def draw(self, x=0, y=0, w=0, h=0, fill=True, invert=False, screen=None):
        if screen is None:
            if(w<3): w=3
            if(h<3): h=3
        colors=self.frameColors
        if(self.tinted):
            colors=self.tinted
        if invert:
            colors=self.invert(colors)
            pass
        if screen==None:
            buff=self.term.gotoxy(x,y)
            buff+=self.term.ansicolor(colors[0], self.bgColor)+self.chars[0]
            buff+=self.term.ansicolor(colors[1], self.bgColor)+self.chars[1]*(w-2)
            buff+=self.term.ansicolor(colors[2], self.bgColor)+self.chars[2]
            buff+=self.term.ansicolor(self.fg0, self.bg0)
            for i in range(1,h-1):
                buff+=self.term.gotoxy(x,y+i)+\
                    self.term.ansicolor(colors[3], self.bgColor)+self.chars[3]
                if(fill):
                    buff+=self.term.ansicolor(colors[4], self.bgColor)+self.chars[4]*(w-2)
                else:
                    buff+=self.term.ansicolor(colors[4], self.bgColor)
                    buff+=F"\x1b[{w-2}C"
                buff+=self.term.ansicolor(colors[5], self.bgColor)+self.chars[5]
                buff+=self.term.ansicolor(self.fg0, self.bg0)
            buff+=self.term.gotoxy(x,y+h-1)
            buff+=self.term.ansicolor(colors[6], self.bgColor)+self.chars[6]
            buff+=self.term.ansicolor(colors[7], self.bgColor)+self.chars[7]*(w-2)
            buff+=self.term.ansicolor(colors[8], self.bgColor)+self.chars[8]
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
        else:
            if self.style in ['', 'plot']:
                pass
                #screen.print(self.t.ansicolor(self.bgColor))
                #screen.print(self.t.clear())
                if fill:
                    for y in range(1, screen.height-2):
                        for x in range(1, screen.width-1):
                            screen.put_cell(x,y,char=self.chars[4], fg=p[colors[4]], bg=p[self.bgColor])
                screen.plot(0,0,p[colors[0]])
                screen.plot(screen.width-1,0,p[colors[2]])
                for x in range(1,screen.width-1):
                    screen.plot(x,0,p[colors[1]])
                    screen.plot(x,1,p[self.bgColor])
                    screen.plot(x,screen.height*2-4,p[self.bgColor])
                    screen.plot(x,screen.height*2-3,p[colors[7]])
                for y in range(1, screen.height*2-3):
                    screen.plot(0,y,p[colors[3]])
                    screen.plot(screen.width-1,y,p[colors[5]])
                screen.plot(0,screen.height*2-3,p[colors[6]])
                screen.plot(screen.width-1,screen.height*2-3,p[colors[8]])
            else:
                screen.put_cell(0,0,char=self.chars[0], fg=p[colors[0]], bg=p[self.bgColor])
                screen.put_cell(screen.width-1,0,char=self.chars[2], fg=p[colors[2]], bg=p[self.bgColor])
                for x in range(1, screen.width-1):
                    screen.put_cell(x,0,char=self.chars[1], fg=p[colors[1]], bg=p[self.bgColor])
                    screen.put_cell(x,screen.height-2,char=self.chars[7], fg=p[colors[7]], bg=p[self.bgColor])
                for y in range(1, screen.height-2):
                    screen.put_cell(0,y,char=self.chars[3], fg=p[colors[3]], bg=p[self.bgColor])
                    screen.put_cell(screen.width-1,y,char=self.chars[5], fg=p[colors[5]], bg=p[self.bgColor])
                    if fill:
                        for x in range(1, screen.width-1):
                            screen.put_cell(x,y,char=self.chars[4], fg=p[colors[4]], bg=p[self.bgColor])
                screen.put_cell(0,screen.height-2,char=self.chars[6], fg=p[colors[6]], bg=p[self.bgColor])
                screen.put_cell(screen.width-1,screen.height-2,char=self.chars[8], fg=p[colors[8]], bg=p[self.bgColor]) 
            return screen
        return ''

class widget():
    def __init__(self, x=1, y=1, w=1, h=1, fg=7, bg=0, key=None, action=None):
        self.screen=None
        self.force_refresh=True
        self.fg0=7
        self.bg0=0
        self.invert=False
        self.key=key
        self.action=action
        self.minW=1
        self.minH=1
        self.t=termcontrol()
        self.setSize(x, y, w, h)
        if Screen:
            self.screen=Screen(width=self.w, height=self.h)
        #self.screen=None
        self.setColors(fg, bg)
        self.widgetList=[]
        self.eventList={}
        self.focus=None
        self.parent=None

    def __del__(self):
        pass

    def refresh(self, event=None):
        self.force_refresh=True

    def addEvent(self, trigger, func):
        self.eventList[trigger]=func

    def checkWidgetEvents(self, key, w):
        if self.key not in self.eventList.items():
            self.eventList[self.key]=self.action
        for  k, m in self.eventList.items():
            if k==key or k=='':
                if f'{type(self.eventList[k])}' in [ "function", "<class 'method'>" ,"<class 'function'>"]:
                    self.action=self.eventList[k]
                    if 'method' in f'{type(self.eventList[k])}':
                        self.action(event=key)
                    elif 'function' in f'{type(self.eventList[k])}':
                        self.action(self, event=key)
                else:
                    print(f'{self.t.gotoxy(10,20)}invalid action for "{k}" type: {type(self.eventList[k])}')
        for cw in w.widgetList:
            cw.checkWidgetEvents(key, cw)

    def guiLoop(self, outputmode=[]):
        self.go=True
        self.input=termInput()
        self.input.raw=True
        output(self.t.disable_cursor())
        output(self.t.enable_mouse())
        output(self.t.alt_screen())
        output(self.t.clear())
        #home=self.t.gotoxy(self.x, self.y)
        home=self.t.gotoxy(1, 1)
        origin=self.t.gotoxy(1, 1)
        buffercache=""
        with open("output.log", "w") as log:
            while self.go:
                #resize to full screen
                sz=self.t.get_terminal_size()
                if sz['columns']!=self.w or sz['rows']!=self.h:
                    self.setSize(0,0,0,0)
                    self.resize()
                if self.screen:
                    sbuffer=self.screen.copy()
                buffer=self.draw()
                if type(buffer)==str:
                    if buffer != buffercache or self.force_refresh:
                        self.force_refresh=False
                        buffercache=buffer
                        if(self.screen):
                            sbuffer.print(origin+buffer)
                            out=home+sbuffer.emit_diff(self.screen,raw=True)
                            output(out)
                            #log.write(out)
                            self.screen=sbuffer.copy()
                        else:
                            output(home+buffer)
                else:
                    if self.force_refresh:
                        self.force_refresh=False
                        output(home+buffer.emit(raw=True))
                    else:
                        output(home+buffer.emit_diff(self.screen, raw=True))
                    self.screen=buffer.copy()
                try:
                    sys.stdout.flush()
                except:
                    pass
                for inp in self.input.read_input():
                    if inp != '':
                        self.checkWidgetEvents(inp, self)
        output(self.t.clear())
        output(self.t.enable_cursor())
        output(self.t.disable_mouse())
        output(self.t.normal_screen())
        try:
            sys.stdout.flush()
        except:
            pass

    def quit(self, event=None):
        self.go=False

    def setColors(self, fg, bg):
        self.fg, self.bg=fg, bg

    def setSize(self, x, y, w, h): #should always be okay
        if x<1:
            x=1
        if y<1:
            y=1
        scr=self.t.get_terminal_size()
        if w==0:
            w=scr['columns']
        if h==0:
            h=scr['rows']
        if w<self.minW:
            w=self.minW
        if h<self.minH:
            h=self.minH
        if x>scr['columns']-self.minW:
            x=scr['columns']-self.minW
        if y>scr['rows']-self.minH:
            y=scr['rows']-self.minH
        if w>scr['columns']-x+1:
            w=scr['columns']-x+1
        if h>scr['rows']-y+1:
            h=scr['rows']-y+1
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        if self.screen:
            self.screen.resize(w, h)

    def addWidget(self, widget):
        widget.parent=self
        widget.fg0=self.fg
        widget.bg0=self.bg
        self.widgetList.append(widget)
        return self.widgetList[-1]

    def resize(self, event=None):
        for w in self.widgetList:
            w.resize(event)

    def drawChildren(self, screen=None):
        if screen:
            buffer=''
            for w in self.widgetList:
                ch=w.draw()
                if type(ch)==str:
                    screen.print(ch)
                    buffer+=ch
                else:
                    screen.paste(w.screen, box=(w.x,w.y,w.w,w.h))
            return buffer
        else:
            buffer=''
            for w in self.widgetList:
                buffer+=w.draw()
            return buffer

    def draw(self):
        return self.drawChildren(screen=self.screen)

    def setFocus(self):
        pass

    def onFocus(self):
        pass

    def onDeFocus(self):
        pass

    def mouseEvent(self, x, y, buttons):
        pass

    def kbEvent(self, ch):
        pass

    def save(self, f):
        pass

    def load(self, f):
        pass

