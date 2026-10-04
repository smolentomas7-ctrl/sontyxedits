"""M510 — Held hero shot: the full late-look warrior, low angle, 24 mm; cape lifting, blade burning.
The montage's last image before the return to the fight."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_intro  # noqa: E402
import rb_mat as M  # noqa: E402
import rb_motion as MO  # noqa: E402
import rb_shot  # noqa: E402
import rb_story as ST  # noqa: E402

shot = rb_shot.Shot("M510", key_frame=1312)
import rb_env_arena as AR  # noqa: E402
import rb_warrior as RW  # noqa: E402

A = AR.build_arena(variant="approach")
w = RW.build_warrior("late", rings=True)
shot.register_cloth(w.cloths)
pos = Vector((0.0, 1.5, 0.0))
heading = 160.0
for f in shot.frames_all:
    br = math.sin(f / 30 * 2 * math.pi / 3.2)
    body = {"spine": (-2 + 0.6 * br, 0, 0), "chest": (-6 + 0.8 * br, 0, 0), "head": (-8, 0, 0), "neck": (-2, 0, 0)}
    base = MO.add(MO.POSES_W["stand"], body)
    base = {k: v for k, v in base.items() if not k.startswith(("thigh", "shin", "foot", "toe"))}
    p = MO.sword_pose(w, base, ST.wl(Vector((-0.1, -0.4, 1.02)), pos, heading), ST.wd(Vector((0.02, -0.22, -1.0)), heading),
                      two_hands=True, root_loc=pos, root_rot=(0, 0, heading), left_slide=0.1)
    feet = {"L": (ST.wl(Vector((0.2, -0.18, 0.092)), pos, heading), 0.0),
            "R": (ST.wl(Vector((-0.2, 0.22, 0.092)), pos, heading), 0.0)}
    pose, loc, rot = MO.solve_walk(w, p, pos, heading, feet, hip_drop=0.02)
    MO.key_pose(w, f, pose, loc, rot)
    rb_intro._key_blade(w, f, 5.0 + 0.6 * math.sin(f * 0.4))
    M.key_ctrl(w.mats["eyes"], "eye_glow", f, 45.0)
# wind lifts the cape (deterministic force field)
bpy.ops.object.effector_add(type="WIND", location=(pos.x, pos.y + 6, 1.2))
wf = bpy.context.object
wf.rotation_euler = (math.radians(90), 0, math.radians(-20))
wf.field.strength = 2.2
wf.field.flow = 0.4
wf.field.noise = 0.8
wf.field.seed = 7

cam = rb_cam.Rig(lens=24, fstop=5.6)


def cam_fn(f):
    u = C.ease_out(shot.u(f))
    loc = pos + Vector((0.55, 2.75 - 0.15 * u, 0.32))
    return dict(loc=loc, target=pos + Vector((0.0, 0.0, 1.72)), focus=pos + Vector((0, 0.2, 1.2)))


cam.key_range(shot.frames_all, cam_fn)
L = AR.lights_walk(warrior=tuple(pos), cam=tuple(cam_fn(shot.key_frame)["loc"]))
C.light("SPOT", "M510_gold", pos + Vector((-2.2, -2.0, 4.5)), color="#F2B544", energy=900, size=0.5,
        target=pos + Vector((0, 0, 1.4)), spot_size=math.radians(30), shadow=False)
try:
    import rb_vfx as VFX
    VFX.embers(shot.sim_start, shot.render_end, center=tuple(pos + Vector((0, 0.5, 1.5))), seed=shot.seed)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
