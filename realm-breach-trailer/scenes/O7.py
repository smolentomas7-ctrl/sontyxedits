"""O7 — The Fallen God tilts his head. Low angle, slow 5% push-in, 35 mm. Silence."""
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

shot = rb_shot.Shot("O7", key_frame=385)
S = rb_intro.build(shot, variant="approach", warrior=True)
import rb_env_arena as AR  # noqa: E402

god = ST.GOD_POS
cam = rb_cam.Rig(lens=35, fstop=5.6)


def cam_fn(f):
    u = C.ease_in_out(shot.u(f))
    loc = Vector((0.9, 3.2 + 0.5 * u, 0.9))
    return dict(loc=loc, target=god + Vector((0, 0, 4.3)), focus=god + Vector((0, -0.3, 5.0)))


cam.key_range(shot.frames_all, cam_fn)
AR.lights_god_reveal(cam=tuple(cam_fn(shot.key_frame)["loc"]))
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
