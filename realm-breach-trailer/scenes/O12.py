"""O12 — The clash on D: wide side-on, both fighters; 2-frame freeze on contact, shockwave ring, sparks,
debris; white impact + shake decaying over 6 frames. 24 mm, deep."""
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

shot = rb_shot.Shot("O12", key_frame=int(round(ST.bf(48))) + 3)
S = rb_intro.build(shot, variant="duel")
import rb_env_arena as AR  # noqa: E402

hit = ST.CLASH + Vector((0.1, 0.0, 2.05))
cam = rb_cam.Rig(lens=24, fstop=8.0)
loc = Vector((-1.9, 5.2, 0.8))
cam.key_range(shot.frames_all, lambda f: dict(loc=loc, target=Vector((0.5, 11.0, 3.0)), focus=4.0))
cam.shake(int(round(ST.bf(48))) - 1, amp=0.06, seed=shot.seed)
AR.lights_duel(warrior=tuple(rb_intro.warrior_pos(shot.key_frame)), cam=tuple(loc))
C.light("POINT", "O12_contact", hit, color="#FFE9A8", energy=0.0, size=0.2, shadow=False)
try:
    import rb_vfx as VFX
    f0 = int(round(ST.bf(48))) - 1
    VFX.shockwave(f0 + 2, tuple(hit), seed=shot.seed)
    VFX.sparks(f0, tuple(hit), seed=shot.seed + 1)
    VFX.debris(f0 + 2, tuple(ST.CLASH), seed=shot.seed + 2)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
