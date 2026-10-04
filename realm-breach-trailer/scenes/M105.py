"""M105 — Floor 1 (cold, grey): his first skeleton fight. Short-sword slash into the skeleton's raised rusted
blade, sparks. Wide 35 mm, handheld; the first frames finish M104's whip pan."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M105", key_frame=824)
D, w = MT.scene(shot, "floor1", look="early")
F_HIT = MT.imp(54.5)
P = Vector((0, 0, 0))
MT.act(w, shot, "short_slash", F_HIT, 16, P, 180)
sk = MT.enemy("skeleton", "SK1_", seed=shot.seed)
SK = Vector((0.15, 1.35, 0))
MT.enemy_act(sk, shot, "block", F_HIT, 14, SK, 0)
cam = rb_cam.Rig(lens=35, fstop=4.0)
cam.handheld(amp=0.012, rot_deg=0.35, freq=1.3, seed=shot.seed)
cam.shake(F_HIT, amp=0.025, seed=shot.seed)
LOC, TGT = Vector((1.3, -3.0, 1.9)), Vector((0.05, 0.9, 1.15))


def cam_fn(f):
    return dict(loc=LOC, target=MT.rot_target(LOC, TGT, MT.whip_in(f, shot.f0, 4, 55.0)), focus=3.4)


cam.key_range(shot.frames_all, cam_fn)
MT.light(shot, "floor1", D, P, LOC, follow=w.root)
MT.fx("sparks", F_HIT, (0.05, 0.95, 1.45), seed=shot.seed, direction=(0.6, -0.8, 0.5))
MT.fx("dust_puff", F_HIT - 3, (0.15, -0.3, 0.0), seed=shot.seed + 1, scale=0.7)
MT.fx("ash", shot.sim_start, shot.render_end, (0, 0.5, 1.5), radius=4.0, seed=shot.seed)
shot.render()
