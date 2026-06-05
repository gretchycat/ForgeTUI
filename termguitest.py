#!/usr/bin/python3
from gm_termcontrol.widget import Widget
from gm_termcontrol.widget_input import WidgetButton, WidgetSlider
from gm_termcontrol.widget_output import WidgetBox
from gm_termcontrol.widget_container import WidgetHBox, WidgetVBox,WidgetScrollArea
from gm_termcontrol.widget_deprecated import WidgetScreen
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
    w=self.get_widget_by_name('bluebox')
    if type(event)==str or True:
        w.feed(f'{repr(self)}: {repr(event)}\n')

s=WidgetScreen(0,0,0,0, style=None, bg=8, fg=15, title='root')
s.scroll(0,0)
s.show_x_scrollbar=False
s.show_y_scrollbar=False
draw_ruler(s)
box=s.addWidget(WidgetScrollArea(10, 5, w=0.5, h=0.5, bg=65,fg=16))
box2=s.addWidget(WidgetScreen(-0.95, 0.5, 0.9, 0.5, style='w', bg=75,fg=0,title='blue d d6tgfr4yjnngr4hhrudu38udhdkdikdmek3orlkekeor', name='bluebox'))
w=s.addWidget(WidgetButton(5,3, style='plot',box_name='box',h=3, bg=248,fg=0,caption=f'Button'))
w.addEvent('', eventout)
vbox=s.addWidget(WidgetVBox(-0.3, 0.25, title='red'))
for n in range(4):
    w=vbox.addWidget(WidgetButton(0,0, style='plot',box_name='box',h=3, bg=248+n,fg=0,caption=f'Button {n+7}'))
    w.addEvent('', eventout)
box2.show_x_scrollbar=False
for i in range(100):
    box.feed(f'Line {i}\n')
box2.feed("Line1\nLine2\nLine3\nLine4\n")
box2.feed("Inputs here\n")
s.addEvent('Ctrl Q', s.quit, persist=True)
s.addEvent('r', s.refresh)
box.addEvent('', eventout)
box2.addEvent('', eventout)
#box.v_bar.addEvent('', eventout)
#box.h_bar.addEvent('', eventout)
vbox.addEvent('', eventout)
s.addEvent('Ctrl D', get_dims)
box.addEvent('Ctrl D', get_dims)
box2.addEvent('Ctrl D', get_dims)
s.addEvent('Ctrl R', draw_ruler)
s.addEvent('Ctrl L', clear)
box.addEvent('Ctrl L', clear)
box2.addEvent('Ctrl L', clear)
s.guiLoop()

