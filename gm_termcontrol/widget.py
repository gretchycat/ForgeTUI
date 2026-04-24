#!/usr/bin/python3
from __future__ import annotations
import sys, os, select, re
from libansiscreen.screen import Screen
from libansiscreen.color.palette import Palette, create_ansi_256_palette
from .termcontrol import termcontrol
from .terminput import termInput
from .box_glyphs import grchr, theme, make_theme
import signal
import copy

class boxDraw:
    def __init__(self, bgColor=0, fgColor=7,
                bg0=0, fg0=7,
                frameColors=[],
                chars='',
                mode='auto',
                charset='utf8',
                style='plot',
                ):
        self.screen=None
        self.style=style
        self.term=termcontrol()
        self.fg0, self.bg0=fg0, bg0
        self.bgColor=bgColor
        self.frame={'w':2, 'h':1}
        self.tinted=None
        self.theme=make_theme(style, bg=bgColor, fg=fgColor)

    def make_inverted(self, theme):
        inv=copy.deepcopy(theme)
        swaps=[
               ("box.top_left", 'box.bottom_right'),
               ("box.top_right", 'box.bottom_left'),
               ("box.top_center", 'box.bottom_center'),
               ("box.middle_left", 'box.middle_right'),
              ]
        for sw in swaps:
            s1,s2=sw
            inv[s2].fg=theme[s1].fg
            inv[s1].fg=theme[s2].fg
        return inv

    def draw(self, x=0, y=0, w=0, h=0, fill=True, invert=False, screen=None, box_type=''):
        if screen is None:
            return
        t=self.theme.get(box_type)
        if not t:
            t=self.theme.get('focus')
        if self.style in ['plot']:
            if fill:
                for y in range(1, screen.height-2):
                    for x in range(1, screen.width-1):
                        screen.set_cell(x,y,t['box.middle_center'])
            screen.plot(0,0,t['box.top_left'].fg)
            screen.plot(screen.width-1,0,t['box.top_right'].fg)
            for x in range(1,screen.width-1):
                screen.plot(x,0,t['box.top_center'].fg)
                screen.plot(x,1,t['box.middle_center'].bg)
                screen.plot(x,screen.height*2-4,t['box.middle_center'].bg)
                screen.plot(x,screen.height*2-3,t['box.bottom_center'].fg)
            for y in range(1, screen.height*2-3):
                screen.plot(0,y,t['box.middle_left'].fg)
                screen.plot(1,y,t['box.middle_center'].bg)
                screen.plot(screen.width-2,y,t['box.middle_center'].bg)
                screen.plot(screen.width-1,y,t['box.middle_right'].fg)
            screen.plot(0,screen.height*2-3,t['box.bottom_left'].fg)
            screen.plot(screen.width-1,screen.height*2-3,t['box.bottom_right'].fg)
        else:
            screen.set_cell(0,0,t['box.top_left'])
            screen.set_cell(screen.width-1,0,t['box.top_right'])
            for x in range(1, screen.width-1):
                screen.set_cell(x,0,t['box.top_center'])
                screen.set_cell(x,screen.height-2,t['box.bottom_center'])
            for y in range(1, screen.height-2):
                screen.set_cell(0,y,t['box.middle_left'])
                screen.set_cell(screen.width-1,y,t['box.middle_right'])
                if fill:
                    for x in range(1, screen.width-1):
                        screen.set_cell(x,y,t['box.middle_center'])
            screen.set_cell(0,screen.height-2,t['box.bottom_left'])
            screen.set_cell(screen.width-1,screen.height-2,t['box.bottom_right'])
        return screen

import uuid
class Widget():
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=0, name=uuid.uuid4()):
        self.log_file=None
        self.name=name
        self.force_refresh=True
        self.screen=None
        self.focus=False
        self.reorder=False
        self.hidden=False
        self.fg0=7
        self.bg0=0
        self.invert=False
        self.minW=1
        self.minH=1
        self.t=termcontrol()
        self._x, self._y=None, None
        self._w, self._h=None, None
        self.setSize(x, y, w, h)
        self.screen=Screen(width=self.w, height=self.h)
        self.setColors(fg, bg)
        self.widgetList=[]
        self.eventList={}
        self.parent=None
        self.last_action=None
        self.last_action_count=0
        self.addEvent('', self.set_last_action)

    def suspend(self, signum, frame):
        self.t.output(self.t.disable_mouse())
        self.t.output(self.t.enable_cursor())
        self.t.output(self.t.normal_screen())
        self.t.output("Preparing for suspend\n")
        os.kill(os.getpid(), signal.SIGSTOP)

    def resume(self, signum, frame):
        self.t.output(self.t.enable_mouse())
        self.t.output(self.t.disable_cursor())
        self.t.output(self.t.alt_screen())
        self.t.output("Resuming\n")

    def stop(self, signum, frame):
        self.t.output(self.t.normal_screen())
        self.t.output('Quit requested. Stopping\n')
        self.t.output(self.t.alt_screen())
        self.quit()

    def set_last_action(self, event=None):
        if type(event)==dict:
            if event['action']==self.last_action:
                self.last_action_count=self.last_action_count+1
            else:
                self.last_action_count=0
                self.last_action=event['action']
        else:
            if event==self.last_action:
                self.last_action_count=self.last_action_count+1
            else:
                self.last_action_count=self.last_action_count+1
                self.last_action=event

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
        rx=x-ox
        ry=y-oy
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
            revent['x']=event['x']-ox
            revent['y']=event['y']-oy
            if  0<=revent['x']<self.w and 0<=revent['y']<self.h:
                return revent
            return ''
        return event

    def set_focus(self):
        root=self
        while root.parent:
            root=root.parent
        #deactivate all focus
        defocused=None
        stack=[ root ]
        while stack:
            node=stack.pop()
            if node.focus:
                defocused=node
            node.focus=False
            for n in node.widgetList:
                stack.append(n)
        #activate self and set parent focus on all parents
        node=self
        self.focus=True
        self.hidden=False
        while node.parent:
            node=node.parent
            node.focus='parent'
        if self.reorder:
            stack=[ root ]
            while stack:
                node=stack.pop()
                move=None
                for n in node.widgetList:
                    stack.append(n)
                    if n.focus:
                        move=n
                if move:
                    node.widgetList.remove(move)
                    node.widgetList.append(move)
        if self!=defocused:
            if defocused:
                defocused.on_defocus()
            self.on_focus()

    def next_focus(self):
        next=False
        if self.parent:
            for w in self.parent.widgetList:
                if w==self:
                    next=True
                if next:
                    w.set_focus()
                    return w
        return None

    def prev_focus(self):
        prev=None
        if self.parent:
            for w in self.parent.widgetList:
                if w==self:
                    if prev:
                        prev.set_focus()
                    return prev
                else:
                    prev=w
        return None

    def hide(self, next='parent'):
        if next=='parent':
            if self.parent:
                self.parent.set_focus()
                self.hidden=True
                return True
        if next=='next':
            if self.next_focus():
                return True
        if next=='prev':
            if self.prev_focus():
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
                focused.set_focus()

    def checkWidgetEvents(self, event):
        if event!='':
            for  e, m in self.eventList.items():
                func=m.get('func')
                persist=m.get('persist')
                if self.focus==True or persist:
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
        self.t.output(self.t.disable_cursor())
        self.t.output(self.t.enable_mouse())
        self.t.output(self.t.alt_screen())
        self.t.output(self.t.clear())
        #home=self.t.gotoxy(self.x, self.y)
        home=self.t.gotoxy(1, 1)
        s_start=self.t.start_sync()
        s_end=self.t.end_sync()
        origin=self.t.gotoxy(1, 1)
        buffercache=""
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGQUIT, self.stop)
        signal.signal(signal.SIGTSTP, self.suspend)
        signal.signal(signal.SIGCONT, self.resume)
        input_cache=[]
        with open("self.t.output.log", "w") as self.log_file:
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
                    self.t.output(s_start+home+buffer.emit(raw=True)+s_end)
                else:
                    self.t.output(s_start+home+buffer.emit_diff(self.screen, raw=True)+s_end)
                self.screen=buffer.copy()
                for inp in self.input.read_input():  #TODO cache input, one per loop
                    if inp != '':
                        input_cache.append(inp)
                #i_go=True
                while len(input_cache):
                    inp=input_cache.pop(0)
                    self.check_mouse_focus_change(inp)
                    self.checkWidgetEvents(inp)
                    #if type(inp)==dict and len(input_cache) and type(input_cache)==dict:
                    #    if input_cache[0]['action']!=inp['action']:i_go=False
        self.t.output(self.t.clear())
        self.t.output(self.t.enable_cursor())
        self.t.output(self.t.disable_mouse())
        self.t.output(self.t.normal_screen())
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
        if type(x)==float or x<0: self._x=x
        if type(y)==float or y<0: self._y=y
        if type(w)==float or w<=0: self._w=w
        if type(h)==float or h<=0: self._h=h
        if self._x is not None: x=self._x
        if self._y is not None: y=self._y
        if self._w is not None: w=self._w
        if self._h is not None: h=self._h
        scr=self.t.get_terminal_size()
        if type(x)==float: x=int(x*scr['columns'])
        if type(y)==float: y=int(y*scr['rows'])
        if type(w)==float: w=int(w*scr['columns'])
        if type(h)==float: h=int(h*scr['rows'])
        if x<0: x=scr['columns']+x
        if y<0: y=scr['rows']+y
        if w<=0: w=scr['columns']+w
        if h<=0: h=scr['rows']+h
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

    def resize(self, event=None):
        self.setSize(self.x,self.y,self.w,self.h)
        for w in self.widgetList:
            w.resize(event)

    def move(self, x,y):
        pass

    def drawChildren(self, screen=None): 
        last=None
        for w in self.widgetList:
            if not w.hidden:
                w.draw()
                if w.focus:
                    last=w
                else:
                    screen.paste(w.screen, box=(w.x,w.y,w.w,w.h))
        if last:
            screen.paste (last.screen, box=(last.x,last.y,last.w,last.h))
        return

    def draw(self):
        #TODO colorize on focus
        colored=self.screen
        if self.focus==False:
            pass
        if self.focus=='parent':
            pass
        return self.drawChildren(screen=colored)

    def on_focus(self):
        pass

    def on_defocus(self):
        pass

