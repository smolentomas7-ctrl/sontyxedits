"""Silhouette strip of the Act V / VI choreography (wide side view)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import bpy
import rb_core as C, rb_motion as MO, rb_story as ST, rb_warrior as RW, rb_god as RG
out = os.path.join(C.ROOT, "build/tests/motion"); os.makedirs(out, exist_ok=True)
C.reset_scene()
C.setup_render(scale=0.22, samples=1, motion_blur=False, volumetrics=False, bloom=0.0, gtao=False, ssr=False, soft_shadows=False, look="AgX - Base Contrast")
C.world(color=(0.85, 0.85, 0.85))
bpy.ops.mesh.primitive_plane_add(size=80)
w = RW.build_warrior("late", cape=False); g = RG.build_god()
C.light("SUN", "sun", (0, 0, 10), energy=1.5, rot=(0.5, 0.2, 0), shadow=False)
cam = C.camera("cam", lens=30)
FR = [1343, 1352, 1365, 1380, 1395, 1414, 1428, 1437, 1465, 1480, 1500, 1515, 1600, 1745, 1790, 1925, 1932, 1990]
for f in FR:
    act = "after" if f >= 1953 else "battle"
    wp = (ST.warrior_after if act == "after" else ST.warrior_battle)(w, f)
    MO.key_pose(w, f, *wp)
    gp, gl, gr, piv, prot = (ST.god_after if act == "after" else ST.god_battle)(g, f)
    MO.key_pose(g, f, gp, gl, gr); MO.key_god_blade(g, f, piv, prot)
sc = bpy.context.scene
cam.location = (15.0, 9.0, 3.2); C.look_at(cam, (0, 9.6, 2.6))
for f in FR:
    sc.frame_set(f)
    sc.render.filepath = os.path.join(out, "battle_%04d.png" % f)
    bpy.ops.render.render(write_still=True)
print("DONE")
