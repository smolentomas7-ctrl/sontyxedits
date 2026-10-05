"""M301 — 50% slow motion: the evil's claw lands on his chest plate; sparks hang in the air.
Side-on slow dolly, 85 mm f/2 (desaturated, darker in the grade)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M301", key_frame=982)
D, w = MT.scene(shot, "deep", look="mid")
F_HIT = MT.imp(65)
P = Vector((0, 0, 0))
MT.act(w, shot, "hit_react", F_HIT, 12, P, 180, slowmo=0.5)
ev = MT.enemy("evil", "EV1_", seed=shot.seed)
MT.enemy_act(ev, shot, "attack", F_HIT, 12, (0.05, 1.75, 0), 0, slowmo=0.5)   # its attack pose leans ~1 m forward
cam = rb_cam.Rig(lens=85, fstop=2.0)
# side-on on his chest; at 5 m the 85 mm frame is ~1.2 m wide: his chest plate and the claw arriving from the left
cam.key_range(shot.frames_all, lambda f: dict(loc=Vector((-5.0 + 0.4 * C.ease_in_out(shot.u(f)), 0.35, 1.45)),
                                              target=Vector((0.0, 0.5, 1.4)), focus=Vector((0.0, 0.2, 1.4))))
MT.light(shot, "deep", D, P, (-5.0, 0.35, 1.45), follow=w.root)
MT.fx("sparks", F_HIT, (0.0, 0.25, 1.35), seed=shot.seed, scale=1.2, time_scale=0.5, direction=(-0.6, -0.4, 0.5))
MT.fx("ash", shot.sim_start, shot.render_end, (0, 0.4, 1.4), radius=2.0, height=3.0, seed=shot.seed)
shot.render()
