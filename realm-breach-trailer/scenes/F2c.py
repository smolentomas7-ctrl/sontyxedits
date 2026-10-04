"""F2c — He is thrown down across the floor. Wide, 24 mm, heavy."""
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

shot = rb_shot.Shot("F2c", key_frame=1508)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


cam = rb_cam.Rig(lens=24, fstop=8.0)
cam.handheld(amp=0.02, rot_deg=0.4, freq=1.2, seed=shot.seed)
cam.shake(int(ST.bf(99.62)) - 1, amp=0.06, seed=shot.seed)
cam.shake(int(ST.bf(100.4)) - 1, amp=0.04, seed=shot.seed + 1)
loc = Vector((-2.8, 2.6, 1.0))
cam.key_range(shot.frames_all, lambda f: dict(loc=loc, target=Vector((0.0, 8.2, 2.1)), focus=5.5))
AR.lights_duel(warrior=tuple(rb_intro.warrior_pos_battle(shot.key_frame)), cam=tuple(loc))
try:
    import rb_vfx as VFX
    VFX.sparks(int(ST.bf(99.62)) - 1, tuple(ST.CONTACT[99.62]), seed=shot.seed)
    VFX.dust_puff(int(ST.bf(100.4)) - 1, tuple(Vector(ST._KNOCK) + Vector((0, -0.6, 0))), seed=shot.seed + 1, scale=1.6)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
