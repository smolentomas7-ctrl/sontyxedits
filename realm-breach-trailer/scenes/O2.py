"""O2 — The walk. Tracking from behind, 0.6 m high, 4.5 m back, tilted up into the vast hall so the warrior is
small in the lower centre third; matched to walk speed, 10% push-in, 35 mm."""
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

shot = rb_shot.Shot("O2", key_frame=62)
S = rb_intro.build(shot, variant="approach")
import rb_env_arena as AR  # noqa: E402

cam = rb_cam.Rig(lens=35, fstop=4.0)
cam.handheld(amp=0.004, rot_deg=0.15, freq=0.6, seed=shot.seed)


def cam_fn(f):
    p = rb_intro.warrior_pos(f)
    u = shot.u(f)
    back = 4.5 - 0.45 * C.ease_in_out(u)
    loc = p + Vector((0.18, -back, 0.6))
    tgt = p + Vector((0.0, 7.0, 3.6))
    return dict(loc=loc, target=tgt, focus=p + Vector((0, 0, 1.2)))


cam.key_range(shot.frames_all, cam_fn)
mid = rb_intro.warrior_pos(shot.key_frame)
L = AR.lights_walk(warrior=tuple(mid), cam=tuple(cam_fn(shot.key_frame)["loc"]))
for k in ("rim", "rim2", "bounce"):
    if k in L:
        C.parent_keep(L[k], S["w"].root)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
