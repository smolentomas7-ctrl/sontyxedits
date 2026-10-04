"""M507 — A fireball detonates on the evil. Low 24 mm near the impact."""
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

shot = rb_shot.Shot("M507", key_frame=1257)
D, w = MT.scene(shot, "legend", look="late")
F_HIT = int(round(MT.ST.bf(83.25))) - 1
P = Vector((0, -2.6, 0))
MT.act(w, shot, "cast", F_HIT - 6, 12, P, 180)
palm = MT.joint_world(w, MT.act_pose(w, "cast", F_HIT - 6, F_HIT - 6, 12, P, 180), "fingers_L")
ev = MT.enemy("evil", "EV1_", seed=shot.seed)
EVP = Vector((0.1, 1.2, 0))
MT.enemy_act(ev, shot, "hit", F_HIT, 8, EVP, 0)
EN.dissolve(ev, F_HIT + 1, frames=8, mode="ash")
cam = rb_cam.Rig(lens=24, fstop=5.6)
cam.shake(F_HIT, amp=0.07, seed=shot.seed)
LOC = Vector((1.7, -0.9, 0.45))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((0.0, 1.0, 1.5)), focus=2.6))
MT.light(shot, "legend", D, EVP, LOC)
MT.fx("fireball", F_HIT - 6, tuple(palm), (0.1, 1.15, 1.5), seed=shot.seed, travel=6)
shot.render()
