#!/usr/bin/python3
from __future__ import annotations
import uuid,os
from .widget_container import WidgetScrollArea

#terminal widgets
class WidgetLog(WidgetScrollArea):
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=None, \
            parent=None, name=None, v_bar=True, h_bar=True,\
            content_events=True, filename='output.log'):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, parent=parent, \
                         name=name or 'Log'+str(uuid.uuid4()), \
                         v_bar=v_bar, h_bar=h_bar, \
                         content_events=content_events)
        self.filename = filename
        self.handle = None
        self._last_size = 0

    def draw(self):
        if self.handle:
            try:
                if not os.path.exists(self.filename):
                    self.handle.close()
                    self.handle = None
                else:
                    current_size = os.path.getsize(self.filename)
                    if current_size < self._last_size:
                        self.handle.seek(0, os.SEEK_SET)
                        self.feed("--- Log truncated ---\n")
                        self._last_size = current_size
            except (OSError, ValueError):
                if self.handle:
                    self.handle.close()
                self.handle = None
        if not self.handle:
            if os.path.exists(self.filename):
                try:
                    self.handle = open(self.filename, "r", errors="ignore")
                    current_size = os.path.getsize(self.filename)
                    self.handle.seek(0, os.SEEK_SET) 
                    self.feed("--- Log file rotated/recreated ---\n")
                    self._last_size = current_size
                except OSError:
                    self.handle = None
        if self.handle:
            try:
                new_data = self.handle.read()
                if new_data:
                    self.feed(new_data)
                self._last_size = os.path.getsize(self.filename)
            except OSError:
                self.handle.close()
                self.handle = None
        super().draw()

class WidgetTerminal(WidgetScrollArea):
    def __init__(self, x=0, y=0, w=1.0, h=1.0, fg=7, bg=None, \
            parent=None, name=None, v_bar=True, h_bar=True,):
        super().__init__(x=x, y=y, w=w, h=h, fg=fg, bg=bg, parent=parent, \
                         name=name or 'Log'+str(uuid.uuid4()), \
                         v_bar=v_bar, h_bar=h_bar, \
                         content_events=False)
        self.events=[]
        self.content.addEvent('', self.queue_event)

    def queue_event(self, event=None):
        if event is not None:
            self.events.append(event)

    def get_event(self):
        if self.events:
            return self.events.pop(0)
        return None

    def process(self):
        pass

    def draw(self):
        self.process()
        return super().draw()
