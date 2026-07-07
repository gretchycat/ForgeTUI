#!/usr/bin/python3
from forgetui.widget import Widget
from forgetui.widget_input import WidgetButton
from forgetui.widget_container import WidgetWindow, WidgetVBox,WidgetScrollArea
from forgetui.widget_terminal import WidgetLog
import os,psutil

def get_detailed_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    
    # rss = Resident Set Size (Physical RAM)
    # vms = Virtual Memory Size (Total Virtual Memory allocated)
    return {
        "rss_mb": mem_info.rss / (1024 * 1024),
        "vms_mb": mem_info.vms / (1024 * 1024)
    }

def clear(self):
    self.feed(self.t.clear())

def get_dims(self):
    self.feed(f"S: ({self.fb.width}, {self.fb.height}) ")
    self.feed("\n")

def draw_ruler(self):
    self.feed(self.t.drawRuler(self.w, self.h))

def eventout(self, event=None):
    w=self.get_widget_by_name('bluebox')
    if type(event)==str or True:
        self.log(f'{repr(event)}')
    stats = get_detailed_memory()
    #self.log(f"Physical RAM: {stats['rss_mb']:.2f} MB | Virtual Allocated: {stats['vms_mb']:.2f} MB")

def corrupt(self):
    print('\x1b[2J')

s=Widget(0,0,0,0, bg=8, fg=15, name='root')
box=s.addWidget(WidgetScrollArea(10, 5, w=0.5, h=0.5, bg=65,fg=16, name='green'))
log=s.addWidget(WidgetWindow(-0.95, 0.5, 0.9, 0.5, style='w', bg=75,fg=0,\
        title='blue d d6tgfr4yjnngr4hhrudu38udhdkdikdmek3orlkekeor',\
        name='bluebox', content=WidgetLog(fg=15, bg=None,\
        name='bluescroll', filename='output.log')))
w=s.addWidget(WidgetButton(5,3, style='plot',box_name='box',h=3, bg=248,fg=0,caption=f'Corrupt', name='corrupt'))
w.addEvent('button up', corrupt)
w.addEvent('Ctrl T', corrupt, persist=True)
vbox=s.addWidget(WidgetVBox(-0.3, 0.25, name='buttonbox'))
for n in range(4):
    w=vbox.addWidget(WidgetButton(0,0, style='plot',box_name='box',h=3, bg=248+n,fg=0,caption=f'Button {n+7}', name=f'button {n+7}'))
    w.addEvent('', eventout)

for i in range(100):
    box.feed(f'Line {i}\n')
log.feed("Line1\nLine2\nLine3\nLine4\n")
log.feed("Inputs here\n")

s.addEvent('r', s.refresh, persist=True)
s.addEvent('Ctrl Q', s.quit, persist=True)
s.addEvent('', eventout)
s.addEvent('Ctrl L', clear)
s.addEvent('Ctrl D', get_dims)
s.addEvent('Ctrl R', draw_ruler)
box.content.addEvent('', eventout)
box.content.addEvent('Ctrl L', clear)
box.content.addEvent('Ctrl D', get_dims)
box.content.addEvent('Ctrl R', draw_ruler)
log.content.content.addEvent('', eventout)
s.mainLoop()

