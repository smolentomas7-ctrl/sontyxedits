"""M202 — A bad angel dives from above (black broken wings, red halo); he braces, looking up. Low angle 24 mm
from behind his shoulder. FLOOR 25 slams in the edit on the first frame."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M202", key_frame=882)
D, w = MT.scene(shot, "struggle", look="mid")
P = Vector((0, 0, 0))
MT.stand(w, shot, P, 180, look_up=24.0, grip=(-0.12, -0.32, 1.42), blade=(0.15, -0.45, 0.88), two=True, stance=0.3)
an = MT.enemy("bad_angel", "BA1_", seed=shot.seed)
F_DIVE = MT.imp(58.5)
MT.enemy_act(an, shot, "dive", F_DIVE, 18, (0, 2.2, 1.6), 0)
MT.enemy_path(an, shot, lambda f: Vector((0.4, 5.5, 6.0)).lerp(Vector((-0.1, 2.1, 1.6)), C.ease_in(C.clamp01((f - shot.f0 + 4) / float(F_DIVE - shot.f0 + 4)))))
cam = rb_cam.Rig(lens=24, fstop=5.6)
cam.handheld(amp=0.01, rot_deg=0.35, freq=1.2, seed=shot.seed)
cam.shake(F_DIVE, amp=0.03, seed=shot.seed)
LOC = Vector((0.55, -1.15, 0.5))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((-0.15, 2.6, 3.4)), focus=3.0))
MT.light(shot, "struggle", D, P, LOC, follow=w.root)
MT.fx("ash", shot.sim_start, shot.render_end, (0, 2.0, 3.0), radius=3.0, height=5.0, seed=shot.seed)
shot.render()
