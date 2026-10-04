"""CHECKPOINT 2 — one graded vertical key still per shot, tiled in shot order.

python3 src/checkpoint2.py [--safe] [--out assets/checkpoint2]

Uses each shot's rendered key still (build/stills/<ID>/<ID>_fNNNN.png; 2D shots use their middle
frame) run through src/edit.py (grade, text, subtitles exactly as in the edit), then writes
contact sheets per act plus one overview sheet. Shots with no still yet show as slates and are
listed as MISSING.
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from contact_sheet import sheet  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--safe", action="store_true")
ap.add_argument("--out", default=os.path.join(ROOT, "assets", "checkpoint2"))
a = ap.parse_args()

tl = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
keys, missing = [], []
for s in tl["shots"]:
    sid = s["id"]
    sd = os.path.join(ROOT, "build", "stills", sid)
    f = None
    if os.path.isdir(sd):
        for x in sorted(os.listdir(sd)):
            m = re.match(r".*_f(\d+)\.png$", x)
            if m:
                f = int(m.group(1))
                break
    if f is None:
        f = s.get("text_frame", (s["start_frame"] + s["end_frame"]) // 2)
        if os.path.exists(os.path.join(ROOT, "scenes", sid + ".py")):
            missing.append(sid)
    f = min(max(f, s["start_frame"]), s["end_frame"] - 1)
    keys.append((s, f))

cmd = [sys.executable, os.path.join(ROOT, "src", "edit.py"), "--mode", "animatic", "--stills",
       ",".join(str(f) for _, f in keys)]
if a.safe:
    cmd.append("--safe")
subprocess.run(cmd, check=True)
os.makedirs(a.out, exist_ok=True)
items_by_act = {}
for s, f in keys:
    p = os.path.join(ROOT, "build", "preview", "frame_%04d.png" % f)
    label = "%s %.2fs" % (s["id"], s["start"])
    items_by_act.setdefault(s["act"], []).append((label, p))
suffix = "_safe" if a.safe else ""
for act, items in items_by_act.items():
    sheet(os.path.join(a.out, "act_%s%s.jpg" % (act, suffix)), 6 if len(items) > 8 else len(items), items,
          tile_w=300, title="REALM BREACH  CHECKPOINT 2  ACT %s" % act)
allitems = [it for its in items_by_act.values() for it in its]
sheet(os.path.join(a.out, "all_shots%s.jpg" % suffix), 12, allitems, tile_w=180,
      title="REALM BREACH  CHECKPOINT 2  ALL %d SHOTS IN ORDER" % len(allitems))
print("MISSING stills:", missing)
