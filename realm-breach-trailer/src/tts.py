"""STEP 9 — Voice-over (text-to-speech) + character voice chains.

No ElevenLabs key is available and HuggingFace is blocked in this
environment, so the voice is Kokoro-82M (Apache-2.0) via kokoro-onnx, with
model files from github.com/thewh1teagle/kokoro-onnx releases.

  Warrior    : bm_lewis (deep British male)  -> warrior chain
  Fallen God : am_onyx  (deep US male)       -> god chain

Each line is rendered as several takes (different speeds); the take whose
length best fits the line's target slot is kept (ties -> the slower,
heavier read). Raw takes go to build/vo/raw, processed lines to
assets/audio/vo/<id>.wav, and durations to assets/audio/vo/vo.json, which the
timeline builder reads.

Usage: python3 src/tts.py            (all lines)
       python3 src/tts.py VO2 VO5    (only these)
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "config"))
import video  # noqa: E402

MODEL = os.environ.get("KOKORO_MODEL", "/opt/tts/kokoro-v1.0.onnx")
VOICES = os.environ.get("KOKORO_VOICES", "/opt/tts/voices-v1.0.bin")
RAW = os.path.join(ROOT, "build", "vo", "raw")
OUT = os.path.join(ROOT, "assets", "audio", "vo")
SR = 48000

WARRIOR_VOICE = "bm_lewis"
GOD_VOICE = "am_onyx"

# id, speaker, display text, tts text, target seconds (slot), shout
LINES = [
    ("VO1", "warrior", "So... you're the one who's been waiting for me.",
     "So... you're the one, who's been waiting for me.", 3.2, False),
    ("VO2", "warrior", "I have crossed worlds... faced death... and sacrificed everything.",
     "I have crossed worlds... faced death... and sacrificed everything.", 5.2, False),
    ("VO2S", "warrior", "I have faced death... and sacrificed everything.",
     "I have faced death... and sacrificed everything.", 3.8, False),
    ("VO3", "warrior", "But now...", "But now...", 1.3, False),
    ("VO4", "warrior", "The Fallen God...", "The Fallen God...", 1.6, False),
    ("VO5", "warrior", "YOUR REIGN ENDS HERE!", "Your reign, ends here!", 1.8, True),
    ("VO6", "god", "After everything you've lost... you still dare to challenge me?",
     "After everything you've lost... you still dare, to challenge me?", 4.8, False),
    ("VO7", "warrior", "You took everything from me...", "You took everything from me...", 2.2, False),
    ("VO8", "warrior", "But you made one mistake.", "But you made, one mistake.", 2.0, False),
    ("VO9", "warrior", "YOU LET ME LIVE.", "You let me live!", 1.6, True),
]
SPEEDS = (0.78, 0.84, 0.90, 0.96)


def ffmpeg_filter(src, dst, af):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", af, "-ar", str(SR), "-ac", "1", dst],
                   check=True)


def trim_silence(a, sr, thr_db=-45, pad=0.04):
    env = np.abs(a)
    thr = 10 ** (thr_db / 20) * env.max()
    idx = np.where(env > thr)[0]
    if not len(idx):
        return a
    s = max(0, idx[0] - int(pad * sr))
    e = min(len(a), idx[-1] + int(pad * sr))
    return a[s:e]


def make_ir(seconds, rt60, sr, seed, predelay=0.0, damp_hz=6000, early=None):
    """Synthetic reverb impulse response: seeded noise with exponential decay,
    progressively low-passed (air damping), optional early reflections."""
    rng = np.random.default_rng(seed)
    n = int(seconds * sr)
    t = np.arange(n) / sr
    noise = rng.standard_normal(n)
    decay = np.exp(-6.91 * t / rt60)
    ir = noise * decay
    # frequency-dependent damping: blend a low-passed copy in over time
    b, a = signal.butter(2, damp_hz / (sr / 2))
    lp = signal.lfilter(b, a, ir)
    w = np.clip(t / (rt60 * 0.6), 0, 1)
    ir = ir * (1 - w) + lp * w
    if early:
        for dt, g in early:
            i = int(dt * sr)
            if i < n:
                ir[i] += g
    pd = int(predelay * sr)
    ir = np.concatenate([np.zeros(pd), ir])
    return ir / np.sqrt(np.sum(ir ** 2))


def convolve_wet(dry, ir, wet):
    w = signal.fftconvolve(dry, ir)[: len(dry) + len(ir)]
    out = np.zeros(len(w))
    out[: len(dry)] += dry * (1 - wet)
    # match wet energy to dry before mixing
    w *= np.sqrt(np.sum(dry ** 2) / (np.sum(w ** 2) + 1e-12))
    out += w * wet
    return out


def soft_sat(x, drive):
    return np.tanh(x * drive) / np.tanh(drive)


def normalise_peak(x, peak_db=-1.0):
    return x * (10 ** (peak_db / 20) / (np.abs(x).max() + 1e-9))


def warrior_chain(src, dst, shout, seed):
    tmp = dst + ".tmp.wav"
    # pitch -1.5 st (formant shifted with it -> bigger chest), EQ, helmet box resonance,
    # 4 ms metal reflection (helmet), gentle top roll-off, 4:1 compression.
    af = ",".join([
        "aresample=48000",
        "rubberband=pitch=%.6f:formant=shifted:pitchq=quality" % (2 ** (-1.5 / 12)),
        "highpass=f=70:poles=2",
        "equalizer=f=120:t=q:w=0.9:g=3",
        "equalizer=f=300:t=q:w=1.0:g=-3",
        "equalizer=f=3000:t=q:w=1.2:g=2",
        "equalizer=f=1150:t=q:w=2.5:g=2.5",
        "aecho=0.9:0.6:4|7:0.22|0.12",
        "lowpass=f=7800:poles=2",
        "acompressor=threshold=0.1:ratio=4:attack=6:release=90:makeup=2.5:knee=3",
    ])
    ffmpeg_filter(src, tmp, af)
    x, sr = sf.read(tmp)
    os.remove(tmp)
    if shout:
        x = soft_sat(normalise_peak(x, -1) * 1.0, 2.2)
    plate = make_ir(1.2, 0.9, sr, seed, predelay=0.012, damp_hz=5000,
                    early=[(0.007, 0.5), (0.013, 0.35), (0.021, 0.25)])
    y = convolve_wet(x, plate, 0.15)
    y = y[: len(x) + int(0.6 * sr)]
    sf.write(dst, normalise_peak(y, -1.0), sr)


def god_chain(src, dst, seed):
    a = dst + ".a.wav"
    b = dst + ".b.wav"
    ffmpeg_filter(src, a, "aresample=48000,rubberband=pitch=%.6f:formant=shifted:pitchq=quality,"
                          "highpass=f=40,equalizer=f=90:t=q:w=1:g=3,equalizer=f=2500:t=q:w=1.5:g=1.5"
                  % (2 ** (-5 / 12)))
    ffmpeg_filter(src, b, "aresample=48000,rubberband=pitch=0.5:formant=shifted:pitchq=quality,"
                          "highpass=f=30,lowpass=f=1800")
    x, sr = sf.read(a)
    o, _ = sf.read(b)
    os.remove(a)
    os.remove(b)
    n = max(len(x), len(o))
    x = np.pad(x, (0, n - len(x)))
    o = np.pad(o, (0, n - len(o)))
    o = soft_sat(normalise_peak(o, 0), 4.0) * 0.45      # distorted octave-down bed
    mix = normalise_peak(x, -3) + o * 10 ** (-3 / 20)
    # long hall, 30% wet
    hall = make_ir(5.0, 3.6, sr, seed, predelay=0.045, damp_hz=3500,
                   early=[(0.031, 0.4), (0.057, 0.3), (0.083, 0.2)])
    wet = convolve_wet(mix, hall, 0.30)
    # reverse-reverb swell before the first word
    head = mix[: int(0.9 * sr)]
    rev = signal.fftconvolve(head[::-1], hall)[::-1]
    rev = rev[-int(1.4 * sr):] if len(rev) > int(1.4 * sr) else rev
    rev *= np.sqrt(np.sum(head ** 2) / (np.sum(rev ** 2) + 1e-12)) * 0.5
    fade = np.linspace(0, 1, len(rev)) ** 2
    rev *= fade
    pre = len(rev)
    out = np.zeros(pre + len(wet))
    out[:pre] += rev
    out[pre:] += wet
    # tail of the swell overlaps the first word slightly (it "sucks into" the voice)
    out = out[: pre + len(mix) + int(2.2 * sr)]
    sf.write(dst, normalise_peak(out, -1.0), sr)
    return pre / sr   # seconds of swell before the first word


def main():
    from kokoro_onnx import Kokoro
    only = set(sys.argv[1:])
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    k = Kokoro(MODEL, VOICES)
    meta_path = os.path.join(OUT, "vo.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    for lid, who, display, text, target, shout in LINES:
        if only and lid not in only:
            continue
        voice = WARRIOR_VOICE if who == "warrior" else GOD_VOICE
        lang = "en-gb" if voice.startswith("b") else "en-us"
        takes = []
        speeds = (0.95, 1.0, 1.06) if shout else SPEEDS
        for i, sp in enumerate(speeds):
            a, sr = k.create(text, voice=voice, speed=sp, lang=lang)
            a = trim_silence(np.asarray(a, dtype=np.float64), sr)
            path = os.path.join(RAW, "%s_t%d.wav" % (lid, i + 1))
            sf.write(path, a, sr)
            takes.append({"take": i + 1, "speed": sp, "dur": round(len(a) / sr, 3), "path": path})
        # keep the take closest to the slot; prefer slower reads on ties (+-0.15 s)
        best = min(takes, key=lambda t: (round(abs(t["dur"] - target) / 0.15), t["speed"]))
        dst = os.path.join(OUT, "%s.wav" % lid)
        seed = video.seed_for(lid)
        lead = 0.0
        if who == "warrior":
            warrior_chain(best["path"], dst, shout, seed)
        else:
            lead = god_chain(best["path"], dst, seed)
        info = sf.info(dst)
        meta[lid] = {"speaker": who, "voice": voice, "text": display, "tts_text": text,
                     "takes": [{k2: v for k2, v in t.items() if k2 != "path"} for t in takes],
                     "chosen_take": best["take"], "speech_dur": best["dur"],
                     "file_dur": round(info.duration, 3), "lead_in": round(lead, 3),
                     "file": os.path.relpath(dst, ROOT)}
        print("%-5s %-8s take %d (%.2fx) speech %.2fs  file %.2fs  lead %.2fs" %
              (lid, voice, best["take"], best["speed"], best["dur"], info.duration, lead))
    with open(meta_path, "w") as fh:
        json.dump(meta, fh, indent=1)


if __name__ == "__main__":
    main()
