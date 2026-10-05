"""API / determinism acceptance check for rb_env_heaven (no render).

blender -b --factory-startup -P scenes/tests/heaven_api_check.py
Builds the gate and the meadow twice each in ONE scene, adds lights twice, and checks:
unique object names, same-seed geometry is identical, petals / motes / grass move with the frame and are
repeatable (pure function of the frame), CTRL_open turns the doors, CTRL_light drives the light energies.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import bpy  # noqa: E402
import numpy as np  # noqa: E402

import rb_core as C  # noqa: E402
import rb_env_heaven as HV  # noqa: E402

C.reset_scene()
sc = C.setup_render(scale=0.25, samples=1)
fails = []


def check(ok, msg):
    print(("OK   " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


def pts(ob, f):
    sc.frame_set(f)
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = ev.to_mesh()
    a = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("co", a)
    ev.to_mesh_clear()
    return a


M1 = HV.build_meadow(5)
M2 = HV.build_meadow(5)
L1 = HV.lights_meadow(M1)
L2 = HV.lights_meadow(M2, warrior=(0.0, 0.0), cam=M2.marks["cam"])
for k in ("warrior", "heading", "cam", "aim", "cam_far"):
    check(k in M1.marks, "meadow mark %s = %s" % (k, M1.marks.get(k)))
check(abs(M1.ground_z(0, 0) - M1.marks["warrior"][2]) < 1e-6, "ground_z(0,0) = %.3f matches warrior mark" % M1.ground_z(0, 0))
a60, b60, a61, a60b = pts(M1.petals, 60), pts(M2.petals, 60), pts(M1.petals, 61), pts(M1.petals, 60)
check(a60.size == b60.size and np.allclose(a60, b60), "petals: same seed -> identical (%d verts)" % (a60.size // 3))
check(np.abs(a61 - a60).max() > 1e-3, "petals move between frames (max %.3f m)" % np.abs(a61 - a60).max())
check(np.array_equal(a60, a60b), "petals repeatable when revisiting frame 60")
g60, g61 = pts(M1.grass, 60), pts(M1.grass, 61)
check(np.abs(g61 - g60).max() > 1e-5, "grass sways with the frame (max %.4f m, %d verts)" % (np.abs(g61 - g60).max(), g60.size // 3))

G1 = HV.build_gate(3)
G2 = HV.build_gate(3)
LG1 = HV.lights_gate(G1)
LG2 = HV.lights_gate(G2, warrior=(0.0, 2.0, 0.0), cam=(0.0, -2.0, 1.5))
for k in ("warrior", "heading", "cam", "aim"):
    check(k in G1.marks, "gate mark %s = %s" % (k, G1.marks.get(k)))
G1.key_ctrl("open", 1, 0.0)
G1.key_ctrl("open", 30, 1.0)
G1.key_ctrl("light", 1, 0.0)
G1.key_ctrl("light", 30, 1.0)
sc.frame_set(1)
y0, e0 = math.degrees(G1.doors[0].matrix_world.to_euler().z), LG1["beam"].data.energy
y2 = math.degrees(G2.doors[0].matrix_world.to_euler().z)
sc.frame_set(30)
y1, e1 = math.degrees(G1.doors[0].matrix_world.to_euler().z), LG1["beam"].data.energy
check(abs(y0) < 0.5 and abs(y1 - 80.0) < 0.5, "CTRL_open 0 -> 1 turns door_L %.1f -> %.1f deg" % (y0, y1))
check(abs(y2 - 36.0) < 0.5, "second gate keeps its own default opening (%.1f deg)" % y2)
check(e0 < 1.0 and e1 > 1e4, "CTRL_light 0 -> 1 drives beam energy %.0f -> %.0f W" % (e0, e1))
m60, m61 = pts(G1.motes, 60), pts(G1.motes, 61)
check(np.abs(m61 - m60).max() > 1e-4, "dust motes drift with the frame")
objs = M1.objects + M2.objects + G1.objects + G2.objects + list(L1.values()) + list(L2.values()) + \
    list(LG1.values()) + list(LG2.values())
names = [o.name for o in objs]
check(len(set(names)) == len(names), "%d handles, all object names unique" % len(names))
print("RESULT", "PASS" if not fails else "FAIL %d" % len(fails))
