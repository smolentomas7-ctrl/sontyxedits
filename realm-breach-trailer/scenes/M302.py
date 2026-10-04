"""M302 — 50% slow motion: he falls backwards to the floor; ash rises. Slow dolly from low side, 85 mm;
the landing sits on the beat."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M302", key_frame=1012)
D, w = MT.scene(shot, "deep", look="mid")
F_LAND = MT.imp(68)
P = Vector((0, 0, 0))
MT.act(w, shot, "fall", F_LAND, 16, P, 180, slowmo=0.5)
cam = rb_cam.Rig(lens=85, fstop=2.0)
cam.key_range(shot.frames_all, lambda f: dict(loc=Vector((-4.2 + 0.4 * C.ease_in_out(shot.u(f)), -0.5, 0.55)),
                                              target=Vector((0.0, -0.45, 0.75)), focus=4.0))
MT.light(shot, "deep", D, (0, -0.4, 0), (-4.2, -0.5, 0.55), follow=w.root)
MT.fx("ash", shot.sim_start, shot.render_end, (0, -0.5, 0.6), radius=2.0, height=2.5, seed=shot.seed, rise=0.6)
MT.fx("dust_puff", F_LAND, (0.0, -0.9, 0.0), seed=shot.seed + 1, scale=1.6)
shot.render()
