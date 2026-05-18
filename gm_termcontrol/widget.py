#!/usr/bin/python3
from __future__ import annotations
import sys, os, select, re
from libansiscreen.screen import Screen
from libansiscreen.color.palette import Palette, create_ansi_256_palette
from .termcontrol import termcontrol
from .terminput import termInput
from .theme import grchr, theme, make_theme
import signal
import copy

import uuid
class Widget():
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=0, name=uuid.uuid4()):
        self.log_file=None
        self.name=name
        self.force_refresh=True
        self.screen=None
        self.focus=False
        self.hidden=False
        self.reorder=False
        self.fg0=7
        self.bg0=0
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
        #self.last_action=None
        #self.last_action_count=0
        self.captured_widget=None
        self.drag_start=None
        self.drag_previous=None
        self.drag_handle=None

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
        #for w in widgets:
        #    if w != root:
        #        if w.focus:
        #            return w
        if widgets:
            return widgets[-1]
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
        root=self
        while root.parent:
            root=root.parent
        stack=[ root ]
        while stack:
            node=stack.pop()
            if node.focus==True:
                return node
            for n in node.widgetList:
                stack.append(n)

    def set_focus(self):
        self.captured_widget=None
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
                    focused=self.widget_at_coordinate(x,y)
                    if focused:
                        focused.set_focus()

    def checkWidgetEvents(self, event):
        if event!='':
            if type(event)==dict:
                if event['action']=='drag':
                    if self.drag_start:
                        event['drag start']=self.drag_start
                    if self.drag_handle is not None:
                        event['drag handle']=self.drag_handle
                    if self.drag_previous:
                        event['drag previous']=self.drag_previous
                        event['drag move']={
                            'x': event['x']-self.drag_previous['x'],
                            'y': event['y']-self.drag_previous['y'],
                            'button': event['button'],
                            'action': event['action']
                            }
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
        if self.drag_start:
            event.pop('drag previous',None)
            event.pop('drag start',None)
            event.pop('drag handle',None)
            self.drag_previous=event.copy()
        else:
            self.drag_previous=None

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
        return(w,h)

    def resize(self, w=None, h=None):
        self._w, self._h=w,h
        self.setSize(self.x,self.y,self.w,self.h)
        for wd in self.widgetList:
            wd.resize(w,h)

    def move(self, x,y):
        if self.parent:
            self.x=max(0, min(self.parent.w-1-self.w,x))
            self.y=max(0, min(self.parent.h-1-self.h,y))
            self._x, self._y=None, None
        pass

    def draw(self):
        pass

    def on_focus(self):
        pass

    def on_defocus(self):
        pass

class WidgetContainer(Widget):
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=0, name=uuid.uuid4()):
        super().__init__(x,y,w,y,fg,bg,name)
        self.t=termcontrol()
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

    #def set_last_action(self, event=None):
    #    if type(event)==dict:
    #        if event['action']==self.last_action:
    #            self.last_action_count=self.last_action_count+1
    #        else:
    #            self.last_action_count=0
    #            self.last_action=event['action']
    #    else:
    #        if event==self.last_action:
    #            self.last_action_count=self.last_action_count+1
    #        else:
    #            self.last_action_count=self.last_action_count+1
    #            self.last_action=event

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
        #for w in widgets:
        #    if w != root:
        #        if w.focus:
        #            return w
        if widgets:
            return widgets[-1]
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
        root=self
        while root.parent:
            root=root.parent
        stack=[ root ]
        while stack:
            node=stack.pop()
            if node.focus==True:
                return node
            for n in node.widgetList:
                stack.append(n)

    def set_focus(self):
        self.captured_widget=None
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
                    focused=self.widget_at_coordinate(x,y)
                    if focused:
                        focused.set_focus()

    def checkWidgetEvents(self, event):
        if event!='':
            if type(event)==dict:
                if event['action']=='drag':
                    if self.drag_start:
                        event['drag start']=self.drag_start
                    if self.drag_handle is not None:
                        event['drag handle']=self.drag_handle
                    if self.drag_previous:
                        event['drag previous']=self.drag_previous
                        event['drag move']={
                            'x': event['x']-self.drag_previous['x'],
                            'y': event['y']-self.drag_previous['y'],
                            'button': event['button'],
                            'action': event['action']
                            }
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
        if self.drag_start:
            event.pop('drag previous',None)
            event.pop('drag start',None)
            event.pop('drag handle',None)
            self.drag_previous=event.copy()
        else:
            self.drag_previous=None

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
        return(w,h)

    def resize(self, w=None, h=None):
        self._w, self._h=w,h
        self.setSize(self.x,self.y,self.w,self.h)
        for wd in self.widgetList:
            wd.resize(w,h)

    def move(self, x,y):
        if self.parent:
            self.x=max(0, min(self.parent.w-1-self.w,x))
            self.y=max(0, min(self.parent.h-1-self.h,y))
            self._x, self._y=None, None
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
        super().draw()
        #if self.focus==False: #too slow
        #    self.screen.shift_hsv(0.0,-1.0,-1.0/4)
        #if self.focus=='parent':
        #    self.screen.shift_hsv(0.0,-1.0,0.0)
        return self.drawChildren(screen=self.screen)

    def on_focus(self):
        pass

    def on_defocus(self):
        pass

class WidgetBox(Widget):
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=0, style='plot', title='', box_name='box'):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg)
        self.title=title
        self.style=style
        self.box_name=box_name
        self.fg0, self.bg0=fg, bg
        self.style=style
        self.box_type='focus'
        self.frame={'w':0, 'h':0}
        if style is not None:
            self.frame={'w':2, 'h':1}
        self.theme=make_theme(style, bg=bg, fg=fg)

    def draw(self):
        super().draw()
        screen=self.screen
        x=self.x
        y=self.y
        fill=True
        box_name=self.box_name
        w=self.w
        h=self.h
        bn=self.box_name
        if screen is None:
            return
        t=self.theme.get(self.box_type)
        if not t:
            t=self.theme.get('focus')
        if self.style in ['plot']:
            if fill:
                for y in range(1, screen.height-2):
                    for x in range(1, screen.width-1):
                        screen.set_cell(x,y,t[f'{bn}.middle_center'])
            screen.plot(0,0,t[f'{bn}.top_left'].fg)
            screen.plot(screen.width-1,0,t[f'{bn}.top_right'].fg)
            for x in range(1,screen.width-1):
                screen.plot(x,0,t[f'{bn}.top_center'].fg)
                screen.plot(x,1,t[f'{bn}.middle_center'].bg)
                screen.plot(x,screen.height*2-4,t[f'{bn}.middle_center'].bg)
                screen.plot(x,screen.height*2-3,t[f'{bn}.bottom_center'].fg)
            for y in range(1, screen.height*2-3):
                screen.plot(0,y,t[f'{bn}.middle_left'].fg)
                screen.plot(1,y,t[f'{bn}.middle_center'].bg)
                screen.plot(screen.width-2,y,t[f'{bn}.middle_center'].bg)
                screen.plot(screen.width-1,y,t[f'{bn}.middle_right'].fg)
            screen.plot(0,screen.height*2-3,t[f'{bn}.bottom_left'].fg)
            screen.plot(screen.width-1,screen.height*2-3,t[f'{bn}.bottom_right'].fg)
        else:
            screen.set_cell(0,0,t[f'{bn}.top_left'])
            screen.set_cell(screen.width-1,0,t[f'{bn}.top_right'])
            for x in range(1, screen.width-1):
                screen.set_cell(x,0,t[f'{bn}.top_center'])
                screen.set_cell(x,screen.height-2,t[f'{bn}.bottom_center'])
            for y in range(1, screen.height-2):
                screen.set_cell(0,y,t[f'{bn}.middle_left'])
                screen.set_cell(screen.width-1,y,t[f'{bn}.middle_right'])
                if fill:
                    for x in range(1, screen.width-1):
                        screen.set_cell(x,y,t[f'{bn}.middle_center'])
            screen.set_cell(0,screen.height-2,t[f'{bn}.bottom_left'])
            screen.set_cell(screen.width-1,screen.height-2,t[f'{bn}.bottom_right'])
        return screen

class WidgetVBox(WidgetContainer):
    pass

class WidgetHBox(WidgetContainer):
    pass

class WidgetWindow(WidgetContainer, WidgetBox):
    pass

class WidgetTabController(WidgetContainer):
    pass

class WidgetScrollArea(WidgetContainer):
    pass

class WidgetScreen(WidgetContainer): #deprecated
    def __init__(self, x, y, w, h, fg=7, bg=None, style=None, title=''):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg)
        self.show_x_scrollbar=True
        self.show_y_scrollbar=True
        self.title=title
        self.style=style
        self.reorder=True
        self.frame=None
        self.frame=frameDraw(style=style, bgColor=self.bg,
                                 bg0=self.bg0, widget=self, title=title)
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
        self.addEvent('button down', self.scrollbar_mouse)
        self.addEvent('scroll down', self.scroll_down)
        self.addEvent('scroll up', self.scroll_up)
        self.addEvent('scroll right', self.scroll_right)
        self.addEvent('scroll left', self.scroll_left)
        self.addEvent('drag', self.drag_handler)

    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.title})"

    def resize(self, w=None, h=None):
        super().resize(w,h)
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
        if(self.frame and self.style is not None):
            fw=self.frame.frame['w']*2
            fh=self.frame.frame['h']*2
            self.frame.draw(0, 0, self.w, self.h, screen=self.screen,
                            sx_lock=self.scroll_x!=-1,
                            sy_lock=self.scroll_y!=-1,
                            show_vsb=self.show_y_scrollbar,
                            show_hsb=self.show_x_scrollbar,
                            focus=self.focus)
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
        super().draw()
        return self.screen

    def scroll(self, x=0, y=-1):
        fw,fh=0,0
        if self.frame:
            fw=self.frame.frame['w']*2
            fh=self.frame.frame['h']*2
        self.scroll_x=int(x)
        self.scroll_y=int(y)
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

    def scroll_down(self, event=None):
        if self.scroll_y==-1:
            return
        #ac=min(max(1,self.last_action_count),5)
        ac=1
        self.scroll(self.scroll_x, self.scroll_y+ac)

    def scroll_up(self, event=None):
        if self.scroll_y==-1:
            self.scroll(self.scroll_x, self.y_max)
            return
        #ac=min(max(1,self.last_action_count),5)
        ac=1
        if self.scroll_y-ac<0:
            ac=1
        if self.scroll_y>0:
            self.scroll(self.scroll_x, self.scroll_y-ac)

    def scroll_right(self, event=None):
        if self.scroll_x==-1:
            return
        #ac=min(max(1,self.last_action_count),5)
        ac=1
        self.scroll(self.scroll_x+1, self.scroll_y)

    def scroll_left(self, event=None):
        if self.scroll_x==-1:
            self.scroll(self.x_max, self.scroll_y)
            return
        #ac=min(max(1,self.last_action_count),5)
        ac=1
        if self.scroll_x-ac<0:
            ac=1
        if self.scroll_x>0:
            self.scroll(self.scroll_x-ac, self.scroll_y)

    def scroll_x_bar(self, event=None):
        if type(event)==dict:
            pos=(event['x']-1)/(self.w-3) #always be between 0.0 and 1.0
            s=int(pos*self.x_max)
            self.scroll(s, self.scroll_y)

    def scroll_y_bar(self, event=None):
        if type(event)==dict:
            pos=(event['y']-1)/(self.h-3) #always be between 0.0 and 1.0
            s=int(pos*self.y_max)
            self.scroll(self.scroll_x, s)

    def scrollbar_mouse(self, event=None):
        #self.log(f"Mouse: {event}")
        if type(event)==dict:
            if event['x']==self.w-1:
                if self.show_y_scrollbar:
                    if event['y']==1:
                        self.scroll_up(event=event)
                    if 1 < event['y'] < self.h-2:
                        self.scroll_y_bar(event=event)
                    if event['y']==self.h-2:
                        self.scroll_down(event=event)
            elif event['y']==self.h-1:
                if self.show_x_scrollbar:
                    if event['x']==1:
                        self.scroll_left(event=event)
                    if 1 < event['y'] < self.w-2:
                        self.scroll_x_bar(event=event)
                    if event['x']==self.w-2:
                        self.scroll_right(event=event)

    def drag_handler(self, event=None):
        self.drag_move(event)
        self.drag_resize(event)

    def drag_move(self, event=None):
        if type(event)==dict and \
                event['action']=='drag' and \
                event.get('drag start') and \
                event.get('drag move'):
            pos=event['drag start']['y']==0
            if event['button']==0 and \
                    ( pos or \
                    event.get('drag handle')=='move'):
                if pos:
                    self.drag_handle='move'
                self.log('move 3')
                m= event['drag move']
                self.move(self.x+m['x'], self.y+m['y'])

    def drag_resize(self, event=None):
        if type(event)==dict and \
                event['action']=='drag' and \
                event.get('drag start') and \
                event.get('drag move'):
            self.log(f"{event['button']}")
            self.log(f"({event['drag start']['x']},{self.w-1})")
            self.log(f"({event['drag start']['y']},{self.h-1})")
            pos=event['drag start']['y']==self.h-1 and \
                    event['drag start']['x']==self.w-1
            if event['button']==0 and \
                    (pos or event.get('drag handle')=='resize' ):
                if pos:
                    self.drag_handle='resize'
                self.log('resize 3')
                m= event['drag move']
                self.resize(self.w+m['x'], self.h+m['y'])

class boxDraw(Widget): #deprecated
    def __init__(self, bgColor=0, fgColor=7,
                bg0=0, fg0=7,
                charset='utf8',
                style='plot',
                box_name='box',
                ):
        self.box_name=box_name
        self.screen=None
        self.style=style
        self.term=termcontrol()
        self.fg0, self.bg0=fg0, bg0
        self.bgColor=bgColor
        self.frame={'w':0, 'h':0}
        if style is not None:
            self.frame={'w':2, 'h':1}
        self.theme=make_theme(style, bg=bgColor, fg=fgColor)

    def draw(self, x=0, y=0, w=0, h=0, fill=True, screen=None, box_type=''):
        bn=self.box_name
        if screen is None:
            return
        t=self.theme.get(box_type)
        if not t:
            t=self.theme.get('focus')
        if self.style in ['plot']:
            if fill:
                for y in range(1, screen.height-2):
                    for x in range(1, screen.width-1):
                        screen.set_cell(x,y,t[f'{bn}.middle_center'])
            screen.plot(0,0,t[f'{bn}.top_left'].fg)
            screen.plot(screen.width-1,0,t[f'{bn}.top_right'].fg)
            for x in range(1,screen.width-1):
                screen.plot(x,0,t[f'{bn}.top_center'].fg)
                screen.plot(x,1,t[f'{bn}.middle_center'].bg)
                screen.plot(x,screen.height*2-4,t[f'{bn}.middle_center'].bg)
                screen.plot(x,screen.height*2-3,t[f'{bn}.bottom_center'].fg)
            for y in range(1, screen.height*2-3):
                screen.plot(0,y,t[f'{bn}.middle_left'].fg)
                screen.plot(1,y,t[f'{bn}.middle_center'].bg)
                screen.plot(screen.width-2,y,t[f'{bn}.middle_center'].bg)
                screen.plot(screen.width-1,y,t[f'{bn}.middle_right'].fg)
            screen.plot(0,screen.height*2-3,t[f'{bn}.bottom_left'].fg)
            screen.plot(screen.width-1,screen.height*2-3,t[f'{bn}.bottom_right'].fg)
        else:
            screen.set_cell(0,0,t[f'{bn}.top_left'])
            screen.set_cell(screen.width-1,0,t[f'{bn}.top_right'])
            for x in range(1, screen.width-1):
                screen.set_cell(x,0,t[f'{bn}.top_center'])
                screen.set_cell(x,screen.height-2,t[f'{bn}.bottom_center'])
            for y in range(1, screen.height-2):
                screen.set_cell(0,y,t[f'{bn}.middle_left'])
                screen.set_cell(screen.width-1,y,t[f'{bn}.middle_right'])
                if fill:
                    for x in range(1, screen.width-1):
                        screen.set_cell(x,y,t[f'{bn}.middle_center'])
            screen.set_cell(0,screen.height-2,t[f'{bn}.bottom_left'])
            screen.set_cell(screen.width-1,screen.height-2,t[f'{bn}.bottom_right'])
        return screen

class frameDraw(boxDraw): #deprecated
    def __init__(self, bgColor=0,
                bg0=0, fg0=7,
                charset='utf8',
                style='',
                scrollbar_bg=7,
                scrollbar_fg=0,
                widget=None,
                title='',
                box_name='box'
                ):
        self.title=title
        super().__init__(bgColor=bgColor,bg0=bg0,fg0=fg0,
                         charset=charset,style=style, box_name=box_name)
        self.widget=widget
        self.scrollbar_bg=scrollbar_bg
        self.scrollbar_fg=scrollbar_fg

    def draw(self, x=0, y=0, w=0, h=0,
             fill=True,
             screen=None,
             show_vsb=False,
             show_hsb=False,
             sx=0,sx_max=0,sx_lock=False,
             sy=0,sy_max=0,sy_lock=False,
             focus=True
             ):
        box_type='focus'
        if not focus:
            box_type='off'
        else:
            if type(focus)!=bool:
                box_type=focus
        frame=super().draw(x=x, y=y, w=w, h=h,
                        fill=fill,
                        screen=screen, box_type=box_type)
        t=self.theme.get(box_type)
        if not t:
            t=self.theme.get('focus')
        sh,sv=0,0
        if self.widget.x_max>0:
            sh=int((w-5)*(self.widget.sx/self.widget.x_max))
        if self.widget.y_max>0:
            sv=int((h-5)*(self.widget.sy/self.widget.y_max))
        if show_vsb:
            screen.set_cell(w-1,1,t['scroll.up'])
            for y in range(2,h-2):
                screen.set_cell(w-1,y,t['scroll.v'])
            if sy_lock:
                screen.set_cell(w-1,2+sv,t['scroll.handle_lock'])
            else:
                screen.set_cell(w-1,2+sv,t['scroll.handle'])
            screen.set_cell(w-1,h-2,t['scroll.down'])
        if show_hsb:
            pass
            screen.set_cell(1,h-1,t['scroll.left'])
            for x in range(2,w-2):
                screen.set_cell(x,h-1,t['scroll.h'])
            screen.set_cell(w-2,h-1,t['scroll.right'])
            if sx_lock:
                screen.set_cell(2+sh,h-1,t['scroll.handle_lock'])
            else:
                screen.set_cell(2+sh,h-1,t['scroll.handle'])
        if self.title:
            left_gap=t['title.bar.properties']['left_gap']
            right_gap=t['title.bar.properties']['right_gap']
            text_align=t['title.text.properties']['align']
            title=f" {self.title[0:w-left_gap-right_gap-1]} "
            t_x=left_gap
            if text_align=='left':
                t_x=left_gap
            if text_align=='center':
                t_x=max(int((w-left_gap-right_gap-1)/2-len(title)/2)+left_gap,0)
            if text_align=='right':
                t_x=w-len(title)-right_gap
            for x in range(left_gap, w-right_gap):
                screen.set_cell(x,0,t['title.bar'])
            screen.cursor_goto(t_x, 0)
            if t['title.text']:
                screen.set_foreground(t['title.text'].fg)
                screen.set_background(t['title.text'].bg)
            screen.print(title)
        return frame



