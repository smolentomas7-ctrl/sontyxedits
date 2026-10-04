"""Representative vertical test frames for rb_env_forest (M101-M104, early-look warrior, 35 mm).

blender -b --factory-startup -P scenes/tests/forest_test.py -- --variant trees|waterfall|boards|hellgate|all
        [--scale 0.25] [--samples 6] [--frame 40] [--tag v1] [--seed 101] [--nowarrior] [--exposure 0]
Writes build/tests/rb_env_forest/<variant>_<tag>.png and prints build / render seconds.
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_env_forest as FO  # noqa: E402
import rb_motion as MO  # noqa: E402
import rb_warrior as RW  # noqa: E402

a = C.script_args()
variants = list(FO.VARIANTS) if a.get("variant", "all") == "all" else a["variant"].split(",")
scale = float(a.get("scale", 0.25))
samples = int(a.get("samples", 6))
frame = int(a.get("frame", 40))
tag = a.get("tag", "v1")
seed = int(a.get("seed", 101))
expo = float(a.get("exposure", 0.0))
out = os.path.join(C.ROOT, "build", "tests", "rb_env_forest")
os.makedirs(out, exist_ok=True)


def pose_warrior(w, mk, f_render):
    x, y, z = mk["warrior"]
    hd = mk["heading"]
    if mk.get("pose") == "walk":
        step, stride = 15, 0.68
        f0 = f_render - 23
        fwd = MO.heading_vec(hd)
        start = Vector((x, y, z)) - fwd * ((f_render - f0) / step * stride)
        at, _ = MO.walk_plan(start, hd, f0, f_render + 30, step, stride)
        up = MO.POSES_W["stand"]
        for f in range(f0, f_render + 3):
            root, feet = at(f)
            upper = MO.blend(up, MO.walk_pose(((f - f0) / (2 * step)) % 1.0), 0.5)
            upper = {j: r for j, r in upper.items() if not j.startswith(("thigh", "shin", "foot", "toe"))}
            p, loc, rot = MO.solve_walk(w, upper, root, hd, feet)
            MO.key_pose(w, f, p, loc, rot)
    else:
        for f in range(f_render - 2, f_render + 3):
            MO.key_pose(w, f, MO.POSES_W["stand"], (x, y, z), (0, 0, hd))
    for ob in w.rig.values():
        C.set_interp(ob, "LINEAR")


for v in variants:
    t0 = time.time()
    C.reset_scene()
    sc = C.setup_render(scale=scale, samples=samples, exposure=expo)
    F = FO.build_forest(v, seed)
    mk = F.marks
    w = None
    if not a.get("nowarrior"):
        w = RW.build_warrior("early")
        pose_warrior(w, mk, frame)
    cam = rb_cam.Rig(lens=35, fstop=5.6)
    wpos = Vector(mk["warrior"]) + Vector((0, 0, 1.2))
    cam.key_range(range(frame - 2, frame + 3), lambda f: dict(loc=mk["cam"], target=mk["aim"], focus=wpos))
    sc.frame_set(frame)
    FO.lights_forest(v, F, follow=w.root if w else None)
    sc.frame_set(frame)
    from bpy_extras.object_utils import world_to_camera_view as w2c
    probes = {"feet": Vector(mk["warrior"]), "head": Vector(mk["warrior"]) + Vector((0, 0, 1.9))}
    for k in ("gate", "lip", "impact", "lantern"):
        if k in mk:
            probes[k] = Vector(mk[k])
    for k, p in probes.items():
        q = w2c(sc, cam.cam, p)
        print("PROJ %s %-7s x %.2f  y_from_top %.2f  (safe: x<.87, .115<y<.80)" % (v, k, q.x, 1 - q.y))
    t1 = time.time()
    sc.render.filepath = os.path.join(out, "%s_%s.png" % (v, tag))
    bpy.ops.render.render(write_still=True)
    t2 = time.time()
    nv = sum(len(o.data.vertices) for o in sc.objects if o.type == "MESH" and o.data and o.visible_get())
    print("FOREST_TEST %s build %.1fs render %.1fs (scale %.2f, %d spp) trees %d rocks %d -> %s"
          % (v, t1 - t0, t2 - t1, scale, samples, len(F.trees), len(F.rocks), sc.render.filepath))
