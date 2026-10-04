"""STEP 10 — Procedural sound design (synthesised in Python, no samples).

Every sound is a pure function of (name, seed): python3 src/sfx.py renders the
whole library to assets/audio/sfx/<name>.wav (48 kHz stereo, peak -1 dBFS).
src/mix.py places them on the timeline from the cue sheet.

Building blocks: filtered noise, modal (inharmonic partial) synthesis for metal,
pitch-swept sines for sub hits, formant filters for growls, granular bursts for
debris, synthetic reverb impulse responses.
"""
import json
import math
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio", "sfx")
SR = 48000


# ---------------------------------------------------------------- primitives
def rng(seed):
    return np.random.default_rng(seed)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def env_ad(n, attack, decay, curve=4.0):
    """Attack-decay envelope over n samples (seconds)."""
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    d = np.exp(-np.maximum(t - attack, 0) * curve / max(decay, 1e-4))
    return a * d


def bandpass(x, lo, hi, order=2):
    lo = max(lo, 10)
    hi = min(hi, SR / 2 - 100)
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lowpass(x, f, order=2):
    sos = signal.butter(order, min(f, SR / 2 - 100), btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def highpass(x, f, order=2):
    sos = signal.butter(order, max(f, 10), btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def pink(n, r):
    w = r.standard_normal(n)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, w) * 6


def brown(n, r):
    x = np.cumsum(r.standard_normal(n))
    x = highpass(x, 20)
    return x / (np.abs(x).max() + 1e-9)


def sat(x, drive=2.0):
    return np.tanh(x * drive) / np.tanh(drive)


def norm(x, peak_db=-1.0):
    return x * (10 ** (peak_db / 20) / (np.abs(x).max() + 1e-12))


def stereo(x, width=0.0, r=None, pan=0.0):
    """Mono -> stereo with optional decorrelation (short random delays) and pan (-1..1)."""
    if x.ndim == 2:
        return x
    L, R = x.copy(), x.copy()
    if width > 0 and r is not None:
        d = int(SR * 0.0007 * width)
        R = np.concatenate([np.zeros(d), x[:-d]]) if d > 0 else R
        R = 0.7 * R + 0.3 * bandpass(x, 300, 6000) * width
    gl = math.cos((pan + 1) * math.pi / 4)
    gr = math.sin((pan + 1) * math.pi / 4)
    return np.stack([L * gl * 1.414, R * gr * 1.414], 1)


def ir(seconds, rt60, seed, damp=6000, predelay=0.01):
    r = rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    x = r.standard_normal(n) * np.exp(-6.91 * t / rt60)
    x = 0.5 * x + 0.5 * lowpass(x, damp)
    x = np.concatenate([np.zeros(int(predelay * SR)), x])
    return x / np.sqrt((x ** 2).sum())


def reverb(x, wet, rt60=1.6, seed=1, damp=5000):
    h = ir(min(6.0, rt60 * 1.4), rt60, seed, damp)
    if x.ndim == 2:
        return np.stack([reverb(x[:, 0], wet, rt60, seed, damp), reverb(x[:, 1], wet, rt60, seed + 1, damp)], 1)
    y = signal.fftconvolve(x, h)
    y *= np.sqrt((x ** 2).sum() / ((y ** 2).sum() + 1e-12))
    out = np.zeros(len(y))
    out[: len(x)] += x * (1 - wet)
    out += y * wet
    return out


def pad_to(x, n):
    if len(x) >= n:
        return x[:n]
    return np.concatenate([x, np.zeros((n - len(x),) + x.shape[1:])])


def mix(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros((n, 2))
    for p in parts:
        p = stereo(p) if p.ndim == 1 else p
        out[: len(p)] += p
    return out


def sine_sweep(dur, f0, f1, curve="exp"):
    t = t_axis(dur)
    if curve == "exp":
        f = f0 * (f1 / f0) ** (t / dur)
    else:
        f = f0 + (f1 - f0) * t / dur
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph)


def modal(dur, freqs, decays, amps, r, jitter=0.01):
    """Inharmonic modal synthesis (bells, metal)."""
    t = t_axis(dur)
    x = np.zeros(len(t))
    for f, d, a in zip(freqs, decays, amps):
        f = f * (1 + r.uniform(-jitter, jitter))
        x += a * np.sin(2 * np.pi * f * t + r.uniform(0, 6.28)) * np.exp(-t / d)
    return x


def formant(x, formants):
    y = np.zeros(len(x))
    for f, bw, g in formants:
        y += g * bandpass(x, f - bw / 2, f + bw / 2, order=2)
    return y


# ---------------------------------------------------------------- sounds
def sub_hit(seed=1, dur=1.6, f0=95, f1=32, click=0.25):
    r = rng(seed)
    x = sine_sweep(dur, f0, f1) * env_ad(int(dur * SR), 0.002, dur * 0.7, 3.5)
    c = highpass(r.standard_normal(int(0.02 * SR)), 1500) * env_ad(int(0.02 * SR), 0.0005, 0.015) * click
    return norm(stereo(sat(pad_to(x, len(x)) + pad_to(c, len(x)), 1.6)))


def boom(seed=2, dur=4.5):
    r = rng(seed)
    n = int(dur * SR)
    body = sine_sweep(dur, 120, 28) * env_ad(n, 0.004, dur * 0.45, 3.0)
    rumble = lowpass(brown(n, r), 140) * env_ad(n, 0.01, dur * 0.8, 2.5)
    crack = bandpass(r.standard_normal(int(0.12 * SR)), 200, 3000) * env_ad(int(0.12 * SR), 0.001, 0.08)
    x = mix(stereo(sat(body * 0.9, 1.8)), stereo(rumble * 0.6, 1, r), stereo(pad_to(crack, n) * 0.35, 1, r))
    return norm(reverb(x, 0.3, 3.5, seed))


def footstep(seed=3, heavy=1.0):
    """Heavy armoured step on stone: thump + grit + plate clank + mail jingle."""
    r = rng(seed)
    n = int(0.9 * SR)
    thump = lowpass(sine_sweep(0.9, 85, 45) * env_ad(n, 0.002, 0.09, 4) + 0.6 * r.standard_normal(n) *
                    env_ad(n, 0.001, 0.03), 260)
    grit = bandpass(r.standard_normal(n), 900, 5000) * env_ad(n, 0.002, 0.06, 5) * 0.35
    clank = modal(0.9, [612, 1340, 2210, 3170], [0.08, 0.06, 0.05, 0.03], [0.5, 0.35, 0.25, 0.15], r, 0.05)
    clank = pad_to(np.concatenate([np.zeros(int(0.012 * SR)), clank]), n) * 0.18
    jing = np.zeros(n)
    for k in range(int(28 * heavy)):
        i = int(r.uniform(0.005, 0.22) * SR)
        m = int(0.012 * SR)
        g = bandpass(r.standard_normal(m), 3500, 9000) * env_ad(m, 0.0003, 0.008) * r.uniform(0.05, 0.2)
        jing[i:i + m] += g
    jing *= np.exp(-np.arange(n) / SR / 0.15)
    x = thump * heavy + grit + clank + jing * 0.6
    return norm(reverb(stereo(x, 0.6, r), 0.18, 1.4, seed), -3)


def chainmail(seed=4, dur=0.8):
    r = rng(seed)
    n = int(dur * SR)
    x = np.zeros(n)
    for k in range(70):
        i = int(r.uniform(0, dur * 0.85) * SR)
        m = int(0.01 * SR)
        g = bandpass(r.standard_normal(m), 3000, 10000) * env_ad(m, 0.0002, 0.007) * r.uniform(0.1, 0.5)
        x[i:i + m] += g
    x *= np.sin(np.pi * np.arange(n) / n) ** 0.7
    return norm(stereo(x, 1.0, r), -6)


def cloth_flap(seed=5, dur=0.7):
    r = rng(seed)
    n = int(dur * SR)
    x = bandpass(pink(n, r), 150, 1800) * env_ad(n, 0.08, dur * 0.6, 3)
    am = 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(9 + 6 * r.random(n)) / SR)
    return norm(stereo(x * am, 0.8, r), -6)


def wind(seed=6, dur=30.0, bright=0.5):
    r = rng(seed)
    n = int(dur * SR)
    base = brown(n, r) * 0.7 + pink(n, r) * 0.02
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * np.arange(n) / SR + r.uniform(0, 6))
    lfo2 = 0.7 + 0.3 * np.sin(2 * np.pi * 0.19 * np.arange(n) / SR + r.uniform(0, 6))
    howl = bandpass(pink(n, r), 300 + 300 * bright, 900 + 900 * bright) * lfo2 * 0.15
    L = lowpass(base, 700) * lfo + howl
    R = lowpass(np.roll(base, int(0.37 * SR)), 700) * lfo[::-1] + np.roll(howl, int(0.21 * SR))
    fade = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (1.5 * SR))
    return norm(np.stack([L * fade, R * fade], 1), -6)


def thunder(seed=7, dur=6.0):
    r = rng(seed)
    n = int(dur * SR)
    x = np.zeros(n)
    for k in range(9):
        st = int(r.uniform(0, 1.6) * SR)
        m = int(r.uniform(1.5, 4.0) * SR)
        g = lowpass(brown(m, r), r.uniform(120, 300)) * env_ad(m, r.uniform(0.01, 0.15), m / SR * 0.6, 3)
        x[st:st + m] += pad_to(g, len(x[st:st + m])) * r.uniform(0.4, 1)
    x = reverb(stereo(x, 1.0, r), 0.45, 4.5, seed, 1200)
    return norm(x, -2)


def ember_crackle(seed=8, dur=20.0, density=6.0):
    r = rng(seed)
    n = int(dur * SR)
    x = np.zeros(n)
    k = int(dur * density)
    for _ in range(k):
        i = int(r.uniform(0, dur - 0.05) * SR)
        m = int(r.uniform(0.002, 0.012) * SR)
        g = highpass(r.standard_normal(m), r.uniform(1500, 4000)) * env_ad(m, 0.0002, m / SR * 0.5) * r.uniform(0.05, 0.5)
        x[i:i + m] += g
    bed = bandpass(pink(n, r), 2000, 7000) * 0.01
    return norm(stereo(x + bed, 1.0, r), -10)


def drone(seed=9, dur=30.0, f=36.7):
    r = rng(seed)
    t = t_axis(dur)
    x = np.zeros(len(t))
    for k, (m, a) in enumerate([(1, 1.0), (2, 0.35), (3, 0.12), (1.5, 0.15), (4.02, 0.06)]):
        det = 1 + 0.002 * math.sin(k)
        x += a * np.sin(2 * np.pi * f * m * det * t + 0.3 * np.sin(2 * np.pi * 0.05 * (k + 1) * t))
    pad = lowpass(signal.sawtooth(2 * np.pi * f * 2 * t) + signal.sawtooth(2 * np.pi * f * 2.005 * t), 300) * 0.15
    x = sat(x * 0.6 + pad, 1.3)
    fade = np.minimum(1, np.minimum(np.arange(len(t)), len(t) - np.arange(len(t))) / (3 * SR))
    return norm(stereo(x * fade, 0.8, r), -6)


def metal_clash(seed=10, dur=3.0, size=1.0):
    """Greatsword vs obsidian: stacked inharmonic strikes + transient + low thud + long ring."""
    r = rng(seed)
    n = int(dur * SR)
    layers = []
    for k in range(3):
        base = r.uniform(380, 520) / size
        ratios = [1.0, 2.31, 3.42, 4.97, 6.13, 7.88, 9.7, 12.4]
        freqs = [base * q * r.uniform(0.98, 1.02) for q in ratios]
        decays = [r.uniform(0.6, 1.6) * (1.2 if q < 3 else 0.7) for q in ratios]
        amps = [1.0 / (1 + 0.45 * i) for i in range(len(ratios))]
        m = modal(dur, freqs, decays, amps, r)
        off = int(r.uniform(0, 0.004) * SR)
        layers.append(pad_to(np.concatenate([np.zeros(off), m]), n) * r.uniform(0.6, 1.0))
    ring = sum(layers)
    tr = highpass(r.standard_normal(int(0.03 * SR)), 2000) * env_ad(int(0.03 * SR), 0.0002, 0.02)
    thud = lowpass(sine_sweep(dur, 140, 45) * env_ad(n, 0.001, 0.25, 4), 300)
    grind = bandpass(r.standard_normal(n), 2500, 8000) * env_ad(n, 0.005, 0.35, 5) * 0.25
    x = norm(ring) * 0.55 + pad_to(tr, n) * 0.8 + thud * 0.8 + grind
    x = sat(x, 1.5)
    return norm(reverb(stereo(x, 1.0, r), 0.32, 2.4, seed, 7000))


def whoosh(seed=11, dur=0.6, lo=200, hi=3500, pan_sweep=0.8):
    r = rng(seed)
    n = int(dur * SR)
    noise = pink(n, r)
    t = np.arange(n) / n
    env = np.sin(np.pi * t) ** 2.2
    # sweep a band-pass by processing in short blocks
    out = np.zeros(n)
    B = 512
    for i in range(0, n, B):
        c = lo * (hi / lo) ** (np.sin(np.pi * min(1, i / n)) )
        seg = noise[max(0, i - 2048):i + B]
        y = bandpass(seg, c * 0.5, c * 1.6)[-min(B, n - i):]
        out[i:i + len(y)] = y
    out *= env
    L = out * (0.5 - 0.5 * pan_sweep * (t * 2 - 1))
    R = out * (0.5 + 0.5 * pan_sweep * (t * 2 - 1))
    return norm(np.stack([L, R], 1), -3)


def riser(seed=12, dur=4.0, f0=80, f1=1800):
    r = rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / n
    tone = 0
    for k in range(3):
        tone = tone + sine_sweep(dur, f0 * (1 + 0.5 * k), f1 * (1 + 0.5 * k)) * (0.5 / (k + 1))
    nz = np.zeros(n)
    noise = pink(n, r)
    B = 1024
    for i in range(0, n, B):
        c = 300 * (8000 / 300) ** (i / n)
        seg = noise[max(0, i - 4096):i + B]
        y = bandpass(seg, c * 0.6, c * 1.4)[-min(B, n - i):]
        nz[i:i + len(y)] = y
    env = t ** 2.4
    x = (tone * 0.5 + nz * 0.8) * env
    x[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    return norm(reverb(stereo(x, 1.0, r), 0.25, 1.8, seed), -2)


def heartbeat(seed=13, beats=4, bpm=62):
    r = rng(seed)
    period = 60 / bpm
    n = int((beats * period + 1.0) * SR)
    x = np.zeros(n)
    for b in range(beats):
        for off, g in ((0.0, 1.0), (0.24, 0.65)):
            i = int((b * period + off) * SR)
            m = int(0.25 * SR)
            th = lowpass(sine_sweep(0.25, 70, 38) * env_ad(m, 0.004, 0.09, 4), 150) * g
            x[i:i + m] += th[: len(x[i:i + m])]
    return norm(stereo(sat(x, 2.0)), -1)


def fire(seed=14, dur=2.0, whoosh_in=True):
    r = rng(seed)
    n = int(dur * SR)
    roar = lowpass(brown(n, r), 600) * (0.6 + 0.4 * np.abs(lowpass(r.standard_normal(n), 8)) * 4)
    crack = ember_crackle(seed + 1, dur, 40)[:, 0]
    env = env_ad(n, 0.05 if whoosh_in else 0.005, dur * 0.7, 2.5)
    x = (roar * 0.8 + pad_to(crack, n) * 0.6) * env
    if whoosh_in:
        w = whoosh(seed + 2, 0.5, 150, 2500)[:, 0]
        x[: len(w)] += w * 0.8
    return norm(reverb(stereo(x, 1.0, r), 0.2, 1.5, seed), -2)


def lightning(seed=15, dur=3.5):
    r = rng(seed)
    n = int(dur * SR)
    crack = highpass(r.standard_normal(int(0.08 * SR)), 1200) * env_ad(int(0.08 * SR), 0.0002, 0.05, 6)
    sizzle = bandpass(r.standard_normal(int(0.4 * SR)), 3000, 12000) * env_ad(int(0.4 * SR), 0.001, 0.25, 4) * \
        (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 60 * np.arange(int(0.4 * SR)) / SR)))
    rumble = thunder(seed + 3, dur)[:, 0] * 0.7
    x = pad_to(crack, n) * 1.0 + pad_to(sizzle, n) * 0.4 + pad_to(rumble, n)
    return norm(stereo(sat(x, 1.4), 1.0, r))


def debris(seed=16, dur=3.0, count=60):
    r = rng(seed)
    n = int(dur * SR)
    x = np.zeros(n)
    for k in range(count):
        tt = r.uniform(0, dur * 0.8) ** 1.6 / (dur * 0.8) ** 0.6
        i = int(tt * SR)
        m = int(r.uniform(0.02, 0.09) * SR)
        f = r.uniform(300, 3500)
        g = bandpass(r.standard_normal(m), f * 0.6, f * 1.5) * env_ad(m, 0.0005, m / SR * 0.4) * r.uniform(0.1, 1) * \
            math.exp(-tt / (dur * 0.5))
        x[i:i + m] += g[: len(x[i:i + m])]
    return norm(reverb(stereo(x, 1.0, r), 0.3, 2.0, seed), -4)


def god_blast(seed=17, dur=6.0):
    """The ultimate: impact + sub drop + shimmer + debris tail."""
    r = rng(seed)
    n = int(dur * SR)
    sub = sine_sweep(dur, 90, 22) * env_ad(n, 0.003, dur * 0.55, 3.2)
    body = lowpass(brown(n, r), 400) * env_ad(n, 0.002, 1.2, 3.5)
    crack = highpass(r.standard_normal(int(0.15 * SR)), 800) * env_ad(int(0.15 * SR), 0.0003, 0.1, 5)
    shimmer = modal(dur, [1760, 2637, 3520, 5274, 7040], [1.6, 1.3, 1.1, 0.9, 0.7], [0.5, 0.4, 0.3, 0.2, 0.15], r)
    deb = debris(seed + 1, dur, 120)[:, 0]
    x = sat(sub * 1.2, 2.0) + body * 0.7 + pad_to(crack, n) + shimmer * 0.12 + pad_to(deb, n) * 0.5
    return norm(reverb(stereo(x, 1.0, r), 0.35, 4.0, seed, 4000))


def growl(seed=18, dur=1.6, pitch=55, vowel="a"):
    r = rng(seed)
    t = t_axis(dur)
    vib = 1 + 0.04 * np.sin(2 * np.pi * 5.5 * t) + 0.03 * lowpass(r.standard_normal(len(t)), 10) * 8
    f = pitch * vib * (1 + 0.25 * np.sin(np.pi * t / dur))
    saw = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR)
    rough = saw * (1 + 0.6 * lowpass(r.standard_normal(len(t)), 80) * 6) + 0.4 * pink(len(t), r)
    F = {"a": [(700, 160, 1.0), (1150, 200, 0.6), (2600, 300, 0.25)],
         "o": [(450, 120, 1.0), (800, 160, 0.6), (2830, 300, 0.2)],
         "u": [(325, 100, 1.0), (700, 140, 0.5), (2530, 300, 0.15)]}[vowel]
    x = formant(rough, F) * env_ad(len(t), 0.12, dur * 0.7, 2)
    return norm(reverb(stereo(sat(x, 2.5), 0.8, r), 0.3, 2.2, seed), -3)


def shriek(seed=19, dur=1.2):
    r = rng(seed)
    t = t_axis(dur)
    f = 900 + 500 * np.sin(np.pi * t / dur) + 40 * np.sin(2 * np.pi * 7 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + bandpass(r.standard_normal(len(t)), 1500, 6000) * 0.6
    x *= env_ad(len(t), 0.05, dur * 0.6, 2)
    return norm(reverb(stereo(x, 1.0, r), 0.5, 3.0, seed), -6)


def chime(seed=20, f=880.0, dur=2.5, bright=1.0):
    r = rng(seed)
    x = modal(dur, [f, f * 2.0, f * 2.76, f * 5.4], [1.4, 0.9, 0.6, 0.3], [1, 0.4 * bright, 0.25 * bright, 0.1 * bright], r, 0.002)
    return norm(reverb(stereo(x), 0.35, 2.5, seed), -6)


def glass_fizz(seed=21, dur=1.5):
    r = rng(seed)
    n = int(dur * SR)
    x = bandpass(r.standard_normal(n), 3000, 9000) * env_ad(n, 0.01, dur * 0.6, 3) * 0.4
    x += modal(dur, [2310, 3890, 5230], [0.4, 0.3, 0.2], [0.3, 0.2, 0.1], r)
    return norm(stereo(x, 0.6, r), -8)


def breath(seed=22, cycles=3, period=1.6):
    """Exhausted breathing inside a helmet (band-limited, boxy)."""
    r = rng(seed)
    n = int(cycles * period * SR)
    x = np.zeros(n)
    for c in range(cycles):
        for k, (st, ln, g) in enumerate(((0.0, 0.6, 0.6), (0.7, 0.8, 1.0))):
            i = int((c * period + st) * SR)
            m = int(ln * SR)
            b = bandpass(pink(m, r), 400, 2400) * np.sin(np.pi * np.arange(m) / m) ** 1.5 * g
            x[i:i + m] += b[: len(x[i:i + m])]
    x = bandpass(x, 300, 3500) + 0.3 * bandpass(x, 1000, 1300)
    return norm(reverb(stereo(x), 0.12, 0.6, seed), -10)


def stone_grind(seed=23, dur=2.0):
    r = rng(seed)
    n = int(dur * SR)
    x = lowpass(brown(n, r), 500) * (0.5 + 0.5 * np.abs(lowpass(r.standard_normal(n), 30)) * 6)
    x += bandpass(r.standard_normal(n), 800, 2500) * 0.08
    x *= np.sin(np.pi * np.arange(n) / n)
    return norm(reverb(stereo(x, 0.8, r), 0.3, 2.5, seed), -6)


def water(seed=24, dur=20.0):
    r = rng(seed)
    n = int(dur * SR)
    x = bandpass(pink(n, r), 200, 6000) * (0.8 + 0.2 * lowpass(r.standard_normal(n), 3) * 10)
    fade = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / SR)
    return norm(stereo(x * fade, 1.0, r), -8)


def meadow_wind(seed=25, dur=20.0):
    r = rng(seed)
    n = int(dur * SR)
    x = highpass(pink(n, r), 500) * 0.3 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * np.arange(n) / SR))
    x = lowpass(x, 5000)
    fade = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (2 * SR))
    return norm(stereo(x * fade, 1.0, r), -14)


def impact(seed=26, dur=1.2, size=1.0):
    r = rng(seed)
    n = int(dur * SR)
    thump = sine_sweep(dur, 120 / size, 40) * env_ad(n, 0.001, 0.2 * size, 4)
    crack = bandpass(r.standard_normal(int(0.05 * SR)), 600, 6000) * env_ad(int(0.05 * SR), 0.0003, 0.03, 5)
    x = sat(thump, 1.8) + pad_to(crack, n) * 0.6
    return norm(reverb(stereo(x, 0.6, r), 0.2, 1.4, seed), -1)


def tick(seed=27):
    r = rng(seed)
    n = int(0.12 * SR)
    x = bandpass(r.standard_normal(n), 1500, 7000) * env_ad(n, 0.0003, 0.02, 6) + \
        lowpass(sine_sweep(0.12, 160, 60), 300) * env_ad(n, 0.001, 0.05, 4) * 0.6
    return norm(stereo(x), -6)


def reverse_swell(seed=28, dur=1.5):
    r = rng(seed)
    n = int(dur * SR)
    x = reverb(stereo(bandpass(pink(int(0.3 * SR), r), 200, 4000), 1.0, r), 0.9, dur * 0.9, seed)[:n]
    x = x[::-1] * np.linspace(0, 1, len(x))[:, None] ** 2
    return norm(x, -4)


LIBRARY = {
    "sub_hit": lambda: sub_hit(1),
    "sub_hit_small": lambda: sub_hit(31, dur=0.9, f0=110, f1=45),
    "boom": lambda: boom(2),
    "footstep_a": lambda: footstep(3),
    "footstep_b": lambda: footstep(33),
    "footstep_c": lambda: footstep(43),
    "footstep_heavy": lambda: footstep(53, heavy=1.4),
    "chainmail": lambda: chainmail(4),
    "cloth_flap": lambda: cloth_flap(5),
    "wind": lambda: wind(6, 34.0),
    "thunder": lambda: thunder(7),
    "thunder_far": lambda: thunder(37, 7.0),
    "ember_crackle": lambda: ember_crackle(8, 30.0),
    "drone": lambda: drone(9, 34.0),
    "clash_big": lambda: metal_clash(10, 3.5, 1.0),
    "clash_a": lambda: metal_clash(40, 2.5, 0.85),
    "clash_b": lambda: metal_clash(50, 2.5, 1.1),
    "whoosh_a": lambda: whoosh(11, 0.55),
    "whoosh_b": lambda: whoosh(41, 0.45, 300, 5000, -0.8),
    "whoosh_long": lambda: whoosh(51, 0.9, 120, 2500),
    "riser_4s": lambda: riser(12, 4.0),
    "riser_2s": lambda: riser(42, 2.0, 120, 2400),
    "heartbeat": lambda: heartbeat(13, 4),
    "fire": lambda: fire(14, 2.0),
    "portal_fire": lambda: fire(44, 6.0, whoosh_in=False),
    "lightning": lambda: lightning(15),
    "debris": lambda: debris(16),
    "god_blast": lambda: god_blast(17),
    "growl_a": lambda: growl(18, 1.6, 52, "a"),
    "growl_o": lambda: growl(48, 1.4, 70, "o"),
    "growl_u": lambda: growl(58, 1.8, 40, "u"),
    "boss_roar": lambda: growl(68, 2.4, 34, "a"),
    "shriek": lambda: shriek(19),
    "chime_low": lambda: chime(20, 330.0),
    "glass_fizz": lambda: glass_fizz(21),
    "breath": lambda: breath(22),
    "stone_grind": lambda: stone_grind(23),
    "water": lambda: water(24, 12.0),
    "meadow_wind": lambda: meadow_wind(25, 20.0),
    "impact": lambda: impact(26),
    "impact_big": lambda: impact(36, 1.8, 1.6),
    "tick": lambda: tick(27),
    "reverse_swell": lambda: reverse_swell(28),
    "blade_ring": lambda: chime(29, 1240.0, 3.0, 1.6),
    "ring_slide": lambda: chime(39, 2200.0, 1.2, 0.6),
}
# rising chimes for the 8 rarities (pentatonic ascent)
for _i, _semi in enumerate([0, 2, 4, 7, 9, 12, 14, 16]):
    LIBRARY["loot_%d" % _i] = (lambda s=_semi, i=_i: chime(60 + i, 392.0 * 2 ** (s / 12), 1.6, 0.8 + 0.1 * i))


def main():
    os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[1:])
    meta = {}
    for name, fn in LIBRARY.items():
        if only and name not in only:
            continue
        x = fn()
        x = np.asarray(x, dtype=np.float64)
        if x.ndim == 1:
            x = stereo(x)
        x = norm(x, -1.0)
        path = os.path.join(OUT, name + ".wav")
        sf.write(path, x.astype(np.float32), SR, subtype="FLOAT")
        meta[name] = {"dur": round(len(x) / SR, 3)}
        print("%-16s %.2fs" % (name, len(x) / SR))
    old = os.path.join(OUT, "sfx.json")
    if os.path.exists(old) and only:
        m = json.load(open(old))
        m.update(meta)
        meta = m
    json.dump(meta, open(old, "w"), indent=1)


if __name__ == "__main__":
    main()
