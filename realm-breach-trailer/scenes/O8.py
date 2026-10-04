"""O8 — He slowly raises the greatsword; the blade crack glows faintly. Mid shot, 15% push-in, 50 mm. (VO2)"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_intro  # noqa: E402
import rb_shot  # noqa: E402
import rb_story as ST  # noqa: E402

shot = rb_shot.Shot("O8", key_frame=int(ST.bf(33.5)))
S = rb_intro.build(shot, variant="approach")
import rb_env_arena as AR  # noqa: E402

p = ST.STOP
cam = rb_cam.Rig(lens=50, fstop=2.8)


def cam_fn(f):
    u = C.ease_in_out(shot.u(f))
    d = 2.9 - 0.45 * u
    loc = p + Vector((0.55, d, 1.15))
    return dict(loc=loc, target=p + Vector((0.0, 0, 1.35)), focus=p + Vector((0, -0.2, 1.4)))


cam.key_range(shot.frames_all, cam_fn)
L = AR.lights_walk(warrior=tuple(p), cam=tuple(cam_fn(shot.key_frame)["loc"]))
C.light("AREA", "O8_bluefill", p + Vector((-1.5, 4.0, 2.5)), color="#6FA8FF", energy=60, size=2.0,
        target=p + Vector((0, 0, 1.3)), shadow=False)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
