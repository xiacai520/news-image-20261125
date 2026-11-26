#!/usr/bin/env python3
"""World News in One Image - 25 November 2026.

Renders a 1024x1024 poster (entry.png) summing up six verified world-news
stories from 25 November 2026. Pure Python standard library only: the PNG
encoder (zlib + struct), the bitmap font and the layout engine are all
hand-written in this single file. No third-party packages, no network
access, no external assets. Running `python3 main.py` twice produces a
byte-identical entry.png.
"""

import hashlib
import os
import struct
import zlib

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 "0"/"1" characters.
# Designed from scratch for this poster: capitals, lowercase, digits and
# the punctuation the headlines need.
# ---------------------------------------------------------------------------

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
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
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "00010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01111", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
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
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "·": ("00000", "00000", "01100", "01100", "00000", "00000", "00000"),
}

GLYPH_W = 5
GLYPH_H = 7
ADVANCE = 6  # glyph width + 1px gap, in font units


def text_width(text, scale):
    """Pixel width of text at the given integer scale."""
    if not text:
        return 0
    return (len(text) * ADVANCE - 1) * scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap. Returns a list of lines that fit max_width px."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if text_width(trial, scale) <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Canvas: an RGB pixel buffer with rectangle and bitmap-text drawing.
# ---------------------------------------------------------------------------

class Canvas:
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, color)

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i] = color[0]
            self.pixels[i + 1] = color[1]
            self.pixels[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.width + x0) * 3
            self.pixels[i:i + len(row)] = row

    def draw_text(self, text, x, y, scale, color):
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT["?"])
            for gy in range(GLYPH_H):
                row = glyph[gy]
                for gx in range(GLYPH_W):
                    if row[gx] == "1":
                        self.fill_rect(
                            cx + gx * scale, y + gy * scale,
                            scale, scale, color,
                        )
            cx += ADVANCE * scale

    def draw_text_right(self, text, right_x, y, scale, color):
        self.draw_text(text, right_x - text_width(text, scale), y, scale, color)


# ---------------------------------------------------------------------------
# Minimal PNG writer: 8-bit RGB, filter 0 scanlines, zlib level 9.
# ---------------------------------------------------------------------------

def _chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png(path, canvas):
    width, height = canvas.width, canvas.height
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0 (None)
        start = y * width * 3
        raw += canvas.pixels[start:start + width * 3]
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )
    with open(path, "wb") as f:
        f.write(png)
    return png


# ---------------------------------------------------------------------------
# Content: six verified stories from 25 November 2026.
# ---------------------------------------------------------------------------

# Palette
BG = (13, 27, 46)        # deep navy page
PANEL = (22, 40, 63)     # card fill
PANEL_EDGE = (48, 76, 108)
WHITE = (236, 241, 246)
MUTED = (150, 166, 186)
BODY = (196, 206, 218)
RED = (214, 48, 49)
HEADER_RULE = (214, 48, 49)

NEWS = [
    {
        "tag": "MIDDLE EAST",
        "color": (214, 48, 49),
        "headline": "Houthi drone hits Riyadh's tallest tower",
        "summary": (
            "Second strike on the PIF Tower in a week wounds 11; "
            "the Saudi-led coalition hits back in Yemen."
        ),
        "source": "Al Jazeera / Reuters",
    },
    {
        "tag": "GAZA",
        "color": (230, 126, 34),
        "headline": "Israeli strike kills Hamas security chief",
        "summary": (
            "Mohammad Abuelouf dies with his wife and two children "
            "in Gaza City, a day after his chief."
        ),
        "source": "Reuters",
    },
    {
        "tag": "TRADE",
        "color": (52, 120, 200),
        "headline": "US proposes tariffs on 14 partners",
        "summary": (
            "Washington targets excess industrial capacity, with "
            "the highest rates aimed at China."
        ),
        "source": "Reuters",
    },
    {
        "tag": "COURTS",
        "color": (140, 90, 200),
        "headline": "US jury convicts Huawei of trade-secrets theft",
        "summary": (
            "Guilty on 10 of 12 counts, including bank fraud and "
            "sanctions violations; Huawei plans to appeal."
        ),
        "source": "Reuters",
    },
    {
        "tag": "MARKETS",
        "color": (46, 160, 90),
        "headline": "Asian stocks slide as AI rally fades",
        "summary": (
            "MSCI Asia-Pacific ex-Japan falls 2.3%; Seoul drops "
            "5.3% and Taiwan 5.1% as tariff fears return."
        ),
        "source": "Reuters",
    },
    {
        "tag": "TRAVEL",
        "color": (30, 160, 170),
        "headline": "O'Hare grounded again in Thanksgiving rush",
        "summary": (
            "A radar outage halts flights into Chicago for a "
            "second day; 373 flights delayed as a storm nears."
        ),
        "source": "Times Now / FAA",
    },
]

SIZE = 1024
MARGIN = 48
GUTTER_X = 24
GUTTER_Y = 20
CARD_W = (SIZE - 2 * MARGIN - GUTTER_X) // 2
CARD_H = 252
GRID_TOP = 170
HEADER_BOTTOM = 150


def render():
    c = Canvas(SIZE, SIZE, BG)

    # Top accent strip.
    c.fill_rect(0, 0, SIZE, 8, RED)

    # Header: masthead left, date right.
    c.draw_text("WORLD NEWS", MARGIN, 44, 6, WHITE)
    c.draw_text_right("25 NOVEMBER 2026", SIZE - MARGIN, 50, 3, WHITE)
    c.draw_text_right("SIX STORIES - ONE DAY", SIZE - MARGIN, 96, 2, MUTED)
    c.fill_rect(MARGIN, HEADER_BOTTOM, SIZE - 2 * MARGIN, 3, HEADER_RULE)

    # Six cards, two columns x three rows.
    for index, item in enumerate(NEWS):
        col = index % 2
        row = index // 2
        x = MARGIN + col * (CARD_W + GUTTER_X)
        y = GRID_TOP + row * (CARD_H + GUTTER_Y)
        draw_card(c, x, y, item)

    # Footer: sources line.
    footer = "Sources: Reuters, Al Jazeera, Times Now, FAA - 25 Nov 2026"
    c.draw_text(footer, MARGIN, 984, 2, MUTED)
    return c


def draw_card(c, x, y, item):
    color = item["color"]
    c.fill_rect(x, y, CARD_W, CARD_H, PANEL)
    # 1px edge + 6px accent bar on the left.
    c.fill_rect(x, y, CARD_W, 1, PANEL_EDGE)
    c.fill_rect(x, y + CARD_H - 1, CARD_W, 1, PANEL_EDGE)
    c.fill_rect(x, y, 6, CARD_H, color)

    inner_x = x + 24
    inner_w = CARD_W - 48

    # Category chip: filled rect, white label, vertically centred text.
    chip_w = text_width(item["tag"], 2) + 20
    chip_y = y + 18
    c.fill_rect(inner_x, chip_y, chip_w, 26, color)
    c.draw_text(item["tag"], inner_x + 10, chip_y + 6, 2, WHITE)

    # Headline, up to three wrapped lines. Roomier leading (22px) so the
    # two-line headlines breathe instead of crowding the card.
    head_lines = wrap_text(item["headline"], inner_w, 2)
    hy = y + 60
    for i, line in enumerate(head_lines[:3]):
        c.draw_text(line, inner_x, hy + i * 22, 2, WHITE)

    # Summary, up to three wrapped lines, below the headline.
    sum_lines = wrap_text(item["summary"], inner_w, 2)
    sy = hy + len(head_lines[:3]) * 22 + 14
    for i, line in enumerate(sum_lines[:3]):
        c.draw_text(line, inner_x, sy + i * 21, 2, BODY)

    # Divider rule, then the source line pinned near the card bottom.
    c.fill_rect(inner_x, y + CARD_H - 44, inner_w, 1, PANEL_EDGE)
    c.draw_text("Source: " + item["source"], inner_x, y + CARD_H - 30, 2, MUTED)


def main():
    canvas = render()
    out_path = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "."), "entry.png")
    png = write_png(out_path, canvas)
    digest = hashlib.sha256(png).hexdigest()
    print("entry.png: %dx%d, %d bytes" % (SIZE, SIZE, len(png)))
    print("sha256: %s" % digest)


if __name__ == "__main__":
    main()
