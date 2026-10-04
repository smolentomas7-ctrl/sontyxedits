"""F1c — Q Fireball into the god chest. Mid, 35 mm, fast."""
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

shot = rb_shot.Shot("F1c", key_frame=1382)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


cam = rb_cam.Rig(lens=35, fstop=4.0)
cam.handheld(amp=0.02, rot_deg=0.5, freq=1.4, seed=shot.seed)
loc = Vector((-2.8, 6.2, 1.3))
cam.key_range(shot.frames_all, lambda f: dict(loc=loc, target=Vector((-0.6, 11.0, 2.4)), focus=4.4))
AR.lights_duel(warrior=tuple(rb_intro.warrior_pos_battle(shot.key_frame)), cam=tuple(loc))
try:
    import rb_vfx as VFX
    hand = ST.wl(Vector((0.24, -0.7, 1.42)), Vector((-1.2, 9.0, 0)))
    VFX.fireball(int(ST.bf(90.95)), tuple(hand), tuple(ST.GOD_POS + Vector((0, -0.6, 3.8))), seed=shot.seed)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
