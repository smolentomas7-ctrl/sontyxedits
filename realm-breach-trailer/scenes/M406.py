"""M406 — R, God Attack: a golden-white blast from his blade into the floor ahead (white flash in the edit).
Wide 24 mm."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M406", key_frame=1186)
D, w = MT.scene(shot, "legend", look="late")
F_HIT = MT.imp(78.5)
P = Vector((0, 0, 0))
MT.act(w, shot, "god_attack", F_HIT, 16, P, 180)
tip = MT.tip_empty(w)
src = MT.world_at(tip, F_HIT)
cam = rb_cam.Rig(lens=24, fstop=8.0)
cam.shake(F_HIT, amp=0.07, seed=shot.seed)
LOC = Vector((2.3, -3.5, 1.05))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((0.0, 1.2, 1.5)), focus=4.2))
MT.light(shot, "legend", D, P, LOC, follow=w.root)
MT.fx("god_attack", F_HIT, tuple(src), (0.0, 3.0, 0.0), seed=shot.seed)
MT.fx("shockwave", F_HIT + 1, (0.0, 3.0, 0.02), seed=shot.seed + 1, scale=1.2)
MT.fx("debris", F_HIT + 1, (0.0, 3.0, 0.05), seed=shot.seed + 2)
shot.render()
