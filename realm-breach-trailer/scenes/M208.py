"""M208 — Close on his left pauldron: a skeleton's blade glances off it; sparks spray. 50 mm."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M208", key_frame=957)   # just after the glancing hit (956): sparks in frame
D, w = MT.scene(shot, "struggle", look="mid")
F_HIT = int(round(MT.ST.bf(63.25))) - 1
P = Vector((0, 0, 0))
MT.act(w, shot, "hit_react", F_HIT, 10, P, 180)
sk = MT.enemy("skeleton", "SK1_", seed=shot.seed)
MT.enemy_act(sk, shot, "attack", F_HIT, 10, (-0.55, 1.1, 0), 25)
cam = rb_cam.Rig(lens=50, fstop=2.8)
cam.shake(F_HIT, amp=0.02, seed=shot.seed)
LOC = Vector((-1.05, -0.85, 1.72))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((-0.24, 0.05, 1.5)), focus=1.2))
MT.light(shot, "struggle", D, P, LOC, follow=w.root)
MT.fx("sparks", F_HIT, (-0.3, 0.05, 1.6), seed=shot.seed, scale=1.3, direction=(-1.0, -0.5, 0.6))
shot.render()
