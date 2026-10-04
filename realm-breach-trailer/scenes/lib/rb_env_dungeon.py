"""THE FALLEN WORLD — dungeon kit (montage M105-M508, E6, F2d).

Infinite floors in a dark void: a broken, floating platform of cracked stone slabs (ember seams glowing
through the joints and a fracture network in the stone), ruined ashlar walls, a grand arch, fluted columns
rising into darkness or snapped off, hanging iron chains, iron braziers, rubble, drifting ground mist, a
cloud sea far below and other floating platforms ("lower / upper floors") receding into the haze.

LOCKED LAYOUT (metres, Z up, characters face -Y)
------------------------------------------------
  fighting area   flat slab floor, top z = 0 for r < R_FIGHT (6.5 m) around the origin (floor_z = 0 there);
                  a carved ritual circle at r = 3.45 / 3.95 m glows faintly (CTRL_circle).
  platform edge   irregular, r ~ 9.5 .. 12.5 m (edge_radius(theta)); beyond r = 6.5 m the slabs sink, tilt
                  and drop out (magma glows through the holes); the rock underside hangs ~9 m into the void.
  causeways       broken slab bridges leaving at 90 deg (+Y, through the grand arch), 250 deg and 345 deg,
                  ending at distant platforms (CAUSEWAYS).
  grand arch      centred on (0, 10.1): opening 3.8 m, crown ~7.5 m. Frames a warrior at the origin seen from -Y.
  broken arch     250 deg, r ~10.3 (one pier + half the ring).
  columns         r 8.6-9.2 at COLUMNS angles; 62/116/195/320 deg rise 19 m into darkness, others snapped off.
  braziers        r 6.8 at 45/135/225/315 deg, bowl rim z = 1.1 m (marks['braziers']).
  walls           ruined ashlar arcs at r ~11 behind the columns (kept low on the -Y camera side).
  chains          hang from the dark above (z 16) down to z 2.6-5.2 m inside the ring, long ones past the
                  edge into the void, catenaries between columns (sway = driver on the frame).
  void            cloud sea around z = -9, floating platforms 30-90 m away at z -42 .. +8.

API
---
  build_dungeon(depth='floor1'|'struggle'|'deep'|'legend', seed=0) -> Dungeon
      .depth .objects .mats .ctrls {ctrl name: [materials]} .marks .floor_z(x, y) .key_ctrl(name, f, v)
      .lights (filled by lights_dungeon(dungeon=...)) .world
      marks: 'center' (0, 0, 0), 'warrior' (0, 0, 0), camera suggestions as (cam, aim, lens):
             'wide', 'high', 'low', 'mid', 'reverse', 'side', 'up'; 'braziers' [(x, y, z) flame centres],
             'arch' (x, y, z), 'causeways' [(start xy, end xy)].
      Also sets the world (void + fog, CTRL_fog) and calls tune_eevee().
  lights_dungeon(depth, dungeon=None, subject=(0,0,0), cam=(0,-6,1.6), follow=None) -> {name: light}
      shadowed key (front-side, high) + shadowed top shaft (the 2 shadow casters), ember rim (3 small cut-off
      points behind the shoulders), depth-coloured back rim, fill, floor bounce, seam up-light, brazier
      practicals (flicker drivers) and void glows from below. follow: subject lights parented to it.
  tune_eevee(sc=None)
  void_world(depth) -> world (used by build_dungeon; also for props on black)
  Material controls (Dungeon.key_ctrl or rb_mat.key_ctrl):
      floor:  CTRL_seam_glow, CTRL_circle, CTRL_time (auto)   magma: CTRL_glow, CTRL_time
      rock:   CTRL_vein      masonry: CTRL_heat      flame/coals: CTRL_flame, CTRL_time
      fog_*:  CTRL_density, CTRL_time                world: CTRL_fog
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import rb_core as C
import rb_mat as M
from rb_core import hexcol, link

DEPTHS = ("floor1", "struggle", "deep", "legend")
EMBER = "#FF6A1A"
R_FIGHT = 6.5
CAUSEWAYS = ((90.0, 44.0, -1.4), (250.0, 38.0, -3.0), (345.0, 34.0, 0.8))   # angle deg, far-platform dist, end z
BRAZIER_ANG = (45.0, 135.0, 225.0, 315.0)
BRAZIER_R = 6.8
TALL = 19.0
# angle deg, r, height (None = tall, into the dark), radius
COLUMNS = [(30, 8.9, 4.3, 0.6), (62, 8.6, None, 0.66), (116, 8.6, None, 0.66), (152, 8.9, 2.6, 0.6),
           (195, 9.0, None, 0.64), (226, 8.7, 6.2, 0.62), (292, 9.2, 1.5, 0.6), (320, 8.8, None, 0.64)]
WALLS = [(8, 48, 11.0, 3.2), (128, 176, 11.1, 4.2), (200, 238, 10.9, 1.7), (268, 334, 11.3, 1.15)]
CHAINS = [(-2.8, 5.6, 3.4), (3.1, 6.4, 4.6), (-6.3, 1.2, 2.9), (6.1, -0.9, 3.9), (1.3, 8.8, 5.2),
          (-4.3, -5.9, 4.4), (5.1, 3.6, 2.7), (-1.0, -3.6, 5.0)]
LONG_CHAINS = [(12.6, 6.0, -8.0), (-13.2, 3.0, -9.0), (4.6, 14.2, -6.0), (-9.4, -10.6, -7.5)]
ISLANDS = [(-36.0, 26.0, -16.0, 7.0), (42.0, 24.0, -26.0, 9.0), (-26.0, -44.0, -32.0, 8.0), (30.0, -38.0, 8.0, 5.0),
           (-52.0, -8.0, 5.0, 6.0), (8.0, 76.0, -42.0, 12.0), (64.0, -6.0, -12.0, 7.0)]

# per-depth look: seam colour/strength, practicals, fog, world, light colours / energies
LOOK = {
    "floor1": dict(seam="#FF6A1A", seam_k=0.45, circle=0.22, brazier=0.7, vein=0.35, magma=0.5, heat=0.15,
                   fog_col=(0.52, 0.55, 0.58), fog=0.07, world_fog=0.009, bg=(0.0030, 0.0034, 0.0040),
                   void="#5A6B7E", void_k=0.45, key="#A9B6C4", key_e=950.0, top="#BCC8D4", top_e=5200.0,
                   rim_k=1.0, back="#93A9BF", back_e=260.0, fill="#7F8FA0", fill_e=30.0, stone=1.0),
    "struggle": dict(seam="#FF6A1A", seam_k=0.8, circle=0.32, brazier=0.85, vein=0.6, magma=0.8, heat=0.3,
                     fog_col=(0.36, 0.56, 0.56), fog=0.08, world_fog=0.011, bg=(0.0016, 0.0038, 0.0044),
                     void="#1F6E6A", void_k=0.9, key="#6FA4A6", key_e=760.0, top="#8CC2C4", top_e=4300.0,
                     rim_k=1.1, back="#4FD2C8", back_e=380.0, fill="#3F6E70", fill_e=24.0, stone=0.8),
    "deep": dict(seam="#FF5A1A", seam_k=0.22, circle=0.08, brazier=0.3, vein=0.18, magma=0.25, heat=0.05,
                 fog_col=(0.47, 0.48, 0.5), fog=0.09, world_fog=0.012, bg=(0.0014, 0.0015, 0.0017),
                 void="#3A3F46", void_k=0.35, key="#9EA2A8", key_e=430.0, top="#C9CCD0", top_e=3600.0,
                 rim_k=0.75, back="#8E959E", back_e=200.0, fill="#5A6068", fill_e=14.0, stone=0.7),
    "legend": dict(seam="#FF9A2A", seam_k=1.6, circle=0.9, brazier=1.6, vein=1.2, magma=1.4, heat=0.6,
                   fog_col=(0.78, 0.58, 0.42), fog=0.07, world_fog=0.010, bg=(0.0045, 0.0026, 0.0015),
                   void="#FF5A14", void_k=1.2, key="#FFB65C", key_e=1300.0, top="#FFD27A", top_e=6200.0,
                   rim_k=1.3, back="#F2B544", back_e=520.0, fill="#7A4A2A", fill_e=24.0, stone=1.05),
}


# =================================================================== numpy value noise
class VN:
    """Seeded 3-D value noise (smoothstep lattice), vectorised. Range ~[-1, 1]."""

    def __init__(self, seed):
        r = np.random.default_rng(int(seed) & 0xFFFFFFFF)
        p = r.permutation(256)
        self.p = np.concatenate([p, p])
        self.v = r.uniform(-1.0, 1.0, 256)

    def __call__(self, x, y, z=0.0):
        x, y, z = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float), np.asarray(z, float))
        xi, yi, zi = np.floor(x).astype(int), np.floor(y).astype(int), np.floor(z).astype(int)
        fx, fy, fz = x - xi, y - yi, z - zi
        u, v, w = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy), fz * fz * (3 - 2 * fz)
        p = self.p

        def h(i, j, k):
            return self.v[p[p[p[i & 255] + (j & 255)] + (k & 255)]]

        def lx(j, k):
            return h(xi, yi + j, zi + k) * (1 - u) + h(xi + 1, yi + j, zi + k) * u

        a = lx(0, 0) * (1 - v) + lx(1, 0) * v
        b = lx(0, 1) * (1 - v) + lx(1, 1) * v
        return a * (1 - w) + b * w

    def fbm(self, x, y, z=0.0, octaves=4, gain=0.5):
        tot, amp, f, norm = 0.0, 1.0, 1.0, 0.0
        for o in range(octaves):
            tot = tot + amp * self(np.asarray(x) * f + o * 17.3, np.asarray(y) * f + o * 5.1, np.asarray(z) * f + o * 9.7)
            norm += amp
            amp *= gain
            f *= 2.03
        return tot / norm


# =================================================================== mesh accumulator
class Acc:
    """Collects many small pieces (blocks, drums, links) into one mesh with float point attributes."""

    def __init__(self):
        self.V, self.F, self.A = [], [], {}

    def add(self, verts, faces, **attrs):
        base = len(self.V)
        verts = np.asarray(verts, float).reshape(-1, 3)
        self.V.extend(verts.tolist())
        self.F.extend([tuple(base + i for i in f) for f in faces])
        n = len(verts)
        for k in set(self.A) | set(attrs):
            lst = self.A.setdefault(k, [0.0] * base)
            v = attrs.get(k, 0.0)
            lst.extend(list(v) if hasattr(v, "__len__") else [float(v)] * n)
        return base

    def build(self, name, mat=None, smooth=35.0, recalc=True, bake=False, mud_top=0.0):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.V, [], self.F)
        if recalc:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(me)
            bm.free()
        for k, lst in self.A.items():
            a = me.attributes.new(k, "FLOAT", "POINT")
            a.data.foreach_set("value", np.asarray(lst, np.float32))
        if smooth:
            me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
            try:
                me.use_auto_smooth = True
                me.auto_smooth_angle = math.radians(smooth)
            except AttributeError:
                pass
        me.update()
        ob = bpy.data.objects.new(name, me)
        link(ob)
        if mat is not None:
            me.materials.append(mat)
        if bake:
            import rb_mesh as G
            G.bake_attributes(ob, mud_top=mud_top, wear_gain=5.0)
        return ob


_BOX_KEYS = [(sx, sy, sz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]


def _cbox_topo():
    idx = {}
    for ci, (sx, sy, sz) in enumerate(_BOX_KEYS):
        for ai, ax in enumerate("xyz"):
            idx[(sx, sy, sz, ax)] = ci * 3 + ai
    F = []
    sq = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    for s in (-1, 1):
        F.append([idx[(s, a, b, "x")] for a, b in sq])
        F.append([idx[(a, s, b, "y")] for a, b in sq])
        F.append([idx[(a, b, s, "z")] for a, b in sq])
    for a in (-1, 1):
        for b in (-1, 1):
            F.append([idx[(-1, a, b, "y")], idx[(1, a, b, "y")], idx[(1, a, b, "z")], idx[(-1, a, b, "z")]])
            F.append([idx[(a, -1, b, "x")], idx[(a, 1, b, "x")], idx[(a, 1, b, "z")], idx[(a, -1, b, "z")]])
            F.append([idx[(a, b, -1, "x")], idx[(a, b, 1, "x")], idx[(a, b, 1, "y")], idx[(a, b, -1, "y")]])
    for c in _BOX_KEYS:
        F.append([idx[(*c, "x")], idx[(*c, "y")], idx[(*c, "z")]])
    return F


_CBOX_F = _cbox_topo()


def cbox(acc, center, half, R=None, ch=0.03, jit=None, top_drop=None, **attrs):
    """Chamfered box (24 verts) into `acc`. half=(hx, hy, hz); R = 3x3 rotation; jit = per-corner jitter (8x3);
    top_drop = per-top-corner downward offsets (4,) for broken / weathered tops."""
    hx, hy, hz = half
    ch = min(ch, 0.45 * min(half))
    V = []
    for ci, (sx, sy, sz) in enumerate(_BOX_KEYS):
        off = np.zeros(3) if jit is None else np.asarray(jit[ci])
        dz = 0.0
        if top_drop is not None and sz > 0:
            dz = -top_drop[(sx > 0) * 2 + (sy > 0)]
        V.append((sx * hx + off[0], sy * (hy - ch) + off[1], sz * (hz - ch) + off[2] + dz))
        V.append((sx * (hx - ch) + off[0], sy * hy + off[1], sz * (hz - ch) + off[2] + dz))
        V.append((sx * (hx - ch) + off[0], sy * (hy - ch) + off[1], sz * hz + off[2] + dz))
    V = np.array(V)
    if R is not None:
        V = V @ np.asarray(R).T
    V += np.asarray(center, float)
    return acc.add(V, _CBOX_F, **attrs)


def rotm(rx=0.0, ry=0.0, rz=0.0):
    return np.array((Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(ry, 3, "Y") @ Matrix.Rotation(rx, 3, "X")))


def lathe(acc, zs, rfn, N=48, cap0=True, cap1=True, jag=None, T=None, **attrs):
    """Surface of revolution around local Z: rows at zs (list), radius rfn(k, z, theta_array) -> array.
    jag(theta) lowers the last row (broken top). T: 4x4 transform (numpy) applied to the result."""
    th = np.linspace(0, 2 * math.pi, N, endpoint=False)
    rows = []
    for k, z in enumerate(zs):
        r = np.broadcast_to(np.asarray(rfn(k, z, th), float), th.shape)
        zz = np.full(N, float(z))
        if jag is not None and k == len(zs) - 1:
            zz = zz - jag(th)
        rows.append(np.stack([r * np.cos(th), r * np.sin(th), zz], 1))
    P = np.concatenate(rows)
    F = []
    R = len(zs)
    for k in range(R - 1):
        for j in range(N):
            j2 = (j + 1) % N
            F.append((k * N + j, k * N + j2, (k + 1) * N + j2, (k + 1) * N + j))
    extra = []
    if cap0:
        extra.append((0.0, 0.0, zs[0]))
        ci = len(P)
        F += [(ci, (j + 1) % N, j) for j in range(N)]
    if cap1:
        top = rows[-1][:, 2].mean() - (0.0 if jag is None else 0.04)
        extra.append((0.0, 0.0, top))
        ci = len(P) + len(extra) - 1
        b = (R - 1) * N
        F += [(ci, b + j, b + (j + 1) % N) for j in range(N)]
    if extra:
        P = np.concatenate([P, np.array(extra)])
    if T is not None:
        T = np.asarray(T)
        P = P @ T[:3, :3].T + T[:3, 3]
    return acc.add(P, F, **attrs)


def tube_poly(acc, pts, radius, N=8, cap=True, **attrs):
    """Tube along a polyline; radius = float or callable(t in 0..1)."""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rows = []
    up = Vector((0, 0, 1))
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        a = up if abs(t.dot(up)) < 0.95 else Vector((1, 0, 0))
        x = t.cross(a).normalized()
        y = t.cross(x)
        r = radius(i / (n - 1)) if callable(radius) else radius
        for j in range(N):
            ang = 2 * math.pi * j / N
            rows.append(tuple(p + (x * math.cos(ang) + y * math.sin(ang)) * r))
    F = []
    for i in range(n - 1):
        for j in range(N):
            j2 = (j + 1) % N
            F.append((i * N + j, i * N + j2, (i + 1) * N + j2, (i + 1) * N + j))
    if cap:
        rows += [tuple(pts[0]), tuple(pts[-1])]
        c0, c1 = n * N, n * N + 1
        F += [(c0, (j + 1) % N, j) for j in range(N)]
        F += [(c1, (n - 1) * N + j, (n - 1) * N + (j + 1) % N) for j in range(N)]
    return acc.add(rows, F, **attrs)


def polar_grid(cx, cy, rfn, zfn, NR=12, NT=96):
    """Disc / cap: rings 0..NR (u = 0 centre .. 1 rim) x NT angles. rfn(theta) -> rim radius,
    zfn(u, theta, x, y) -> z. Returns verts, faces (CCW from above)."""
    th = np.linspace(0, 2 * math.pi, NT, endpoint=False)
    rim = rfn(th)
    V = [(cx, cy, float(zfn(0.0, 0.0, cx, cy)))]
    for i in range(1, NR + 1):
        u = i / NR
        x = cx + rim * u * np.cos(th)
        y = cy + rim * u * np.sin(th)
        z = zfn(u, th, x, y)
        V += list(zip(x, y, np.broadcast_to(z, th.shape)))
    F = [(0, 1 + j, 1 + (j + 1) % NT) for j in range(NT)]
    for i in range(NR - 1):
        a, b = 1 + i * NT, 1 + (i + 1) * NT
        for j in range(NT):
            j2 = (j + 1) % NT
            F.append((a + j, b + j, b + j2, a + j2))
    return V, F


def box_object(name, lo, hi, mat):
    me = bpy.data.meshes.new(name)
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me.from_pydata(v, [], f)
    ob = bpy.data.objects.new(name, me)
    link(ob)
    me.materials.append(mat)
    ob.visible_shadow = False
    return ob


# =================================================================== node helpers
def _mr(b, v, f0, f1, t0=0.0, t1=1.0, clamp=True):
    node = b.n("ShaderNodeMapRange", Value=v, **{"From Min": f0, "From Max": f1, "To Min": t0, "To Max": t1})
    node.clamp = clamp
    return node


def _noise(b, vec, scale, detail=4.0, rough=0.55, dims="3D", w=None):
    nz = b.n("ShaderNodeTexNoise", Vector=vec, Scale=scale, Detail=detail, Roughness=rough)
    nz.noise_dimensions = dims
    if w is not None:
        b._in(nz, "W", w)
    return nz


def _vadd(b, a, c, op="ADD"):
    node = b.n("ShaderNodeVectorMath", _operation=op)
    b._in(node, 0, a)
    b._in(node, 1, c)
    return (node, "Vector")


def _vscale(b, a, s):
    node = b.n("ShaderNodeVectorMath", _operation="SCALE")
    b._in(node, 0, a)
    b._in(node, "Scale", s)
    return (node, "Vector")


def _lerp(b, f, x, y):
    return b.math("ADD", x, b.math("MULTIPLY", b.math("SUBTRACT", y, x), f))


def key_time(mat, fps=C.FPS):
    """CTRL_time = frame / fps on every frame (2 linear keys + linear extrapolation)."""
    node = M.ctrl_node(mat, "time")
    if node is None:
        return
    sock = node.outputs[0]
    for f, v in ((0, 0.0), (fps, 1.0)):
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=f)
    for fc in mat.node_tree.animation_data.action.fcurves:
        if 'CTRL_time' in fc.data_path:
            fc.extrapolation = "LINEAR"
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"


def _cached(name):
    m = bpy.data.materials.get(name)
    return m if (m is not None and m.get("rb_dungeon")) else None


def _tag(m):
    m["rb_dungeon"] = 1
    return m


def additive(b, color, strength):
    """Emission added on top of what is behind (BLEND material, no shadow)."""
    em = b.n("ShaderNodeEmission", Color=color, Strength=strength)
    tr = b.n("ShaderNodeBsdfTransparent", Color=(1.0, 1.0, 1.0))
    add = b.n("ShaderNodeAddShader")
    b.link(tr, add.inputs[0])
    b.link(em, add.inputs[1])
    return add


def new_additive(name):
    m, b = M.new(name, blend="BLEND")
    m.shadow_method = "NONE"
    m.use_backface_culling = False
    m.show_transparent_back = True
    return m, b


# =================================================================== materials
def mat_floor(depth):
    """Dark cracked basalt-like slabs. Point attributes: slab (per-slab random), geo (1 = real slab; 0 = far
    platform top -> procedural brick joints), wear / cav / mud (baked). Fracture network of warped Voronoi
    edges in broken runs: dark grooves with thin seam-coloured cores; ash in the low spots, damp patches;
    a carved ritual circle around the origin (CTRL_circle)."""
    name = "DG_floor_" + depth
    m = _cached(name)
    if m:
        return m
    lk = LOOK[depth]
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=(geo, "Position"))
    xy = b.n("ShaderNodeCombineXYZ", X=(sep, "X"), Y=(sep, "Y"), Z=0.0)
    tm = b.ctrl("time", 0.0)
    glow = b.ctrl("seam_glow", lk["seam_k"])
    circ = b.ctrl("circle", lk["circle"])
    a_slab, a_geo, a_wear, a_cav = b.attr("slab"), b.attr("geo"), b.attr("wear"), b.attr("cav")
    brick = b.n("ShaderNodeTexBrick", Vector=xy, Color1=(0, 0, 0), Color2=(1, 1, 1), Mortar=(0, 0, 0), Scale=1.0,
                **{"Mortar Size": 0.035, "Mortar Smooth": 0.2, "Bias": 0.0, "Brick Width": 1.45, "Row Height": 1.06})
    brick.offset, brick.offset_frequency = 0.5, 2
    slab = _lerp(b, a_geo, (brick, "Color"), a_slab)
    joint = b.math("MULTIPLY", (brick, "Fac"), b.math("SUBTRACT", 1.0, a_geo))
    n_big = _noise(b, xy, 0.11, 3.0)
    n_mid = _noise(b, xy, 0.85, 6.0, 0.62)
    n_fine = _noise(b, xy, 7.0, 8.0, 0.66)
    n_grain = _noise(b, xy, 48.0, 2.0)
    tone = b.math("ADD", b.math("MULTIPLY", slab, 0.4), b.math("MULTIPLY", (n_big, "Fac"), 0.35))
    tone = b.math("ADD", tone, b.math("MULTIPLY", (n_mid, "Fac"), 0.45))
    tone = b.math("SUBTRACT", tone, 0.2)
    s = lk["stone"]
    col = b.ramp(tone, [(0.12, (0.012 * s, 0.012 * s, 0.013 * s)), (0.45, (0.036 * s, 0.034 * s, 0.032 * s)),
                        (0.85, (0.085 * s, 0.078 * s, 0.07 * s))])
    col = b.mix(b.math("MULTIPLY", _mr(b, (n_grain, "Fac"), 0.63, 0.73), 0.45), col, (0.11, 0.105, 0.098))
    col = b.mix(b.math("MULTIPLY", _mr(b, (n_mid, "Fac"), 0.57, 0.7), 0.5), col, (0.006, 0.006, 0.006))
    col = b.mix(b.math("MULTIPLY", a_wear, 0.75), col, (0.14, 0.132, 0.12))
    col = b.mix(b.math("MULTIPLY", a_cav, 0.8), col, (0.004, 0.004, 0.004))
    col = b.mix(joint, col, (0.002, 0.002, 0.002))
    # fracture network
    wbig = _noise(b, xy, 0.14, 2.0)
    wfine = _noise(b, xy, 1.0, 3.0)
    wv = _vadd(b, xy, _vscale(b, _vadd(b, (wbig, "Color"), (0.5, 0.5, 0.5), "SUBTRACT"), 1.6))
    wv = _vadd(b, wv, _vscale(b, _vadd(b, (wfine, "Color"), (0.5, 0.5, 0.5), "SUBTRACT"), 0.2))
    v1 = b.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=0.55)
    b._in(v1, "Vector", wv)
    e1 = b.math("DIVIDE", (v1, "Distance"), 0.55)
    v2 = b.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=2.1)
    b._in(v2, "Vector", _vadd(b, wv, (3.1, 7.7, 0.0)))
    e2 = b.math("DIVIDE", (v2, "Distance"), 2.1)
    g1 = _mr(b, (_noise(b, _vadd(b, xy, (13.0, 7.0, 0.0)), 0.25, 2.0), "Fac"), 0.5, 0.54)
    g2 = b.math("MULTIPLY", b.math("MULTIPLY", _mr(b, e1, 0.05, 0.35), g1),
                _mr(b, (_noise(b, wv, 0.9, 2.0), "Fac"), 0.52, 0.56))
    core1, groove1 = _mr(b, e1, 0.002, 0.006, 1.0, 0.0), _mr(b, e1, 0.004, 0.022, 1.0, 0.0)
    core2, groove2 = _mr(b, e2, 0.0012, 0.004, 1.0, 0.0), _mr(b, e2, 0.002, 0.01, 1.0, 0.0)
    crack = b.math("MAXIMUM", b.math("MULTIPLY", core1, g1), b.math("MULTIPLY", core2, g2))
    groove = b.math("MAXIMUM", b.math("MULTIPLY", groove1, g1), b.math("MULTIPLY", groove2, g2))
    halo = b.math("MULTIPLY", _mr(b, e1, 0.0, 0.05, 1.0, 0.0), g1)
    halo = b.math("MULTIPLY", halo, halo)
    seg = _mr(b, (_noise(b, wv, 0.8, 3.0), "Fac"), 0.38, 0.64)
    col = b.mix(b.math("MULTIPLY", halo, 0.5), col, (0.006, 0.003, 0.0015))
    col = b.mix(b.math("MULTIPLY", groove, 0.9), col, (0.002, 0.0018, 0.0016))
    col = b.mix(crack, col, (0.0, 0.0, 0.0))
    # ritual circle: two carved rings + rune ticks between them, worn away in places
    rr = b.n("ShaderNodeVectorMath", _operation="LENGTH")
    b._in(rr, 0, xy)
    rad = (rr, "Value")
    ring1 = _mr(b, b.math("ABSOLUTE", b.math("SUBTRACT", rad, 3.45)), 0.012, 0.03, 1.0, 0.0)
    ring2 = _mr(b, b.math("ABSOLUTE", b.math("SUBTRACT", rad, 3.95)), 0.01, 0.026, 1.0, 0.0)
    ang = b.math("ARCTAN2", (sep, "Y"), (sep, "X"))
    tick = b.math("FRACT", b.math("MULTIPLY", ang, 72.0 / (2 * math.pi)))
    tickm = _mr(b, b.math("ABSOLUTE", b.math("SUBTRACT", tick, 0.5)), 0.42, 0.47)
    band = b.math("MULTIPLY", _mr(b, rad, 3.52, 3.56), _mr(b, rad, 3.88, 3.84))
    glyph = b.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=9.0)
    b._in(glyph, "Vector", b.n("ShaderNodeCombineXYZ", X=b.math("MULTIPLY", ang, 3.7), Y=rad, Z=0.0))
    glyphm = b.math("MULTIPLY", _mr(b, (glyph, "Distance"), 0.015, 0.04, 1.0, 0.0),
                    _mr(b, (_noise(b, xy, 2.2, 1.0), "Fac"), 0.45, 0.55))
    runes = b.math("MULTIPLY", band, b.math("MAXIMUM", b.math("MULTIPLY", tickm, 0.8), glyphm))
    cmask = b.math("MAXIMUM", b.math("MAXIMUM", ring1, ring2), runes)
    cmask = b.math("MULTIPLY", cmask, _mr(b, (_noise(b, xy, 1.3, 3.0), "Fac"), 0.36, 0.48))
    col = b.mix(b.math("MULTIPLY", cmask, 0.85), col, (0.003, 0.0025, 0.002))
    # ash in hollows, damp patches (glossy), dust
    wn = b.math("ADD", b.math("MULTIPLY", (_noise(b, xy, 0.2, 4.0), "Fac"), 0.6), b.math("MULTIPLY", (n_mid, "Fac"), 0.4))
    damp = _mr(b, wn, 0.53, 0.58)
    ash = b.math("MULTIPLY", _mr(b, (_noise(b, _vadd(b, xy, (17.0, 29.0, 0.0)), 0.35, 5.0, 0.6), "Fac"), 0.55, 0.68),
                 b.math("SUBTRACT", 1.0, damp))
    col = b.mix(b.math("MULTIPLY", ash, 0.55), col, (0.075, 0.072, 0.068))
    col = b.mix(b.math("MULTIPLY", damp, 0.5), col, (0.0, 0.0, 0.0))
    rough = b.math("ADD", 0.8, b.math("MULTIPLY", b.math("SUBTRACT", (n_fine, "Fac"), 0.5), 0.3))
    rough = _lerp(b, damp, rough, b.math("ADD", 0.18, b.math("MULTIPLY", (n_fine, "Fac"), 0.2)))
    rough = _lerp(b, ash, rough, 0.95)
    # emission
    fs = _vscale(b, xy, 0.6)
    flick = _noise(b, fs, 1.0, 2.0, dims="4D", w=b.math("MULTIPLY", tm, 0.5))
    flick = _mr(b, (flick, "Fac"), 0.3, 0.7, 0.5, 1.0)
    estr = b.math("MULTIPLY", b.math("ADD", b.math("MULTIPLY", crack, 9.0), b.math("MULTIPLY", halo, 0.3)), seg)
    estr = b.math("MULTIPLY", b.math("MULTIPLY", estr, flick), glow)
    estr = b.math("ADD", estr, b.math("MULTIPLY", b.math("MULTIPLY", cmask, circ), 5.0))
    # bump
    pits = b.n("ShaderNodeTexVoronoi", Vector=xy, Scale=16.0)
    hgt = b.math("ADD", b.math("MULTIPLY", (n_fine, "Fac"), 0.3), b.math("MULTIPLY", (n_mid, "Fac"), 0.25))
    hgt = b.math("ADD", hgt, b.math("ADD", b.math("MULTIPLY", (n_grain, "Fac"), 0.06),
                                     b.math("MULTIPLY", _mr(b, (pits, "Distance"), 0.0, 0.18, -1.0, 0.0), 0.1)))
    hgt = b.math("SUBTRACT", hgt, b.math("ADD", b.math("MULTIPLY", groove, 0.7), b.math("MULTIPLY", crack, 0.4)))
    hgt = b.math("SUBTRACT", hgt, b.math("ADD", b.math("MULTIPLY", joint, 1.2), b.math("MULTIPLY", cmask, 0.8)))
    bump = b.n("ShaderNodeBump", Strength=b.math("SUBTRACT", 1.0, b.math("MULTIPLY", damp, 0.6)), Distance=0.02,
               Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump, "Emission Color": hexcol(lk["seam"]),
                   "Emission Strength": estr})
    bs.inputs["Specular IOR Level"].default_value = 0.5
    b.out(bs)
    key_time(m)
    return _tag(m)


def mat_magma(depth):
    """Under the slabs (seen through joints and missing slabs): cooled crust with glowing seams."""
    name = "DG_magma_" + depth
    m = _cached(name)
    if m:
        return m
    lk = LOOK[depth]
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=(geo, "Position"))
    xy = b.n("ShaderNodeCombineXYZ", X=(sep, "X"), Y=(sep, "Y"), Z=0.0)
    g = b.ctrl("glow", lk["magma"])
    tm = b.ctrl("time", 0.0)
    nz = _noise(b, xy, 0.25, 3.0, dims="4D", w=b.math("MULTIPLY", tm, 0.12))
    k = _mr(b, (nz, "Fac"), 0.35, 0.7, 0.25, 1.0)
    vo = b.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=2.5)
    b._in(vo, "Vector", _vadd(b, xy, _vscale(b, (_noise(b, xy, 1.5, 2.0), "Color"), 0.3)))
    seam = _mr(b, (vo, "Distance"), 0.0, 0.14, 1.0, 0.1)
    heat = b.math("MULTIPLY", b.math("MULTIPLY", seam, seam), k)
    col = b.mix(_mr(b, heat, 0.0, 0.9), (0.5, 0.04, 0.003), hexcol(lk["seam"]))
    em = b.n("ShaderNodeEmission", Color=col, Strength=b.math("MULTIPLY", b.math("MULTIPLY", heat, g), 4.0))
    b.out(em)
    key_time(m)
    return _tag(m)


def mat_masonry(depth):
    """Ashlar blocks / columns / arches: weathered dark stone. Attributes: blk (per block), wear, cav, mud
    (dust at the base). Vertical rain / soot streaks, chisel tooling, faint heat glow in cracks near the floor."""
    name = "DG_masonry_" + depth
    m = _cached(name)
    if m:
        return m
    lk = LOOK[depth]
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    pos = (geo, "Position")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=pos)
    heat = b.ctrl("heat", lk["heat"])
    blk, wear, cav, mud = b.attr("blk"), b.attr("wear"), b.attr("cav"), b.attr("mud")
    n1 = _noise(b, pos, 0.6, 5.0, 0.6)
    n2 = _noise(b, pos, 5.0, 8.0, 0.65)
    s = lk["stone"]
    tone = b.math("ADD", b.math("MULTIPLY", blk, 0.45), b.math("MULTIPLY", (n1, "Fac"), 0.55))
    col = b.ramp(tone, [(0.25, (0.02 * s, 0.019 * s, 0.018 * s)), (0.55, (0.05 * s, 0.047 * s, 0.043 * s)),
                        (0.85, (0.1 * s, 0.093 * s, 0.084 * s))])
    smp = b.n("ShaderNodeMapping", Vector=pos, Scale=(5.0, 5.0, 0.3))
    streak = _noise(b, smp, 3.0, 6.0, 0.6)
    col = b.mix(1.0, col, _mr(b, (streak, "Fac"), 0.45, 0.7, 1.0, 0.45), blend="MULTIPLY")
    col = b.mix(b.math("MULTIPLY", wear, 0.8), col, (0.16, 0.15, 0.135))
    col = b.mix(b.math("MULTIPLY", cav, 0.9), col, (0.004, 0.004, 0.004))
    dust = b.math("MULTIPLY", mud, _mr(b, (n2, "Fac"), 0.4, 0.6))
    col = b.mix(b.math("MULTIPLY", dust, 0.7), col, (0.08, 0.077, 0.072))
    # cracks
    vo = b.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=1.3)
    b._in(vo, "Vector", _vadd(b, pos, _vscale(b, (_noise(b, pos, 1.2, 2.0), "Color"), 0.35)))
    cr = b.math("MULTIPLY", _mr(b, (vo, "Distance"), 0.003, 0.012, 1.0, 0.0),
                _mr(b, (_noise(b, pos, 0.5, 2.0), "Fac"), 0.52, 0.58))
    col = b.mix(cr, col, (0.0, 0.0, 0.0))
    low = _mr(b, (sep, "Z"), 1.6, 0.0)
    estr = b.math("MULTIPLY", b.math("MULTIPLY", cr, low), b.math("MULTIPLY", heat, 6.0))
    chis = b.n("ShaderNodeTexWave", Vector=pos, Scale=6.0, Distortion=4.0, Detail=3.0, _bands_direction="DIAGONAL")
    pits = b.n("ShaderNodeTexVoronoi", Vector=pos, Scale=22.0)
    hgt = b.math("ADD", b.math("MULTIPLY", (n2, "Fac"), 0.5), b.math("MULTIPLY", (chis, "Fac"), 0.12))
    hgt = b.math("ADD", hgt, b.math("MULTIPLY", _mr(b, (pits, "Distance"), 0.0, 0.15, -1.0, 0.0), 0.15))
    hgt = b.math("SUBTRACT", hgt, b.math("MULTIPLY", cr, 0.8))
    bump = b.n("ShaderNodeBump", Strength=0.6, Distance=0.02, Height=hgt)
    rough = b.math("ADD", 0.78, b.math("MULTIPLY", b.math("SUBTRACT", (n2, "Fac"), 0.5), 0.3))
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump, "Emission Color": hexcol(lk["seam"]),
                   "Emission Strength": estr})
    bs.inputs["Specular IOR Level"].default_value = 0.4
    b.out(bs)
    return _tag(m)


def mat_rock(depth):
    """Underside of the floating platforms and void debris: jagged basalt with strata and seam-coloured veins,
    hotter toward the bottom (CTRL_vein)."""
    name = "DG_rock_" + depth
    m = _cached(name)
    if m:
        return m
    lk = LOOK[depth]
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    pos = (geo, "Position")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=pos)
    vk = b.ctrl("vein", lk["vein"])
    n1 = _noise(b, pos, 0.35, 6.0, 0.6)
    n2 = _noise(b, pos, 3.5, 8.0, 0.65)
    strata = b.n("ShaderNodeTexWave", Vector=pos, Scale=0.9, Distortion=6.0, Detail=4.0, _bands_direction="Z")
    t = b.math("ADD", b.math("MULTIPLY", (n1, "Fac"), 0.6), b.math("MULTIPLY", (strata, "Fac"), 0.3))
    s = lk["stone"]
    col = b.ramp(t, [(0.3, (0.008 * s, 0.008 * s, 0.009 * s)), (0.6, (0.03 * s, 0.028 * s, 0.026 * s)),
                     (0.9, (0.07 * s, 0.064 * s, 0.058 * s))])
    vo = b.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=0.5)
    b._in(vo, "Vector", _vadd(b, pos, _vscale(b, (_noise(b, pos, 0.4, 3.0), "Color"), 1.2)))
    d = b.math("DIVIDE", (vo, "Distance"), 0.5)
    core = _mr(b, d, 0.004, 0.018, 1.0, 0.0)
    halo = _mr(b, d, 0.0, 0.12, 1.0, 0.0)
    gate = _mr(b, (_noise(b, pos, 0.3, 2.0), "Fac"), 0.47, 0.55)
    depthk = _mr(b, (sep, "Z"), -0.6, -7.0, 0.25, 1.4)
    vein = b.math("MULTIPLY", b.math("ADD", core, b.math("MULTIPLY", b.math("MULTIPLY", halo, halo), 0.15)), gate)
    col = b.mix(b.math("MULTIPLY", core, gate), col, (0.0, 0.0, 0.0))
    estr = b.math("MULTIPLY", b.math("MULTIPLY", vein, depthk), b.math("MULTIPLY", vk, 7.0))
    hgt = b.math("ADD", b.math("MULTIPLY", (n2, "Fac"), 0.6), b.math("MULTIPLY", (n1, "Fac"), 0.6))
    hgt = b.math("SUBTRACT", hgt, b.math("MULTIPLY", core, 0.5))
    bump = b.n("ShaderNodeBump", Strength=0.8, Distance=0.05, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Roughness": 0.9, "Normal": bump, "Emission Color": hexcol(lk["seam"]),
                   "Emission Strength": estr})
    bs.inputs["Specular IOR Level"].default_value = 0.35
    b.out(bs)
    return _tag(m)


def mat_iron(name="DG_iron"):
    """Blackened forged iron with rust blooms (chains, braziers, props)."""
    m = _cached(name)
    if m:
        return m
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    geo = b.n("ShaderNodeNewGeometry")
    pos = (geo, "Position")
    wear = b.attr("wear")
    n1 = _noise(b, pos, 3.0, 6.0, 0.6)
    n2 = _noise(b, pos, 40.0, 4.0, 0.6)
    rust = b.math("MULTIPLY", _mr(b, (n1, "Fac"), 0.5, 0.66), _mr(b, (n2, "Fac"), 0.3, 0.6, 0.6, 1.0))
    base = b.ramp((n2, "Fac"), [(0.3, (0.014, 0.0135, 0.013)), (0.7, (0.03, 0.028, 0.026))])
    col = b.mix(rust, base, (0.07, 0.03, 0.014))
    col = b.mix(b.math("MULTIPLY", wear, 0.7), col, (0.22, 0.21, 0.2))
    metal = b.math("SUBTRACT", 0.85, b.math("MULTIPLY", rust, 0.7))
    rough = b.math("ADD", 0.42, b.math("MULTIPLY", rust, 0.45))
    pit = _noise(b, (tc, "Object"), 120.0, 2.0)
    hgt = b.math("ADD", b.math("MULTIPLY", (pit, "Fac"), 0.3), b.math("MULTIPLY", rust, 0.4))
    bump = b.n("ShaderNodeBump", Strength=0.25, Distance=0.004, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Metallic": metal, "Roughness": rough, "Normal": bump})
    b.out(bs)
    return _tag(m)


def mat_flame(depth, name=None):
    """Additive fire tongues: object-space height mask (origin at the brazier foot, flames from z 1.0),
    rising 4-D noise; colour from deep red to yellow-white. CTRL_flame, CTRL_time."""
    name = name or "DG_flame_" + depth
    m = _cached(name)
    if m:
        return m
    lk = LOOK[depth]
    m, b = new_additive(name)
    tc = b.n("ShaderNodeTexCoord")
    obj = (tc, "Object")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=obj)
    tm = b.ctrl("time", 0.0)
    fk = b.ctrl("flame", lk["brazier"])
    rise = b.n("ShaderNodeCombineXYZ", X=0.0, Y=0.0, Z=b.math("MULTIPLY", tm, -1.6))
    p = _vadd(b, b.n("ShaderNodeMapping", Vector=obj, Scale=(1.0, 1.0, 0.55)), rise)
    nz = _noise(b, p, 5.0, 3.0, 0.6, dims="4D", w=b.math("MULTIPLY", tm, 1.3))
    h = _mr(b, (sep, "Z"), 1.0, 1.75, 1.0, 0.0)
    lw = b.n("ShaderNodeLayerWeight", Blend=0.4)
    core = b.math("SUBTRACT", 1.0, (lw, "Facing"))
    mask = b.math("MULTIPLY", b.math("POWER", h, 1.4), _mr(b, (nz, "Fac"), 0.32, 0.68, 0.0, 1.3))
    mask = b.math("MULTIPLY", mask, b.math("ADD", 0.25, b.math("MULTIPLY", core, 0.75)))
    col = b.ramp(mask, [(0.0, (0.35, 0.02, 0.0)), (0.35, (1.0, 0.22, 0.03)), (0.75, (1.0, 0.55, 0.16)),
                        (1.0, (1.0, 0.85, 0.55))])
    strength = b.math("MULTIPLY", b.math("POWER", mask, 1.6), b.math("MULTIPLY", fk, 30.0))
    b.out(additive(b, col, strength))
    key_time(m)
    return _tag(m)


def mat_coals(depth):
    name = "DG_coals_" + depth
    m = _cached(name)
    if m:
        return m
    lk = LOOK[depth]
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    pos = (geo, "Position")
    tm = b.ctrl("time", 0.0)
    fk = b.ctrl("flame", lk["brazier"])
    vo = b.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=18.0)
    b._in(vo, "Vector", pos)
    seam = _mr(b, (vo, "Distance"), 0.0, 0.12, 1.0, 0.0)
    fl = _noise(b, pos, 6.0, 2.0, dims="4D", w=b.math("MULTIPLY", tm, 0.8))
    heat = b.math("MULTIPLY", b.math("ADD", seam, 0.15), _mr(b, (fl, "Fac"), 0.3, 0.7, 0.3, 1.2))
    col = b.mix(_mr(b, heat, 0.2, 1.0), (0.6, 0.06, 0.005), (1.0, 0.45, 0.1))
    bs = b.bsdf(**{"Base Color": (0.01, 0.009, 0.008), "Roughness": 0.9, "Emission Color": col,
                   "Emission Strength": b.math("MULTIPLY", heat, b.math("MULTIPLY", fk, 9.0))})
    b.out(bs)
    key_time(m)
    return _tag(m)


def mat_fog(name, density=0.05, height=1.2, color=(0.5, 0.55, 0.6), anisotropy=0.4, scale=0.09,
            wind=(0.35, 0.12, 0.0), z0=0.0, layer=None, emit_color=None, emit=0.0, contrast=(0.35, 0.68, 0.06, 1.4),
            radial=None):
    """Drifting haze. density = CTRL_density * shape * noise; shape = exp(-(z-z0)/height) (or a gaussian layer
    (zc, half-width) when layer is set, or a radial ball (centre xyz, radius) when radial is set)."""
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    pos = (geo, "Position")
    tm = b.ctrl("time", 0.0)
    dk = b.ctrl("density", density)
    sep = b.n("ShaderNodeSeparateXYZ", Vector=pos)
    drift = b.n("ShaderNodeCombineXYZ", X=b.math("MULTIPLY", tm, -wind[0]), Y=b.math("MULTIPLY", tm, -wind[1]),
                Z=b.math("MULTIPLY", tm, -wind[2]))
    p = _vadd(b, pos, drift)
    nz = _noise(b, p, scale, 3.0, 0.55, dims="4D", w=b.math("MULTIPLY", tm, 0.04))
    nz2 = _noise(b, p, scale * 4.0, 2.0, 0.5)
    n = b.math("ADD", b.math("MULTIPLY", (nz, "Fac"), 0.75), b.math("MULTIPLY", (nz2, "Fac"), 0.25))
    nk = _mr(b, n, *contrast)
    if radial is not None:
        dc = b.n("ShaderNodeVectorMath", _operation="DISTANCE")
        b._in(dc, 0, pos)
        dc.inputs[1].default_value = radial[0]
        f = _mr(b, (dc, "Value"), radial[1], 0.0)
        shape = b.math("MULTIPLY", f, f)
    elif layer is not None:
        dz = b.math("DIVIDE", b.math("SUBTRACT", (sep, "Z"), layer[0]), layer[1])
        shape = b.math("EXPONENT", b.math("MULTIPLY", b.math("MULTIPLY", dz, dz), -1.0))
    else:
        shape = b.math("MINIMUM", b.math("EXPONENT", b.math("MULTIPLY", b.math("SUBTRACT", (sep, "Z"), z0),
                                                              -1.0 / height)), 1.0)
    shape = b.math("MULTIPLY", shape, nk)
    vol = b.n("ShaderNodeVolumePrincipled", Color=color, Density=b.math("MULTIPLY", shape, dk), Anisotropy=anisotropy)
    if emit_color is not None:
        vol.inputs["Emission Color"].default_value = (*hexcol(emit_color), 1.0)
        ek = b.ctrl("emit", emit)
        b.link(b.math("MULTIPLY", shape, ek), vol.inputs["Emission Strength"])
    b.out(volume=vol)
    key_time(m)
    return _tag(m)


# =================================================================== world / render
def void_world(depth="struggle"):
    """Void: near-black background, a faint depth-coloured glow from the abyss below the horizon (dimmer to
    the camera than in reflections), uniform haze (CTRL_fog)."""
    lk = LOOK[depth]
    sc = bpy.context.scene
    w = bpy.data.worlds.new("DG_world_" + depth)
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")

    def math(op, a, bb):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for i, v in enumerate((a, bb)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]

    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    fog = nt.nodes.new("ShaderNodeValue")
    fog.name, fog.label = "CTRL_fog", "fog"
    fog.outputs[0].default_value = lk["world_fog"]
    below = math("MAXIMUM", math("MULTIPLY", sep.outputs["Z"], -1.4), 0.0)
    below = math("POWER", math("MINIMUM", below, 1.0), 1.5)
    lp = nt.nodes.new("ShaderNodeLightPath")
    k = math("ADD", 1.0, math("MULTIPLY", lp.outputs["Is Camera Ray"], -0.7))
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*hexcol(lk["void"]), 1.0)
    nt.links.new(math("MULTIPLY", math("MULTIPLY", below, k), 0.03 * lk["void_k"]), em.inputs["Strength"])
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (*lk["bg"], 1.0)
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(bg.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = (*lk["fog_col"], 1.0)
    pv.inputs["Anisotropy"].default_value = 0.5
    nt.links.new(fog.outputs[0], pv.inputs["Density"])
    nt.links.new(pv.outputs[0], out.inputs["Volume"])
    return w


def tune_eevee(sc=None):
    """Render settings the dungeon relies on (build_dungeon calls it; call again after setup_render)."""
    sc = sc or bpy.context.scene
    e = sc.eevee
    e.use_ssr = True
    e.ssr_max_roughness = 0.4
    e.ssr_thickness = 0.3
    e.ssr_border_fade = 0.06
    e.ssr_firefly_fac = 5.0
    e.use_ssr_halfres = True
    e.volumetric_end = max(e.volumetric_end, 140.0)
    e.volumetric_start = 0.1
    e.use_volumetric_shadows = True
    e.volumetric_shadow_samples = 12
    e.gtao_distance = 0.8
    e.gtao_factor = 1.0
    e.shadow_cube_size = "1024"
    e.light_threshold = 0.01
    e.use_soft_shadows = True
    return sc


# =================================================================== layout helpers
class Dungeon:
    """Handles of one built dungeon (see module docstring)."""

    def __init__(self, depth, seed):
        self.depth, self.seed = depth, seed
        self.objects, self.mats, self.ctrls, self.lights = [], {}, {}, {}
        self.marks = {}
        self.world = None
        self._slabs = {}
        self._sl = []
        self._edge = None

    def edge_radius(self, theta):
        return self._edge(theta)

    def floor_z(self, x, y):
        """Top of the floor (m) at world (x, y): 0 in the fighting area (r < 6.5 m); outside, the top of the
        (sunk / tilted) slab there, -0.07 in a gap, -9 beyond the platform edge."""
        r = math.hypot(x, y)
        if r < R_FIGHT:
            return 0.0
        best = None
        for sid in self._slabs.get((math.floor(x), math.floor(y)), ()):
            c, R, h = self._sl[sid]
            lp = R.T @ (np.array((x, y, c[2])) - c)
            if abs(lp[0]) <= h[0] and abs(lp[1]) <= h[1]:
                n = R[:, 2]
                top = c + n * h[2]
                z = top[2] - (n[0] * (x - top[0]) + n[1] * (y - top[1])) / n[2]
                best = z if best is None else max(best, z)
        if best is not None:
            return float(best)
        return -0.07 if r < self._edge(math.atan2(y, x)) else -9.0

    def key_ctrl(self, name, frame, value):
        for m in self.ctrls.get(name, []):
            M.key_ctrl(m, name, frame, value)


def _edge_fn(seed):
    vn = VN(seed * 7 + 3)

    def f(th):
        th = np.asarray(th, float)
        c, s = np.cos(th), np.sin(th)
        r = 10.9 + 1.25 * vn(c * 1.4, s * 1.4, 0.5) + 0.55 * vn(c * 4.0, s * 4.0, 2.5) + 0.2 * vn(c * 11, s * 11, 7.5)
        for ang, _, _ in CAUSEWAYS:
            d = np.angle(np.exp(1j * (th - math.radians(ang))))
            r = r + 1.4 * np.exp(-(d / 0.16) ** 2)
        return r if r.shape else float(r)
    return f


# =================================================================== builders
def _floor(D, rnd, vn, mat):
    """Staggered slab rows clipped by the irregular edge; flat inside R_FIGHT, sinking / tilting / missing
    toward the rim. Returns the slab object."""
    acc = Acc()
    D._sl = []
    y = -13.5
    row = 0
    while y < 13.5:
        hgt = rnd.uniform(0.95, 1.15)
        x = -13.5 + rnd.uniform(0, 1.2)
        while x < 13.5:
            w = rnd.uniform(1.0, 1.85)
            cx, cy = x + w / 2, y + hgt / 2
            x += w
            r = math.hypot(cx, cy)
            th = math.atan2(cy, cx)
            e = D._edge(th) - r
            if e < 0.45:
                continue
            out = C.clamp01((r - R_FIGHT) / 4.0)
            if r > R_FIGHT + 0.5 and rnd.random() < 0.05 + 0.4 * C.clamp01(1 - e / 1.6):
                continue
            hx, hy = w / 2 - 0.018 - rnd.uniform(0, 0.012), hgt / 2 - 0.018 - rnd.uniform(0, 0.012)
            hz = 0.16
            if r < R_FIGHT:
                Rm = rotm(0, 0, rnd.uniform(-0.004, 0.004))
                cz = -hz
            else:
                tilt = out * 0.06 + 0.12 * C.clamp01(1 - e / 1.4)
                Rm = rotm(rnd.uniform(-tilt, tilt), rnd.uniform(-tilt, tilt), rnd.uniform(-0.03, 0.03) * (1 + out))
                cz = -hz - out * rnd.uniform(0.0, 0.1) - 0.25 * C.clamp01(1 - e / 1.0) * rnd.random()
            jit = None if r < R_FIGHT else [(rnd.uniform(-0.03, 0.03), rnd.uniform(-0.03, 0.03), 0.0) for _ in range(8)]
            cbox(acc, (cx, cy, cz), (hx, hy, hz), R=Rm, ch=0.025, jit=jit, slab=rnd.random(), geo=1.0)
            sid = len(D._sl)
            D._sl.append((np.array((cx, cy, cz)), np.asarray(Rm), (hx, hy, hz)))
            for gx in range(math.floor(cx - hx - 0.1), math.floor(cx + hx + 0.1) + 1):
                for gy in range(math.floor(cy - hy - 0.1), math.floor(cy + hy + 0.1) + 1):
                    D._slabs.setdefault((gx, gy), []).append(sid)
        y += hgt
        row += 1
    return acc.build("DG_floor_slabs", mat, smooth=40.0, bake=True, mud_top=0.0)


def _rock_mass(acc, cx, cy, ztop, rimfn, depth, vn, NT=128, NR=22, spikes=1.0):
    """Floating-island underside: closed jagged cone under a rim, top cap at ztop."""
    th = np.linspace(0, 2 * math.pi, NT, endpoint=False)
    rim = rimfn(th)
    rows = []
    for i in range(NR + 1):
        u = i / NR
        rr = rim * (1.0 + 0.03 * (1 - u)) * (1 - u ** 1.6) ** 0.75
        z = ztop - 0.1 - depth * (u ** 0.85)
        x, y = cx + rr * np.cos(th), cy + rr * np.sin(th)
        n = vn.fbm(x * 0.35, y * 0.35, z * 0.35, 4)
        sp = np.maximum(vn(x * 0.9, y * 0.9, 3.3), 0.0) ** 2 * spikes * depth * 0.35 * min(1.0, u * 3)
        rr2 = rr * (1.0 + 0.12 * n * min(1.0, u * 4 + 0.15))
        z2 = z + 0.5 * n * min(1.0, u * 5) - sp
        if i == 0:
            z2 = np.full(NT, ztop)
            rr2 = rr
        rows.append(np.stack([cx + rr2 * np.cos(th), cy + rr2 * np.sin(th), z2], 1))
    P = np.concatenate(rows + [np.array([[cx, cy, ztop]])])
    F = []
    for i in range(NR):
        for j in range(NT):
            j2 = (j + 1) % NT
            F.append((i * NT + j, i * NT + j2, (i + 1) * NT + j2, (i + 1) * NT + j))
    ci = len(P) - 1
    F += [(ci, j, (j + 1) % NT) for j in range(NT)]
    return acc.add(P, F)


def _column(acc, x, y, radius, height, rnd, vn, base_z=0.0, tall=False):
    """Fluted column on a plinth with a moulded base; drums with joints; broken (jagged) top unless tall."""
    blk = rnd.random()
    cbox(acc, (x, y, base_z + 0.22), (radius * 1.45, radius * 1.45, 0.26), R=rotm(0, 0, rnd.uniform(-0.1, 0.1)),
         ch=0.04, jit=[(rnd.uniform(-0.02, 0.02), rnd.uniform(-0.02, 0.02), 0) for _ in range(8)], blk=blk)
    T = np.eye(4)
    T[:3, 3] = (x, y, 0)
    prof = [(0.48, 1.3), (0.56, 1.32), (0.62, 1.2), (0.7, 1.22), (0.78, 1.08), (0.84, 1.03)]
    lathe(acc, [base_z + z for z, _ in prof], lambda k, z, th: radius * prof[k][1] * (1 + 0.02 * vn(np.cos(th) * 3, np.sin(th) * 3, z + x)),
          N=64, T=T, blk=blk)
    z0 = base_z + 0.84
    top = base_z + height
    zs = [z0]
    drum = rnd.uniform(0.85, 1.05)
    zj = z0 + drum
    while zj < top - 0.15:
        zs += [zj - 0.035, zj, zj + 0.035]
        zj += drum * rnd.uniform(0.92, 1.08)
    zs.append(top)
    joints = [zs[i] for i in range(2, len(zs) - 1, 3)]
    flutes = 16
    seedz = rnd.uniform(0, 100)

    def rf(k, z, th):
        rr = radius * (1.0 - 0.035 * (0.5 + 0.5 * np.cos(flutes * th)) ** 2) * (1 - 0.012 * (z - z0) / max(height, 1))
        rr = rr * (1 + 0.025 * vn(np.cos(th) * 2.5 + seedz, np.sin(th) * 2.5, z * 0.7))
        chip = np.maximum(vn(np.cos(th) * 5 + seedz, np.sin(th) * 5, z * 2.2) - 0.45, 0) * 0.25 * radius
        for zj_ in joints:
            if abs(z - zj_) < 1e-6:
                rr = rr * 0.965
        return rr - chip

    jag = None
    if not tall:
        ph = rnd.uniform(0, 6)
        amp = rnd.uniform(0.35, 0.8)
        jag = lambda th: amp * (0.5 + 0.5 * vn(np.cos(th) * 1.6 + ph, np.sin(th) * 1.6, 1.0)) + 0.06 * np.abs(vn(np.cos(th) * 9, np.sin(th) * 9, 3.0))
    lathe(acc, zs, rf, N=96, T=T, jag=jag, blk=blk)


def _fallen_drums(acc, x, y, yaw, radius, rnd, vn, n=2):
    for i in range(n):
        L = rnd.uniform(0.8, 1.0)
        T = np.eye(4)
        T[:3, :3] = rotm(0, math.pi / 2 + rnd.uniform(-0.15, 0.15), yaw + rnd.uniform(-0.5, 0.5))
        d = Vector((math.cos(yaw), math.sin(yaw), 0)) * (i * 1.3 + 1.2)
        T[:3, 3] = (x + d.x, y + d.y, radius * 0.92)
        seedz = rnd.uniform(0, 50)
        lathe(acc, [-L / 2, -L / 2 + 0.03, L / 2 - 0.03, L / 2],
              lambda k, z, th: radius * (0.94 + 0.06 * (0 < k < 3)) * (1 - 0.03 * (0.5 + 0.5 * np.cos(16 * th)) ** 2)
              * (1 + 0.04 * vn(np.cos(th) * 3 + seedz, np.sin(th) * 3, z)), N=64, T=T, blk=rnd.random())


def _rubble(acc, D, center, radius, count, rnd, size=(0.05, 0.4), avoid=R_FIGHT - 0.3, bias=2.0):
    cx, cy = center
    for _ in range(count):
        a = rnd.uniform(0, 2 * math.pi)
        rr = radius * rnd.random() ** 0.6
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        if math.hypot(x, y) < avoid:
            continue
        s = size[0] + (size[1] - size[0]) * rnd.random() ** bias
        z = D.floor_z(x, y)
        if z < -1:
            continue
        h = (s * rnd.uniform(0.6, 1.0), s * rnd.uniform(0.45, 0.9), s * rnd.uniform(0.3, 0.6))
        jit = [tuple(rnd.uniform(-0.3, 0.3) * hh for hh in h) for _ in range(8)]
        cbox(acc, (x, y, z + h[2] * 0.55), h, R=rotm(rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), rnd.uniform(0, 6.3)),
             ch=0.3 * min(h), jit=jit, blk=rnd.random())


def _wall_arc(acc, D, th0, th1, r, hmax, rnd, vn, thick=0.85, course=0.46):
    """Ruined ashlar wall along an arc: staggered courses, broken top profile, a few fallen blocks."""
    a0, a1 = math.radians(th0), math.radians(th1)
    arc = (a1 - a0) * r
    nc = max(1, int(hmax / course + 0.999))
    ph = rnd.uniform(0, 50)
    for c in range(nc):
        s = rnd.uniform(0, 0.5) if c % 2 else 0.0
        z0 = -0.12 + c * course
        while s < arc:
            L = rnd.uniform(0.55, 1.15)
            sm = s + L / 2
            s += L
            u = sm / arc
            prof = hmax * (0.25 + 0.75 * C.clamp01(0.55 + 0.9 * vn(u * 3.0 + ph, 0.3, 1.0))) * (0.4 + 0.6 * math.sin(math.pi * C.clamp01(u * 1.15 - 0.07)))
            if z0 + course * 0.5 > prof:
                continue
            a = a0 + sm / r
            rr = min(r, D._edge(a) - 0.9)
            x, y = rr * math.cos(a), rr * math.sin(a)
            topc = z0 + course > prof
            drop = [rnd.uniform(0, 0.18) if topc else rnd.uniform(0, 0.02) for _ in range(4)]
            jit = [(rnd.uniform(-0.02, 0.02), rnd.uniform(-0.02, 0.02), rnd.uniform(-0.01, 0.01)) for _ in range(8)]
            tilt = 0.06 if topc else 0.012
            Rm = rotm(rnd.uniform(-tilt, tilt), rnd.uniform(-tilt, tilt), a + math.pi / 2 + rnd.uniform(-0.03, 0.03))
            cbox(acc, (x, y, z0 + course / 2), (L / 2 - 0.012, thick / 2 * rnd.uniform(0.92, 1.0), course / 2 - 0.01),
                 R=Rm, ch=0.035, jit=jit, top_drop=drop, blk=rnd.random())
    # fallen blocks at the inner foot
    for _ in range(int(arc / 2.2)):
        a = rnd.uniform(a0, a1)
        rr = min(r, D._edge(a) - 0.9) - rnd.uniform(0.8, 1.8)
        x, y = rr * math.cos(a), rr * math.sin(a)
        L = rnd.uniform(0.5, 1.0)
        cbox(acc, (x, y, D.floor_z(x, y) + course * 0.42), (L / 2, thick / 2 * 0.9, course / 2 - 0.01),
             R=rotm(rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), rnd.uniform(0, 6.3)), ch=0.04,
             jit=[(rnd.uniform(-0.04, 0.04), rnd.uniform(-0.04, 0.04), rnd.uniform(-0.03, 0.03)) for _ in range(8)],
             top_drop=[rnd.uniform(0, 0.12) for _ in range(4)], blk=rnd.random())


def _hexa(acc, P8, **attrs):
    """General hexahedron from 8 corners ordered like _BOX_KEYS (x-major, then y, then z)."""
    F = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return acc.add(P8, F, **attrs)


def _arch(acc, D, cx, cy, yaw, rnd, vn, span=3.8, pier=1.25, depth=1.35, spring=4.0, ring=0.8, broken=0.0):
    """Ashlar arch with piers, voussoir ring, keystone and broken spandrel courses above.
    Local frame: x across the opening, y through it (axis), z up. broken > 0 removes the +x side progressively."""
    Rz = rotm(0, 0, yaw)
    org = np.array((cx, cy, 0.0))

    def W(p):
        return org + Rz @ np.asarray(p, float)

    course = 0.5
    for side in (-1, 1):
        px = side * (span / 2 + pier / 2)
        hmax = spring if not (broken and side > 0) else spring * (1 - broken) + 0.6
        z = -0.1
        c = 0
        while z < hmax - 0.05:
            h = min(course, hmax - z)
            for k, (yy, dd) in enumerate(((-depth / 4, depth / 2), (depth / 4, depth / 2)) if c % 2 else ((0.0, depth),)):
                drop = [rnd.uniform(0, 0.15) for _ in range(4)] if (z + h >= hmax - 0.05 and broken and side > 0) else None
                cbox(acc, W((px + rnd.uniform(-0.02, 0.02), yy, z + h / 2)), (pier / 2 - 0.012, dd / 2 - 0.012, h / 2 - 0.01),
                     R=Rz @ rotm(0, 0, rnd.uniform(-0.015, 0.015)), ch=0.04,
                     jit=[(rnd.uniform(-0.015, 0.015), rnd.uniform(-0.015, 0.015), 0) for _ in range(8)], top_drop=drop,
                     blk=rnd.random())
            z += h
            c += 1
        if not (broken and side > 0):
            cbox(acc, W((px - side * 0.06, 0, spring + 0.13)), (pier / 2 + 0.12, depth / 2 + 0.1, 0.14), R=Rz, ch=0.04,
                 blk=rnd.random())
    # voussoirs
    n = 15
    r0, r1 = span / 2, span / 2 + ring
    zc = spring + 0.26
    for i in range(n):
        a0 = math.pi * i / n + 0.006
        a1 = math.pi * (i + 1) / n - 0.006
        am = (a0 + a1) / 2
        if broken and -math.cos(am) > 1 - 2 * broken:
            continue
        kr = r1 + (0.18 if i == n // 2 else 0.0)
        P = []
        for xs in (0, 1):
            for ys in (-1, 1):
                for zs in (0, 1):
                    a = a1 if xs else a0
                    rr = kr if zs else r0
                    P.append((math.cos(a) * rr, ys * depth / 2 * (1.03 if i == n // 2 else 1.0), zc + math.sin(a) * rr))
        P = np.array(P)
        P[:, 0] = -P[:, 0]
        jit = np.array([(rnd.uniform(-0.01, 0.01), rnd.uniform(-0.01, 0.01), rnd.uniform(-0.01, 0.01)) for _ in range(8)])
        _hexa(acc, (P + jit) @ Rz.T + org, blk=rnd.random())
    # spandrel courses above the springing, cut by the ring, broken top profile
    top = zc + r1 + 0.9
    z = spring + 0.27
    ph = rnd.uniform(0, 20)
    xmax = span / 2 + pier
    c = 0
    while z < top:
        x = -xmax + (rnd.uniform(0.1, 0.4) if c % 2 else 0.0)
        while x < xmax:
            L = rnd.uniform(0.5, 1.0)
            xm = min(x + L / 2, xmax - 0.05)
            x += L
            prof = top - 1.6 * max(0.0, vn(xm * 0.6 + ph, 0.5, 0.0)) - (2.5 * broken * (xm + xmax) / (2 * xmax) if broken else 0)
            if z + course / 2 > prof:
                continue
            if math.hypot(xm, z + course / 2 - zc) < r1 + 0.22:
                continue
            if broken and xm > 0 and z < spring + 1.0:
                continue
            cbox(acc, W((xm, 0, z + course / 2)), (L / 2 - 0.012, depth / 2 - 0.02, course / 2 - 0.01),
                 R=Rz @ rotm(0, 0, rnd.uniform(-0.01, 0.01)), ch=0.035,
                 top_drop=[rnd.uniform(0, 0.12) for _ in range(4)] if z + course > prof - 0.3 else None,
                 jit=[(rnd.uniform(-0.015, 0.015), rnd.uniform(-0.015, 0.015), 0) for _ in range(8)], blk=rnd.random())
        z += course
        c += 1


_LINK = None


def _link_template(a=0.04, R0=0.022, rw=0.0085, M_=16, N=6):
    """Chain link (stadium torus) centred at the origin, long axis Z, flat in XZ. Returns verts, faces."""
    phis = (np.arange(M_) + 0.5) / M_ * 2 * math.pi
    cl = np.stack([R0 * np.cos(phis), np.zeros(M_), R0 * np.sin(phis) + a * np.sign(np.sin(phis))], 1)
    V = []
    for i in range(M_):
        t = cl[(i + 1) % M_] - cl[i - 1]
        t /= np.linalg.norm(t)
        nrm = np.array((0.0, 1.0, 0.0))
        bn = np.cross(t, nrm)
        for j in range(N):
            ps = 2 * math.pi * j / N
            V.append(cl[i] + rw * (math.cos(ps) * bn + math.sin(ps) * nrm))
    F = []
    for i in range(M_):
        i2 = (i + 1) % M_
        for j in range(N):
            j2 = (j + 1) % N
            F.append((i * N + j, i * N + j2, i2 * N + j2, i2 * N + j))
    return np.array(V), F, 2 * (a + R0 - rw)


def chain(name, pts, mat, scale=1.0, origin=None, rnd=None):
    """Chain of interlocking links along a polyline (pts). One object; origin at `origin` (default pts[0])."""
    global _LINK
    if _LINK is None:
        _LINK = _link_template()
    LV, LF, pitch = _LINK
    LV = LV * scale
    pitch *= scale
    pts = [Vector(p) for p in pts]
    org = Vector(origin) if origin is not None else pts[0]
    seg = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    lens = [(b - a).length for a, b in seg]
    total = sum(lens)
    acc = Acc()
    s = pitch / 2
    k = 0
    rnd = rnd or random.Random(len(pts))
    while s < total - pitch / 2:
        i, acc_l = 0, 0.0
        while i < len(seg) - 1 and acc_l + lens[i] < s:
            acc_l += lens[i]
            i += 1
        a, b = seg[i]
        t = (b - a).normalized()
        p = a + t * (s - acc_l)
        up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        x = t.cross(up).normalized()
        y = t.cross(x)
        if k % 2:
            x, y = y, -x
        tw = rnd.uniform(-0.12, 0.12)
        x, y = x * math.cos(tw) + y * math.sin(tw), y * math.cos(tw) - x * math.sin(tw)
        Rm = np.array([[x.x, y.x, t.x], [x.y, y.y, t.y], [x.z, y.z, t.z]])
        acc.add(LV @ Rm.T + np.array(p - org), LF)
        s += pitch
        k += 1
    ob = acc.build(name, mat, smooth=0, recalc=False)
    for poly in ob.data.polygons:
        poly.use_smooth = True
    ob.location = org
    return ob


def sway(ob, amp_deg, speed, phase):
    """Pendulum sway of a hanging object around its origin: drivers on the frame (pure function)."""
    for i, (a, sp, ph) in enumerate(((amp_deg, speed, phase), (amp_deg * 0.6, speed * 1.37, phase + 1.9))):
        fc = ob.driver_add("rotation_euler", i)
        fc.driver.type = "SCRIPTED"
        fc.driver.expression = "%.5f*sin(frame*%.4f+%.3f)" % (math.radians(a), sp, ph)


def bob(ob, amp, speed, phase, z0):
    fc = ob.driver_add("location", 2)
    fc.driver.type = "SCRIPTED"
    fc.driver.expression = "%.4f+%.4f*sin(frame*%.4f+%.3f)" % (z0, amp, speed, phase)


def brazier(D, name, x, y, z, rnd, depth, scale=1.0):
    """Tripod iron brazier (bowl rim at z + 1.1): iron, coals and flame objects; returns (objs, flame_centre)."""
    lk = LOOK[depth]
    acc = Acc()
    T = np.eye(4)
    T[:3, 3] = (0, 0, 0)
    prof = [(0.80, 0.07), (0.84, 0.2), (0.92, 0.31), (1.02, 0.37), (1.08, 0.395), (1.11, 0.41), (1.12, 0.395),
            (1.09, 0.36), (1.02, 0.33), (0.96, 0.27)]
    lathe(acc, [p[0] for p in prof], lambda k, zz, th: prof[k][1] * (1 + 0.01 * np.sin(th * 7 + k)), N=48, T=T)
    for i in range(10):
        a = 2 * math.pi * i / 10 + 0.2
        p0 = Vector((0.4 * math.cos(a), 0.4 * math.sin(a), 1.1))
        tube_poly(acc, [p0, p0 + Vector((0.05 * math.cos(a), 0.05 * math.sin(a), 0.16))],
                  lambda t: 0.018 * (1 - t) + 0.001, N=6)
    tube_poly(acc, [(0, 0, 0.82), (0, 0, 0.5)], 0.045, N=12)
    lathe(acc, [0.5, 0.56, 0.6], lambda k, zz, th: (0.07, 0.085, 0.06)[k], N=24)
    for i in range(3):
        a = 2 * math.pi * i / 3 + 0.4
        c, s_ = math.cos(a), math.sin(a)
        pts = [(0.05 * c, 0.05 * s_, 0.55), (0.2 * c, 0.2 * s_, 0.45), (0.33 * c, 0.33 * s_, 0.22),
               (0.4 * c, 0.4 * s_, 0.06), (0.47 * c, 0.47 * s_, 0.02)]
        tube_poly(acc, pts, 0.026, N=8)
        tube_poly(acc, [(0.08 * c, 0.08 * s_, 0.92), (0.3 * c, 0.3 * s_, 0.6), (0.2 * c, 0.2 * s_, 0.45)], 0.014, N=6)
    iron = acc.build(name + "_iron", D.mats["iron"], smooth=45.0, bake=True)
    # coals
    vn = VN(rnd.randrange(1 << 20))
    V, F = polar_grid(0, 0, lambda th: np.full(th.shape, 0.335), lambda u, th, xx, yy: 1.02 + 0.03 * (1 - u ** 2)
                      + 0.025 * vn(np.asarray(xx) * 14, np.asarray(yy) * 14, 0.0), NR=6, NT=40)
    ca = Acc()
    ca.add(V, F)
    coals = ca.build(name + "_coals", D.mats["coals"], smooth=0, recalc=False)
    # flame tongues
    fa = Acc()
    for i in range(6):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0.0, 0.17)
        h = rnd.uniform(0.38, 0.72) * (1.0 if lk["brazier"] > 0.5 else 0.6)
        ph = rnd.uniform(0, 6)
        pts = [(rr * math.cos(a) + 0.04 * math.sin(k * 1.3 + ph) * k / 6, rr * math.sin(a) + 0.04 * math.cos(k * 1.1 + ph) * k / 6,
                1.0 + h * k / 6) for k in range(7)]
        tube_poly(fa, pts, lambda t: 0.11 * (1 - t) ** 0.8 + 0.006, N=10, cap=False)
    flame = fa.build(name + "_flame", D.mats["flame"], smooth=0, recalc=False)
    for p in flame.data.polygons:
        p.use_smooth = True
    for ob in (iron, coals, flame):
        ob.location = (x, y, z)
        ob.scale = (scale, scale, scale)
    flame.visible_shadow = False
    return [iron, coals, flame], (x, y, z + 1.25 * scale)


def _far_glow(D, name, centre, color, radius=2.5, emit=0.08):
    m = mat_fog(name + "_mat", density=0.0, color=(0.8, 0.6, 0.5), emit_color=color, emit=emit,
                radial=(centre, radius), contrast=(0.3, 0.7, 0.6, 1.2), scale=0.6)
    lo = tuple(c - radius for c in centre)
    hi = tuple(c + radius for c in centre)
    return box_object(name, lo, hi, m)


def build_dungeon(depth="struggle", seed=0):
    """Build the Fallen World set (see module docstring) for one depth variant. Returns a Dungeon handle."""
    assert depth in DEPTHS, depth
    D = Dungeon(depth, seed)
    lk = LOOK[depth]
    rnd = random.Random(seed * 7919 + 17)
    vn = VN(seed + 11)
    D._edge = _edge_fn(seed)
    D.world = void_world(depth)
    tune_eevee()
    D.mats.update(floor=mat_floor(depth), magma=mat_magma(depth), masonry=mat_masonry(depth), rock=mat_rock(depth),
                  iron=mat_iron(), flame=mat_flame(depth), coals=mat_coals(depth))
    O = D.objects
    # ---- main platform
    O.append(_floor(D, rnd, vn, D.mats["floor"]))
    V, F = polar_grid(0, 0, lambda th: D._edge(th) - 0.15, lambda u, th, x, y: -0.075, NR=8, NT=128)
    ma = Acc()
    ma.add(V, F)
    O.append(ma.build("DG_magma", D.mats["magma"], smooth=0, recalc=False))
    ra = Acc()
    _rock_mass(ra, 0, 0, -0.2, lambda th: D._edge(th) + 0.1, 9.5, vn)
    # ---- causeways + far platforms
    masonry = Acc()
    cw = Acc()
    D.marks["causeways"] = []
    for ci, (ang, dist, zend) in enumerate(CAUSEWAYS):
        a = math.radians(ang)
        d = np.array((math.cos(a), math.sin(a), 0.0))
        sv = np.array((-d[1], d[0], 0.0))
        s0 = D._edge(a) - 0.6
        s1 = dist - 6.5
        gaps = []
        gs = s0 + rnd.uniform(3.0, 6.0)
        while gs < s1 - 3:
            gl = rnd.uniform(1.4, 3.2)
            gaps.append((gs, gs + gl))
            gs += gl + rnd.uniform(4.0, 9.0)
        s = s0
        while s < s1:
            L = rnd.uniform(0.9, 1.3)
            sm = s + L / 2
            s += L
            if any(g0 < sm < g1 for g0, g1 in gaps):
                continue
            u = (sm - s0) / (s1 - s0)
            zc = zend * C.smooth(u)
            near_gap = min([min(abs(sm - g0), abs(sm - g1)) for g0, g1 in gaps] + [9.0])
            for k in range(3):
                off = (k - 1) * 1.0 + rnd.uniform(-0.03, 0.03)
                if near_gap < 1.0 and rnd.random() < 0.45:
                    continue
                tilt = 0.02 + 0.18 * (near_gap < 1.0)
                c = d * sm + sv * off + np.array((0, 0, zc - 0.16 - (0.1 * rnd.random() if near_gap < 1.0 else 0)))
                cbox(cw, c, (L / 2 - 0.02, 0.48, 0.16), R=rotm(rnd.uniform(-tilt, tilt), rnd.uniform(-tilt, tilt), a + rnd.uniform(-0.03, 0.03)),
                     ch=0.025, jit=[(rnd.uniform(-0.03, 0.03), rnd.uniform(-0.03, 0.03), 0) for _ in range(8)], slab=rnd.random(), geo=1.0)
            # rock beam under the deck
            if rnd.random() < 0.9:
                c = d * sm + np.array((0, 0, zc - 0.32 - 0.5))
                cbox(ra, c, (L / 2 + 0.05, 1.45, 0.5), R=rotm(0, 0, a), ch=0.12,
                     jit=[(rnd.uniform(-0.1, 0.1), rnd.uniform(-0.15, 0.15), rnd.uniform(-0.25, 0.1)) for _ in range(8)])
                if rnd.random() < 0.35:
                    cbox(ra, c - np.array((0, 0, 0.9)), (L / 2, 0.8, 0.5), R=rotm(0, 0, a + 0.3), ch=0.12,
                         jit=[(rnd.uniform(-0.1, 0.1), rnd.uniform(-0.2, 0.2), rnd.uniform(-0.4, 0.0)) for _ in range(8)])
            # parapet stubs
            if rnd.random() < 0.28:
                side = rnd.choice((-1, 1))
                c = d * sm + sv * side * 1.62 + np.array((0, 0, zc + 0.25))
                cbox(masonry, c, (L / 2 - 0.05, 0.2, 0.28 + rnd.uniform(0, 0.25)), R=rotm(0, 0, a), ch=0.04,
                     top_drop=[rnd.uniform(0, 0.15) for _ in range(4)], blk=rnd.random())
        cen = d * dist + np.array((0, 0, zend))
        D.marks["causeways"].append((tuple(d[:2] * s0), tuple(cen[:2])))
        # far platform
        isl_r = 6.0 + rnd.uniform(-0.5, 1.5)
        ph = rnd.uniform(0, 30)
        rimf = (lambda R_, ph_: (lambda th: R_ * (1 + 0.16 * VN(int(ph_ * 100)).fbm(np.cos(th) * 1.5 + ph_, np.sin(th) * 1.5, 0.0, 3))))(isl_r, ph)
        _rock_mass(ra, cen[0], cen[1], cen[2] - 0.2, rimf, isl_r * 1.1, vn, NT=64, NR=14)
        V, F = polar_grid(cen[0], cen[1], rimf, lambda u, th, x, y: cen[2] - 0.02, NR=4, NT=64)
        cw.add(V, F, slab=0.5, geo=0.0)
        for k in range(rnd.randint(1, 3)):
            aa = rnd.uniform(0, 2 * math.pi)
            px, py = cen[0] + isl_r * 0.6 * math.cos(aa), cen[1] + isl_r * 0.6 * math.sin(aa)
            _column(masonry, px, py, 0.6, TALL if rnd.random() < 0.4 else rnd.uniform(2.0, 6.0), rnd, vn, base_z=cen[2],
                    tall=False)
        objs, fc = brazier(D, "DG_far_brazier%d" % ci, cen[0] + 1.5, cen[1] - 1.0, cen[2], rnd, depth)
        O.extend(objs)
        O.append(_far_glow(D, "DG_far_glow%d" % ci, fc, lk["seam"] if depth != "legend" else "#FF9A2A", 3.0,
                           0.05 * lk["brazier"]))
    for ii, (x, y, z, R_) in enumerate(ISLANDS):
        ph = rnd.uniform(0, 30)
        rimf = (lambda R__, ph_: (lambda th: R__ * (1 + 0.18 * VN(int(ph_ * 100)).fbm(np.cos(th) * 1.5 + ph_, np.sin(th) * 1.5, 0.0, 3))))(R_, ph)
        _rock_mass(ra, x, y, z - 0.2, rimf, R_ * 1.2, vn, NT=64, NR=14)
        V, F = polar_grid(x, y, rimf, lambda u, th, xx, yy: z - 0.02, NR=4, NT=64)
        cw.add(V, F, slab=0.5, geo=0.0)
        for k in range(rnd.randint(1, 3)):
            aa = rnd.uniform(0, 2 * math.pi)
            px, py = x + R_ * 0.55 * math.cos(aa), y + R_ * 0.55 * math.sin(aa)
            _column(masonry, px, py, 0.65, TALL if rnd.random() < 0.35 else rnd.uniform(2.0, 7.0), rnd, vn, base_z=z)
        if ii % 2 == 0:
            objs, fc = brazier(D, "DG_isl_brazier%d" % ii, x - 1.0, y + 0.5, z, rnd, depth, scale=1.3)
            O.extend(objs)
            O.append(_far_glow(D, "DG_isl_glow%d" % ii, fc, lk["seam"], 3.5, 0.04 * lk["brazier"]))
    O.append(cw.build("DG_causeways", D.mats["floor"], smooth=40.0, bake=True))
    # ---- arches, columns, walls
    _arch(masonry, D, 0.0, 10.1, 0.0, rnd, vn)
    a = math.radians(250)
    _arch(masonry, D, 10.3 * math.cos(a), 10.3 * math.sin(a), a - math.pi / 2, rnd, vn, span=3.4, spring=3.4, broken=0.55)
    D.marks["arch"] = (0.0, 10.1, 0.0)
    rub = Acc()
    for ang, r, h, rad in COLUMNS:
        a = math.radians(ang)
        x, y = r * math.cos(a), r * math.sin(a)
        _column(masonry, x, y, rad, TALL if h is None else h, rnd, vn, tall=h is None)
        if h is not None:
            _rubble(rub, D, (x, y), 2.4, 45, rnd, size=(0.05, 0.45))
            if h < 3.0:
                _fallen_drums(masonry, x, y, a + rnd.uniform(-0.8, 0.8), rad, rnd, vn, n=2)
    for th0, th1, r, h in WALLS:
        _wall_arc(masonry, D, th0, th1, r, h, rnd, vn)
        am = math.radians((th0 + th1) / 2)
        _rubble(rub, D, ((r - 1.0) * math.cos(am), (r - 1.0) * math.sin(am)), 3.5, 40, rnd, size=(0.05, 0.35))
    # fine debris across the outer floor + a few pebbles in the fighting area
    for _ in range(260):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(R_FIGHT - 0.5, 11.5)
        _rubble(rub, D, (rr * math.cos(a), rr * math.sin(a)), 0.01, 1, rnd, size=(0.025, 0.16), avoid=0.0, bias=2.5)
    for _ in range(70):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(1.0, R_FIGHT)
        _rubble(rub, D, (rr * math.cos(a), rr * math.sin(a)), 0.01, 1, rnd, size=(0.012, 0.04), avoid=0.0, bias=1.5)
    O.append(masonry.build("DG_masonry", D.mats["masonry"], smooth=35.0, bake=True, mud_top=0.6))
    O.append(rub.build("DG_rubble", D.mats["masonry"], smooth=35.0, bake=True, mud_top=0.3))
    # floating debris in the void (bobbing)
    for i in range(34):
        a = rnd.uniform(0, 2 * math.pi)
        rr = D._edge(a) + rnd.uniform(1.0, 9.0)
        z = rnd.uniform(-7.0, -0.6) if rnd.random() < 0.8 else rnd.uniform(1.0, 6.0)
        s = rnd.uniform(0.25, 1.4) * (1.0 if rr < D._edge(a) + 5 else 1.6)
        acc = Acc()
        h = (s, s * rnd.uniform(0.5, 0.9), s * rnd.uniform(0.35, 0.7))
        cbox(acc, (0, 0, 0), h, R=rotm(rnd.uniform(0, 6), rnd.uniform(0, 6), rnd.uniform(0, 6)), ch=0.25 * min(h),
             jit=[tuple(rnd.uniform(-0.35, 0.35) * hh for hh in h) for _ in range(8)])
        ob = acc.build("DG_debris%02d" % i, D.mats["rock"], smooth=30.0)
        ob.location = (rr * math.cos(a), rr * math.sin(a), z)
        bob(ob, rnd.uniform(0.04, 0.14), rnd.uniform(0.015, 0.035), rnd.uniform(0, 6.3), z)
        O.append(ob)
    O.append(ra.build("DG_rock", D.mats["rock"], smooth=50.0))
    # ---- braziers
    D.marks["braziers"] = []
    for i, ang in enumerate(BRAZIER_ANG):
        a = math.radians(ang)
        x, y = BRAZIER_R * math.cos(a), BRAZIER_R * math.sin(a)
        objs, fc = brazier(D, "DG_brazier%d" % i, x, y, D.floor_z(x, y), rnd, depth)
        O.extend(objs)
        D.marks["braziers"].append(fc)
    # ---- chains
    for i, (x, y, zb) in enumerate(CHAINS):
        ch = chain("DG_chain%02d" % i, [(x, y, 16.0), (x, y, zb)], D.mats["iron"], scale=1.0, rnd=rnd)
        sway(ch, rnd.uniform(0.15, 0.35), rnd.uniform(0.03, 0.05), rnd.uniform(0, 6.3))
        O.append(ch)
        if i % 3 == 0:
            hk = Acc()
            tube_poly(hk, [(x, y, zb), (x, y, zb - 0.25), (x + 0.08, y, zb - 0.38), (x + 0.16, y, zb - 0.3),
                           (x + 0.15, y, zb - 0.2)], lambda t: 0.022 * (1 - 0.6 * t), N=8)
            hob = hk.build("DG_hook%02d" % i, D.mats["iron"], smooth=60.0)
            C.parent_keep(hob, ch)
            O.append(hob)
    for i, (x, y, zb) in enumerate(LONG_CHAINS):
        ch = chain("DG_chain_long%02d" % i, [(x, y, 18.0), (x, y, zb)], D.mats["iron"], scale=1.7, rnd=rnd)
        sway(ch, 0.12, 0.025, i * 1.7)
        O.append(ch)
    tallc = {ang: (r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang))) for ang, r, h, _ in COLUMNS}
    for i, (a0, z0, a1, z1, sag) in enumerate(((62, 8.6, 116, 9.2, 2.2), (195, 7.6, 226, 5.9, 0.9),
                                                (320, 7.2, 30, 4.1, 1.6))):
        p0 = Vector((*tallc[a0], z0))
        p1 = Vector((*tallc[a1], z1))
        pts = [p0.lerp(p1, t) - Vector((0, 0, sag * 4 * t * (1 - t))) for t in np.linspace(0, 1, 24)]
        O.append(chain("DG_chain_drape%d" % i, pts, D.mats["iron"], scale=1.2, rnd=rnd))
    # ---- fog
    D.mats["fog_ground"] = mat_fog("DG_fog_ground_" + depth, density=lk["fog"], height=0.9, color=lk["fog_col"],
                                   anisotropy=0.35, scale=0.12)
    O.append(box_object("DG_fog_ground", (-20, -20, -0.5), (20, 20, 4.0), D.mats["fog_ground"]))
    D.mats["fog_void"] = mat_fog("DG_fog_void_" + depth, density=0.09, color=lk["fog_col"], anisotropy=0.3,
                                 scale=0.03, layer=(-10.0, 3.5), emit_color=lk["void"], emit=0.012 * lk["void_k"],
                                 contrast=(0.3, 0.7, 0.3, 1.4), wind=(0.25, 0.1, 0.0))
    O.append(box_object("DG_fog_void", (-110, -110, -24), (110, 110, -2.0), D.mats["fog_void"]))
    # ---- marks
    D.marks.update(center=(0.0, 0.0, 0.0), warrior=(0.0, 0.0, 0.0),
                   wide=((0.6, -7.6, 1.55), (0.0, 2.0, 2.3), 35),
                   high=((0.0, -6.5, 7.0), (0.0, 0.6, 0.0), 24),
                   low=((0.5, -2.6, 0.35), (0.0, 1.0, 1.1), 24),
                   mid=((0.7, -4.2, 1.5), (0.0, 0.0, 1.35), 50),
                   reverse=((-0.5, 7.4, 1.6), (0.0, -2.0, 1.6), 35),
                   side=((7.2, -1.8, 1.4), (-1.0, 0.6, 1.5), 35),
                   up=((0.4, -3.0, 0.4), (0.0, 2.0, 4.5), 24))
    # ---- ctrl index
    for m in D.mats.values():
        if m is not None and m.node_tree:
            for n in m.node_tree.nodes:
                if n.name.startswith("CTRL_"):
                    D.ctrls.setdefault(n.name[5:], []).append(m)
    return D


# =================================================================== lights
def _L(kind, name, loc, color, energy, target=None, size=0.3, shadow=False, spot=45.0, blend=0.3, volume=1.0,
       specular=1.0, diffuse=1.0, cutoff=None):
    ob = C.light(kind, "DG_" + name, tuple(loc), color=color, energy=energy, size=size, target=target,
                 shadow=shadow, spot_size=math.radians(spot), blend=blend, volume=volume, specular=specular)
    ob.data.diffuse_factor = diffuse
    if cutoff:
        ob.data.use_custom_distance = True
        ob.data.cutoff_distance = cutoff
    if shadow and kind != "SUN":
        ob.data.shadow_buffer_bias = 0.02
        ob.data.shadow_buffer_clip_start = 0.3
    return ob


def flicker(light, base, amp=0.12, speed=1.0, phase=0.0):
    """Energy driver: pure function of the frame (simple expression)."""
    fc = light.data.driver_add("energy")
    fc.driver.type = "SCRIPTED"
    fc.driver.expression = ("%.4f*(1+%.4f*sin(frame*%.4f+%.3f)+%.4f*sin(frame*%.4f+%.3f)+%.4f*sin(frame*%.4f+%.3f))"
                            % (base, amp, 0.71 * speed, phase, amp * 0.6, 1.93 * speed, phase * 2.1 + 1.3,
                               amp * 0.4, 4.37 * speed, phase * 0.7 + 0.4))
    return light


def lights_dungeon(depth, dungeon=None, subject=(0, 0, 0), cam=(0, -6, 1.6), follow=None):
    """Light rig for a subject standing at `subject` seen from `cam` (see module docstring).
    Shadow casters: 'key' and 'top' only. follow: parent the subject lights (key, top, rims, back, fill,
    bounce) to this object keeping their world transform. Returns {name: light object}."""
    lk = LOOK[depth]
    S, Cm = Vector(subject), Vector(cam)
    d = S - Cm
    d.z = 0
    if d.length < 1e-4:
        d = Vector((0, 1, 0))
    d.normalize()
    side = Vector((-d.y, d.x, 0.0))          # camera-left
    L = {}
    L["key"] = _L("SPOT", "key", S - d * 4.2 + side * 4.4 + Vector((0, 0, 6.8)), lk["key"], lk["key_e"],
                  target=S + Vector((0, 0, 1.0)), size=0.7, spot=36.0, blend=0.55, shadow=True, volume=0.35)
    L["top"] = _L("SPOT", "top", S + d * 1.2 - side * 0.8 + Vector((0, 0, 15.0)), lk["top"], lk["top_e"],
                  target=S + Vector((0, 0, 0.2)), size=0.45, spot=17.0, blend=0.45, shadow=True, volume=1.0,
                  specular=0.6)
    for nm, off, z, e in (("rimL", 0.55, 1.38, 1.0), ("rimR", -0.55, 1.38, 1.0), ("rimH", 0.15, 1.95, 0.5)):
        ob = _L("POINT", nm, S + d * 0.45 + side * off + Vector((0, 0, z)), EMBER, 15.0 * e * lk["rim_k"], size=0.1,
                volume=0.0, specular=1.0, cutoff=1.15)
        L[nm] = ob
    L["back"] = _L("SPOT", "back", S + d * 3.4 - side * 1.3 + Vector((0, 0, 2.7)), lk["back"], lk["back_e"],
                   target=S + Vector((0, 0, 1.3)), size=0.5, spot=30.0, blend=0.5, volume=0.25, diffuse=0.25,
                   specular=1.3)
    fl = _L("AREA", "fill", Cm.lerp(S, 0.35) + side * -2.2 + Vector((0, 0, 0.8)), lk["fill"], lk["fill_e"],
            target=S + Vector((0, 0, 1.2)), size=3.0, volume=0.0, specular=0.3)
    L["fill"] = fl
    bo = _L("AREA", "bounce", S + Vector((0, 0, 0.04)), lk["seam"], 18.0 * lk["seam_k"], size=3.0, volume=0.0,
            specular=0.2)
    bo.rotation_euler = (math.pi, 0, 0)
    L["bounce"] = bo
    su = _L("AREA", "seam_up", Vector((S.x, S.y, 0.03)), lk["seam"], 110.0 * lk["seam_k"], size=16.0, volume=0.15,
            specular=0.1)
    su.rotation_euler = (math.pi, 0, 0)
    L["seam_up"] = su
    braz = (dungeon.marks.get("braziers") if dungeon is not None else None) or \
        [(BRAZIER_R * math.cos(math.radians(a)), BRAZIER_R * math.sin(math.radians(a)), 1.25) for a in BRAZIER_ANG]
    for i, p in enumerate(braz):
        e = 70.0 * lk["brazier"]
        L["brazier%d" % i] = flicker(_L("POINT", "brazier%d" % i, Vector(p) + Vector((0, 0, 0.25)), "#FF7A2E", e,
                                        size=0.25, volume=0.6, specular=0.6), e, 0.14, 1.3, i * 1.7)
    for i, (x, y) in enumerate(((14.0, 9.0), (-15.0, 6.0), (2.0, -16.0))):
        L["void%d" % i] = _L("POINT", "void%d" % i, (x, y, -20.0), lk["void"], 2600.0 * lk["void_k"], size=6.0,
                             volume=0.35, specular=0.1)
    if follow is not None:
        for nm in ("key", "top", "rimL", "rimR", "rimH", "back", "fill", "bounce"):
            C.parent_keep(L[nm], follow)
    if dungeon is not None:
        dungeon.lights = L
    return L
