"""F1a — Return: greatsword and obsidian blade mid-clash. Wide, heavy handheld feel, 24 mm."""
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

shot = rb_shot.Shot("F1a", key_frame=1342)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


cam = rb_cam.Rig(lens=24, fstop=8.0)
cam.handheld(amp=0.03, rot_deg=0.6, freq=1.4, seed=shot.seed)
cam.shake(int(ST.bf(88.5)) - 1, amp=0.05, seed=shot.seed)
loc = Vector((-2.5, 5.3, 1.05))
cam.key_range(shot.frames_all, lambda f: dict(loc=loc + Vector((0, 0.4 * shot.u(f), 0)), target=Vector((0.0, 11.0, 3.0)), focus=5.0))
AR.lights_duel(warrior=tuple(rb_intro.warrior_pos_battle(shot.key_frame)), cam=tuple(loc))
try:
    import rb_vfx as VFX
    VFX.sparks(int(ST.bf(88.5)) - 1, tuple(ST.CONTACT[88.5]), seed=shot.seed)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
