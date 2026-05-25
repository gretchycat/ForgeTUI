#!/usr/bin/python3
from __future__ import annotations
import sys, os, select, re
from libansiscreen.screen import Screen
from libansiscreen.color.palette import Palette, create_ansi_256_palette
from .termcontrol import termcontrol
from .terminput import termInput
from .theme import grchr, theme, make_theme
import signal
import copy
import uuid

from gm_termcontrol.widget_container import WidgetScrollArea
#terminal widgets
class WidgetLog(WidgetScrollArea):
    pass

class WidgetTerminal(WidgetScrollArea):
    pass
