"""M303 — Three life orbs in their iron frame; the right one dies (core fades, smoke wisp) — one held beat of
near silence. Static macro, 85 mm, the deep dungeon a dark blur behind."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

import rb_props as PR  # noqa: E402

shot = rb_shot.Shot("M303", key_frame=1048)
D, _ = MT.scene(shot, "deep", warrior=False)
O = PR.life_orbs(loc=(0.0, 0.0, 1.2), rot_z=0.0, scale=1.0)
PR.orb_dark(O, 2, MT.imp(69), frames=10)
kids = [o for o in O.root.children_recursive if o.type == "MESH"] or [O.root]
LOC, CTR = MT.frame_fit(kids, 85, margin=0.9, axis=(0.0, -1.0, 0.08))
cam = rb_cam.Rig(lens=85, fstop=4.0)
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=CTR, focus=(LOC - CTR).length))
MT.light(shot, "deep", D, CTR - Vector((0, 0, 1.2)), LOC)
MT.fx("ash", shot.sim_start, shot.render_end, tuple(CTR), radius=0.8, height=1.0, count=60, seed=shot.seed)
shot.render()
