"""M505 — The biggest God Attack: a pillar of gold light erupts up from him. Wide, low 24 mm."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M505", key_frame=1242)
D, w = MT.scene(shot, "legend", look="late")
F_HIT = shot.f0 + 2
P = Vector((0, 0, 0))
MT.act(w, shot, "god_attack", F_HIT, 14, P, 180)
cam = rb_cam.Rig(lens=24, fstop=8.0)
cam.shake(F_HIT, amp=0.08, seed=shot.seed)
LOC = Vector((1.6, -4.0, 0.35))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((0.0, 0.0, 2.6)), focus=4.2))
MT.light(shot, "legend", D, P, LOC, follow=w.root)
# the column rises just behind him (away from the lens) so he stands as a silhouette against the light
MT.fx("god_attack", F_HIT, (0.15, 0.85, 0.1), (0.15, 0.85, 30.0), seed=shot.seed, column=True, scale=1.3, strength=0.4)
MT.fx("shockwave", F_HIT, (0.15, 0.85, 0.02), seed=shot.seed + 1, scale=1.4)
MT.fx("debris", F_HIT, (0.0, 0.0, 0.1), seed=shot.seed + 2, scale=1.3)
shot.render()
