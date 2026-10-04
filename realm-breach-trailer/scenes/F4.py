"""F4 — He slowly rises, gripping the greatsword. Mid shot, 50 mm; the ember rim returns. (VO7)"""
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

shot = rb_shot.Shot("F4", key_frame=1775)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


r = Vector(ST._RISE)
cam = rb_cam.Rig(lens=50, fstop=2.8)


def cam_fn(f):
    u = C.ease_in_out(shot.u(f))
    return dict(loc=r + Vector((0.9, 3.0, 0.75 + 0.45 * u)), target=r + Vector((0, 0, 0.9 + 0.55 * u)),
                focus=r + Vector((0, 0.2, 1.2)))


cam.key_range(shot.frames_all, cam_fn)
AR.lights_walk(warrior=tuple(r), cam=tuple(cam_fn(shot.key_frame)["loc"]))
C.light("AREA", "F4_blue", r + Vector((-1.0, 5.0, 3.0)), color="#6FA8FF", energy=90, size=2.5,
        target=r + Vector((0, 0, 1.2)), shadow=False)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
