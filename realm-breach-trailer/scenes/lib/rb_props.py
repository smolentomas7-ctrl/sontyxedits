"""UI-WORLD PROPS — loot drops, life orbs, the REBIRTH plaque and rings (M106, M303, M401-M403, F2d, E6).

All props are built around a root empty at `loc` (rotated by rot_z, scaled by scale) so a shot can move /
parent / key the root. Every call creates new uniquely named objects and materials, so each instance can
be animated independently.

API
---
  RARITY_ORDER = ["common", "rare", "epic", "mythic", "legendary", "morbidious", "god", "fallen equip"]
  loot(item='greatsword'|'sword'|'scythe'|'ring', rarity='common', loc, rot_z, seed) -> Loot
      .root (empty) .item (empty parenting the item meshes) .pillar (light beam, 7 m) .disc (floor glow)
      .light (point light at the item; .lights = both lights) .mats {item, pillar, disc}
      The item lies on the floor (z = loc z), centred in the pillar; its edges / fuller glow in the rarity colour.
      Controls on every loot material: CTRL_color (RGB), CTRL_rarity (ladder strength), CTRL_navy (fallen
      equip body), CTRL_glow (free master fade, default 1), CTRL_time (auto).
  set_rarity(loot, frame, rarity)       rarity name or index; keys colour / strength / beam width / light at
                                        `frame` with CONSTANT interpolation (call per quarter beat to cycle).
  life_orbs(loc, rot_z, scale) -> Orbs  .root .orbs [3 x Orb(.glass .core .halo .smoke .light .mats)] .frame
      Three ember-red glass orbs (core #FF3B3B) in a dark iron frame, orb centres at z = 0.2 * scale, 0.125 m
      apart along local X (orb 0 at -X). Glass radius 0.05.
  orb_dark(orbs, i, f0, frames=10)      orb i flares, dies over `frames` (core + its light fade, cinder glints),
                                        a smoke wisp curls up out of it for ~50 frames. Glass stays.
  rebirth_plaque(loc, rot_z, scale) -> Plaque  .root .text (Cinzel FONT object) .mat (text glow; CTRL_glow)
      .body .light .mats. Upright obsidian plaque 1.44 x 0.46 m centred on loc, facing -Y.
  plaque_pulse(plaque, f0, frames=12, peak=1.0)   one ember-gold glow pulse (keys CTRL_glow on its mats).
  ring(loc, rot=(0,0,0), gem='#FFE9A8', scale=1.0) -> band object (gem + light are children).
      Gold band lying flat (axis Z) on the floor at loc, gem on the band's -Y side. ob['glow_mat'] names the
      gem material (CTRL_glow, default 1); ring_glow(ob, frame, value) keys it. The light follows CTRL_glow.
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Vector

import rb_core as C
import rb_env_dungeon as DG
import rb_mat as M
import rb_mesh as G
from rb_core import hexcol, link

RARITY_ORDER = ["common", "rare", "epic", "mythic", "legendary", "morbidious", "god", "fallen equip"]
RARITY_HEX = dict(C.video.RARITIES)
FALLEN_GLOW = C.video.FALLEN_EQUIP_GLOW
LADDER = {"common": 0.35, "rare": 0.85, "epic": 1.0, "mythic": 1.05, "legendary": 1.2, "morbidious": 1.05,
          "god": 1.45, "fallen equip": 1.2}
BEAM_W = {"common": 0.45, "rare": 0.85, "epic": 0.95, "mythic": 1.0, "legendary": 1.08, "morbidious": 1.0,
          "god": 1.22, "fallen equip": 1.08}
NAVY = "#1B2A4A"
FONT = os.path.join(C.ROOT, "assets", "fonts", "Cinzel.ttf")


class _H:
    pass


def _root(name, loc, rot_z=0.0, scale=1.0):
    r = C.empty(name, loc, size=0.1)
    r.rotation_euler = (0, 0, rot_z)
    r.scale = (scale, scale, scale)
    return r


def _child(ob, parent):
    ob.parent = parent
    return ob


def _recalc(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def _rgb_ctrl(b, name, color):
    n = b.n("ShaderNodeRGB")
    n.name, n.label = "CTRL_" + name, name
    n.outputs[0].default_value = (*color, 1.0)
    return n


def _sphere(name, r, u=32, v=16, scale=(1, 1, 1), loc=(0, 0, 0), mat=None, smooth=True):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r)
    for vt in bm.verts:
        vt.co = Vector((vt.co.x * scale[0], vt.co.y * scale[1], vt.co.z * scale[2]))
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    ob = bpy.data.objects.new(name, me)
    link(ob)
    ob.location = loc
    if mat is not None:
        me.materials.append(mat)
    return ob


def _torus(acc, center, R, rx, rz, axis="Z", N=48, Mr=12, **attrs):
    """Torus with elliptical section (rx radial, rz along the axis) around `axis` ('Z' or 'Y')."""
    us = np.linspace(0, 2 * math.pi, N, endpoint=False)
    vs = np.linspace(0, 2 * math.pi, Mr, endpoint=False)
    V = []
    for u in us:
        for v in vs:
            rr = R + rx * math.cos(v)
            a, b_, h = rr * math.cos(u), rr * math.sin(u), rz * math.sin(v)
            V.append((a, b_, h) if axis == "Z" else (a, h, b_))
    V = np.array(V) + np.asarray(center, float)
    F = []
    for i in range(N):
        i2 = (i + 1) % N
        for j in range(Mr):
            j2 = (j + 1) % Mr
            F.append((i * Mr + j, i * Mr + j2, i2 * Mr + j2, i2 * Mr + j))
    return acc.add(V, F, **attrs)


def _constant(idblock, keys=("CTRL_color", "CTRL_rarity", "CTRL_navy", "color", "energy", "scale")):
    ad = getattr(idblock, "animation_data", None)
    if ad and ad.action:
        for fc in ad.action.fcurves:
            if any(k in fc.data_path for k in keys):
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"


def _drive_energy(light, mat, ctrl, k):
    fc = light.data.driver_add("energy")
    d = fc.driver
    d.type = "SCRIPTED"
    v = d.variables.new()
    v.name = "g"
    v.type = "SINGLE_PROP"
    v.targets[0].id_type = "MATERIAL"
    v.targets[0].id = mat
    v.targets[0].data_path = 'node_tree.nodes["CTRL_%s"].outputs[0].default_value' % ctrl
    d.expression = "max(g,0)*%.4f" % k
    return light


# =================================================================== materials
def mat_gold(name="PR_gold"):
    m = DG._cached(name)
    if m:
        return m
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    obj = (tc, "Object")
    n1 = DG._noise(b, obj, 300.0, 3.0)
    mp = b.n("ShaderNodeMapping", Vector=obj, Scale=(1.0, 1.0, 40.0))
    scr = DG._noise(b, mp, 400.0, 2.0)
    col = b.mix(b.math("MULTIPLY", (n1, "Fac"), 0.3), (0.86, 0.6, 0.24), (0.7, 0.45, 0.16))
    rough = b.math("ADD", 0.18, b.math("MULTIPLY", DG._mr(b, (scr, "Fac"), 0.55, 0.7), 0.18))
    bump = b.n("ShaderNodeBump", Strength=0.05, Distance=0.0003, Height=(scr, "Fac"))
    bs = b.bsdf(**{"Base Color": col, "Metallic": 1.0, "Roughness": rough, "Normal": bump})
    b.out(bs)
    return DG._tag(m)


def mat_leather(name="PR_leather"):
    m = DG._cached(name)
    if m:
        return m
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    nz = DG._noise(b, (tc, "Object"), 160.0, 6.0, 0.7)
    big = DG._noise(b, (tc, "Object"), 14.0, 3.0)
    col = b.mix(b.math("MULTIPLY", (big, "Fac"), 0.6), (0.025, 0.016, 0.01), (0.06, 0.038, 0.024))
    bump = b.n("ShaderNodeBump", Strength=0.3, Distance=0.001, Height=(nz, "Fac"))
    bs = b.bsdf(**{"Base Color": col, "Roughness": 0.7, "Normal": bump})
    b.out(bs)
    return DG._tag(m)


def mat_item(name, fuller=(1.0, 0.0), base_glow=0.06, steel=(0.06, 0.059, 0.057), edge_k=2.2):
    """Loot item metal: worn steel (or navy for 'fallen equip', CTRL_navy) whose edges (baked 'wear') and fuller
    line glow in CTRL_color * CTRL_rarity * CTRL_glow. fuller = (x0, x1) span of the fuller in object X."""
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    obj = (tc, "Object")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=obj)
    colc = _rgb_ctrl(b, "color", hexcol(RARITY_HEX["common"]))
    rk = b.ctrl("rarity", LADDER["common"])
    navy = b.ctrl("navy", 0.0)
    gk = b.ctrl("glow", 1.0)
    base_k = b.ctrl("glowbase", base_glow)
    wear = b.attr("wear")
    n1 = DG._noise(b, obj, 18.0, 5.0, 0.6)
    n2 = DG._noise(b, obj, 160.0, 3.0)
    st = b.mix(b.math("MULTIPLY", wear, 1.4), steel, (0.42, 0.41, 0.4))
    st = b.mix(b.math("MULTIPLY", DG._mr(b, (n1, "Fac"), 0.5, 0.7), 0.6), st, (0.03, 0.022, 0.016))
    nv = b.mix(b.math("MULTIPLY", wear, 0.8), hexcol(NAVY), (0.2, 0.3, 0.5))
    col = b.mix(navy, st, nv)
    fl = b.math("MULTIPLY", DG._mr(b, b.math("ABSOLUTE", (sep, "Y")), 0.0025, 0.0045, 1.0, 0.0),
                b.math("MULTIPLY", DG._mr(b, (sep, "X"), fuller[0], fuller[0] + 0.04),
                       DG._mr(b, (sep, "X"), fuller[1], fuller[1] - 0.06)))
    fl = b.math("MULTIPLY", fl, DG._mr(b, (n2, "Fac"), 0.35, 0.5, 0.5, 1.0))
    mask = b.math("ADD", base_k, b.math("ADD", b.math("MULTIPLY", b.math("POWER", wear, 1.5), edge_k),
                                        b.math("MULTIPLY", fl, 3.0)))
    estr = b.math("MULTIPLY", b.math("MULTIPLY", mask, rk), b.math("MULTIPLY", gk, 4.0))
    rough = b.math("ADD", 0.3, b.math("MULTIPLY", (n1, "Fac"), 0.2))
    bump = b.n("ShaderNodeBump", Strength=0.06, Distance=0.001, Height=(n2, "Fac"))
    bs = b.bsdf(**{"Base Color": col, "Metallic": b.math("SUBTRACT", 1.0, b.math("MULTIPLY", navy, 0.35)),
                   "Roughness": rough, "Normal": bump, "Emission Color": colc, "Emission Strength": estr})
    b.out(bs)
    return m


def mat_beam(name, height=7.0):
    """Loot light pillar (additive): bright at the floor fading upward, brighter at grazing angles, rising
    streaks and motes (CTRL_time)."""
    m, b = DG.new_additive(name)
    tc = b.n("ShaderNodeTexCoord")
    obj = (tc, "Object")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=obj)
    colc = _rgb_ctrl(b, "color", hexcol(RARITY_HEX["common"]))
    rk = b.ctrl("rarity", LADDER["common"])
    gk = b.ctrl("glow", 1.0)
    tm = b.ctrl("time", 0.0)
    h = b.math("DIVIDE", (sep, "Z"), height)
    vert = b.math("MULTIPLY", b.math("POWER", DG._mr(b, h, 0.0, 1.0, 1.0, 0.0), 1.6), DG._mr(b, (sep, "Z"), 0.0, 0.35))
    lw = b.n("ShaderNodeLayerWeight", Blend=0.5)
    fac = (lw, "Facing")
    edge = b.math("ADD", 0.05, b.math("MULTIPLY", b.math("MULTIPLY", b.math("POWER", fac, 1.5),
                                                           b.math("SUBTRACT", 1.0, b.math("POWER", fac, 5.0))), 1.4))
    ang = b.math("ARCTAN2", (sep, "Y"), (sep, "X"))
    sv = b.n("ShaderNodeCombineXYZ", X=b.math("MULTIPLY", ang, 1.6), Y=0.0, Z=b.math("SUBTRACT", (sep, "Z"),
                                                                                   b.math("MULTIPLY", tm, 1.1)))
    stk = DG._noise(b, b.n("ShaderNodeMapping", Vector=sv, Scale=(1.0, 1.0, 0.25)), 3.0, 3.0)
    stk = DG._mr(b, (stk, "Fac"), 0.3, 0.75, 0.45, 1.3)
    mv = DG._vadd(b, b.n("ShaderNodeMapping", Vector=obj, Scale=(7.0, 7.0, 3.0)),
                  b.n("ShaderNodeCombineXYZ", X=0.0, Y=0.0, Z=b.math("MULTIPLY", tm, -1.8)))
    vo = b.n("ShaderNodeTexVoronoi", Scale=1.0)
    b._in(vo, "Vector", mv)
    motes = b.math("MULTIPLY", DG._mr(b, (vo, "Distance"), 0.07, 0.02), DG._mr(b, h, 0.6, 0.0))
    s = b.math("ADD", b.math("MULTIPLY", b.math("MULTIPLY", vert, edge), b.math("MULTIPLY", stk, 4.0)),
               b.math("MULTIPLY", motes, 10.0))
    s = b.math("MULTIPLY", s, b.math("MULTIPLY", rk, gk))
    white = b.mix(b.math("MULTIPLY", vert, 0.35), colc, (1.0, 1.0, 1.0))
    b.out(DG.additive(b, white, s))
    DG.key_time(m)
    return m


def mat_disc(name):
    """Floor glow under a loot drop: soft radial pool + a crisp ring at the beam footprint."""
    m, b = DG.new_additive(name)
    tc = b.n("ShaderNodeTexCoord")
    obj = (tc, "Object")
    colc = _rgb_ctrl(b, "color", hexcol(RARITY_HEX["common"]))
    rk = b.ctrl("rarity", LADDER["common"])
    gk = b.ctrl("glow", 1.0)
    ln = b.n("ShaderNodeVectorMath", _operation="LENGTH")
    b._in(ln, 0, obj)
    r = (ln, "Value")
    pool = b.math("POWER", DG._mr(b, r, 0.0, 1.4, 1.0, 0.0), 2.6)
    ring = DG._mr(b, b.math("ABSOLUTE", b.math("SUBTRACT", r, 0.4)), 0.005, 0.03, 1.0, 0.0)
    nz = DG._noise(b, obj, 6.0, 3.0)
    s = b.math("ADD", b.math("MULTIPLY", pool, 1.6), b.math("MULTIPLY", ring, DG._mr(b, (nz, "Fac"), 0.35, 0.6, 0.6, 3.0)))
    s = b.math("MULTIPLY", s, b.math("MULTIPLY", rk, gk))
    b.out(DG.additive(b, colc, s))
    return m


# =================================================================== loot items (local: length along +X, flat)
def _blade(name, L, w0, w1, t, tip, mat, x0=0.0):
    xs = np.linspace(0.0, L, 46)
    P = []
    for x in xs:
        u = x / L
        w = w0 + (w1 - w0) * u
        th = t * (1 - 0.35 * u)
        if x > L - tip:
            k = ((L - x) / tip) ** 0.75
            w = w * k + 0.0006
            th = th * (0.4 + 0.6 * k)
        sec = [(w, 0.0), (0.55 * w, 0.7 * th), (0.18 * w, th), (-0.18 * w, th), (-0.55 * w, 0.7 * th),
               (-w, 0.0), (-0.55 * w, -0.7 * th), (-0.18 * w, -th), (0.18 * w, -th), (0.55 * w, -0.7 * th)]
        P.append([(x0 + x, sy, sz) for sy, sz in sec])
    ob = G.grid_mesh(name, P, closed_u=True, cap_start=True, cap_end=True)
    _recalc(ob)
    G.bake_attributes(ob, mud_top=0.0, wear_gain=3.0)
    ob.data.materials.append(mat)
    try:
        ob.data.use_auto_smooth = True
        ob.data.auto_smooth_angle = math.radians(50)
    except AttributeError:
        pass
    return ob


def _hilt(prefix, guard_half, grip_len, grip_r, pommel_r, iron, leather):
    acc = DG.Acc()
    DG.cbox(acc, (0, 0, 0), (0.022, guard_half, 0.019), ch=0.006)
    for s in (-1, 1):
        DG.cbox(acc, (0.008, s * (guard_half + 0.012), 0), (0.016, 0.018, 0.024), R=DG.rotm(0, 0, s * 0.35), ch=0.006)
    DG.cbox(acc, (0.03, 0, 0), (0.02, 0.03, 0.012), ch=0.005)
    T = np.eye(4)
    T[:3, :3] = DG.rotm(0, -math.pi / 2, 0)
    T[:3, 3] = (-grip_len - 0.02 - pommel_r * 0.8, 0, 0)
    DG.lathe(acc, list(np.linspace(-pommel_r, pommel_r, 9)),
             lambda k, z, th: pommel_r * math.sqrt(max(0.0, 1 - (z / pommel_r) ** 2)) * (1 + 0.06 * np.cos(8 * th)) + 0.002,
             N=24, T=T)
    hilt = acc.build(prefix + "_hilt", iron, smooth=40.0, bake=True)
    ga = DG.Acc()
    T = np.eye(4)
    T[:3, :3] = DG.rotm(0, -math.pi / 2, 0)
    T[:3, 3] = (-0.02, 0, 0)
    zs = list(np.linspace(0, grip_len, 28))
    DG.lathe(ga, zs, lambda k, z, th: grip_r * (1 + 0.07 * abs(math.sin(z / grip_len * math.pi * 9 + th.mean() * 0)))
             * (1 - 0.1 * (z / grip_len - 0.5) ** 2), N=16, T=T)
    grip = ga.build(prefix + "_grip", leather, smooth=60.0)
    return [hilt, grip]


def _scythe(prefix, mat, iron, leather):
    shaft = DG.Acc()
    pts = [(x, 0.012 * math.sin(x * 2.0), 0.0) for x in np.linspace(-0.15, 1.62, 14)]
    DG.tube_poly(shaft, pts, 0.017, N=12)
    for x in (-0.1, 0.55, 1.55):
        DG.tube_poly(shaft, [(x - 0.03, 0.012 * math.sin(x * 2), 0), (x + 0.03, 0.012 * math.sin(x * 2), 0)], 0.021, N=12)
    DG.cbox(shaft, (1.64, 0.02, 0), (0.05, 0.035, 0.02), ch=0.006)
    sh = shaft.build(prefix + "_shaft", leather, smooth=50.0)
    P = []
    S = np.linspace(0, 1, 40)
    for s in S:
        c = np.array((1.64 - 0.48 * s ** 1.8, 0.04 + 0.95 * s, 0.0))
        dc = np.array((-0.48 * 1.8 * max(s, 1e-3) ** 0.8, 0.95, 0.0))
        tg = dc / np.linalg.norm(dc)
        n = np.array((tg[1], -tg[0], 0.0))      # toward +X: the sharp inner edge faces the shaft's head side
        w = 0.085 * (1 - s) ** 0.8 + 0.002
        t = 0.0055 * (1 - 0.6 * s)
        sec = [(0.5 * w, 0.0), (0.0, 0.55 * t), (-0.45 * w, t), (-0.5 * w, 0.0), (-0.45 * w, -t), (0.0, -0.55 * t)]
        P.append([c + n * a + np.array((0, 0, z)) for a, z in sec])
    bl = G.grid_mesh(prefix + "_blade", P, closed_u=True, cap_start=True, cap_end=True)
    _recalc(bl)
    G.bake_attributes(bl, mud_top=0.0, wear_gain=3.0)
    bl.data.materials.append(mat)
    return [sh, bl]


def _ring_geo(name, gem_mat, gold, gem_scale=1.0):
    acc = DG.Acc()
    R = 0.0118
    _torus(acc, (0, 0, 0), R, 0.0016, 0.0028, axis="Z", N=64, Mr=12)
    cy = -(R + 0.0016 + 0.0022)
    T = np.eye(4)
    T[:3, :3] = DG.rotm(math.pi / 2, 0, 0)       # local Z -> -Y
    T[:3, 3] = (0, -(R + 0.0006), 0)
    DG.lathe(acc, [0.0, 0.0012, 0.0026, 0.0034], lambda k, z, th: (0.0034, 0.0046, 0.0052, 0.0049)[k], N=24, T=T)
    for i in range(4):
        a = math.pi / 4 + i * math.pi / 2
        p0 = Vector((0.0048 * math.cos(a), -(R + 0.0035), 0.0048 * math.sin(a)))
        p1 = Vector((0.0038 * math.cos(a), -(R + 0.0062), 0.0038 * math.sin(a)))
        DG.tube_poly(acc, [p0, p1], 0.0007, N=6)
    band = acc.build(name, gold, smooth=45.0, recalc=True)
    gem = _sphere(name + "_gem", 0.0044 * gem_scale, u=10, v=6, scale=(1.0, 0.8, 0.9), loc=(0, cy - 0.0012, 0),
                  mat=gem_mat, smooth=False)
    gem.parent = band
    return band, gem


def loot(item="greatsword", rarity="common", loc=(0, 0, 0), rot_z=0.0, seed=0, item_scale=None, beam_height=7.0,
         beam_radius=0.38):
    """Loot drop: item lying on the floor in a vertical light pillar of its rarity colour (see module doc)."""
    assert item in ("sword", "greatsword", "scythe", "ring"), item
    L = _H()
    L.kind = item
    L.root = _root("PR_loot", loc, rot_z)
    L.mats = {}
    iron = DG.mat_iron("PR_iron")
    leather = mat_leather()
    L.item = C.empty("PR_loot_item", (0, 0, 0), size=0.05)
    _child(L.item, L.root)
    parts = []
    if item in ("sword", "greatsword"):
        g = item == "greatsword"
        Lb = 1.22 if g else 0.64
        mi = mat_item("PR_loot_item_mat", fuller=(0.06, Lb * 0.72))
        parts.append(_blade("PR_loot_blade", Lb, 0.036 if g else 0.026, 0.028 if g else 0.021, 0.0065 if g else 0.005,
                            0.16 if g else 0.1, mi, x0=0.02))
        parts += _hilt("PR_loot", 0.2 if g else 0.11, 0.32 if g else 0.13, 0.0165 if g else 0.014,
                       0.034 if g else 0.024, mat_item("PR_loot_hilt_mat", base_glow=0.0, steel=(0.09, 0.088, 0.085),
                                                       edge_k=0.12), leather)
        L.mats["hilt"] = parts[-2].data.materials[0]
        span = (-(0.32 if g else 0.13) - 0.07, Lb + 0.02)
    elif item == "scythe":
        mi = mat_item("PR_loot_item_mat", fuller=(1.0, 0.0))
        parts += _scythe("PR_loot", mi, iron, leather)
        span = (-0.15, 1.68)
    else:
        mi = mat_item("PR_loot_item_mat", base_glow=1.6, steel=(0.06, 0.05, 0.03))
        band, gem = _ring_geo("PR_loot_ring", mi, mat_gold(), 1.0)
        parts += [band]
        span = (-0.015, 0.015)
    L.mats["item"] = mi
    sc = item_scale if item_scale is not None else (2.2 if item == "ring" else 1.0)
    # centre the item in the beam, rest it on the floor with a slight tilt (tip / pommel touching)
    cx = 0.5 * (span[0] + span[1])
    for p in parts:
        p.location = (-cx, 0, 0)
        _child(p, L.item)
    L.item.scale = (sc, sc, sc)
    tilt = 0.0 if item == "ring" else math.radians(1.2)
    L.item.rotation_euler = (0.0, tilt, 0.0)
    bpy.context.view_layer.update()
    zmin = 1e9
    for p in parts + [c for p in parts for c in p.children]:
        mw = p.matrix_world
        for v in p.data.vertices:
            zmin = min(zmin, (mw @ v.co).z)
    L.item.location.z = (loc[2] - zmin) / 1.0 + 0.001
    # beam, inner core, floor disc
    L.mats["pillar"] = mat_beam("PR_loot_beam", beam_height)
    acc = DG.Acc()
    for r, hh in ((beam_radius, beam_height),):
        N = 48
        th = np.linspace(0, 2 * math.pi, N, endpoint=False)
        zs = np.linspace(0, hh, 14)
        V = [(r * math.cos(a), r * math.sin(a), z) for z in zs for a in th]
        F = [(i * N + j, i * N + (j + 1) % N, (i + 1) * N + (j + 1) % N, (i + 1) * N + j) for i in range(len(zs) - 1)
             for j in range(N)]
        acc.add(V, F)
    L.pillar = acc.build("PR_loot_pillar", L.mats["pillar"], smooth=0, recalc=False)
    L.pillar.data.polygons.foreach_set("use_smooth", [True] * len(L.pillar.data.polygons))
    L.pillar.visible_shadow = False
    _child(L.pillar, L.root)
    L.mats["disc"] = mat_disc("PR_loot_disc")
    V, F = DG.polar_grid(0, 0, lambda th: np.full(th.shape, 1.5), lambda u, th, x, y: 0.004, NR=10, NT=64)
    da = DG.Acc()
    da.add(V, F)
    L.disc = da.build("PR_loot_disc", L.mats["disc"], smooth=0, recalc=False)
    L.disc.visible_shadow = False
    _child(L.disc, L.root)
    l1 = C.light("POINT", "PR_loot_light", (0, 0, 0.35), color=RARITY_HEX["common"], energy=30.0, size=0.15,
                 shadow=False, volume=1.5, specular=0.8)
    l1.data.use_custom_distance, l1.data.cutoff_distance = True, 7.0
    l2 = C.light("POINT", "PR_loot_light_hi", (0, 0, 2.3), color=RARITY_HEX["common"], energy=70.0, size=0.3,
                 shadow=False, volume=2.0, specular=0.15)
    l2.data.diffuse_factor = 0.35
    l2.data.use_custom_distance, l2.data.cutoff_distance = True, 8.0
    for lt in (l1, l2):
        _child(lt, L.root)
    L.light, L.lights = l1, [l1, l2]
    L.light_base = {l1.name: 30.0, l2.name: 70.0}
    L.rarity = None
    _apply_rarity(L, rarity, None)
    return L


def _apply_rarity(L, rarity, frame):
    name = RARITY_ORDER[rarity] if isinstance(rarity, int) else str(rarity)
    assert name in RARITY_ORDER, name
    col = hexcol(FALLEN_GLOW if name == "fallen equip" else RARITY_HEX[name])
    if name == "fallen equip":
        col = tuple(0.8 * c + 0.2 * n for c, n in zip(col, hexcol(NAVY)))
    k = LADDER[name]
    navy = 1.0 if name == "fallen equip" else 0.0
    for m in L.mats.values():
        nt = m.node_tree
        for cname, val in (("CTRL_color", (*col, 1.0)), ("CTRL_rarity", k), ("CTRL_navy", navy)):
            n = nt.nodes.get(cname)
            if n is None:
                continue
            n.outputs[0].default_value = val
            if frame is not None:
                n.outputs[0].keyframe_insert("default_value", frame=frame)
        if frame is not None:
            _constant(nt)
    for lt in L.lights:
        lt.data.color = col
        lt.data.energy = L.light_base[lt.name] * k
        if frame is not None:
            lt.data.keyframe_insert("color", frame=frame)
            lt.data.keyframe_insert("energy", frame=frame)
            _constant(lt.data)
    w = BEAM_W[name]
    L.pillar.scale = (w, w, 1.0)
    L.disc.scale = (0.7 + 0.3 * w, 0.7 + 0.3 * w, 1.0)
    if frame is not None:
        L.pillar.keyframe_insert("scale", frame=frame)
        L.disc.keyframe_insert("scale", frame=frame)
        _constant(L.pillar)
        _constant(L.disc)
    L.rarity = name


def set_rarity(loot, frame, rarity):
    """Key the loot's rarity (name or index into RARITY_ORDER) at `frame`, CONSTANT interpolation."""
    _apply_rarity(loot, rarity, frame)


# =================================================================== life orbs
def mat_glass(name="PR_orb_glass"):
    m = DG._cached(name)
    if m:
        return m
    m, b = M.new(name, blend="BLEND")
    m.shadow_method = "NONE"
    m.use_backface_culling = True
    lw = b.n("ShaderNodeLayerWeight", Blend=0.12)
    alpha = b.math("ADD", 0.07, b.math("MULTIPLY", (lw, "Fresnel"), 0.9))
    tc = b.n("ShaderNodeTexCoord")
    nz = DG._noise(b, (tc, "Object"), 60.0, 2.0)
    bump = b.n("ShaderNodeBump", Strength=0.04, Distance=0.0005, Height=(nz, "Fac"))
    bs = b.bsdf(**{"Base Color": (0.03, 0.006, 0.005), "Roughness": 0.03, "Alpha": alpha, "Normal": bump})
    bs.inputs["Specular IOR Level"].default_value = 1.0
    bs.inputs["Coat Weight"].default_value = 1.0
    bs.inputs["Coat Roughness"].default_value = 0.02
    b.out(bs)
    return DG._tag(m)


def mat_core(name):
    """Orb core: swirling ember-red fire (CTRL_core 1 = alive, 0 = dead charcoal), cinder glints (CTRL_cinder)."""
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    obj = (tc, "Object")
    tm = b.ctrl("time", 0.0)
    ck = b.ctrl("core", 1.0)
    cin = b.ctrl("cinder", 0.0)
    lw = b.n("ShaderNodeLayerWeight", Blend=0.5)
    hot = b.math("SUBTRACT", 1.0, (lw, "Facing"))
    sw = DG._noise(b, DG._vscale(b, obj, 40.0), 1.0, 4.0, 0.6, dims="4D", w=b.math("MULTIPLY", tm, 0.9))
    swk = DG._mr(b, (sw, "Fac"), 0.3, 0.75, 0.35, 1.25)
    heat = b.math("MULTIPLY", b.math("MULTIPLY", b.math("POWER", hot, 1.4), swk), b.math("MINIMUM", ck, 1.0))
    col = b.ramp(heat, [(0.0, (0.1, 0.0, 0.0)), (0.45, hexcol("#FF3B3B")), (0.85, (1.0, 0.3, 0.12)),
                        (1.0, (1.0, 0.62, 0.4))])
    estr = b.math("MULTIPLY", b.math("ADD", 0.8, b.math("MULTIPLY", b.math("POWER", heat, 1.5), 7.0)), ck)
    cv = b.n("ShaderNodeTexVoronoi", Scale=1.0)
    b._in(cv, "Vector", DG._vscale(b, obj, 160.0))
    glint = b.math("MULTIPLY", DG._mr(b, (cv, "Distance"), 0.18, 0.05), cin)
    estr = b.math("ADD", estr, b.math("MULTIPLY", glint, 6.0))
    ecol = b.mix(b.math("MINIMUM", ck, 1.0), (1.0, 0.25, 0.05), col)
    bs = b.bsdf(**{"Base Color": (0.012, 0.01, 0.01), "Roughness": 0.55, "Emission Color": ecol,
                   "Emission Strength": estr})
    b.out(bs)
    DG.key_time(m)
    return m


def mat_halo(name):
    m, b = DG.new_additive(name)
    m.use_backface_culling = True
    ck = b.ctrl("core", 1.0)
    lw = b.n("ShaderNodeLayerWeight", Blend=0.5)
    k = b.math("POWER", b.math("SUBTRACT", 1.0, (lw, "Facing")), 2.2)
    b.out(DG.additive(b, hexcol("#FF3B3B"), b.math("MULTIPLY", b.math("MULTIPLY", k, ck), 0.9)))
    return m


def mat_smoke(name):
    """Smoke wisp ribbons: attributes across (-1..1) / along (0..1). CTRL_smoke (opacity), CTRL_rise (reveal
    height 0..1.6), CTRL_time (auto)."""
    m, b = M.new(name, blend="BLEND")
    m.shadow_method = "NONE"
    m.use_backface_culling = False
    m.show_transparent_back = True
    tc = b.n("ShaderNodeTexCoord")
    obj = (tc, "Object")
    tm = b.ctrl("time", 0.0)
    sk = b.ctrl("smoke", 0.0)
    rise = b.ctrl("rise", 0.0)
    acr, alg = b.attr("across"), b.attr("along")
    p = DG._vadd(b, b.n("ShaderNodeMapping", Vector=obj, Scale=(22.0, 22.0, 7.0)),
                 b.n("ShaderNodeCombineXYZ", X=0.0, Y=0.0, Z=b.math("MULTIPLY", tm, -0.9)))
    nz = DG._noise(b, p, 1.0, 5.0, 0.6, dims="4D", w=b.math("MULTIPLY", tm, 0.3))
    edge = b.math("SUBTRACT", 1.0, b.math("POWER", b.math("ABSOLUTE", acr), 1.6))
    a = b.math("MULTIPLY", edge, DG._mr(b, (nz, "Fac"), 0.38, 0.72))
    a = b.math("MULTIPLY", a, b.math("MULTIPLY", DG._mr(b, alg, 0.0, 0.08), DG._mr(b, alg, 1.0, 0.45)))
    a = b.math("MULTIPLY", a, DG._mr(b, b.math("SUBTRACT", rise, alg), 0.0, 0.25))
    a = b.math("MULTIPLY", a, b.math("MULTIPLY", sk, 1.25))
    em = b.math("MULTIPLY", b.math("POWER", DG._mr(b, alg, 0.35, 0.0), 2.0), b.math("MULTIPLY", sk, 1.5))
    bs = b.bsdf(**{"Base Color": (0.22, 0.21, 0.2), "Roughness": 1.0, "Alpha": b.math("MINIMUM", a, 0.85),
                   "Emission Color": (1.0, 0.18, 0.06), "Emission Strength": em})
    bs.inputs["Specular IOR Level"].default_value = 0.0
    b.out(bs)
    DG.key_time(m)
    return m


def _wisp(name, x, z0, mat, seed):
    rnd = np.random.default_rng(seed)
    acc = DG.Acc()
    H = 0.32
    ph = rnd.uniform(0, 6, 3)
    for k, rot in enumerate((0.0, math.pi / 2, math.pi / 4)):
        rows = 30
        V, AC, AL = [], [], []
        for i in range(rows):
            u = i / (rows - 1)
            c = np.array((0.025 * math.sin(u * 7.0 + ph[k]) * u + 0.012 * math.sin(u * 15 + ph[k]),
                          0.02 * math.cos(u * 6.0 + ph[k]) * u, u * H))
            w = 0.008 + 0.075 * u ** 1.1
            d = np.array((math.cos(rot + u * 2.5), math.sin(rot + u * 2.5), 0.0))
            for j, s in enumerate((-1.0, 0.0, 1.0)):
                V.append(c + d * w * s)
                AC.append(s)
                AL.append(u)
        F = [(i * 3 + j, i * 3 + j + 1, (i + 1) * 3 + j + 1, (i + 1) * 3 + j) for i in range(rows - 1) for j in range(2)]
        acc.add(V, F, across=AC, along=AL)
    ob = acc.build(name, mat, smooth=0, recalc=False)
    ob.data.polygons.foreach_set("use_smooth", [True] * len(ob.data.polygons))
    ob.location = (x, 0, z0)
    ob.visible_shadow = False
    return ob


def life_orbs(loc=(0, 0, 0), rot_z=0.0, scale=1.0):
    """Three ember-red glass life orbs in a small dark-iron frame (see module doc)."""
    O = _H()
    O.root = _root("PR_orbs", loc, rot_z, scale)
    iron = DG.mat_iron("PR_iron")
    gold = mat_gold()
    glass = mat_glass()
    R, sp, zc = 0.05, 0.125, 0.2
    xs = [-sp, 0.0, sp]
    fr = DG.Acc()
    trim = DG.Acc()
    # lower bar (gently arched) + foot + stem + side arms
    bar = [(x, 0.0, zc - 0.072 + 0.012 * (1 - (x / 0.2) ** 2)) for x in np.linspace(-0.2, 0.2, 13)]
    DG.tube_poly(fr, bar, 0.0075, N=10)
    DG.tube_poly(fr, [(0, 0, zc - 0.06), (0, 0, 0.035)], lambda t: 0.009 + 0.004 * t, N=12)
    DG.lathe(fr, [0.0, 0.012, 0.022, 0.03, 0.036], lambda k, z, th: (0.07, 0.072, 0.06, 0.03, 0.018)[k] *
             (1 + 0.04 * np.cos(6 * th)), N=36)
    for s in (-1, 1):
        DG.tube_poly(fr, [(s * 0.02, 0, 0.03), (s * 0.12, 0, 0.06), (s * 0.2, 0, zc - 0.07), (s * 0.235, 0, zc + 0.01),
                          (s * 0.22, 0, zc + 0.06)], lambda t: 0.006 * (1 - 0.5 * t), N=8)
        DG.lathe(fr, [0.0, 0.012, 0.045], lambda k, z, th: (0.006, 0.004, 0.0)[k], N=10,
                 T=np.array([[1, 0, 0, s * 0.22], [0, 1, 0, 0], [0, 0, 1, zc + 0.06], [0, 0, 0, 1]]))
    for i, x in enumerate(xs):
        _torus(fr, (x, 0, zc), R + 0.008, 0.0042, 0.0042, axis="Y", N=56, Mr=10)
        _torus(trim, (x, -0.0005, zc), R + 0.0118, 0.0011, 0.0011, axis="Y", N=56, Mr=6)
        for a in (math.radians(210), math.radians(330), math.radians(270)):
            p0 = Vector((x + (R + 0.006) * math.cos(a), 0.0, zc + (R + 0.006) * math.sin(a)))
            p1 = Vector((x + (R - 0.012) * math.cos(a) * 0.9, -0.03, zc + (R - 0.01) * math.sin(a) * 0.95))
            p2 = Vector((x + (R - 0.012) * math.cos(a) * 0.9, 0.03, zc + (R - 0.01) * math.sin(a) * 0.95))
            DG.tube_poly(fr, [p0, p1], lambda t: 0.0035 * (1 - 0.6 * t), N=6)
            DG.tube_poly(fr, [p0, p2], lambda t: 0.0035 * (1 - 0.6 * t), N=6)
        DG.lathe(fr, [0.0, 0.01, 0.05], lambda k, z, th: (0.007, 0.005, 0.0)[k], N=10,
                 T=np.array([[1, 0, 0, x], [0, 1, 0, 0], [0, 0, 1, zc + R + 0.008], [0, 0, 0, 1]]))
    O.frame = fr.build("PR_orbs_frame", iron, smooth=45.0, bake=True)
    tr = trim.build("PR_orbs_trim", gold, smooth=60.0)
    for ob in (O.frame, tr):
        _child(ob, O.root)
    O.orbs = []
    O.mats = {"iron": iron, "gold": gold, "glass": glass}
    for i, x in enumerate(xs):
        o = _H()
        o.index = i
        o.mat = mat_core("PR_orb_core%d" % i)
        o.halo_mat = mat_halo("PR_orb_halo%d" % i)
        o.smoke_mat = mat_smoke("PR_orb_smoke%d" % i)
        o.glass = _sphere("PR_orb_glass%d" % i, R, 40, 20, loc=(x, 0, zc), mat=glass)
        o.glass.visible_shadow = False
        o.core = _sphere("PR_orb_core%d" % i, R * 0.56, 32, 16, loc=(x, 0, zc), mat=o.mat)
        o.halo = _sphere("PR_orb_halo%d" % i, R * 0.93, 32, 16, loc=(x, 0, zc), mat=o.halo_mat)
        o.halo.visible_shadow = False
        o.smoke = _wisp("PR_orb_smoke%d" % i, x, zc + R * 0.55, o.smoke_mat, 101 + i)
        o.light = C.light("POINT", "PR_orb_light%d" % i, (x, -0.01, zc), color="#FF3B3B", energy=0.35, size=0.02,
                          shadow=False, volume=0.0, specular=0.6)
        o.light.data.use_custom_distance, o.light.data.cutoff_distance = True, 0.8
        _drive_energy(o.light, o.mat, "core", 0.35)
        for ob in (o.glass, o.core, o.halo, o.smoke, o.light):
            _child(ob, O.root)
        o.mats = [o.mat, o.halo_mat, o.smoke_mat]
        O.orbs.append(o)
    return O


def orb_dark(orbs, i, f0, frames=10):
    """Key orb i dying from f0: brief flare, core + light fade out over `frames` with a flicker, cinder glints,
    a smoke wisp rising for ~50 frames. Glass stays."""
    o = orbs.orbs[i]
    frames = max(3, int(frames))
    keys = [(f0 - 1, 1.0), (f0 + 1, 1.35)]
    for k in range(2, frames + 1):
        u = (k - 1) / (frames - 1)
        v = 1.35 * (1 - C.ease_in_out(u)) * (1 + 0.22 * math.sin(k * 2.7)) if k < frames else 0.0
        keys.append((f0 + k, max(0.0, v)))
    for f, v in keys:
        M.key_ctrl(o.mat, "core", f, v)
        M.key_ctrl(o.halo_mat, "core", f, v)
    for f, v in ((f0, 0.0), (f0 + frames, 1.0), (f0 + frames + 30, 0.0)):
        M.key_ctrl(o.mat, "cinder", f, v)
    for f, v in ((f0 + 1, 0.0), (f0 + frames, 1.0), (f0 + frames + 25, 0.8), (f0 + frames + 55, 0.0)):
        M.key_ctrl(o.smoke_mat, "smoke", f, v)
    for f, v in ((f0, 0.0), (f0 + frames + 55, 1.6)):
        M.key_ctrl(o.smoke_mat, "rise", f, v)
    ad = o.smoke_mat.node_tree.animation_data
    for fc in ad.action.fcurves:
        if "CTRL_rise" in fc.data_path:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
    return o


# =================================================================== REBIRTH plaque
def mat_obsidian(name="PR_obsidian"):
    m = DG._cached(name)
    if m:
        return m
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    pos = (geo, "Position")
    wear = b.attr("wear")
    n1 = DG._noise(b, pos, 9.0, 4.0)
    vo = b.n("ShaderNodeTexVoronoi", Vector=pos, Scale=14.0, _feature="SMOOTH_F1")
    col = b.mix(b.math("MULTIPLY", wear, 0.6), (0.005, 0.0045, 0.005), (0.04, 0.034, 0.03))
    rough = b.math("ADD", 0.06, b.math("MULTIPLY", (n1, "Fac"), 0.12))
    hgt = b.math("ADD", b.math("MULTIPLY", (vo, "Distance"), 0.4), b.math("MULTIPLY", (n1, "Fac"), 0.2))
    bump = b.n("ShaderNodeBump", Strength=0.08, Distance=0.004, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump})
    bs.inputs["Specular IOR Level"].default_value = 0.8
    bs.inputs["Coat Weight"].default_value = 0.6
    bs.inputs["Coat Roughness"].default_value = 0.05
    b.out(bs)
    return DG._tag(m)


def mat_gold_glow(name, base=1.0, k=1.0, front=("Y", -1.0)):
    """Ember-gold carved letters / inlay: gold metal + emission (CTRL_glow); fronts burn brighter than bevels."""
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    nrm = b.n("ShaderNodeSeparateXYZ", Vector=(tc, "Normal"))
    gk = b.ctrl("glow", base)
    nz = DG._noise(b, (tc, "Object"), 9.0, 3.0)
    front = DG._mr(b, b.math("MULTIPLY", (nrm, front[0]), front[1]), 0.3, 0.95, 0.35, 1.0)
    heat = b.math("MULTIPLY", front, DG._mr(b, (nz, "Fac"), 0.3, 0.7, 0.75, 1.1))
    ecol = b.ramp(heat, [(0.3, hexcol("#FF6A1A")), (0.75, hexcol("#F2B544")), (1.0, hexcol("#FFE9A8"))])
    bs = b.bsdf(**{"Base Color": (0.9, 0.6, 0.25), "Metallic": 1.0, "Roughness": 0.28, "Emission Color": ecol,
                   "Emission Strength": b.math("MULTIPLY", b.math("MULTIPLY", heat, gk), 12.0 * k)})
    b.out(bs)
    return m


def mat_aura(name, base=1.0):
    m, b = DG.new_additive(name)
    tc = b.n("ShaderNodeTexCoord")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=(tc, "Object"))
    gk = b.ctrl("glow", base)
    ex = b.math("DIVIDE", (sep, "X"), 1.15)
    ez = b.math("DIVIDE", (sep, "Z"), 0.55)
    r = b.math("SQRT", b.math("ADD", b.math("MULTIPLY", ex, ex), b.math("MULTIPLY", ez, ez)))
    k = b.math("POWER", DG._mr(b, r, 0.55, 1.0, 1.0, 0.0), 2.5)
    b.out(DG.additive(b, hexcol("#FF7A22"), b.math("MULTIPLY", b.math("MULTIPLY", k, gk), 0.1)))
    return m


def cartouche(a, b, N=96):
    """Closed outline (N x 2, x / z) of a dark-fantasy cartouche: long flat top and bottom, notched pointed
    ends, chamfered corners. Resampled evenly along the perimeter, starting at (a, 0), counter-clockwise."""
    q = [(a, 0.0), (a - 0.07 * b / 0.23, 0.42 * b), (a - 0.1 * b / 0.23, 0.42 * b), (a - 0.16 * b / 0.23, b),
         (-(a - 0.16 * b / 0.23), b), (-(a - 0.1 * b / 0.23), 0.42 * b), (-(a - 0.07 * b / 0.23), 0.42 * b), (-a, 0.0)]
    q = q + [(x, -z) for x, z in reversed(q[1:-1])]
    q = np.array(q + [q[0]])
    seg = np.linalg.norm(np.diff(q, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    t = np.linspace(0, cum[-1], N, endpoint=False)
    return np.stack([np.interp(t, cum, q[:, 0]), np.interp(t, cum, q[:, 1])], 1)


def rebirth_plaque(loc=(0, 0, 0), rot_z=0.0, scale=1.0, word="REBIRTH"):
    """Carved obsidian plaque with the word in Cinzel, ember-gold glow (see module doc)."""
    P = _H()
    P.root = _root("PR_plaque", loc, rot_z, scale)
    obs = mat_obsidian()
    P.mat = mat_gold_glow("PR_plaque_glow", front=("Z", 1.0))
    aura = mat_aura("PR_plaque_aura")
    inl_mat = mat_gold_glow("PR_plaque_inlay", k=0.22)
    P.mats = [P.mat, aura, inl_mat]
    W, H, T = 0.72, 0.23, 0.05

    def sel(a, b_, n, N=96):
        return cartouche(a, b_, N)

    body = DG.Acc()
    for (a, b_, y0, y1, ch) in ((W, H, T, -T, 0.014), (W * 0.9, H * 0.78, -T + 0.004, -T - 0.012, 0.004)):
        rows = []
        for y, sc in ((y0, 1 - ch / W), (y0 - (y0 - y1) * 0.12, 1.0), (y1 + (y0 - y1) * 0.12, 1.0), (y1, 1 - ch / W)):
            pts = sel(a * sc, b_ * (1 - (1 - sc) * W / H), 5.0)
            rows.append([(x, y, z) for x, z in pts])
        Pm = np.array(rows)
        R_, Cc = Pm.shape[:2]
        V = Pm.reshape(-1, 3).tolist() + [[0, y0, 0], [0, y1, 0]]
        F = [(i * Cc + j, i * Cc + (j + 1) % Cc, (i + 1) * Cc + (j + 1) % Cc, (i + 1) * Cc + j)
             for i in range(R_ - 1) for j in range(Cc)]
        c0, c1 = len(V) - 2, len(V) - 1
        F += [(c0, (j + 1) % Cc, j) for j in range(Cc)]
        F += [(c1, (R_ - 1) * Cc + j, (R_ - 1) * Cc + (j + 1) % Cc) for j in range(Cc)]
        body.add(V, F)
    # side fleurons (raised diamonds) and top / bottom points
    for s in (-1, 1):
        V = [(s * 0.655, -T - 0.002, 0), (s * 0.615, -T - 0.002, 0.045), (s * 0.575, -T - 0.002, 0), (s * 0.615, -T - 0.002, -0.045),
             (s * 0.615, -T - 0.016, 0)]
        body.add(V, [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 3, 2, 1)])
    P.body = body.build("PR_plaque_body", obs, smooth=40.0, bake=True)
    _child(P.body, P.root)
    inl = DG.Acc()
    pts = sel(W * 0.945, H * 0.86, 5.0, 120)
    loop = [(x, -T - 0.003, z) for x, z in pts] + [(pts[0][0], -T - 0.003, pts[0][1])]
    DG.tube_poly(inl, loop, 0.0035, N=6, cap=False)
    for s in (-1, 1):
        DG.tube_poly(inl, [(s * 0.615, -T - 0.017, -0.026), (s * 0.615, -T - 0.017, 0.026)], 0.0028, N=6)
    inlay = inl.build("PR_plaque_inlay", inl_mat, smooth=60.0, recalc=True)
    _child(inlay, P.root)
    cu = bpy.data.curves.new("PR_plaque_text", "FONT")
    cu.body = word
    try:
        cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    except RuntimeError:
        pass
    cu.size = 0.24
    cu.space_character = 1.12
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    cu.extrude = 0.006
    cu.bevel_depth = 0.0022
    cu.bevel_resolution = 2
    cu.resolution_u = 8
    cu.materials.append(P.mat)
    P.text = bpy.data.objects.new("PR_plaque_text", cu)
    link(P.text)
    P.text.rotation_euler = (math.pi / 2, 0, 0)
    P.text.location = (0, -T - 0.012 - 0.006, -0.004)
    _child(P.text, P.root)
    P.glyphs = _union_glyphs(P.text, P.mat)
    me = bpy.data.meshes.new("PR_plaque_aura")
    me.from_pydata([(-1.3, T + 0.06, -0.7), (1.3, T + 0.06, -0.7), (1.3, T + 0.06, 0.7), (-1.3, T + 0.06, 0.7)], [],
                   [(0, 1, 2, 3)])
    au = bpy.data.objects.new("PR_plaque_aura", me)
    link(au)
    me.materials.append(aura)
    au.visible_shadow = False
    _child(au, P.root)
    P.aura = au
    P.light = C.light("POINT", "PR_plaque_light", (0, -0.42, -0.08), color="#FFA040", energy=3.0, size=0.25,
                      shadow=False, volume=0.4, specular=0.6)
    P.light.data.use_custom_distance, P.light.data.cutoff_distance = True, 3.0
    _drive_energy(P.light, P.mat, "glow", 3.0)
    _child(P.light, P.root)
    P.base = 1.0
    return P


def _union_glyphs(txt, mat):
    """Blender fills a glyph's contours even-odd, so fonts that keep overlapping contours (variable Cinzel: the
    E's arms) get holes. Rebuild the text as curve objects holding ONE outer contour each (+ the counters inside
    it) parented to the text object (which is then hidden in render): overlapping strokes union visually."""
    tmp = txt.copy()
    tmp.data = txt.data.copy()
    tmp.parent = None
    link(tmp)
    vl = bpy.context.view_layer
    for o in bpy.context.selected_objects:
        o.select_set(False)
    vl.objects.active = tmp
    tmp.select_set(True)
    bpy.ops.object.convert(target="CURVE")
    tmp = vl.objects.active
    cu = tmp.data

    def pts_of(sp):
        return [(p.co.x, p.co.y) for p in (sp.bezier_points if sp.type == "BEZIER" else sp.points)]

    def area(pts):
        return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))

    def inside(pt, poly):
        x, y = pt
        c = False
        for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
            if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                c = not c
        return c

    sps = [(sp, pts_of(sp)) for sp in cu.splines if len(pts_of(sp)) > 2]
    if not sps:
        bpy.data.objects.remove(tmp)
        return []
    ar = [area(p) for _, p in sps]
    sgn = 1.0 if ar[max(range(len(ar)), key=lambda i: abs(ar[i]))] > 0 else -1.0
    outers = [i for i, a_ in enumerate(ar) if a_ * sgn > 0]
    holes = [i for i, a_ in enumerate(ar) if a_ * sgn <= 0]
    out = []
    for k, oi in enumerate(outers):
        members = [oi] + [h for h in holes if inside(sps[h][1][0], sps[oi][1])]
        nc = bpy.data.curves.new("PR_plaque_glyph", "CURVE")
        nc.dimensions = "2D"
        nc.fill_mode = "BOTH"
        for attr in ("extrude", "bevel_depth", "bevel_resolution", "resolution_u", "offset"):
            setattr(nc, attr, getattr(cu, attr))
        for mi in members:
            sp = sps[mi][0]
            if sp.type == "BEZIER":
                ns = nc.splines.new("BEZIER")
                ns.bezier_points.add(len(sp.bezier_points) - 1)
                for a_, b_ in zip(ns.bezier_points, sp.bezier_points):
                    a_.handle_left_type, a_.handle_right_type = "FREE", "FREE"
                    a_.co, a_.handle_left, a_.handle_right = b_.co, b_.handle_left, b_.handle_right
            else:
                ns = nc.splines.new("POLY")
                ns.points.add(len(sp.points) - 1)
                for a_, b_ in zip(ns.points, sp.points):
                    a_.co = b_.co
            ns.use_cyclic_u = True
            ns.resolution_u = sp.resolution_u
        nc.materials.append(mat)
        ob = bpy.data.objects.new("PR_plaque_glyph", nc)
        link(ob)
        ob.parent = txt
        ob.location = (0, 0, 0.00004 * (k % 3))
        out.append(ob)
    bpy.data.objects.remove(tmp)
    txt.hide_render = True
    return out


def plaque_pulse(plaque, f0, frames=12, peak=1.0):
    """Key one glow pulse: base -> base * (1 + 2.2 * peak) at ~35 % -> base at f0 + frames."""
    b = plaque.base
    fp = f0 + max(1, int(round(frames * 0.35)))
    for m in plaque.mats:
        for f, v in ((f0, b), (fp, b * (1 + 2.2 * peak)), (f0 + frames, b)):
            M.key_ctrl(m, "glow", f, v)


# =================================================================== ring
def mat_gem(name, color):
    m, b = M.new(name)
    gk = b.ctrl("glow", 1.0)
    lw = b.n("ShaderNodeLayerWeight", Blend=0.4)
    core = b.math("SUBTRACT", 1.0, (lw, "Facing"))
    col = hexcol(color)
    hot = tuple(min(1.0, c * 0.4 + 0.6) for c in col)
    ecol = b.mix(b.math("POWER", core, 3.0), col, hot)
    bs = b.bsdf(**{"Base Color": col, "Roughness": 0.05, "Emission Color": ecol,
                   "Emission Strength": b.math("MULTIPLY", gk, b.math("ADD", 6.0, b.math("MULTIPLY", core, 14.0)))})
    bs.inputs["Coat Weight"].default_value = 1.0
    bs.inputs["Specular IOR Level"].default_value = 1.0
    b.out(bs)
    return m


def ring(loc=(0, 0, 0), rot=(0, 0, 0), gem="#FFE9A8", scale=1.0):
    """Gold ring with a glowing gem lying on the floor (see module doc). Returns the band object."""
    gm = mat_gem("PR_ring_gem", gem)
    band, g = _ring_geo("PR_ring", gm, mat_gold(), 1.0)
    band.location = (loc[0], loc[1], loc[2] + 0.0028 * scale)
    band.rotation_euler = rot
    band.scale = (scale, scale, scale)
    band["glow_mat"] = gm.name
    lt = C.light("POINT", "PR_ring_light", (0, -0.03, 0.012), color=gem, energy=0.25, size=0.004, shadow=False,
                 volume=0.3, specular=0.5)
    lt.data.use_custom_distance, lt.data.cutoff_distance = True, 0.6
    _drive_energy(lt, gm, "glow", 0.25 * scale)
    lt.parent = band
    return band


def ring_glow(ob, frame, value):
    M.key_ctrl(bpy.data.materials[ob["glow_mat"]], "glow", frame, value)
