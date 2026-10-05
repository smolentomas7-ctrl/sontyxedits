"""E4 — Beyond the gate: a soft flower meadow, petals drifting; he stands small again, at peace. Slow wide
pull-back, 24 mm; the title REALM BREACH and the tagline land in the edit over the calm sky."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_montage as MT  # noqa: E402
import rb_shot  # noqa: E402

import bpy  # noqa: E402
import rb_env_heaven as HV  # noqa: E402
import rb_warrior as RW  # noqa: E402

shot = rb_shot.Shot("E4", key_frame=2150)
Mw = HV.build_meadow(seed=shot.seed)
mk = Mw.marks
w = RW.build_warrior("late", rings=True, cape=True)
shot.register_cloth(w.cloths)
W = Vector(mk["warrior"])
MT.stand(w, shot, W, mk["heading"], ground=Mw.ground_z, look_up=6.0, crack=0.4, breath=0.7)
bpy.ops.object.effector_add(type="WIND", location=tuple(W + Vector((-3, 2, 1.2))))
wind = bpy.context.object
wind.rotation_euler = (math.radians(90), 0, math.radians(-120))
wind.field.strength = 1.2
wind.field.flow = 0.3
wind.field.noise = 0.6
wind.field.seed = 3
cam = rb_cam.Rig(lens=24, fstop=8.0)
CN, CF, AIM = Vector(mk["cam"]), Vector(mk.get("cam_far", mk["cam"])), Vector(mk["aim"])
cam.key_range(shot.frames_all, lambda f: dict(loc=CN.lerp(CF, C.ease_in_out(C.clamp01(shot.u(f)))), target=AIM,
                                              focus=W + Vector((0, 0, 1.0))))
shot.scene.frame_set(shot.key_frame)
HV.lights_meadow(Mw, warrior=tuple(W), cam=tuple(CN), follow=w.root)
# petals: the meadow set animates its own (frame-driven), no extra layer
shot.render()
