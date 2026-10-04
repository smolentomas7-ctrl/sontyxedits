"""Silhouettes of every montage action at 5 phases (calibration)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import bpy
import rb_core as C, rb_motion as MO, rb_warrior as RW, rb_actions as A
out = os.path.join(C.ROOT, "build/tests/motion"); os.makedirs(out, exist_ok=True)
C.reset_scene()
C.setup_render(scale=0.18, samples=1, motion_blur=False, volumetrics=False, bloom=0.0, gtao=False, ssr=False, soft_shadows=False, look="AgX - Base Contrast")
C.world(color=(0.85, 0.85, 0.85)); bpy.ops.mesh.primitive_plane_add(size=40)
w = RW.build_warrior("late", cape=False)
C.light("SUN", "sun", (0, 0, 10), energy=1.5, rot=(0.5, 0.2, 0), shadow=False)
cam = C.camera("cam", lens=35); cam.location = (5.5, -2.2, 1.1); C.look_at(cam, (0, -0.3, 1.0))
names = ["cleave", "slash", "block", "thrust", "cast", "god_attack", "hit_react", "fall", "kneel"]
f = 1
sc = bpy.context.scene
for n in names:
    for k, u in enumerate([0.0, 0.3, A.PEAK[n] * 0.85, A.PEAK[n], 1.0]):
        pk = 1000
        dur = 30
        fr = pk + (u - A.PEAK[n]) * dur
        p, loc, rot = A.perform(w, fr, n, pk, dur, (0, 0, 0), 0)
        MO.key_pose(w, f, p, loc, rot)
        sc.frame_set(f)
        sc.render.filepath = os.path.join(out, "act_%s_%d.png" % (n, k))
        bpy.ops.render.render(write_still=True)
        f += 1
print("DONE")
