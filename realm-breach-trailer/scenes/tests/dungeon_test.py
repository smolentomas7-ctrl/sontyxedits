"""Representative vertical test frames for rb_env_dungeon + rb_props.

xvfb-run -a -s "-screen 0 1920x1080x24" blender -b --factory-startup -P scenes/tests/dungeon_test.py -- \
    --shots a,b,c,d,e,f,g --scale 0.35 --samples 8 [--tag v1]
  a  floor1 wide, early warrior standing ready at the origin, 35 mm
  b  low insert 50 mm f/2.8: grey COMMON short-sword loot on the floor, early warrior's boots behind (M106)
  c  loot greatsword pillar in EPIC, 50 mm (M401, legend set)
  d  85 mm macro of the three life orbs, the right one dead and smoking (M303 / F2d)
  e  REBIRTH plaque glowing on black, mid-pulse (E6)
  f  struggle wide from 7 m high looking down, 24 mm, mid warrior in guard (M204)
  g  legend mid shot 50 mm, late warrior, a glowing ring on the floor (M402-ish)
Writes build/tests/rb_env_dungeon/<shot>_<tag>.png and prints build / render seconds.
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import rb_actions as RA  # noqa: E402
import rb_core as C  # noqa: E402
import rb_env_dungeon as DG  # noqa: E402
import rb_mat as M  # noqa: E402
import rb_motion as MO  # noqa: E402
import rb_props as PR  # noqa: E402

a = C.script_args()
shots = str(a.get("shots", "a")).split(",")
scale = float(a.get("scale", 0.35))
samples = int(a.get("samples", 8))
tag = a.get("tag", "v1")
out = os.path.join(C.ROOT, a.get("out", "build/tests/rb_env_dungeon"))
os.makedirs(out, exist_ok=True)


def setup():
    C.reset_scene()
    M._cache.clear()
    sc = C.setup_render(scale=scale, samples=samples, motion_blur=False, vol_end=140.0, vol_tile="8", vol_samples=48)
    DG.tune_eevee(sc)
    sc.frame_start, sc.frame_end = 1, 80
    return sc


def cam_at(loc, aim, lens, fstop=None, focus=None):
    cam = C.camera("cam", lens=lens, fstop=fstop, focus=focus)
    cam.location = loc
    C.look_at(cam, aim)
    if fstop and focus is None:
        cam.data.dof.focus_distance = (Vector(aim) - Vector(loc)).length
    return cam


def warrior(look, f, action="idle", pos=(0, 0, 0), heading=0.0):
    import rb_warrior as RW
    w = RW.build_warrior(look)
    if action == "stand":
        MO.key_pose(w, f, MO.POSES_W["stand"], pos, (0, 0, math.radians(heading)))
    else:
        p, loc, rot = RA.perform(w, f, action, f, 30, pos, heading)
        MO.key_pose(w, f, p, loc, rot)
    return w


def shot_a(sc):
    D = DG.build_dungeon("floor1")
    warrior("early", 1)
    c, aim, lens = D.marks["wide"]
    cam = cam_at(c, aim, lens, 5.6, 7.6)
    DG.lights_dungeon("floor1", D, (0, 0, 0), cam.location)
    return 1


def shot_b(sc):
    D = DG.build_dungeon("floor1")
    warrior("early", 1, "stand", (0.05, 0.55, 0))
    L = PR.loot("sword", "common", (0.15, -0.75, 0.0), rot_z=math.radians(62))
    cam = cam_at((0.55, -2.55, 0.25), (0.12, -0.6, 0.22), 50, 2.8)
    cam.data.dof.focus_distance = (Vector((0.15, -0.75, 0.05)) - cam.location).length
    DG.lights_dungeon("floor1", D, (0.05, 0.55, 0), cam.location)
    return 1


def shot_c(sc):
    D = DG.build_dungeon("legend")
    L = PR.loot("greatsword", "common", (0, 0, 0), rot_z=math.radians(28))
    PR.set_rarity(L, 1, "common")
    PR.set_rarity(L, 8, "epic")
    PR.set_rarity(L, 16, "mythic")
    cam = cam_at((0.45, -4.3, 1.15), (0.0, 0.0, 1.45), 50, 2.8, 4.3)
    DG.lights_dungeon("legend", D, (0, 0.6, 0), cam.location)
    return 10


def shot_d(sc):
    DG.void_world("deep")
    acc = DG.Acc()
    DG.cbox(acc, (0, 0.05, -0.15), (0.45, 0.22, 0.15), ch=0.03, blk=0.4)
    DG.cbox(acc, (0.1, 0.35, 0.25), (0.6, 0.1, 0.55), ch=0.03, blk=0.7)
    acc.build("ledge", DG.mat_masonry("deep"), bake=True)
    fog = DG.mat_fog("fog", density=0.25, height=0.6, color=(0.5, 0.52, 0.55), scale=2.0)
    DG.box_object("fogbox", (-1.5, -1.5, -0.3), (1.5, 1.5, 1.0), fog)
    O = PR.life_orbs((0, 0, 0))
    PR.orb_dark(O, 2, 10, 10)
    cam = cam_at((0.05, -1.55, 0.27), (0.0, 0.0, 0.2), 85, 2.8)
    C.light("SPOT", "key", (-0.9, -1.0, 1.1), color="#9CB4D0", energy=25.0, size=0.3, target=(0, 0, 0.2),
            spot_size=math.radians(40), shadow=True, volume=0.3)
    C.light("SPOT", "rim", (0.5, 0.9, 0.7), color="#FF6A1A", energy=12.0, size=0.2, target=(0, 0, 0.2),
            spot_size=math.radians(40), shadow=False, volume=0.2)
    return 30


def shot_e(sc):
    DG.void_world("legend")
    fog = DG.mat_fog("fog", density=0.06, height=3.0, color=(0.7, 0.6, 0.5), scale=0.6)
    DG.box_object("fogbox", (-3, -3, -1), (3, 3, 3), fog)
    P = PR.rebirth_plaque((0, 0, 1.0))
    PR.plaque_pulse(P, 10, 12)
    cam_at((0.0, -4.6, 1.0), (0.0, 0.0, 1.0), 50)
    C.light("AREA", "top", (0, -0.6, 2.4), color="#FFD8A0", energy=6.0, size=1.5, target=(0, 0, 1.0), shadow=False)
    return 14


def shot_f(sc):
    D = DG.build_dungeon("struggle")
    warrior("mid", 1, "idle", (0, 0, 0), 0.0)
    c, aim, lens = D.marks["high"]
    cam = cam_at(c, aim, lens, 8.0, 9.0)
    DG.lights_dungeon("struggle", D, (0, 0, 0), cam.location)
    return 1


def shot_g(sc):
    D = DG.build_dungeon("legend")
    warrior("late", 1, "idle", (0, 0, 0), 0.0)
    PR.ring((0.38, 0.2, 0.0), rot=(0, 0, 0.5), gem="#FFE9A8")
    c, aim, lens = D.marks["mid"]
    cam = cam_at(c, aim, lens, 2.8)
    DG.lights_dungeon("legend", D, (0, 0, 0), cam.location)
    return 1


for s in shots:
    sc = setup()
    t0 = time.time()
    f = globals()["shot_" + s](sc)
    sc.frame_set(f)
    t1 = time.time()
    sc.render.filepath = os.path.join(out, "%s_%s.png" % (s, tag))
    bpy.ops.render.render(write_still=True)
    t2 = time.time()
    nobj = len(bpy.data.objects)
    nv = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == "MESH")
    print("SHOT %s build %.1fs render %.1fs objects %d verts %d" % (s, t1 - t0, t2 - t1, nobj, nv), flush=True)
