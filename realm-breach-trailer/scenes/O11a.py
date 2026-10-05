"""O11a — Close-up: the roar, "YOUR REIGN ENDS HERE!". Slight low angle, slow push, 50 mm."""
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

shot = rb_shot.Shot("O11a", key_frame=int(ST.bf(45.0)))
S = rb_intro.build(shot, variant="approach")
import rb_env_arena as AR  # noqa: E402

p = ST.STOP
cam = rb_cam.Rig(lens=35, fstop=4.0)


def cam_fn(f):
    # low angle from the front, knees up: the head thrown back in the roar and the low-guard blade (flaring) both
    # in frame; slow push
    u = C.ease_in_out(shot.u(f))
    loc = p + Vector((0.55, 2.15 - 0.3 * u, 0.85))
    return dict(loc=loc, target=p + Vector((0.0, 0.0, 1.38)), focus=p + Vector((0, 0.15, 1.5)))


cam.key_range(shot.frames_all, cam_fn)
cam.shake(int(ST.bf(44.0)) - 1, amp=0.012, seed=shot.seed)
AR.lights_walk(warrior=tuple(p), cam=tuple(cam_fn(shot.key_frame)["loc"]))
C.light("POINT", "O11a_ember_under", p + Vector((0.1, 0.95, 0.18)), color="#FF6A1A", energy=140, size=0.3,
        shadow=False, volume=0.1)
C.light("AREA", "O11a_bluefill", p + Vector((-1.0, 3.5, 2.6)), color="#6FA8FF", energy=50, size=1.6,
        target=p + Vector((0, 0, 1.6)), shadow=False)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
