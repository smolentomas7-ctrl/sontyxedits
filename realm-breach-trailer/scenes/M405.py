"""M405 — E, Lightning: white-blue forks tear from his blade through three skeletons. Push-in, 50 mm."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M405", key_frame=1171)
D, w = MT.scene(shot, "legend", look="late")
F_CAST = MT.imp(77.5)
P = Vector((0, 0, 0))
MT.act(w, shot, "cast", F_CAST, 14, P, 180)
tip = MT.tip_empty(w)
src = MT.world_at(tip, F_CAST)
targets = []
for k, (x, y, hd) in enumerate(((-1.7, 3.3, -25), (0.35, 4.0, 0), (2.0, 3.1, 30))):
    e = MT.enemy("skeleton", "SK%d_" % k, seed=shot.seed + k)
    MT.enemy_act(e, shot, "hit", F_CAST + 1, 10, (x, y, 0), hd)
    targets.append((x, y - 0.1, 1.25))
cam = rb_cam.Rig(lens=50, fstop=5.6)
cam.shake(F_CAST, amp=0.03, seed=shot.seed)
cam.key_range(shot.frames_all, lambda f: dict(loc=Vector((-1.0, -3.3, 1.75)).lerp(Vector((-0.8, -2.6, 1.7)), C.ease_in_out(shot.u(f))),
                                              target=Vector((0.2, 2.6, 1.35)), focus=4.5))
MT.light(shot, "legend", D, P, (-1.0, -3.3, 1.75), follow=w.root)
MT.fx("lightning", F_CAST, tuple(src), targets, seed=shot.seed, duration=9, strength=0.6)   # full strength washed the frame white
shot.render()
