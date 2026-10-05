"""M205 — Floor-5 boss: the towering armoured skeleton king raises its axe over him; he looks up, guard
high. Low angle 24 mm from behind him; the king fills the top half. FLOOR 250 in the edit."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M205", key_frame=930)
D, w = MT.scene(shot, "struggle", look="mid")
P = Vector((0, 0, 0))
MT.stand(w, shot, P, 180, look_up=28.0, grip=(-0.15, -0.3, 1.5), blade=(0.85, -0.35, 0.35), two=True, stance=0.4)
kg = MT.enemy("skeleton_king", "KG1_", seed=shot.seed)
MT.enemy_act(kg, shot, "raise", MT.imp(61.5), 16, (0.0, 2.7, 0.0), 0)
cam = rb_cam.Rig(lens=24, fstop=5.6)
cam.handheld(amp=0.008, rot_deg=0.25, freq=0.9, seed=shot.seed)
cam.shake(MT.imp(61.5), amp=0.02, seed=shot.seed)
# over his shoulder, tight and looking steeply up: his pauldron anchors the lower left, the king and the raised
# axe fill the frame above (from further back they read the same size)
LOC = Vector((0.55, -0.75, 1.45))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC + Vector((0, 0.08, -0.03)) * shot.u(f),
                                              target=Vector((0.0, 2.7, 3.7)), focus=3.9))
MT.light(shot, "struggle", D, P, LOC, follow=w.root)
MT.fx("ash", shot.sim_start, shot.render_end, (0, 2.0, 2.5), radius=3.5, height=5.0, seed=shot.seed)
shot.render()
