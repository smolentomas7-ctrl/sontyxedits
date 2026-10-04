"""E6 — A glowing REBIRTH button: the carved obsidian plaque on black, its ember-gold glow pulses once.
Static."""
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

shot = rb_shot.Shot("E6", key_frame=2216)
C.world((0.0, 0.0, 0.0), volume_density=0.004)
Pq = PR.rebirth_plaque(loc=(0.0, 0.0, 0.0), rot_z=0.0, scale=1.0)
PR.plaque_pulse(Pq, MT.imp(147), frames=14, peak=1.0)
kids = [o for o in Pq.root.children_recursive if o.type in ("MESH", "FONT")] or [Pq.root]
LOC, CTR = MT.frame_fit(kids, 50, margin=1.15, axis=(0.0, -1.0, 0.0))
cam = rb_cam.Rig(lens=50, fstop=8.0)
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC + (CTR - LOC) * (0.04 * shot.u(f)), target=CTR, focus=(LOC - CTR).length))
C.light("AREA", "E6_key", tuple(CTR + Vector((-0.8, -1.2, 1.0))), color="#FFB070", energy=40, size=1.0, target=tuple(CTR), shadow=False)
MT.fx("embers", shot.sim_start, shot.render_end, tuple(CTR), radius=1.2, height=1.5, count=50, seed=shot.seed, strength=0.6)
shot.render()
