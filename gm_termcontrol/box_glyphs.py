
from libansiscreen.cell import Cell
from libansiscreen.color.rgb import Color
from libansiscreen.color.palette import Palette, create_ansi_256_palette
"""
         0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
U+250x   ─   ━   │   ┃   ┄   ┅   ┆   ┇   ┈   ┉   ┊   ┋   ┌   ┍   ┎   ┏
U+251x   ┐   ┑   ┒   ┓   └   ┕   ┖   ┗   ┘   ┙   ┚   ┛   ├   ┝   ┞   ┟
U+252x   ┠   ┡   ┢   ┣   ┤   ┥   ┦   ┧   ┨   ┩   ┪   ┫   ┬   ┭   ┮   ┯
U+253x   ┰   ┱   ┲   ┳   ┴   ┵   ┶   ┷   ┸   ┹   ┺   ┻   ┼   ┽   ┾   ┿

         0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
U+254x   ╀   ╁   ╂   ╃   ╄   ╅   ╆   ╇   ╈   ╉   ╊   ╋   ╌   ╍   ╎   ╏
U+255x   ═   ║   ╒   ╓   ╔   ╕   ╖   ╗   ╘   ╙   ╚   ╛   ╜   ╝   ╞   ╟
U+256x   ╠   ╡   ╢   ╣   ╤   ╥   ╦   ╧   ╨   ╩   ╪   ╫   ╬   ╭   ╮   ╯
U+257x   ╰   ╱   ╲   ╳   ╴   ╵   ╶   ╷   ╸   ╹   ╺   ╻   ╼   ╽   ╾   ╿

         0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
U+258x   ▀   ▁   ▂   ▃   ▄   ▅   ▆   ▇   █   ▉   ▊   ▋   ▌   ▍   ▎   ▏
U+259x   ▐   ░   ▒   ▓   ▔   ▕   ▖   ▗   ▘   ▙   ▚   ▛   ▜   ▝   ▞   ▟
U+25Ax   ■   □   ▢   ▣   ▤   ▥   ▦   ▧   ▨   ▩   ▪   ▫   ▬   ▭   ▮   ▯
U+25Bx   ▰   ▱   ▲   △   ▴   ▵   ▶   ▷   ▸   ▹   ►   ▻   ▼   ▽   ▾   ▿

         0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
U+25Cx   ◀   ◁   ◂   ◃   ◄   ◅   ◆   ◇   ◈   ◉   ◊   ○   ◌   ◍   ◎   ●
U+25Dx   ◐   ◑   ◒   ◓   ◔   ◕   ◖   ◗   ◘   ◙   ◚   ◛   ◜   ◝   ◞   ◟
U+25Ex   ◠   ◡   ◢   ◣   ◤   ◥   ◦   ◧   ◨   ◩   ◪   ◫   ◬   ◭   ◮   ◯
U+25Fx   ◰   ◱   ◲   ◳   ◴   ◵   ◶   ◷   ◸   ◹   ◺   ◻   ◼   ◽   ◾   ◿

         0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
U+218x   ↀ   ↁ   ↂ   Ↄ   ↄ   ↅ   ↆ   ↇ   ↈ   ↉   ↊   ↋   ↌   ↍   ↎   ↏
U+219x   ←   ↑   →   ↓   ↔   ↕   ↖   ↗   ↘   ↙   ↚   ↛   ↜   ↝   ↞   ↟
U+21Ax   ↠   ↡   ↢   ↣   ↤   ↥   ↦   ↧   ↨   ↩   ↪   ↫   ↬   ↭   ↮   ↯
U+21Bx   ↰   ↱   ↲   ↳   ↴   ↵   ↶   ↷   ↸   ↹   ↺   ↻   ↼   ↽   ↾   ↿

         0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
U+21Cx   ⇀   ⇁   ⇂   ⇃   ⇄   ⇅   ⇆   ⇇   ⇈   ⇉   ⇊   ⇋   ⇌   ⇍   ⇎   ⇏
U+21Dx   ⇐   ⇑   ⇒   ⇓   ⇔   ⇕   ⇖   ⇗   ⇘   ⇙   ⇚   ⇛   ⇜   ⇝   ⇞   ⇟
U+21Ex   ⇠   ⇡   ⇢   ⇣   ⇤   ⇥   ⇦   ⇧   ⇨   ⇩   ⇪   ⇫   ⇬   ⇭   ⇮   ⇯
U+21Fx   ⇰   ⇱   ⇲   ⇳   ⇴   ⇵   ⇶   ⇷   ⇸   ⇹   ⇺   ⇻   ⇼   ⇽   ⇾   ⇿
"""

grchr={}
grchr['ascii']={
                'hline':'-', 'vline':'|',
                'hline2':'=', 'vline2':'|',
                'UP': '^', 'DOWN': 'v', 'LEFT': '<', 'RIGHT': '>',
                'TH':'^', 'BH':'o',
                'B0':' ', 'B25':':', 'B50':'$', 'B75':'#', 'B100':'@',
                'BLC':'\\', 'TLC':'/', 'BRC':'/', 'TRC':'\\',
                'BLB':'+', 'TLB':'+', 'BRB':'+', 'TRB':'+',
                'BLR':'+', 'TLR':'+', 'BRR':'+', 'TRR':'+',
                'BL2':'+', 'TL2':'+', 'BR2':'+', 'TR2':'+',
                }

grchr['utf8']={ 'hline':'\u2500', 'vline':'\u2502', #1 line
                'hline2':'\u2550', 'vline2':'\u2551', #2 line
                'UP': '\u25b2', 'DOWN': '\u25bc',
                'LEFT': '\u25c0', 'RIGHT': '\u25b6',
                'TH':'\u2580', 'BH':'\u2584',
                'B0':' ', 'B25':'\u2591', 'B50':'\u2593',
                'B75':'\u2593', 'B100':'\u2588',
                '3BAR':'\u2630',
                'U':'\u2575', 'D':'\u2577', 'L':'\u2574', 'R':'\u2576',
                'UD': '\u2502', 'LR':'\u2500',
                'UL': '\u2518', 'UR':'\u2514',
                'LD': '\u2510', 'RD':'\u250c',
                'ULR': '\u2534','LRD':'\u252c',
                'ULD': '\u2561','URD':'\u251c', 'ULRD':'\u253c',
                'UD.2': '\u2551', 'LR.2':'\u2550',
                'UL.2': '\u255d', 'UR.2':'\u255a',
                'LD.2': '\u2557', 'RD.2':'\u2554',
                'ULR.2': '\u2569','LRD.2':'\u2566',
                'ULD.2': '\u2563','URD.2':'\u2560', 'ULRD.2':'\u256c',
                'UL.c': '\u256f', 'UR.c':'\u2514',
                'LD.c': '\u256e', 'RD.c':'\u256d',
                'U.w':'\u2579', 'D.w':'\u257b',
                'L.w':'\u2578', 'R.w':'\u257a',
                'UD.w':'\u2503', 'LR.w':'\u2501',
                'RD.w':'\u250f', 'LD.w':'\u2513',
                'UR.w':'\u2517', 'UL.w':'\u251b',
                'LRD.w':'\u2533', 'ULR.w':'\u253b',
                'URD.w':'\u2523', 'ULD.w':'\u252b', 'ULRD.w':'\u254b',
                'UD.w.d2':'\u254f', 'LR.w.d2':'\u254d',
                'UD.w.d3':'\u2507', 'LR.w.d3':'\u2505',
                'UD.w.d4':'\u250b', 'LR.w.d4':'\u2509',
                'UD.d2':'\u254e', 'LR.d2':'\u254c',
                'UD.d3':'\u2506', 'LR.d3':'\u2504',
                'UD.d4':'\u250a', 'LR.d4':'\u2508',
               }

theme={}
theme['inside']={
        'TL': 'BH', 'TC': 'BH', 'TR': 'BH',
        'ML': 'B100', 'MC': 'B75', 'MR': 'B100',
        'BL': 'TH', 'BC': 'TH', 'BR': 'TH',
        'SU': 'UP','SD':'DOWN', 'SL':'LEFT', 'SR':'RIGHT',
        'SHR':'B25', 'SVR':'B25','SH':'B100',
        'TB':'3BAR','TT':' ',
        }

theme['outside']={
        'TL': 'B100', 'TC': 'TH', 'TR': 'B100',
        'ML': 'B100', 'MC': 'B0', 'MR': 'B100',
        'BL': 'B100', 'BC': 'BH', 'BR': 'B100',
        'SU': 'UP','SD':'DOWN', 'SL':'LEFT', 'SR':'RIGHT',
        'SHR':'B25', 'SVR':'B25','SH':'B100',
        'TB':'3BAR','TT':' ',
        }

theme['plot']=theme['outside']

theme['curve']={
        'TL': 'RD.c', 'TC': 'LR', 'TR': 'LD.c',
        'ML': 'UD', 'MC': 'B0', 'MR': 'UD',
        'BL': 'UR.c', 'BC': 'LR', 'BR': 'UL.c',
        'SU': 'UP','SD':'DOWN', 'SL':'LEFT', 'SR':'RIGHT',
        'SHR':'B25', 'SVR':'B25','SH':'B100',
        'TB':'3BAR','TT':' ',
        }

theme['line']={
        'TL': 'RD', 'TC': 'LR', 'TR': 'LD',
        'ML': 'UD', 'MC': 'B0', 'MR': 'UD',
        'BL': 'UR', 'BC': 'LR', 'BR': 'UL',
        'SU': 'UP','SD':'DOWN', 'SL':'LEFT', 'SR':'RIGHT',
        'SHR':'B25', 'SVR':'B25','SH':'B100',
        'TB':'3BAR','TT':' ',
        }

theme['2line']={
        'TL': 'RD.2', 'TC': 'LR.2', 'TR': 'LD.2',
        'ML': 'UD.2', 'MC': 'B0', 'MR': 'UD.2',
        'BL': 'UR.2', 'BC': 'LR.2', 'BR': 'UL.2',
        'SU': 'UP','SD':'DOWN', 'SL':'LEFT', 'SR':'RIGHT',
        'SHR':'B25', 'SVR':'B25','SH':'B100',
        'TB':'3BAR','TT':' ',
        }

theme_template={
        'box.top_left': ( 'RD', '#fff', '#bg', 0, None),
        'box.top_center': ( 'LR', '#ddd', '#bg', 0, None),
        'box.top_right': ( 'LD', '#aaa', '#bg', 0, None),
        'box.middle_left': ( 'UD', '#ddd', '#bg', 0, None),
        'box.middle_center': ( 'B0', '#fg', '#bg', 0, None),
        'box.middle_right': ( 'UD', '#888', '#bg', 0, None),
        'box.bottom_left': ( 'UR', '#aaa', '#bg', 0, None),
        'box.bottom_center': ( 'LR', '#888', '#bg', 0, None),
        'box.bottom_right': ( 'UL', '#555', '#bg', 0, None),
        'scroll.up': ( 'UP', '#000', '#aaa', 0, None),
        'scroll.down': ('DOWN', '#000', '#aaa', 0, None),
        'scroll.left': ('LEFT', '#000', '#aaa', 0, None),
        'scroll.right': ('RIGHT', '#000', '#aaa', 0, None),
        'scroll.h': ('B25', '#000', '#aaa', 0, None),
        'scroll.v': ('B25', '#000', '#aaa', 0, None),
        'scroll.handle': ('B100', '#000', '#aaa', 0, None),
        'title.bar': ('LR', '#44f', '#00a', 0, None),
        'title.text': (' ', '#fff', '#00A', 1, { 'align':'center' }),
        }

def make_theme(style=None, template=theme_template, fg="#aaa", bg="#000", inactive='darken 50', parent='desaturate 50'):
    fcs_thm=template.copy()
    for k,v in template.items():
        c, tfg, tbg, attr, properties=v
        if style is not None:
            c=f"{c}.{style}"
        t=None
        while '.' in c and not grchr['utf8'].get(c):
            spc=c.split('.')
            spc.pop()
            c='.'.join(spc)
        if tfg=='#fg':
            tfg=fg
        if tbg=='#bg':
            tbg=bg
        fcs_thm[k]=Cell(grchr['utf8'].get(c),
                        Color.set(tfg),
                        Color.set(tbg), attr)
    off_thm=fcs_thm.copy()
    prnt_thm=fcs_thm.copy()
    return {'focus':fcs_thm, 'off':off_thm, 'parent':prnt_thm}


