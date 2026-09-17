#!/usr/bin/env python3
"""rip.py - pull glyph masks out of fontdump screenshots.

Closes the loop:

    fontdump ROM  ->  screenshot  ->  rip.py  ->  editable masks  ->  mkfont.py

Reads one or both fontdump pages, finds the tile grid, and emits every glyph
as an 8x8 ASCII mask you can paste into a generator or edit by hand.

Usage
    python3 rip.py page1.png [page2.png]            all glyphs
    python3 rip.py page1.png page2.png --codes A1-DF   just the katakana
    python3 rip.py page1.png --show 41              print one glyph big

Why bother
    Hand-reconstructing 8x8 Japanese letterforms from memory does not work -
    the strokes do not survive the resolution and you get plausible-looking
    glyphs that are simply wrong. Ripping the real charset gives you the
    shapes the hardware actually uses, which you can then restyle (add a drop
    shadow, thicken, outline) with confidence that the letterform underneath
    is correct.

Assumptions
    Matches the layout fontdump/src/main.c draws:
      - page 1 = codes 0x00-0x8F, page 2 = 0x90-0xFF
      - 16 columns, tiles start at tile x=3, first tile row at tile y=1
      - native 160x152; larger screenshots are scaled down automatically
    Alignment is SELF-CHECKED against known ASCII, so a layout change or a
    bad crop is caught rather than silently producing garbage.
"""
import sys
import os

try:
    from PIL import Image
except ImportError:
    sys.exit('rip.py needs Pillow:  pip install pillow')

GRID_X, GRID_Y, COLS = 3, 1, 16
NATIVE = (160, 152)

# Known-good shapes used to verify the grid is where we think it is.
# ink-pixel counts for a handful of unambiguous ASCII glyphs.
PROBE = {0x20: 0, 0x41: 17, 0x30: 19, 0x2E: 4}

# The BIOS charset layout, established by dumping a real NGPC.
# JIS X 0201: ASCII in 0x20-0x7F, half-width katakana in 0xA1-0xDF.
JIS_KANA = {
    0xA1: '。', 0xA2: '「', 0xA3: '」', 0xA4: '、', 0xA5: '・', 0xA6: 'ヲ',
    0xA7: 'ァ', 0xA8: 'ィ', 0xA9: 'ゥ', 0xAA: 'ェ', 0xAB: 'ォ', 0xAC: 'ャ',
    0xAD: 'ュ', 0xAE: 'ョ', 0xAF: 'ッ', 0xB0: 'ー', 0xB1: 'ア', 0xB2: 'イ',
    0xB3: 'ウ', 0xB4: 'エ', 0xB5: 'オ', 0xB6: 'カ', 0xB7: 'キ', 0xB8: 'ク',
    0xB9: 'ケ', 0xBA: 'コ', 0xBB: 'サ', 0xBC: 'シ', 0xBD: 'ス', 0xBE: 'セ',
    0xBF: 'ソ', 0xC0: 'タ', 0xC1: 'チ', 0xC2: 'ツ', 0xC3: 'テ', 0xC4: 'ト',
    0xC5: 'ナ', 0xC6: 'ニ', 0xC7: 'ヌ', 0xC8: 'ネ', 0xC9: 'ノ', 0xCA: 'ハ',
    0xCB: 'ヒ', 0xCC: 'フ', 0xCD: 'ヘ', 0xCE: 'ホ', 0xCF: 'マ', 0xD0: 'ミ',
    0xD1: 'ム', 0xD2: 'メ', 0xD3: 'モ', 0xD4: 'ヤ', 0xD5: 'ユ', 0xD6: 'ヨ',
    0xD7: 'ラ', 0xD8: 'リ', 0xD9: 'ル', 0xDA: 'レ', 0xDB: 'ロ', 0xDC: 'ワ',
    0xDD: 'ン', 0xDE: '゛', 0xDF: '゜',
}

# Romaji names for the katakana, so ripped masks land with usable identifiers.
KANA_NAME = {
    0xA1: 'MARU', 0xA2: 'KAKKO_L', 0xA3: 'KAKKO_R', 0xA4: 'TEN',
    0xA5: 'NAKAGURO', 0xA6: 'WO', 0xA7: 'A_S', 0xA8: 'I_S', 0xA9: 'U_S',
    0xAA: 'E_S', 0xAB: 'O_S', 0xAC: 'YA_S', 0xAD: 'YU_S', 0xAE: 'YO_S',
    0xAF: 'TSU_S', 0xB0: 'BAR', 0xB1: 'A', 0xB2: 'I', 0xB3: 'U', 0xB4: 'E',
    0xB5: 'O', 0xB6: 'KA', 0xB7: 'KI', 0xB8: 'KU', 0xB9: 'KE', 0xBA: 'KO',
    0xBB: 'SA', 0xBC: 'SHI', 0xBD: 'SU', 0xBE: 'SE', 0xBF: 'SO', 0xC0: 'TA',
    0xC1: 'CHI', 0xC2: 'TSU', 0xC3: 'TE', 0xC4: 'TO', 0xC5: 'NA', 0xC6: 'NI',
    0xC7: 'NU', 0xC8: 'NE', 0xC9: 'NO', 0xCA: 'HA', 0xCB: 'HI', 0xCC: 'FU',
    0xCD: 'HE', 0xCE: 'HO', 0xCF: 'MA', 0xD0: 'MI', 0xD1: 'MU', 0xD2: 'ME',
    0xD3: 'MO', 0xD4: 'YA', 0xD5: 'YU', 0xD6: 'YO', 0xD7: 'RA', 0xD8: 'RI',
    0xD9: 'RU', 0xDA: 'RE', 0xDB: 'RO', 0xDC: 'WA', 0xDD: 'N',
    0xDE: 'DAKUTEN', 0xDF: 'HANDAKUTEN',
}


def load(path):
    """Open a screenshot, scale to native, and work out which value is ink."""
    im = Image.open(path).convert('L')
    if im.size != NATIVE:
        im = im.resize(NATIVE, Image.NEAREST)
    hist = {}
    for v in im.tobytes():
        hist[v] = hist.get(v, 0) + 1
    if len(hist) < 2:
        sys.exit('%s: only one grey level - is this a blank screen?' % path)
    # background is the most common value; ink is the most common of the rest
    order = sorted(hist.items(), key=lambda kv: -kv[1])
    bg = order[0][0]
    ink = order[1][0]
    return im.load(), ink, bg


def glyph(px, ink, code, page_base):
    idx = code - page_base
    r, c = idx >> 4, idx & 15
    ox = (GRID_X + c) * 8
    oy = (GRID_Y + r) * 8
    return [''.join('#' if px[ox + x, oy + y] == ink else '.'
                    for x in range(8)) for y in range(8)]


def verify(px, ink):
    """Catch a moved grid or a bad crop instead of emitting nonsense."""
    bad = []
    for code, expect in PROBE.items():
        got = sum(row.count('#') for row in glyph(px, ink, code, 0x00))
        if abs(got - expect) > 4:
            bad.append('0x%02X: %d ink px, expected about %d' % (code, got, expect))
    if bad:
        print('WARNING: page 1 does not look like the expected layout:',
              file=sys.stderr)
        for b in bad:
            print('   ' + b, file=sys.stderr)
        print('   check the screenshot is a full 160x152 fontdump frame',
              file=sys.stderr)
        return False
    return True


def parse_codes(spec):
    out = []
    for part in spec.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-')
            out += list(range(int(a, 16), int(b, 16) + 1))
        else:
            out.append(int(part, 16))
    return out


def name_for(code):
    if code in KANA_NAME:
        return KANA_NAME[code]
    if 0x41 <= code <= 0x5A:
        return 'LAT_%s' % chr(code)
    if 0x30 <= code <= 0x39:
        return 'DIG_%s' % chr(code)
    return 'C%02X' % code


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)

    # walk the args so an option's VALUE is never mistaken for a filename
    pages, codes, show = [], None, None
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--codes':
            codes = parse_codes(args[i + 1]); i += 2
        elif a == '--show':
            show = int(args[i + 1], 16); i += 2
        elif a.startswith('--'):
            sys.exit('unknown option %s' % a)
        else:
            pages.append(a); i += 1
    if not pages:
        sys.exit('give me at least one fontdump screenshot')

    loaded = []
    if len(pages) >= 1:
        px, ink, bg = load(pages[0])
        ok = verify(px, ink)
        loaded.append((px, ink, 0x00, 0x00, 0x8F, ok))
    if len(pages) >= 2:
        px, ink, bg = load(pages[1])
        loaded.append((px, ink, 0x90, 0x90, 0xFF, True))

    def get(code):
        for px, ink, base, lo, hi, ok in loaded:
            if lo <= code <= hi:
                return glyph(px, ink, code, base)
        return None

    if show is not None:
        g = get(show)
        if g is None:
            sys.exit('0x%02X is not in the pages supplied' % show)
        print('0x%02X  %s  %s' % (show, name_for(show), JIS_KANA.get(show, '')))
        for row in g:
            print('   ' + row.replace('.', ' ').replace('#', '##')[:16])
        return

    if codes is None:
        codes = [c for px, ink, base, lo, hi, ok in loaded
                 for c in range(lo, hi + 1)]

    print('# Ripped from a real NGPC BIOS charset by fontgen/rip.py.')
    print('# 8x8 masks, "#" = ink. Paste into a generator or edit by hand.')
    print('# ASCII lives at 0x20-0x7F, half-width katakana at 0xA1-0xDF')
    print('# (JIS X 0201). Dakuten is a SEPARATE cell: 0xDE, handakuten 0xDF.')
    print('GLYPHS = {')
    n = 0
    for code in codes:
        g = get(code)
        if g is None:
            continue
        if not any('#' in r for r in g):
            continue
        jis = JIS_KANA.get(code, '')
        label = chr(code) if 0x21 <= code <= 0x7E else jis
        print("    0x%02X: [   # %-4s %s" % (code, name_for(code), label))
        for row in g:
            print('        "%s",' % row)
        print('    ],')
        n += 1
    print('}')
    print('# %d non-blank glyphs' % n)


if __name__ == '__main__':
    main()
