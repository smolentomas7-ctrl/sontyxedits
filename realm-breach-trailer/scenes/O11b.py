"""O11b — The charge: low fast dolly beside him, 24 mm, speed ramp 0.5x -> 1.5x, whip into the clash."""
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

shot = rb_shot.Shot("O11b", key_frame=716)
S = rb_intro.build(shot, variant="duel")
import rb_env_arena as AR  # noqa: E402

cam = rb_cam.Rig(lens=24, fstop=4.0)
cam.whip(shot.f1 - 3, shot.f1 + 4, -35)


def cam_fn(f):
    p = rb_intro.warrior_pos(f)
    loc = p + Vector((-1.7, 0.7, 0.45))
    return dict(loc=loc, target=p + Vector((0.2, 2.6, 1.15)), focus=p + Vector((0, 0, 1.0)))


cam.key_range(shot.frames_all, cam_fn)
L = AR.lights_duel(warrior=tuple(rb_intro.warrior_pos(shot.key_frame)), cam=tuple(cam_fn(shot.key_frame)["loc"]))
for k in ("rim", "rim2", "bounce"):
    if k in L:
        C.parent_keep(L[k], S["w"].root)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
