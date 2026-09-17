/* fontdump - dump the NGPC BIOS charset so we can stop guessing.
 *
 * Paints tile codes 0x00-0x8F in a 16-wide grid with a hex ruler, so one
 * screenshot tells us exactly which codes hold katakana and what the
 * official letterforms look like.  Worth keeping around: this answers the
 * same question for every future project, not just Pengu.
 *
 * OPTION toggles to the 0x90-0xFF range, which is where our own tiles live
 * once install_tiles() has run - here it just shows whatever the BIOS left
 * there, which is also useful to know.
 *
 * Build with the same Makefile, pointed at probe/ instead of src/.
 */
#define CARTHDR_IMPL
#include "carthdr.h"
#include "ngpc.h"
#include "library.h"

void main(void);
static void draw_page(u8 page);

static void draw_page(u8 page) {
    u8 r, c, base;

    FillScreen(SCR_1_PLANE, ' ', 0);

    /* column ruler across the top */
    PrintString(SCR_1_PLANE, 0, 0, 0, "   0123456789ABCDEF");

    base = 0;
    if (page) base = 0x90;

    for (r = 0; r < 9; r++) {
        u8 hi;
        hi = base + (r << 4);
        if (page && r >= 7) break;          /* 0x90..0xFF is seven rows */
        PrintHex(SCR_1_PLANE, 0, 0, r + 1, hi, 2);
        for (c = 0; c < 16; c++)
            PutTile(SCR_1_PLANE, 0, c + 3, r + 1, hi + c);
    }

    PrintString(SCR_1_PLANE, 0, 0, 11, "OPTION = NEXT PAGE");
    if (page) PrintString(SCR_1_PLANE, 0, 0, 12, "PAGE 2  0x90-0xFF");
    else      PrintString(SCR_1_PLANE, 0, 0, 12, "PAGE 1  0x00-0x8F");
}

void main(void) {
    u8 page, cur, prev, press;

    InitNGPC();

    /* plain white on black - this is a diagnostic, not a game */
    SetBackgroundColour(RGB(0, 0, 0));
    SetPalette(SCR_1_PLANE, 0, 0, RGB(15, 15, 15), RGB(8, 8, 8), RGB(4, 4, 4));

    SysSetSystemFont();

    page  = 0;
    cur   = 0;
    prev  = 0;
    draw_page(page);

    for (;;) {
        WaitVsync();
        prev  = cur;
        cur   = JOYPAD & 0x7F;
        press = cur & ~prev;
        if (press & J_OPTION) {
            if (page) page = 0;
            else      page = 1;
            draw_page(page);
        }
    }
}
