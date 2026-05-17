#!/usr/bin/python3
from __future__ import annotations
from libansiscreen.screen import Screen
from libansiscreen.color.palette import Palette, create_ansi_256_palette
from .widget import Widget, WidgetBox, boxDraw

class frameDraw(boxDraw):
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
        if not t:
            t=self.theme.get('focus')
        sh,sv=0,0
        if self.widget.x_max>0:
            sh=int((w-5)*(self.widget.sx/self.widget.x_max))
        if self.widget.y_max>0:
            sv=int((h-5)*(self.widget.sy/self.widget.y_max))
        if show_vsb:
            screen.set_cell(w-1,1,t['scroll.up'])
            for y in range(2,h-2):
                screen.set_cell(w-1,y,t['scroll.v'])
            if sy_lock:
                screen.set_cell(w-1,2+sv,t['scroll.handle_lock'])
            else:
                screen.set_cell(w-1,2+sv,t['scroll.handle'])
            screen.set_cell(w-1,h-2,t['scroll.down'])
        if show_hsb:
            pass
            screen.set_cell(1,h-1,t['scroll.left'])
            for x in range(2,w-2):
                screen.set_cell(x,h-1,t['scroll.h'])
            screen.set_cell(w-2,h-1,t['scroll.right'])
            if sx_lock:
                screen.set_cell(2+sh,h-1,t['scroll.handle_lock'])
            else:
                screen.set_cell(2+sh,h-1,t['scroll.handle'])
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

class WidgetScreen(Widget):
    def __init__(self, x, y, w, h, fg=7, bg=None, style=None, title=''):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg)
        self.show_x_scrollbar=True
        self.show_y_scrollbar=True
        self.title=title
        self.style=style
        self.reorder=True
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

class WidgetButton(WidgetBox):
    def __init__(self, x, y, w=0, h=1, fg=7, bg=None, style='curve', box_name='button', caption='Button', toggle=False):
        minw=len(caption)+4
        if w<minw:
            w=minw
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, style=style, box_name=box_name)
        self.active=False
        self.active_disp=False
        self.style=style
        self.caption=caption
        self.title=caption
        self.resize()
        self.addEvent('button down', self.b_down)
        self.addEvent('button up', self.b_up)

    def b_down(self, event=None):
        if event['button']==0:
            if 0<=event['x']<self.w and 0<=event['y']<self.h:
                self.active=True
                self.active_disp=True

    def b_up(self, event=None):
        if event['button']==0:
            if 0<=event['x']<self.w and 0<=event['y']<self.h:
                self.active=False

    def draw(self):
        self.fg0=7
        self.bg0=0
        if self.parent:
            self.fg0=self.parent.fg
            self.bg0=self.parent.bg
        fw=0
        fh=0
        box_type='focus'
        if self.active or self.active_disp:
            box_type='active'
            if self.active_disp:
                self.active_disp=False
        self.box_type=box_type
        fw=self.frame['w']*2
        fh=self.frame['h']*2
        cap_x=int(self.w/2-len(self.caption)/2)
        cap_y=int((self.h-fh)/2+fh/2)
        super().draw()
        self.screen.cursor_goto(cap_x, cap_y)
        c=self.theme[box_type][f'{self.box_name}.middle_center']
        if c:
            self.screen.set_foreground(c.fg)
            self.screen.set_background(c.bg)
        self.screen.print(self.caption)

class WidgetProgressBar(Widget):
    pass

class WidgetSlider(Widget):
    pass

class WidgetTextInput(Widget):
    pass

class WidgetTextArea(Widget):
    pass

class WidgetLabel(Widget):
    pass

class WidgetCheckBox(Widget):
    pass

class WidgetListBox(Widget):
    pass

class WidgetRadioBox(Widget):
    pass

class WidgetDropDown(Widget):
    pass

class WidgetSpinner(Widget):
    pass

class WidgetTitleBar(Widget):
    pass

class WidgetStatusBar(Widget):
    pass

class WidgetMenu(Widget):
    pass

class WidgetLabel(Widget):
    pass

class WidgetVBox(Widget):
    pass

class WidgetHBox(Widget):
    pass
