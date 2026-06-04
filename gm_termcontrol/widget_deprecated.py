#!/usr/bin/python3
from __future__ import annotations
import sys, os, select, re
import signal
import copy
import uuid
from libansiscreen.screen import Screen
from libansiscreen.color.palette import Palette, create_ansi_256_palette
from .termcontrol import termcontrol
from .terminput import termInput
from .theme import grchr, theme, make_theme
from .widget import Widget

#to be deprecated
class WidgetScreen(Widget): #will be deprecated
    def __init__(self, x, y, w, h, fg=7, bg=None, style=None, title='', name='Screen'+str(uuid.uuid4())):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, name=name)
        self.show_x_scrollbar=True
        self.show_y_scrollbar=True
        self.title=title
        self.style=style
        self.frame=None
        self.frame=frameDraw(style=style, bgColor=self.bg,
                                 bg0=self.bg0, widget=self, title=title)
        fw=0
        fh=0
        if(self.frame):
            fw=self.frame.frame['w']*2
            fh=self.frame.frame['h']*2
        self.content=Screen(width=max(1,w-fw), height=max(1,h-fh))
        self.style=style
        self.content.print(self.t.ansicolor(fg=fg,bg=bg))
        self.content.print(self.t.clear())
        self.scroll_x=0
        self.scroll_y=-1
        self.resize()
        self.scroll_type='cursor'
        self.addEvent('button down', self.scrollbar_mouse)
        self.addEvent('scroll down', self.scroll_down)
        self.addEvent('scroll up', self.scroll_up)
        self.addEvent('scroll right', self.scroll_right)
        self.addEvent('scroll left', self.scroll_left)
        self.addEvent('drag', self.drag_handler)

    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.title})"

    def resize(self, w=None, h=None):
        super().resize(w,h)
        fw=0
        fh=0
        if(self.frame):
            fw=self.frame.frame['w']*2
            fh=self.frame.frame['h']*2
        self.content.resize(max(self.screen.width-fw, self.content.width),
                        max(self.screen.height-fh, self.content.height))

    def feed(self, s):
        self.content.print(s)

    def draw(self):
        self.fg0=7
        self.bg0=0
        if self.parent:
            self.fg0=self.parent.fg
            self.bg0=self.parent.bg
        x,y=self.scroll(self.scroll_x, self.scroll_y)
        fw=0
        fh=0
        if(self.frame and self.style is not None):
            fw=self.frame.frame['w']*2
            fh=self.frame.frame['h']*2
            self.frame.draw(0, 0, self.w, self.h, screen=self.screen,
                            sx_lock=self.scroll_x!=-1,
                            sy_lock=self.scroll_y!=-1,
                            show_vsb=self.show_y_scrollbar,
                            show_hsb=self.show_x_scrollbar,
                            focus=self.focus)
        scrolled=self.content
        if self.scroll_x==0 and self.scroll_y==0:
            self.screen.paste(self.content,
                box=(fw//2, fh//2, self.screen.width-fw,
                     self.screen.height-fh-1))
        else:
            scrolled=self.content.copy(box=(x,y,
                    self.screen.width-fw,self.screen.height-fh))
            self.screen.paste(scrolled,
                box=(fw//2, fh//2, self.screen.width-fw,
                     self.screen.height-fh-1))
        super().draw()
        return self.screen

    def scroll(self, x=0, y=-1):
        fw,fh=0,0
        if self.frame:
            fw=self.frame.frame['w']*2
            fh=self.frame.frame['h']*2
        self.scroll_x=int(x)
        self.scroll_y=int(y)
        if self.scroll_type=='cursor':
            self.x_max=max(0, self.content.cursor.x-(self.screen.width-1-fw))
            self.y_max=max(0, self.content.cursor.y-(self.screen.height-1-fh))
        if self.scroll_type=='cursor_center':
            self.x_max=max(0, self.content.cursor.x-(self.screen.width-1-fw)//2)
            self.y_max=max(0, self.content.cursor.y-(self.screen.height-1-fh)//2)
        if x<0 or x>self.x_max:
            x=self.x_max
            self.scroll_x=-1
        if y<0 or y>self.y_max:
            y=self.y_max
            self.scroll_y=-1
        self.sx=x
        self.sy=y
        return x, y

    def scroll_down(self, event=None):
        if self.scroll_y==-1:
            return
        #ac=min(max(1,self.last_action_count),5)
        ac=1
        self.scroll(self.scroll_x, self.scroll_y+ac)

    def scroll_up(self, event=None):
        if self.scroll_y==-1:
            self.scroll(self.scroll_x, self.y_max)
            return
        #ac=min(max(1,self.last_action_count),5)
        ac=1
        if self.scroll_y-ac<0:
            ac=1
        if self.scroll_y>0:
            self.scroll(self.scroll_x, self.scroll_y-ac)

    def scroll_right(self, event=None):
        if self.scroll_x==-1:
            return
        #ac=min(max(1,self.last_action_count),5)
        ac=1
        self.scroll(self.scroll_x+1, self.scroll_y)

    def scroll_left(self, event=None):
        if self.scroll_x==-1:
            self.scroll(self.x_max, self.scroll_y)
            return
        #ac=min(max(1,self.last_action_count),5)
        ac=1
        if self.scroll_x-ac<0:
            ac=1
        if self.scroll_x>0:
            self.scroll(self.scroll_x-ac, self.scroll_y)

    def scroll_x_bar(self, event=None):
        if type(event)==dict:
            pos=(event['x']-1)/(self.w-3) #always be between 0.0 and 1.0
            s=int(pos*self.x_max)
            self.scroll(s, self.scroll_y)

    def scroll_y_bar(self, event=None):
        if type(event)==dict:
            pos=(event['y']-1)/(self.h-3) #always be between 0.0 and 1.0
            s=int(pos*self.y_max)
            self.scroll(self.scroll_x, s)

    def scrollbar_mouse(self, event=None):
        #self.log(f"Mouse: {event}")
        if type(event)==dict:
            if event['x']==self.w-1:
                if self.show_y_scrollbar:
                    if event['y']==1:
                        self.scroll_up(event=event)
                    if 1 < event['y'] < self.h-2:
                        self.scroll_y_bar(event=event)
                    if event['y']==self.h-2:
                        self.scroll_down(event=event)
            elif event['y']==self.h-1:
                if self.show_x_scrollbar:
                    if event['x']==1:
                        self.scroll_left(event=event)
                    if 1 < event['y'] < self.w-2:
                        self.scroll_x_bar(event=event)
                    if event['x']==self.w-2:
                        self.scroll_right(event=event)

    def drag_handler(self, event=None):
        self.drag_move(event)
        self.drag_resize(event)

    def drag_move(self, event=None):
        if type(event)==dict and \
                event['action']=='drag' and \
                event.get('drag start') and \
                event.get('drag move'):
            pos=event['drag start']['y']==0
            if event['button']==0 and \
                    ( pos or \
                    event.get('drag handle')=='move'):
                if pos:
                    self.drag_handle='move'
                self.log('move 3')
                m= event['drag move']
                self.move(self.x+m['x'], self.y+m['y'])

    def drag_resize(self, event=None):
        if type(event)==dict and \
                event['action']=='drag' and \
                event.get('drag start') and \
                event.get('drag move'):
            self.log(f"{event['button']}")
            self.log(f"({event['drag start']['x']},{self.w-1})")
            self.log(f"({event['drag start']['y']},{self.h-1})")
            pos=event['drag start']['y']==self.h-1 and \
                    event['drag start']['x']==self.w-1
            if event['button']==0 and \
                    (pos or event.get('drag handle')=='resize' ):
                if pos:
                    self.drag_handle='resize'
                self.log('resize 3')
                m= event['drag move']
                self.resize(self.w+m['x'], self.h+m['y'])

class boxDraw(Widget): #will be deprecated
    def __init__(self, bgColor=0, fgColor=7,
                bg0=0, fg0=7,
                charset='utf8',
                style='plot',
                box_name='box',
                ):
        self.box_name=box_name
        self.screen=None
        self.style=style
        self.term=termcontrol()
        self.fg0, self.bg0=fg0, bg0
        self.bgColor=bgColor
        self.frame={'w':0, 'h':0}
        if style is not None:
            self.frame={'w':2, 'h':1}
        self.theme=make_theme(style, bg=bgColor, fg=fgColor)

    def draw(self, x=0, y=0, w=0, h=0, fill=True, screen=None, box_type=''):
        bn=self.box_name
        if screen is None:
            return
        t=self.theme.get(box_type)
        if not t:
            t=self.theme.get('focus')
        if self.style in ['plot']:
            if fill:
                for y in range(1, screen.height-2):
                    for x in range(1, screen.width-1):
                        screen.set_cell(x,y,t[f'{bn}.middle_center'])
            screen.plot(0,0,t[f'{bn}.top_left'].fg)
            screen.plot(screen.width-1,0,t[f'{bn}.top_right'].fg)
            for x in range(1,screen.width-1):
                screen.plot(x,0,t[f'{bn}.top_center'].fg)
                screen.plot(x,1,t[f'{bn}.middle_center'].bg)
                screen.plot(x,screen.height*2-4,t[f'{bn}.middle_center'].bg)
                screen.plot(x,screen.height*2-3,t[f'{bn}.bottom_center'].fg)
            for y in range(1, screen.height*2-3):
                screen.plot(0,y,t[f'{bn}.middle_left'].fg)
                screen.plot(1,y,t[f'{bn}.middle_center'].bg)
                screen.plot(screen.width-2,y,t[f'{bn}.middle_center'].bg)
                screen.plot(screen.width-1,y,t[f'{bn}.middle_right'].fg)
            screen.plot(0,screen.height*2-3,t[f'{bn}.bottom_left'].fg)
            screen.plot(screen.width-1,screen.height*2-3,t[f'{bn}.bottom_right'].fg)
        else:
            screen.set_cell(0,0,t[f'{bn}.top_left'])
            screen.set_cell(screen.width-1,0,t[f'{bn}.top_right'])
            for x in range(1, screen.width-1):
                screen.set_cell(x,0,t[f'{bn}.top_center'])
                screen.set_cell(x,screen.height-2,t[f'{bn}.bottom_center'])
            for y in range(1, screen.height-2):
                screen.set_cell(0,y,t[f'{bn}.middle_left'])
                screen.set_cell(screen.width-1,y,t[f'{bn}.middle_right'])
                if fill:
                    for x in range(1, screen.width-1):
                        screen.set_cell(x,y,t[f'{bn}.middle_center'])
            screen.set_cell(0,screen.height-2,t[f'{bn}.bottom_left'])
            screen.set_cell(screen.width-1,screen.height-2,t[f'{bn}.bottom_right'])
        return screen

class frameDraw(boxDraw): #will be deprecated
    def __init__(self, bgColor=0,
                bg0=0, fg0=7,
                charset='utf8',
                style='',
                scrollbar_bg=7,
                scrollbar_fg=0,
                widget=None,
                title='',
                box_name='box'
                ):
        self.title=title
        super().__init__(bgColor=bgColor,bg0=bg0,fg0=fg0,
                         charset=charset,style=style, box_name=box_name)
        self.widget=widget
        self.scrollbar_bg=scrollbar_bg
        self.scrollbar_fg=scrollbar_fg

    def draw(self, x=0, y=0, w=0, h=0,
             fill=True,
             screen=None,
             show_vsb=False,
             show_hsb=False,
             sx=0,sx_max=0,sx_lock=False,
             sy=0,sy_max=0,sy_lock=False,
             focus=True
             ):
        box_type='focus'
        if not focus:
            box_type='off'
        else:
            if type(focus)!=bool:
                box_type=focus
        frame=super().draw(x=x, y=y, w=w, h=h,
                        fill=fill,
                        screen=screen, box_type=box_type)
        t=self.theme.get(box_type)
        bar_type="scroll"
        if not t:
            t=self.theme.get('focus')
        sh,sv=0,0
        if self.widget.x_max>0:
            sh=int((w-5)*(self.widget.sx/self.widget.x_max))
        if self.widget.y_max>0:
            sv=int((h-5)*(self.widget.sy/self.widget.y_max))
        if show_vsb:
            screen.set_cell(w-1,1,t[f'{bar_type}.up'])
            for y in range(2,h-2):
                screen.set_cell(w-1,y,t[f'{bar_type}.v'])
            if sy_lock:
                screen.set_cell(w-1,2+sv,t[f'{bar_type}.handle_lock'])
            else:
                screen.set_cell(w-1,2+sv,t[f'{bar_type}.handle'])
            screen.set_cell(w-1,h-2,t[f'{bar_type}.down'])
        if show_hsb:
            pass
            screen.set_cell(1,h-1,t[f'{bar_type}.left'])
            for x in range(2,w-2):
                screen.set_cell(x,h-1,t[f'{bar_type}.h'])
            screen.set_cell(w-2,h-1,t[f'{bar_type}.right'])
            if sx_lock:
                screen.set_cell(2+sh,h-1,t[f'{bar_type}.handle_lock'])
            else:
                screen.set_cell(2+sh,h-1,t[f'{bar_type}.handle'])
        if self.title:
            left_gap=t['title.bar.properties']['left_gap']
            right_gap=t['title.bar.properties']['right_gap']
            text_align=t['title.text.properties']['align']
            title=f" {self.title[0:w-left_gap-right_gap-1]} "
            t_x=left_gap
            if text_align=='left':
                t_x=left_gap
            if text_align=='center':
                t_x=max(int((w-left_gap-right_gap-1)/2-len(title)/2)+left_gap,0)
            if text_align=='right':
                t_x=w-len(title)-right_gap
            for x in range(left_gap, w-right_gap):
                screen.set_cell(x,0,t['title.bar'])
            screen.cursor_goto(t_x, 0)
            if t['title.text']:
                screen.set_foreground(t['title.text'].fg)
                screen.set_background(t['title.text'].bg)
            screen.print(title)
        return frame



