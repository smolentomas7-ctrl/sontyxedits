"""CHECKPOINT 1 — character turnarounds under neutral light.

blender -b -P scenes/turnarounds.py -- --char warrior_late --scale 0.5 --out build/characters
Characters: warrior_late, warrior_early, god. Views: front, side, back, closeup.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import bpy  # noqa: E402

import rb_core as C  # noqa: E402

args = C.script_args()
char = args.get("char", "warrior_late")
scale = float(args.get("scale", 0.5))
samples = int(args.get("samples", 16))
out = os.path.join(C.ROOT, args.get("out", "build/characters"))
views = args.get("views", "front,side,back,closeup").split(",")

C.reset_scene()
C.setup_render(scale=scale, samples=samples, motion_blur=False, volumetrics=False, bloom=0.05,
               look="AgX - Base Contrast")
C.world_gradient(top=(0.11, 0.113, 0.12), bottom=(0.012, 0.012, 0.013), strength=1.0)

# studio floor
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
floor = bpy.context.object
import rb_mat as M  # noqa: E402

floor.data.materials.append(M.matte("studio_floor", (0.025, 0.025, 0.026), rough=0.75))

if char.startswith("warrior"):
    import rb_warrior as RW  # noqa: E402

    look = char.split("_")[1]
    w = RW.build_warrior(look=look, rings=(look == "late"))
    height, focus_head = 1.9, (0, -0.02, 1.76)
    # relaxed stance: arms lowered a touch, sword hanging forward
    RW.pose(w, 1, {"upperarm_L": (0, -6, 0), "upperarm_R": (0, 6, 0), "forearm_R": (-25, 0, 0)})
    sim_frames = 40 if w.cape else 1
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, sim_frames
    for cl in getattr(w, "cloths", []):
        cl.point_cache.frame_start, cl.point_cache.frame_end = 1, sim_frames
    closeup = dict(loc=(0.0, -0.75, 1.765), target=focus_head, lens=85, fstop=2.8)
else:
    import rb_god as RG  # noqa: E402

    g = RG.build_god()
    height, focus_head = 5.7, (0, 0, 5.2)
    sim_frames = 1
    closeup = dict(loc=(-1.35, -2.35, 4.55), target=(0, -0.05, 5.15), lens=85, fstop=4.0)
    # film-like key for the face check: cold underlight from below-front
    C.light("SPOT", "UnderBlue", (0.6, -2.2, 3.6), color="#6FA8FF", energy=900, size=0.3, target=(0, 0, 5.1),
            spot_size=0.6, shadow=True)

H = height
dist = H * 2.35
key = C.light("AREA", "Key", (-2.5 * H / 1.9, -3.2 * H / 1.9, 2.8 * H / 1.9), energy=260 * (H / 1.9) ** 2, size=2.5 * H / 1.9,
              target=(0, 0, H * 0.55), color=(1.0, 0.97, 0.93), shadow=True)
fill = C.light("AREA", "Fill", (3.0 * H / 1.9, -2.0 * H / 1.9, 1.6 * H / 1.9), energy=70 * (H / 1.9) ** 2, size=3.0 * H / 1.9,
               target=(0, 0, H * 0.5), color=(0.9, 0.95, 1.0), shadow=False)
rim = C.light("AREA", "Rim", (0.5, 3.2 * H / 1.9, 2.6 * H / 1.9), energy=320 * (H / 1.9) ** 2, size=1.5 * H / 1.9,
              target=(0, 0, H * 0.6), color=(1.0, 0.75, 0.55), shadow=False)

cam = C.camera("Cam", lens=50, fstop=None)
sc = bpy.context.scene
for f in range(1, sim_frames + 1):
    sc.frame_set(f)

VIEWS = {
    "front": ((0, -dist, H * 0.52), (0, 0, H * 0.5)),
    "side": ((dist, 0, H * 0.52), (0, 0, H * 0.5)),
    "back": ((0, dist, H * 0.52), (0, 0, H * 0.5)),
    "q34": ((-dist * 0.7, -dist * 0.7, H * 0.55), (0, 0, H * 0.5)),
}
os.makedirs(out, exist_ok=True)
for v in views:
    if v == "closeup":
        cam.data.lens = closeup["lens"]
        cam.location = closeup["loc"]
        C.look_at(cam, closeup["target"])
        cam.data.dof.use_dof = True
        cam.data.dof.focus_distance = (cam.location - __import__("mathutils").Vector(closeup["target"])).length
        cam.data.dof.aperture_fstop = closeup["fstop"]
    else:
        cam.data.dof.use_dof = False
        cam.data.lens = 50
        loc, tgt = VIEWS[v]
        cam.location = loc
        C.look_at(cam, tgt)
    sc.render.filepath = os.path.join(out, "%s_%s.png" % (char, v))
    bpy.ops.render.render(write_still=True)
    print("WROTE", sc.render.filepath)
