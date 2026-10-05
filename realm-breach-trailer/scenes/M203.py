"""M203 — The horned evil looms; he drives the greatsword into its chest (thrust). Over the evil's shoulder
onto his helm and blade, 35 mm. FLOOR 100 in the edit."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M203", key_frame=900)
D, w = MT.scene(shot, "struggle", look="mid")
F_HIT = MT.imp(59.5)
P = Vector((0, 0, 0))
MT.act(w, shot, "thrust", F_HIT, 14, P, 180)
ev = MT.enemy("evil", "EV1_", seed=shot.seed)
EV = Vector((0.1, 1.75, 0))
MT.enemy_act(ev, shot, "hit", F_HIT, 12, EV, 0)
cam = rb_cam.Rig(lens=35, fstop=4.0)
cam.handheld(amp=0.01, rot_deg=0.3, freq=1.2, seed=shot.seed)
cam.shake(F_HIT, amp=0.03, seed=shot.seed)
LOC = Vector((1.3, 4.7, 2.55))      # far enough that the evil reads as a horned silhouette, not a purple mass
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC + Vector((0, -0.2, 0)) * shot.u(f),
                                              target=Vector((0.0, 0.3, 1.45)), focus=3.7))
MT.light(shot, "struggle", D, P, LOC, follow=w.root)
MT.fx("sparks", F_HIT, (0.05, 1.45, 1.45), seed=shot.seed, color="#C58BFF", direction=(0, -1, 0.4))
MT.fx("smoke_burst", F_HIT, (0.1, 1.6, 1.5), seed=shot.seed, scale=0.5)
shot.render()
