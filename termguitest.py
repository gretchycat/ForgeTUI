#!/usr/bin/python3
from forgetui.widget import Widget
from forgetui.widget_input import WidgetButton, WidgetSlider
from forgetui.widget_output import WidgetMarquee, WidgetProgressBar
from forgetui.widget_container import WidgetTabs, WidgetWindow, WidgetVBox,WidgetScrollArea
from forgetui.widget_terminal import WidgetLog
import os,random

def get_detailed_memory():
    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        # rss = Resident Set Size (Physical RAM)
        # vms = Virtual Memory Size (Total Virtual Memory allocated)
        return {
            "rss_mb": mem_info.rss / (1024 * 1024),
            "vms_mb": mem_info.vms / (1024 * 1024)
        }
    except: return { 'rss_mb':0, 'vms_mb':0}

def clear(self):
    self.feed(self.t.clear())

def get_dims(self):
    self.feed(f"S: ({self.fb.width}, {self.fb.height}) ")
    self.feed("\n")

def draw_ruler(self):
    self.feed(self.t.drawRuler(self.w, self.h))

def ruler(self, width=1, height=1):
    self.feed(self.t.drawRuler(width, height))

def eventout(self, event=None):
    if type(event)==str:
        self.log(f'{repr(event)}')
    #stats = get_detailed_memory()
    #self.log(f"Physical RAM: {stats['rss_mb']:.2f} MB | Virtual Allocated: {stats['vms_mb']:.2f} MB")

def maze(self, width, height):
    random.seed(42)
    for _ in range(height):
        for _ in range(width):
            self.feed(chr(0x2571+random.randint(0,1)))
        self.feed('\n')
def pb_cycle(self):
    p=self.progress+self.total/100
    if p>self.total:
        p=0
    self.set_progress(p)

def corrupt(self):
    print('\x1b[2J')

tabs=WidgetTabs(0,0,0,0,bg=0,fg=7)
s=Widget(0,0,0,0, bg=8, fg=15, name='root')
tabs.add_tab('Main', widget=s , hotkey='Ctrl Home')
e=tabs.add_tab('Next', widget=Widget(fg=9,bg=1) , hotkey='Ctrl End')
e.addWidget(WidgetMarquee(0.1,5,-0.2,1,text='ltr short', direction='ltr', name='ltr short'))
e.addWidget(WidgetMarquee(0.1,7,-0.2,1,text='[[[['+'ltr long '*20+']]]]', direction='ltr'))
e.addWidget(WidgetMarquee(0.1,6,-0.2,1,text='rtl short', direction='rtl'))
e.addWidget(WidgetMarquee(0.1,8,-0.2,1,text='[[[['+'rtl long '*20+']]]]', direction='rtl'))
e.addWidget(WidgetMarquee(0.1,9,-0.2,1,text='pingpong short', direction='pingpong'))
e.addWidget(WidgetMarquee(0.1,10,-0.2,1,text='[[[['+'pingpong long—'*20+']]]]', direction='pingpong'))
pb=e.addWidget(WidgetProgressBar(0.1,15,-0.2,1))
bgsl=e.addWidget(WidgetSlider(0.1,20,-0.2, discreet=[maze, '-|\n_-\n',' #\n# \n']))
pb.addEvent(0.1, pb_cycle, persist=True)
l=tabs.add_tab('Last', widget=Widget(fg=12,bg=4) , hotkey='Ctrl 3')
l.addWidget(WidgetMarquee(0.1,5,-0.2,1,text='This is Blue'))
e.background=maze
l.background='██ \n▄▄°\n▀▀.'
s.background=ruler
box=s.addWidget(WidgetScrollArea(10, 5, w=0.5, h=0.5, bg=65,fg=16, name='green'))
log=s.addWidget(WidgetWindow(-0.95, 0.5, 0.9, 0.5, style='w', bg=75,fg=0,\
        title='blue d d6tgfr4yjnngr4hhrudu38udhdkdikdmek3orlkekeor',\
        name='bluebox', content=WidgetLog(fg=15, bg=None,\
        name='bluescroll', filename='output.log')))
w=s.addWidget(WidgetButton(5,3, style='plot',box_name='box',h=3, bg=248,fg=0,caption=f'Corrupt', name='corrupt'))
w.addEvent('click', corrupt)
w.addEvent('Ctrl R', corrupt, persist=True)
vbox=s.addWidget(WidgetVBox(-20, 0, w=20, h=1.0,name='buttonbox'))
styles=['', 'c', '2', 'w', 'd2', 'd3', 'd4', 'braille', 'octant', 'sextant', 'quadrant', 'plot', ]
for n in range(len(styles)):
    st=styles[n%len(styles)]
    w=vbox.addWidget(WidgetButton(0,0, w=20, h=3, style=st,box_name='box', bg=248,fg=0,caption=f"Style '{st}'", name=f'button {n+1}'))
    w.addEvent('', eventout)

for i in range(100):
    box.feed(f'Line {i}\n')
log.feed("Debug Log\n*********\n")

tabs.addEvent('r', s.refresh, persist=True)
tabs.addEvent('Ctrl Q', s.quit, persist=True)
s.addEvent('', eventout)
s.addEvent('Ctrl D', get_dims)
s.addEvent('Alt R', draw_ruler)
box.content.addEvent('', eventout)
box.content.addEvent('Ctrl L', box.content.fb.cls)
box.content.addEvent('Ctrl D', get_dims)
box.content.addEvent('Alt R', draw_ruler)
log.content.content.addEvent('', eventout)
tabs.mainLoop()

