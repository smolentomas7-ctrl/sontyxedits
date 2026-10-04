"""M506 — A lightning-wreathed slash through a crowd. Fast 24 mm."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

import rb_enemies as EN  # noqa: E402

shot = rb_shot.Shot("M506", key_frame=1249)
D, w = MT.scene(shot, "legend", look="late")
F_HIT = int(round(MT.ST.bf(82.75))) - 1
P = Vector((0, 0, 0))
MT.act(w, shot, "slash", F_HIT, 12, P, 180)
crowd = EN.crowd(["skeleton", "ghost"], 9, (0, 1.2, 0), 2.6, seed=shot.seed, face=(0, 0, 0), min_r=1.3)
tip = MT.tip_empty(w)
src = MT.world_at(tip, F_HIT)
targets = []
for k, m in enumerate(crowd[:5]):
    p = m.root.matrix_world.translation
    targets.append((p.x, p.y, p.z + 1.2))
cam = rb_cam.Rig(lens=24, fstop=5.6)
cam.shake(F_HIT, amp=0.05, seed=shot.seed)
LOC = Vector((1.8, -2.6, 1.3))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((-0.1, 1.2, 1.3)), focus=3.2))
MT.light(shot, "legend", D, P, LOC, follow=w.root)
MT.fx("lightning", F_HIT - 1, tuple(src), targets, seed=shot.seed, duration=7)
MT.fx("sparks", F_HIT, (0.0, 1.0, 1.3), seed=shot.seed + 1, color="#CFE6FF")
shot.render()
