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
up = side.cross(axis).normalized()
cam = rb_cam.Rig(lens=50, fstop=4.0)


def cam_fn(f):
    # side-on to the blade (it crosses the vertical frame diagonally), pushing from the hilt toward the tip as
    # the crack ignites
    mid = hilt.lerp(tp, 0.32 + 0.3 * C.ease_in_out(shot.u(f)))
    return dict(loc=mid - side * 1.05 + up * 0.12, target=mid, focus=mid)


cam.key_range(shot.frames_all, cam_fn)
MT.light(shot, "legend", D, P, hilt - side * 1.0, follow=w.root)
MT.fx("embers", shot.sim_start, shot.render_end, tuple(hilt.lerp(tp, 0.5) + side * 0.7), radius=0.45, height=1.0, count=45,
      seed=shot.seed)    # behind the blade: embers near the lens bloomed into big white blobs
shot.render()
