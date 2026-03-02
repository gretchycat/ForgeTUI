#!/usr/bin/python3
from __future__ import annotations
import sys, os, fcntl, select, asyncio, time, termios, tty, logging, pyte, re, icat
try:
    from libansiscreen.screen import Screen
    from libansiscreen.renderer.ansi_emitter import ANSIEmitter, Box
except:
    Screen=None
from .termkeymap import gen_keymap
from .widget import widget


