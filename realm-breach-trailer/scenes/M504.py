"""M504 — A bad angel is cut out of the air by a rising slash; black feathers and red sparks. Wide 24 mm,
low side."""
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

shot = rb_shot.Shot("M504", key_frame=1234)
D, w = MT.scene(shot, "legend", look="late")
F_HIT = int(round(MT.ST.bf(81.75))) - 1
P = Vector((0, 0, 0))
MT.act(w, shot, "slash", F_HIT, 12, P, 180)
an = MT.enemy("bad_angel", "BA1_", seed=shot.seed)
MT.enemy_act(an, shot, "hit", F_HIT, 8, (0.1, 1.5, 1.4), 0)
MT.enemy_path(an, shot, lambda f: Vector((0.6, 3.0, 3.2)).lerp(Vector((0.1, 1.5, 1.4)), C.ease_out(C.clamp01((f - shot.f0 + 6) / float(F_HIT - shot.f0 + 6)))))
EN.dissolve(an, F_HIT + 1, frames=7, mode="ash")
cam = rb_cam.Rig(lens=24, fstop=5.6)
cam.shake(F_HIT, amp=0.05, seed=shot.seed)
LOC = Vector((-2.6, -1.2, 0.6))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((0.0, 1.0, 1.7)), focus=3.2))
MT.light(shot, "legend", D, P, LOC, follow=w.root)
MT.fx("sparks", F_HIT, (0.1, 1.4, 1.6), seed=shot.seed, color="#FF4A3A", scale=1.2)
MT.fx("ash", F_HIT - 2, shot.render_end, (0.1, 1.5, 1.6), radius=1.2, height=1.5, count=140, seed=shot.seed + 1, color=(0.05, 0.05, 0.05))
shot.render()
