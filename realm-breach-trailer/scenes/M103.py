"""M103 — Wide low past the ranking boards (runic rows, a few glowing slots, a lantern): the early-look
warrior walks past them along the path (slow push, the camera pans a touch with him)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_env_forest as FO  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_motion as MO  # noqa: E402
import rb_shot  # noqa: E402
import rb_warrior as RW  # noqa: E402

shot = rb_shot.Shot("M103", key_frame=793)
F = FO.build_forest("boards", seed=101)
mk = F.marks
w = RW.build_warrior("early")
at = MT.walk(w, shot, mk["warrior"], mk["heading"], ground=F.ground_z)
W = Vector(mk["warrior"])
fwd = MO.heading_vec(mk["heading"])
cam = rb_cam.Rig(lens=35, fstop=5.6)
CAM, AIM = Vector(mk["cam"]), Vector(mk["aim"])


def cam_fn(f):
    u = shot.u(f)
    loc = CAM + Vector((0.25 * u, 0.5 * u, 0.04 * u))       # slow low push
    return dict(loc=loc, target=AIM + fwd * (0.35 * u), focus=at(f)[0] + Vector((0, 0, 1.0)))


cam.key_range(shot.frames_all, cam_fn)
cam.handheld(amp=0.003, rot_deg=0.12, freq=0.7, seed=shot.seed)
F.key_ctrl("glow", shot.sim_start, 1.0)
shot.scene.frame_set(shot.key_frame)
FO.lights_forest("boards", F, warrior=W, cam=cam_fn(shot.key_frame)["loc"], follow=w.root)
shot.render()
