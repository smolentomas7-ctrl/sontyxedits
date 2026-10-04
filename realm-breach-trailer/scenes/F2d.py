"""F2d — Macro, 85 mm: the second life orb goes dark — one left. The fallen warrior lies blurred on the
arena floor behind the orbs."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

import rb_intro  # noqa: E402
import rb_props as PR  # noqa: E402
import rb_story as ST  # noqa: E402

shot = rb_shot.Shot("F2d", key_frame=1556)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402

K = Vector(ST._KNOCK)
ORB = K + Vector((0.35, -2.1, 0.95))
O = PR.life_orbs(loc=tuple(ORB), rot_z=0.0, scale=1.0)
PR.orb_dark(O, 2, shot.sim_start - 12, frames=1)          # the first life was lost in M303
PR.orb_dark(O, 1, MT.imp(102.5), frames=12)
kids = [o for o in O.root.children_recursive if o.type == "MESH"] or [O.root]
LOC, CTR = MT.frame_fit(kids, 85, margin=1.3, axis=(0.05, -1.0, 0.12))
cam = rb_cam.Rig(lens=85, fstop=2.8)
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC + (CTR - LOC) * (0.06 * C.ease_in_out(shot.u(f))), target=CTR,
                                              focus=(LOC - CTR).length))
AR.lights_after(warrior=tuple(K), cam=tuple(LOC))

MT.fx("ash", shot.sim_start, shot.render_end, tuple(CTR), radius=1.0, height=1.2, count=60, seed=shot.seed)
shot.render()
