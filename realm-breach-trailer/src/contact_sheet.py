"""Tile rendered images into a labelled contact sheet (Cinzel labels).

python3 src/contact_sheet.py OUT.png COLS "label|path" "label|path" ...
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "assets", "fonts", "Cinzel.ttf")


def sheet(out, cols, items, tile_w=360, title=None):
    ims = []
    for label, path in items:
        im = Image.open(path).convert("RGB")
        h = int(im.height * tile_w / im.width)
        ims.append((label, im.resize((tile_w, h), Image.LANCZOS)))
    th = max(im.height for _, im in ims)
    pad, lab = 10, 34
    top = 60 if title else 0
    rows = (len(ims) + cols - 1) // cols
    W = cols * (tile_w + pad) + pad
    H = top + rows * (th + lab + pad) + pad
    S = Image.new("RGB", (W, H), (11, 20, 24))
    d = ImageDraw.Draw(S)
    f = ImageFont.truetype(FONT, 20)
    if title:
        ft = ImageFont.truetype(FONT, 30)
        d.text((pad + 4, 14), title, font=ft, fill=(237, 230, 218))
    for k, (label, im) in enumerate(ims):
        r, c = divmod(k, cols)
        x = pad + c * (tile_w + pad)
        y = top + pad + r * (th + lab + pad)
        S.paste(im, (x, y + lab))
        d.text((x + 2, y + 6), label, font=f, fill=(255, 150, 90))
    S.save(out)
    print("wrote", out, S.size)


if __name__ == "__main__":
    out, cols = sys.argv[1], int(sys.argv[2])
    title = None
    items = []
    for a in sys.argv[3:]:
        if a.startswith("title="):
            title = a[6:]
            continue
        l, p = a.split("|", 1)
        items.append((l, p))
    sheet(out, cols, items, title=title)
