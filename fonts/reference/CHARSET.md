# The NGPC BIOS charset — what's actually in there

Established by dumping a real unit with `fontdump`. Screenshots in this
directory; masks in `bios-full.py` and `bios-katakana.py`, both produced by
`fontgen/rip.py`.

## Layout

| codes | contents | tiles |
|---|---|---|
| `0x00`–`0x1F` | symbols and box-drawing | 32 |
| `0x20`–`0x7F` | ASCII | 96 |
| `0x80`–`0xA0` | symbols | 33 |
| `0xA1`–`0xDF` | **half-width katakana (JIS X 0201)** | 63 |
| `0xE0`–`0xFF` | symbols | 32 |

**249 of 256 tiles are non-blank.** Only seven codes are genuinely empty:
`0x00`, `0x01`, `0x07`, `0x20`, `0x7F`, `0x80`, `0xA0`.

## Two things this changes

**1. The katakana are already there, correctly drawn.**
`0xA1`–`0xDF`, standard JIS X 0201 order. There is no reason to hand-draw
Japanese glyphs — hand-reconstructed 8x8 kana come out plausible-looking and
wrong, because the strokes don't survive the resolution. Rip them instead.

**2. Dakuten is a SEPARATE CELL.**
`0xDE` = ゛, `0xDF` = ゜. So グ is ク + ゛ across two cells, not one composite
glyph. This is why cramming a diacritic into a 7x7 cell alongside a base glyph
never looks right — the hardware doesn't do it that way.

The cost is width: ゲームオーバー becomes ケ゛ームオーハ゛ー, nine cells
instead of seven. Budget for it in HUD and banner layouts, or draw composites
and accept they'll be tight.

## The 144+ convention is based on a wrong assumption

Projects here install custom tiles at 144–255 on the belief that the font
occupies 0–143. It doesn't — it runs to `0xFF`. **144–255 is `0x90`–`0xFF`,
which sits directly on the katakana block.**

So it's a choice, not a coexistence: BIOS kana, *or* custom art at 144+.
This is also the mechanism behind "Japanese font bleed" — art installed at
144+ partially overwrites kana, and whatever survives shows through.

Keeping both ASCII and kana leaves custom art these gaps:

```
0x00-0x1F   32 tiles
0x80-0xA0   33 tiles
0xE0-0xFF   32 tiles
            97 usable, in three non-contiguous ranges
```

Workable, but the `T_` offsets and `install_tiles()` get messier. Worth it
only if a project actually needs Japanese text.

## Install order

```c
SysSetSystemFont();   /* BIOS charset into tile RAM, BOTH BG planes */
install_font();       /* optional: overwrite ASCII with your own    */
install_tiles();      /* your art — mind the overlap above          */
```
