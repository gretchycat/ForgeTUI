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
style='curve'
#style='inside'
#style='outside'
#style='gdw4thjj'
s=widgetScreen(0,0,0,0, style=style, bg=233)
s.feed(s.t.drawRuler(s.content.width, s.content.height))
box=s.addWidget(widgetScreen(23, 5, 20, 10, style='inside', bg=65,fg=1))
box2=s.addWidget(widgetScreen(53, 10, 20, 10, style='outside', bg=75,fg=16))
box.feed(box.t.gotoxy(1,1)+box.t.ansicolor(fg='black')+"Testing 123")
box2.feed(box2.t.gotoxy(3,3)+box2.t.ansicolor(fg=16)+"hello\n")
s.addEvent('Ctrl Q', s.quit)
s.addEvent('r', s.refresh)

def eventout(self, event=None):
    self.feed(repr(str(event))+"\n")

box2.addEvent('', eventout)
s.guiLoop()
