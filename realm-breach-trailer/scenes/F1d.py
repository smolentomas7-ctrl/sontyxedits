"""F1d — E Lightning forks across the god stone. Mid, 35 mm."""
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

shot = rb_shot.Shot("F1d", key_frame=1396)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


cam = rb_cam.Rig(lens=35, fstop=4.0)
cam.handheld(amp=0.02, rot_deg=0.5, freq=1.4, seed=shot.seed)
loc = Vector((2.6, 6.0, 1.1))
cam.key_range(shot.frames_all, lambda f: dict(loc=loc, target=Vector((-0.4, 11.5, 3.0)), focus=5.5))
AR.lights_duel(warrior=tuple(rb_intro.warrior_pos_battle(shot.key_frame)), cam=tuple(loc))
try:
    import rb_vfx as VFX
    hand = ST.wl(Vector((0.22, -0.7, 1.5)), Vector((-1.2, 9.0, 0)))
    VFX.lightning(int(ST.bf(91.95)), tuple(hand), tuple(ST.GOD_POS + Vector((0, -0.4, 4.2))), seed=shot.seed)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
