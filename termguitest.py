#!/usr/bin/python3
from gm_termcontrol.widget import widget
from gm_termcontrol.widget_libansiscreen import widgetScreen
#from gm_termcontrol.widget_ansi import widgetScreen
import signal
import sys

def handle_sigtstp(signum, frame):
    pass

#signal.signal(signal.SIGINT, handle_sigint)
signal.signal(signal.SIGTSTP, handle_sigtstp)
#signal.signal(signal.SIGQUIT, handle_sigquit)

def clear(self, event=None):
    self.feed(self.t.clear())

def get_dims(self, event=None):
    self.feed(f"S: ({self.screen.width}, {self.screen.height}) ")
    self.feed(f"C: ({self.content.width}, {self.content.height}) ")
    #self.feed(f"_: ({self.content.cursor.x}, {self.content.cursor.y}) ")
    #x,y=self.scroll(self.scroll_x, self.scroll_y)
    #self.feed(f"{x}, {y}")
    self.feed("\n")

def draw_ruler(self, event=None):
    self.feed(self.t.drawRuler(self.content.width, self.content.height))

def eventout(self, event=None):
    self.feed(repr(str(self.rel_event(event)))+"\n")

style=None
style='2line'
#style='curve'
#style='inside'
#style='outside'
#style='gdw4thjj'
s=widgetScreen(0,0,0,0, style=style, bg=233)
#s.stream.feed(s.t.drawRuler(s.w-4, s.h-2))
s.scroll(0,0)
draw_ruler(s)
box=s.addWidget(widgetScreen(10, 5, 40, 10, style='2line', bg=65,fg=16))
box2=s.addWidget(widgetScreen(15, 7, 60, 10, style='line', bg=75,fg=0))
box.feed("Line1\nLine2\nLine3\nLine4\n")
box2.feed("Line1\nLine2\nLine3\nLine4\n")
box2.feed("Inputs here\n")
s.addEvent('Ctrl Q', s.quit)
s.addEvent('r', s.refresh)
box2.addEvent('', eventout)
s.addEvent('Ctrl D', get_dims)
box.addEvent('Ctrl D', get_dims)
box2.addEvent('Ctrl D', get_dims)
s.addEvent('Ctrl R', draw_ruler)
s.addEvent('Ctrl L', clear)
box.addEvent('Ctrl L', clear)
box2.addEvent('Ctrl L', clear)
s.guiLoop()
