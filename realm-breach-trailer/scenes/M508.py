"""M508 — A great arc of the greatsword with an ember trail. Fast 24 mm."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M508", key_frame=1264)
D, w = MT.scene(shot, "legend", look="late")
F_HIT = int(round(MT.ST.bf(83.75))) - 1
P = Vector((0, 0, 0))
MT.act(w, shot, "slash", F_HIT, 12, P, 180, crack=6.0)
tip = MT.tip_empty(w)
cam = rb_cam.Rig(lens=24, fstop=5.6)
cam.shake(F_HIT, amp=0.04, seed=shot.seed)
LOC = Vector((-0.4, 2.9, 1.3))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((0.0, 0.0, 1.35)), focus=2.9))
MT.light(shot, "legend", D, P, LOC, follow=w.root)
MT.fx("ember_trail", tip, F_HIT - 8, shot.render_end, seed=shot.seed)
MT.fx("embers", shot.sim_start, shot.render_end, (0, 0.5, 1.4), radius=2.5, seed=shot.seed + 1, cam=cam.cam)
shot.render()
