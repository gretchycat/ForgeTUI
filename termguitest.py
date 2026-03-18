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

style=None
style='plot'
#style='curve'
#style='inside'
#style='outside'
#style='gdw4thjj'
s=widgetScreen(0,0,0,0, style=style, bg=233)
#s.stream.feed(s.t.drawRuler(s.w-4, s.h-2))
s.scroll(0,0)
s.feed(s.t.drawRuler(s.content.width, s.content.height))
box=s.addWidget(widgetScreen(10, 5, 40, 10, style='plot', bg=65,fg=16))
box2=s.addWidget(widgetScreen(15, 7, 60, 10, style=None, bg=75,fg=0))
box.feed("Line1\nLine2\nLine3\nLine4\n")
box2.feed("Line1\nLine2\nLine3\nLine4\n")
box2.feed("Inputs here\n")
s.addEvent('Ctrl Q', s.quit)
s.addEvent('r', s.refresh)

def clear(self, event=None):
    self.feed(self.t.clear())
    self.feed(self.t.gotoxy(1,1))

def get_dims(self, event=None):
    self.feed(f"S: ({self.screen.width}, {self.screen.height}) ")
    self.feed(f"C: ({self.content.width}, {self.content.height}) ")
    x,y=self.scroll(self.scroll_x, self.scroll_y)
    self.feed(f"{x}, {y}\n")

def eventout(self, event=None):
    self.feed(repr(str(event))+"\n")

box2.addEvent('', eventout)
s.addEvent('Ctrl D', get_dims)
box.addEvent('Ctrl D', get_dims)
box2.addEvent('Ctrl D', get_dims)
s.addEvent('Ctrl L', clear)
box.addEvent('Ctrl L', clear)
box2.addEvent('Ctrl L', clear)
s.guiLoop()
