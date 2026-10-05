"""F7 — R God Attack on U: golden-white blast hits the Fallen God; the camera whips with the strike; white floods the frame. 24 mm."""
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

shot = rb_shot.Shot("F7", key_frame=1935)   # just after the white flash in the edit: the blast reads
S = rb_intro.build(shot, variant="duel", act="battle")
import rb_env_arena as AR  # noqa: E402


r = Vector(ST._RISE)
cam = rb_cam.Rig(lens=24, fstop=8.0)
F_HIT = int(ST.bf(128.0)) - 1
F_WHIP = int(ST.bf(127.6))
cam.shake(F_HIT, amp=0.08, seed=shot.seed)
loc = r + Vector((-1.0, -3.2, 0.6))
T_WARRIOR = r + Vector((0.0, 0.0, 1.3))
T_WIDE = r + Vector((0.2, 4.5, 1.6))         # at impact: warrior lower right, the god upper centre


def cam_fn(f):
    # camera whips (tilt + pan, motion-blurred) from the warrior's wind-up to the god as the blast lands
    u = C.ease_in_out(C.clamp01((f - F_WHIP) / max(1, F_HIT - F_WHIP)))
    drift = Vector((0, -0.25, 0.05)) * C.clamp01((f - F_HIT) / 20.0)
    return dict(loc=loc + drift, target=T_WARRIOR.lerp(T_WIDE, u), focus=4.0)


cam.key_range(shot.frames_all, cam_fn)
AR.lights_duel(warrior=tuple(r), cam=tuple(loc))
try:
    import rb_vfx as VFX
    tip = ST.wl(Vector((-0.05, -1.4, 1.6)), r)
    VFX.god_attack(F_HIT, tuple(tip), tuple(ST.GOD_POS + Vector((0, 0, 3.6))), seed=shot.seed)
except Exception as e:
    print("vfx missing:", e)
rb_intro.clear_view(rb_intro.cam_samples(cam, shot), rb_intro.cam_target_sample(cam, shot))
shot.render()
