"""M403 — Macro: the new ring slides onto his gauntlet finger beside the other three; all four glow.
50 mm f/2.8 push-in on the left fist."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

import bpy  # noqa: E402
import rb_mat as M  # noqa: E402
import rb_motion as MO  # noqa: E402
import rb_warrior as RW  # noqa: E402

shot = rb_shot.Shot("M403", key_frame=1143)
D, w = MT.scene(shot, "legend", look="late")
P = Vector((0, 0, 0))
LEFT = {"upperarm_L": (-58, -8, 0), "forearm_L": (-72, 0, 0), "hand_L": (0, 0, -10)}
MT.stand(w, shot, P, 180, extra=LEFT)
F_ON = MT.imp(75.75)
hd = (Vector(RW.J["fingers_L"]) - Vector(RW.J["hand_L"])).normalized()
new = [bpy.data.objects[n] for n in ("W_ring3", "W_gem3") if n in bpy.data.objects]
for f in shot.frames_all:
    u = C.ease_out(C.clamp01((f - (F_ON - 8)) / 8.0))
    for o in new:
        o.delta_location = hd * (0.05 * (1 - u))
        o.keyframe_insert("delta_location", frame=f)
for k in range(4):
    m = bpy.data.materials.get("ringglow%d" % k)
    if m is None:
        continue
    lo = 0.0 if k == 3 else 0.5
    for f, v in ((shot.sim_start, lo), (F_ON, lo), (F_ON + 2, 2.2), (F_ON + 9, 1.3)):
        M.key_ctrl(m, "ring%d" % k, f, v)
bpy.context.scene.frame_set(shot.key_frame)
fist = w.rig["fingers_L"].matrix_world.translation.copy()
cam = rb_cam.Rig(lens=50, fstop=2.8)
cam.key_range(shot.frames_all, lambda f: dict(loc=fist + Vector((-0.12, 0.5 - 0.08 * C.ease_in_out(shot.u(f)), 0.1)),
                                              target=fist, focus=fist))
MT.light(shot, "legend", D, P, fist + Vector((-0.12, 0.5, 0.1)), follow=w.root)
shot.render()
