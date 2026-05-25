#!/usr/bin/python3
from __future__ import annotations
import sys, os, select, re
import signal
import uuid
from .widget_container import WidgetScrollArea

#terminal widgets
class WidgetLog(WidgetScrollArea):
    pass

class WidgetTerminal(WidgetScrollArea):
    pass

