"""F2a — Low angle on the boss: the Fallen God raises the obsidian blade overhead. 24 mm, heavy; blue overpowers."""
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

shot = rb_shot.Shot("F2a", key_frame=1470)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


cam = rb_cam.Rig(lens=24, fstop=8.0)
cam.handheld(amp=0.01, rot_deg=0.25, freq=0.8, seed=shot.seed)
cam.key_range(shot.frames_all, lambda f: dict(loc=Vector((0.6, 8.2 + 0.3 * C.ease_in_out(shot.u(f)), 0.5)),
                                              target=ST.GOD_POS + Vector((0, 0, 4.9)), focus=6.0))
AR.lights_god_reveal(cam=(0.6, 8.2, 0.5))
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
