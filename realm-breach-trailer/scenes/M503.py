"""M503 — Colossal boss kill: the skeleton king shatters into bone and armour. Low 24 mm."""
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

shot = rb_shot.Shot("M503", key_frame=1226)
D, w = MT.scene(shot, "legend", look="late")
F_HIT = shot.f0   # 0.65 f before beat 81 (f0 + 1 landed after it)
P = Vector((0, -0.4, 0))
MT.act(w, shot, "slash", F_HIT, 10, P, 180,
       crack=lambda f: 5.0 + 3.0 * max(0.0, 1 - abs(f - F_HIT) / 6.0))   # ignited blade (M407 -> M508), flares on the hit
kg = MT.enemy("skeleton_king", "KG1_", seed=shot.seed)
MT.enemy_act(kg, shot, "hit", F_HIT, 8, (0.0, 1.9, 0.0), 0)
EN.dissolve(kg, F_HIT + 1, frames=7, mode="shatter")
cam = rb_cam.Rig(lens=24, fstop=5.6)
cam.shake(F_HIT, amp=0.07, seed=shot.seed)
LOC = Vector((1.1, -2.6, 0.4))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((0.0, 1.6, 2.1)), focus=4.0))
MT.light(shot, "legend", D, P, LOC, follow=w.root)
MT.fx("debris", F_HIT + 1, (0.0, 1.9, 1.9), seed=shot.seed, kind="bone", scale=1.8)
MT.fx("debris", F_HIT + 1, (0.0, 1.9, 1.2), seed=shot.seed + 1, kind="rock", scale=1.2)
MT.fx("shockwave", F_HIT + 1, (0.0, 1.9, 0.02), seed=shot.seed + 2, scale=0.8)
shot.render()
