"""STEP 8 — Render orchestration.

python3 src/render_shots.py --mode still|preview|final [--shots O2,O5,...] [--workers 2] [--chunk 24]
                            [--scale S] [--samples N] [--force]

* Every shot with a script scenes/<ID>.py is rendered (shots without a script —
  O1, E1, END — are pure 2D and built in src/edit.py).
* still   : one key frame per shot (build/stills/<ID>/).
* preview : 50% resolution, the frames the edit uses ± --handles (default 1) (build/shots/<ID>/preview/).
* final   : 0.75 scale (810x1440), 8 spp, light volumetrics; upscaled to 1080x1920 in the edit (build/shots/<ID>/final/).
* Shots are split into frame-range chunks distributed over N parallel Blender
  workers; cloth/particle shots re-step their simulation from the shot's sim start
  inside each chunk, so chunks are independent and deterministic. Already-rendered
  frames are skipped (resumable); --force re-renders.
"""
import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "config"))
import video  # noqa: E402

BLENDER = ["xvfb-run", "-a", "-s", "-screen 0 1920x1080x24", "blender", "-b", "--factory-startup", "-P"]


# preview is for motion/staging review: 4 spp, hard 512 px shadows and lighter volumetrics render ~1.8x faster than
# 6 spp soft shadows at a near-identical image (benchmarked on O5: 6.5 s vs 11.5 s per frame on one worker).
PROFILES = {
    "preview": dict(scale="0.5", samples="4", vol_tile="16", vol_samples="16", soft_shadows="0", shadow_cube="512"),
    "final": dict(scale="0.75", samples="8", vol_tile="16", vol_samples="32"),
}
QUALITY_KEYS = ("vol_tile", "vol_samples", "soft_shadows", "shadow_cube", "shadow_cascade", "gtao", "ssr")


def jobs_for(shot, mode, chunk, handles=1):
    # the edit only reads [start, end) (M509's strobe reads inside its sources), so renders need ~no handles
    h = handles
    a, b = shot["start_frame"] - h, shot["end_frame"] + h
    if mode == "still":
        return [(shot["id"], None, None)]
    out = []
    k = a
    while k < b:
        out.append((shot["id"], k, min(b, k + chunk)))
        k += chunk
    return out


def frames_done(sid, mode, lo, hi):
    d = os.path.join(ROOT, "build", "shots", sid, mode)
    return all(os.path.exists(os.path.join(d, "f_%04d.png" % f)) for f in range(lo, hi))


def run(job, mode, extra, force, threads=None):
    sid, lo, hi = job
    script = os.path.join(ROOT, "scenes", "%s.py" % sid)
    if mode != "still" and not force and frames_done(sid, mode, lo, hi):
        return sid, lo, hi, "skip", 0.0
    args = ["--mode", mode] + extra
    if lo is not None:
        args += ["--range", str(lo), str(hi)]
    if force:
        args += ["--force"]
    log_dir = os.path.join(ROOT, "build", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log = os.path.join(log_dir, "%s_%s_%s.log" % (sid, mode, lo if lo is not None else "still"))
    t = time.time()
    env = dict(os.environ)
    if threads:
        # llvmpipe rasterises on every core by default: two full-width workers contend and are slower than one;
        # two workers at half width overlap one's scene build / cloth pre-roll with the other's rendering
        env["LP_NUM_THREADS"] = str(threads)
    with open(log, "w") as fh:
        p = subprocess.run(BLENDER + [script, "--"] + args, stdout=fh, stderr=subprocess.STDOUT, cwd=ROOT, env=env)
    dt = time.time() - t
    ok = p.returncode == 0 and "Traceback" not in open(log).read()
    return sid, lo, hi, "ok" if ok else "FAIL (%s)" % log, dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="still", choices=["still", "preview", "final"])
    ap.add_argument("--shots")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--chunk", type=int, default=24)
    ap.add_argument("--scale")
    ap.add_argument("--samples")
    ap.add_argument("--frame")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--handles", type=int, default=1, help="extra frames rendered each side (max %d)" % video.HANDLE_FRAMES)
    ap.add_argument("--threads", type=int, help="llvmpipe threads per worker (default: CPUs // workers)")
    a = ap.parse_args()
    tl = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
    want = set(a.shots.split(",")) if a.shots else None
    shots = [s for s in tl["shots"] if os.path.exists(os.path.join(ROOT, "scenes", "%s.py" % s["id"]))
             and (want is None or s["id"] in want)]
    # render profiles (benchmarked on F3: the final profile is ~3x faster than 1.0x/12 spp and visually equal after
    # the editor's Lanczos upscale to 1080x1920 + grain). CLI --scale/--samples override.
    prof = PROFILES.get(a.mode, {})
    extra = []
    extra += ["--scale", a.scale or prof.get("scale")] if (a.scale or prof.get("scale")) else []
    extra += ["--samples", a.samples or prof.get("samples")] if (a.samples or prof.get("samples")) else []
    for k in QUALITY_KEYS:
        if k in prof:
            extra += ["--" + k, prof[k]]
    threads = a.threads or max(1, (os.cpu_count() or 4) // max(1, a.workers))
    if a.frame:
        extra += ["--frame", a.frame]
    jobs = [j for s in shots for j in jobs_for(s, a.mode, a.chunk, min(a.handles, video.HANDLE_FRAMES))]
    print("%d shots, %d jobs, %d workers x %d threads, mode %s %s" % (len(shots), len(jobs), a.workers, threads, a.mode,
                                                                     " ".join(extra)), flush=True)
    t0 = time.time()
    fails = []
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(run, j, a.mode, extra, a.force, threads) for j in jobs]
        for i, fu in enumerate(cf.as_completed(futs)):
            sid, lo, hi, st, dt = fu.result()
            if st.startswith("FAIL"):
                fails.append((sid, lo, hi, st))
            print("[%3d/%3d] %-6s %s-%s %-6s %6.1fs  (elapsed %.0fs)" % (i + 1, len(jobs), sid, lo, hi, st[:4], dt,
                                                                       time.time() - t0), flush=True)
    print("done in %.0fs, %d failures" % (time.time() - t0, len(fails)))
    for f in fails:
        print("  ", f)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
