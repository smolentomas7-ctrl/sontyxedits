"""Burned-in subtitle timing: word groups synced to the voice.

Each line's display text is split into word groups at its pauses ("...", ","
in the TTS text). The pauses are *measured* in the raw TTS take (silence gaps in
the RMS envelope); groups without a measured pause are split by character
count. Output: edit/subtitles.json, times in video seconds.
"""
import json
import os
import re

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# display groups per line (what appears on screen, in order)
GROUPS = {
    "VO1": ["So...", "you're the one", "who's been waiting for me."],
    "VO2": ["I have crossed worlds...", "faced death...", "and sacrificed everything."],
    "VO3": ["But now..."],
    "VO4": ["The Fallen God..."],
    "VO5": ["YOUR REIGN", "ENDS HERE!"],
    "VO6": ["After everything", "you've lost...", "you still dare", "to challenge me?"],
    "VO7": ["You took everything", "from me..."],
    "VO8": ["But you made", "one mistake."],
    "VO9": ["YOU LET ME LIVE."],
}
# which group boundaries coincide with an audible pause in the TTS text
PAUSED = {"VO1": [True, True], "VO2": [True, True], "VO5": [True], "VO6": [False, True, True],
          "VO7": [False], "VO8": [True]}


def gaps(path, min_gap=0.09, thr_db=-32.0):
    x, sr = sf.read(path)
    if x.ndim == 2:
        x = x.mean(1)
    hop = int(0.01 * sr)
    rms = np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, mode="same"))[::hop]
    db = 20 * np.log10(rms + 1e-9) - 20 * np.log10(rms.max() + 1e-9)
    quiet = db < thr_db
    out, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]:
                j += 1
            if (j - i) * 0.01 >= min_gap and i > 0 and j < len(quiet):
                out.append(((i + j) / 2 * 0.01, (j - i) * 0.01, i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return out, len(x) / sr


def main():
    tl = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
    vo = json.load(open(os.path.join(ROOT, "assets", "audio", "vo", "vo.json")))
    subs = []
    for vid, groups in GROUPS.items():
        meta = vo[vid]
        raw = os.path.join(ROOT, "build", "vo", "raw", "%s_t%d.wav" % (vid, meta["chosen_take"]))
        start = tl["vo"][vid]["speech_start"]
        dur = meta["speech_dur"]
        bounds = []
        if os.path.exists(raw) and len(groups) > 1:
            g, _ = gaps(raw)
            paused = PAUSED.get(vid, [True] * (len(groups) - 1))
            need = sum(paused)
            # take the `need` longest gaps, in time order
            longest = sorted(sorted(g, key=lambda q: -q[1])[:need], key=lambda q: q[0])
            k = 0
            chars = [len(x) for x in groups]
            for bi, p in enumerate(paused):
                if p and k < len(longest):
                    bounds.append(("gap", longest[k]))
                    k += 1
                else:
                    bounds.append(("chars", None))
        # resolve boundaries to times
        times = [0.0]
        for bi, (kind, q) in enumerate(bounds):
            if kind == "gap":
                times.append(q[3])            # next group appears when speech resumes
            else:
                # split the span between neighbours by character count
                nxt = next((b[1][3] for b in bounds[bi + 1:] if b[0] == "gap"), dur)
                prev = times[-1]
                c0 = len(groups[bi])
                c1 = len(groups[bi + 1])
                times.append(prev + (nxt - prev) * c0 / (c0 + c1))
        times.append(dur)
        for gi, text in enumerate(groups):
            s = start + times[gi]
            e = start + times[gi + 1]
            # hold the last group a little after the line ends
            if gi == len(groups) - 1:
                e += 0.35
            subs.append({"vo": vid, "text": text, "start": round(s - 0.03, 3), "end": round(e, 3),
                         "speaker": meta["speaker"]})
    # no overlaps: each group ends when the next begins
    subs.sort(key=lambda s: s["start"])
    for a, b in zip(subs, subs[1:]):
        if a["end"] > b["start"]:
            a["end"] = b["start"]
    with open(os.path.join(ROOT, "edit", "subtitles.json"), "w") as fh:
        json.dump(subs, fh, indent=1)
    for s in subs:
        print("%6.2f-%6.2f %-5s %s" % (s["start"], s["end"], s["vo"], s["text"]))


if __name__ == "__main__":
    main()
