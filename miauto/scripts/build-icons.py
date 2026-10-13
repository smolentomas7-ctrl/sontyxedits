#!/usr/bin/env python3
"""
Renders the PNG app icons from the mark in components/brand/Logo.tsx.

The paths are read out of the component rather than copied, so an icon can never
show a different mark from the header. They are pure move/line/close outlines,
which is why this needs nothing but Pillow: the disc is filled, then every
monogram outline is filled again in the background colour, which knocks it out.

Everything is drawn at 4x and downsampled, so the edges land where a vector
renderer would put them.

Run:  python3 scripts/build-icons.py
"""
import os
import re

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(ROOT, "components", "brand", "Logo.tsx")

ACCENT = "#FF7A3D"
INK = "#0B0D0E"
BOX = 64.0
SS = 4  # supersample


def read_path(name: str) -> str:
    source = open(LOGO, encoding="utf8").read()
    match = re.search(rf'export const {name} =\s*\n?\s*"([^"]+)"', source)
    if not match:
        raise SystemExit(f"{name} not found in {LOGO}")
    return match.group(1)


def polygons(d: str, scale: float, offset: float = 0.0):
    """Every subpath of an M/L/Z outline, as a list of scaled points."""
    out = []
    for chunk in d.split("M")[1:]:
        nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", chunk)]
        pts = [
            (x * scale + offset, y * scale + offset)
            for x, y in zip(nums[0::2], nums[1::2])
        ]
        if len(pts) >= 3:
            out.append(pts)
    return out


def icon(size: int, *, square: bool, inset: float) -> Image.Image:
    """`square` fills the canvas (iOS and Android mask it themselves)."""
    s = size * SS
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    if square:
        draw.rectangle((0, 0, s, s), fill=ACCENT)
    else:
        draw.ellipse((0, 0, s - 1, s - 1), fill=ACCENT)

    # The mark sits inside `inset` of the canvas, centred.
    span = s * (1 - 2 * inset)
    scale = span / BOX
    offset = s * inset

    if square:
        for poly in polygons(RING, scale, offset):
            draw.polygon(poly, fill=INK)
    for poly in polygons(GLYPH, scale, offset):
        draw.polygon(poly, fill=INK)

    return im.resize((size, size), Image.LANCZOS)


RING = read_path("MARK_RING")
GLYPH = read_path("MARK_GLYPH")

TARGETS = [
    # path, size, square, inset
    (os.path.join(ROOT, "app", "apple-icon.png"), 180, True, 0.14),
    (os.path.join(ROOT, "public", "icons", "icon-192.png"), 192, True, 0.14),
    (os.path.join(ROOT, "public", "icons", "icon-512.png"), 512, True, 0.14),
]

if __name__ == "__main__":
    for path, size, square, inset in TARGETS:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        icon(size, square=square, inset=inset).save(path, optimize=True)
        print(f"  {os.path.relpath(path, ROOT):<34} {size}x{size}  "
              f"{os.path.getsize(path) / 1024:.1f} KB")
