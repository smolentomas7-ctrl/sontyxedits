"""O9 — Extreme close-up on the visor: the eyes flare. Static, 85 mm. (VO3; the build starts)"""
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

shot = rb_shot.Shot("O9", key_frame=585)
S = rb_intro.build(shot, variant="approach")
import rb_env_arena as AR  # noqa: E402

head = ST.STOP + Vector((0, 0, 1.763))
cam = rb_cam.Rig(lens=85, fstop=5.6)
loc = head + Vector((-0.05, 0.5, 0.0))
cam.key_range(shot.frames_all, lambda f: dict(loc=loc, target=head, focus=head + Vector((0, 0.15, 0))))
AR.lights_walk(warrior=tuple(ST.STOP), cam=tuple(loc))
C.light("AREA", "O9_bluefill", head + Vector((0.9, 2.0, 0.7)), color="#6FA8FF", energy=30, size=1.0,
        target=head, shadow=False)
# soft ember side-key so the helm steel reads around the slit
_hp = ST.STOP if "ST._RISE" not in open(__file__).read() else Vector(ST._RISE)
C.light("AREA", "ecu_key", Vector(_hp) + Vector((-0.75, 0.55, 1.95)), color="#FF8A4A", energy=22, size=0.6,
        target=Vector(_hp) + Vector((0, 0, 1.76)), shadow=False)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
