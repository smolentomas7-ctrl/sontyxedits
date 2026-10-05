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

shot = rb_shot.Shot("F2b", key_frame=1479)   # 1 frame after the impact: compact burst, blades visible
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


c = ST.CONTACT[98.0]
cam = rb_cam.Rig(lens=50, fstop=2.8)
cam.shake(int(ST.bf(98.0)) - 1, amp=0.03, seed=shot.seed)
# side-on to the clash (the blades move in the warrior's Y-Z plane): the obsidian comes down from upper left onto
# the greatsword held up from the right; camera kept inside the nave (pillar plinths reach |x| ~ 3.1)
loc = Vector((-2.9, 8.6, 1.95))
cam.key_range(shot.frames_all, lambda f: dict(loc=loc + Vector((0.08, 0.05, 0.0)) * shot.u(f),
                                              target=c + Vector((0.05, -0.05, -0.02)), focus=c))
AR.lights_duel(warrior=tuple(rb_intro.warrior_pos_battle(shot.key_frame)), cam=tuple(loc))
try:
    import rb_vfx as VFX
    VFX.sparks(int(ST.bf(98.0)) - 1, tuple(c), seed=shot.seed, scale=0.75)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
