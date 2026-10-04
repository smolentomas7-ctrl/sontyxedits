"""Test frames for the VFX library (rb_vfx) on a dark wet stone floor with light haze, vertical 35 mm.

blender -b --factory-startup -P scenes/tests/vfx_test.py -- [--do sheet,strips,det,timing] [--only a,b]
        [--scale 0.3] [--samples 6]
  sheet   one panel per effect at its peak -> build/tests/rb_vfx/sheet.png (6 columns, order = PANELS)
  strips  4-frame strips of shockwave, fireball, lightning, god_attack -> strip_<name>.png
  det     renders the god_attack panel twice (rebuilt from scratch) and compares pixels
  timing  one full-res 8 spp render of the god_attack + embers frame, prints seconds
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import bpy  # noqa: E402
import numpy as np  # noqa: E402

import rb_core as C  # noqa: E402
import rb_mat as M  # noqa: E402
import rb_vfx as V  # noqa: E402

args = C.script_args()
DO = str(args.get("do", "sheet,strips,det")).split(",")
ONLY = str(args.get("only", "")).split(",") if args.get("only") else None
SCALE = float(args.get("scale", 0.3))
SAMPLES = int(args.get("samples", 6))
OUT = os.path.join(C.ROOT, "build", "tests", "rb_vfx")
os.makedirs(OUT, exist_ok=True)
B = 20


def stone_floor():
    m, b = M.new("test_floor")
    geo = b.n("ShaderNodeNewGeometry")
    n1 = b.n("ShaderNodeTexNoise", Vector=(geo, "Position"), Scale=0.35, Detail=6.0, Roughness=0.6)
    n2 = b.n("ShaderNodeTexNoise", Vector=(geo, "Position"), Scale=6.0, Detail=8.0, Roughness=0.65)
    vor = b.n("ShaderNodeTexVoronoi", Vector=(geo, "Position"), Scale=0.9, _feature="DISTANCE_TO_EDGE")
    crack = b.n("ShaderNodeMapRange", Value=(vor, "Distance"), **{"From Min": 0.0, "From Max": 0.03})
    base = b.ramp((n2, "Fac"), [(0.3, (0.012, 0.012, 0.013)), (0.7, (0.045, 0.043, 0.041))])
    col = b.mix((crack, "Result"), (0.004, 0.004, 0.004), (base, "Color"))
    rough = b.ramp((n1, "Fac"), [(0.4, (0.35, 0.35, 0.35)), (0.65, (0.8, 0.8, 0.8))])
    bump = b.n("ShaderNodeBump", Strength=0.12, Height=(n2, "Fac"))
    bs = b.bsdf(**{"Base Color": col, "Roughness": (rough, "Color"), "Normal": (bump, "Normal")})
    b.out(bs)
    return m


def box(name, loc, dims, rotz, mat):
    me = bpy.data.meshes.new(name)
    x, y, z = [d / 2 for d in dims]
    vs = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    fs = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me.from_pydata(vs, [], fs)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (0, 0, rotz)
    me.materials.append(mat)
    return ob


def setup(scale=SCALE, samples=SAMPLES):
    C.reset_scene()
    M._cache.clear()
    sc = C.setup_render(scale=scale, samples=samples, motion_blur=True, vol_end=60.0, vol_samples=32)
    sc.frame_start, sc.frame_end = 1, 80
    C.world(color=(0.003, 0.0045, 0.006), strength=1.0, volume_density=0.022, volume_color=(0.55, 0.6, 0.66),
            anisotropy=0.45)
    fm = stone_floor()
    me = bpy.data.meshes.new("floor")
    me.from_pydata([(-40, -40, 0), (40, -40, 0), (40, 40, 0), (-40, 40, 0)], [], [(0, 1, 2, 3)])
    fl = bpy.data.objects.new("floor", me)
    sc.collection.objects.link(fl)
    me.materials.append(fm)
    pm = M.matte("test_pillar", (0.03, 0.029, 0.028), rough=0.7)
    box("pillar_L", (-2.3, 4.5, 2.5), (0.9, 0.9, 5.0), 0.3, pm)
    box("pillar_R", (2.4, 7.0, 1.2), (1.0, 1.0, 2.4), -0.4, pm)
    cam = C.camera("Cam", lens=35, fstop=4.0, focus=6.6)
    cam.location = (0.0, -6.4, 1.45)
    C.look_at(cam, (0.0, 0.8, 1.75))
    C.light("SPOT", "key", (-3.5, -1.0, 6.5), color="#AFC2D6", energy=2600, size=0.4, target=(0, 1, 1.0),
            spot_size=math.radians(60), shadow=True)
    C.light("SPOT", "rim", (2.5, 7.0, 2.6), color="#FF6A1A", energy=260, size=0.5, target=(0, 0.5, 1.0),
            spot_size=math.radians(45), shadow=False)
    C.light("AREA", "fill", (0.0, -5.0, 2.5), color="#3A5A6A", energy=40, size=3.0, target=(0, 0, 1), shadow=False)
    return sc, cam


def trail_rig():
    piv = C.empty("swing_pivot", (0.0, 0.6, 1.25))
    me = bpy.data.meshes.new("blade")
    w, t = 0.03, 0.006
    vs = [(-w, -t, 0.2), (w, -t, 0.2), (w, t, 0.2), (-w, t, 0.2), (-w, -t, 1.45), (w, -t, 1.45), (w, t, 1.45),
          (-w, t, 1.45)]
    me.from_pydata(vs, [], [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    bl = bpy.data.objects.new("blade", me)
    bpy.context.scene.collection.objects.link(bl)
    me.materials.append(M.matte("test_steel", (0.05, 0.05, 0.055), rough=0.35, metal=1.0))
    bl.parent = piv
    for f in range(8, 34):
        u = C.ease_in_out((f - 12) / 12.0)
        piv.rotation_euler = (0.0, math.radians(-115 + 230 * u), 0.0)
        piv.keyframe_insert("rotation_euler", frame=f)
    C.set_interp(piv)
    return [piv, bl], bl


FB = dict(start=(-0.45, -0.8, 1.3), end=(0.55, 4.0, 2.3))
LT = dict(start=(-0.3, -0.6, 1.5), end=[(-1.0, 3.5, 0.0), (0.3, 4.6, 1.1), (1.2, 3.0, 0.0)])
GD = dict(origin=(-0.2, -0.4, 1.6), target=(0.6, 3.5, 5.0))


def build(key, cam):
    """-> (handles, frame, extra objects to delete)"""
    if key == "embers":
        return V.embers(1, 80, (0, 1.0, 1.7), radius=2.6, height=4.0, seed=3, cam=cam), 40, []
    if key == "embers_fall":
        return V.embers(1, 80, (0, 1.0, 2.0), radius=2.6, height=4.0, seed=4, falling=True), 40, []
    if key == "ash":
        return V.ash(1, 80, (0, 0.5, 1.6), radius=2.5, height=3.5, seed=5), 40, []
    if key == "dust":
        return V.dust_puff(B, (0, 0.2, 0), seed=6, scale=1.6), B + 4, []
    if key == "sparks":
        return V.sparks(B, (0, 0.3, 1.3), seed=7, scale=1.4), B + 2, []
    if key == "sparks_slow":
        return V.sparks(B, (0, 0.3, 1.3), seed=8, direction=(0.6, -0.3, 0.5), time_scale=0.5), B + 5, []
    if key == "shockwave":
        return V.shockwave(B, (0, 0.6, 0), seed=9), B + 3, []
    if key == "debris_rock":
        return V.debris(B, (0, 0.6, 0), seed=10), B + 7, []
    if key == "debris_bone":
        return V.debris(B, (0, 0.6, 1.1), seed=11, kind="bone"), B + 6, []
    if key == "smoke":
        return V.smoke_burst(B, (0, 0.6, 1.2), seed=12), B + 4, []
    if key == "fireball_fly":
        return V.fireball(B, FB["start"], FB["end"], seed=13), B + 3, []
    if key == "fireball_boom":
        return V.fireball(B, FB["start"], FB["end"], seed=13), B + 8, []
    if key == "lightning":
        return V.lightning(B, LT["start"], LT["end"], seed=14), B + 1, []
    if key == "god":
        return V.god_attack(B, GD["origin"], GD["target"], seed=15), B + 2, []
    if key == "god_column":
        return V.god_attack(B, (0.0, 1.2, 0.0), None, seed=16, column=True), B + 4, []
    if key == "trail":
        extra, bl = trail_rig()
        return V.ember_trail(bl, 10, 30, seed=17), 19, extra
    if key == "petals":
        return V.petals(1, 80, (0, 1.0, 2.0), radius=3.0, height=4.0, seed=18), 40, []
    raise KeyError(key)


PANELS = ["embers", "embers_fall", "ash", "dust", "sparks", "sparks_slow", "shockwave", "debris_rock",
          "debris_bone", "smoke", "fireball_fly", "fireball_boom", "lightning", "god", "god_column", "trail",
          "petals"]
STRIPS = {"shockwave": [B, B + 3, B + 7, B + 11], "fireball_fly": [B - 2, B + 3, B + 7, B + 12],
          "lightning": [B - 1, B + 1, B + 4, B + 7], "god": [B - 4, B + 1, B + 4, B + 10]}


def render(sc, frame, path):
    sc.frame_set(frame)
    sc.render.filepath = path
    t = time.time()
    bpy.ops.render.render(write_still=True)
    return time.time() - t


def clear(h, extra):
    V.remove(h)
    for o in extra:
        bpy.data.objects.remove(o, do_unlink=True)


def load(path):
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(h, w, 4)[::-1]


def tile(paths, cols, dst):
    ims = [load(p) for p in paths]
    h, w = ims[0].shape[:2]
    rows = int(math.ceil(len(ims) / cols))
    canvas = np.zeros((rows * h + (rows - 1) * 4, cols * w + (cols - 1) * 4, 4), np.float32)
    canvas[..., 3] = 1.0
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        canvas[r * (h + 4):r * (h + 4) + h, c * (w + 4):c * (w + 4) + w] = im
    out = bpy.data.images.new("tile", canvas.shape[1], canvas.shape[0], alpha=False)
    out.pixels.foreach_set(canvas[::-1].ravel())
    out.filepath_raw = dst
    out.file_format = "PNG"
    out.save()
    print("WROTE", dst)


sc, cam = setup()
if "sheet" in DO:
    paths = []
    for key in PANELS:
        if ONLY and key not in ONLY:
            continue
        t0 = time.time()
        h, fr, extra = build(key, cam)
        tb = time.time() - t0
        p = os.path.join(OUT, "p_%s.png" % key)
        tr = render(sc, fr, p)
        print("PANEL %-14s frame %3d  build %.2fs  render %.2fs  objs %d" % (key, fr, tb, tr, len(h["objects"])))
        clear(h, extra)
        paths.append(p)
    if len(paths) > 1:
        tile(paths, 6, os.path.join(OUT, "sheet.png"))
if "strips" in DO:
    for key, frames in STRIPS.items():
        if ONLY and key not in ONLY:
            continue
        h, _, extra = build(key, cam)
        ps = []
        for fr in frames:
            p = os.path.join(OUT, "s_%s_%03d.png" % (key, fr))
            tr = render(sc, fr, p)
            ps.append(p)
        print("STRIP %s %s  last render %.2fs" % (key, frames, tr))
        clear(h, extra)
        tile(ps, 4, os.path.join(OUT, "strip_%s.png" % key))
if "det" in DO:
    imgs = []
    for k in range(2):
        h, fr, extra = build("god", cam)
        p = os.path.join(OUT, "det_%d.png" % k)
        render(sc, fr + 1, p)
        clear(h, extra)
        imgs.append(load(p))
    print("DETERMINISM max abs diff = %.6f" % float(np.abs(imgs[0] - imgs[1]).max()))
if "timing" in DO:
    sc, cam = setup(scale=1.0, samples=8)
    t0 = time.time()
    h1, fr, _ = build("god", cam)
    V.embers(1, 80, (0, 1.0, 1.7), radius=2.6, height=4.0, seed=3, cam=cam)
    print("TIMING build %.2fs" % (time.time() - t0))
    tr = render(sc, fr, os.path.join(OUT, "timing_full.png"))
    tr2 = render(sc, fr + 1, os.path.join(OUT, "timing_full2.png"))
    print("TIMING full-res 8spp: %.2fs, %.2fs per frame" % (tr, tr2))
