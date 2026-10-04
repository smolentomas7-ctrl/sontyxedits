"""M206 — Close: the greatsword slashes through a skeleton's ribs; bones fly. 35 mm side-on."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M206", key_frame=941)
D, w = MT.scene(shot, "struggle", look="mid")
F_HIT = int(round(MT.ST.bf(62.25))) - 1
P = Vector((0, 0, 0))
MT.act(w, shot, "slash", F_HIT, 12, P, 180)
sk = MT.enemy("skeleton", "SK1_", seed=shot.seed)
MT.enemy_act(sk, shot, "hit", F_HIT, 10, (0.15, 1.3, 0), 0)
import rb_enemies as EN  # noqa: E402
EN.dissolve(sk, F_HIT + 1, frames=6, mode="shatter")
cam = rb_cam.Rig(lens=35, fstop=4.0)
cam.shake(F_HIT, amp=0.03, seed=shot.seed)
LOC = Vector((-1.25, 0.35, 1.4))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((0.1, 1.05, 1.2)), focus=1.6))
MT.light(shot, "struggle", D, P, LOC, follow=w.root)
MT.fx("debris", F_HIT, (0.15, 1.25, 1.25), seed=shot.seed, kind="bone", scale=0.8)
MT.fx("sparks", F_HIT, (0.1, 1.2, 1.3), seed=shot.seed + 1, scale=0.8)
shot.render()
