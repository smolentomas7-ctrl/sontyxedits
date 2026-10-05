"""M201 — Phase 2 (struggle, mid look): a ghost lunges out of the fog, claws first; he swings into a block.
Handheld tracking 35 mm from behind his right shoulder; shake on contact."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M201", key_frame=860)
D, w = MT.scene(shot, "struggle", look="mid")
F_HIT = MT.imp(57)
P = Vector((0, 0, 0))
MT.act(w, shot, "block", F_HIT, 14, P, 180)
gh = MT.enemy("ghost", "GH1_", seed=shot.seed)
MT.enemy_act(gh, shot, "lunge", F_HIT, 16, (-0.3, 1.25, 0.0), 10)
MT.enemy_path(gh, shot, lambda f: Vector((-1.4, 3.6, 0.5)).lerp(Vector((-0.3, 1.25, 0.15)), C.ease_out(C.clamp01((f - (F_HIT - 12)) / 12.0))))
cam = rb_cam.Rig(lens=35, fstop=4.0)
cam.handheld(amp=0.014, rot_deg=0.45, freq=1.4, seed=shot.seed)
cam.shake(F_HIT, amp=0.035, seed=shot.seed)
LOC = Vector((1.5, -2.5, 1.65))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC + Vector((-0.1, 0.25, 0)) * shot.u(f),
                                              target=Vector((-0.35, 1.5, 1.55)), focus=3.2))
MT.light(shot, "struggle", D, P, LOC, follow=w.root)
MT.fx("sparks", F_HIT, (-0.15, 0.62, 1.75), seed=shot.seed, scale=1.2, direction=(0.3, -0.6, 0.6))
MT.fx("embers", shot.sim_start, shot.render_end, (0, 1.0, 1.5), radius=4.0, seed=shot.seed, cam=cam.cam, near=2)
shot.render()
