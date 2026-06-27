#!/usr/bin/python3
from forgetui.widget import Widget
from forgetui.widget_input import WidgetButton
from forgetui.widget_container import WidgetWindow, WidgetVBox,WidgetScrollArea
import sys,types

def clear(self, event=None):
    self.feed(self.t.clear())

def get_dims(self, event=None):
    self.feed(f"S: ({self.screen.width}, {self.screen.height}) ")
    self.feed(f"C: ({self.content.width}, {self.content.height}) ")
    self.feed("\n")

def draw_ruler(self, event=None):
    self.feed(self.t.drawRuler(self.w, self.h))

def eventout(self, event=None):
    w=self.get_widget_by_name('bluebox')
    if type(event)==str or True:
        w.feed(f'{repr(self)}: {repr(event)}\n')

def corrupt(self, event=None):
    print('\x1b[2J')

s=Widget(0,0,0,0, bg=8, fg=15)
#s=WidgetWindow(0,0,0,0, bg=8, fg=15)
draw_ruler(s)
box=s.addWidget(WidgetScrollArea(10, 5, w=0.5, h=0.5, bg=65,fg=16))
box2=s.addWidget(WidgetWindow(-0.95, 0.5, 0.9, 0.5, style='w', bg=75,fg=0,title='blue d d6tgfr4yjnngr4hhrudu38udhdkdikdmek3orlkekeor', name='bluebox'))
w=s.addWidget(WidgetButton(5,3, style='plot',box_name='box',h=3, bg=248,fg=0,caption=f'Corrupt'))
w.addEvent('', corrupt)
w.addEvent('Ctrl T', corrupt, persist=True)
vbox=s.addWidget(WidgetVBox(-0.3, 0.25))
for n in range(4):
    w=vbox.addWidget(WidgetButton(0,0, style='plot',box_name='box',h=3, bg=248+n,fg=0,caption=f'Button {n+7}'))
    w.addEvent('', eventout)
box2.show_x_scrollbar=False
for i in range(100):
    box.feed(f'Line {i}\n')
box2.feed("Line1\nLine2\nLine3\nLine4\n")
box2.feed("Inputs here\n")
s.addEvent('Ctrl Q', s.quit, persist=True)
s.addEvent('r', s.refresh, persist=True)
box.addEvent('', types.MethodType(eventout, box))
s.addEvent('', types.MethodType(eventout, box2))
box2.addEvent('', types.MethodType(eventout, box2))
box.v_bar.addEvent('', types.MethodType(eventout,box))
box.h_bar.addEvent('', types.MethodType(eventout,box))
box.addEvent('', types.MethodType(eventout,vbox))
box.content.addEvent('', types.MethodType(eventout,vbox))
box.v_bar.addEvent('', types.MethodType(eventout,vbox))
box.h_bar.addEvent('', types.MethodType(eventout,vbox))
s.addEvent('Ctrl D', types.MethodType(get_dims,s))
box.addEvent('Ctrl D', types.MethodType(get_dims,box))
box2.addEvent('Ctrl D', types.MethodType(get_dims,box2))
s.addEvent('Ctrl R', types.MethodType(draw_ruler,s))
s.addEvent('Ctrl L', types.MethodType(clear, s))
box.addEvent('Ctrl L', types.MethodType(clear, box))
box2.addEvent('Ctrl L', types.MethodType(clear, box2))
s.guiLoop()

