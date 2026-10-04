"""M204 — Overwhelming odds: a crowd of skeletons and ghosts closes in around him. High wide 24 mm from
7 m up, slow push down; uses the full vertical frame."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

import rb_enemies as EN  # noqa: E402

shot = rb_shot.Shot("M204", key_frame=915)
D, w = MT.scene(shot, "struggle", look="mid")
P = Vector((0, 0, 0))
MT.stand(w, shot, P, 200, grip=(-0.1, -0.35, 1.1), blade=(0.05, -0.6, 0.8), two=True, stance=0.35)
crowd = EN.crowd(["skeleton", "skeleton", "ghost"], 22, (0, 0, 0), 4.6, seed=shot.seed, face=(0, 0, 0), min_r=2.2)
EN.crowd_advance(crowd, shot.sim_start, shot.render_end, 1.1)
cam = rb_cam.Rig(lens=24, fstop=8.0)
cam.handheld(amp=0.006, rot_deg=0.15, freq=0.6, seed=shot.seed)
cam.key_range(shot.frames_all, lambda f: dict(loc=Vector((0.4, -4.3, 7.1 - 0.6 * C.ease_in_out(shot.u(f)))),
                                              target=Vector((0.0, 0.35, 0.0)), focus=7.8))
MT.light(shot, "struggle", D, P, (0.4, -4.3, 7.0), follow=w.root)
MT.fx("embers", shot.sim_start, shot.render_end, (0, 0, 2.0), radius=6.0, height=6.0, seed=shot.seed)
shot.render()
