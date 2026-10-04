"""E3 — He turns his back on the fallen god and walks toward the Gate of Heaven; warm white light pours
out past him. Tracking from behind, 35 mm."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

import rb_env_heaven as HV  # noqa: E402
import rb_warrior as RW  # noqa: E402

shot = rb_shot.Shot("E3", key_frame=2060)
G = HV.build_gate(seed=shot.seed)
mk = G.marks
w = RW.build_warrior("late", rings=True, cape=True)
shot.register_cloth(w.cloths)
at = MT.walk(w, shot, mk["warrior"], mk["heading"], crack=1.2, carry=True)
W = Vector(mk["warrior"])
fwd = MT.MO.heading_vec(mk["heading"])
cam = rb_cam.Rig(lens=35, fstop=5.6)
cam.handheld(amp=0.004, rot_deg=0.12, freq=0.6, seed=shot.seed)


def cam_fn(f):
    r = at(f)[0]
    loc = Vector((r.x, r.y, 0)) - fwd * 3.6 + Vector((0.35, 0, 1.45))
    return dict(loc=loc, target=Vector((r.x, r.y, 0)) + fwd * 8.0 + Vector((0, 0, 2.6)), focus=r + Vector((0, 0, 1.2)))


cam.key_range(shot.frames_all, cam_fn)
shot.scene.frame_set(shot.key_frame)
HV.lights_gate(G, warrior=tuple(W), cam=tuple(cam_fn(shot.key_frame)["loc"]), follow=w.root)
MT.fx("ash", shot.sim_start, shot.render_end, tuple(W + fwd * 3 + Vector((0, 0, 2))), radius=4.0, height=4.0, count=160, seed=shot.seed, color=(0.9, 0.85, 0.75))
shot.render()
