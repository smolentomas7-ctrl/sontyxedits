"""STEP 11 (audio) — Mix song + voice + sound design to output/realm_breach_mix.wav.

* Song: plays continuously from config/timing.json song_offset; music automation
  (low-pass cutoff + gain keys) creates the muffled intro, the one beat of
  silence, the life-lost dips, the dialogue break and the outro.
* Voice: placed at timing.json vo[...].file_start; music ducks 9 dB under every
  line (80 ms attack, 300 ms release).
* SFX: beds + cues from src/cues.py (positions in song beats).
* Ending: the song's first note (its first 808 hit) on the final black frames so
  the loop back to frame 0 lands on the beat.
* Master: gentle bus compression, loudness normalised to -14 LUFS integrated,
  true-peak limited to -1 dBTP.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import cues as CUE  # noqa: E402

SR = 48000


def load(path):
    if path.endswith(".mp3"):
        tmp = os.path.join(ROOT, "build", "audio", "song_48k.wav")
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        if not os.path.exists(tmp):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-ar", str(SR), "-ac", "2", tmp], check=True)
        path = tmp
    x, sr = sf.read(path, always_2d=True)
    if sr != SR:
        x = signal.resample_poly(x, SR, sr, axis=0)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, 1)
    return x.astype(np.float64)


def db(g):
    return 10 ** (g / 20)


def place(bus, x, t, gain_db=0.0, pan=0.0, fade_out=None, dur=None, rate=1.0):
    if rate != 1.0:
        n = int(len(x) / rate)
        x = signal.resample(x, n, axis=0)
    if dur is not None:
        x = x[: int(dur * SR)]
    x = x * db(gain_db)
    if fade_out:
        m = min(len(x), int(fade_out * SR))
        x[-m:] *= np.linspace(1, 0, m)[:, None]
    if pan:
        gl = math.cos((pan + 1) * math.pi / 4) * 1.414
        gr = math.sin((pan + 1) * math.pi / 4) * 1.414
        x = x * np.array([gl, gr])
    i = int(round(t * SR))
    if i < 0:
        x = x[-i:]
        i = 0
    j = min(len(bus), i + len(x))
    if j > i:
        bus[i:j] += x[: j - i]


def automation(keys, n, field, log=False):
    ts = np.array([k["t"] for k in keys])
    vs = np.array([k[field] for k in keys], dtype=float)
    tt = np.arange(n) / SR
    if log:
        return np.exp(np.interp(tt, ts, np.log(vs)))
    return np.interp(tt, ts, vs)


def tv_lowpass(x, cutoff, block=256):
    """Time-varying 2nd-order low-pass (block-wise coefficients, state carried)."""
    out = np.zeros_like(x)
    zi = np.zeros((1, 2, x.shape[1]))
    for i in range(0, len(x), block):
        fc = float(np.clip(cutoff[min(i + block // 2, len(cutoff) - 1)], 40, 20000))
        sos = signal.butter(2, min(fc, SR / 2 * 0.95), btype="low", fs=SR, output="sos")
        y, zi = signal.sosfilt(sos, x[i:i + block], axis=0, zi=zi)
        out[i:i + block] = y
    return out


def compressor(x, thr_db=-18, ratio=2.0, attack=0.01, release=0.15):
    lvl = np.abs(x).max(1)
    a = math.exp(-1 / (attack * SR))
    r = math.exp(-1 / (release * SR))
    env = signal.lfilter([1 - r], [1, -r], lvl)  # smooth (release-dominated)
    env = np.maximum(env, signal.lfilter([1 - a], [1, -a], lvl))
    edb = 20 * np.log10(env + 1e-9)
    gdb = np.minimum(0, (thr_db - edb) * (1 - 1 / ratio))
    return x * db(gdb)[:, None]


AAC_CEILING_DB = -2.4


def limiter(x, ceiling_db=-1.0, look=0.005, release=0.08, block=32):
    """Look-ahead peak limiter on a 4x-oversampled (true-peak) estimate:
    instant attack, exponential release, gain applied per small block."""
    from scipy.ndimage import minimum_filter1d
    c = db(ceiling_db)
    up = signal.resample_poly(x, 4, 1, axis=0)
    peak = np.abs(up).max(1)
    peak = peak[: len(x) * 4].reshape(-1, 4).max(1)
    need = np.minimum(1.0, c / (peak + 1e-12))
    need = minimum_filter1d(need, size=2 * int(look * SR) + 1)
    nb = int(math.ceil(len(need) / block))
    req = np.array([need[i * block:(i + 1) * block].min() for i in range(nb)])
    r = math.exp(-block / (release * SR))
    g = np.empty(nb)
    cur = 1.0
    for i in range(nb):
        cur = req[i] if req[i] < cur else req[i] - (req[i] - cur) * r
        g[i] = cur
    gs = np.repeat(g, block)[: len(x)]
    return x * gs[:, None]


def main():
    tm = json.load(open(os.path.join(ROOT, "config", "timing.json")))
    t0, beat, off = tm["song_grid_t0"], tm["beat_sec"], tm["song_offset"]
    dur = tm["total_frames"] / tm["fps"]
    n = int(round(dur * SR))
    vt = lambda b: t0 + b * beat - off  # noqa: E731

    # ---- music
    song = load(os.path.join(ROOT, "input", "song", "kingdom_beat_tiktok.mp3"))
    s0 = int(round(off * SR))
    music = np.zeros((n, 2))
    seg = song[s0:s0 + n]
    music[: len(seg)] = seg
    keys = tm["music_automation"]
    cutoff = automation(keys, n, "lowpass_hz", log=True)
    gain = automation(keys, n, "gain_db")
    music = tv_lowpass(music, cutoff)
    music *= db(gain)[:, None]
    # the song's first note on the final black frames (loop point)
    first = song[int((t0 - 0.03) * SR): int((t0 + 0.55) * SR)].copy()
    first = signal.sosfilt(signal.butter(2, 900, btype="low", fs=SR, output="sos"), first, axis=0)
    first[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))[:, None]
    place(music, first, vt(tm["markers_beats"]["black"]) - 0.03, -4)

    # ---- voice + ducking envelope
    vo = np.zeros((n, 2))
    duck = np.zeros(n)
    for vid, v in tm["vo"].items():
        x = load(os.path.join(ROOT, v["file"]))
        place(vo, x, v["file_start"], 0.0)
        a, b = int(v["speech_start"] * SR), int((v["speech_end"] + 0.15) * SR)
        duck[max(0, a - int(0.08 * SR)):min(n, b)] = 1.0
    att, rel = math.exp(-1 / (0.03 * SR)), math.exp(-1 / (0.3 * SR))
    env = np.zeros(n)
    cur = 0.0
    for i in range(0, n, 32):
        tgt = duck[i]
        k = att if tgt > cur else rel
        cur = tgt + (cur - tgt) * k ** 32
        env[i:i + 32] = cur
    music *= db(-9.0 * env)[:, None]

    # ---- sound design
    sfxdir = os.path.join(ROOT, "assets", "audio", "sfx")
    cache = {}

    def snd(name):
        if name not in cache:
            cache[name] = load(os.path.join(sfxdir, name + ".wav"))
        return cache[name]

    fx = np.zeros((n, 2))
    for b_in, b_out, name, g, fi, fo in CUE.BEDS:
        x = snd(name)
        L = int((vt(b_out) - vt(b_in)) * SR)
        reps = int(math.ceil(L / len(x))) + 1
        y = np.concatenate([x] * reps)[:L].copy()
        fi_n, fo_n = min(L, int(fi * SR)), min(L, int(fo * SR))
        if fi_n:
            y[:fi_n] *= np.linspace(0, 1, fi_n)[:, None]
        if fo_n:
            y[-fo_n:] *= np.linspace(1, 0, fo_n)[:, None]
        place(fx, y, vt(b_in), g)
    for b, name, g, o in CUE.CUES:
        x = snd(name)
        t = vt(b)
        if o.get("align") == "peak":
            t -= CUE.PEAK[name] / o.get("rate", 1.0)
        place(fx, x, t, g, pan=o.get("pan", 0.0), fade_out=o.get("fade_out"), dur=o.get("dur"), rate=o.get("rate", 1.0))
    # silence after the flash: hard cut of everything except the blast tail
    cut = vt(129.0)
    ci = int(cut * SR)
    fade = np.ones(n)
    fade[ci:ci + int(0.04 * SR)] = np.linspace(1, 0, int(0.04 * SR))
    fade[ci + int(0.04 * SR):int(vt(132.0) * SR)] = 0.0
    music *= fade[:, None]

    # ---- bus
    mixbus = music * db(-3.0) + vo * db(-1.0) + fx * db(-4.0)
    mixbus = compressor(mixbus, -16, 1.8)
    meter = pyln.Meter(SR)
    # converge: gain to -14 LUFS, then true-peak limit (the limiter is always the last stage). The ceiling sits
    # below -1 dBTP because AAC encoding overshoots by ~1.1 dB (measured: -1.21 dBTP wav -> -0.08 dBTP decoded).
    for _ in range(4):
        loud = meter.integrated_loudness(mixbus)
        mixbus *= db(-14.0 - loud)
        mixbus = limiter(mixbus, AAC_CEILING_DB)
    out = os.path.join(ROOT, "build", "audio", "mix.wav")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sf.write(out, mixbus.astype(np.float32), SR, subtype="FLOAT")
    # stems for review
    for nm, x in (("music", music), ("vo", vo), ("fx", fx)):
        sf.write(os.path.join(ROOT, "build", "audio", "stem_%s.wav" % nm), (x * 0.5).astype(np.float32), SR, subtype="FLOAT")
    print("mix -> %s  %.2fs  loudness %.2f LUFS  peak %.2f dBFS" %
          (out, n / SR, meter.integrated_loudness(mixbus), 20 * np.log10(np.abs(mixbus).max())))


if __name__ == "__main__":
    main()
