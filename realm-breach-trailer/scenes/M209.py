"""M209 — He is driven back across the floor (hit reaction, boots scraping), the evil pressing after him.
Wide 24 mm from behind-left, he is pushed toward the lens."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M209", key_frame=963)
D, w = MT.scene(shot, "struggle", look="mid")
F_HIT = shot.f0 + 1
import rb_actions as RA  # noqa: E402
import rb_motion as MO  # noqa: E402


def wpos(f):
    u = C.ease_out(C.clamp01((f - F_HIT) / 9.0))
    return Vector((0, 0.3, 0)).lerp(Vector((0.1, -0.95, 0)), u)


for f in shot.frames_all:
    pose, loc, rot = RA.perform(w, f, "hit_react", F_HIT, 12, wpos(f), 180)
    MO.key_pose(w, f, pose, loc, rot)
for ob in w.rig.values():
    C.set_interp(ob, "LINEAR")
ev = MT.enemy("evil", "EV1_", seed=shot.seed)
MT.enemy_act(ev, shot, "attack", F_HIT, 12, (0.0, 1.8, 0), 0)
MT.enemy_path(ev, shot, lambda f: Vector((0, 1.9, 0)).lerp(Vector((0.0, 1.0, 0)), C.ease_out(C.clamp01((f - F_HIT) / 9.0))))
cam = rb_cam.Rig(lens=24, fstop=5.6)
cam.handheld(amp=0.012, rot_deg=0.35, freq=1.3, seed=shot.seed)
cam.shake(F_HIT, amp=0.04, seed=shot.seed)
LOC = Vector((-1.9, -3.4, 1.25))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((0.0, 0.4, 1.2)), focus=3.6))
MT.light(shot, "struggle", D, (0, -0.4, 0), LOC, follow=w.root)
for k, side in enumerate((0.15, -0.15)):
    MT.fx("sparks", F_HIT + 3 + 2 * k, (side, -0.4, 0.05), seed=shot.seed + k, scale=0.5, direction=(0, 1, 0.3))
MT.fx("dust_puff", F_HIT + 6, (0.1, -0.8, 0.0), seed=shot.seed + 3, scale=1.2)
shot.render()
