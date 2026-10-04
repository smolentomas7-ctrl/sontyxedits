"""M404 — Q, Fireball: orange-red fire erupts from his left palm and roars off to camera right. Orbit 20 deg,
50 mm."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M404", key_frame=1156)
D, w = MT.scene(shot, "legend", look="late")
F_CAST = MT.imp(76.5)
P = Vector((0, 0, 0))
MT.act(w, shot, "cast", F_CAST, 14, P, 200)
palm = MT.joint_world(w, MT.act_pose(w, "cast", F_CAST, F_CAST, 14, P, 200), "fingers_L")
cam = rb_cam.Rig(lens=50, fstop=4.0)
cam.shake(F_CAST + 1, amp=0.02, seed=shot.seed)


def cam_fn(f):
    a = math.radians(-35 + 20 * C.ease_in_out(shot.u(f)))
    loc = Vector((3.6 * math.sin(a), 3.6 * math.cos(a), 1.45))
    return dict(loc=loc, target=Vector((0.15, 0.4, 1.35)), focus=palm)


cam.key_range(shot.frames_all, cam_fn)
MT.light(shot, "legend", D, P, cam_fn(shot.key_frame)["loc"], follow=w.root)
MT.fx("fireball", F_CAST, tuple(palm), (3.2, 6.5, 1.4), seed=shot.seed, travel=8)
MT.fx("embers", shot.sim_start, shot.render_end, (0, 0.5, 1.5), radius=3.0, seed=shot.seed + 1)
shot.render()
