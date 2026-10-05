"""Enemy module test renders (rb_enemies).
  xvfb-run -a -s "-screen 0 1920x1080x24" blender -b --factory-startup -P scenes/tests/enemies_test.py -- \
      --mode lineup|attack|crowd|build --scale 0.35 --samples 8 --out renders/tests/enemies
"""
import argparse
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

import rb_core as C  # noqa: E402
import rb_enemies as EN  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--mode", default="lineup")
ap.add_argument("--scale", type=float, default=0.35)
ap.add_argument("--samples", type=int, default=8)
ap.add_argument("--out", default=os.path.join(C.ROOT, "renders", "tests", "enemies"))
ap.add_argument("--kinds", default=",".join(EN.KINDS))
ap.add_argument("--repeat", type=int, default=1)
ap.add_argument("--hide", type=int, default=0)
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
os.makedirs(args.out, exist_ok=True)


def floor_mat():
    m = bpy.data.materials.new("T_floor")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N = nt.nodes.new
    L = nt.links.new
    tc = N("ShaderNodeTexCoord")
    vor = N("ShaderNodeTexVoronoi")
    vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = 2.4
    L(tc.outputs["Object"], vor.inputs["Vector"])
    gr = N("ShaderNodeMapRange")
    gr.inputs["From Min"].default_value = 0.0
    gr.inputs["From Max"].default_value = 0.035
    L(vor.outputs["Distance"], gr.inputs["Value"])
    nz = N("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 8.0
    L(tc.outputs["Object"], nz.inputs["Vector"])
    nz2 = N("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = 0.35
    nz2.inputs["Detail"].default_value = 3.0
    L(tc.outputs["Object"], nz2.inputs["Vector"])
    mix = N("ShaderNodeMix")
    mix.data_type = "RGBA"
    L(nz.outputs["Fac"], mix.inputs["Factor"])
    mix.inputs[6].default_value = (0.008, 0.009, 0.01, 1)
    mix.inputs[7].default_value = (0.028, 0.026, 0.024, 1)
    mul = N("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    L(mix.outputs[2], mul.inputs[6])
    L(gr.outputs["Result"], mul.inputs[7])
    wet = N("ShaderNodeMapRange")
    wet.inputs["From Min"].default_value = 0.45
    wet.inputs["From Max"].default_value = 0.6
    wet.inputs["To Min"].default_value = 0.3
    wet.inputs["To Max"].default_value = 0.85
    L(nz2.outputs["Fac"], wet.inputs["Value"])
    bump = N("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.5
    bump.inputs["Distance"].default_value = 0.02
    hm = N("ShaderNodeMath")
    hm.operation = "ADD"
    L(gr.outputs["Result"], hm.inputs[0])
    L(nz.outputs["Fac"], hm.inputs[1])
    L(hm.outputs[0], bump.inputs["Height"])
    bs = N("ShaderNodeBsdfPrincipled")
    L(mul.outputs[2], bs.inputs["Base Color"])
    L(wet.outputs["Result"], bs.inputs["Roughness"])
    L(bump.outputs["Normal"], bs.inputs["Normal"])
    out = N("ShaderNodeOutputMaterial")
    L(bs.outputs[0], out.inputs["Surface"])
    return m


def stage(scale, samples, haze=0.03):
    C.reset_scene()
    C.setup_render(scale=scale, samples=samples, motion_blur=False)
    C.world(color=(0.0025, 0.003, 0.004), volume_density=haze, volume_color=(0.55, 0.6, 0.7), anisotropy=0.45)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
    fl = bpy.context.active_object
    fl.data.materials.append(floor_mat())
    return fl


def cam(loc, target, lens, fstop=None, focus=None):
    c = C.camera("Cam", lens=lens, fstop=fstop, focus=focus)
    c.location = loc
    C.look_at(c, target)
    bpy.context.scene.camera = c
    return c


def render(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    t = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t
    print("RENDER %s %.1fs" % (path, dt))
    return dt


def pose_at(e, action, u, loc, heading, f=1):
    EN.key_enemy(e, f, EN._life(e, EN.pose_enemy(e, action, u), f), loc, heading)


kinds = args.kinds.split(",")
if args.mode == "build":
    C.reset_scene()
    for k in kinds:
        t = time.time()
        e = EN.build_enemy(k, seed=3)
        bpy.context.view_layer.update()
        zs = [(o.matrix_world @ Vector(b)).z for o in e.parts for b in o.bound_box]
        xs = [(o.matrix_world @ Vector(b)).x for o in e.parts for b in o.bound_box]
        nv = sum(len(o.data.vertices) for o in e.parts)
        nf = sum(len(o.data.polygons) for o in e.parts)
        print("BUILD %-14s %.1fs parts=%d verts=%d faces=%d top=%.2f span=%.2f mats=%d glow=%d" % (
            k, time.time() - t, len(e.parts), nv, nf, max(zs), max(xs) - min(xs), len(e.mats), len(e.glow_mats)))
        for a in EN.ACTIONS:
            for u in (0.0, 0.3, 0.6, 1.0):
                EN.key_enemy(e, 1, EN.pose_enemy(e, a, u), (0, 0, 0), 0)
        EN.perform_enemy(e, range(1, 20), "attack", 10, 12, (0, 0, 0), 0)
        EN.set_glow(e, 5, 2.0)
    print("BUILD OK")

elif args.mode == "dissolve":
    stage(args.scale, args.samples)
    sk = EN.build_enemy("skeleton", seed=1)
    ev = EN.build_enemy("evil", seed=2)
    an = EN.build_enemy("bad_angel", seed=3)
    for e, x, a in ((sk, -1.6, "hit"), (ev, 0.2, "idle"), (an, 2.2, "idle")):
        EN.perform_enemy(e, range(1, 25), a, 10, 10, (x, 0, 0), 0)
    EN.dissolve(sk, 11, frames=6, mode="shatter")
    EN.dissolve(ev, 11, frames=8, mode="smoke")
    EN.dissolve(an, 11, frames=8, mode="ash")
    cr = EN.crowd(["skeleton", "ghost"], 4, (0, 8, 0), 2.0, seed=3, face=(0, 0, 0), min_r=1.0)
    EN.dissolve(cr[0], 12, frames=6, mode="ash")
    EN.dissolve(cr[1], 12, frames=6, mode="shatter")
    C.light("SPOT", "rim", (0.6, 9.0, 7.5), color="#A9C2E6", energy=9000, size=0.6, target=(0, 0, 1.2), shadow=True,
            spot_size=math.radians(60), blend=0.6, volume=0.5)
    C.light("SPOT", "key", (-4.0, -6.0, 6.0), color="#8FA3B8", energy=3000, size=0.4, target=(0, 0, 1.0), shadow=True,
            spot_size=math.radians(45), blend=0.7, volume=0.3)
    cam((0.3, -8.5, 1.6), (0.3, 0.0, 1.2), 28)
    for f in (9, 13, 15):
        bpy.context.scene.frame_set(f)
        render(os.path.join(args.out, "dissolve_%02d.png" % f))

elif args.mode == "lineup":
    stage(args.scale, args.samples)
    lay = {"skeleton": ((-1.55, 0.0, 0), 12, "idle", 0.3), "ghost": ((0.0, -0.7, 0), 0, "idle", 0.6),
           "morbidious": ((1.55, 0.3, 0), -12, "idle", 0.1), "bad_angel": ((-3.0, 3.6, 0), 14, "raise", 0.45),
           "skeleton_king": ((0.0, 4.6, 0), 0, "idle", 0.2), "evil": ((3.2, 3.3, 0), -16, "idle", 0.8)}
    for i, k in enumerate(kinds):
        e = EN.build_enemy(k, seed=i + 1)
        loc, hd, act, u = lay[k]
        pose_at(e, act, u, loc, hd)
    bpy.context.scene.frame_set(1)
    C.light("SPOT", "rim", (0.6, 13.0, 11.0), color="#A9C2E6", energy=16000, size=0.6, target=(0, 1.5, 1.2), shadow=True,
            spot_size=math.radians(60), blend=0.6, volume=0.5)
    C.light("SPOT", "key", (-5.0, -5.0, 7.0), color="#8FA3B8", energy=5000, size=0.4, target=(0, 2.2, 1.0), shadow=True,
            spot_size=math.radians(45), blend=0.7, volume=0.5)
    C.light("POINT", "ember", (2.5, -3.5, 0.4), color="#FF6A1A", energy=40, size=0.4, shadow=False, volume=0.2)
    cam((0.0, -9.8, 2.7), (0.0, 2.4, 1.75), 28)
    render(os.path.join(args.out, "lineup.png"))

elif args.mode == "attack":
    acts = {"skeleton": ("attack", 0.42), "ghost": ("lunge", 0.55), "bad_angel": ("attack", 0.4), "evil": ("attack", 0.42),
            "morbidious": ("attack", 0.42), "skeleton_king": ("raise", 0.72)}
    tiles = []
    for i, k in enumerate(kinds):
        stage(args.scale, args.samples, haze=0.025)
        e = EN.build_enemy(k, seed=i + 1)
        a, u = acts[k]
        pose_at(e, a, u, (0, 0, 0), 0)
        bpy.context.scene.frame_set(1)
        H = e.height
        tgt = Vector((0.0, -0.25 * H, 0.52 * H))
        dist = H * (2.1 if k != "bad_angel" else 2.4)
        d = Vector((0.55, -1.0, 0.1)).normalized()
        cam(tgt + d * dist, tgt, 50, fstop=4.0, focus=dist)
        C.light("SPOT", "rim", (-1.5, 4.5, H * 1.6), color="#A9C2E6", energy=2500 * H / 2, size=0.4, target=(0, 0, H * 0.6),
                shadow=True, spot_size=math.radians(60), blend=0.6)
        C.light("SPOT", "key", (3.5, -2.5, H * 1.4), color="#94A6BA", energy=500 * H / 2, size=0.3, target=tuple(tgt),
                shadow=True, spot_size=math.radians(40), blend=0.7, volume=0.3)
        C.light("POINT", "ember", (-1.5, -2.2, 0.5), color="#FF6A1A", energy=15, size=0.3, shadow=False, volume=0.1)
        p = os.path.join(args.out, "attack_%s.png" % k)
        render(p)
        tiles.append(p)
    imgs = []
    for p in tiles:
        im = bpy.data.images.load(p)
        w, h = im.size
        a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
        imgs.append(a)
    h, w = imgs[0].shape[:2]
    sheet = np.ones((h * 2, w * 3, 4), np.float32)
    for i, a in enumerate(imgs):
        r, c = divmod(i, 3)
        sheet[(1 - r) * h:(2 - r) * h, c * w:(c + 1) * w] = a
    out = bpy.data.images.new("sheet", w * 3, h * 2, alpha=False)
    out.pixels = sheet.ravel()
    out.filepath_raw = os.path.join(args.out, "attack_sheet.png")
    out.file_format = "PNG"
    out.save()
    print("SHEET", out.filepath_raw)

elif args.mode == "crowd":
    stage(args.scale, args.samples, haze=0.03)
    t = time.time()
    members = EN.crowd(["skeleton", "skeleton", "ghost"], 20, (0, 0, 0), 4.6, seed=7, face=(0, 0, 0), min_r=2.0)
    EN.crowd_advance(members, 1, 30, 1.1)
    if args.hide == 1:
        for m in members:
            for o in m.parts:
                o.hide_render = True
    print("CROWD build %.1fs members=%d" % (time.time() - t, len(members)))
    bpy.context.scene.frame_set(24)
    C.light("SPOT", "top", (0.3, 1.2, 9.0), color="#A9C2E6", energy=6000, size=0.5, target=(0, 0, 0), shadow=True,
            spot_size=math.radians(75), blend=0.7, volume=0.8)
    C.light("SPOT", "rim", (-1.5, 9.5, 4.0), color="#8FAAD0", energy=5000, size=0.5, target=(0, 0, 0.8), shadow=True,
            spot_size=math.radians(60), blend=0.6, volume=1.0)
    C.light("POINT", "ember", (0, 0, 1.2), color="#FF6A1A", energy=60, size=0.3, shadow=False, volume=0.3)
    cam((0.4, -4.3, 7.0), (0.0, 0.35, 0.0), 24, fstop=8.0, focus=7.8)
    bpy.context.scene.frame_set(24)
    dt = render(os.path.join(args.out, "crowd_s%d.png" % int(args.scale * 100)))
    if args.repeat > 1:
        bpy.context.scene.frame_set(25)
        dt = render(os.path.join(args.out, "crowd_s%d_b.png" % int(args.scale * 100)))
    print("CROWD_RENDER_SECONDS %.1f" % dt)
    if args.hide == 2:
        print("CROWD tris/member ~%d" % sum(len(o.data.polygons) for o in members[0].parts))
        for m in members:
            for o in m.parts:
                o.hide_render = True
        bpy.context.scene.frame_set(26)
        db = render(os.path.join(args.out, "crowd_hidden.png"))
        print("CROWD_DELTA_SECONDS %.1f (with %.1f / without %.1f)" % (dt - db, dt, db))
