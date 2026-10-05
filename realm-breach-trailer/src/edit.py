"""STEP 11 (picture) — Edit, grade, titles, subtitles, mux.

python3 src/edit.py --mode animatic|preview|final [--safe] [--frames A B] [--out path]

Per video frame:
  source  : the shot covering the frame (scene frame == video frame). Sources by mode:
            final -> build/shots/<id>/final, preview -> build/shots/<id>/preview,
            fallbacks: preview renders, then the shot's key still (with a slow push), then a slate.
            M509 is a quarter-beat strobe built from M502-M508.
  effects : punch-in zoom (ease-out), seeded camera shake decaying over 6 frames on impacts,
            white flash frames (D, phase changes, the ultimate), Phase-3 desaturation.
  grade   : lifted blacks, filmic S-curve, teal shadows / ember highlights split-tone,
            act-specific balance (cold Phase 1, desaturated Phase 3, warm heaven), light
            vignette, seeded film grain (constant strength).
  overlays: FLOOR numbers (slam with overshoot), subtitles (word groups, synced), title + tagline,
            all inside the TikTok safe zone.
Frames are piped straight into ffmpeg and muxed with build/audio/mix.wav.
"""
import argparse
import json
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "config"))
import video  # noqa: E402

FPS = video.FPS
FONT = os.path.join(ROOT, "assets", "fonts", "Cinzel.ttf")
OFFWHITE = (237, 230, 218)
EMBER = (255, 106, 26)


# ------------------------------------------------------------------ text
def font(size, weight=600):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def text_layer(text, size, tracking=0.18, weight=600, color=OFFWHITE, glow=EMBER, glow_radius=None,
               glow_alpha=0.55, shadow=True):
    """RGBA image of tracked text with an ember glow and a soft dark shadow."""
    f = font(size, weight)
    adv = []
    for ch in text:
        adv.append(f.getlength(ch) + (size * tracking if ch != " " else size * tracking * 0.6))
    w = int(sum(adv) - size * tracking + size)
    h = int(size * 1.6)
    pad = int(size * 0.8)
    base = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    d = ImageDraw.Draw(base)
    x = pad + size * 0.5
    for ch, a in zip(text, adv):
        d.text((x, pad + size * 0.1), ch, font=f, fill=255)
        x += a
    bbox = base.getbbox() or (0, 0, base.width, base.height)
    out = Image.new("RGBA", base.size, (0, 0, 0, 0))
    if shadow:
        sh = base.filter(ImageFilter.GaussianBlur(size * 0.12))
        sh_rgba = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sh_rgba.putalpha(sh.point(lambda v: int(v * 0.85)))
        out = Image.alpha_composite(out, sh_rgba)
    if glow is not None:
        gr = glow_radius or size * 0.35
        gl = base.filter(ImageFilter.GaussianBlur(gr))
        g_rgba = Image.new("RGBA", base.size, glow + (0,))
        g_rgba.putalpha(gl.point(lambda v: int(min(255, v * glow_alpha * 1.6))))
        out = Image.alpha_composite(out, g_rgba)
    t_rgba = Image.new("RGBA", base.size, color + (0,))
    t_rgba.putalpha(base)
    out = Image.alpha_composite(out, t_rgba)
    cx = (bbox[0] + bbox[2]) / 2
    cy = (bbox[1] + bbox[3]) / 2
    return out, (cx, cy), bbox[2] - bbox[0]


_text_cache = {}


def cached_text(key, *a, **k):
    if key not in _text_cache:
        _text_cache[key] = text_layer(*a, **k)
    return _text_cache[key]


def paste(frame, layer, center, scale=1.0, alpha=1.0, max_w=None):
    """Alpha-composite an RGBA PIL layer onto an HxWx3 float frame (0..1) at a pixel centre.
    max_w: shrink so the visible text never exceeds this many pixels."""
    img, (cx, cy), tw = layer
    if max_w and tw * scale > max_w:
        scale = max_w / tw
    if scale != 1.0:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.LANCZOS)
        cx, cy = cx * scale, cy * scale
    a = np.asarray(img).astype(np.float32) / 255.0
    H, W = frame.shape[:2]
    x0 = int(round(center[0] - cx))
    y0 = int(round(center[1] - cy))
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(W, x0 + a.shape[1]), min(H, y0 + a.shape[0])
    if xb <= xa or yb <= ya:
        return
    sub = a[ya - y0:yb - y0, xa - x0:xb - x0]
    al = sub[..., 3:4] * alpha
    frame[ya:yb, xa:xb] = frame[ya:yb, xa:xb] * (1 - al) + sub[..., :3] * al


# ------------------------------------------------------------------ grade
def srgb_curve(x, contrast=1.18, pivot=0.42):
    """Filmic S-curve around a pivot (operates on display-referred 0..1)."""
    y = np.where(x < pivot,
                 pivot * (x / pivot) ** contrast,
                 1 - (1 - pivot) * ((1 - x) / (1 - pivot)) ** contrast)
    return y


def grade(img, look, H, W, vignette_map):
    """img: float32 HxWx3 0..1 (display-referred)."""
    lum = img[..., 0] * 0.2126 + img[..., 1] * 0.7152 + img[..., 2] * 0.0722
    sat = look.get("sat", 1.0)
    if sat != 1.0:
        img = lum[..., None] + (img - lum[..., None]) * sat
    # split tone: teal shadows, warm (ember) highlights
    sh = np.clip(1 - lum / 0.35, 0, 1)[..., None] ** 1.5
    hi = np.clip((lum - 0.45) / 0.55, 0, 1)[..., None]
    teal = np.array(look.get("shadow_tint", (-0.010, 0.006, 0.012)), np.float32)
    warm = np.array(look.get("high_tint", (0.035, 0.008, -0.03)), np.float32)
    img = img + sh * teal + hi * warm
    bp = look.get("black", 0.0)      # black point: pulls haze-lifted blacks back down (legend dungeon)
    if bp:
        img = (img - bp) / (1.0 - bp)
    img = srgb_curve(np.clip(img, 0, 1), look.get("contrast", 1.15))
    lift = look.get("lift", 0.012)
    img = img * (1 - lift) + lift * np.array(look.get("lift_color", (0.55, 0.85, 1.0)), np.float32)
    img *= look.get("gain", 1.0)
    img = img * vignette_map[..., None]
    return img


LOOKS = {
    "dark": dict(),                                           # acts I-III, V
    "phase1": dict(sat=0.82, shadow_tint=(-0.012, 0.004, 0.016), high_tint=(0.0, 0.004, 0.012)),
    "phase2": dict(sat=0.9),
    "phase3": dict(sat=0.65, gain=0.9, contrast=1.2),
    "phase4": dict(sat=1.05, high_tint=(0.045, 0.02, -0.03), black=0.07, contrast=1.22),
    "phase5": dict(sat=1.0, high_tint=(0.045, 0.015, -0.03), black=0.07, contrast=1.22),
    "heaven": dict(sat=0.95, shadow_tint=(0.01, 0.008, 0.0), high_tint=(0.02, 0.012, -0.005), lift=0.03,
                   lift_color=(1.0, 0.95, 0.85), contrast=1.05),
    "white": dict(),
}


def look_for(shot):
    sid = shot["id"]
    if shot.get("phase"):
        return "phase%d" % shot["phase"]
    if sid in ("E3", "E4"):
        return "heaven"
    return "dark"


# ------------------------------------------------------------------ sources
class Sources:
    def __init__(self, mode, W, H):
        self.mode, self.W, self.H = mode, W, H
        self.cache = {}

    def _read(self, path):
        im = cv2.imread(path, cv2.IMREAD_COLOR)
        if im is None:
            return None
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        if im.shape[1] != self.W or im.shape[0] != self.H:
            im = cv2.resize(im, (self.W, self.H), interpolation=cv2.INTER_AREA if im.shape[1] > self.W else cv2.INTER_CUBIC)
        return im.astype(np.float32) / 255.0

    def frame(self, shot, f):
        sid = shot["id"]
        order = {"final": ["final", "preview"], "preview": ["preview"], "animatic": ["preview"]}[self.mode]
        for m in order:
            p = os.path.join(ROOT, "build", "shots", sid, m, "f_%04d.png" % f)
            if os.path.exists(p):
                return self._read(p), "render"
        # fall back to a key still, held with a slow push
        sd = os.path.join(ROOT, "build", "stills", sid)
        if os.path.isdir(sd):
            fs = sorted(x for x in os.listdir(sd) if x.endswith(".png"))
            if fs:
                key = ("still", sid)
                if key not in self.cache:
                    self.cache[key] = self._read(os.path.join(sd, fs[0]))
                return self.cache[key], "still"
        return None, "slate"


def slate(shot, W, H):
    img = np.zeros((H, W, 3), np.float32)
    img[:] = np.linspace(0.02, 0.06, H)[:, None, None]
    return img


# ------------------------------------------------------------------ effects
def zoom_shift(img, scale, dx, dy):
    if abs(scale - 1) < 1e-4 and abs(dx) < 0.01 and abs(dy) < 0.01:
        return img
    H, W = img.shape[:2]
    M = np.float32([[scale, 0, (1 - scale) * W / 2 + dx], [0, scale, (1 - scale) * H / 2 + dy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def shake_offset(f, impacts, W, seed):
    dx = dy = 0.0
    for fi, amp in impacts:
        k = f - fi
        if 0 <= k <= 6:
            r = np.random.default_rng(seed * 1000 + fi * 7 + k)
            fall = (1 - k / 6.0) ** 2
            dx += r.uniform(-1, 1) * amp * W * fall
            dy += r.uniform(-1, 1) * amp * W * fall
    return dx, dy


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def overshoot(x, s=2.2):
    x = min(1.0, max(0.0, x))
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="animatic", choices=["animatic", "preview", "final"])
    ap.add_argument("--safe", action="store_true", help="draw TikTok safe-zone guides")
    ap.add_argument("--frames", nargs=2, type=int)
    ap.add_argument("--out")
    ap.add_argument("--stills", help="write these comma-separated frames as PNGs instead of a video")
    a = ap.parse_args()

    tl = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
    tm = json.load(open(os.path.join(ROOT, "config", "timing.json")))
    subs = json.load(open(os.path.join(ROOT, "edit", "subtitles.json")))
    shots = tl["shots"]
    byid = {s["id"]: s for s in shots}
    total = tl["total_frames"]
    full = a.mode == "final"
    W, H = (video.WIDTH, video.HEIGHT) if full else (video.WIDTH // 2, video.HEIGHT // 2)
    k = W / video.WIDTH                                      # pixel scale vs 1080 wide
    src = Sources(a.mode, W, H)
    band_cx = (video.SAFE_LEFT + (video.WIDTH - video.SAFE_RIGHT)) / 2 * k     # centre of the usable band
    band_w = (video.WIDTH - video.SAFE_LEFT - video.SAFE_RIGHT - 40) * k        # usable text width

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r2 = ((xx - W / 2) / (W / 2)) ** 2 * 0.8 + ((yy - H / 2) / (H / 2)) ** 2 * 0.6
    vig = np.clip(1 - 0.22 * r2 ** 1.3, 0, 1).astype(np.float32)

    def bf(b):
        return int(round((tm["song_grid_t0"] + b * tm["beat_sec"] - tm["song_offset"]) * FPS)) - 1

    # flashes: (frame, frames, strength)
    flashes = [(bf(48), 2, 1.0), (bf(128), 3, 1.0)]
    for b in (50, 56, 64, 72, 80, 88):
        flashes.append((bf(b), 1, 0.55))
    flashes.append((byid["M406"]["start_frame"] + 4, 2, 0.9))
    # impacts for shake: (frame, amplitude as fraction of width)
    impacts = [(bf(48), 0.018), (bf(128), 0.02), (bf(8), 0.004), (bf(16), 0.006), (bf(88), 0.01), (bf(90.35), 0.01),
               (bf(98), 0.012), (bf(99.6), 0.016), (bf(64.15), 0.008), (bf(78), 0.012)]
    for b in (62, 62.5, 63, 63.5, 80, 80.5, 81, 81.5, 82, 82.5, 83, 83.5):
        impacts.append((bf(b), 0.006))
    strobe_src = ["M502", "M504", "M506", "M508", "M503", "M505", "M507", "M501"]

    out = a.out or os.path.join(ROOT, "output" if full else "build/preview",
                                "realm_breach_trailer.mp4" if full else "realm_breach_%s.mp4" % a.mode)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    f_lo, f_hi = (a.frames if a.frames else (0, total))
    stills = [int(x) for x in a.stills.split(",")] if a.stills else None
    proc = None
    if not stills:
        audio = os.path.join(ROOT, "build", "audio", "mix.wav")
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
               "-r", str(FPS), "-i", "-"]
        if os.path.exists(audio) and not a.frames:
            cmd += ["-i", audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
        cmd += ["-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "16" if full else "20",
                "-preset", "slow" if full else "medium", "-r", str(FPS), "-movflags", "+faststart", "-shortest", out]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    stats = {"render": 0, "still": 0, "slate": 0}
    frames_iter = stills if stills else range(f_lo, f_hi)
    for f in frames_iter:
        shot = next(s for s in shots if s["start_frame"] <= f < s["end_frame"])
        sid = shot["id"]
        img = None
        kind = "slate"
        if sid in ("O1", "END"):
            img = np.zeros((H, W, 3), np.float32)
            kind = "render"
        elif sid == "E1":
            img = np.ones((H, W, 3), np.float32)
            kind = "render"
        elif sid == "M509":
            q = (f - shot["start_frame"]) / (tm["beat_sec"] * FPS / 4)
            qi = int(q)
            ss = byid[strobe_src[qi % len(strobe_src)]]
            sf_ = min(ss["end_frame"] + 9, ss["start_frame"] + 2 + (f - shot["start_frame"]) % 4)
            img, kind = src.frame(ss, sf_)
            if img is not None:
                img = img.copy()
        else:
            img, kind = src.frame(shot, f)
            if img is not None and kind == "still":
                u = (f - shot["start_frame"]) / max(1, shot["frames"])
                img = zoom_shift(img, 1.0 + 0.04 * u, 0, 0)
        if img is None:
            img = slate(shot, W, H)
        stats[kind] = stats.get(kind, 0) + 1

        # punch-in zoom on flagged shots (ease-out over the first 70% of the shot)
        sc = 1.0
        if "punch_in" in shot.get("flags", []):
            u = (f - shot["start_frame"]) / max(1, shot["frames"])
            sc = 1.0 + 0.09 * ease_out(u / 0.7)
        dx, dy = shake_offset(f, impacts, W, 11)
        if sc != 1.0 or dx or dy:
            img = zoom_shift(img, sc * (1.03 if (dx or dy) else 1.0), dx, dy)

        if sid not in ("O1", "END", "E1"):
            img = grade(img, LOOKS[look_for(shot)], H, W, vig)

        # ---------------- overlays
        if sid == "O1":
            t0 = 4
            if f >= t0:
                u = (f - t0) / 4.0
                s = 1.15 - 0.15 * overshoot(u)
                layer = cached_text(("floor999", W), "FLOOR 999", int(150 * k), tracking=0.2, weight=700, glow_alpha=0.7)
                paste(img, layer, (band_cx, H * 0.47), s, max_w=band_w * 0.92 * s)
        if shot.get("text"):
            tf = shot["text_frame"]
            if f >= tf:
                u = (f - tf) / 3.0
                s = 1.2 - 0.2 * overshoot(u)
                layer = cached_text((shot["text"], W), shot["text"], int(118 * k), tracking=0.2, weight=700, glow_alpha=0.7)
                paste(img, layer, (band_cx, H * 0.42), s, max_w=band_w * 0.9 * s)
        tv = f / FPS
        for sb in subs:
            if sb["start"] <= tv < sb["end"]:
                age = (tv - sb["start"]) * FPS
                al = min(1.0, (age + 1) / 3.0)
                layer = cached_text(("sub", sb["text"], W), sb["text"], int(video.SUBTITLE_SIZE * k), tracking=0.06,
                                    weight=700, glow_alpha=0.25, glow=EMBER)
                paste(img, layer, (band_cx, video.SUBTITLE_BASELINE_Y * k - 20 * k), 1.0, al, max_w=band_w)
        if sid == "E4":
            tf = bf(140)
            if f >= tf - 6:
                u = (f - (tf - 6)) / 18.0
                al = min(1.0, max(0.0, u))
                s = 1.0 + 0.035 * min(1.0, (f - tf + 6) / (6 * FPS))
                layer = cached_text(("title", W), "REALM BREACH", int(112 * k), tracking=0.22, weight=700,
                                    glow_alpha=0.55)
                paste(img, layer, (band_cx, H * 0.36), s, al, max_w=band_w * 0.95 * s)
            t2 = bf(142)
            if f >= t2:
                al = min(1.0, (f - t2) / 15.0)
                l1 = cached_text(("tag1", W), "EVERY LEGEND HAS A BEGINNING.", int(40 * k), tracking=0.16, weight=500,
                                 glow_alpha=0.3)
                l2 = cached_text(("tag2", W), "EVERY JOURNEY HAS AN END.", int(40 * k), tracking=0.16, weight=500,
                                 glow_alpha=0.3)
                paste(img, l1, (band_cx, H * 0.36 + 120 * k), 1.0, al, max_w=band_w)
                paste(img, l2, (band_cx, H * 0.36 + 175 * k), 1.0, al, max_w=band_w)

        # white flashes
        for ff, n, st in flashes:
            if ff <= f < ff + n:
                img = img * (1 - st) + st
        # grain (seeded per frame, constant strength)
        rng = np.random.default_rng(10007 + f)
        g = rng.standard_normal((H // 2, W // 2)).astype(np.float32)
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
        lum = img.mean(2, keepdims=True)
        img = img + g[..., None] * (0.022 * (0.6 + 0.4 * (1 - lum)))
        if a.safe:
            img[: int(video.SAFE_TOP * k)] *= 0.6
            img[H - int(video.SAFE_BOTTOM * k):] *= 0.6
            img[:, W - int(video.SAFE_RIGHT * k):] *= 0.6
        out8 = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
        if stills:
            p = os.path.join(ROOT, "build", "preview", "frame_%04d.png" % f)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            cv2.imwrite(p, cv2.cvtColor(out8, cv2.COLOR_RGB2BGR))
        else:
            proc.stdin.write(out8.tobytes())
    if proc:
        proc.stdin.close()
        proc.wait()
        print("wrote", out, stats)
    else:
        print("stills written", stats)


if __name__ == "__main__":
    main()
