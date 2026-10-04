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
    # inside the nave, 3 m to his right, tracking at his pace: a clean profile (he faces frame left)
    p = rb_intro.warrior_pos(f)
    loc = Vector((-3.0, p.y + 0.05 * shot.u(f), 1.05))
    return dict(loc=loc, target=Vector((0.0, p.y, 1.12)), focus=p + Vector((0, 0, 1.2)))


cam.key_range(shot.frames_all, cam_fn)
mid = rb_intro.warrior_pos(shot.key_frame)
# foreground parallax: an out-of-focus broken pillar stump 1 m from the lens; the track wipes it off frame
# right, revealing the profile a few frames before the key frame
stump = AR.make_pillar("O3_fg_stump", (-2.0, mid.y - 0.62), radius=0.33, height=3.0, flutes=12, seed=31,
                       broken=2.5, plinth=False, mouldings=False, mat=S["arena"].mats["pillar"])
L = AR.lights_walk(warrior=tuple(mid), cam=tuple(cam_fn(shot.key_frame)["loc"]))
# silhouette: kill the front bounce, push a strong ember rim from the far side
if "bounce" in L:
    L["bounce"].data.energy = 0.0
C.parent_keep(C.light("SPOT", "O3_rim", mid + Vector((3.2, 1.2, 1.6)), color="#FF6A1A", energy=1400, size=0.4,
                      target=mid + Vector((0, 0, 1.2)), spot_size=math.radians(35), shadow=False), S["w"].root)
hid = rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
