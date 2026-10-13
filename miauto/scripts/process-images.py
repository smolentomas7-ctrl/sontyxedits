#!/usr/bin/env python3
"""
One-off image pipeline for the M.I.Auto site.

Reads originals from assets-originals/, and for every slot:
  1. strips ALL metadata (phone photos carry GPS, device and capture time)
  2. redacts anything that would make a false claim or expose a customer
  3. crops to the slot's aspect ratio and resizes to the slot target
  4. writes WebP + AVIF + a JPEG fallback
  5. samples a dominant colour for the placeholder
and prints a before/after byte report.

Run:  python3 scripts/process-images.py
"""
import json, os, shutil, sys
from PIL import Image, ImageFilter, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets-originals")
OUT = os.path.join(ROOT, "public", "assets", "miauto")

# Every slot is emitted at three widths. The page picks one with `sizes`, so a
# card never ships the full-width file. Budgets below are per variant, not per slot.
VARIANTS = (
    ("full",  1.00, 76, 200),   # suffix, scale, quality, KB budget
    ("card",  0.50, 74,  80),
    ("thumb", 0.27, 70,  40),
)

# Provenance per slot, written into the manifest so the site can never describe
# a generic photograph as this workshop's own premises.
#   "own"   — photographed at M.I.Auto
#   "stock" — generic imagery, NOT their workshop
ORIGIN = {
    "hero": "own",
    "service-diagnostika": "stock",
    "service-cipovanie-ecu": "stock",
    "service-geometria": "stock",
    "service-pneuservis": "stock",
    "service-elektroinstalacia": "stock",
    "service-rozvody": "stock",
    "service-klimatizacia": "own",
    "about-interior": "own",
    "about-detail-01": "own",
    "about-detail-02": "own",
    "owner-01": "own",
    "owner-02": "own",
}

# Source-pixel crops applied before everything else, where framing alone solves a
# problem that retouching would only half-solve.
PRECROP = {
    # Owner portraits. Both arrive as phone shots with the subject low in the
    # frame; these boxes take a 4:5 portrait around each person. The second one
    # also arrives letterboxed (246px of black top and bottom), and the crop
    # starts below that black.
    #
    # The 4:5 target is 560x700 rather than anything larger on purpose: the
    # tighter of the two crops is 560px wide, and upscaling a face past its real
    # resolution looks worse than showing it smaller. Reshooting both portraits
    # on a camera, framed waist-up, is the one change that would lift them.
    "owner-01-marian.jpg": (330, 1120, 1010, 1970),
    "owner-02-ivan.jpg": (175, 1090, 735, 1790),

    # Reframes away from a "Volkswagen Service" fender cover in the background.
    # The VW Group electrics page states in both locales that this is an independent
    # workshop and NOT an authorised Volkswagen service centre, and a legible
    # factory-service cover would contradict the sentence directly above it.
    # Retouching the lettering left a visible patch; cropping is clean, and the
    # tighter frame is a better photograph.
    "elektro.jpg": (380, 160, 1200, 707),
}

# slot id -> (source file, target W, target H, crop anchor, quality)
# anchor: where to keep the subject when cropping to ratio (0 = top/left, .5 = centre, 1 = bottom/right)
SLOTS = {
    "hero":                         ("hero.jpg",        1920, 1080, 0.50, 82),
    "service-diagnostika":          ("diagnostika.jpg", 1200,  800, 0.50, 80),
    "service-cipovanie-ecu":        ("ecu.jpg",         1200,  800, 0.50, 80),
    "service-geometria":            ("geometria.jpg",   1200,  800, 0.50, 80),
    "service-pneuservis":           ("pneuservis.jpg",  1200,  800, 0.50, 80),
    # Targets below 1200x800 are deliberate: these originals are smaller than
    # that once cropped to ratio, and an upscale invents detail that was never
    # photographed. The handover report lists them as worth reshooting.
    "service-elektroinstalacia":    ("elektro.jpg",      816,  544, 0.50, 80),
    "service-rozvody":              ("rozvody.jpg",     1200,  800, 0.50, 80),
    "service-klimatizacia":         ("klimatizacia.jpg", 894,  596, 0.42, 80),
    "about-interior":               ("about-01.jpg",     896, 1120, 0.50, 80),
    "about-detail-01":              ("about-02.jpg",     894,  596, 0.45, 80),
    "about-detail-02":              ("about-03.jpg",     894,  596, 0.50, 80),

    # 1.2 — owner portraits, 4:5.
    "owner-01":                     ("owner-01-marian.jpg", 560, 700, 0.50, 84),
    "owner-02":                     ("owner-02-ivan.jpg",   560, 700, 0.50, 84),
}

# Redactions applied BEFORE crop, in source-pixel coordinates.
#   ("blur", x0, y0, x1, y1)   feathered gaussian, for detail that only needs softening
#   ("fill", x0, y0, x1, y1)   vertical inpaint from the rows above and below the box.
# A gaussian smears high-contrast lettering but leaves a readable low-frequency ghost,
# so anything that must be unreadable is filled, not blurred.
REDACT = {
    # Customer licence plate on the white Skoda. The other real photos arrived
    # with plates already blurred; this one did not.
    "hero.jpg":          [("blur", 1428, 762, 1532, 832)],
}

def strip_metadata(im: Image.Image) -> Image.Image:
    """Re-encode raw pixels into a clean container. Drops EXIF, GPS, ICC, XMP, IPTC."""
    rgb = im.convert("RGB")
    return Image.frombytes("RGB", rgb.size, rgb.tobytes())

def _fill(im: Image.Image, x0: int, y0: int, x1: int, y1: int,
          donor_dy: int = 0) -> None:
    """Rebuild a rectangle so the lettering under it is destroyed, not smeared.

    A gaussian leaves a readable low-frequency ghost, so instead:
      * low frequencies come from interpolating the rows above and below the box,
        which reproduces the gentle shading of the fabric;
      * high frequencies are grafted from a clean patch of the same fabric
        `donor_dy` pixels lower, so the repair keeps real weave and grain rather
        than reading as a flat rectangle.
    """
    import numpy as np

    w, h = x1 - x0, y1 - y0
    # Low frequency: interpolate the smoothed rows just outside the box.
    smooth = np.asarray(
        im.filter(ImageFilter.GaussianBlur(radius=7)), dtype=np.float32
    )
    above = smooth[max(0, y0 - 3), x0:x1]
    below = smooth[min(im.height - 1, y1 + 3), x0:x1]
    t = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
    base = above[None, :, :] * (1.0 - t) + below[None, :, :] * t

    # High frequency: clean fabric from elsewhere on the same cover.
    if donor_dy:
        dy0 = max(0, min(im.height - h, y0 + donor_dy))
        patch = np.asarray(im, dtype=np.float32)[dy0:dy0 + h, x0:x1]
        patch_lf = np.asarray(
            im.filter(ImageFilter.GaussianBlur(radius=7)), dtype=np.float32
        )[dy0:dy0 + h, x0:x1]
        base = base + (patch - patch_lf)

    out = np.asarray(im, dtype=np.float32)
    out[y0:y1, x0:x1] = np.clip(base, 0, 255)
    im.paste(Image.fromarray(out.astype("uint8"), "RGB"))
    # soften the patch and its seams so it matches the shot's depth of field
    pad = 14
    rx0, ry0 = max(0, x0 - pad), max(0, y0 - pad)
    rx1, ry1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
    region = im.crop((rx0, ry0, rx1, ry1))
    blurred = region.filter(ImageFilter.GaussianBlur(radius=9))
    mask = Image.new("L", region.size, 0)
    ImageDraw.Draw(mask).rectangle(
        (x0 - rx0 - 6, y0 - ry0 - 6, x1 - rx0 + 6, y1 - ry0 + 6), fill=255
    )
    mask = mask.filter(ImageFilter.GaussianBlur(radius=10))
    region.paste(blurred, (0, 0), mask)
    im.paste(region, (rx0, ry0))


def redact(im: Image.Image, boxes) -> Image.Image:
    for box in boxes:
        mode, x0, y0, x1, y1 = box[:5]
        if mode == "fill":
            _fill(im, x0, y0, x1, y1, donor_dy=box[5] if len(box) > 5 else 0)
            continue
        w, h = x1 - x0, y1 - y0
        pad = int(max(w, h) * 0.5)
        rx0, ry0 = max(0, x0 - pad), max(0, y0 - pad)
        rx1, ry1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
        region = im.crop((rx0, ry0, rx1, ry1))
        blurred = region.filter(ImageFilter.GaussianBlur(radius=max(w, h) / 3.0))
        mask = Image.new("L", region.size, 0)
        ImageDraw.Draw(mask).ellipse(
            (x0 - rx0, y0 - ry0, x1 - rx0, y1 - ry0), fill=255
        )
        mask = mask.filter(ImageFilter.GaussianBlur(radius=max(w, h) / 6.0))
        region.paste(blurred, (0, 0), mask)
        im.paste(region, (rx0, ry0))
    return im

def crop_to_ratio(im: Image.Image, tw: int, th: int, anchor: float) -> Image.Image:
    target = tw / th
    w, h = im.size
    if w / h > target:                      # too wide -> trim the sides
        nw = int(round(h * target))
        x = int((w - nw) * anchor)
        return im.crop((x, 0, x + nw, h))
    nh = int(round(w / target))             # too tall -> trim top/bottom
    y = int((h - nh) * anchor)
    return im.crop((0, y, w, y + nh))

def dominant(im: Image.Image) -> str:
    small = im.resize((1, 1), Image.LANCZOS)
    r, g, b = small.getpixel((0, 0))
    # darken slightly: the placeholder sits under a dark page, a bright flash is worse
    r, g, b = int(r * 0.72), int(g * 0.72), int(b * 0.72)
    return f"#{r:02X}{g:02X}{b:02X}"

def kb(path: str) -> float:
    return os.path.getsize(path) / 1024

def main() -> int:
    if not os.path.isdir(SRC):
        print(f"no originals at {SRC}", file=sys.stderr)
        return 1
    os.makedirs(OUT, exist_ok=True)
    manifest, before_total, after_total, rows = {}, 0.0, 0.0, []

    for slot, (fname, tw, th, anchor, q) in SLOTS.items():
        src = os.path.join(SRC, fname)
        if not os.path.exists(src):
            print(f"  SKIP {slot}: no {fname}")
            continue
        before = kb(src)
        before_total += before

        im = Image.open(src)
        im = strip_metadata(im)
        if fname in PRECROP:
            im = im.crop(PRECROP[fname])
        if fname in REDACT:
            im = redact(im, REDACT[fname])
        im = crop_to_ratio(im, tw, th, anchor)
        upscaled = im.width < tw
        im = im.resize((tw, th), Image.LANCZOS)

        colour = dominant(im)
        variants, after = {}, 0.0
        if upscaled:
            print(f"  WARNING {slot}: source is smaller than the target; "
                  f"shrink the target or reshoot rather than shipping an upscale")
        for vname, scale, vq, budget in VARIANTS:
            vw, vh = int(round(tw * scale)), int(round(th * scale))
            vim = im if scale == 1.0 else im.resize((vw, vh), Image.LANCZOS)
            suffix = "" if vname == "full" else f"-{vname}"
            sizes = {}
            for ext, kwargs in (
                ("webp", dict(quality=vq, method=6)),
                ("avif", dict(quality=max(vq - 12, 38))),
                ("jpg",  dict(quality=vq, optimize=True, progressive=True)),
            ):
                path = os.path.join(OUT, f"miauto-{slot}{suffix}.{ext}")
                vim.save(path, **kwargs)
                sizes[ext] = kb(path)
                after += kb(path)
            variants[vname] = {
                "width": vw, "height": vh, "budgetKB": budget,
                "bytes": {e: round(k * 1024) for e, k in sizes.items()},
            }
        after_total += after

        manifest[slot] = {
            "width": tw, "height": th, "placeholder": colour,
            "origin": ORIGIN.get(slot, "stock"),
            "upscaled": upscaled, "variants": variants,
        }
        rows.append((slot, before, after, variants, upscaled))
        best_full = min(variants["full"]["bytes"][e] for e in ("webp", "avif")) / 1024
        print(f"  {slot:<28} {before:7.0f} KB -> 3 sizes x 3 formats, "
              f"full {best_full:5.1f} KB"
              + ("   [upscaled]" if upscaled else ""))

    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    print("\n--- byte report ---")
    print(f"  originals, as supplied      {before_total:9.0f} KB  ({len(rows)} files)")
    print(f"  published, 3 sizes x 3 fmt  {after_total:9.0f} KB")
    for vname, _, _, _ in VARIANTS:
        for ext in ("webp", "avif"):
            tot = sum(v[vname]["bytes"][ext] for _, _, _, v, _ in rows) / 1024
            print(f"  what a visitor downloads: {vname:<5} {ext}  {tot:8.0f} KB"
                  f"   ({100 * tot / before_total:.1f}% of originals)")

    print("\n--- budget check, per variant (best of webp/avif) ---")
    over = 0
    for slot, _, _, variants, _ in rows:
        for vname, _, _, budget in VARIANTS:
            v = variants[vname]
            limit = 200 if (slot == "hero" and vname == "full") else budget
            best = min(v["bytes"]["webp"], v["bytes"]["avif"]) / 1024
            ok = best <= limit
            over += 0 if ok else 1
            print(f"  {'ok  ' if ok else 'OVER'} {slot}-{vname:<6} "
                  f"{v['width']}x{v['height']:<5} {best:6.1f} KB / {limit} KB")
    print(f"\n  {over} variant(s) over budget")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
