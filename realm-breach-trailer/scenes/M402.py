"""M402 — A boss (the skeleton king) collapses to ash and drops a glowing ring that lands at our feet.
Low 50 mm; the speed ramp into the next beat is done in the edit."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

import rb_enemies as EN  # noqa: E402
import rb_props as PR  # noqa: E402

shot = rb_shot.Shot("M402", key_frame=1126)
D, _ = MT.scene(shot, "legend", warrior=False)
kg = MT.enemy("skeleton_king", "KG1_", seed=shot.seed)
F_DIE = shot.f0 + 1
MT.enemy_act(kg, shot, "death", F_DIE + 8, 14, (0.0, 1.6, 0.0), 0)
EN.dissolve(kg, F_DIE, frames=12, mode="ash")
RING_AT = Vector((0.06, -0.45, 0.012))
ring = PR.ring(loc=tuple(RING_AT), rot=(0, 0, math.radians(30)), gem="#FFE9A8")
F_LAND = MT.imp(74.75)
# the ring drops out of the ash and lands with a small bounce, its gem lighting up on landing
for f in shot.frames_all:
    u = C.clamp01((f - (F_LAND - 7)) / 7.0)
    z = RING_AT.z + (1.6 * (1 - u * u) if u < 1 else 0.03 * max(0.0, math.sin((f - F_LAND) * 0.9)) * math.exp(-(f - F_LAND) * 0.4))
    ring.location = (RING_AT.x, RING_AT.y + 0.4 * (1 - u), z)
    ring.keyframe_insert("location", frame=f)
MT.key_glow(ring, [(shot.sim_start, 0.15), (F_LAND, 0.15), (F_LAND + 2, 1.6), (F_LAND + 8, 1.0)])
cam = rb_cam.Rig(lens=50, fstop=2.8)
LOC = Vector((0.28, -1.6, 0.2))
cam.key_range(shot.frames_all, lambda f: dict(loc=LOC, target=Vector((0.0, -0.2, 0.42)), focus=RING_AT))
MT.light(shot, "legend", D, (0, 1.0, 0), LOC)
MT.fx("ash", shot.sim_start, shot.render_end, (0, 1.6, 1.5), radius=1.5, height=3.0, count=200, seed=shot.seed, rise=0.8)
shot.render()
