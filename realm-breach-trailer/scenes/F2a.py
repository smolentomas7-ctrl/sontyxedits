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
# low side angle 7 m from the god (the warrior, 5 m in front of him, stays out of frame left): the figure plus
# the blade raised overhead fill the frame, feet at the bottom safe line, blade tip under the top one
CAM = Vector((3.0, 7.67, 0.35))
cam.key_range(shot.frames_all, lambda f: dict(loc=CAM + Vector((-0.2, 0.25, 0.0)) * C.ease_in_out(shot.u(f)),
                                              target=ST.GOD_POS + Vector((0, 0, 3.47)), focus=7.0))
AR.lights_god_reveal(cam=tuple(CAM))
# the near-black obsidian vanished against the dark: glossy glass reads by its reflections, so a big cool
# area light behind/above the raised blade puts a specular rim on its facets (plus a little edge glow)
import bpy  # noqa: E402
import rb_mat as M  # noqa: E402
ob_m = bpy.data.materials.get("obsidian")
if ob_m is not None:
    M.key_ctrl(ob_m, "edge_glow", shot.sim_start, 1.8)   # x4 + the rim read as a glowing white blade
C.light("AREA", "F2a_blade_rim", ST.GOD_POS + Vector((-1.6, 3.2, 9.8)), color="#8FB8FF", energy=3500, size=4.0,
        target=ST.GOD_POS + Vector((0.0, -0.3, 7.0)), shadow=False, volume=0.2)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
