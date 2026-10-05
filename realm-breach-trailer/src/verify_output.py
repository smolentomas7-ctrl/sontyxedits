"""STEP 13 — Verify the delivered MP4 against the spec and write a JSON report.

python3 src/verify_output.py [output/realm_breach_trailer.mp4]

Checks: container/codec (H.264 High, yuv420p), 1080x1920 (9:16), 30 fps CFR, 45-75 s duration matching the
timeline, AAC 48 kHz ~320 kb/s, integrated loudness -14 LUFS +-0.5, true peak <= -1 dBTP (4x oversampled),
no letterboxing (no black bars on any side across sampled frames), and the loop seam (last frame ~ first
frame). Prints PASS/FAIL per check and writes output/verify_report.json.
"""
import json
import os
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "output", "realm_breach_trailer.mp4")
tm = json.load(open(os.path.join(ROOT, "config", "timing.json")))


def probe(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", p],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def frames_at(p, times, w=270, h=480):
    imgs = []
    for t in times:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % t, "-i", p, "-frames:v", "1", "-vf",
                              "scale=%d:%d" % (w, h), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, check=True).stdout
        imgs.append(np.frombuffer(raw, np.uint8).reshape(h, w, 3).astype(np.float32) / 255.0)
    return imgs


def main():
    res = {"file": path, "checks": {}}
    ok_all = True

    def check(name, ok, detail):
        nonlocal ok_all
        res["checks"][name] = {"pass": bool(ok), "detail": detail}
        ok_all &= bool(ok)
        print("%-4s %-22s %s" % ("PASS" if ok else "FAIL", name, detail))

    info = probe(path)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    num, den = map(int, v["r_frame_rate"].split("/"))
    fps = num / den
    dur = float(info["format"]["duration"])
    nb = int(v.get("nb_frames", 0) or 0)
    check("video_codec", v["codec_name"] == "h264" and v.get("profile", "").lower().startswith("high")
          and v.get("pix_fmt") == "yuv420p", "%s %s %s" % (v["codec_name"], v.get("profile"), v.get("pix_fmt")))
    check("resolution_9x16", (v["width"], v["height"]) == (1080, 1920), "%dx%d" % (v["width"], v["height"]))
    check("fps_30", abs(fps - 30.0) < 1e-6, "%.3f fps, %d frames" % (fps, nb))
    check("duration", 45.0 <= dur <= 75.0 and abs(dur - tm["duration"]) < 0.1,
          "%.3f s (timeline %.3f s)" % (dur, tm["duration"]))
    if a is None:
        check("audio", False, "no audio stream")
    else:
        br = int(a.get("bit_rate", 0) or 0)
        check("audio_codec", a["codec_name"] == "aac" and int(a["sample_rate"]) == 48000 and br >= 280000,
              "%s %s Hz %d kb/s %s ch" % (a["codec_name"], a["sample_rate"], br // 1000, a.get("channels")))
        import pyloudnorm as pyln
        wav = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-f", "f32le", "-ac", "2", "-ar", "48000",
                              "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(wav, np.float32).reshape(-1, 2).astype(np.float64)
        lufs = pyln.Meter(48000).integrated_loudness(x)
        check("loudness_-14", abs(lufs + 14.0) <= 0.5, "%.2f LUFS integrated" % lufs)
        from scipy.signal import resample_poly
        tp = max(np.max(np.abs(resample_poly(x[:, c], 4, 1))) for c in range(2))
        tp_db = 20 * np.log10(max(tp, 1e-9))
        check("true_peak", tp_db <= -1.0, "%.2f dBTP (4x oversampled, after AAC decode)" % tp_db)
        res["loudness_lufs"], res["true_peak_dbtp"] = lufs, tp_db
    # letterboxing: no row/column band at the frame edges that is black in every sampled frame
    ts = list(np.linspace(1.0, dur - 1.0, 24))
    imgs = frames_at(path, ts)
    lit = np.max(np.stack([im.max(2) for im in imgs]), 0)            # brightest value per pixel over time
    rows, cols = lit.max(1), lit.max(0)
    bars = {"top": int(np.argmax(rows > 0.03)), "bottom": int(np.argmax(rows[::-1] > 0.03)),
            "left": int(np.argmax(cols > 0.03)), "right": int(np.argmax(cols[::-1] > 0.03))}
    check("no_letterbox", max(bars.values()) <= 2, "black edge bands (px @270x480): %s" % bars)
    # loop: the last frame should cut cleanly into the first (both black)
    first, last = frames_at(path, [0.0, dur - 1.0 / fps])
    diff = float(np.abs(first - last).mean())
    check("loop_seam", diff < 0.02, "mean |last - first| = %.4f" % diff)
    res["pass"] = ok_all
    out = os.path.join(os.path.dirname(path), "verify_report.json")
    json.dump(res, open(out, "w"), indent=2, default=float)
    print("ALL PASS" if ok_all else "SOME CHECKS FAILED", "->", out)
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
