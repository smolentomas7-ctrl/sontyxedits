"""THE FALLEN GOD — locked design, see assets/characters.md.

5.7 m statue-god: cracked pale stone with black void and cold blue light in
the cracks (CTRL_ignite height, CTRL_glow), stern sculpted face with deep
sockets and blue-white eyes (CTRL_eye_glow), broken three-arc halo
(CTRL_halo), tattered dark robes and a faceted obsidian blade.

build_god() returns a God with .rig (FK empties), .root, .blade, .halo,
.mats. Rest pose: blade planted point-down in front, both hands on the pommel.
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import rb_mat as M
import rb_mesh as G
from rb_core import empty, link, parent_keep

S = 3.0  # scale vs. a 1.9 m human

J = {
    "root": (0, 0, 0),
    "pelvis": (0, 0.0, 2.85),
    "spine": (0, 0.0, 3.25),
    "chest": (0, 0.03, 3.85),
    "neck": (0, 0.05, 4.62),
    "head": (0, 0.03, 4.88),
    "clav_L": (0.12, 0.04, 4.42), "upperarm_L": (0.66, 0.05, 4.38), "forearm_L": (0.86, -0.12, 3.62),
    "hand_L": (0.5, -0.62, 3.25),
    "thigh_L": (0.3, 0.0, 2.78), "shin_L": (0.34, -0.04, 1.52), "foot_L": (0.36, 0.06, 0.24),
}
for k in list(J):
    if k.endswith("_L"):
        x, y, z = J[k]
        J[k[:-2] + "_R"] = (-x, y, z)
PARENT = {"pelvis": "root", "spine": "pelvis", "chest": "spine", "neck": "chest", "head": "neck",
          "clav_L": "chest", "upperarm_L": "clav_L", "forearm_L": "upperarm_L", "hand_L": "forearm_L",
          "clav_R": "chest", "upperarm_R": "clav_R", "forearm_R": "upperarm_R", "hand_R": "forearm_R",
          "thigh_L": "pelvis", "shin_L": "thigh_L", "foot_L": "shin_L",
          "thigh_R": "pelvis", "shin_R": "thigh_R", "foot_R": "shin_R", "blade": "root"}
ORDER = ["root", "pelvis", "spine", "chest", "neck", "head", "clav_L", "upperarm_L", "forearm_L", "hand_L",
         "clav_R", "upperarm_R", "forearm_R", "hand_R", "thigh_L", "shin_L", "foot_L", "thigh_R", "shin_R", "foot_R"]


class God:
    pass


def V(*a):
    return np.array(a, float)


def skin_mesh(name, nodes, edges, smooth_levels=2, disp=0.0, seed=0):
    """Skin-modifier body part. nodes: [(x,y,z,rx,ry)], edges: [(i,j)]."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([n[:3] for n in nodes], edges, [])
    ob = bpy.data.objects.new(name, me)
    link(ob)
    sk = ob.modifiers.new("skin", "SKIN")
    sk.use_smooth_shade = True
    sk.branch_smoothing = 0.6
    for i, n in enumerate(nodes):
        me.skin_vertices[0].data[i].radius = (n[3], n[4])
    me.skin_vertices[0].data[0].use_root = True
    ob.modifiers.new("sub", "SUBSURF").levels = smooth_levels
    ob.modifiers["sub"].render_levels = smooth_levels
    G.apply_all(ob)
    if disp:
        tex = bpy.data.textures.new(name + "_n", "CLOUDS")
        tex.noise_scale = 0.35
        tex.noise_depth = 3
        d = ob.modifiers.new("disp", "DISPLACE")
        d.texture = tex
        d.strength = disp
        d.mid_level = 0.5
        d.texture_coords = "GLOBAL"
        G.apply_all(ob)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def bulge(ob, center, radius, amount, axis=None):
    """Sculpt helper: push vertices along their normal (or `axis`) with a gaussian falloff."""
    c = Vector(center)
    for v in ob.data.vertices:
        d = (v.co - c).length / radius
        if d < 2.2:
            k = amount * math.exp(-d * d * 1.6)
            v.co += (Vector(axis) if axis else v.normal) * k
    ob.data.update()


def build_rig(prefix):
    rig = {}
    for n in ORDER:
        e = empty(prefix + n, J[n], size=0.15)
        p = rig.get(PARENT.get(n))
        if p is not None:
            e.parent = p
            e.matrix_parent_inverse = p.matrix_world.inverted()
            bpy.context.view_layer.update()
        e.rotation_mode = "XYZ"
        rig[n] = e
    return rig


def attach(ob, rig, j):
    bpy.context.view_layer.update()
    parent_keep(ob, rig[j])
    return ob


# ------------------------------------------------------------------ head
def build_head(name, center, H=0.72, seed=3):
    """Stern statue face. center = head centre (between the ears)."""
    cx, cy, cz = center
    hw, hd, hh = 0.235, 0.31, H / 2
    R, C = 90, 120
    P = np.zeros((R, C, 3))
    for i in range(R):
        lat = math.pi * (i / (R - 1)) - math.pi / 2       # -pi/2 (chin) .. pi/2 (crown)
        for j in range(C):
            lon = 2 * math.pi * j / C                       # 0 = front (-Y)
            u = math.cos(lat) * math.sin(lon)               # -1..1 across
            v = -math.cos(lat) * math.cos(lon)              # -1 front .. 1 back
            w = math.sin(lat)                               # -1 chin .. 1 crown
            x, y, z = u * hw, v * hd, w * hh
            front = max(0.0, -v)
            # skull: flatter sides, fuller back of the head
            if v > 0:
                y *= 1.0 + 0.08 * v
            # jaw narrows toward the chin
            jaw = 1 - 0.26 * max(0.0, min(1.0, (-w - 0.25) / 0.75)) ** 1.6
            x *= jaw
            if w < -0.2:
                y = y * (1 - 0.25 * max(0.0, min(1.0, (-w - 0.2) / 0.8))) if v > 0 else y
            g = lambda a, s: math.exp(-(a / s) ** 2)
            fwd = 0.0
            # crown: rounder skull (less egg-shaped)
            if w > 0.3:
                k = (w - 0.3) / 0.7
                x *= 1.0 + 0.1 * math.sin(k * math.pi)
                y *= 1.0 + 0.08 * math.sin(k * math.pi)
                z *= 1.0 - 0.1 * k * k
            # brow ridge (heavy)
            fwd += 0.05 * g(w - 0.24, 0.07) * g(u, 0.75) * front
            # eye sockets (deep)
            for sx in (-1, 1):
                fwd -= 0.07 * g(w - 0.11, 0.1) * g(u - sx * 0.37, 0.17) * front
            # nose: continuous from the brow, straight classical bridge, flat base
            if -0.36 < w < 0.32:
                k = (0.3 - w) / 0.6                      # 0 at the brow .. 1 at the tip
                k = max(0.0, min(1.0, k))
                ramp_top = min(1.0, max(0.0, (0.32 - w) / 0.08))
                ramp_bot = min(1.0, max(0.0, (w + 0.36) / 0.05))
                width = 0.075 + 0.07 * k ** 1.5
                fwd += (0.045 + 0.1 * k ** 1.2) * g(u, width) * front * ramp_top * ramp_bot
                for sx in (-1, 1):                         # nostril wings
                    fwd += 0.022 * g(w + 0.3, 0.045) * g(u - sx * 0.13, 0.07) * front
            # philtrum and lips
            fwd -= 0.01 * g(w + 0.39, 0.025) * g(u, 0.2) * front
            fwd += 0.018 * g(w + 0.45, 0.028) * g(u, 0.3) * front
            fwd -= 0.02 * g(w + 0.49, 0.01) * g(u, 0.34) * front
            fwd += 0.014 * g(w + 0.54, 0.028) * g(u, 0.26) * front
            fwd -= 0.012 * g(w + 0.63, 0.03) * g(u, 0.3) * front
            # chin
            fwd += 0.05 * g(w + 0.8, 0.11) * g(u, 0.36) * front
            # temples sink, brow overhangs the sockets
            for sx in (-1, 1):
                fwd -= 0.02 * g(w - 0.2, 0.15) * g(u - sx * 0.85, 0.15) * front
            # cheekbones (sideways + forward)
            side = 0.0
            for sx in (-1, 1):
                side += 0.03 * g(w + 0.04, 0.1) * g(u - sx * 0.7, 0.2) * front

            # hollow cheeks under the cheekbones
            for sx in (-1, 1):
                side -= 0.016 * g(w + 0.3, 0.12) * g(u - sx * 0.62, 0.2) * front
            n = Vector((x / hw ** 2, y / hd ** 2, z / hh ** 2)).normalized()
            p = Vector((x, y, z)) + n * side
            p.y -= fwd
            P[i, j] = (cx + p.x, cy + p.y, cz + p.z)
    head = G.grid_mesh(name, P, closed_u=True, cap_start=False, cap_end=False)
    me = head.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    sub = head.modifiers.new("sub", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 1
    G.apply_all(head)
    return head


# ------------------------------------------------------------------ blade
def build_blade(prefix, length=4.3, seed=5):
    """Faceted obsidian greatblade. Own space: grip along +Z from -1.0 to 0, blade from 0 to `length`."""
    rnd = random.Random(seed)
    rows = 40
    prof = []
    for i in range(rows):
        t = i / (rows - 1)
        z = 0.05 + t * length
        w = 0.2 * (1 - 0.25 * t) if t < 0.86 else 0.2 * 0.785 * max(0.0, (1 - (t - 0.86) / 0.14)) ** 0.8
        w = max(w, 0.004)
        jl = rnd.uniform(-0.03, 0.02) * (1 if t < 0.95 else 0.2)
        jr = rnd.uniform(-0.03, 0.02) * (1 if t < 0.95 else 0.2)
        th = 0.05 * (1 - 0.5 * t)
        ring = [(-(w + jl), 0, z), (-0.45 * w, th, z), (0.0, th * 1.1, z), (0.45 * w, th, z), ((w + jr), 0, z),
                (0.45 * w, -th, z), (0.0, -th * 1.1, z), (-0.45 * w, -th, z)]
        prof.append(ring)
    bl = G.grid_mesh(prefix + "god_blade", np.array(prof), closed_u=True, cap_start=True, cap_end=True, smooth=False)
    parts = [bl]
    # jagged obsidian guard: shards
    for k, (dx, dz, sz) in enumerate([(-0.36, 0.0, 0.12), (-0.2, -0.04, 0.1), (0.2, -0.04, 0.1), (0.36, 0.0, 0.12),
                                      (-0.5, 0.08, 0.09), (0.5, 0.08, 0.09)]):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=sz)
        for v in bm.verts:
            v.co.x *= 1.6
            v.co.z *= 0.55
            v.co += Vector((rnd.uniform(-0.02, 0.02), rnd.uniform(-0.02, 0.02), rnd.uniform(-0.02, 0.02)))
            v.co += Vector((dx, 0, dz))
        me = bpy.data.meshes.new("shard%d" % k)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(prefix + "shard%d" % k, me)
        link(o)
        parts.append(o)
    grip = G.tube(prefix + "god_grip", (0, 0, 0.0), (0, 0, -1.0), lambda t, th: 0.055 + 0.006 * math.sin(t * 40), N=16, M=40)
    G.set_mat(grip, M.leather("god_grip", (0.012, 0.012, 0.016), rough=0.7))
    parts.append(grip)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.12)
    for v in bm.verts:
        v.co.z = v.co.z * 1.6 - 1.12
    me = bpy.data.meshes.new("pommel")
    bm.to_mesh(me)
    bm.free()
    po = bpy.data.objects.new(prefix + "god_pommel", me)
    link(po)
    parts.append(po)
    obs = M.obsidian()
    for o in parts:
        if o is not grip:
            G.set_mat(o, obs)
    blade = G.join(parts, prefix + "god_weapon")
    G.bake_attributes(blade, mud_top=0, wear_gain=4.0)
    for p in blade.data.polygons:
        if p.material_index == 0:
            p.use_smooth = False
    return blade


# ------------------------------------------------------------------ halo
def build_halo(prefix, center, radius=0.95, seed=9):
    rnd = random.Random(seed)
    mat = M.emission("god_halo", (0.62, 0.8, 1.0), 9.0, ctrl="halo")
    arcs = [(0.18, 1.85), (2.1, 3.95), (4.25, 5.95)]
    objs = []
    for k, (a0, a1) in enumerate(arcs):
        n = 64
        pts = []
        for i in range(n):
            a = a0 + (a1 - a0) * i / (n - 1)
            r = radius + 0.012 * math.sin(a * 13 + k)
            pts.append((center[0] + r * math.cos(a), center[1], center[2] + r * math.sin(a)))
        t = G.curve_tube(prefix + "halo_arc%d" % k, pts, radius=0.032)
        # jagged broken ends: taper the last few rings
        objs.append(t)
    # floating fragments in the gaps
    for k in range(6):
        a = [1.98, 2.02, 4.1, 4.08, 6.08, 6.15][k]
        r = radius + rnd.uniform(-0.05, 0.06)
        c = (center[0] + r * math.cos(a), center[1] + rnd.uniform(-0.04, 0.04), center[2] + r * math.sin(a))
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rnd.uniform(0.018, 0.035))
        for v in bm.verts:
            v.co.x *= 1.8
            v.co += Vector(c)
        me = bpy.data.meshes.new("frag%d" % k)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(prefix + "halo_frag%d" % k, me)
        link(o)
        objs.append(o)
    halo = G.join(objs, prefix + "halo")
    G.set_mat(halo, mat)
    return halo


# ------------------------------------------------------------------ god
def build_god(prefix="G_", seed=21):
    g = God()
    g.prefix = prefix
    rnd = random.Random(seed)
    rig = build_rig(prefix)
    g.rig = rig
    g.root = rig["root"]
    stone = M.stone_god()
    robe = M.robe("god_robe", z_range=(0.0, 3.2))
    g.mats = {"stone": stone, "robe": robe}
    parts = []

    def fin(ob, joint):
        G.bake_attributes(ob, mud_top=0, wear_gain=5.0)
        G.set_mat(ob, stone)
        attach(ob, rig, joint)
        parts.append(ob)
        return ob

    # torso (pelvis..neck) with deltoid masses; gaunt, broad, statue-like
    tn = [(0, 0.0, 2.7, 0.4, 0.3), (0, 0.0, 3.05, 0.38, 0.28), (0, 0.02, 3.45, 0.46, 0.3), (0, 0.04, 3.9, 0.58, 0.34),
          (0, 0.05, 4.3, 0.56, 0.33), (0, 0.06, 4.62, 0.21, 0.21), (0, 0.06, 4.9, 0.19, 0.19),
          (0.56, 0.06, 4.36, 0.27, 0.26), (-0.56, 0.06, 4.36, 0.27, 0.26)]
    te = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (4, 7), (4, 8)]
    torso = skin_mesh(prefix + "torso", tn, te, disp=0.03)
    # chest: pectoral masses and a sunken sternum line, ribs under the pecs
    for sx in (-1, 1):
        bulge(torso, (sx * 0.22, -0.26, 4.08), 0.2, 0.07)
        bulge(torso, (sx * 0.2, -0.24, 3.62), 0.1, -0.025)
        bulge(torso, (sx * 0.12, -0.24, 3.35), 0.09, 0.025)
        bulge(torso, (sx * 0.12, -0.24, 3.15), 0.08, 0.02)
    bulge(torso, (0, -0.3, 3.9), 0.06, -0.035)
    fin(torso, "chest")
    for side, sx in (("L", 1), ("R", -1)):
        sh, el, wr = V(*J["upperarm_" + side]), V(*J["forearm_" + side]), V(*J["hand_" + side])
        ua = skin_mesh(prefix + "uarm_" + side, [tuple(sh) + (0.25, 0.25), tuple(sh + (el - sh) * 0.5) + (0.22, 0.21),
                                                 tuple(el) + (0.17, 0.17)], [(0, 1), (1, 2)], disp=0.02)
        fin(ua, "upperarm_" + side)
        fa = skin_mesh(prefix + "farm_" + side, [tuple(el) + (0.17, 0.17), tuple(el + (wr - el) * 0.35) + (0.18, 0.16),
                                                 tuple(wr) + (0.12, 0.1)], [(0, 1), (1, 2)], disp=0.02)
        fin(fa, "forearm_" + side)
        # fist (gripping the pommel/grip): palm block + curled fingers
        hd = (wr - el) / np.linalg.norm(wr - el)
        pc = wr + hd * 0.12
        hn = [tuple(wr) + (0.1, 0.08), tuple(pc) + (0.14, 0.09)]
        he = [(0, 1)]
        for f in range(4):
            base = pc + hd * 0.1 + V(sx * (-0.09 + 0.06 * f), 0, 0)
            k1 = base + hd * 0.07 + V(0, 0.05, 0)
            k2 = k1 + V(0, 0.07, 0.04)
            hn += [tuple(base) + (0.042, 0.038), tuple(k1) + (0.038, 0.035), tuple(k2) + (0.034, 0.031)]
            i0 = len(hn) - 3
            he += [(1, i0), (i0, i0 + 1), (i0 + 1, i0 + 2)]
        tb = pc + V(-sx * 0.1, -0.03, 0.02)
        hn += [tuple(tb) + (0.04, 0.035), tuple(tb + hd * 0.07 + V(sx * 0.02, 0.04, 0)) + (0.03, 0.028)]
        he += [(1, len(hn) - 2), (len(hn) - 2, len(hn) - 1)]
        hand = skin_mesh(prefix + "hand_" + side, hn, he, disp=0.01)
        fin(hand, "hand_" + side)
        # legs (mostly under the robe) and bare feet
        hip, kn, an = V(*J["thigh_" + side]), V(*J["shin_" + side]), V(*J["foot_" + side])
        th = skin_mesh(prefix + "thigh_" + side, [tuple(hip) + (0.24, 0.24), tuple(kn) + (0.16, 0.16)], [(0, 1)], disp=0.02)
        fin(th, "thigh_" + side)
        sh2 = skin_mesh(prefix + "shin_" + side, [tuple(kn) + (0.16, 0.16), tuple(kn + (an - kn) * 0.3) + (0.15, 0.15),
                                                  tuple(an) + (0.09, 0.09)], [(0, 1), (1, 2)], disp=0.02)
        fin(sh2, "shin_" + side)
        fn = [tuple(an) + (0.1, 0.09), tuple(an + V(0, 0.1, -0.12)) + (0.09, 0.07),
              tuple(an + V(0, -0.2, -0.13)) + (0.1, 0.06), tuple(an + V(0, -0.36, -0.16)) + (0.105, 0.055)]
        fe = [(0, 1), (0, 2), (2, 3)]
        for k in range(5):
            tx = sx * (-0.065 + 0.033 * k) * (1 if sx > 0 else 1)
            b0 = an + V(tx, -0.38, -0.165)
            t1 = b0 + V(tx * 0.1, -0.06 + 0.008 * k, -0.02)
            r0 = 0.034 if k == 0 else 0.026 - 0.002 * k
            fn += [tuple(b0) + (r0, r0 * 0.8), tuple(t1) + (r0 * 0.85, r0 * 0.7)]
            i0 = len(fn) - 2
            fe += [(3, i0), (i0, i0 + 1)]
        foot = skin_mesh(prefix + "foot_" + side, fn, fe, disp=0.008)
        fin(foot, "foot_" + side)

    # head
    head = build_head(prefix + "head", (0, 0.03, 5.2), H=0.8)
    fin(head, "head")
    eyem = M.emission("god_eyes", (0.75, 0.88, 1.0), 40.0, ctrl="eye_glow")
    for sx in (-1, 1):
        e = G.ellipsoid_cap(prefix + "eye_%d" % sx, (sx * 0.096, -0.235, 5.243), (0.034, 0.016, 0.014), axis=(0, -1, 0),
                            polar=(0, 3.1), N=16, M=8)
        G.set_mat(e, eyem)
        attach(e, rig, "head")
        parts.append(e)
    g.mats["eyes"] = eyem

    # robes: floor-length skirt with deep folds, dragging hem
    rows, cols = 40, 96
    P = np.zeros((rows, cols, 3))
    for i in range(rows):
        t = i / (rows - 1)
        z = 3.15 - t * 3.13
        for j in range(cols):
            a = 2 * math.pi * j / cols
            rr = 0.46 + 0.62 * t ** 1.3
            rr += (0.02 + 0.07 * t) * math.sin(a * 13 + 0.7 * math.sin(a * 3)) + 0.03 * t * math.sin(a * 5 + 1.3)
            x = rr * math.sin(a) * 1.05
            y = -rr * math.cos(a) * 0.85 + 0.05
            zz = z + (0.05 * math.sin(a * 7) * t ** 3 if t > 0.9 else 0.0)
            P[i, j] = (x, y, zz)

    def skirt_skip(i, j):
        a = 2 * math.pi * j / cols
        # front slit over the left leg so the knee/foot can step through
        return i > rows * 0.42 and abs(a - 0.35) < 0.22

    skirt = G.grid_mesh(prefix + "robe_skirt", P, closed_u=True, skip=skirt_skip)
    G.finish_plate(skirt, thick=0.025, bevel=0, subsurf=1)
    G.set_mat(skirt, robe)
    attach(skirt, rig, "pelvis")
    parts.append(skirt)
    # cloak over the shoulders with a high collar, open at the front to show the cracked chest
    rows, cols = 56, 110
    P = np.zeros((rows, cols, 3))
    angs = []
    for i in range(rows):
        t = i / (rows - 1)
        z = 4.78 - t * 4.74
        open_half = 0.55 + 0.35 * t          # opening widens toward the floor
        for j in range(cols):
            a = open_half + (2 * math.pi - 2 * open_half) * j / (cols - 1)
            if z > 4.42:                      # collar: narrow, rising around the neck
                k = (z - 4.42) / 0.36
                rx, ry = 0.62 - 0.32 * k, 0.48 - 0.16 * k
            else:                             # over the shoulders, then falling wide
                k = (4.42 - z) / 4.4
                rx = 0.78 + 0.05 * math.sin(min(1, k * 6) * math.pi / 2) + 0.42 * k ** 1.2
                ry = 0.5 + 0.48 * k ** 1.1
            fold = (0.015 + 0.07 * t) * math.sin(a * 11 + 0.5 * math.sin(a * 3))
            x = (rx + fold) * math.sin(a)
            y = -(ry + fold) * math.cos(a) + 0.08
            zz = z - (0.06 * math.sin(a * 6) * (t - 0.9) / 0.1 if t > 0.9 else 0.0)
            P[i, j] = (x, y, zz)
    cloak = G.grid_mesh(prefix + "robe_cloak", P)
    G.finish_plate(cloak, thick=0.03, bevel=0, subsurf=1)
    G.set_mat(cloak, robe)
    attach(cloak, rig, "chest")
    parts.append(cloak)
    # halo behind the head (follows the head, floats with its own slow rotation)
    g.halo = build_halo(prefix, (0, 0.62, 5.25))
    halo_pivot = empty(prefix + "halo_pivot", (0, 0.62, 5.25), size=0.2)
    attach(halo_pivot, rig, "neck")
    halo_pivot.rotation_mode = "XYZ"
    attach(g.halo, {"p": halo_pivot}, "p")
    g.halo_pivot = halo_pivot
    parts.append(g.halo)

    # obsidian blade: planted point-down in front, hands on the pommel/grip
    g.blade = build_blade(prefix)
    m = Matrix.Rotation(math.pi, 4, "X")          # blade points down
    m.translation = Vector((0, -0.72, 3.15))       # grip top between the fists
    g.blade.matrix_world = m
    bpy.context.view_layer.update()
    blade_pivot = empty(prefix + "blade_pivot", (0, -0.72, 3.15), size=0.2)
    blade_pivot.rotation_mode = "XYZ"
    attach(blade_pivot, rig, "root")
    attach(g.blade, {"p": blade_pivot}, "p")
    g.blade_pivot = blade_pivot
    parts.append(g.blade)
    g.parts = parts
    return g
