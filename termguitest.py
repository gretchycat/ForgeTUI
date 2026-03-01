#!/usr/bin/python3
from gm_termcontrol import widget, widgetScreen
import signal
import sys

def handle_sigint(signum, frame):
    #print("Caught Ctrl-C (SIGINT)")
    # Clean up here if needed
    #sys.exit(0)
    pass

#signal.signal(signal.SIGINT, handle_sigint)
signal.signal(signal.SIGTSTP, handle_sigint)
#signal.signal(signal.SIGQUIT, handle_sigint)

s=widgetScreen(1, 1, 80, 25, style='curve', bg=233)
s.stream.feed(s.t.drawRuler(s.w, s.h))
box=s.addWidget(widgetScreen(23, 5, 20, 10, style='outside', bg=65,fg=1))
box2=s.addWidget(widgetScreen(53, 10, 20, 10, style='inside', bg=75,fg=16))
box.stream.feed(box.t.gotoxy(1,1)+box2.t.ansicolor(fg='black')+"Testing 123")
box2.stream.feed(box2.t.gotoxy(3,3)+box2.t.ansicolor(fg=16)+"hello\n")
s.addEvent('Ctrl Q', s.quit)
s.addEvent('r', s.refresh)

def eventout(self, event=None):
    self.stream.feed(repr(str(event))+"\n")

box2.addEvent('', eventout)
s.guiLoop()
