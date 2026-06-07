#!/usr/bin/python3
from __future__ import annotations
import sys, os, select, re
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color
from libansiscreen.color.palette import Palette, create_ansi_256_palette
from .termcontrol import termcontrol
from .terminput import termInput
from .theme import grchr, theme, make_theme
import signal
import copy
import uuid

class Widget():
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=0, parent=None, name=str(uuid.uuid4())):
        self.log_file=None
        self.name=name
        self.force_refresh=True
        self.screen=None
        self.focus=False
        self.hidden=False
        self.reorder=True
        self.parent=parent
        self.fg0=7
        self.bg0=0
        self.minW=1
        self.minH=1
        self.t=termcontrol()
        self._x, self._y=None, None
        self._w, self._h=None, None
        self.set_geometry(x, y, w, h)
        self.screen=Screen(width=self.w, height=self.h)
        self.screen_resize=True
        self.screen_x_offset=0
        self.screen_y_offset=0
        self.setColors(fg, bg)
        self.screen.cls()
        self.widgetList=[]
        self.eventList={}
        self.parent=None
        #self.last_action=None
        #self.last_action_count=0
        self.captured_widget=None
        self.drag_start=None
        self.drag_previous=None
        self.drag_handle=None

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

    def __del__(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(id={id(self):x})"

    def root(self):
        root = self
        while root.parent:
            root = root.parent
        return root

    def log(self, string):
        winfo = repr(self)
        root = self.root()
        if root.log_file:
            root.log_file.write(f"{winfo}: {string}\n")
            root.log_file.flush()

    def get_widget_by_name(self, name:str):
        stack=[ self.root() ] #traversal/find widgets.
        full_stack=[]  #all widgets/flattened
        while stack:
            node=stack.pop()
            full_stack.append(node)
            for n in reversed(node.widgetList):
                stack.append(n)
        for w in full_stack:
            if w.name==name:
                return w
        return None

    def offset(self):
        pox, poy=0,0
        w=self
        while w.parent:
            pox+=w.parent.x
            poy+=w.parent.y
            w=w.parent
        return pox+self.x, poy+self.y

    def coordinate_in_widget(self, x, y):
        if self.hidden:
            return False
        ox,oy=self.offset()
        rx=x-ox
        ry=y-oy
        return  0<=rx<self.w and 0<=ry<self.h

    def widgets_at_coordinate(self, x, y):
        stack=[ self.root() ] #traversal/find widgets.
        full_stack=[]  #all widgets/flattened
        while stack:
            node=stack.pop()
            full_stack.append(node)
            for n in node.widgetList:
                stack.append(n)
        widgets=[]     #widgets at coord.
        for w in full_stack:
            if w.coordinate_in_widget(x,y):
                widgets.append(w)
        if widgets:
            return widgets  #return on top 
        return None

    def rel_event(self, event=None):
        if type(event)==dict:
            ox,oy=self.offset()
            revent=event.copy()
            revent['abs']={'x':event['x'],'y':event['y']}
            revent['x']=event['x']-ox
            revent['y']=event['y']-oy
            return revent
        return event

    def get_focused(self):
        stack=[ self.root() ]
        while stack:
            node=stack.pop()
            if node.focus==True:
                return node
            for n in node.widgetList:
                stack.append(n)

    def set_focus(self):
        self.captured_widget=None
        root = self.root()
        #deactivate all focus
        defocused=None
        stack=[ root ]
        while stack:
            node=stack.pop()
            if node.focus==True:
                defocused=node
            node.focus=False
            for n in node.widgetList:
                stack.append(n)
        #focus self and set parent focus on all parents
        self.focus=True
        self.hidden=False
        node=self
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
                    if n.focus!=False:
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

    def unhide(self, focus=True):
        self.hidden=False
        if focus:
            self.set_focus()
        return True

    def refresh(self, event=None):
        self.force_refresh=True

    def addEvent(self, trigger, func, persist=False):
        self.eventList[trigger]={ 'func':func, 'persist':persist }

    def check_captured(self, event):
        if event=='':
            return
        if type(event)==dict:
            if event['action'] in [ 'button down', 'drag' ]:
                if self.captured_widget==None:
                    self.captured_widget=self.get_focused()
                    event.pop('drag start',None)
                    self.drag_start=self.captured_widget.rel_event(event)
                return
        self.captured_widget=None
        self.drag_start=None
        self.drag_previous=None
        self.drag_handle=None

    def check_mouse_focus_change(self, event):
        if type(event)==dict:
            if event['action'] not in ['button up']:
                if not self.captured_widget:
                    x=event.get('x')
                    y=event.get('y')
                    focused=self.widgets_at_coordinate(x,y)
                    if focused:
                        focused[-1].set_focus()

    def checkWidgetEvents(self, event):
        if event=='' or not event:
            return
        root = self.root()
        if type(event)==dict:
            if event['action']=='drag':
                if root.drag_start:
                    event['drag start']=root.drag_start
                if root.drag_handle is not None:
                    event['drag handle']=root.drag_handle
                if root.drag_previous:
                    event['drag previous']=root.drag_previous
                    event['drag move']={
                        'x': event['x']-root.drag_previous['x'],
                        'y': event['y']-root.drag_previous['y'],
                        'button': event['button'],
                        'action': event['action']
                        }
        stack=[ root ] #traversal/find widgets.
        full_stack=[]  #all widgets/flattened
        while stack:
            node=stack.pop()
            full_stack.append(node)
            for n in reversed(node.widgetList):
                stack.append(n)
        for w in full_stack:
            for  e, m in w.eventList.items():
                func=m.get('func')
                persist=m.get('persist')
                if w.focus==True or persist:
                    rel_event=w.rel_event(event)
                    if e==rel_event or e=='' or (type(rel_event)==dict and e==rel_event['action']):
                        if f'{type(func)}' in [ "function", "<class 'method'>" ,"<class 'function'>"]:
                            w.action=func
                            if 'method' in f'{type(func)}':
                                w.action(event=rel_event)
                            elif 'function' in f'{type(func)}':
                                w.action(w, event=rel_event)
                        else:
                            w.log(f'invalid action for "{e}" type: {type(func)}')
        if root.drag_start:
            event.pop('drag previous',None)
            event.pop('drag start',None)
            event.pop('drag handle',None)
            root.drag_previous=event.copy()
        else:
            root.drag_previous=None

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
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGQUIT, self.stop)
        signal.signal(signal.SIGTSTP, self.suspend)
        signal.signal(signal.SIGCONT, self.resume)
        input_cache=[]
        with open("output.log", "w") as self.log_file:
            while self.go:
                #resize to full screen
                sz=self.t.get_terminal_size()
                pbuffer=None
                if sz['columns']!=self.w or sz['rows']!=self.h:
                    self.set_geometry(0,0,0,0)
                    self.resize()
                else:
                    pbuffer=self.screen.copy()
                buffer=self.draw()
                if self.force_refresh:
                    self.force_refresh=False
                    self.t.output(s_start+home+buffer.emit(raw=True)+s_end)
                else:
                    self.t.output(s_start+home+buffer.emit_diff(pbuffer, raw=True)+s_end)
                self.screen=buffer.copy()
                for inp in self.input.read_input():
                    if inp != '':
                        input_cache.append(inp)
                while len(input_cache):
                    inp=input_cache.pop(0)
                    self.check_mouse_focus_change(inp)
                    self.check_captured(inp)
                    self.checkWidgetEvents(inp)
        self.t.output(self.t.clear())
        self.t.output(self.t.enable_cursor())
        self.t.output(self.t.disable_mouse())
        self.t.output(self.t.normal_screen())
        try: sys.stdout.flush()
        except: pass

    def quit(self, event=None):
        self.go=False

    def setColors(self, fg, bg):
        self.fg, self.bg=fg, bg
        self.screen.set_foreground(Color.set(fg))
        self.screen.set_background(Color.set(bg))

    def feed(self, s):
        self.screen.print(s)

    def addWidget(self, widget, focus=True):
        widget.parent=self
        widget.set_geometry(widget._x,widget._y,widget._w,widget._h)
        widget.fg0=self.fg
        widget.bg0=self.bg
        self.widgetList.append(widget)
        if focus: widget.set_focus()
        return self.widgetList[-1]

    def set_geometry(self, x, y, w, h): #should always be okay
        if type(x) in [ float, str ]: self._x=x
        if type(y) in [ float, str ]: self._y=y
        if type(w) in [ float, str ]: self._w=w
        if type(h) in [ float, str ]: self._h=h
        if self._x is not None: x=self._x
        if self._y is not None: y=self._y
        if self._w is not None: w=self._w
        if self._h is not None: h=self._h
        if x=='min':
            x=0 
        if y=='min':
            y=0 
        if w=='min':
            w=self.minW
        if h=='min':
            h=self.minH
        scr=self.t.get_terminal_size()
        if self.parent:
            scr['columns']=self.parent.w
            scr['rows']=self.parent.h
        if type(x)==float:
            if abs(x)<=1.0:
                x=int(x*scr['columns'])
        if type(y)==float: 
            if abs(y)<=1.0:
               y=int(y*scr['rows'])
        if type(w)==float: 
            if abs(w)<=1.0:
                w=int(w*scr['columns'])
        if type(h)==float: 
            if abs(h)<=1.0:
                h=int(h*scr['rows'])
        if x is not None:
            self.x=int(x)%scr['columns']
        if y is not None:
            self.y=int(y)%scr['rows']
        if w is not None:
            self.w=int(w)%scr['columns']
        if h is not None:
            self.h=int(h)%scr['rows']
        if self.w==0: self.w=scr['columns']
        if self.h==0: self.h=scr['rows']
        if self.screen and self.screen_resize:
            self.screen.resize(self.w, self.h)
        return(w,h)

    def resize(self, w=None, h=None):
        if w==None: w=self.w
        if h==None: h=self.h
        self.set_geometry(self.x,self.y,w,h)
        for wd in self.widgetList:
            wd.resize(wd.w,wd.h)

    def move(self, x,y):
        if self.parent:
            self.x=max(0, min(self.parent.w-1-self.w,x))
            self.y=max(0, min(self.parent.h-1-self.h,y))
            self._x, self._y=None, None
        pass

    def drawChildren(self, screen=None):
        if screen is None: screen=self.screen
        last=None
        for w in self.widgetList:
            if not w.hidden:
                w.draw()
                if w.focus!=False:
                    last=w
                else:
                    if self.screen_x_offset==0 and self.screen_y_offset==0:
                        screen.paste(w.screen, box=(w.x,w.y,w.w,w.h))
                    else:
                        pass #not quite FIXME
            if last:
                if self.screen_x_offset==0 and self.screen_y_offset==0:
                    screen.paste (last.screen, box=(last.x,last.y,last.w,last.h))
                else:
                    pass #FIXME
        return

    def draw(self):
        return self.drawChildren()

    def on_focus(self):
        pass

    def on_defocus(self):
        pass

    pass
