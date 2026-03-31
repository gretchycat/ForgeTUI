#!/usr/bin/python3
from __future__ import annotations
import sys, os, fcntl, select, asyncio, time, termios, tty, logging, pyte, re, icat
from libansiscreen.screen import Screen
from libansiscreen.renderer.ansi_emitter import ANSIEmitter, Box
from gm_termcontrol.termkeymap import gen_keymap


rgb_file_path = '/usr/share/X11/rgb.txt'

class termcontrol:
    def __init__(self):
        self.x11_colors = self.parse_rgb_file(rgb_file_path)
        self.image_support=[]
        self.img_cache={}
        term=os.environ.get('TERM', '')
        konsole_ver=os.environ.get('KONSOLE_VERSION', '')
        if 'kitty' in term:
            self.image_support.append('kitty')
        if 'vt340' in term or len(konsole_ver or '')>0:
            self.image_support.append('sixel')

    # ------------------------------------------------------------------
    # Mouse control
    # ------------------------------------------------------------------
    def enable_mouse(self, utf8=True, all_motion=False):
        """
        Enable mouse reporting.
        Parameters:
        - utf8: Use UTF-8 or SGR encoding for coordinates (1005 / 1006)
        - all_motion: Track all mouse motion events, even without buttons (1003)
        """
        codes = []
        # Base tracking
        codes.append("\x1b[?1002h")  # Button-event tracking (press/release + drag)
        # Optional: all motion reporting
        if all_motion:
            codes.append("\x1b[?1003h")  # Any-motion tracking (hover)
        # Coordinate encoding
        if utf8:
            codes.append("\x1b[?1005h")  # UTF-8 coordinates
        codes.append("\x1b[?1006h")      # SGR coordinates (decimal)
        return "".join(codes)

    def disable_mouse(self, utf8=True, all_motion=False):
        """
        Disable mouse reporting.
        """
        codes = []
        # Base tracking
        codes.append("\x1b[?1002l")  # Disable button-event tracking
        # Optional: disable all-motion reporting
        if all_motion:
            codes.append("\x1b[?1003l")  # Disable any-motion tracking
        # Coordinate encoding
        if utf8:
            codes.append("\x1b[?1005l")  # Disable UTF-8 coordinates
        codes.append("\x1b[?1006l")      # Disable SGR coordinates
        return "".join(codes)

    def enable_cursor(self):
        return "\x1b[?25h"

    def disable_cursor(self):
        return "\x1b[?25l"

    def normal_screen(self):
        return "\x1b[?1049l"

    def alt_screen(self):
        return "\x1b[?1049h"

    def set_title(self, title):
        return f"\x1b]0;{title}\\a"

    def pause_terminal_output(self):
        sys.stdout.flush()
        os.system('stty -icanon -echo')

    def resume_terminal_output(self):
        sys.stdout.flush()
        os.system('stty icanon echo')

    def parse_rgb_file(self, file_path):
        colors = {}
        if not os.path.isfile(file_path):
            return colors
        return colors
        with open(file_path, 'r') as file:
            for line in file:
                if not line.startswith('!'):
                    parts = line.strip().split('\t')
                    if len(parts) >= 4:
                        name = parts[3].lower()
                        red, green, blue = int(parts[0]), int(parts[1]), int(parts[2])
                        colors[name] = {'red':red, 'green':green, 'blue':blue}
        return colors

    def pause(self):
        print ('[pause]')
        return sys.stdin.readline()

    def get_terminal_size(self):
        import array, fcntl, sys, termios
        buf = array.array('H', [0, 0, 0, 0])
        fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, buf)
        # Create a dictionary with meaningful keys
        window_info = {
            "rows": buf[0],
            "columns": buf[1],
            "width": buf[2],
            "height": buf[3]
        }
        return window_info

    def color(self, color):
        if type(color)==int:
            return color
        co={
                'black'  : 0,
                'red'    : 1,
                'green'  : 2,
                'yellow' : 3,
                'brown'  : 3,
                'blue'   : 4,
                'magenta': 5,
                'cyan'   : 6,
                'white'  : 7,
                'brightblack'  : 8,
                'brightred'    : 9,
                'brightgreen'  : 10,
                'brightbrown'  : 11,
                'brightyellow' : 11,
                'brightblue'   : 12,
                'brightmagenta': 13,
                'brightcyan'   : 14,
                'brightwhite'  : 15,
            }
        if type(color)==str:
            regex = r'^([A-Fa-f0-9]{6})$'
            if re.match(regex, color) is not None:
                color={
                        'red'  :int(color[0:2], 16),
                        'green':int(color[2:4], 16),
                        'blue' :int(color[4:6], 16),
                      }
                return color
            regex = r'^([A-Fa-f0-9]{3})$'
            if re.match(regex, color) is not None:
                color={
                        'red'  :int(color[0:1], 16)*16,
                        'green':int(color[1:2], 16)*16,
                        'blue' :int(color[2:3], 16)*16,
                      }
                return color
            regex = r'^#([A-Fa-f0-9]{6})$'
            if re.match(regex, color) is not None:
                color={
                        'red'  :int(color[1:3], 16),
                        'green':int(color[3:5], 16),
                        'blue' :int(color[5:7], 16),
                      }
                return color
            regex = r'^#([A-Fa-f0-9]{3})$'
            if re.match(regex, color) is not None:
                color={
                        'red'  :int(color[1:2], 16)*16,
                        'green':int(color[2:3], 16)*16,
                        'blue' :int(color[3:4], 16)*16,
                      }
                return color
            if co.get(color):
                return co.get(color.lower())
            return self.x11_colors.get(color.lower())
        return None

    def getRGB(self, c):
        color=self.color(c)
        if type(color)==dict:
            return color
        if type(color)==int:
            pass #FIXME
        return {'red':127, 'green':127, 'blue':127}

    def ansicolor(self, fg='default', bg='default',
                  bold=False, dim=False, italic=False, underline=False,
                  strike=False, blink=False, blink2=False, reverse=False,
                  bold_is_bright=False):
        if fg=='default':
            fg=7
        if bg=='default':
            bg=None
        fg=self.color(fg)
        bg=self.color(bg)
        fgs=""
        bgs=""
        if type(fg)==int:
            if fg<16:
                if fg<8:
                    if bold_is_bright:
                        fgs=f"{fg+90}"
                    else:
                        fgs=f"{fg+30}"
                else:
                    fgs=f"{(fg-8)+90}"
            else:
                fgs=f'38;5;{fg}'
        elif type(fg)==dict:
            fgs=f'38;2;{fg["red"]};{fg["green"]};{fg["blue"]}'
        if type(bg)==int:
            if bg<16:
                if bg<8:
                    bgs=f"{bg+40}"
                else:
                    bgs=f"{(bg-8)+100}"
            else:
                bgs=f'48;5;{bg}'
        elif type(bg)==dict:
            bgs=f'48;2;{bg["red"]};{bg["green"]};{bg["blue"]}'
        bo, bl, bl2, dm, it, ul, st, rv="","","","","","","", ""
        if bold:bo='1;'
        if dim:bdm='2;'
        if italic:it='3;'
        if underline:ul='4;'
        if blink:bl='5;'
        if blink2:bl2='6;'
        if reverse:rv='7;'
        ansi=""
        if len(bgs) and len(fgs):
            ansi=f'{fgs};{bgs}'
        elif len(bgs):
            ansi=bgs
        elif len(fgs):
            ansi=fgs
        if len(ansi)>0:
            return f"\x1b[{bo}{dm}{it}{ul}{bl}{bl2}{rv}{ansi}m"
        return ""

    def drawRuler(self,w,h):
        buffer=''
        for y in range(0,h-2):
            for x in range(0,int((w)/10)):
                buffer+=self.gotoxy(x*10+1,y+1)
                buffer+=f'({x*10},{y})'
        return buffer

    def pyte_render(self, x, y, screen, line=1,
                    fg='default', bg='default',
                    fg0='default', bg0='default',
                    bold_is_bright=False):
        bold=False
        blink=False
        w=screen.columns
        h=screen.screen_lines
        start_line=line-1
        if start_line<0:
            start_line=int(screen.cursor.y-h+2)
        if start_line<0:
            start_line=0
        if start_line>int(screen.cursor.y-h+2):
            start_line=int(screen.cursor.y-h+2)
        buffer = self.ansicolor(fg, bg, bold=bold, blink=blink)
        screen.cursor_position(screen.screen_lines+start_line, 1)
        for yy in range(start_line, start_line+h):
            buffer += self.gotoxy(x, y+yy-(start_line))
            buffer+=self.ansicolor(fg, bg)
            for xx in range(w):
                if screen.buffer[yy][xx].fg!=fg or screen.buffer[yy][xx].bold!=bold:
                    fg=screen.buffer[yy][xx].fg
                    bold=screen.buffer[yy][xx].bold
                    buffer += self.ansicolor(fg, None, bold=bold, bold_is_bright=bold_is_bright)
                if screen.buffer[yy][xx].bg!=bg or screen.buffer[yy][xx].blink!=blink:
                    bg=screen.buffer[yy][xx].bg
                    blink=screen.buffer[yy][xx].blink
                    buffer += self.ansicolor(None, bg, blink=blink)
                buffer += screen.buffer[yy][xx].data
            buffer+=self.ansicolor(fg0, bg0)
        return buffer

    def gotoxy(self, x, y):
        return f'\x1b[{int(y)};{int(x)}f'

    def clear(self):
        return '\x1b[2J'

    def reset(self):
        return '\x1b[0m'

    def setbg(self, c):
        return self.ansicolor(None, c)

    def setfg(self, c):
        return self.ansicolor(c, None)

    def up(self, n):
        return f'\x1b[{n}A'

    def down(self, n):
        return f'\x1b[{n}B'

    def left(self, n):
        return f'\x1b[{n}D'

    def right(self, n):
        return f'\x1b[{n}C'

    def clear_images(self):
        out=''
        if 'kitty' in self.image_support:
            out+='\x1b_Ga=d\x1b\\'
        if 'sixel' in self.image_support:
            pass
        return out

    def showImage(self, image, x=0, y=0, w=30, h=15, showInfo=False, mode='auto', charset='utf8'):
        desc=""
        imgX,imgY=0,0
        if(showInfo):
            try:
                img = Image.open(image)
                imgX,imgY=img.size
                img.close()
            except:
                pass
            filename=os.path.basename(image)
            desc=f'({imgX}x{imgY}) {filename}'[:w]
            descX=int(x+(w/2)-(len(desc)/2))+1
            descY=int(y+h)-1
            desc=f'\x1b[s\x1b[48;5;245;30m\x1b[{descY};{descX}H{desc}\n'
        start_pos = f'\x1b[{y};{x+1}H'
        if not self.img_cache.get(image):
            ic=ICat(w=int(w), h=int(h), zoom='aspect', f=True, x=int(0), y=int(0), place=True, mode=mode, charset=charset)
            self.img_cache[image]=ic.print(image)
        return f'{start_pos}{self.img_cache[image]}{desc}'

def clean(input_string):
    # Use regular expressions to replace consecutive whitespace characters with a single space
    cleaned_string = re.sub(r'\s+', ' ', input_string)
    # Remove leading and trailing spaces
    return cleaned_string.strip()

