"""Preview QA: per-shot frame strips + automatic motion checks on the rendered animation frames.

python3 src/preview_qa.py [--mode preview|final] [--shots O2,O5] [--n 10]

For every shot with rendered frames in build/shots/<ID>/<mode>/:
  * completeness: every frame the edit reads ([start_frame, end_frame)) exists;
  * pops: a frame-to-frame change far above the shot's own typical change (a jump in a pose, a camera key,
    a cloth explosion, a light popping on), excluding the frames around beat impacts listed in the edit;
  * flicker: luminance alternating up/down for 3+ frames with a meaningful swing;
  * black / blown frames (mean luminance < 0.015 or > 0.85).
Writes build/qa/<mode>/<ID>.jpg (n frames sampled evenly over the shot, labelled) and build/qa/<mode>/report.json,
and prints one line per shot.
"""
import argparse
import json
import os

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_small(p, w=135, h=240):
    im = cv2.imread(p, cv2.IMREAD_COLOR)
    if im is None:
        return None
    im = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    return im


def lum(im):
    return 0.0722 * im[..., 0] + 0.7152 * im[..., 1] + 0.2126 * im[..., 2]


def strip(frames, paths, out, sid, tile_w=270, title=None, cols=4):
    tiles = []
    for f, p in zip(frames, paths):
        im = cv2.imread(p)
        h = int(round(tile_w * im.shape[0] / im.shape[1]))
        im = cv2.resize(im, (tile_w, h), interpolation=cv2.INTER_AREA)
        cv2.rectangle(im, (0, 0), (tile_w, 22), (0, 0, 0), -1)
        cv2.putText(im, "%s f%d" % (sid, f), (5, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (120, 200, 255), 1, cv2.LINE_AA)
        tiles.append(im)
    gap = np.zeros((tiles[0].shape[0], 4, 3), np.uint8)
    rows = []
    for r in range(0, len(tiles), cols):
        part = tiles[r:r + cols] + [np.zeros_like(tiles[0])] * (cols - len(tiles[r:r + cols]))
        rows.append(np.hstack([x for t in part for x in (t, gap)][:-1]))
    vgap = np.zeros((4, rows[0].shape[1], 3), np.uint8)
    row = np.vstack([x for rr in rows for x in (rr, vgap)][:-1])
    if title:
        bar = np.zeros((30, row.shape[1], 3), np.uint8)
        cv2.putText(bar, title, (6, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230, 230, 230), 1, cv2.LINE_AA)
        row = np.vstack([bar, row])
    cv2.imwrite(out, row, [cv2.IMWRITE_JPEG_QUALITY, 88])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="preview", choices=["preview", "final"])
    ap.add_argument("--shots")
    ap.add_argument("--n", type=int, default=8)
    a = ap.parse_args()
    tl = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
    tm = json.load(open(os.path.join(ROOT, "config", "timing.json")))
    want = set(a.shots.split(",")) if a.shots else None
    out_dir = os.path.join(ROOT, "build", "qa", a.mode)
    os.makedirs(out_dir, exist_ok=True)
    rep_path = os.path.join(out_dir, "report.json")
    report = json.load(open(rep_path)) if os.path.exists(rep_path) else {}

    def bf(b):        # beat -> frame (same as the edit)
        return int(round((tm["song_grid_t0"] + b * tm["beat_sec"] - tm["song_offset"]) * 30)) - 1

    for s in tl["shots"]:
        sid = s["id"]
        if want is not None and sid not in want:
            continue
        d = os.path.join(ROOT, "build", "shots", sid, a.mode)
        if not os.path.isdir(d):
            continue
        lo, hi = s["start_frame"], s["end_frame"]
        need = list(range(lo, hi))
        missing = [f for f in need if not os.path.exists(os.path.join(d, "f_%04d.png" % f))]
        have = [f for f in need if f not in missing]
        if not have:
            continue
        ims = {f: load_small(os.path.join(d, "f_%04d.png" % f)) for f in have}
        L = {f: float(lum(ims[f]).mean()) for f in have}
        diffs = {}
        for f in have:
            if f - 1 in ims:
                diffs[f] = float(np.abs(ims[f] - ims[f - 1]).mean())
        issues = []
        if missing:
            issues.append("missing %d frames: %s" % (len(missing), missing[:8]))
        # beats inside the shot (impacts and flashes land within ~2 frames of a quarter beat)
        b0 = int((lo - 5) / 15.045 * 4) - 4
        beat_frames = {bf(q / 4.0) + k for q in range(b0, b0 + int((hi - lo) / 15.045 * 4) + 9) for k in (-2, -1, 0, 1, 2)}
        if len(diffs) >= 3:
            v = np.array(list(diffs.values()))
            med = float(np.median(v))
            for f, dv in diffs.items():
                if dv > max(5.0 * med, 0.045) and f not in beat_frames:
                    issues.append("pop at f%d (diff %.3f vs median %.3f)" % (f, dv, med))
        fs = sorted(L)
        for i in range(2, len(fs)):
            a0, a1, a2 = L[fs[i - 2]], L[fs[i - 1]], L[fs[i]]
            if (a1 - a0) * (a2 - a1) < 0 and min(abs(a1 - a0), abs(a2 - a1)) > 0.03 and fs[i] - fs[i - 2] == 2:
                issues.append("flicker around f%d (%.3f %.3f %.3f)" % (fs[i - 1], a0, a1, a2))
        for f in have:
            if L[f] < 0.015:
                issues.append("near-black f%d (%.3f)" % (f, L[f]))
            elif L[f] > 0.85:
                issues.append("blown f%d (%.3f)" % (f, L[f]))
        # strip
        k = min(a.n, len(have))
        pick = sorted({have[int(round(i * (len(have) - 1) / max(1, k - 1)))] for i in range(k)})
        strip(pick, [os.path.join(d, "f_%04d.png" % f) for f in pick], os.path.join(out_dir, "%s.jpg" % sid), sid,
              title="%s  %s  f%d-%d  %s" % (sid, s.get("subject", "")[:70], lo, hi - 1, s.get("motion", "")))
        report[sid] = {"frames": [lo, hi], "missing": len(missing), "lum_mean": float(np.mean(list(L.values()))),
                       "diff_median": float(np.median(list(diffs.values()))) if diffs else 0.0, "issues": issues}
        print("%-6s f%d-%d  %3d/%3d frames  lum %.3f  %s" % (sid, lo, hi - 1, len(have), len(need),
                                                             report[sid]["lum_mean"], "; ".join(issues) or "ok"))
    json.dump(report, open(rep_path, "w"), indent=1)


if __name__ == "__main__":
    main()
