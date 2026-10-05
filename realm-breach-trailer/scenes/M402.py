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

shot = rb_shot.Shot("M402", key_frame=1131)   # the ring has landed (1128) and its gem glows
D, _ = MT.scene(shot, "legend", warrior=False)
kg = MT.enemy("skeleton_king", "KG1_", seed=shot.seed)
F_DIE = shot.f0 + 1
MT.enemy_act(kg, shot, "death", F_DIE + 8, 14, (0.0, 1.6, 0.0), 0)
EN.dissolve(kg, F_DIE, frames=12, mode="ash")
RING_AT = Vector((0.06, -0.45, 0.012))
# hero-sized drop (a real 2.4 cm ring was a speck even at 1.2 m)
ring = PR.ring(loc=tuple(RING_AT), rot=(0, 0, math.radians(30)), gem="#6FA8FF", scale=2.2)   # the blue ring that slides onto the gauntlet in M403
F_LAND = MT.imp(74.75)
# the ring drops out of the ash and lands with a small bounce, its gem lighting up on landing
for f in shot.frames_all:
    u = C.clamp01((f - (F_LAND - 7)) / 7.0)
    z = RING_AT.z + (1.6 * (1 - u * u) if u < 1 else 0.03 * max(0.0, math.sin((f - F_LAND) * 0.9)) * math.exp(-(f - F_LAND) * 0.4))
    ring.location = (RING_AT.x, RING_AT.y + 0.4 * (1 - u), z)
    ring.keyframe_insert("location", frame=f)
MT.key_glow(ring, [(shot.sim_start, 0.15), (F_LAND, 0.15), (F_LAND + 2, 1.6), (F_LAND + 8, 1.0)])
# floor-level macro: 0.5 m from the ring (frame ~0.2 m wide there), looking slightly down so the ring sits just below
# centre on dark stone and the king's ash pile stays soft behind it (from 1.6 m the frame was all gold fog)
cam = rb_cam.Rig(lens=50, fstop=5.6)
LOC = RING_AT + Vector((0.1, -0.48, 0.1))
KING = Vector((0.0, 1.6, 1.0))


def cam_fn(f):
    # opens on the king collapsing to ash behind, then tilts down with the falling ring and lands on it (a fixed
    # macro on the ring showed two thirds of the shot as empty floor)
    e = C.ease_in_out(C.clamp01((f - (F_LAND - 9)) / 8.0))
    tgt = KING.lerp(RING_AT + Vector((0.0, 0.0, 0.03)), e)
    return dict(loc=LOC, target=tgt, focus=tgt)


cam.key_range(shot.frames_all, cam_fn)
MT.light(shot, "legend", D, (0, 1.0, 0), LOC)
MT.fx("ash", shot.sim_start, shot.render_end, (0, 1.6, 1.5), radius=1.5, height=3.0, count=200, seed=shot.seed, rise=0.8)
shot.render()
