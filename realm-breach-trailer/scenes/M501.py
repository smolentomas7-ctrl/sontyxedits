"""M501 — The morbidious brute lunges at him, toxic green pustules glowing. Fast, low 24 mm over his
right shoulder."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M501", key_frame=1212)
D, w = MT.scene(shot, "legend", look="late")
P = Vector((0, 0, 0))
MT.stand(w, shot, P, 180, grip=(-0.25, -0.15, 1.05), blade=(-0.3, 0.5, 0.8), two=True, stance=0.4,
         crack=5.0)   # ignited blade (M407 -> M508)
mb = MT.enemy("morbidious", "MB1_", seed=shot.seed)
F_L = shot.f1 - 1   # the leap peaks on the last frame, 2 f before beat 80.5 (imp + 1 was after the cut)
MT.enemy_act(mb, shot, "lunge", F_L, 10, (0.0, 1.5, 0.0), 0)
MT.enemy_path(mb, shot, lambda f: Vector((0.1, 3.4, 0)).lerp(Vector((0.0, 1.5, 0)), C.ease_in(C.clamp01((f - shot.f0 + 3) / 9.0))))
cam = rb_cam.Rig(lens=24, fstop=5.6)
cam.handheld(amp=0.015, rot_deg=0.5, freq=1.6, seed=shot.seed)
LOC = Vector((0.55, -1.05, 1.15))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((0.0, 2.2, 1.45)), focus=2.6))
MT.light(shot, "legend", D, P, LOC, follow=w.root)
shot.render()
