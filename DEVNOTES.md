# Pengu — development notes

Build-level detail. Player-facing README is [README.md](README.md).

Pengo homage. Single screen, 10x9 cells of 16px, four fields, one tile set
retinted four ways. CartID 0x0054, cart title "PENGU       ".

## Controls
- **D-pad** walk. Walking into a block pushes it; it slides until it hits
  something. The penguin stays put, arcade style.
- **A** breaks a block. It only works on a block that is **jammed** - one
  with something solid directly behind it, either another block or the outer
  wall. A block with room to move gets pushed, not broken. Hold the D-pad
  toward the block and press A, or just press A to break whatever you're
  currently facing. Diamonds never break.
- Facing the outer wall instead, A punches the wall: any Sno-Bee against that
  wall is stunned, walk over it to finish it.
- **OPTION** pause. On the title screen, OPTION shows the score table.

## Three ways to kill a Sno-Bee
1. Slide a block into it. Multi-kills pay 400 / 1600 / 3200.
2. Crush its egg block before it hatches (500).
3. Stun it against a wall, then walk over it (100).

Clear every Sno-Bee **and** every egg to take the round.

## Levels
Four fields in `src/maps.h`, then they wrap. One tile set, four palette
themes - level 3 is the desert island purely by recolour, same ice tiles as
sand. Sno-Bees recolour per round (green/red/yellow/pink), which is what the
arcade does.

Sudden death at 60 seconds: Sno-Bees move at penguin speed and eggs hatch
twice as fast. The stage marker flashes.

## Build
Drop `src/` into a tree with your universal `Makefile`, `toolchain.mk`,
`lcf/` and `common/`.

**Link order check:** if the Makefile globs `src/*.c`, the sort order is now
entities, game, kana, main, save, screen, snobee, sound, tiles - so main.c is
4th, not 1st. Asteroids had main.c 3rd under the same glob and builds fine, so
this is probably handled, but it's the first thing to check if the cart
doesn't boot. The Sno-Bee module is named `snobee.c` rather than `bees.c`
specifically so it sorts AFTER main.c instead of leading the link.

`fontdump/` is a separate project with its own `src/`, so the same Makefile
builds it unmodified. CartID 0x0053.

## Tools
- `python3 tools/mkart.py` - regenerate tiles from the ASCII art
- `python3 tools/checkmaps.py` - validate fields (reachability, slide
  quality, sealed-egg pockets). Run this after editing any map.
- `python3 tools/checksound.py` - audit sound.c against the verified NGPC
  sound rules. Run after any sound edit.
- `tools/test_crush.c` - regression test for the crush rules (facing,
  jammed-only, diamonds, and the stale-direction bug). Build the same way as
  sim.c but with `tools/test_crush.c`.
- `tools/sim.c` - host harness. Compiles the real game.c/entities.c/bees.c/
  screen.c against stubbed library calls and asserts invariants over
  thousands of frames:
  `gcc -std=gnu90 -D__interrupt= -Isrc -o sim tools/sim.c src/game.c src/entities.c src/snobee.c src/screen.c`

## fontdump/ - BIOS charset dump
Standalone project. Paints tile codes 0x00-0x8F in a 16-wide grid with a hex
ruler; OPTION pages to 0x90-0xFF. Screenshot it once and we know the BIOS
letterforms for good - useful for every future project, not just Pengu.

## Tiles
144-241, 98 used, 14 spare. All IDs <= 255. Egg blocks, stunned Sno-Bees and
all four level themes cost **zero** tiles - they're palette work.

## Palette / plane architecture
**Settled on hardware:** scroll-plane index 0 is TRANSPARENT to the
background register, not opaque. Blue Print's black field had hidden this.
The code still paints defensively in indices 1-3 (harmless, and it means the
field colour is guaranteed rather than inherited), but the sprite-based
banners and the gem's opaque surround are belt-and-braces rather than
necessities.

The consequence that matters: an 8x8 tile stamped over existing art ERASES
it wherever the new tile is index 0. That's what clipped the border blocks in
v1 - the wall was an overlay. The frame is now part of the empty-cell fill
(`frame_tile()`), so nothing overwrites anything.

Plane 1: playfield, wall, HUD. Plane 2: unused.
Sprites: penguin (pal 0), block in flight + shatter + stunned bees (pal 1),
Sno-Bees (pal 2), overlay kana (pal 3). Slots 0-3 only.

Consequence: kana over the playfield must be sprites, or every glyph carries
a black box. Pause and the banners do it that way.

## Flash save
Adapted from Blue Print's working save.c. Layout: 0xCAFEBABE at words 0-1
(library sentinel - the magic MUST be there, a game magic at word 0 silently
prevents saves), game magic 'PG' at word 2, version at 3, five scores at 4-8,
checksum at 127. The library's Flash()/GetSavedData() own the actual ROM
offset; this code does not set it.

**Unverified on hardware:** whether the score survives a power cycle. If it
saves within a session but not across power-off, that's the rbc3 write-size
issue and it needs a custom routine.

## Sound compliance
`sound.c` is audited by `tools/checksound.py` - run it after ANY edit there.
The rules it enforces are verified, not inferred:
- **No WaitVsync between InstallSoundDriver() and InstallSounds().** An
  earlier note of mine claimed two were needed as a Z80 boot-race guard. That
  is wrong for this driver and yields *no sound at all*. v1-v4 of Pengu were
  silent for exactly this reason.
- `sound_init()` after graphics setup.
- Never call `StopAllSounds()` - declared in library.h, not exported by
  system.lib, fails at tulink. gnu90 preflight cannot see it.
- Every effect must decay to volume 0 within its Length. No hardware
  envelope; a channel holds its last level forever and hisses. All 11 rows
  satisfy `ceil(InitialVol/VolStep) * VolSpeed <= Length` with
  VolLowerLimit 0.
- ToneStep must be non-zero or the tone register is never written and the
  channel plays static.
- Channels 1 and 2 only. Channel 3 is noise - leave it silent.
- `PlaySound(n)` is 1-based, so `SND_*` run 1..11.

No music. NeoTracker is the BGM path and links, but authoring a module needs
NeoTracker.exe; deferred.
