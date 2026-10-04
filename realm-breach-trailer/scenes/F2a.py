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
# low side angle ~8.4 m from the god (the warrior, 5 m in front of him, stays out of frame left): the whole
# figure plus the blade raised overhead fits, feet near the bottom safe line, blade tip below the top one
CAM = Vector((3.6, 6.4, 0.35))
cam.key_range(shot.frames_all, lambda f: dict(loc=CAM + Vector((-0.25, 0.3, 0.0)) * C.ease_in_out(shot.u(f)),
                                              target=ST.GOD_POS + Vector((0, 0, 3.9)), focus=8.4))
AR.lights_god_reveal(cam=tuple(CAM))
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
