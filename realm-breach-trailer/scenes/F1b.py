"""F1b — He dodges; the obsidian blade smashes the floor. Low angle, 24 mm, fast."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_intro  # noqa: E402
import rb_shot  # noqa: E402
import rb_story as ST  # noqa: E402

shot = rb_shot.Shot("F1b", key_frame=1366)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


cam = rb_cam.Rig(lens=24, fstop=5.6)
cam.handheld(amp=0.03, rot_deg=0.7, freq=1.6, seed=shot.seed)
cam.shake(int(ST.bf(90.3)) - 1, amp=0.07, seed=shot.seed)
loc = Vector((-2.7, 6.4, 0.35))
cam.key_range(shot.frames_all, lambda f: dict(loc=loc, target=Vector((-0.3, 10.2, 1.9)), focus=4.6))
AR.lights_duel(warrior=tuple(rb_intro.warrior_pos_battle(shot.key_frame)), cam=tuple(loc))
try:
    import rb_vfx as VFX
    f0 = int(ST.bf(90.3)) - 1
    VFX.debris(f0, tuple(ST.SLAM), seed=shot.seed)
    VFX.sparks(f0, tuple(ST.SLAM), seed=shot.seed + 1)
    VFX.shockwave(f0, tuple(ST.SLAM), seed=shot.seed + 2, scale=0.6)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
