"""M207 — The evil bursts into dark smoke after his cut (cleave follow-through). Mid 35 mm. FLOOR 500."""
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

shot = rb_shot.Shot("M207", key_frame=948)
D, w = MT.scene(shot, "struggle", look="mid")
F_HIT = shot.f0
P = Vector((0, 0, 0))
MT.act(w, shot, "cleave", F_HIT, 14, P, 180)
ev = MT.enemy("evil", "EV1_", seed=shot.seed)
MT.enemy_act(ev, shot, "hit", F_HIT, 10, (0.05, 1.6, 0), 0)
EN.dissolve(ev, F_HIT + 1, frames=8, mode="smoke")
cam = rb_cam.Rig(lens=35, fstop=4.0)
cam.shake(F_HIT, amp=0.03, seed=shot.seed)
LOC = Vector((1.45, -2.35, 1.6))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((0.0, 1.3, 1.5)), focus=3.3))
MT.light(shot, "struggle", D, P, LOC, follow=w.root)
MT.fx("smoke_burst", F_HIT + 1, (0.05, 1.6, 1.4), seed=shot.seed, scale=1.2)
MT.fx("sparks", F_HIT, (0.05, 1.2, 1.3), seed=shot.seed + 1, color="#C58BFF")
shot.render()
