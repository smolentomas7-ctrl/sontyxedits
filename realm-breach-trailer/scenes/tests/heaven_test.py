"""Test frames for rb_env_heaven (E3 gate of heaven, E4 flower meadow), vertical 9:16.

blender -b --factory-startup -P scenes/tests/heaven_test.py -- --which a,b,c [--scale 0.35] [--samples 8]
        [--frame 60] [--tag v1] [--repeat N] [--nowarrior] [--open 0.45]
  a  E3: late-look warrior (no cape) from behind walking toward the gate, warm light past him, 35 mm
  b  E4: wide pull-back end over the meadow (cam_far), warrior tiny in the lower-middle third, 24 mm
  c  the open gate alone, mid (35 mm from cam_gate); also checks that keying CTRL_open moves the doors
Writes build/tests/rb_env_heaven/<which>_<tag>.png; prints build / render seconds and screen probes.
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import bpy  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view as w2c  # noqa: E402
from mathutils import Vector  # noqa: E402

import rb_cam  # noqa: E402
import rb_core as C  # noqa: E402
import rb_env_heaven as HV  # noqa: E402
import rb_motion as MO  # noqa: E402
import rb_warrior as RW  # noqa: E402

a = C.script_args()
which = a.get("which", "a,b,c").split(",")
scale = float(a.get("scale", 0.35))
samples = int(a.get("samples", 8))
frame = int(a.get("frame", 60))
tag = a.get("tag", "v1")
repeat = int(a.get("repeat", 0))
out = os.path.join(C.ROOT, "build", "tests", "rb_env_heaven")
os.makedirs(out, exist_ok=True)


def walk(w, mark, hd, f_render):
    step, stride = 15, 0.64
    f0 = f_render - 23
    fwd = MO.heading_vec(hd)
    start = Vector(mark) - fwd * ((f_render - f0) / step * stride)
    at, _ = MO.walk_plan(start, hd, f0, f_render + 40, step, stride)
    for f in range(f0, f_render + 3 + repeat):
        root, feet = at(f)
        upper = MO.blend(MO.POSES_W["stand"], MO.walk_pose(((f - f0) / (2 * step)) % 1.0), 0.6)
        upper = {j: r for j, r in upper.items() if not j.startswith(("thigh", "shin", "foot", "toe"))}
        p, loc, rot = MO.solve_walk(w, upper, root, hd, feet)
        MO.key_pose(w, f, p, loc, rot)
    for ob in w.rig.values():
        C.set_interp(ob, "LINEAR")


def stand(w, pos, hd, f_render):
    for f in range(f_render - 2, f_render + 3 + repeat):
        MO.key_pose(w, f, MO.POSES_W["stand"], tuple(pos), (0, 0, hd))
    for ob in w.rig.values():
        C.set_interp(ob, "LINEAR")


for v in which:
    t0 = time.time()
    C.reset_scene()
    sc = C.setup_render(scale=scale, samples=samples)
    rng_f = range(frame - 2, frame + 3 + repeat)
    w = None
    if v in ("a", "c"):
        G = HV.build_gate(C.video.seed_for("E3"))
        mk = G.marks
        if v == "a":
            if not a.get("nowarrior"):
                w = RW.build_warrior("late", cape=False)
                walk(w, mk["warrior"], mk["heading"], frame)
            cam = rb_cam.Rig(lens=35, fstop=5.6)
            cam.key_range(rng_f, lambda f: dict(loc=mk["cam"], target=mk["aim"],
                                                focus=Vector(mk["warrior"]) + Vector((0, 0, 1.2))))
            sc.frame_set(frame)
            HV.lights_gate(G, warrior=mk["warrior"], cam=mk["cam"], follow=w.root if w else None)
            probes = {"feet": Vector(mk["warrior"]), "head": Vector(mk["warrior"]) + Vector((0, 0, 1.9)),
                      "gap": Vector(mk["gap"]), "crown": Vector((0, HV.GATE_Y, HV.ZE + 6.7))}
        else:
            op = float(a.get("open", 0.6))
            G.key_ctrl("open", frame - 10, 0.15)
            G.key_ctrl("open", frame, op)
            cam = rb_cam.Rig(lens=35, fstop=8.0)
            cam.key_range(rng_f, lambda f: dict(loc=mk["cam_gate"], target=mk["aim_gate"], focus=Vector(mk["gap"])))
            sc.frame_set(frame - 10)
            r0 = math.degrees(G.doors[0].matrix_world.to_euler().z)
            sc.frame_set(frame)
            r1 = math.degrees(G.doors[0].matrix_world.to_euler().z)
            print("DOOR_L yaw at open 0.15 -> %.1f deg, at open %.2f -> %.1f deg" % (r0, op, r1))
            HV.lights_gate(G)
            probes = {"gap": Vector(mk["gap"]), "crown": Vector((0, HV.GATE_Y, HV.ZE + 6.7)),
                      "base": Vector(mk["steps"])}
    else:
        Mw = HV.build_meadow(C.video.seed_for("E4"))
        mk = Mw.marks
        print("COUNTS", Mw.counts)
        W = Vector(mk["warrior"])
        if not a.get("nowarrior"):
            w = RW.build_warrior("late", cape=False)
            stand(w, W, mk["heading"], frame)
        cam = rb_cam.Rig(lens=24, fstop=8.0)
        key = a.get("cam", "cam_far")
        cam.key_range(rng_f, lambda f: dict(loc=mk[key], target=mk["aim"], focus=W + Vector((0, 0, 1.0))))
        sc.frame_set(frame)
        HV.lights_meadow(Mw, follow=w.root if w else None)
        probes = {"feet": W, "head": W + Vector((0, 0, 1.9))}
    sc.frame_set(frame)
    for k, p in probes.items():
        q = w2c(sc, cam.cam, p)
        print("PROBE %s %s: x=%d y=%d (full-res px, y from top)" % (v, k, q.x * 1080, (1 - q.y) * 1920))
    tb = time.time() - t0
    path = os.path.join(out, "%s_%s.png" % (v, tag))
    sc.render.filepath = path
    t1 = time.time()
    bpy.ops.render.render(write_still=True)
    tr = time.time() - t1
    print("TIMING %s build %.1fs render %.1fs (scale %.2f, %d spp) -> %s" % (v, tb, tr, scale, samples, path))
    for k in range(repeat):
        sc.frame_set(frame + 1 + k)
        t1 = time.time()
        bpy.ops.render.render(write_still=False)
        print("TIMING %s repeat frame %d render %.1fs" % (v, frame + 1 + k, time.time() - t1))
