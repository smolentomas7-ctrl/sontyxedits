"""O3 — Profile. Side tracking through the colonnade (foreground pillars for parallax), 50 mm, rim only."""
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

shot = rb_shot.Shot("O3", key_frame=106)
S = rb_intro.build(shot, variant="approach")
import rb_env_arena as AR  # noqa: E402

cam = rb_cam.Rig(lens=50, fstop=2.0)


def cam_fn(f):
    p = rb_intro.warrior_pos(f)
    loc = Vector((-8.6, p.y - 0.6 + 0.25 * shot.u(f), 1.05))
    return dict(loc=loc, target=p + Vector((0, 0.35, 1.1)), focus=p + Vector((0, 0, 1.2)))


cam.key_range(shot.frames_all, cam_fn)
mid = rb_intro.warrior_pos(shot.key_frame)
L = AR.lights_walk(warrior=tuple(mid), cam=tuple(cam_fn(shot.key_frame)["loc"]))
# silhouette: kill the front bounce, push a strong ember rim from the far side
if "bounce" in L:
    L["bounce"].data.energy = 0.0
C.light("SPOT", "O3_rim", mid + Vector((3.2, 1.2, 1.6)), color="#FF6A1A", energy=1400, size=0.4,
        target=mid + Vector((0, 0, 1.2)), spot_size=math.radians(35), shadow=False)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
