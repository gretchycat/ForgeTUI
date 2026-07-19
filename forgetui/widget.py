#!/usr/bin/python3
from __future__ import annotations
import sys, os, signal, uuid, termios, inspect
from libansiscreen.screen import Screen, frameBuffer
from libansiscreen.color.rgb import Color
from .termcontrol import termcontrol
from .terminput import termInput
from dataclasses import dataclass
from enum import Enum, auto

class EventSource(Enum):
    INPUT = auto()
    KEYBOARD = auto()
    MOUSE = auto()
    SYSTEM = auto()   # Timers, window resizes
    PROGRAM = auto()  # Programmatic/functional triggers

@dataclass
class EventTrigger:
    event: any=None
    source: EventSource = EventSource.PROGRAM

class Widget(): #base Widget class.
    def __init__(self, x:int|float=0, y:int|float=0,\
                 w:int|float=1.0, h:int|float=1.0, fg=None, bg=None,\
                 parent=None, name=str(uuid.uuid4())):
        self.log_file=None
        self.name=name
        self.force_refresh=True     #for the emitter
        self.dirty=True             #redraw widget into frameBuffer
        self.can_focus=True
        self.focus=False
        self.hidden=False
        self.reorder=True
        self.parent=parent
        self.background=None
        self.fg0=7
        self.bg0=0
        self.minW=1
        self.minH=1
        self.content=None
        self.t=termcontrol()
        self._x, self._y=None, None
        self._w, self._h=None, None
        self.fb_resize=False
        self.set_geometry(x, y, w, h)
        self.fb_resize=True
        self.fb_x_offset=0
        self.fb_y_offset=0
        self.fb=Screen(width=self.w)
        self.setColors(fg, bg)
        self.fb.cls()
        self.widgetList=[]
        self.eventList={}
        self.parent=None
        self.captured_widget=None
        self.drag_start=None
        self.drag_previous=None
        self.drag_handle=None
        self.event_buffer=[]    #list of Events

    def handle_signal(self, signum, frame):
        match signum:
            case signal.SIGTSTP:  # Suspend (Ctrl+Z)
                self.t.output(self.t.disable_mouse())
                self.t.output(self.t.enable_cursor())
                self.t.output(self.t.normal_screen())
                self.t.output("Preparing for suspend\n")
                sys.stdout.flush()
                # Restore standard terminal settings for the shell
                termios.tcsetattr(
                    sys.stdin.fileno(), termios.TCSADRAIN, self.old_settings)
                # Put process to sleep
                os.kill(os.getpid(), signal.SIGSTOP)

            case signal.SIGCONT:  # Resume
                # Force the terminal back into raw mode immediately
                termios.tcsetattr(
                    sys.stdin.fileno(), termios.TCSADRAIN, self.raw_settings)
                # Redraw ANSI states
                self.t.output("Resuming\n")
                self.t.output(self.t.enable_mouse())
                self.t.output(self.t.disable_cursor())
                self.t.output(self.t.alt_screen())
                self.refresh()
                sys.stdout.flush()

            case signal.SIGINT | signal.SIGTERM:  # Stop
                self.t.output(self.t.normal_screen())
                self.t.output("Quit requested. Stopping\n")
                self.t.output(self.t.alt_screen())
                # Clean up termios back to normal before exiting
                termios.tcsetattr(
                    sys.stdin.fileno(), termios.TCSADRAIN,\
                    self.old_settings)
                self.quit()

    def __del__(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

    def remove_child(self, widget:Widget):
        try:
            self.widgetList.remove(widget)
            return True
        except ValueError:return False

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
        ox, oy=0,0
        w=self
        while w:
            ox+=w.x
            oy+=w.y
            w=w.parent
        return ox,oy

    def coordinate_in_widget(self, x, y):
        if self.hidden:
            return False
        ox,oy=self.offset()
        rx=x-ox
        ry=y-oy
        return 0<=rx<=self.w and 0<=ry<=self.h

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
            return widgets
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
        return None

    def set_focus(self):
        if not self.can_focus:
            return
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
        return None
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
        return None
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
        self.makeDirty()
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
        self.makeDirty()
        self.hidden=False
        if focus:
            self.set_focus()
        return True

    def refresh(self):
        self.root().force_refresh=True

    def addEvent(self, trigger, func, persist=False, target='__focus__', data=None):
        self.eventList[trigger]={ 'func':func, 'persist':persist, 'target':target, 'data':data}
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
                focused=None
                if not self.captured_widget:
                    x=event.get('x')
                    y=event.get('y')
                    ws=self.widgets_at_coordinate(x,y)
                    if ws is not None:
                        #purge parents
                        ws_p=ws.copy()
                        for w in ws:
                            if w.parent in ws:
                                if w.parent in ws_p:
                                    ws_p.remove(w.parent)
                        for w in ws_p: #FIXME:
                            if w.focus==True:
                                focused=w
                        if focused:
                            focused.set_focus()
                        else:
                            ws[-1].set_focus()

    def run_callback(self, func, kwargs):
        self.makeDirty()
        if callable(func):
            try:
                sig = inspect.signature(func)
                # Filter kwargs to only include parameters accepted by the function
                # (Handles positional-or-keyword and keyword-only parameters)
                has_kwargs_param = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
                if not has_kwargs_param:
                    filtered_kwargs = {
                        k: v for k, v in kwargs.items()
                        if k in sig.parameters and sig.parameters[k].kind not in (
                            inspect.Parameter.POSITIONAL_ONLY,
                            inspect.Parameter.VAR_POSITIONAL
                        )
                    }
                else:
                    filtered_kwargs = kwargs
                return func(**filtered_kwargs)
            except (TypeError, ValueError):
                # Fallback if signature inspection fails (e.g., some C extensions)
                return func(**kwargs)
            self.makeDirty()
        else:
            if isinstance(func, (frameBuffer, str)):
                return func
            return None

    def runEvent(self, event):
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
                target=m.get('target')
                data=m.get('data')
                if target=='__focus__':
                    target=self.get_focused()
                if type(target)==str:
                    target=self.get_widget_by_name(target)
                if w.focus==True or persist or w==target:
                    rel_event=w.rel_event(event)
                    if e==rel_event or e=='' or\
                            type(rel_event)==dict and\
                            (e==rel_event['action'] or\
                            e=='click' and rel_event['action']=='button up'):
                        w.run_callback(func, {'self':w,'event': rel_event,'data':data})
        if root.drag_start:
            event.pop('drag previous',None)
            event.pop('drag start',None)
            event.pop('drag handle',None)
            root.drag_previous=event.copy()
        else:
            root.drag_previous=None

    def mainLoop(self, outputmode=[]):
        if self.parent is not None:
            return
        self.old_settings = termios.tcgetattr(sys.stdin.fileno())
        self.go=True
        self.input=termInput()
        self.input.raw=True
        self.t.output(self.t.disable_cursor())
        self.t.output(self.t.enable_mouse())
        self.t.output(self.t.alt_screen())
        self.t.output(self.t.clear())
        home=self.t.gotoxy(1, 1)
        s_start=self.t.start_sync()
        s_end=self.t.end_sync()
        self.raw_settings = termios.tcgetattr(sys.stdin.fileno())
        for sig in [signal.SIGINT,signal.SIGQUIT,signal.SIGTSTP,signal.SIGCONT]:
            signal.signal(sig, self.handle_signal)
        with open("output.log", "w") as self.log_file:
            while self.go:
                #resize to full screen
                sz=self.t.get_terminal_size()
                pbuffer=None
                if sz['columns']!=self.w or sz['rows']!=self.h:
                    self.set_geometry(0,0,0,0)
                    self.resize()
                else:
                    pbuffer=self.fb.copy()
                self.fb=self.draw()
                if self.force_refresh:
                    self.force_refresh=False
                    self.t.output(s_start+home+\
                        self.fb.emit(raw=True)+s_end)
                else:
                    self.t.output(s_start+home+\
                        self.fb.emit_diff(pbuffer, raw=True)+s_end)
                for inp in self.input.read_input():
                    if inp != '':
                        if type(inp)==str:
                            self.event_buffer.append(EventTrigger(inp,EventSource.KEYBOARD))
                        if type(inp)==dict:
                            self.event_buffer.append(EventTrigger(inp,EventSource.MOUSE))
                while len(self.event_buffer):
                    inp=self.event_buffer.pop(0)
                    if inp.source==EventSource.MOUSE:
                        self.check_mouse_focus_change(inp.event)
                        self.check_captured(inp.event)
                    self.runEvent(inp.event)
        self.t.output(self.t.clear())
        self.t.output(self.t.enable_cursor())
        self.t.output(self.t.disable_mouse())
        self.t.output(self.t.normal_screen())
        try: sys.stdout.flush()
        except: pass
        termios.tcsetattr(
            sys.stdin.fileno(), termios.TCSADRAIN,\
            self.old_settings)

    def quit(self):
        self.root().go=False

    def makeDirty(self):
        w=self
        while w:
            w.dirty=True
            w=w.parent

    def setColors(self, fg, bg):
        self.fg, self.bg=fg, bg
        self.fb.set_foreground(Color.set(fg))
        self.fb.set_background(Color.set(bg))

    def feed(self, s):
        self.fb.print(s)
        self.on_update()

    def addWidget(self, widget, focus=True):
        widget.parent=self
        widget.set_geometry(widget._x,widget._y,widget._w,widget._h)
        widget.fg0=self.fg
        widget.bg0=self.bg
        #widget.fb=Screen(width=widget.w)
        #widget.setColors(widget.fg, widget.bg)
        #widget.fb.cls()
        self.widgetList.append(widget)
        if focus: widget.set_focus()
        self.resize()
        return self.widgetList[-1]

    def set_geometry(self, x, y, w, h, force=False):
        scr=self.t.get_terminal_size()
        if self.parent:
            scr['columns']=self.parent.w
            scr['rows']=self.parent.h
        if type(x) in [ float, str ]: self._x=x
        if type(y) in [ float, str ]: self._y=y
        if type(w) in [ float, str ]: self._w=w
        if type(h) in [ float, str ]: self._h=h
        if type(x)==int and x<0: self._x=x
        if type(y)==int and y<0: self._y=y
        if type(w)==int and w<=0: self._w=w
        if type(h)==int and h<=0: self._h=h
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
        if self.fb_resize or force:
            if self.fb_resize=='grow' and not force:
                self.fb.resize(max(self.fb.width, self.w),
                                   max(self.fb.height, self.h))
            else:
                self.fb.resize(self.w, self.h)
            self.fb.cls()
        return(w,h)

    def resize(self, w=None, h=None):
        if w==None: w=self.w
        if h==None: h=self.h
        self.set_geometry(self.x,self.y,w,h)
        if w!=self.w or h!=self.w:
            self.makeDirty()
            for wd in self.widgetList:
                wd.resize(wd.w,wd.h)

    def move(self, x,y):
        if self.parent:
            self.parent.makeDirty()
            self.parent.fb.cls()
            self.root().force_refresh=True
            self.x=max(0, min(self.parent.w-1-self.w,x))
            self.y=max(0, min(self.parent.h-1-self.h,y))
            self._x, self._y=None, None

    def drawChildren(self, screen=None):
        if screen is None: screen=self.fb
        last=None
        lastbox=None
        for w in self.widgetList:
            inbox=None
            if not w.hidden:
                if w.dirty: #FIXME: make sure all widgets are refreshed
                    w.draw()
                if w.fb_x_offset or w.fb_y_offset:
                    inbox=(int(max(0, w.fb_x_offset)),
                           int(max(0, w.fb_y_offset)),
                           max(1, min(w.w,w.fb.width)),
                           max(1, min(w.h,w.fb.height)))
                if w.focus!=False:
                    last=w
                    lastbox=inbox
                else:
                    if inbox:
                        screen.paste(w.fb.copy(inbox), box=(w.x,w.y,w.w,w.h))
                    else:
                        screen.paste(w.fb, box=(w.x,w.y,w.w,w.h))
        if last:
            if lastbox:
                screen.paste (last.fb.copy(lastbox), box=(last.x,last.y,last.w,last.h))
            else:
                screen.paste (last.fb, box=(last.x,last.y,last.w,last.h))
        return screen

    def draw(self):
        if self.dirty and not self.hidden:
            if self.bg==None and not self.parent:
                self.bg=0
            if self.fg==None and self.parent:
                self.fg=self.parent.fg
            if self.background is not None:
                ret=self.run_callback(self.background, {'self':self, 'width':self.w, 'height':self.h})
                if isinstance(ret, str):
                    self.fb.feed(ret)
                if isinstance(ret, frameBuffer):
                    self.fb.tile(ret)
            self.dirty=False
        return self.drawChildren()

    def on_focus(self):
        self.makeDirty()

    def on_defocus(self):
        self.makeDirty()

    def on_update(self):
        self.makeDirty()
