"""M101 — Phase 1 opens: the haunted forest under the moon, the early-look warrior small in frame,
walking away from us between the dead trees (wide observational, slow drift; punch-in added in the edit)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_env_forest as FO  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402
import rb_warrior as RW  # noqa: E402

shot = rb_shot.Shot("M101", key_frame=763)
F = FO.build_forest("trees", seed=101)
mk = F.marks
w = RW.build_warrior("early")
MT.walk(w, shot, mk["warrior"], mk["heading"], ground=F.ground_z)
W = Vector(mk["warrior"])
cam = rb_cam.Rig(lens=35, fstop=5.6)
CAM, AIM = Vector(mk["cam"]), Vector(mk["aim"])


def cam_fn(f):
    u = shot.u(f)
    loc = CAM + Vector((0.35 * u, 0.55 * u, 0.06 * u))      # slow drift in and across
    return dict(loc=loc, target=AIM + Vector((0.12 * u, 0, 0)), focus=W + Vector((0, 0, 1.2)))


cam.key_range(shot.frames_all, cam_fn)
cam.handheld(amp=0.004, rot_deg=0.15, freq=0.7, seed=shot.seed)
shot.scene.frame_set(shot.key_frame)
FO.lights_forest("trees", F, warrior=W, cam=cam_fn(shot.key_frame)["loc"], follow=w.root)
shot.render()
