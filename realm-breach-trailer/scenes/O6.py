"""O6 — Extreme close-up on the visor slit; ember eyes; breathing micro-move. 85 mm, very shallow. (VO1)"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_intro  # noqa: E402
import rb_shot  # noqa: E402
import rb_story as ST  # noqa: E402

shot = rb_shot.Shot("O6", key_frame=300)
S = rb_intro.build(shot, variant="approach", god=True)
import rb_env_arena as AR  # noqa: E402

head = ST.STOP + Vector((0, 0, 1.763))
cam = rb_cam.Rig(lens=85, fstop=5.6)
cam.handheld(amp=0.0025, rot_deg=0.12, freq=0.35, seed=shot.seed)


def cam_fn(f):
    br = 0.004 * math.sin(f / 30 * 2 * math.pi / 3.6)
    return dict(loc=head + Vector((0.02, 0.62, -0.03 + br)), target=head + Vector((0, 0, 0.0)),
                focus=head + Vector((0, 0.15, 0)))


cam.key_range(shot.frames_all, cam_fn)
AR.lights_walk(warrior=tuple(ST.STOP), cam=tuple(cam_fn(shot.key_frame)["loc"]))
C.light("AREA", "O6_bluefill", head + Vector((-0.8, 2.2, 0.9)), color="#6FA8FF", energy=35, size=1.2,
        target=head, shadow=False)
# soft ember side-key so the helm steel reads around the slit
_hp = ST.STOP if "ST._RISE" not in open(__file__).read() else Vector(ST._RISE)
C.light("AREA", "ecu_key", Vector(_hp) + Vector((-0.75, 0.55, 1.95)), color="#FF8A4A", energy=22, size=0.6,
        target=Vector(_hp) + Vector((0, 0, 1.76)), shadow=False)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
