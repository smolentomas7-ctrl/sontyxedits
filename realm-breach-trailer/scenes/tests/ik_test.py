"""Silhouettes of IK sword poses (calibration). Character at origin facing -Y."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import bpy
from mathutils import Vector
import rb_core as C, rb_motion as MO, rb_warrior as RW
out = os.path.join(C.ROOT, "build/tests/motion"); os.makedirs(out, exist_ok=True)
C.reset_scene()
C.setup_render(scale=0.22, samples=1, motion_blur=False, volumetrics=False, bloom=0.0, gtao=False, ssr=False, soft_shadows=False, look="AgX - Base Contrast")
C.world(color=(0.85, 0.85, 0.85))
bpy.ops.mesh.primitive_plane_add(size=40)
w = RW.build_warrior("late", cape=False)
C.light("SUN", "sun", (0, 0, 10), energy=1.5, rot=(0.5, 0.2, 0), shadow=False)
cam = C.camera("cam", lens=50)
base = MO.POSES_W["stand"]
SPECS = {
  "salute": dict(grip=(-0.12, -0.32, 1.42), blade=(0.05, -0.25, 1.0), two=True),
  "point": dict(grip=(-0.12, -0.62, 1.42), blade=(0.0, -1.0, 0.04), two=False),
  "overhead": dict(grip=(-0.02, 0.05, 2.05), blade=(0.0, 0.55, 0.85), two=True),
  "strike_end": dict(grip=(-0.05, -0.55, 0.85), blade=(0.0, -0.75, -0.65), two=True),
  "guard": dict(grip=(-0.06, -0.33, 1.05), blade=(0.03, -0.5, 0.86), two=True),
  "clash": dict(grip=(-0.02, -0.5, 1.38), blade=(0.15, -0.95, 0.3), two=True),
}
names = list(SPECS)
for i, n in enumerate(names):
    sp = SPECS[n]
    p = MO.sword_pose(w, base, Vector(sp["grip"]), Vector(sp["blade"]), two_hands=sp["two"])
    MO.key_pose(w, i + 1, p)
sc = bpy.context.scene
for i, n in enumerate(names):
    sc.frame_set(i + 1)
    for v, loc in (("front", (0, -4.9, 1.0)), ("side", (4.9, 0, 1.0)), ("q34", (3.4, -3.4, 1.1))):
        cam.location = loc; C.look_at(cam, (0, 0, 1.0))
        sc.render.filepath = os.path.join(out, "ik_%d_%s_%s.png" % (i, n, v))
        bpy.ops.render.render(write_still=True)
print("DONE")
