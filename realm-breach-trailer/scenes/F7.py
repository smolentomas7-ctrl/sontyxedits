"""F7 — R God Attack on U: golden-white blast hits the Fallen God; the camera whips with the strike; white floods the frame. 24 mm."""
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

shot = rb_shot.Shot("F7", key_frame=1931)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


r = Vector(ST._RISE)
cam = rb_cam.Rig(lens=24, fstop=8.0)
cam.whip(int(ST.bf(127.6)), int(ST.bf(128.0)) + 2, 28)
cam.shake(int(ST.bf(128.0)) - 1, amp=0.08, seed=shot.seed)
loc = r + Vector((-2.6, -2.2, 1.0))
cam.key_range(shot.frames_all, lambda f: dict(loc=loc, target=r + Vector((0.8, 3.2, 1.9)), focus=4.0))
AR.lights_duel(warrior=tuple(r), cam=tuple(loc))
try:
    import rb_vfx as VFX
    tip = ST.wl(Vector((-0.05, -1.4, 1.6)), r)
    VFX.god_attack(int(ST.bf(128.0)) - 1, tuple(tip), tuple(ST.GOD_POS + Vector((0, 0, 3.6))), seed=shot.seed)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
