"""O5 — The reveal. From the Fallen God's feet (0.3 m high, 4 m away) tilting up 70 deg over 3 s, decelerating at the
face; cracks ignite bottom->top, eyes last. 24 mm, deep focus."""
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

shot = rb_shot.Shot("O5", key_frame=236)
S = rb_intro.build(shot, variant="approach", warrior=False)
import rb_env_arena as AR  # noqa: E402

god = ST.GOD_POS
cam = rb_cam.Rig(lens=24, fstop=8.0)
loc = god + Vector((0.35, -4.0, 0.3))


def cam_fn(f):
    u = C.ease_out(shot.u(f) * 1.05)
    feet = god + Vector((0.0, -0.4, 0.35))
    face = god + Vector((0.0, -0.1, 4.15))
    return dict(loc=loc + Vector((0, 0.15 * u, 0.05 * u)), target=feet.lerp(face, u), focus=4.2)


cam.key_range(shot.frames_all, cam_fn)
AR.lights_god_reveal(cam=tuple(loc))
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
