"""M502 — He cleaves the morbidious: a green burst and sparks. Fast 24 mm from the side."""
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

shot = rb_shot.Shot("M502", key_frame=1219)
D, w = MT.scene(shot, "legend", look="late")
F_HIT = int(round(MT.ST.bf(80.75))) - 1
P = Vector((0, 0, 0))
MT.act(w, shot, "cleave", F_HIT, 12, P, 180)
mb = MT.enemy("morbidious", "MB1_", seed=shot.seed)
MT.enemy_act(mb, shot, "hit", F_HIT, 8, (0.0, 1.45, 0.0), 0)
EN.dissolve(mb, F_HIT + 1, frames=6, mode="shatter")
cam = rb_cam.Rig(lens=24, fstop=5.6)
cam.shake(F_HIT, amp=0.05, seed=shot.seed)
LOC = Vector((-2.4, 0.2, 1.1))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((0.0, 0.85, 1.35)), focus=2.5))
MT.light(shot, "legend", D, (0, 0.6, 0), LOC, follow=w.root)
MT.fx("smoke_burst", F_HIT + 1, (0.0, 1.45, 1.1), seed=shot.seed, color="#0D1A08", glow="#6BFF4A", scale=1.1)
MT.fx("sparks", F_HIT, (0.0, 1.0, 1.0), seed=shot.seed + 1, scale=1.2)
shot.render()
