"""STEP 3 — Reference edit analysis.

Extracts the pacing of the reference TikTok edit (not its content):
cuts (PySceneDetect), shot lengths, white flashes (luma spikes), punch-in
zooms (frame-to-frame similarity scale), motion spikes (whips / ramps),
its own audio drop and beat grid, and cut rates per section and per beat.
Writes analysis/reference.json.
"""
import json
import os

import cv2
import librosa
import numpy as np
from scenedetect import ContentDetector, SceneManager, open_video

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "input", "reference", "reference_edit.mp4")
SONG_JSON = os.path.join(ROOT, "analysis", "song.json")
OUT = os.path.join(ROOT, "analysis", "reference.json")


def active_box(path):
    """Bounding box of the non-letterbox picture (max over all frames)."""
    cap = cv2.VideoCapture(path)
    acc = None
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        acc = g if acc is None else np.maximum(acc, g)
    cap.release()
    r = np.where(acc.mean(1) > 10)[0]
    c = np.where(acc.mean(0) > 10)[0]
    return int(c.min()), int(r.min()), int(c.max()), int(r.max())


def detect_cuts(path, threshold, box):
    video = open_video(path)
    sm = SceneManager()
    sm.crop = box
    sm.add_detector(ContentDetector(threshold=threshold, min_scene_len=2))
    sm.detect_scenes(video)
    scenes = sm.get_scene_list()
    fps = video.frame_rate
    return [(s.get_frames(), e.get_frames()) for s, e in scenes], fps


def frame_stats(path, box):
    """Per-frame mean luma (active picture only), similarity-scale and motion vs
    the previous frame, and caption-band change (word-by-word captions)."""
    cap = cv2.VideoCapture(path)
    lumas, scales, motion, caption = [], [], [], []
    x0, y0, x1, y1 = box
    prev_cap = None
    prev = None
    orb = cv2.ORB_create(600)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        act = g[y0:y1 + 1, x0:x1 + 1]
        # caption band = bottom quarter of the active strip, bright text only
        band = (act[int(act.shape[0] * 0.72):] > 225).astype(np.float32)
        caption.append(0.0 if prev_cap is None else float(np.abs(band - prev_cap).mean()))
        prev_cap = band
        lumas.append(float(act.mean()))
        small = cv2.resize(act, (256, int(256 * act.shape[0] / act.shape[1])))
        s, m = 1.0, 0.0
        if prev is not None and prev.shape == small.shape:
            k1, d1 = orb.detectAndCompute(prev, None)
            k2, d2 = orb.detectAndCompute(small, None)
            if d1 is not None and d2 is not None and len(k1) > 12 and len(k2) > 12:
                mt = bf.match(d1, d2)
                if len(mt) > 12:
                    p1 = np.float32([k1[x.queryIdx].pt for x in mt])
                    p2 = np.float32([k2[x.trainIdx].pt for x in mt])
                    A, inl = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC)
                    if A is not None and inl is not None and inl.sum() > 10:
                        s = float(np.sqrt(A[0, 0] ** 2 + A[0, 1] ** 2))
                        m = float(np.hypot(A[0, 2], A[1, 2]))
            flow = cv2.calcOpticalFlowFarneback(prev, small, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            m = max(m, float(np.linalg.norm(flow, axis=2).mean()))
        scales.append(s)
        motion.append(m)
        prev = small
    cap.release()
    return np.array(lumas), np.array(scales), np.array(motion), np.array(caption)


def main():
    box = active_box(REF)
    cuts_scenes, fps = detect_cuts(REF, threshold=27.0, box=box)
    fps = float(fps)
    cut_frames = [s for s, _ in cuts_scenes][1:]
    shot_lengths = [(e - s) / fps for s, e in cuts_scenes]

    luma, scale, motion, caption = frame_stats(REF, box)
    n = len(luma)
    t = np.arange(n) / fps

    # White flashes: luma spike well above the local median
    med = np.array([np.median(luma[max(0, i - 15):i + 16]) for i in range(n)])
    flashes = [i for i in range(n) if luma[i] > max(150, med[i] + 60)]
    flash_events = []
    for i in flashes:
        if not flash_events or i - flash_events[-1][-1] > 1:
            flash_events.append([i])
        else:
            flash_events[-1].append(i)

    # Zooms: runs of frames inside one shot with steady scale drift
    cutset = set(cut_frames)
    zoom_events = []
    run = []
    for i in range(1, n):
        if i in cutset or abs(scale[i] - 1) < 0.004:
            if len(run) >= 4:
                total = float(np.prod(scale[run]))
                if abs(total - 1) > 0.03:
                    zoom_events.append({"start_s": round(run[0] / fps, 3), "end_s": round(run[-1] / fps, 3),
                                        "frames": len(run), "total_scale": round(total, 3)})
            run = []
        else:
            if run and np.sign(scale[i] - 1) != np.sign(scale[run[-1]] - 1):
                run = []
            run.append(i)

    # Motion spikes (whip pans / speed ramps): flow magnitude far above median
    mmed = np.median(motion)
    spikes = [round(i / fps, 3) for i in range(1, n) if i not in cutset and motion[i] > max(6.0, 5 * mmed)]

    # Reference audio: drop and beat grid of its own track
    y, sr = librosa.load(REF, sr=22050, mono=True)
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    rt = librosa.times_like(rms, sr=sr, hop_length=512)
    win = int(0.5 * sr / 512)
    sm = np.convolve(rms, np.ones(win) / win, mode="same")
    # Drop = first moment (after 2 s) the smoothed RMS exceeds 2x the track median
    above = np.where((rt > 2.0) & (sm > 2.0 * np.median(sm)))[0]
    drop_t = float(rt[above[0]]) if len(above) else float(rt[-1])
    # snap to the nearest detected cut within 0.25 s (the edit cuts on the drop)
    oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=256)
    tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=256, units="time")
    tempo = float(np.atleast_1d(tempo)[0])
    # pulse period after the drop (strong hits)
    post = (rt > drop_t) & (rt < rt[-1] - 0.5)
    pk = librosa.util.peak_pick(sm[post], pre_max=20, post_max=20, pre_avg=20, post_avg=20, delta=0.02, wait=40)
    post_peaks = rt[post][pk]

    cut_times = np.array(cut_frames) / fps
    near = cut_times[np.abs(cut_times - drop_t) < 0.25]
    if len(near):
        drop_t = float(near[0])
    # Word-by-word caption changes (the pre-drop "cuts")
    cap_thr = max(0.004, float(np.percentile(caption, 90)) * 0.6)
    word_changes = [i / fps for i in range(1, n) if caption[i] > cap_thr and caption[i] >= caption[i - 1]
                    and (i + 1 >= n or caption[i] >= caption[i + 1])]
    word_changes = np.array([w for w in word_changes if w < drop_t])
    dedup = []
    for w in word_changes:
        if not dedup or w - dedup[-1] > 0.12:
            dedup.append(float(w))
    word_changes = np.array(dedup)
    pre = cut_times[cut_times < drop_t]
    postc = cut_times[cut_times >= drop_t]
    beat_sec = 60.0 / tempo
    sections = {
        "pre_drop": {"start": 0.0, "end": round(drop_t, 3), "cuts": int(len(pre)),
                     "caption_word_changes": int(len(word_changes)),
                     "caption_changes_per_sec": round(len(word_changes) / max(drop_t, 1e-6), 3),
                     "cuts_per_sec": round(len(pre) / max(drop_t, 1e-6), 3),
                     "median_shot_s": round(float(np.median(np.diff(np.concatenate([[0], pre])))) if len(pre) else 0, 3)},
        "post_drop": {"start": round(drop_t, 3), "end": round(n / fps, 3), "cuts": int(len(postc)),
                      "cuts_per_sec": round(len(postc) / max(n / fps - drop_t, 1e-6), 3),
                      "median_shot_s": round(float(np.median(np.diff(np.concatenate([[drop_t], postc])))) if len(postc) else 0, 3)},
    }
    for k in sections:
        sections[k]["cuts_per_beat"] = round(sections[k]["cuts_per_sec"] * beat_sec, 3)

    # Is it the same track as our song? (onset-envelope correlation)
    same_track = False
    corr = None
    if os.path.exists(SONG_JSON):
        sy, _ = librosa.load(os.path.join(ROOT, "input", "song", "kingdom_beat_tiktok.mp3"), sr=22050, mono=True)
        a = librosa.onset.onset_strength(y=sy, sr=sr, hop_length=256)
        b = oenv
        a = (a - a.mean()) / a.std()
        b = (b - b.mean()) / b.std()
        xc = np.correlate(a, b, mode="valid") / len(b)
        corr = float(xc.max())
        same_track = corr > 0.5

    ref = {
        "file": os.path.relpath(REF, ROOT),
        "fps": fps,
        "frames": n,
        "duration": round(n / fps, 3),
        "layout": "16:9 footage letterboxed in a 9:16 frame; pre-drop is one static split-screen interview "
                  "where only word-by-word captions change; post-drop is a cut montage; grayscale grade",
        "active_box_xyxy": box,
        "same_track_as_song": same_track,
        "onset_corr_with_song": round(corr, 3) if corr is not None else None,
        "audio": {"tempo_librosa": round(tempo, 2), "drop_t": round(drop_t, 3),
                  "post_drop_pulses": [round(float(p), 3) for p in post_peaks]},
        "cuts_s": [round(float(c), 3) for c in cut_times],
        "post_drop_cut_intervals_beats": [round(float(d) / beat_sec, 2) for d in np.diff(np.concatenate([[drop_t], postc]))],
        "caption_word_changes_s": [round(float(w), 3) for w in word_changes],
        "shot_lengths_s": [round(s, 3) for s in shot_lengths],
        "shot_length_stats": {"min": round(min(shot_lengths), 3), "median": round(float(np.median(shot_lengths)), 3),
                              "mean": round(float(np.mean(shot_lengths)), 3), "max": round(max(shot_lengths), 3)},
        "sections": sections,
        "white_flashes": [{"t": round(e[0] / fps, 3), "frames": len(e)} for e in flash_events],
        "zooms": zoom_events,
        "motion_spikes_s": spikes,
        "mean_luma_per_sec": [round(float(luma[int(s * fps):int((s + 1) * fps)].mean()), 1)
                              for s in range(int(n / fps))],
    }
    with open(OUT, "w") as fh:
        json.dump(ref, fh, indent=1)
    print(json.dumps({k: ref[k] for k in ("duration", "same_track_as_song", "onset_corr_with_song", "audio",
                                          "shot_length_stats", "sections")}, indent=1))
    print("cuts:", ref["cuts_s"])
    print("flashes:", ref["white_flashes"])
    print("zooms:", ref["zooms"])
    print("motion spikes:", spikes)


if __name__ == "__main__":
    main()
