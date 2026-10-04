"""F3 — Low angle looking up at the Fallen God as he speaks; slow push. 24 mm, cold blue key. (VO6)"""
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

shot = rb_shot.Shot("F3", key_frame=1690)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


k = Vector(ST._KNOCK)
cam = rb_cam.Rig(lens=24, fstop=8.0)
cam.key_range(shot.frames_all, lambda f: dict(loc=k + Vector((0.5, 0.9 + 0.6 * C.ease_in_out(shot.u(f)), 0.35)),
                                              target=ST.GOD_POS + Vector((0, 0, 4.6)), focus=9.0))
AR.lights_god_reveal(cam=tuple(k + Vector((0.5, 1.2, 0.35))))
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
