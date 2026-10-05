"""M401 — The loot pillar climbs every rarity in order on quarter beats: common, rare, epic, mythic,
legendary, morbidious, god, fallen equip. Orbit 30 deg + push-in, 50 mm."""
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

shot = rb_shot.Shot("M401", key_frame=1110)
D, _ = MT.scene(shot, "legend", warrior=False)
L = PR.loot(item="greatsword", rarity="common", loc=(0.0, 0.0, 0.0), rot_z=math.radians(35), seed=shot.seed)
for k, name in enumerate(PR.RARITY_ORDER):
    PR.set_rarity(L, int(round(MT.ST.bf(72 + 0.25 * k))) - 1 if k else shot.sim_start, name)
for ob in (L.root, L.pillar):
    MT.key_glow(ob, [(shot.sim_start, 0.38)])     # the top rarities clipped the frame to white
cam = rb_cam.Rig(lens=50, fstop=2.8)


def cam_fn(f):
    u = C.ease_in_out(shot.u(f))
    a = math.radians(-15 + 30 * u)
    r = 4.4 - 0.8 * u                      # outside the beam: item, beam and the room all read
    loc = Vector((r * math.sin(a), -r * math.cos(a), 1.25 - 0.15 * u))
    return dict(loc=loc, target=Vector((0, 0, 0.75)), focus=Vector((0, 0, 0.2)))


cam.key_range(shot.frames_all, cam_fn)
MT.light(shot, "legend", D, (0, 0, 0), cam_fn(shot.key_frame)["loc"])
MT.fx("embers", shot.sim_start, shot.render_end, (0, 0, 1.5), radius=2.5, height=4.0, count=80, seed=shot.seed)
shot.render()
