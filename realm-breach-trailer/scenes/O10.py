"""O10 — Over the warrior's shoulder, the blade pointed at the Fallen God, the boss framed beyond the tip.
Static, 35 mm, deep focus. (VO4, then one beat of silence)"""
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

shot = rb_shot.Shot("O10", key_frame=650)
S = rb_intro.build(shot, variant="approach")
import rb_env_arena as AR  # noqa: E402

p = ST.STOP
cam = rb_cam.Rig(lens=35, fstop=8.0)
loc = p + Vector((0.4, -0.62, 1.74))
cam.key_range(shot.frames_all, lambda f: dict(loc=loc, target=ST.GOD_POS + Vector((0.2, 0, 3.2)), focus=9.0))
AR.lights_walk(warrior=tuple(p), cam=tuple(loc))
AR.lights_god_reveal(cam=tuple(loc))
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
