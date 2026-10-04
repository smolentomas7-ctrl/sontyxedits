"""F1e — Full exchange: blocks, the god barely moves. Wide, 24 mm, heavy."""
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

shot = rb_shot.Shot("F1e", key_frame=1414)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


cam = rb_cam.Rig(lens=24, fstop=8.0)
cam.handheld(amp=0.025, rot_deg=0.5, freq=1.2, seed=shot.seed)
for b in (93.5, 94.5, 95.2):
    cam.shake(int(ST.bf(b)) - 1, amp=0.035, seed=shot.seed + int(b))
loc = Vector((2.6, 5.4, 1.35))
cam.key_range(shot.frames_all, lambda f: dict(loc=loc + Vector((-0.6 * shot.u(f), 0.3 * shot.u(f), 0)),
                                              target=Vector((0.0, 11.4, 3.2)), focus=5.0))
AR.lights_duel(warrior=tuple(rb_intro.warrior_pos_battle(shot.key_frame)), cam=tuple(loc))
try:
    import rb_vfx as VFX
    for b in (93.5, 94.5, 95.2):
        VFX.sparks(int(ST.bf(b)) - 1, tuple(ST.CONTACT[b]), seed=shot.seed + int(b * 10))
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
