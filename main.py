#!/usr/bin/env python3
"""make.fun entry for news-image-20261123.

Draws a 1024x1024 newspaper front page that sums up the world news of
Monday 23 November 2026 and writes it to /output/entry.png (or to the
folder named by MAKEFUN_OUTPUT_DIR when that variable is set).

Pure Python 3.13 standard library: no Pillow, no network, no system
fonts. The PNG is encoded by hand with zlib and struct, and every
letter is drawn from the embedded 5x7 bitmap font below, so the same
bytes come out on every run, in any bare sandbox.
"""

import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, seven rows of five pixels, top row first.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01111", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
}

# ------------------------------------------------------------- colours
PAPER = (247, 242, 231)
INK = (18, 18, 18)
WHITE = (255, 255, 255)
RED = (186, 28, 28)
NAVY = (16, 42, 86)
GOLD = (238, 178, 32)
TEAL = (0, 108, 96)
GREEN = (28, 110, 52)
GREY = (92, 92, 92)
SKY = (120, 178, 224)
SEA = (24, 84, 140)
ORANGE = (244, 120, 24)
LIGHT = (226, 232, 240)


class Canvas:
    """A flat RGB pixel buffer with rectangle and bitmap-text drawing."""

    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.px = bytearray(colour) * (width * height)

    def set_px(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale if text else 0

    def draw_text(self, x, y, text, scale, colour):
        cx = x
        for ch in text.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == "1":
                        self.rect(cx + col_i * scale, y + row_i * scale,
                                  scale, scale, colour)
            cx += 6 * scale
        return cx - scale

    def draw_text_centered(self, cx, y, text, scale, colour):
        x = cx - self.text_width(text, scale) // 2
        return self.draw_text(x, y, text, scale, colour)

    def wrap(self, text, scale, max_width):
        max_chars = max(1, max_width // (6 * scale))
        lines, cur = [], ""
        for word in text.split():
            trial = word if not cur else cur + " " + word
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def draw_wrapped(self, x, y, text, scale, colour, max_width, leading):
        yy = y
        for line in self.wrap(text, scale, max_width):
            self.draw_text(x, yy, line, scale, colour)
            yy += leading
        return yy


def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def encode_png(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        start = yy * stride
        raw.extend(canvas.px[start:start + stride])
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# -------------------------------------------------------------- drawing
def draw_ship(c, x, y, w, h):
    """Simple pixel-art warship with an explosion, inside a sea panel."""
    c.rect(x, y, w, h, NAVY)
    c.rect(x, y + h - 46, w, 46, SEA)
    # waves
    for wx in range(x + 10, x + w - 20, 42):
        c.rect(wx, y + h - 34, 22, 4, SKY)
        c.rect(wx + 18, y + h - 20, 22, 4, SKY)
    # hull and superstructure
    hx, hy = x + 34, y + h - 96
    c.rect(hx, hy, w - 90, 26, LIGHT)
    c.rect(hx + 12, hy + 26, w - 114, 10, GREY)
    c.rect(hx + 52, hy - 30, 62, 30, LIGHT)
    c.rect(hx + 66, hy - 52, 10, 22, LIGHT)
    c.rect(hx + 130, hy - 18, 44, 18, LIGHT)
    c.rect(hx + 20, hy + 4, w - 130, 4, RED)
    # explosion star over the stern
    ex, ey = hx + w - 150, hy - 64
    c.rect(ex, ey, 44, 44, ORANGE)
    c.rect(ex - 14, ey + 14, 72, 16, GOLD)
    c.rect(ex + 14, ey - 14, 16, 72, GOLD)
    c.rect(ex + 8, ey + 8, 28, 28, RED)
    # incoming sea drones
    for dx, dy in ((18, 66), (64, 92)):
        c.rect(x + dx, y + h - dy, 30, 8, GOLD)
        c.rect(x + dx + 30, y + h - dy + 2, 8, 4, ORANGE)


def story_cell(c, x, y, w, kicker, kicker_colour, headline, body):
    c.rect(x, y, w, 8, kicker_colour)
    c.draw_text(x, y + 16, kicker, 2, kicker_colour)
    yy = c.draw_wrapped(x, y + 38, headline, 3, INK, w, 28)
    c.draw_wrapped(x, yy + 4, body, 2, GREY, w, 18)


def build_image():
    c = Canvas(WIDTH, HEIGHT, PAPER)

    # Masthead
    c.rect(0, 0, WIDTH, 128, INK)
    c.rect(0, 128, WIDTH, 8, RED)
    c.draw_text_centered(512, 18, "THE WORLD IN ONE DAY", 6, WHITE)
    c.draw_text_centered(512, 76, "MONDAY 23 NOVEMBER 2026", 3, GOLD)

    # Lead story
    lx, ly = 36, 152
    c.rect(lx, ly, 196, 30, RED)
    c.draw_text(lx + 10, ly + 8, "LEAD STORY", 2, WHITE)
    c.draw_text(lx + 220, ly + 8, "WAR AT SEA - LIBYA", 2, RED)
    lead_head = "UKRAINE SEA DRONES SINK RUSSIAN CORVETTE IN LIBYA"
    yy = c.draw_wrapped(lx, ly + 42, lead_head, 5, INK, 580, 48)
    lead_body = (
        "PRESIDENT ZELENSKYY SAID SEVEN UKRAINIAN-MADE NAVAL DRONES "
        "SANK THE CORVETTE MERKURY AT BENGHAZI AND HIT CARGO SHIP "
        "MV ANGARA. A KA-27 HELICOPTER ABOARD WAS ALSO DESTROYED."
    )
    c.draw_wrapped(lx, yy + 8, lead_body, 2, GREY, 580, 20)
    draw_ship(c, 648, 194, 340, 206)
    c.draw_text(648, 408, "MERKURY - BENGHAZI", 2, NAVY)
    c.rect(36, 444, 952, 3, INK)

    # Four-story grid
    gx, gy, gw, gap = 36, 460, 460, 32
    story_cell(
        c, gx, gy, gw, "CLIMATE - ANTALYA", RED,
        "COP31 ENDS WITH NO DEAL ON FOSSIL FUELS",
        "TALKS COLLAPSED AS THE EU AND OTHERS REJECTED A DRAFT "
        "THAT NEVER MENTIONED FOSSIL FUELS.",
    )
    story_cell(
        c, gx + gw + gap, gy, gw, "UKRAINE - DYMER", NAVY,
        "DYMER TOLL RISES TO 11 AS RESCUERS SEARCH",
        "RESCUERS PULLED A 79-YEAR-OLD WOMAN ALIVE AFTER 22 "
        "HOURS IN THE RUBBLE. A BOY OF 7 WAS SAVED.",
    )
    gy2 = gy + 162
    story_cell(
        c, gx, gy2, gw, "WASHINGTON", TEAL,
        "DEMOCRATS WIN 258 HOUSE SEATS, MOST SINCE 1992",
        "CHUCK HUBBARD BEAT VIRGINIA FOXX IN NORTH CAROLINA "
        "FOR A NET GAIN OF 44 SEATS.",
    )
    story_cell(
        c, gx + gw + gap, gy2, gw, "FOOTBALL - FIFA", GREEN,
        "FIFA NAMES 2031 AND 2035 WOMENS WORLD CUP HOSTS",
        "2031: USA, MEXICO, COSTA RICA AND JAMAICA, FIRST "
        "WITH 48 TEAMS. UK HOME NATIONS HOST 2035.",
    )
    c.rect(36, 788, 952, 3, INK)

    # Bottom band: markets and AI safety
    bx, by = 36, 804
    c.draw_text(bx, by, "MARKETS - SEOUL", 2, RED)
    c.draw_text(bx, by + 22, "-3.31%", 5, RED)
    c.draw_wrapped(
        bx, by + 66,
        "KOSPI TUMBLES AS THE AI SELL-OFF HITS SAMSUNG "
        "AND SK HYNIX. US FUTURES REBOUNDED.",
        2, GREY, 452, 18,
    )
    mx = 540
    c.rect(mx - 22, by, 3, 118, INK)
    c.draw_text(mx, by, "AI SAFETY - BARBADOS", 2, TEAL)
    yy = c.draw_wrapped(mx, by + 22, "UN CHIEF SEEKS GLOBAL AI SAFETY RULES",
                        3, INK, 448, 28)
    c.draw_wrapped(
        mx, yy + 4,
        "GUTERRES CALLED FOR TALKS ON A MULTILATERAL AI "
        "RISK FRAMEWORK AT BRIDGETOWN.",
        2, GREY, 448, 18,
    )
    c.rect(36, 948, 952, 3, INK)

    # Footer sport ticker
    c.rect(0, 958, WIDTH, 66, INK)
    c.draw_text_centered(
        512, 970,
        "SPORT - ALCARAZ BEATS ZVEREV 6-2 7-6 TO WIN FIRST ATP FINALS TITLE",
        2, GOLD,
    )
    c.draw_text_centered(
        512, 994, "SOURCES: REUTERS - AP - CNN - UN NEWS - FIFA", 2, WHITE,
    )
    return encode_png(c)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    data = build_image()
    dest = os.path.join(out_dir, "entry.png")
    with open(dest, "wb") as fh:
        fh.write(data)
    print(f"wrote {dest} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
