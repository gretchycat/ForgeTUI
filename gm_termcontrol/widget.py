#!/usr/bin/python3
from __future__ import annotations
import sys, os, fcntl, select, asyncio, time, termios, tty, re
from libansiscreen.screen import Screen
from libansiscreen.renderer.ansi_emitter import ANSIEmitter, Box
from libansiscreen.color.palette import Palette, create_ansi_256_palette
from .termcontrol import termcontrol
from .terminput import termInput
from .box_glyphs import grchr, theme
import signal

rgb_file_path = '/usr/share/X11/rgb.txt'
CHUNK_SIZE = 4096  # safe per-write chunk

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
                frameColors=[],
                chars='',
                mode='auto', charset='utf8',
                style='inside',
                ):
        self.screen=None
        self.style=style
        self.term=termcontrol()
        self.fg0, self.bg0=fg0, bg0
        self.bgColor=bgColor
        self.frame={'w':2, 'h':1}
        if len(chars)!=17:
            if style in theme.keys():
                cd=grchr['utf8']
                if charset.lower() in ['utf8', 'utf-8']:
                    cd=grchr['utf8']
                else:
                    cd=grchr['ascii']
                self.chars= f'{cd[theme[style]["TL"]]}{cd[theme[style]["TC"]]}{cd[theme[style]["TR"]]}'\
                            f'{cd[theme[style]["ML"]]}{cd[theme[style]["MC"]]}{cd[theme[style]["MR"]]}'\
                            f'{cd[theme[style]["BL"]]}{cd[theme[style]["BC"]]}{cd[theme[style]["BR"]]}'\
                            f'{cd[theme[style]["SU"]]}{cd[theme[style]["SD"]]}{cd[theme[style]["SL"]]}{cd[theme[style]["SR"]]}'\
                            f'{cd[theme[style]["SVR"]]}{cd[theme[style]["SHR"]]}{cd[theme[style]["SH"]]}{cd[theme[style]["SC"]]}'
            else:
                self.chars="         ^v<>:-O*"
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
        if self.style in ['', 'plot']:
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

class Widget():
    def __init__(self, x=0, y=0, w=1, h=1, fg=7, bg=0):
        self.log_file=None
        self.force_refresh=True
        self.screen=None
        self.focus=False
        self.reotder=False
        self.child_focus=False
        self.hidden=False
        self.fg0=7
        self.bg0=0
        self.invert=False
        self.minW=1
        self.minH=1
        self.t=termcontrol()
        self.setSize(x, y, w, h)
        self.screen=Screen(width=self.w, height=self.h)
        self.setColors(fg, bg)
        self.widgetList=[]
        self.eventList={}
        self.focus=None
        self.parent=None

    def suspend(self, signum, frame):
        output(self.t.disable_mouse())
        output(self.t.enable_cursor())
        output(self.t.normal_screen())
        output("Preparing for suspend\n")
        os.kill(os.getpid(), signal.SIGSTOP)

    def resume(self, signum, frame):
        output(self.t.enable_mouse())
        output(self.t.disable_cursor())
        output(self.t.alt_screen())
        output("Resuming\n")

    def stop(self, signum, frame):
        output(self.t.normal_screen())
        output('Quit requested. Stopping\n')
        output(self.t.alt_screen())
        self.quit()

    def __del__(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(id={id(self):x})"

    def log(self, string):
        winfo = repr(self)
        root = self
        while root.parent:
            root = root.parent
        if root.log_file:
            root.log_file.write(f"{winfo}: {string}\n")
            root.log_file.flush()

    def offset(self):
        pox, poy=0,0
        w=self
        while w.parent:
            pox,poy=w.parent.offset()
            w=w.parent
        return pox+self.x, poy+self.y

    def coordinate_in_widget(self, x, y):
        if self.hidden:
            return False
        ox,oy=self.offset()
        rx=x-ox+1
        ry=y-oy+1
        return  0<=rx<self.w and 0<=ry<self.h

    def widget_at_coordinate(self, x,y):
        root=self
        while root.parent:
            root=root.parent
        stack=[ root ]
        full_stack=[]
        while stack:
            node=stack.pop()
            full_stack.append(node)
            for n in reversed(node.widgetList):
                stack.append(n)
        widgets=[]
        for w in full_stack:
            if w.coordinate_in_widget(x,y):
                widgets.append(w)
        self.log(str(widgets))
        for w in widgets:
            if w != root:
                if w.focus:
                    return w
        if widgets:
            return widgets[-1]
        return None

    def rel_event(self, event=None):
        if type(event)==dict:
            ox,oy=self.offset()
            revent=event.copy()
            revent['x']=event['x']-ox+1
            revent['y']=event['y']-oy+1
            if  0<=revent['x']<self.w and 0<=revent['y']<self.h:
                return revent
            return ''
        return event

    def set_focus(self):
        root=self
        while root.parent:
            root=root.parent
        #deactivate all widgets and clear child focus
        defocused=None
        stack=[ root ]
        while stack:
            node=stack.pop()
            if node.focus:
                defocused=node
            node.focus=False
            node.child_focus=False
            for n in node.widgetList:
                stack.append(n)
        #activate self and set child_focus on all parents
        node=self
        self.focus=True
        self.hidden=False
        while node.parent:
            node=node.parent
            node.child_focus=True
        if self.reorder:
            stack=[ root ]
            while stack:
                node=stack.pop()
                move=None
                for n in node.widgetList:
                    stack.append(n)
                    if n.focus or n.child_focus:
                        move=n
                if move:
                    node.widgetList.remove(move)
                    node.widgetList.append(move)
        if self!=defocused:
            if defocused:
                defocused.on_defocus()
            self.on_focus()

    def next_focus(self): #FIXME
        root=self
        while root.parent:
            root=root.parent
        found=False
        stack=[ root ]
        while stack:
            node=stack.pop()
            if found:
                node.set_focus()
                return node
            if node==self:
                found=True
            for n in node.widgetList:
                stack.append(n)

    def prev_focus(self): #FIXME
        root=self
        while root.parent:
            root=root.parent
        stack=[ root ]
        while stack:
            node=stack.pop()
            if node==self:
                if stack:
                    prev=stack.pop()
                    prev.set_focus()
                    return prev
            for n in node.widgetList:
                stack.append(n)

    def hide(self, next='parent'):
        if next=='parent':
            if self.parent:
                self.parent.set_focus()
                self.hidden=True
                return True
        if next=='next':
            self.next_focus()
            return True
        if next=='prev':
            self.prev_focus()
            return True
        elif isinstance(next, Widget):
            if next!=self:
                next.set_focus()
                self.hidden=True
                return True
        return False

    def unhide(self, activate=True):
        self.hidden=False
        if activate:
            self.set_focus()
        return True

    def refresh(self, event=None):
        self.force_refresh=True

    def addEvent(self, trigger, func, persist=False):
        self.eventList[trigger]={ 'func':func, 'persist':persist }

    def check_mouse_focus_change(self, event):
        if type(event)==dict:
            x=event.get('x')
            y=event.get('y')
            focused=self.widget_at_coordinate(x,y)
            if focused:
                self.log(str(focused))
                focused.set_focus()

    def checkWidgetEvents(self, event):
        if event!='':
            for  e, m in self.eventList.items():
                func=m.get('func')
                persist=m.get('persist')
                if self.focus or persist:
                    if e==event or e=='' or (type(event)==dict and e==event['action']):
                        if f'{type(func)}' in [ "function", "<class 'method'>" ,"<class 'function'>"]:
                            self.action=func
                            if 'method' in f'{type(func)}':
                                self.action(event=event)
                            elif 'function' in f'{type(func)}':
                                self.action(self, event=event)
                        else:
                            self.log(f'invalid action for "{e}" type: {type(func)}')
        for cw in self.widgetList:
            cw.checkWidgetEvents(cw.rel_event(event))

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
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGQUIT, self.stop)
        signal.signal(signal.SIGTSTP, self.suspend)
        signal.signal(signal.SIGCONT, self.resume)
        with open("output.log", "w") as self.log_file:
            while self.go:
                #resize to full screen
                sz=self.t.get_terminal_size()
                if sz['columns']!=self.w or sz['rows']!=self.h:
                    self.setSize(0,0,0,0)
                    self.resize()
                if self.screen:
                    sbuffer=self.screen.copy()
                buffer=self.draw()
                if self.force_refresh:
                    self.force_refresh=False
                    output(home+buffer.emit(raw=True))
                else:
                    output(home+buffer.emit_diff(self.screen, raw=True))
                self.screen=buffer.copy()
                for inp in self.input.read_input():
                    if inp != '':
                        self.check_mouse_focus_change(inp)
                        self.checkWidgetEvents(inp)
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

    def addWidget(self, widget):
        widget.parent=self
        widget.fg0=self.fg
        widget.bg0=self.bg
        self.widgetList.append(widget)
        widget.set_focus()
        return self.widgetList[-1]

    def setSize(self, x, y, w, h): #should always be okay
        if x<0:
            x=0
        if y<0:
            y=0
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

    def move(self, x,y):
        pass

    def resize(self, event=None):
        for w in self.widgetList:
            w.resize(event)

    def drawChildren(self, screen=None):
        last=None
        for w in self.widgetList:
            if not w.hidden:
                w.draw()
                if w.focus or w.child_focus:
                    last=w
                else:
                    screen.paste(w.screen, box=(w.x,w.y,w.w,w.h))
        if last:
            screen.paste (last.screen, box=(last.x,last.y,last.w,last.h))
        return

    def draw(self):
        return self.drawChildren(screen=self.screen)

    def on_focus(self):
        pass

    def on_defocus(self):
        pass

