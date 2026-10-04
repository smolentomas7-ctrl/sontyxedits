"""O4 — The stop. Ground-level static insert: his sabaton plants on the 808 (beat 8), dust settles. 50 mm, shallow."""
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

shot = rb_shot.Shot("O4", key_frame=int(round(ST.bf(8))) + 2)
S = rb_intro.build(shot, variant="approach")
import rb_env_arena as AR  # noqa: E402

foot = ST._plant_pos()
cam = rb_cam.Rig(lens=50, fstop=2.0)
loc = foot + Vector((-0.55, 0.85, 0.11))
cam.key_range(shot.frames_all, lambda f: dict(loc=loc, target=foot + Vector((0.05, -0.1, 0.12)),
                                              focus=foot + Vector((0, 0, 0.08))))
L = AR.lights_walk(warrior=tuple(rb_intro.warrior_pos(shot.key_frame)), cam=tuple(loc))
C.light("SPOT", "O4_rake", foot + Vector((2.6, -0.4, 0.25)), color="#FF7A2E", energy=900, size=0.2,
        target=foot + Vector((0, 0, 0.05)), spot_size=math.radians(30), shadow=True)
try:
    import rb_vfx as VFX
    VFX.dust_puff(int(round(ST.bf(8))) - 1, tuple(foot), seed=shot.seed)
except Exception as e:  # VFX module not built yet
    print("no dust:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
