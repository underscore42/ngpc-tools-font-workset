#!/usr/bin/env python3
"""mkfont.py - a replacement 8x8 font for the NGPC / NGP.

WHY THIS IS FREE
    SysSetSystemFont() writes the BIOS charset into tile RAM at codes 0-143.
    install_font() overwrites those codes IN PLACE, so a custom font costs
    nothing from the 144-255 custom-tile range every project fights over.

    Install order matters:
        SysSetSystemFont()  ->  install_font()  ->  install_tiles()

GLYPHS
    Authored as 5x7 masks ('#'/'.') in an 8x8 cell. Letterforms at 5x7 are
    largely dictated by the grid, so these are the obvious shapes rather than
    anyone's typeface.

STYLES
    plain    body only, index 1                    (crisp, smallest)
    shadow   body index 1 + 1px drop shadow index 2  (reads far better on a
             washed-out LCD in sunlight - value contrast, not hue)
    outline  body index 1 + full outline index 2     (works on any background)

Covers 0x20-0x5F: space, punctuation, digits, uppercase. 64 glyphs, the
classic arcade range.
"""
import os
import sys

OUT = os.path.join(os.path.dirname(__file__), '..', 'out')

# ---------------------------------------------------------------------------
# 5 wide x 7 tall masks, code 0x20 upward.
# ---------------------------------------------------------------------------
G = {}
def d(ch, *rows): G[ch] = list(rows)

d(' ', ".....", ".....", ".....", ".....", ".....", ".....", ".....")
d('!', "..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#..")
d('"', ".#.#.", ".#.#.", ".....", ".....", ".....", ".....", ".....")
d('#', ".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#.")
d('$', "..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#..")
d('%', "#...#", "#...#", "...#.", "..#..", ".#...", "#...#", "#...#")
d('&', ".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#")
d("'", "..#..", "..#..", ".....", ".....", ".....", ".....", ".....")
d('(', "...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#.")
d(')', ".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#...")
d('*', ".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", ".....")
d('+', ".....", "..#..", "..#..", "#####", "..#..", "..#..", ".....")
d(',', ".....", ".....", ".....", ".....", "..##.", "..#..", ".#...")
d('-', ".....", ".....", ".....", "#####", ".....", ".....", ".....")
d('.', ".....", ".....", ".....", ".....", ".....", "..##.", "..##.")
d('/', "....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#....")
d('0', ".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###.")
d('1', "..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###.")
d('2', ".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####")
d('3', "#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###.")
d('4', "...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#.")
d('5', "#####", "#....", "####.", "....#", "....#", "#...#", ".###.")
d('6', "..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###.")
d('7', "#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#..")
d('8', ".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###.")
d('9', ".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##..")
d(':', ".....", "..##.", "..##.", ".....", "..##.", "..##.", ".....")
d(';', ".....", "..##.", "..##.", ".....", "..##.", "..#..", ".#...")
d('<', "....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#")
d('=', ".....", ".....", "#####", ".....", "#####", ".....", ".....")
d('>', "#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#....")
d('?', ".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#..")
d('@', ".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###.")
d('A', ".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
d('B', "####.", "#...#", "#...#", "####.", "#...#", "#...#", "####.")
d('C', ".###.", "#...#", "#....", "#....", "#....", "#...#", ".###.")
d('D', "####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####.")
d('E', "#####", "#....", "#....", "####.", "#....", "#....", "#####")
d('F', "#####", "#....", "#....", "####.", "#....", "#....", "#....")
d('G', ".###.", "#...#", "#....", "#..##", "#...#", "#...#", ".###.")
d('H', "#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
d('I', ".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###.")
d('J', "..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##..")
d('K', "#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#")
d('L', "#....", "#....", "#....", "#....", "#....", "#....", "#####")
d('M', "#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#")
d('N', "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#")
d('O', ".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.")
d('P', "####.", "#...#", "#...#", "####.", "#....", "#....", "#....")
d('Q', ".###.", "#...#", "#...#", "#...#", "#.#.#", "#..##", ".####")
d('R', "####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#")
d('S', ".####", "#....", "#....", ".###.", "....#", "....#", "####.")
d('T', "#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..")
d('U', "#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.")
d('V', "#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#..")
d('W', "#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#")
d('X', "#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#")
d('Y', "#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..")
d('Z', "#####", "....#", "...#.", "..#..", ".#...", "#....", "#####")
d('[', ".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###.")
d('\\', "#....", ".#...", ".#...", "..#..", "...#.", "...#.", "....#")
d(']', ".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###.")
d('^', "..#..", ".#.#.", "#...#", ".....", ".....", ".....", ".....")
d('_', ".....", ".....", ".....", ".....", ".....", ".....", "#####")

FIRST, LAST = 0x20, 0x5F


def check():
    missing = [c for c in range(FIRST, LAST + 1) if chr(c) not in G]
    if missing:
        sys.exit('missing glyphs: %s' % ' '.join('0x%02X' % c for c in missing))
    for ch, rows in G.items():
        if len(rows) != 7:
            sys.exit('%r: %d rows' % (ch, len(rows)))
        for r in rows:
            if len(r) != 5:
                sys.exit('%r: row %r not 5 wide' % (ch, r))
    return True


def cell(ch, style):
    """5x7 mask -> 8x8 index map."""
    m = G[ch]
    body = [[0] * 8 for _ in range(8)]
    for y in range(7):
        for x in range(5):
            if m[y][x] == '#':
                body[y][x] = 1
    out = [[0] * 8 for _ in range(8)]
    for y in range(8):
        for x in range(8):
            out[y][x] = body[y][x]
    if style == 'plain':
        return out
    if style == 'shadow':
        for y in range(8):
            for x in range(8):
                if out[y][x]:
                    continue
                if y > 0 and x > 0 and body[y - 1][x - 1]:
                    out[y][x] = 2
        return out
    if style == 'outline':
        for y in range(8):
            for x in range(8):
                if out[y][x]:
                    continue
                near = False
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < 8 and 0 <= xx < 8 and body[yy][xx]:
                            near = True
                if near:
                    out[y][x] = 2
        return out
    sys.exit('unknown style %r' % style)


def words(idx):
    ws = []
    for y in range(8):
        w = 0
        for x in range(8):
            w |= (idx[y][x] & 3) << (14 - x * 2)
        ws.append(w)
    return ws


def emit(style):
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    tiles = [words(cell(chr(c), style)) for c in range(FIRST, LAST + 1)]
    name = 'font_%s' % style
    with open(os.path.join(OUT, name + '.c'), 'w') as f:
        f.write('/* %s.c - replacement NGPC font, style "%s".\n'
                ' * GENERATED by tools/mkfont.py - do not hand edit.\n'
                ' *\n'
                ' * %d glyphs, codes 0x%02X-0x%02X. Overwrites the BIOS charset\n'
                ' * IN PLACE, so it costs nothing from the 144-255 range.\n'
                ' *\n'
                ' * Install order:  SysSetSystemFont() -> install_font()\n'
                ' *                 -> install_tiles()\n'
                ' *\n'
                ' * Palette: index 1 = body%s\n'
                ' */\n#include "%s.h"\n\n'
                % (name, style, len(tiles), FIRST, LAST,
                   '' if style == 'plain' else ', index 2 = %s' % style, name))
        f.write('static const u16 %s_tiles[%d][8] = {\n' % (name, len(tiles)))
        for i, t in enumerate(tiles):
            c = FIRST + i
            gl = chr(c) if 33 <= c <= 126 else ' '
            f.write('    { %s },  /* 0x%02X %s */\n'
                    % (', '.join('0x%04X' % w for w in t), c, gl))
        f.write('};\n\nvoid install_font(void) {\n')
        f.write('    InstallTileSetAt((const unsigned short (*)[8])%s_tiles, '
                '%d, 0x%02X);\n}\n' % (name, len(tiles) * 8, FIRST))
    with open(os.path.join(OUT, name + '.h'), 'w') as f:
        f.write('/* %s.h - GENERATED by tools/mkfont.py */\n'
                '#ifndef %s_H\n#define %s_H\n\n'
                '#include "ngpc.h"\n#include "library.h"\n\n'
                '#define FONT_FIRST 0x%02X\n#define FONT_LAST  0x%02X\n\n'
                'void install_font(void);\n\n#endif\n'
                % (name, name.upper(), name.upper(), FIRST, LAST))
    return tiles


if __name__ == '__main__':
    check()
    for st in ('plain', 'shadow', 'outline'):
        t = emit(st)
        print('%-8s %d glyphs, %d tiles, codes 0x%02X-0x%02X -> out/font_%s.c'
              % (st, len(t), len(t), FIRST, LAST, st))
