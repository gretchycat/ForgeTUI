#!/usr/bin/python3
from __future__ import annotations
import sys, os, fcntl, select, asyncio, time, termios, tty, logging, pyte, re, icat
try:
    from libansiscreen.screen import Screen
    from libansiscreen.renderer.ansi_emitter import ANSIEmitter, Box
except:
    Screen=None
from .termcontrol import termcontrol
from .terminput import termInput
from .box_glyphs import grchr, theme

rgb_file_path = '/usr/share/X11/rgb.txt'

import os
import select

CHUNK_SIZE = 4096  # safe per-write chunk

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

class widget():
    def __init__(self, x=1, y=1, w=1, h=1, fg=7, bg=0, key=None, action=None):
        self.screen=None
        self.forceRefresh=False
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
        self.outstream=None #sys.stdout
        self.focus=None
        self.parent=None

    def __del__(self):
        pass

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

    def refresh(self, event=None):
        self.forceRefresh=True

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
        if self.screen:
            emitter = ANSIEmitter(dos_mode=False, ice_mode=False)
        with open("output.log", "w") as log:
            while self.go:
                #resize to full screen
                sz=self.t.get_terminal_size()
                if sz['columns']!=self.w or sz['rows']!=self.h:
                    self.setSize(0,0,0,0)
                if self.screen:
                    sbuffer=self.screen.copy()
                buffer=self.draw()
                if type(buffer)==str:
                    if buffer != buffercache or self.forceRefresh:
                        self.forceRefresh=False
                        buffercache=buffer
                        if(self.screen):
                            sbuffer.print(origin+buffer)
                            out=home+emitter.emit_diff(sbuffer, self.screen,raw=True)
                            output(out)
                            log.write(out)
                            self.screen=sbuffer.copy()
                        else:
                            output(home+buffer)
                else:
                    output(home+emitter.emit_diff(buffer, self.screen))
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


    def resize(self):
        for w in self.widgetList:
            w.resize()

    def drawChildren(self):
        buffer=''
        for w in self.widgetList:
            buffer+=w.draw()
        return buffer

    def draw(self):

        buffer=self.drawChildren()
        if self.outstream:
            self.outstream.write(buffer)
        return buffer

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

