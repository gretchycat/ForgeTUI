#!/usr/bin/python3
from __future__ import annotations
import sys, os, fcntl, select, asyncio, time, termios, tty, re

from .termkeymap import gen_keymap

class termInput:
    def __init__(self):
        self.fps=60
        self.timeout=1/self.fps
        self.start=0
        self.keymap=gen_keymap()
        self.buffer=''
        self.flags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
        self.filedescriptors = termios.tcgetattr(sys.stdin)
        self.raw=False
        self.__enter__()

    def __enter__(self):
        fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, self.flags | os.O_NONBLOCK)
        if self.raw:
            tty.setraw(sys.stdin)
        else:
            tty.setcbreak(sys.stdin)

    def __del__(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.filedescriptors)
        fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, self.flags & ~os.O_NONBLOCK)

    def __exit__(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.filedescriptors)
        fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, self.flags & ~os.O_NONBLOCK)

    def disable_keyboard_echo(self): # Get the current terminal attributes
        attributes = termios.tcgetattr(sys.stdin)
        # Disable echo flag
        attributes[3] = attributes[3] & ~termios.ECHO
        # Apply the modified attributes
        termios.tcsetattr(sys.stdin, termios.TCSANOW, attributes)

    def enable_keyboard_echo(self): # Get the current terminal attributes
        attributes = termios.tcgetattr(sys.stdin)
        # Enable echo flag
        attributes[3] = attributes[3] | termios.ECHO
        # Apply the modified attributes
        termios.tcsetattr(sys.stdin, termios.TCSANOW, attributes)

    def read(self, bin=False):
        self.buffer = ''
        try:
            rlist, _, _ = select.select([sys.stdin], [], [], self.timeout)
        except (InterruptedError, OSError) as e:
            if isinstance(e, InterruptedError) or getattr(e, "errno", None) == errno.EINTR:
                return self.buffer
            raise
        if rlist:
            if not bin:
                try:
                    # Read only a chunk of available buffer (e.g., 4096 bytes) instead of EOF
                    self.buffer += sys.stdin.read(4096)
                except Exception:
                    self.buffer += sys.stdin.buffer.read(4096).decode('utf-8', errors='ignore')
            else:
                self.buffer += sys.stdin.buffer.read(4096)
        return self.buffer

    def ord(self, d):
        if(type(d)==int):
            return d
        if(type(d)==str):
            return ord(d[0])
        if(type(d)==bytes):
            return int.from_bytes(d)
        return int(d)

    def split_codes(self, buffer): #TODO split by all of the key map values and then every character individually
        inputlist=buffer.split('\x1b')
        for k,i in enumerate(inputlist[1:], start=1):
            inputlist[k]='\x1b'+i
        if inputlist[0]=='':
            inputlist.pop(0)
        return inputlist

    def mouse_input(self, buffer):
        m = re.match(r"\x1b\[<(\d+);(\d+);(\d+)([Mm])", buffer)
        scroll_dir={64:'up', 65:'down',66:'left',67:'right'}
        if m:
            button, column, row, event = m.groups()
            detail=''
            button = int(button)
            action = "button down" if event == "M" else "button up" if event == "m" else "Unknown"
            if button>=64:
                if button<=67:
                    action='scroll '+scroll_dir[button]
                else:
                    action='scroll'
            elif button >= 32:
                button=button%32
                action='drag'
            column = int(column)-1
            row = int(row)-1
            return {'button':button, 'x':column, 'y':row,
                    'action':action}
        return None

    def read_input(self): # Get the current settings of the terminal
        buffer = self.read()
        inputs=self.split_codes(buffer)
        all_inputs=[]
        for i in inputs:
            key=self.keymap.get(i)
            if key:
                all_inputs.append(key)
                continue
            mouse=self.mouse_input(i)
            if mouse:
                all_inputs.append(mouse)
                continue
            all_inputs.append(i)
        return all_inputs

