"""M407 — Close along the blade: the crack in his greatsword ignites, ember fire racing up to the tip.
50 mm push from the hilt toward the tip."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M407", key_frame=1204)
D, w = MT.scene(shot, "legend", look="late")
P = Vector((0, 0, 0))
F_IGN = MT.imp(79.25)


def crack(f):
    u = C.clamp01((f - F_IGN) / 8.0)
    return 0.3 + 8.0 * C.ease_in(u) * (0.85 + 0.15 * math.sin(f * 1.7))


MT.stand(w, shot, P, 180, grip=(-0.08, -0.38, 1.3), blade=(0.12, -0.55, 0.83), two=True, crack=crack)
tip = MT.tip_empty(w)
import bpy  # noqa: E402
bpy.context.scene.frame_set(shot.key_frame)
hilt = w.sword.matrix_world.translation.copy()
tp = tip.matrix_world.translation.copy()
axis = (tp - hilt).normalized()
side = axis.cross(Vector((0, 0, 1))).normalized()
cam = rb_cam.Rig(lens=50, fstop=2.8)
cam.key_range(shot.frames_all, lambda f: dict(loc=hilt + side * 0.32 + Vector((0, 0, -0.06)) + axis * (0.1 + 0.35 * C.ease_in_out(shot.u(f))),
                                              target=tp, focus=hilt.lerp(tp, 0.45)))
MT.light(shot, "legend", D, P, hilt + side * 0.4, follow=w.root)
MT.fx("embers", shot.sim_start, shot.render_end, tuple(hilt.lerp(tp, 0.5)), radius=0.8, height=1.2, count=60, seed=shot.seed)
shot.render()
