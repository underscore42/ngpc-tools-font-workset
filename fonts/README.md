# ngpc-fontkit

Font tooling for the Neo Geo Pocket / Color. Three parts:

| | what it is |
|---|---|
| `fontdump/` | a tiny **ROM** that paints the BIOS charset on screen so you can photograph it |
| `fontgen/rip.py` | pulls glyph masks **out of** a fontdump screenshot |
| `fontgen/mkfont.py` | builds a replacement font **into** installable tile data |
| `reference/` | the charset already dumped from real hardware, plus what it taught us |

## The loop

```
fontdump ROM  ->  screenshot  ->  rip.py  ->  edit masks  ->  mkfont.py  ->  font.c
```

You only need `fontdump` once per BIOS revision. `reference/` already has the
result, so most of the time you start at `rip.py` or `mkfont.py`.

## Why a font costs zero tiles

`SysSetSystemFont()` writes the BIOS charset into tile RAM. `install_font()`
overwrites those codes **in place**, so a replacement font takes nothing from
the custom-tile range every project fights over.

```c
SysSetSystemFont();   /* charset into tile RAM — writes BOTH BG planes */
install_font();       /* overwrite 0x20-0x5F with yours                */
install_tiles();      /* your game art                                 */
```

Order matters. `SysSetSystemFont()` must come first or it overwrites you.

**But read `reference/CHARSET.md` before choosing where your art lives.** The
BIOS charset runs to `0xFF`, not `0x8F`, and the usual "custom tiles at 144+"
convention sits on top of the katakana block.

---

## fontdump — dump a BIOS charset

Standalone project with its own `src/`, so a universal Makefile builds it
unmodified.

```sh
cp -r ngpc-project-template ngpc-fontdump
cd ngpc-fontdump && rm -f src/*.c src/*.h
cp /path/to/fontkit/fontdump/src/* src/
make
```

Needs `Makefile`, `toolchain.mk`, `lcf/` and `common/` from the template —
`main.c` includes `ngpc.h` and `library.h`.

Paints codes `0x00`–`0x8F` in a 16-wide grid with hex rulers. **OPTION** pages
to `0x90`–`0xFF`. Screenshot both. Mednafen is fine; you don't need a cart.

CartID `0x0055`, title `FONTDUMP`.

---

## rip.py — screenshot to masks

```sh
python3 rip.py page1.png page2.png                  # everything
python3 rip.py page1.png page2.png --codes A1-DF    # just the katakana
python3 rip.py page1.png page2.png --show C0        # one glyph, big
```

Emits 8x8 ASCII masks as a Python dict. Auto-detects which grey is ink,
rescales oversized screenshots, and **self-checks the grid against known
ASCII** so a bad crop is reported rather than silently producing garbage.

Katakana come out with romaji identifiers (`TA`, `SHI`, `DAKUTEN`), so ripped
masks are usable as-is.

---

## mkfont.py — masks to installable tiles

```sh
python3 mkfont.py     # -> out/font_{plain,shadow,outline}.[ch]
python3 preview.py    # -> preview sheets at 1x and 3x
```

64 glyphs, codes `0x20`–`0x5F`: space, punctuation, digits, uppercase — the
classic arcade range. Authored as 5x7 masks in an 8x8 cell, so there's a pixel
of letterspacing and a pixel of leading and text never touches.

| style | index 1 | index 2 |
|---|---|---|
| `plain` | body | — |
| `shadow` | body | 1px drop shadow |
| `outline` | body | full outline |

`shadow` and `outline` leave index 3 free for a highlight or a second text
colour on the same palette.

**Default to `shadow`.** NGPC screens wash out badly in sunlight and hue
separation is the first thing to go, so design for **value** contrast. A drop
shadow survives a bad screen; a colour change may not.

`outline` is the one for shooters — it reads over a moving starfield.

Lowercase (`0x60`–`0x7F`) isn't included. Add masks and raise `LAST`; still
free.

Edit the masks in `mkfont.py`, never the generated `.c`.

---

## Notes

- 2bpp tiles, so one glyph carries a body and a shadow at no extra cost.
- `PrintString()` works unchanged — same codes, different pixels.
- Check any new font at **1x** on the target background. Everything looks fine
  at 4x.
