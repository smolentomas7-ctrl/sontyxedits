"""M102 — The dark waterfall pouring into the black lake; the early-look warrior stands on the rocks
looking up at it (wide, slow lateral drift)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_env_forest as FO  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402
import rb_warrior as RW  # noqa: E402

shot = rb_shot.Shot("M102", key_frame=778)
F = FO.build_forest("waterfall", seed=101)
mk = F.marks
w = RW.build_warrior("early")
W = Vector(mk["warrior"])
MT.stand(w, shot, W, mk["heading"], look_up=10.0, stance=0.25)
cam = rb_cam.Rig(lens=35, fstop=5.6)
CAM, AIM = Vector(mk["cam"]), Vector(mk["aim"])


def cam_fn(f):
    u = shot.u(f)
    loc = CAM + Vector((-0.6 * u, 0.25 * u, -0.05 * u))     # slow drift left, toward the falls
    return dict(loc=loc, target=AIM + Vector((-0.25 * u, 0, 0.1 * u)), focus=W + Vector((0, 0, 1.2)))


cam.key_range(shot.frames_all, cam_fn)
cam.handheld(amp=0.003, rot_deg=0.12, freq=0.6, seed=shot.seed)
shot.scene.frame_set(shot.key_frame)
FO.lights_forest("waterfall", F, warrior=W, cam=cam_fn(shot.key_frame)["loc"], follow=w.root)
shot.render()
