"""M106 — Low insert: a grey COMMON short sword glows on the floor in a thin grey pillar; his boots step in
behind it, out of focus (50 mm f/2.8; punch-in added in the edit)."""
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

shot = rb_shot.Shot("M106", key_frame=840)
D, w = MT.scene(shot, "floor1", look="early")
# he walks toward the lens and stops just behind the drop (boots only in frame)
MT.walk(w, shot, (0.05, 0.62, 0.0), 0.0, key_frame=MT.imp(55.5), stop_frame=MT.imp(55.5), carry=True)
L = PR.loot(item="sword", rarity="common", loc=(0.0, 0.0, 0.0), rot_z=math.radians(62), seed=shot.seed)
cam = rb_cam.Rig(lens=50, fstop=2.8)
LOC = Vector((0.06, -1.05, 0.2))


def cam_fn(f):
    return dict(loc=LOC + Vector((0, 0.06, 0)) * shot.u(f), target=Vector((0.0, 0.05, 0.13)), focus=Vector((0, 0, 0.05)))


cam.key_range(shot.frames_all, cam_fn)
MT.light(shot, "floor1", D, (0, 0.3, 0), LOC)
MT.fx("ash", shot.sim_start, shot.render_end, (0, 0.2, 0.5), radius=1.5, height=1.5, count=120, seed=shot.seed)
shot.render()
