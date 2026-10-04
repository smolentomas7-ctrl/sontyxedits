"""F2b — Weapon close-up: obsidian crashes into the greatsword; sparks. 50 mm, shallow."""
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

shot = rb_shot.Shot("F2b", key_frame=1481)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


c = ST.CONTACT[98.0]
cam = rb_cam.Rig(lens=50, fstop=2.8)
cam.shake(int(ST.bf(98.0)) - 1, amp=0.03, seed=shot.seed)
# 3 m from the contact, from his right rear and a little below: helm + grip, the contact and the obsidian
# blade crashing down from the top of frame all read in one vertical image
loc = c + Vector((1.0, -0.8, -0.15)).normalized() * 3.0
cam.key_range(shot.frames_all, lambda f: dict(loc=loc + Vector((-0.08, 0.1, 0.0)) * shot.u(f),
                                              target=c + Vector((0.1, 0.15, 0.05)), focus=c))
AR.lights_duel(warrior=tuple(rb_intro.warrior_pos_battle(shot.key_frame)), cam=tuple(loc))
try:
    import rb_vfx as VFX
    VFX.sparks(int(ST.bf(98.0)) - 1, tuple(c), seed=shot.seed, scale=1.4)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
