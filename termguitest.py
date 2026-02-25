#!/usr/bin/python3
from gm_termcontrol import widget, widgetScreen

s=widgetScreen(1, 1, 80, 25, style='curve', bg=233)
s.stream.feed(s.t.drawRuler(s.w, s.h))
box=s.addWidget(widgetScreen(23, 5, 20, 10, style='outside', bg=65,fg=0))
box2=s.addWidget(widgetScreen(53, 5, 20, 10, style='inside', bg=75,fg=16))
box.stream.feed(box.t.gotoxy(1,1)+"Testing 123")
box2.stream.feed(box2.t.gotoxy(3,3)+box2.t.ansicolor(fg=16)+"hello\n")
box2.stream.feed(str(s.screen)+"\n")
#s.setSize(0,1,132,50)
box2.stream.feed(str(s.screen))
s.addEvent('q', s.quit)
s.addEvent('r', s.refresh)
def eventout(self, event=None):
    self.stream.feed(repr(str(event))+"    \n")

box2.addEvent('', eventout)
s.guiLoop()
