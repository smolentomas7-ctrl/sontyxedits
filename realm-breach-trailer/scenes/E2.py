"""E2 — Fallen God defeated, halo shattered on the floor; the warrior stands exhausted, embers drifting down. Slow crane-down, 35 mm."""
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

shot = rb_shot.Shot("E2", key_frame=1990)
S = rb_intro.build(shot, variant="after", act="after")
import rb_env_arena as AR  # noqa: E402


r = Vector(ST._RISE)
cam = rb_cam.Rig(lens=35, fstop=8.0)


def cam_fn(f):
    # crane down on the line through both: the exhausted warrior lower centre (back to us), the kneeling god
    # behind and above him (stacked for the vertical frame)
    u = C.ease_out(shot.u(f))
    loc = Vector((-0.6, 0.6, 5.0 - 3.0 * u))
    return dict(loc=loc, target=Vector((-0.1, 8.6, 0.5 + 0.2 * u)), focus=4.6)


cam.key_range(shot.frames_all, cam_fn)
AR.lights_after(warrior=tuple(r), cam=tuple(cam_fn(shot.key_frame)["loc"]))
try:
    import rb_vfx as VFX
    VFX.embers(shot.sim_start, shot.render_end, center=tuple(r + Vector((0, 2, 3))), seed=shot.seed, falling=True)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
