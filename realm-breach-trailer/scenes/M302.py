"""M302 — 50% slow motion: he falls backwards to the floor; ash rises. Slow dolly from low side, 85 mm;
the landing sits on the beat."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

shot = rb_shot.Shot("M302", key_frame=1012)
D, w = MT.scene(shot, "deep", look="mid")
F_LAND = MT.imp(68)
P = Vector((0, 0, 0))
MT.act(w, shot, "fall", F_LAND, 16, P, 180, slowmo=0.5)
cam = rb_cam.Rig(lens=85, fstop=2.0)
# high in front (his feet side, ~43 deg down): he falls back away from the lens with his front and helm turned up to
# us, so the vertical frame holds him; the camera tracks his chest. (Side-on 85 mm lost him as he went down; 3 m away
# at 14 deg down showed a headless chest close-up.)


def chest(f):
    pose_loc_rot = MT.act_pose(w, "fall", f, F_LAND, 16, P, 180, slowmo=0.5)
    return MT.joint_world(w, pose_loc_rot, "chest")


def cam_fn(f):
    c = chest(f)
    loc = Vector((0.35, 2.75 - 0.35 * C.ease_in_out(shot.u(f)), 4.0))   # slow push-in from above
    return dict(loc=loc, target=c, focus=(c - loc).length)


cam.key_range(shot.frames_all, cam_fn)
MT.light(shot, "deep", D, (0, -0.4, 0), (0.35, 2.75, 4.0), follow=w.root)
C.parent_keep(MT.cold_key(P + Vector((0, 0, 0.9)), (0.35, 2.75, 4.0), side=1.0, energy=200.0, dist=2.2), w.root)
MT.fx("ash", shot.sim_start, shot.render_end, (0, -0.5, 0.6), radius=2.0, height=2.5, seed=shot.seed, rise=0.6)
MT.fx("dust_puff", F_LAND, (0.0, -0.9, 0.0), seed=shot.seed + 1, scale=1.6)
shot.render()
