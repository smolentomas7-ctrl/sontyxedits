"""STEP 2 — Song analysis.

Measures tempo, beat grid, downbeats, phrases, onset strength and RMS energy
of the song and writes analysis/song.json + analysis/waveform.png.

Findings that drive the edit (see song.json["notes"]):
  * The track is a single 8-bar hook (16.04 s) looped for ~104 s, then a
    ~3 s tail. Band energies repeat to within 0.1 dB every phrase, so the
    song itself has no level-based intro / build / drop.
  * librosa's default tracker locks to a syncopated 3/16 figure (79.5 BPM).
    The true pulse is ~119.7 BPM: every onset sits on an 8th-note grid of
    0.2507 s, and the two-bar pattern repeats every 4.011 s.
  So the beat grid is fitted by least squares to the detected onsets, and the
  trailer's sections are created in the mix (filter / level automation) on
  top of that measured grid — no timestamp is invented.
"""
import json
import os
import sys

import librosa
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONG = os.path.join(ROOT, "input", "song", "kingdom_beat_tiktok.mp3")
OUT_JSON = os.path.join(ROOT, "analysis", "song.json")
OUT_PNG = os.path.join(ROOT, "analysis", "waveform.png")

SR = 44100
HOP = 256


def fit_grid(onsets, step0, t00):
    """Fit t = t0 + k*step to onsets (each onset snapped to its nearest grid k)."""
    step, t0 = step0, t00
    for _ in range(8):
        k = np.round((onsets - t0) / step)
        keep = np.abs(onsets - (t0 + k * step)) < step * 0.3
        A = np.vstack([np.ones(keep.sum()), k[keep]]).T
        (t0, step), *_ = np.linalg.lstsq(A, onsets[keep], rcond=None)
    resid = onsets[keep] - (t0 + k[keep] * step)
    return float(t0), float(step), float(np.sqrt(np.mean(resid ** 2))), int(keep.sum())


def main():
    y, sr = librosa.load(SONG, sr=SR, mono=True)
    duration = len(y) / sr

    oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    ot = librosa.times_like(oenv, sr=sr, hop_length=HOP)
    onsets = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, hop_length=HOP,
                                        units="time", backtrack=False)
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]

    # librosa's own estimate, recorded for transparency
    lib_tempo, _ = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=HOP)

    # Two-bar period from onset autocorrelation (strongest lag between 3 and 5 s)
    ac = librosa.autocorrelate(oenv, max_size=int(5.0 * sr / HOP))
    lags = np.arange(len(ac)) * HOP / sr
    win = (lags > 3.0) & (lags < 5.0)
    period2 = float(lags[win][np.argmax(ac[win])])

    # 8th-note grid fitted to all onsets in the looped body of the song
    body = onsets[onsets < 104.0]
    t0, eighth, rms_err, n_used = fit_grid(body, period2 / 16.0, body[0])
    beat = eighth * 2.0
    bpm = 60.0 / beat

    # Beats over the whole file
    k0 = int(np.ceil((0 - t0) / beat))
    beats = []
    k = k0
    while t0 + k * beat < duration - 0.05:
        beats.append(t0 + k * beat)
        k += 1
    beats = np.array(beats)

    def strength_at(t, w=0.04):
        m = (ot >= t - w) & (ot <= t + w)
        return float(oenv[m].max()) if m.any() else 0.0

    def rms_at(t, w=0.25):
        m = (ot >= t) & (ot <= t + w)
        return float(rms[m].mean()) if m.any() else 0.0

    beat_strength = np.array([strength_at(b) for b in beats])

    # Downbeat phase: the 808/kick lands on the "one". Use low-band (<150 Hz)
    # spectral flux at each of the 4 beat positions (broadband RMS is fooled
    # by the sustained 808 tail and the syncopated snares).
    Sl = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
    fl = librosa.fft_frequencies(sr=sr, n_fft=2048)
    Xl = np.log1p(Sl[fl < 150])
    low_flux = np.concatenate([[0.0], np.maximum(0, np.diff(Xl, axis=1)).sum(0)])
    lt = librosa.times_like(Sl, sr=sr, hop_length=HOP)

    def low_at(t, w=0.03):
        m = (lt >= t - w) & (lt <= t + w)
        return float(low_flux[m].max()) if m.any() else 0.0

    phase_scores = []
    for p in range(4):
        idx = np.arange(p, len(beats), 4)
        phase_scores.append(float(np.mean([low_at(beats[i]) for i in idx if beats[i] < 104])))
    db_phase = int(np.argmax(phase_scores))
    downbeats = beats[db_phase::4]

    # Loop / phrase detection: compare per-bar band energy fingerprints
    S = np.abs(librosa.stft(y, n_fft=4096, hop_length=1024)) ** 2
    f = librosa.fft_frequencies(sr=sr, n_fft=4096)
    st = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=1024)
    bands = [(20, 60), (60, 150), (150, 500), (500, 2000), (2000, 6000), (6000, 16000)]

    def bar_fp(t):
        m = (st >= t) & (st < t + 4 * beat)
        return np.array([10 * np.log10(S[(f >= lo) & (f < hi)][:, m].sum(0).mean() + 1e-9)
                         for lo, hi in bands])

    loudness = [rms_at(d, w=4 * beat) for d in downbeats]
    # End of the looped body: first downbeat (after 60 s) where energy falls away
    body_end = None
    for d, ld in zip(downbeats, loudness):
        if d > 60 and ld < 0.6 * np.median(loudness):
            body_end = float(d)
            break
    body_bars = [d for d in downbeats if d + 4 * beat <= (body_end or duration)]
    bar_fps = np.array([bar_fp(d) for d in body_bars])
    # Loop length = bar lag with the smallest mean band-energy difference
    loop_stats = {}
    for L in (2, 4, 8, 16):
        n = len(bar_fps) - L
        if n >= 4:
            loop_stats[L] = float(np.abs(bar_fps[:n] - bar_fps[L:L + n]).mean())
    loop_bars = min(loop_stats, key=loop_stats.get)
    if loop_stats[loop_bars] > 0.5:
        loop_bars = None
    phrase_len = loop_bars or 8
    # The loop restarts where the song's first downbeat is.
    phrase_starts = downbeats[::phrase_len]
    phrase_starts = phrase_starts[phrase_starts < (body_end or duration)]
    # Two-bar cycle starts (loud bar of the call/response) = strongest 808 hits
    cycle_starts = downbeats[::2]

    # 8th-note accent map: broadband onset + high band (>2 kHz: snares/claps)
    Xh = np.log1p(Sl[fl >= 2000])
    high_flux = np.concatenate([[0.0], np.maximum(0, np.diff(Xh, axis=1)).sum(0)])

    def high_at(t, w=0.03):
        m = (lt >= t - w) & (lt <= t + w)
        return float(high_flux[m].max()) if m.any() else 0.0

    eighths = np.arange(beats[0], duration - 0.05, eighth)
    eighth_strength = [round(strength_at(e8), 3) for e8 in eighths]
    eighth_high = [round(high_at(e8), 2) for e8 in eighths]
    # average accent per position in the 2-bar cycle (16 eighths)
    pos_high = [round(float(np.mean(eighth_high[p:int(104 / eighth):16])), 2) for p in range(16)]
    pos_low = [round(float(np.mean([low_at(e8) for e8 in eighths[p:int(104 / eighth):16]])), 3) for p in range(16)]

    # Strongest hits: downbeat onset strength, ranked
    db_strength = [strength_at(d) for d in downbeats]
    order = np.argsort(db_strength)[::-1]
    strongest = [{"t": round(float(downbeats[i]), 4), "strength": round(float(db_strength[i]), 3)}
                 for i in order[:12]]

    # Per-second RMS summary for the report
    rms_sec = []
    for s in range(int(duration) + 1):
        m = (ot >= s) & (ot < s + 1)
        rms_sec.append(round(float(rms[m].mean()) if m.any() else 0.0, 4))

    song = {
        "file": os.path.relpath(SONG, ROOT),
        "duration": round(duration, 4),
        "sample_rate": SR,
        "librosa_default_tempo": round(float(np.atleast_1d(lib_tempo)[0]), 3),
        "bpm": round(bpm, 4),
        "beat_sec": round(beat, 6),
        "bar_sec": round(beat * 4, 6),
        "grid_t0": round(t0, 5),
        "grid_fit_rms_error_ms": round(rms_err * 1000, 2),
        "grid_fit_onsets_used": n_used,
        "two_bar_period_autocorr": round(period2, 4),
        "downbeat_phase": db_phase,
        "loop_length_bars": loop_bars,
        "loop_mean_band_diff_db": {str(k): round(v, 3) for k, v in loop_stats.items()},
        "phrase_length_bars": phrase_len,
        "body_end": body_end,
        "beats": [round(float(b), 4) for b in beats],
        "beat_strength": [round(float(s), 3) for s in beat_strength],
        "downbeats": [round(float(d), 4) for d in downbeats],
        "phrase_starts": [round(float(p), 4) for p in phrase_starts],
        "cycle_starts": [round(float(c), 4) for c in cycle_starts],
        "downbeat_phase_scores_lowband": [round(v, 3) for v in phase_scores],
        "strongest_downbeats": strongest,
        "onsets": [round(float(o), 4) for o in onsets],
        "eighth_sec": round(eighth, 6),
        "eighth_strength": eighth_strength,
        "eighth_high": eighth_high,
        "cycle_position_high_accent": pos_high,
        "cycle_position_low_accent": pos_low,
        "rms_per_second": rms_sec,
        "notes": [
            "Track is one %d-bar hook looped until %.1fs, then a short tail; band energies repeat "
            "to %.2f dB on average every loop, so there is no level-based intro/build/drop in the audio." % (phrase_len, body_end or duration, loop_stats.get(phrase_len, 0)),
            "librosa's default tracker reports %.1f BPM (it locks onto a syncopated 3/16 figure); "
            "the fitted 8th-note grid gives %.2f BPM with %.1f ms RMS error over %d onsets."
            % (float(np.atleast_1d(lib_tempo)[0]), bpm, rms_err * 1000, n_used),
            "Intro / build / drop / break / outro are therefore created in the mix by filter and level "
            "automation on this measured grid. The 808 lands on the downbeat (low-band flux), so D and U "
            "are placed on 808 downbeats at phrase starts.",
        ],
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(song, fh, indent=1)

    # --- waveform.png -------------------------------------------------------
    markers = {}
    tpath = os.path.join(ROOT, "config", "timing.json")
    if os.path.exists(tpath) and "--no-markers" not in sys.argv:
        with open(tpath) as fh:
            tm = json.load(fh)
        off = tm["song_offset"]
        for key in ("D", "U", "break_start", "outro_start", "build_start"):
            if key in tm["markers"]:
                markers[key] = tm["markers"][key] + off  # song time
    fig, axes = plt.subplots(2, 1, figsize=(22, 7), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1]})
    ds = 64
    tt = np.arange(0, len(y), ds) / sr
    axes[0].fill_between(tt, -np.abs(y[::ds]), np.abs(y[::ds]), color="#3a3f47", lw=0)
    rt = librosa.times_like(rms, sr=sr, hop_length=HOP)
    axes[0].plot(rt, rms / rms.max(), color="#FF6A1A", lw=0.8, label="RMS")
    for d in downbeats:
        axes[0].axvline(d, color="#6FA8FF", lw=0.35, alpha=0.6)
    for p in phrase_starts:
        axes[0].axvline(p, color="#F2B544", lw=1.4, alpha=0.9)
    colors = {"D": "#FF3B3B", "U": "#FFE9A8", "break_start": "#A04DFF",
              "outro_start": "#8DB580", "build_start": "#FF9A1A"}
    for i, (k, v) in enumerate(sorted(markers.items(), key=lambda kv: kv[1])):
        axes[0].axvline(v, color=colors[k], lw=3)
        axes[0].text(v + 0.4, 0.97 - 0.09 * (i % 3), "%s %.2fs" % (k, v), color=colors[k], fontsize=12,
                     fontweight="bold", transform=axes[0].get_xaxis_transform(), va="top")
    axes[0].set_ylim(-1, 1.05)
    axes[0].set_title("Song time. Kingdom Beat (TikTok Version) — %.2f BPM, %d-bar loop. "
                      "Blue = downbeats, gold = phrase starts" % (bpm, phrase_len))
    axes[1].plot(ot, oenv / oenv.max(), color="#9A9A9A", lw=0.5)
    axes[1].vlines(beats, 0, beat_strength / beat_strength.max(), color="#FF6A1A", lw=1)
    axes[1].set_xlabel("song time (s)")
    axes[1].set_ylabel("onset")
    for ax in axes:
        ax.set_facecolor("#07080A")
    fig.patch.set_facecolor("#0B1418")
    for ax in axes:
        ax.tick_params(colors="#cccccc")
        ax.title.set_color("#eeeeee")
    axes[1].xaxis.label.set_color("#cccccc")
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=90)
    print("BPM %.3f  beat %.4fs  t0 %.4f  fit err %.1fms  loop %s bars  phrases %s"
          % (bpm, beat, t0, rms_err * 1000, loop_bars, [round(p, 2) for p in phrase_starts]))
    print("body end", body_end, " strongest downbeats", strongest[:5])


if __name__ == "__main__":
    main()
