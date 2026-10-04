"""Fast silhouette renders of a posed character (for calibrating poses).

blender -b -P scenes/tests/silhouette.py -- --who warrior|god --poses name1,name2 --views front,side --out DIR
Poses come from rb_motion.POSES_W / POSES_G (or 'walk:0.25' style phases).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import bpy  # noqa: E402

import rb_core as C  # noqa: E402
import rb_motion as MO  # noqa: E402

a = C.script_args()
who = a.get("who", "warrior")
poses = a.get("poses", "stand").split(",")
views = a.get("views", "front,side").split(",")
out = os.path.join(C.ROOT, a.get("out", "build/tests/motion"))
os.makedirs(out, exist_ok=True)

C.reset_scene()
C.setup_render(scale=0.22, samples=1, motion_blur=False, volumetrics=False, bloom=0.0, gtao=False, ssr=False,
               soft_shadows=False, look="AgX - Base Contrast")
C.world(color=(0.85, 0.85, 0.85), strength=1.0)
bpy.ops.mesh.primitive_plane_add(size=40)
if who == "warrior":
    import rb_warrior as RW
    ch = RW.build_warrior("late", cape=False)
    H = 1.9
else:
    import rb_god as RG
    ch = RG.build_god()
    H = 5.7
C.light("SUN", "sun", (0, 0, 10), energy=1.5, rot=(0.5, 0.2, 0), shadow=False)
cam = C.camera("cam", lens=50)
sc = bpy.context.scene
for i, pn in enumerate(poses):
    f = i + 1
    if pn.startswith("walk:"):
        MO.key_pose(ch, f, MO.walk_pose(float(pn.split(":")[1]), who))
    else:
        MO.key_pose(ch, f, (MO.POSES_W if who == "warrior" else MO.POSES_G)[pn])
for i, pn in enumerate(poses):
    f = i + 1
    sc.frame_set(f)
    for v in views:
        d = H * 2.6
        loc = {"front": (0, -d, H * 0.5), "side": (d, 0, H * 0.5), "back": (0, d, H * 0.5),
               "q34": (d * 0.7, -d * 0.7, H * 0.55)}[v]
        cam.location = loc
        C.look_at(cam, (0, 0, H * 0.5))
        sc.render.filepath = os.path.join(out, "%s_%02d_%s_%s.png" % (who, i, pn.replace(":", "-"), v))
        bpy.ops.render.render(write_still=True)
print("DONE")
