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

shot = rb_shot.Shot("F2c", key_frame=1512)   # nearer the crash, bigger in frame
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


cam = rb_cam.Rig(lens=24, fstop=8.0)
cam.handheld(amp=0.02, rot_deg=0.4, freq=1.2, seed=shot.seed)
cam.shake(int(ST.bf(99.62)) - 1, amp=0.06, seed=shot.seed)
cam.shake(int(ST.bf(100.4)) - 1, amp=0.04, seed=shot.seed + 1)
# low, just beyond where he lands: he is thrown toward the lens, the god looming behind him
loc = Vector((-0.25, 2.0, 0.5))           # on his line of flight: he falls toward the lens, the god behind him


def cam_fn(f):
    p = rb_intro.warrior_pos_battle(f)
    tgt = (p + Vector((0, 0, 1.0))).lerp(ST.GOD_POS + Vector((0, 0, 3.4)), 0.45)
    return dict(loc=loc, target=tgt, focus=max(1.5, (p - loc).length))


cam.key_range(shot.frames_all, cam_fn)
AR.lights_duel(warrior=tuple(rb_intro.warrior_pos_battle(shot.key_frame)), cam=tuple(loc))
try:
    import rb_vfx as VFX
    VFX.sparks(int(ST.bf(99.62)) - 1, tuple(ST.CONTACT[99.62]), seed=shot.seed)
    VFX.dust_puff(int(ST.bf(100.4)) - 1, tuple(Vector(ST._KNOCK) + Vector((0, -0.6, 0))), seed=shot.seed + 1, scale=1.6)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
