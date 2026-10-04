"""M104 — Tracking from behind: the early-look warrior walks into the burning Hellgate; the camera
pushes after him and whips (accelerating yaw, motion blur) through the portal into M105."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Matrix, Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_env_forest as FO  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402
import rb_warrior as RW  # noqa: E402

shot = rb_shot.Shot("M104", key_frame=806)
F = FO.build_forest("hellgate", seed=101)
mk = F.marks
w = RW.build_warrior("early")
at = MT.walk(w, shot, mk["warrior"], mk["heading"], ground=F.ground_z)
W = Vector(mk["warrior"])
GATE = Vector(mk["gate"])
cam = rb_cam.Rig(lens=35, fstop=5.6)
CAM, AIM = Vector(mk["cam"]), Vector(mk["aim"])
WHIP0 = shot.f1 - 6


def cam_fn(f):
    u = shot.u(f)
    root = at(f)[0]
    # tracking from behind, closing the gap (push) faster than he walks
    loc = CAM.lerp(Vector((root.x + 0.25, root.y - 4.2, 1.55)), C.ease_in(C.clamp01(u)) * 0.55)
    loc.y = max(loc.y, CAM.y + (root.y - W.y))
    tgt = AIM + Vector((0, 0, -0.15 * u))
    yaw = 0.0
    if f > WHIP0:
        k = (f - WHIP0) / (shot.f1 + 2 - WHIP0)
        yaw = -80.0 * k * k                                   # whip right, accelerating into the cut
    d = Matrix.Rotation(math.radians(yaw), 3, "Z") @ (tgt - loc)
    return dict(loc=loc, target=loc + d, focus=root + Vector((0, 0, 1.2)))


cam.key_range(shot.frames_all, cam_fn)
cam.handheld(amp=0.005, rot_deg=0.2, freq=1.0, seed=shot.seed)
F.key_ctrl("portal", shot.sim_start, 1.0)
F.key_ctrl("portal", shot.f1, 1.6)
F.key_ctrl("heat", shot.sim_start, 1.0)
shot.scene.frame_set(shot.key_frame)
FO.lights_forest("hellgate", F, warrior=W, cam=cam_fn(shot.key_frame)["loc"], follow=w.root)
shot.render()
