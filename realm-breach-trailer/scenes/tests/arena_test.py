"""Representative vertical test frames of the Floor 999 arena (rb_env_arena).

blender -b --factory-startup -P scenes/tests/arena_test.py -- --shots a,b,c --scale 0.25 --samples 6 [--build-only]
  a  O2      late warrior from behind (0.6 m high, 3 m back, 35 mm), pillars towering, god far ahead
  b  O5 end  Fallen God from a low angle (24 mm, ~4 m away, looking up), blue underlight, cracks ignited
  c  F1e     wide 24 mm, warrior and god ~5 m apart in the 'duel' arena, the god towering in the top half
  d  O4      ground-level 50 mm insert: sabaton planted on the cracked, wet, glowing floor at WARRIOR_STOP
  e  E2      'after' arena from a high crane position (35 mm): shattered halo on the floor, exhausted warrior
Writes build/tests/rb_env_arena/<shot>_s<scale>_<samples>spp.png and prints build / render seconds.
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import rb_core as C  # noqa: E402
import rb_env_arena as AR  # noqa: E402
import rb_mat as M  # noqa: E402
import rb_motion as MO  # noqa: E402

a = C.script_args()
shots = str(a.get("shots", "a,b,c")).split(",")
scale = float(a.get("scale", 0.25))
samples = int(a.get("samples", 6))
out = os.path.join(C.ROOT, a.get("out", "build/tests/rb_env_arena"))
tag = a.get("tag", "")
build_only = bool(a.get("build-only", False))
os.makedirs(out, exist_ok=True)
FRAME = 30


def setup():
    C.reset_scene()
    import rb_mat
    rb_mat._cache.clear()
    sc = C.setup_render(scale=scale, samples=samples, motion_blur=False, **AR.RENDER_KW)
    AR.tune_eevee(sc)
    sc.frame_start, sc.frame_end = 1, 60
    return sc


def walk_pose_at(w, w_start, f, heading=180.0):
    """Planted-foot heavy walk (rb_motion.walk_plan) evaluated at frame f."""
    step = 15
    at, _ = MO.walk_plan(w_start, heading, 1, 80, step, 0.68)
    root, feet = at(f)
    upper = MO.blend(MO.POSES_W["stand"], MO.walk_pose(((f - 1) / (2 * step)) % 1.0), 0.5)
    for j in list(upper):
        if j.startswith(("thigh", "shin", "foot", "toe")):
            del upper[j]
    return MO.solve_walk(w, upper, root, heading, feet)


def shot_a(sc):
    A = AR.build_arena("approach")
    import rb_god as RG
    g = RG.build_god()
    g.root.location = AR.GOD_POS
    import rb_warrior as RW
    w = RW.build_warrior("late")
    pose, loc, rot = walk_pose_at(w, (0.0, -16.2, 0.0), 22)
    MO.key_pose(w, FRAME, pose, loc, rot)
    W = Vector(loc)
    cam = C.camera("cam", lens=35, fstop=4.0)
    cam.location = W + Vector((-0.7, -3.0, 0.6 - W.z))
    # frame centre between the warrior (right of centre) and the far god (left of centre), tilted up 8 deg
    C.look_at(cam, cam.location + Vector((1.25, 9.92, 1.4)))
    cam.data.dof.focus_distance = 3.0
    L = AR.lights_walk(warrior=(W.x, W.y, 0.0), cam=cam.location)
    return A, L


def shot_b(sc):
    A = AR.build_arena("approach")
    import rb_god as RG
    g = RG.build_god()
    g.root.location = AR.GOD_POS
    M.ctrl_node(g.mats["stone"], "ignite").outputs[0].default_value = 12.0
    cam = C.camera("cam", lens=24, fstop=8.0)
    Gp = Vector(AR.GOD_POS)
    cam.location = Gp + Vector((0.35, -4.0, 0.3))
    C.look_at(cam, Gp + Vector((0.0, 0.0, 3.9)))
    cam.data.dof.focus_distance = 5.0
    L = AR.lights_god_reveal(cam=cam.location)
    return A, L


def shot_c(sc):
    A = AR.build_arena("duel")
    import rb_god as RG
    g = RG.build_god()
    g.root.location = AR.GOD_POS
    import rb_warrior as RW
    w = RW.build_warrior("late")
    Wp = Vector((0.15, 8.9, 0.0))
    pose = MO.sword_pose(w, MO.POSES_W["point"], Wp + Vector((-0.15, 0.55, 1.25)), (0.05, 0.75, 0.66),
                         root_loc=Wp, root_rot=(0, 0, 180))
    MO.key_pose(w, FRAME, pose, Wp, (0, 0, 180))
    cam = C.camera("cam", lens=24, fstop=8.0)
    cam.location = Vector((-3.1, 4.4, 0.6))
    C.look_at(cam, cam.location + Vector((3.9, 8.9, 1.75)))
    cam.data.dof.focus_distance = 9.0
    L = AR.lights_duel(warrior=Wp, cam=cam.location)
    return A, L


def shot_d(sc):
    A = AR.build_arena("approach")
    import rb_god as RG
    g = RG.build_god()
    g.root.location = AR.GOD_POS
    import rb_warrior as RW
    w = RW.build_warrior("late")
    Wp = Vector(AR.WARRIOR_STOP)
    MO.key_pose(w, FRAME, MO.POSES_W["stand"], Wp, (0, 0, 180))
    cam = C.camera("cam", lens=50, fstop=2.0)
    cam.location = Wp + Vector((-1.1, -1.5, 0.14))
    C.look_at(cam, Wp + Vector((0.05, 0.25, 0.32)))
    cam.data.dof.focus_distance = (Vector(cam.location) - (Wp + Vector((0.12, 0.0, 0.1)))).length
    L = AR.lights_walk(warrior=Wp, cam=cam.location)
    return A, L


def shot_e(sc):
    A = AR.build_arena("after")
    import rb_warrior as RW
    w = RW.build_warrior("late")
    Wp = Vector((0.4, 8.3, 0.0))
    MO.key_pose(w, FRAME, MO.blend(MO.POSES_W["stand"], MO.POSES_W["kneel"], 0.25), Wp, (0, 0, 165))
    cam = C.camera("cam", lens=35, fstop=8.0)
    cam.location = Vector((-4.2, -1.5, 6.5))
    C.look_at(cam, Vector((0.6, 12.5, 0.4)))
    cam.data.dof.focus_distance = 12.0
    L = AR.lights_after(warrior=Wp, cam=cam.location)
    return A, L


for s in shots:
    t0 = time.time()
    sc = setup()
    A, L = {"a": shot_a, "b": shot_b, "c": shot_c, "d": shot_d, "e": shot_e}[s](sc)
    sc.frame_set(FRAME)
    nshadow = sum(1 for o in L.values() if o.data.use_shadow)
    t1 = time.time()
    print("BUILD %s %.1fs  lights=%d shadow=%d  objects=%d" % (s, t1 - t0, len(L), nshadow, len(bpy.data.objects)))
    if build_only:
        continue
    sc.render.filepath = os.path.join(out, "%s_s%g_%dspp%s.png" % (s, scale, samples, tag))
    bpy.ops.render.render(write_still=True)
    print("RENDER %s %.1fs -> %s" % (s, time.time() - t1, sc.render.filepath))
print("DONE")
