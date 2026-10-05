"""F6 — Slow push into an extreme close-up of the visor: YOU LET ME LIVE. Eyes and blade crack blaze; ember overtakes blue. 85 mm. (VO9)"""
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

shot = rb_shot.Shot("F6", key_frame=1910)
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


h = Vector(ST._RISE) + Vector((0, 0, 1.763))
cam = rb_cam.Rig(lens=85, fstop=5.6)


import rb_motion as MO  # noqa: E402


def _head(f):
    return MO.fk(S["w"], *ST.warrior_battle(S["w"], f))["head"][0]


_H0 = _head(shot.key_frame)


def cam_fn(f):
    # the camera rides with the head: the god-attack wind-up (from ~1910) arches him back by up to ~18 cm, far outside
    # the few millimetres of depth of field at 0.5 m
    hh = h + (_head(f) - _H0)
    u = C.ease_in(shot.u(f))
    return dict(loc=hh + Vector((0.03, 1.1 - 0.55 * u, -0.02)), target=hh, focus=hh + Vector((0, 0.15, 0)))


cam.key_range(shot.frames_all, cam_fn)
AR.lights_walk(warrior=tuple(ST._RISE), cam=tuple(cam_fn(shot.key_frame)["loc"]))
# soft ember side-key so the helm steel reads around the slit
_hp = ST.STOP if "ST._RISE" not in open(__file__).read() else Vector(ST._RISE)
C.light("AREA", "ecu_key", Vector(_hp) + Vector((-0.75, 0.55, 1.95)), color="#FF8A4A", energy=22, size=0.6,
        target=Vector(_hp) + Vector((0, 0, 1.76)), shadow=False)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
