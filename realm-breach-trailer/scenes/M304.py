"""M304 — He kneels, both hands on the greatsword planted before him, head bowed. Slow push, 85 mm, 3/4
front. The low point before the rise."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M304", key_frame=1074)
D, w = MT.scene(shot, "deep", look="mid")
P = Vector((0, 0, 0))
MT.act(w, shot, "kneel", shot.f0 + 4, 20, P, 180, slowmo=0.5)
cam = rb_cam.Rig(lens=85, fstop=2.2)
cam.key_range(shot.frames_all, lambda f: dict(loc=Vector((1.75, 3.35, 1.05)).lerp(Vector((1.5, 2.95, 1.0)), C.ease_in_out(shot.u(f))),
                                              target=Vector((0.0, 0.1, 0.85)), focus=Vector((0, 0.15, 1.0))))
MT.light(shot, "deep", D, P, (1.75, 3.35, 1.05), follow=w.root)
MT.fx("ash", shot.sim_start, shot.render_end, (0, 0.3, 1.0), radius=2.0, height=2.5, seed=shot.seed)
MT.fx("embers", shot.sim_start, shot.render_end, (0, 0.6, 1.2), radius=2.5, height=3.0, count=40, seed=shot.seed + 1, strength=0.5)
shot.render()
