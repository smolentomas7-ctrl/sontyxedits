"""Side-view strip of the planted-foot walk (calibration)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import bpy
import rb_core as C, rb_motion as MO, rb_warrior as RW
a = C.script_args()
out = os.path.join(C.ROOT, "build/tests/motion"); os.makedirs(out, exist_ok=True)
C.reset_scene()
C.setup_render(scale=0.22, samples=1, motion_blur=False, volumetrics=False, bloom=0.0, gtao=False, ssr=False, soft_shadows=False, look="AgX - Base Contrast")
C.world(color=(0.85, 0.85, 0.85))
bpy.ops.mesh.primitive_plane_add(size=60)
w = RW.build_warrior("late", cape=False)
C.light("SUN", "sun", (0, 0, 10), energy=1.5, rot=(0.5, 0.2, 0), shadow=False)
cam = C.camera("cam", lens=35)
step = 15
at, plants = MO.walk_plan((0, 0, 0), 180, 1, 80, step, 0.68, stop_frame=70)
up = MO.POSES_W["stand"]
for f in range(1, 81):
    root, feet = at(f)
    ph = (f - 1) / (2 * step)
    upper = MO.blend(up, MO.walk_pose(ph % 1.0), 0.5)
    for j in list(upper):
        if j.startswith(("thigh", "shin", "foot", "toe")):
            del upper[j]
    pose, loc, rot = MO.solve_walk(w, upper, root, 180, feet)
    MO.key_pose(w, f, pose, loc, rot)
sc = bpy.context.scene
for f in [1, 8, 15, 22, 30, 37, 45, 52, 60, 75]:
    sc.frame_set(f)
    r, _ = at(f)
    cam.location = (4.2, r.y, 1.0); C.look_at(cam, (0, r.y, 0.85))
    sc.render.filepath = os.path.join(out, "walk_%03d.png" % f)
    bpy.ops.render.render(write_still=True)
print("DONE")
