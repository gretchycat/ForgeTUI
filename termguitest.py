#!/usr/bin/python3
from gm_termcontrol.widget import Widget, WidgetBox, WidgetVBox, WidgetHBox, WidgetScreen 
from gm_termcontrol.widget_libansiscreen import WidgetButton
from gm_termcontrol.termcontrol import termcontrol
from gm_termcontrol.theme import make_theme
import sys

def clear(self, event=None):
    self.feed(self.t.clear())

def get_dims(self, event=None):
    self.feed(f"S: ({self.screen.width}, {self.screen.height}) ")
    self.feed(f"C: ({self.content.width}, {self.content.height}) ")
    self.feed("\n")

def draw_ruler(self, event=None):
    self.feed(self.t.drawRuler(self.content.width, self.content.height))

def eventout(self, event=None):
    if type(event)==str:
        self.feed(repr(str(event))+"\n")

s=WidgetScreen(0,0,0,0, style=None, bg=8, fg=15, title='root')
s.scroll(0,0)
s.show_x_scrollbar=False
s.show_y_scrollbar=False
draw_ruler(s)
box=s.addWidget(WidgetScreen(10, 5, 40, 10, style='c', bg=65,fg=16,title='green'))
box2=s.addWidget(WidgetScreen(-0.75, 0.5, 0.5, 0.5, style='w', bg=75,fg=0,title='blue d d6tgfr4yjnngr4hhrudu38udhdkdikdmek3orlkekeor'))
box3=s.addWidget(WidgetVBox(-0.3, 0.25, 0.25, 0.5, style='plot', bg=196,fg=0,title='red'))
s.addWidget(WidgetButton(5,3, style='plot',box_name='box',h=3, bg=248,fg=0,caption=f'Button'))
for n in range(4):
    box3.addWidget(WidgetButton(0,0, style='plot',box_name='box',h=3, bg=248+n,fg=0,caption=f'Button {n}'))
box2.show_x_scrollbar=False
box.feed("Line1\nLine2\nLine3\nLine4\n")
box2.feed("Line1\nLine2\nLine3\nLine4\n")
box2.feed("Inputs here\n")
s.addEvent('Ctrl Q', s.quit, persist=True)
s.addEvent('r', s.refresh)
box2.addEvent('', eventout)
box.addEvent('', eventout)
s.addEvent('Ctrl D', get_dims)
box.addEvent('Ctrl D', get_dims)
box2.addEvent('Ctrl D', get_dims)
s.addEvent('Ctrl R', draw_ruler)
s.addEvent('Ctrl L', clear)
box.addEvent('Ctrl L', clear)
box2.addEvent('Ctrl L', clear)
s.guiLoop()

