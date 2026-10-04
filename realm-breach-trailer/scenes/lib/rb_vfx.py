"""REALM BREACH — VFX library (embers, ash, dust, sparks, shockwaves, debris, smoke,
Q fireball, E lightning, R god attack, ember trails, heaven petals).

HOW IT WORKS
------------
Every effect is ONE OR A FEW mesh objects driven by a shared Geometry Nodes rig
("RBVFX_cache_v1"). At build time the effect's particle states for every frame of
its life window are computed in Python/numpy from the arguments and a seeded RNG
(position, euler rotation, xyz scale, heat, alpha per particle per frame) and stored
as loose "cache" points inside the object's mesh, next to the particle template
geometry (spheres, streaks, chunks, petals, tubes, ribbons...). The GN rig reads the
scene frame (Scene Time), samples the cache at floor(frame) and floor(frame)+1 and
interpolates (so sub-frame motion blur samples are right), places the template
vertices and stores `heat` / `alpha` for the shaders. No particle caches, no
handlers: the result is a pure function of the frame number. Frames before / after
the effect window clamp to invisible (or resting, for debris) states.

Lights are real lights keyed per frame (energy / location), never shadow-casting
(the 2 shadow lights of a shot belong to the key rig). Glows are additive
(Emission + Transparent, BLEND, no shadow) with a soft |N.I| falloff and an
animated 4D-noise turbulence (shader time = driver `frame / 30`).

All objects live in the "VFX" collection and are uniquely named VFX_<kind>_###,
so every function can be called any number of times in one scene.

PALETTE: ember #FF6A1A, fire orange-red, sparks #FFB060, lightning #CFE6FF / #6FA8FF,
god attack #FFE9A8 -> white. Floors are assumed at z = 0 unless `floor=` is given.

API (frame = video frame of the effect's key moment; returns a dict of handles:
     'obj' main object, 'objects' every object incl. lights and sub-effects,
     'lights', 'mats', 'frames' (first, last cache frame) + effect-specific keys)
---------------------------------------------------------------------------------
  embers(f0, f1, center, radius=4, height=5, count=160, seed=0, falling=False, cam=None,
         color="#FF6A1A", strength=1.0, near=6, wind=(0, 0))
      ambient drifting / flickering embers alive over [f0, f1); 3 size/brightness layers
      (fine far dust, embers, hero embers); falling=True drifts down like burning ash.
      cam (camera object or rb_cam.Rig) -> `near` big soft embers parented to the camera
      0.35-1.1 m in front of the lens (bokeh with DOF).
  ash(f0, f1, center, radius=4, height=4, count=220, seed=0, color=(.55,.55,.55), rise=0.3)
      lit tumbling ash flakes / dust motes (rise in m/s, negative = falling)
  dust_puff(frame, loc, seed=0, scale=1.0, floor=None)      boot-plant dust ring (+ grit), ~14 f
  sparks(frame, loc, seed=0, scale=1.0, direction=None, count=None, color="#FFB060",
         time_scale=1.0, gravity=9.81, speed=(2.5, 8.5), life=(6, 16), flash=True, light=True)
      streaky white-hot sparks with gravity, drag, floor bounce/skid; time_scale=0.5 hangs them
  shockwave(frame, loc, seed=0, scale=1.0, floor=None, dust=True)
      floor ring + air ring + dome flash + light (+ lifted dust), ~12 f
  debris(frame, loc, seed=0, scale=1.0, count=None, kind="rock"|"bone", floor=None, dust=True)
      faceted chunks with gravity, spin, bounce and rest (rock chunks glow ember when fresh)
  smoke_burst(frame, loc, seed=0, scale=1.0, color="#1A1220", glow="#A04DFF")
      dark smoke puffs with inner glow + glowing core + glow motes + light, ~16-20 f
  fireball(frame, start, end, seed=0, scale=1.0, travel=6, floor=None)
      4-frame charge at start, turbulent fire ball flying start->end in `travel` frames with
      a fire trail, a moving light, and an explosion (fire, flash, smoke, sparks, light) at end
  lightning(frame, start, end, seed=0, scale=1.0, duration=8)
      end = point or list of points (forks); fractal branching bolts re-randomised every
      1-2 frames (leader frame at frame-1), impact sparks, strobing flash lights
  god_attack(frame, origin, target, seed=0, scale=1.0, column=False, height=45, floor=None)
      6-frame build-up at origin, beam origin->target (reaches target at frame+1),
      expanding sphere + gold sparks at target, flood lights (2 points + a sun).
      column=True: vertical pillar of gold light from (origin.x, origin.y, floor) + ring + motes.
  ember_trail(obj, f0, f1, seed=0, color="#FF6A1A", width=0.08, span=None, offset=(0,0,0),
              axis=(0,0,1), fade=6, sparks=60)
      glowing ribbon following obj's world path (sampled with scene.frame_set incl. sub-frames),
      fading over `fade` frames + shed embers. span=(a, b) local points makes a blade smear;
      default: a mesh's longest bounding-box axis (outer 70 % toward the tip), else a
      `width` ribbon at `offset` oriented along local `axis`.
  petals(f0, f1, center, radius=6, height=4, count=150, seed=0)   pale tumbling petals (heaven)
  remove(handles)            delete every object of an effect (tests / re-takes)
  glow_mat / soft_mat        the material builders (usable for custom effects)
"""
import math

import bpy
import numpy as np
from mathutils import Matrix, Vector

import rb_core as C
import rb_mat as M

EMBER = "#FF6A1A"
FIRE = "#FF4A14"
SPARK = "#FFB060"
BOLT_CORE = "#CFE6FF"
BOLT_GLOW = "#6FA8FF"
GOLD = "#FFE9A8"
GOLD_DEEP = "#F2B544"
WHITE_HOT = "#FFF6E6"
GN_NAME = "RBVFX_cache_v1"
COLL = "VFX"
FPS = C.FPS


# ===================================================================== seeds / noise
def _seed(seed, salt=""):
    h = 2166136261
    for ch in str(salt):
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return (int(seed) * 2654435761 + h * 40503) & 0xFFFFFFFFFFFF


def _rng(seed, salt=""):
    return np.random.default_rng(_seed(seed, salt))


_MASK = np.uint64(0xFFFFFFFF)


def _hash(i, s):
    """Deterministic integer hash -> float in [0, 1). i, s: int arrays (broadcast)."""
    with np.errstate(all="ignore"):
        i = np.asarray(i).astype(np.int64).astype(np.uint64)
        s = (np.asarray(s).astype(np.int64) & 0x7FFFFFFF).astype(np.uint64)
        x = (i * np.uint64(0x9E3779B1) + s * np.uint64(0x85EBCA77) + np.uint64(0x27D4EB2F)) & _MASK
        x = x ^ (x >> np.uint64(15))
        x = (x * np.uint64(0x2C1B3C6D)) & _MASK
        x = x ^ (x >> np.uint64(12))
        x = (x * np.uint64(0x297A2D39)) & _MASK
        x = x ^ (x >> np.uint64(15))
    return x.astype(np.float64) / 4294967296.0


def _vn(t, s, octaves=2):
    """Smooth 1-D value noise in [-1, 1], vectorised over t and per-particle seeds s."""
    t = np.asarray(t, float)
    tot = 0.0
    amp, fr, norm = 1.0, 1.0, 0.0
    for o in range(octaves):
        x = t * fr + 17.31 * o
        i = np.floor(x)
        f = x - i
        ii = i.astype(np.int64)
        a = _hash(ii, np.asarray(s) + 7919 * o) * 2 - 1
        b = _hash(ii + 1, np.asarray(s) + 7919 * o) * 2 - 1
        u = f * f * (3 - 2 * f)
        tot = tot + amp * (a + (b - a) * u)
        norm += amp
        amp *= 0.5
        fr *= 2.0
    return tot / norm


def _ss(e0, e1, x):
    x = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0.0, 1.0)
    return x * x * (3 - 2 * x)


def _eo(x):
    x = np.clip(np.asarray(x, float), 0.0, 1.0)
    return 1 - (1 - x) ** 3


def _unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-9)


def _align_euler(d):
    """Euler XYZ (..., 3) rotating local +Z onto direction d (..., 3); unwrapped along axis 0 (time)."""
    d = np.asarray(d, float)
    n = np.linalg.norm(d, axis=-1, keepdims=True)
    d = np.where(n > 1e-9, d / np.maximum(n, 1e-9), np.array([0.0, 0.0, 1.0]))
    beta = np.arccos(np.clip(d[..., 2], -1, 1))
    gamma = np.arctan2(d[..., 1], d[..., 0])
    if gamma.ndim >= 1 and gamma.shape[0] > 1:
        gamma = np.unwrap(gamma, axis=0)
    return np.stack([np.zeros_like(beta), beta, gamma], -1)


def _vec3(p):
    return np.array([float(p[0]), float(p[1]), float(p[2])])


def _floor(floor, loc):
    if floor is not None:
        return float(floor)
    return min(0.0, float(loc[2]) - 0.01)


def _lighten(hexc, k):
    c = np.array(C.hexcol(hexc))
    return tuple(c * (1 - k) + k)


# ===================================================================== templates
def _uv_sphere(seg=8, rings=5):
    V = [(0.0, 0.0, 1.0)]
    for r in range(1, rings):
        ph = math.pi * r / rings
        for s in range(seg):
            th = 2 * math.pi * s / seg
            V.append((math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)))
    V.append((0.0, 0.0, -1.0))
    F = []
    for s in range(seg):
        F.append((0, 1 + s, 1 + (s + 1) % seg))
    for r in range(rings - 2):
        for s in range(seg):
            a = 1 + r * seg + s
            b = 1 + r * seg + (s + 1) % seg
            F.append((a, a + seg, b + seg, b))
    bot = len(V) - 1
    base = 1 + (rings - 2) * seg
    for s in range(seg):
        F.append((base + s, bot, base + (s + 1) % seg))
    return np.array(V), F


def _ico(sub=1):
    t = (1 + 5 ** 0.5) / 2
    V = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
         (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6),
         (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10),
         (8, 6, 7), (9, 8, 1)]
    V = [np.array(v, float) / np.linalg.norm(v) for v in V]
    for _ in range(sub):
        cache = {}

        def mid(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache:
                m = V[a] + V[b]
                V.append(m / np.linalg.norm(m))
                cache[k] = len(V) - 1
            return cache[k]
        nf = []
        for a, b, c in F:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            nf += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        F = nf
    return np.array(V), F


def _annulus(seg=96, rows=4, r0=0.55, r1=1.0):
    V, v = [], []
    for j in range(rows + 1):
        rr = r0 + (r1 - r0) * j / rows
        for s in range(seg):
            th = 2 * math.pi * s / seg
            V.append((rr * math.cos(th), rr * math.sin(th), 0.0))
            v.append(j / rows)
    F = []
    for j in range(rows):
        for s in range(seg):
            a = j * seg + s
            b = j * seg + (s + 1) % seg
            F.append((a, a + seg, b + seg, b))
    return np.array(V), F, np.array(v)


def _beam(seg=20, rows=14, tip0=0.03, tip1=0.06):
    """Unit-radius cylinder along +Z (0..1) with rounded, tapered ends; returns V, F, u."""
    V, u = [], []
    zs = np.concatenate([[0.0, tip0 * 0.35, tip0], np.linspace(tip0, 1 - tip1, rows)[1:-1],
                         [1 - tip1, 1 - tip1 * 0.4, 1.0]])
    for z in zs:
        r = min(1.0, z / tip0) * min(1.0, (1 - z) / tip1)
        r = max(r, 0.0) ** 0.5
        for s in range(seg):
            th = 2 * math.pi * s / seg
            V.append((r * math.cos(th), r * math.sin(th), z))
            u.append(z)
    F = []
    for j in range(len(zs) - 1):
        for s in range(seg):
            a = j * seg + s
            b = j * seg + (s + 1) % seg
            F.append((a, b, b + seg, a + seg))
    return np.array(V), F, np.array(u)


def _tube(pts, radii, sides=5):
    """World-space tube along a polyline (parallel transport frames). Returns V, F, u."""
    pts = np.asarray(pts, float)
    n = len(pts)
    radii = np.broadcast_to(np.asarray(radii, float), (n,))
    T = np.gradient(pts, axis=0)
    T = _unit(T)
    ref = np.array([0.0, 0.0, 1.0]) if abs(T[0, 2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    nrm = _unit(np.cross(T[0], ref))
    V = []
    for i in range(n):
        nrm = nrm - T[i] * (nrm @ T[i])
        nrm = nrm / max(np.linalg.norm(nrm), 1e-9)
        bn = np.cross(T[i], nrm)
        for s in range(sides):
            a = 2 * math.pi * s / sides
            V.append(pts[i] + radii[i] * (math.cos(a) * nrm + math.sin(a) * bn))
    F = []
    for i in range(n - 1):
        for s in range(sides):
            a = i * sides + s
            b = i * sides + (s + 1) % sides
            F.append((a, b, b + sides, a + sides))
    u = np.repeat(np.linspace(0, 1, n), sides)
    return np.array(V), F, u


def _flake(rg, n=6):
    ang = np.sort(rg.uniform(0, 2 * math.pi, n))
    rad = rg.uniform(0.55, 1.0, n)
    V = [(0.0, 0.0, 0.0)] + [(r * math.cos(a), r * math.sin(a), rg.uniform(-0.08, 0.08)) for a, r in zip(ang, rad)]
    F = [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
    return np.array(V), F


def _petal():
    V = []
    nu, nv = 6, 3
    for i in range(nu):
        u = i / (nu - 1)
        w = 0.32 * math.sin(math.pi * min(0.98, u * 0.92 + 0.06)) ** 0.7 + 0.02
        for j in range(nv):
            x = (j / (nv - 1) - 0.5) * 2 * w
            V.append((x, u - 0.5, 0.9 * x * x + 0.12 * math.sin(math.pi * u)))
    F = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            a = i * nv + j
            F.append((a, a + 1, a + nv + 1, a + nv))
    return np.array(V), F


# ===================================================================== mesh / object plumbing
def _fgroups(faces):
    if isinstance(faces, dict):
        return {k: np.asarray(v, np.int64).reshape(-1, k) for k, v in faces.items() if len(v)}
    out = {}
    for f in faces:
        out.setdefault(len(f), []).append(f)
    return {k: np.asarray(v, np.int64) for k, v in out.items()}


def _mk_mesh(name, V, groups):
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(V))
    me.vertices.foreach_set("co", np.ascontiguousarray(V, np.float32).ravel())
    if groups:
        loops = np.concatenate([g.ravel() for g, _ in groups]).astype(np.int32)
        sizes = np.concatenate([np.full(len(g), g.shape[1], np.int32) for g, _ in groups])
        starts = np.concatenate([[0], np.cumsum(sizes)[:-1]]).astype(np.int32)
        me.loops.add(len(loops))
        me.loops.foreach_set("vertex_index", loops)
        me.polygons.add(len(sizes))
        me.polygons.foreach_set("loop_start", starts)
        try:
            me.polygons.foreach_set("loop_total", sizes)
        except (AttributeError, TypeError, RuntimeError):
            pass
        me.polygons.foreach_set("material_index", np.concatenate([m for _, m in groups]).astype(np.int32))
    me.update(calc_edges=True)
    if groups:
        me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
    return me


def _attr(me, name, kind, data):
    a = me.attributes.new(name, kind, "POINT")
    if kind == "INT":
        a.data.foreach_set("value", np.ascontiguousarray(data, np.int32).ravel())
    elif kind == "FLOAT":
        a.data.foreach_set("value", np.ascontiguousarray(data, np.float32).ravel())
    else:
        a.data.foreach_set("vector", np.ascontiguousarray(data, np.float32).ravel())


def _uname(base):
    i = 1
    while True:
        nm = "VFX_%s_%03d" % (base, i)
        if nm not in bpy.data.objects and nm not in bpy.data.meshes and nm not in bpy.data.lights:
            return nm
        i += 1


def _coll():
    sc = bpy.context.scene
    co = bpy.data.collections.get(COLL)
    if co is None:
        co = bpy.data.collections.new(COLL)
    if sc.collection.children.get(co.name) is None:
        sc.collection.children.link(co)
    return co


def _gn_group():
    ng = bpy.data.node_groups.get(GN_NAME)
    if ng is not None:
        return ng
    ng = bpy.data.node_groups.new(GN_NAME, "GeometryNodeTree")
    itf = ng.interface
    itf.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    for nm in ("F0", "NF", "N"):
        itf.new_socket(nm, in_out="INPUT", socket_type="NodeSocketFloat")
    itf.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    nd, ln = ng.nodes, ng.links

    def node(kind, **props):
        n = nd.new(kind)
        for k, v in props.items():
            setattr(n, k, v)
        return n

    def sin(n, name):
        return [s for s in n.inputs if s.name == name and s.enabled][0]

    def sout(n, name):
        return [s for s in n.outputs if s.name == name and s.enabled][0]

    def put(a, sock):
        if isinstance(a, (int, float)):
            sock.default_value = a
        else:
            ln.new(a, sock)

    def math_(op, a, b=None):
        n = node("ShaderNodeMath", operation=op)
        put(a, n.inputs[0])
        if b is not None:
            put(b, n.inputs[1])
        return n.outputs[0]

    def named(name, dtype):
        n = node("GeometryNodeInputNamedAttribute", data_type=dtype)
        n.inputs["Name"].default_value = name
        return sout(n, "Attribute")

    gi = node("NodeGroupInput")
    go = node("NodeGroupOutput")
    tm = node("GeometryNodeInputSceneTime")
    local = math_("SUBTRACT", tm.outputs["Frame"], gi.outputs["F0"])
    local = math_("MAXIMUM", local, 0.0)
    local = math_("MINIMUM", local, math_("SUBTRACT", gi.outputs["NF"], 1.0))
    kA = math_("MINIMUM", math_("FLOOR", local), math_("SUBTRACT", gi.outputs["NF"], 2.0))
    t = math_("SUBTRACT", local, kA)
    kB = math_("ADD", kA, 1.0)
    sep = node("GeometryNodeSeparateGeometry", domain="POINT")
    ln.new(gi.outputs["Geometry"], sep.inputs["Geometry"])
    ln.new(named("is_cache", "INT"), sep.inputs["Selection"])
    cache, tmpl = sep.outputs["Selection"], sep.outputs["Inverted"]
    pid = named("pid", "INT")
    iA = math_("ADD", math_("MULTIPLY", kA, gi.outputs["N"]), pid)
    iB = math_("ADD", math_("MULTIPLY", kB, gi.outputs["N"]), pid)

    def sample(dtype, field):
        res = []
        for idx in (iA, iB):
            s = node("GeometryNodeSampleIndex", data_type=dtype, domain="POINT")
            s.clamp = True
            ln.new(cache, s.inputs["Geometry"])
            ln.new(field, sin(s, "Value"))
            ln.new(idx, s.inputs["Index"])
            res.append(sout(s, "Value"))
        mx = node("ShaderNodeMix", data_type="VECTOR" if dtype == "FLOAT_VECTOR" else "FLOAT")
        ln.new(t, sin(mx, "Factor"))
        ln.new(res[0], sin(mx, "A"))
        ln.new(res[1], sin(mx, "B"))
        return sout(mx, "Result")

    pos = node("GeometryNodeInputPosition").outputs["Position"]
    P = sample("FLOAT_VECTOR", pos)
    R = sample("FLOAT_VECTOR", named("rot", "FLOAT_VECTOR"))
    S = sample("FLOAT_VECTOR", named("scl", "FLOAT_VECTOR"))
    H = sample("FLOAT", named("heat", "FLOAT"))
    A = sample("FLOAT", named("alpha", "FLOAT"))
    mul = node("ShaderNodeVectorMath", operation="MULTIPLY")
    ln.new(node("GeometryNodeInputPosition").outputs["Position"], mul.inputs[0])
    ln.new(S, mul.inputs[1])
    rot = node("ShaderNodeVectorRotate", rotation_type="EULER_XYZ")
    ln.new(mul.outputs["Vector"], rot.inputs["Vector"])
    ln.new(R, rot.inputs["Rotation"])
    add = node("ShaderNodeVectorMath", operation="ADD")
    ln.new(rot.outputs["Vector"], add.inputs[0])
    ln.new(P, add.inputs[1])
    sp = node("GeometryNodeSetPosition")
    ln.new(tmpl, sp.inputs["Geometry"])
    ln.new(add.outputs["Vector"], sp.inputs["Position"])
    geo = sp.outputs["Geometry"]
    for name, val in (("heat", H), ("alpha", A)):
        st = node("GeometryNodeStoreNamedAttribute", data_type="FLOAT", domain="POINT")
        st.inputs["Name"].default_value = name
        ln.new(geo, st.inputs["Geometry"])
        ln.new(val, sin(st, "Value"))
        geo = st.outputs["Geometry"]
    ln.new(geo, go.inputs[0])
    return ng


class _FX:
    """Accumulates particle templates + per-frame states, then builds one GN-driven object."""

    def __init__(self, kind, fa, fb):
        self.kind = kind
        self.fa = int(fa)
        self.fb = max(int(fb), self.fa + 1)
        self.NF = self.fb - self.fa + 1
        self.F = np.arange(self.fa, self.fb + 1, dtype=float)
        self.parts = []
        self.n = 0

    def add(self, V, faces, P, rot=None, scl=None, size=None, heat=None, alpha=None, vpid=None, u=None, v=None,
            mat=0):
        NF = self.NF
        V = np.asarray(V, float).reshape(-1, 3)
        P = np.asarray(P, float)
        if P.ndim == 2:
            P = P[:, None, :]
        k = P.shape[1]
        sh3, sh1 = (NF, k, 3), (NF, k)
        P = np.broadcast_to(P, sh3)
        rot = np.zeros(sh3) if rot is None else np.broadcast_to(np.asarray(rot, float), sh3)
        if scl is None:
            sz = np.ones(sh1) if size is None else np.broadcast_to(np.asarray(size, float), sh1)
            scl = np.repeat(sz[..., None], 3, -1)
        else:
            scl = np.broadcast_to(np.asarray(scl, float), sh3)
        heat = np.zeros(sh1) if heat is None else np.broadcast_to(np.asarray(heat, float), sh1)
        alpha = np.ones(sh1) if alpha is None else np.broadcast_to(np.asarray(alpha, float), sh1)
        nv = len(V)
        vpid = np.zeros(nv, int) if vpid is None else np.asarray(vpid, int)
        u = np.zeros(nv) if u is None else np.broadcast_to(np.asarray(u, float), (nv,))
        v = np.zeros(nv) if v is None else np.broadcast_to(np.asarray(v, float), (nv,))
        self.parts.append(dict(V=V, faces=_fgroups(faces), P=P, R=rot, S=scl, H=heat, A=alpha,
                               vpid=vpid + self.n, u=u, v=v, mat=int(mat)))
        self.n += k

    def add_tiled(self, Vt, Ft, P, u=None, v=None, **kw):
        P = np.asarray(P, float)
        k = P.shape[1]
        Vt = np.asarray(Vt, float)
        nt = len(Vt)
        V = np.tile(Vt, (k, 1))
        G = _fgroups(Ft)
        faces = {ar: (arr[None] + (np.arange(k) * nt)[:, None, None]).reshape(-1, ar) for ar, arr in G.items()}
        vpid = np.repeat(np.arange(k), nt)
        u = None if u is None else np.tile(np.asarray(u, float), k)
        v = None if v is None else np.tile(np.asarray(v, float), k)
        self.add(V, faces, P, vpid=vpid, u=u, v=v, **kw)

    def build(self, mats, parent=None):
        parts = self.parts
        V = np.concatenate([p["V"] for p in parts])
        offs = np.cumsum([0] + [len(p["V"]) for p in parts])
        groups = []
        for p, o in zip(parts, offs):
            for ar, arr in p["faces"].items():
                groups.append((arr + o, np.full(len(arr), p["mat"], np.int32)))
        P = np.concatenate([p["P"] for p in parts], 1)
        R = np.concatenate([p["R"] for p in parts], 1)
        S = np.concatenate([p["S"] for p in parts], 1)
        H = np.concatenate([p["H"] for p in parts], 1)
        A = np.concatenate([p["A"] for p in parts], 1)
        N = P.shape[1]
        T = len(V)
        NC = self.NF * N
        name = _uname(self.kind)
        me = _mk_mesh(name, np.concatenate([V, P.reshape(-1, 3)]), groups)
        z1, z3 = np.zeros(NC), np.zeros((NC, 3))
        _attr(me, "is_cache", "INT", np.concatenate([np.zeros(T), np.ones(NC)]))
        _attr(me, "pid", "INT", np.concatenate([np.concatenate([p["vpid"] for p in parts]), z1]))
        _attr(me, "rot", "FLOAT_VECTOR", np.concatenate([np.zeros((T, 3)), R.reshape(-1, 3)]))
        _attr(me, "scl", "FLOAT_VECTOR", np.concatenate([np.zeros((T, 3)), S.reshape(-1, 3)]))
        _attr(me, "heat", "FLOAT", np.concatenate([np.zeros(T), H.reshape(-1)]))
        _attr(me, "alpha", "FLOAT", np.concatenate([np.zeros(T), A.reshape(-1)]))
        _attr(me, "u", "FLOAT", np.concatenate([np.concatenate([p["u"] for p in parts]), z1]))
        _attr(me, "v", "FLOAT", np.concatenate([np.concatenate([p["v"] for p in parts]), z1]))
        _attr(me, "lco", "FLOAT_VECTOR", np.concatenate([V, z3]))
        for m in mats:
            me.materials.append(m)
        ob = bpy.data.objects.new(name, me)
        _coll().objects.link(ob)
        mod = ob.modifiers.new("RBVFX", "NODES")
        mod.node_group = _gn_group()
        vals = {"F0": float(self.fa), "NF": float(self.NF), "N": float(N)}
        for it in mod.node_group.interface.items_tree:
            if getattr(it, "in_out", "") == "INPUT" and it.name in vals:
                mod[it.identifier] = vals[it.name]
        if parent is not None:
            ob.parent = parent
            ob.matrix_parent_inverse = Matrix.Identity(4)
        return ob


def _linear(idb):
    ad = idb.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"


def _light(kind_name, color, frames, energy, locs=None, loc=None, size=0.3, volume=1.0, specular=0.5, kind="POINT",
           rot=None):
    """Shadowless light keyed per frame: energy[i] at frames[i] (+ zero keys around), optional locs[i]."""
    frames = [int(f) for f in frames]
    energy = [max(0.0, float(e)) for e in energy]
    nm = _uname(kind_name)
    p0 = tuple(locs[0]) if locs is not None else tuple(loc)
    ob = C.light(kind, nm, p0, color=color, energy=0.0, size=size, shadow=False, volume=volume, specular=specular)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    _coll().objects.link(ob)
    if rot is not None:
        ob.rotation_euler = rot
    ld = ob.data
    seq = [(frames[0] - 1, 0.0)] + list(zip(frames, energy)) + [(frames[-1] + 1, 0.0)]
    for f, e in seq:
        ld.energy = e
        ld.keyframe_insert("energy", frame=f)
    if locs is not None:
        for f, p in zip(frames, locs):
            ob.location = tuple(p)
            ob.keyframe_insert("location", frame=f)
        _linear(ob)
    _linear(ld)
    return ob


def _handles(obj, objects, lights=(), mats=None, frames=None, **extra):
    h = dict(obj=obj, objects=[o for o in objects if o is not None], lights=list(lights), mats=mats or {},
             frames=frames)
    for o in lights:
        if o not in h["objects"]:
            h["objects"].append(o)
    h.update(extra)
    return h


def _merge(h, sub):
    """Add a sub-effect's objects / lights to handle dict h."""
    if sub:
        for o in sub["objects"]:
            if o not in h["objects"]:
                h["objects"].append(o)
        h["lights"] += [o for o in sub["lights"] if o not in h["lights"]]
    return h


def remove(h):
    """Delete every object created by an effect (handles dict)."""
    for ob in list(h.get("objects", [])):
        try:
            bpy.data.objects.remove(ob, do_unlink=True)
        except (ReferenceError, RuntimeError):
            pass


# ===================================================================== materials
def _time(b):
    node = b.n("ShaderNodeValue")
    node.name = "CTRL_time"
    node.label = "time"
    fc = node.outputs[0].driver_add("default_value")
    fc.driver.type = "SCRIPTED"
    fc.driver.expression = "frame / 30.0"
    return node


def _noise_mask(b, nscale, nspeed, lo=0.32, hi=0.70, coord="world", detail=5.0):
    if coord == "world":
        geo = b.n("ShaderNodeNewGeometry")
        src = (geo, "Position")
    else:
        src = (b.n("ShaderNodeAttribute", _attribute_name="lco", _attribute_type="GEOMETRY"), "Vector")
    vec = b.n("ShaderNodeVectorMath", _operation="SCALE", Vector=src)
    vec.inputs["Scale"].default_value = nscale
    w = b.math("MULTIPLY", _time(b), nspeed)
    nz = b.n("ShaderNodeTexNoise", _noise_dimensions="4D", Vector=(vec, "Vector"), W=w, Scale=1.0, Detail=detail,
             Roughness=0.62, Distortion=0.35)
    return (b.n("ShaderNodeMapRange", Value=(nz, "Fac"), **{"From Min": lo, "From Max": hi}), "Result")


def _mad(b, a, mul, add):
    n = b.n("ShaderNodeMath", _operation="MULTIPLY_ADD")
    b._in(n, 0, a)
    n.inputs[1].default_value = mul
    n.inputs[2].default_value = add
    return n


def _heat_stops(color, hot, deep=None):
    c = np.array(C.hexcol(color) if isinstance(color, str) else color[:3], float)
    w = np.array(C.hexcol(hot) if isinstance(hot, str) else hot[:3], float)
    if deep is not None:
        d = np.array(C.hexcol(deep) if isinstance(deep, str) else deep[:3], float)
    elif c[0] >= c[2]:
        d = c * np.array([0.32, 0.10, 0.06])
    else:
        d = c * 0.22
    return [(0.0, (0.0, 0.0, 0.0)), (0.16, tuple(d)), (0.42, tuple(c)), (0.72, tuple(c * 0.45 + w * 0.55)),
            (1.0, tuple(w))]


def glow_mat(name, color, strength=10.0, hot=WHITE_HOT, soft=1.5, profile="facing", stops=None, noise=0.0,
             nscale=3.0, nspeed=0.6, cull=True, heat_pow=2.0, deep=None):
    """Additive emissive glow. Reads point attr `heat` (0 off, 1 = base colour..hot, >1 clips white).
    profile: 'facing' soft core (|N.I|^soft), 'shell' bright rim, 'v' uses ramp `stops` over attr v."""
    full = "VFXM_" + name
    m = bpy.data.materials.get(full)
    if m is not None:
        return m
    m, b = M.new(full, "BLEND")
    m.shadow_method = "NONE"
    m.use_backface_culling = cull
    m.show_transparent_back = True
    heat = b.attr("heat")
    h = heat
    mask = None
    if noise > 0:
        mask = _noise_mask(b, nscale, nspeed)
        h = b.math("MULTIPLY", heat, _mad(b, mask, noise * 0.8, 1.0 - noise * 0.45))
    ramp = b.ramp(h, _heat_stops(color, hot, deep))
    if profile == "v":
        p = (b.ramp(b.attr("v"), stops or [(0.0, (0, 0, 0)), (0.5, (1, 1, 1)), (1.0, (0, 0, 0))]), "Color")
    else:
        lw = b.n("ShaderNodeLayerWeight", Blend=0.5)
        if profile == "shell":
            p = b.math("POWER", (lw, "Facing"), soft)
        else:
            p = b.math("POWER", b.math("SUBTRACT", 1.0, (lw, "Facing"), clamp=True), soft)
    st = b.math("MULTIPLY", b.math("POWER", h, heat_pow), p)
    if mask is not None:
        st = b.math("MULTIPLY", st, _mad(b, mask, noise, 1.0 - noise))
    st = b.math("MULTIPLY", st, strength)
    em = b.n("ShaderNodeEmission", Color=(ramp, "Color"), Strength=st)
    tr = b.n("ShaderNodeBsdfTransparent")
    add = b.n("ShaderNodeAddShader")
    b.link(em, add.inputs[0])
    b.link(tr, add.inputs[1])
    b.out(add)
    return m


def soft_mat(name, color, glow=None, glow_strength=0.0, soft=1.3, noise=0.7, nscale=2.5, nspeed=0.5, opacity=1.0,
             rough=0.95, spec=0.12):
    """Lit soft volume-ish puff (smoke / dust): Principled with alpha = attr alpha * |N.I|^soft * noise;
    optional inner glow (emission colour `glow` * attr heat)."""
    full = "VFXM_" + name
    m = bpy.data.materials.get(full)
    if m is not None:
        return m
    m, b = M.new(full, "BLEND")
    m.shadow_method = "NONE"
    m.use_backface_culling = True
    m.show_transparent_back = True
    col = C.hexcol(color) if isinstance(color, str) else tuple(color[:3])
    lw = b.n("ShaderNodeLayerWeight", Blend=0.5)
    prof = b.math("POWER", b.math("SUBTRACT", 1.0, (lw, "Facing"), clamp=True), soft)
    mask = _noise_mask(b, nscale, nspeed, 0.28, 0.72)
    brk = _mad(b, mask, noise, 1.0 - noise)
    al = b.math("MULTIPLY", b.math("MULTIPLY", b.attr("alpha"), prof), brk)
    al = b.math("MULTIPLY", al, opacity, clamp=True)
    base = b.mix(mask, tuple(np.array(col) * 0.7), tuple(np.array(col) * 1.25))
    bs = b.bsdf(**{"Base Color": base, "Roughness": rough, "Specular IOR Level": spec, "Alpha": al})
    if glow is not None and glow_strength > 0:
        gc = C.hexcol(glow) if isinstance(glow, str) else tuple(glow[:3])
        gs = b.math("MULTIPLY", b.math("POWER", b.attr("heat"), 2.0), prof)
        gs = b.math("MULTIPLY", gs, _mad(b, mask, 0.8, 0.3))
        gs = b.math("MULTIPLY", gs, glow_strength)
        b.set(bs, "Emission Color", gc)
        b.link(gs, bs.inputs["Emission Strength"])
    b.out(bs)
    return m


def debris_mat(kind="rock"):
    full = "VFXM_debris_" + kind
    m = bpy.data.materials.get(full)
    if m is not None:
        return m
    m, b = M.new(full)
    lco = (b.n("ShaderNodeAttribute", _attribute_name="lco", _attribute_type="GEOMETRY"), "Vector")
    n1 = b.n("ShaderNodeTexNoise", Vector=lco, Scale=9.0, Detail=6.0, Roughness=0.62)
    n2 = b.n("ShaderNodeTexNoise", Vector=lco, Scale=38.0, Detail=4.0, Roughness=0.7)
    bump = b.n("ShaderNodeBump", Strength=0.45, Distance=0.004, Height=(n2, "Fac"))
    if kind == "bone":
        base = b.ramp((n1, "Fac"), [(0.3, (0.20, 0.17, 0.12)), (0.55, (0.52, 0.47, 0.38)), (0.8, (0.66, 0.61, 0.50))])
        bs = b.bsdf(**{"Base Color": (base, "Color"), "Roughness": 0.62, "Specular IOR Level": 0.35,
                       "Subsurface Weight": 0.12, "Normal": (bump, "Normal")})
        bs.inputs["Subsurface Radius"].default_value = (0.02, 0.012, 0.008)
    else:
        base = b.ramp((n1, "Fac"), [(0.25, (0.018, 0.017, 0.016)), (0.6, (0.05, 0.047, 0.043)),
                                    (0.85, (0.085, 0.078, 0.07))])
        rough = b.ramp((n2, "Fac"), [(0.3, (0.55, 0.55, 0.55)), (0.8, (0.9, 0.9, 0.9))])
        vein = b.n("ShaderNodeMapRange", Value=(n1, "Fac"), **{"From Min": 0.5, "From Max": 0.62})
        hs = b.math("MULTIPLY", b.math("POWER", b.attr("heat"), 2.0), (vein, "Result"))
        hs = b.math("MULTIPLY", hs, 8.0)
        bs = b.bsdf(**{"Base Color": (base, "Color"), "Roughness": (rough, "Color"), "Specular IOR Level": 0.4,
                       "Normal": (bump, "Normal"), "Emission Color": C.hexcol(EMBER)})
        b.link(hs, bs.inputs["Emission Strength"])
    b.out(bs)
    return m


def flake_mat(name, color, translucent=0.25, rough=0.85, tint2=None, sheen=0.0, sss=0.0):
    """Lit thin flakes (ash, petals): double sided, colour varied per particle by attr heat."""
    full = "VFXM_" + name
    m = bpy.data.materials.get(full)
    if m is not None:
        return m
    m, b = M.new(full)
    m.use_backface_culling = False
    m.shadow_method = "NONE"
    c1 = C.hexcol(color) if isinstance(color, str) else tuple(color[:3])
    c2 = (C.hexcol(tint2) if isinstance(tint2, str) else tuple(tint2[:3])) if tint2 is not None else \
        tuple(np.array(c1) * 0.45)
    base = b.mix(b.attr("heat"), c2, c1)
    bs = b.bsdf(**{"Base Color": base, "Roughness": rough, "Specular IOR Level": 0.25, "Sheen Weight": sheen,
                   "Subsurface Weight": sss})
    tl = b.n("ShaderNodeBsdfTranslucent", Color=base)
    mx = b.n("ShaderNodeMixShader", Fac=translucent)
    b.link(bs, mx.inputs[1])
    b.link(tl, mx.inputs[2])
    b.out(mx)
    return m


# ===================================================================== drift fields
def _drift(rg, N, c, radius, height, vz, period, sway, sfreq, rmul=None, band=0.6, wind=(0.0, 0.0)):
    """Cyclic respawning drift field -> pos(t) returning ((T,N,3) positions, (T,N) cycle age 0..1).
    vz (N,) m/frame (+up / -down), period (N,) frames. A pure function of t."""
    phase = rg.uniform(0, 1, N)
    ps = rg.integers(1, 2 ** 30, N)
    swr = rg.uniform(0.02, 0.09, N)
    swo = rg.uniform(0.05, 0.16, N) * rg.choice([-1.0, 1.0], N)
    swp = rg.uniform(0, 2 * math.pi, N)
    rm = np.ones(N) if rmul is None else rmul
    up = vz >= 0

    def pos(t):
        tt = np.asarray(t, float)[:, None]
        x = tt / period + phase
        cyc = np.floor(x)
        a = x - cyc
        ci = cyc.astype(np.int64)
        h0, h1, h2 = _hash(ci, ps), _hash(ci, ps + 101), _hash(ci, ps + 202)
        rr = radius * rm * np.sqrt(h0)
        th = 2 * math.pi * h1
        z0 = np.where(up, c[2] - height / 2 + h2 * height * band, c[2] + height / 2 - h2 * height * band)
        z = z0 + vz * period * a
        sx = sway * _vn(tt * sfreq, ps + 11)
        sy = sway * _vn(tt * sfreq, ps + 23)
        sz = 0.3 * sway * _vn(tt * sfreq * 1.3, ps + 37)
        X = c[0] + rr * np.cos(th) + sx + swr * np.cos(swo * tt + swp) + wind[0] * a * period
        Y = c[1] + rr * np.sin(th) + sy + swr * np.sin(swo * tt + swp) + wind[1] * a * period
        return np.stack([X, Y, z + sz], -1), a
    return pos, ps


def _vel(pos, F, vmax=0.15):
    v = pos(F + 0.5)[0] - pos(F - 0.5)[0]
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return np.where(n > vmax, v * vmax / np.maximum(n, 1e-9), v)


def _window(F, f0, f1):
    """(T,1) mask: 1 inside [f0, f1), 0 outside."""
    return ((F >= f0) & (F < f1)).astype(float)[:, None]


# ===================================================================== embers
def embers(f0, f1, center, radius=4.0, height=5.0, count=160, seed=0, falling=False, cam=None, color=EMBER,
           strength=1.0, near=6, wind=(0.0, 0.0)):
    f0, f1 = int(f0), int(f1)
    if f1 <= f0:
        f1 = f0 + 1
    c = _vec3(center)
    N = max(1, int(count))
    rg = _rng(seed, "embers%d" % int(bool(falling)))
    fx = _FX("embers", f0 - 1, f1)
    F = fx.F
    cls = rg.choice(3, N, p=[0.5, 0.36, 0.14])
    size = np.choose(cls, [rg.uniform(0.006, 0.010, N), rg.uniform(0.010, 0.017, N), rg.uniform(0.018, 0.028, N)])
    bright = np.choose(cls, [rg.uniform(0.5, 0.75, N), rg.uniform(0.7, 0.95, N), rg.uniform(0.9, 1.2, N)])
    rmul = np.choose(cls, [np.full(N, 1.4), np.full(N, 1.0), np.full(N, 0.75)])
    if falling:
        vz = -rg.uniform(0.008, 0.02, N)
        period = rg.uniform(70, 150, N)
        sway = rg.uniform(0.25, 0.7, N)
    else:
        vz = rg.uniform(0.016, 0.042, N) * np.choose(cls, [np.full(N, 1.15), np.full(N, 1.0), np.full(N, 0.8)])
        period = rg.uniform(50, 105, N)
        sway = rg.uniform(0.15, 0.45, N)
    sfreq = rg.uniform(0.012, 0.03, N)
    pos, ps = _drift(rg, N, c, radius, height, vz, period, sway, sfreq, rmul, band=0.55, wind=wind)
    P, a = pos(F)
    vel = _vel(pos, F)
    env = _ss(0.0, 0.1, a) * (1 - _ss(0.62, 1.0, a))
    tt = F[:, None]
    flick = 0.62 + 0.38 * _vn(tt * 0.42, ps + 5)
    pop = (_hash(tt.astype(np.int64) * 7 + np.arange(N), ps + 77) > 0.985) * 0.5
    cool = 1 - (0.5 if falling else 0.35) * a
    win = _window(F, f0, f1)
    heat = env * (flick + pop) * cool * bright * (0.8 if falling else 1.0) * win
    spd = np.linalg.norm(vel, axis=-1)
    sz = size * (0.35 + 0.65 * env) * win
    scl = np.stack([sz, sz, sz + spd * 0.75 * win], -1)
    Vt, Ft = _uv_sphere(6, 4)
    fx.add_tiled(Vt, Ft, P, rot=_align_euler(vel), scl=scl, heat=heat)
    sname = "%s_%.2f" % (color, strength)
    mat = glow_mat("ember_" + sname, color, strength=28.0 * strength, soft=1.1)
    ob = fx.build([mat])
    h = _handles(ob, [ob], mats={"ember": mat}, frames=(fx.fa, fx.fb))
    if cam is not None and near > 0:
        lens = _near_lens(cam, f0, f1, rg, falling, color, strength, int(near))
        h["near"] = lens
        h["objects"].append(lens)
    return h


def _near_lens(cam, f0, f1, rg, falling, color, strength, n):
    camob = getattr(cam, "cam", cam)
    cd = camob.data
    sc = bpy.context.scene
    rw, rh = sc.render.resolution_x, sc.render.resolution_y
    if cd.sensor_fit == "VERTICAL":
        tv = cd.sensor_height / 2 / cd.lens
    elif cd.sensor_fit == "HORIZONTAL" or rw >= rh:
        tv = cd.sensor_width / 2 / cd.lens * rh / rw
    else:
        tv = cd.sensor_width / 2 / cd.lens
    th = tv * rw / rh
    fx = _FX("embers_lens", f0 - 1, f1)
    F = fx.F
    depth = rg.uniform(0.35, 1.1, n)
    period = rg.uniform(80, 150, n)
    phase = rg.uniform(0, 1, n)
    ps = rg.integers(1, 2 ** 30, n)

    def pos(t):
        tt = np.asarray(t, float)[:, None]
        x = tt / period + phase
        cyc = np.floor(x)
        a = x - cyc
        hx = _hash(cyc.astype(np.int64), ps)
        X = depth * th * (hx * 1.5 - 0.75) + 0.04 * depth * _vn(tt * 0.02, ps + 3)
        yy = (0.85 - 1.7 * a) if falling else (-0.85 + 1.7 * a)
        Y = depth * tv * yy + 0.03 * depth * _vn(tt * 0.025, ps + 9)
        Z = -depth + 0.0 * tt
        return np.stack([X, Y, Z], -1), a
    P, a = pos(F)
    vel = _vel(pos, F, 0.05)
    env = _ss(0.0, 0.15, a) * (1 - _ss(0.75, 1.0, a))
    win = _window(F, f0, f1)
    heat = env * (0.65 + 0.3 * _vn(F[:, None] * 0.35, ps + 5)) * 0.45 * win
    sz = depth * rg.uniform(0.022, 0.04, n) * (0.6 + 0.4 * env) * win
    spd = np.linalg.norm(vel, axis=-1)
    scl = np.stack([sz, sz, sz + spd * 0.3], -1)
    Vt, Ft = _uv_sphere(16, 8)
    fx.add_tiled(Vt, Ft, P, rot=_align_euler(vel), scl=scl, heat=heat)
    mat = glow_mat("ember_lens_%s_%.2f" % (color, strength), color, strength=6.0 * strength, soft=0.9, heat_pow=1.0)
    return fx.build([mat], parent=camob)


# ===================================================================== ash
def ash(f0, f1, center, radius=4.0, height=4.0, count=220, seed=0, color=(0.55, 0.55, 0.55), rise=0.3):
    f0, f1 = int(f0), int(f1)
    if f1 <= f0:
        f1 = f0 + 1
    c = _vec3(center)
    N = max(1, int(count))
    rg = _rng(seed, "ash")
    fx = _FX("ash", f0 - 1, f1)
    F = fx.F
    vz = float(rise) / FPS * rg.uniform(0.6, 1.4, N)
    period = rg.uniform(60, 140, N)
    pos, ps = _drift(rg, N, c, radius, height, vz, period, rg.uniform(0.25, 0.6, N), rg.uniform(0.01, 0.025, N),
                     band=0.7)
    P, a = pos(F)
    env = _ss(0.0, 0.15, a) * (1 - _ss(0.82, 1.0, a)) * _window(F, f0, f1)
    size = np.exp(rg.uniform(np.log(0.008), np.log(0.026), N))
    shape = np.stack([np.ones(N), rg.uniform(0.45, 1.0, N), np.ones(N)], -1)
    scl = (size[None, :, None] * shape[None]) * env[..., None]
    rot0 = rg.uniform(0, 2 * math.pi, (N, 3))
    spin = rg.uniform(-0.12, 0.12, (N, 3))
    tt = F[:, None, None]
    rot = rot0[None] + spin[None] * tt + 0.6 * _vn(tt * 0.05, ps[None, :, None] + np.arange(3))
    tint = rg.uniform(0.0, 1.0, N)
    Vt, Ft = _flake(rg)
    fx.add_tiled(Vt, Ft, P, rot=rot, scl=scl, heat=np.broadcast_to(tint, (fx.NF, N)))
    col = tuple(float(x) for x in (color if not isinstance(color, str) else C.hexcol(color))[:3])
    mat = flake_mat("ash_%.3f_%.3f_%.3f" % col, col, translucent=0.3, rough=0.9,
                    tint2=tuple(np.array(col) * 0.35))
    ob = fx.build([mat])
    return _handles(ob, [ob], mats={"ash": mat}, frames=(fx.fa, fx.fb))


# ===================================================================== dust puff
def dust_puff(frame, loc, seed=0, scale=1.0, floor=None, color=(0.42, 0.38, 0.33), opacity=1.0, grit=True):
    f = int(frame)
    s = float(scale)
    L = _vec3(loc)
    fl = _floor(floor, L) if floor is not None or L[2] < 0.3 else float(L[2])
    rg = _rng(seed, "dust")
    fx = _FX("dust", f - 1, f + 30)
    F = fx.F
    a = (F - f)[:, None]
    N = 30
    ring = np.arange(N) < 22
    th = 2 * math.pi * np.arange(N) / 22 + rg.uniform(-0.2, 0.2, N)
    th = np.where(ring, th, rg.uniform(0, 2 * math.pi, N))
    dmax = s * np.where(ring, rg.uniform(0.45, 0.8, N), rg.uniform(0.08, 0.3, N))
    rr = s * 0.08 + dmax * _eo(a / rg.uniform(10, 15, N))
    rise = rg.uniform(0.6, 1.3, N)
    z = fl + s * (0.03 + 0.15 * rise * _eo(a / 18.0))
    P = np.stack([L[0] + rr * np.cos(th), L[1] + rr * np.sin(th), np.broadcast_to(z, rr.shape)], -1)
    rad = s * rg.uniform(0.6, 1.2, N) * (0.05 + 0.18 * _eo(a / 16.0)) * (a >= 0)
    flat = np.stack([rad, rad * 0.8, rad * 0.5], -1)
    alpha = rg.uniform(0.4, 0.65, N) * _ss(-0.5, 2.0, a) * (1 - _ss(4.0, 20.0, a)) * opacity
    rot = rg.uniform(0, 2 * math.pi, (N, 3))[None] + 0.03 * a[..., None]
    Vt, Ft = _uv_sphere(10, 6)
    fx.add_tiled(Vt, Ft, P, rot=rot, scl=flat, alpha=alpha)
    mat = soft_mat("dust_%.2f_%.2f_%.2f_%.2f" % (tuple(color) + (s,)), color, soft=2.0, noise=1.0, nscale=7.0 / max(s, 0.3),
                   nspeed=0.8)
    mats = [mat]
    if grit:
        G = 18
        az = rg.uniform(0, 2 * math.pi, G)
        hs = rg.uniform(0.6, 2.0, G) * math.sqrt(s)
        v0 = np.stack([np.cos(az) * hs, np.sin(az) * hs, rg.uniform(0.8, 2.2, G) * math.sqrt(s)], -1)
        gr = s * rg.uniform(0.004, 0.011, G)
        p0 = np.stack([L[0] + np.cos(az) * 0.08 * s, L[1] + np.sin(az) * 0.08 * s, np.full(G, fl + 0.02)], -1)
        Pg, _, Rg, _ = _ballistic(p0, v0, rg.normal(0, 15, (G, 3)), fx.NF - 2, floor=fl, radius=gr * 0.6,
                                  rest=0.25, fric=0.6)
        Pg = np.concatenate([p0[None], Pg], 0)
        Rg = np.concatenate([np.zeros((1, G, 3)), Rg], 0)
        on = (F >= f)[:, None]
        Vg, Fg = _ico(0)
        jit = rg.uniform(0.7, 1.2, len(Vg))[:, None]
        fx.add_tiled(Vg * jit, Fg, Pg, rot=Rg, size=gr[None] * on, heat=0.0, mat=1)
        mats.append(debris_mat("rock"))
    ob = fx.build(mats)
    return _handles(ob, [ob], mats={"dust": mat}, frames=(fx.fa, fx.fb))


# ===================================================================== ballistic sim
def _ballistic(p0, v0, w0, n, ts=1.0, g=9.81, drag=0.0, floor=0.0, rest=0.3, fric=0.8, radius=None, sub=4,
               spin_damp=0.6):
    """Fixed-step ballistic integration (m, m/s, rad/s). Returns per-frame arrays (n+1, N, 3) for
    positions, velocities (m/s), euler rotations and (n+1, N) floor-contact flags; index 0 = start."""
    N = len(p0)
    dt = ts / FPS / sub
    p = np.array(p0, float)
    v = np.array(v0, float)
    w = np.array(w0, float)
    r = np.zeros((N, 3))
    rad = np.zeros(N) if radius is None else np.broadcast_to(np.asarray(radius, float), (N,))
    hit = np.zeros(N, bool)
    Ps, Vs, Rs, Hs = [p.copy()], [v.copy()], [r.copy()], [hit.copy()]
    for _ in range(n):
        for _ in range(sub):
            v[:, 2] -= g * dt
            v *= max(0.0, 1.0 - drag * dt)
            p += v * dt
            r += w * dt
            low = p[:, 2] - rad < floor
            if low.any():
                p[low, 2] = floor + rad[low]
                vz = v[low, 2]
                v[low, 2] = np.where(vz < 0, -vz * rest, vz)
                v[low, :2] *= fric
                w[low] *= spin_damp
                slow = low & (np.abs(v[:, 2]) < 0.35)
                v[slow, 2] = 0.0
                hit |= low
        Ps.append(p.copy())
        Vs.append(v.copy())
        Rs.append(r.copy())
        Hs.append(hit.copy())
    return np.array(Ps), np.array(Vs), np.array(Rs), np.array(Hs)


# ===================================================================== sparks
def sparks(frame, loc, seed=0, scale=1.0, direction=None, count=None, color=SPARK, time_scale=1.0, gravity=9.81,
           speed=(2.5, 8.5), life=(6.0, 16.0), floor=None, flash=True, light=True, strength=1.0, drag=0.6):
    f = int(frame)
    s = float(scale)
    ts = max(0.05, float(time_scale))
    L = _vec3(loc)
    fl = _floor(floor, L)
    rg = _rng(seed, "sparks")
    N = int(count) if count else int(np.clip(70 * s, 24, 220))
    life_f = rg.uniform(life[0], life[1], N) / ts
    nfr = int(math.ceil(life_f.max())) + 2
    fx = _FX("sparks", f - 1, f + nfr)
    F = fx.F
    g = rg.normal(size=(N, 3))
    if direction is None:
        g[:, 2] = np.abs(g[:, 2]) * 0.9 + 0.35
    else:
        d = _unit(_vec3(direction))
        g = d[None] * 1.6 + g * 0.55
    dirs = _unit(g)
    sp = rg.uniform(speed[0], speed[1], N) * math.sqrt(s)
    blob = rg.random(N) < 0.12
    sp = np.where(blob, sp * 0.45, sp)
    p0 = L[None] + rg.normal(0, 0.015 * s, (N, 3))
    Pw, Vw, _, hit = _ballistic(p0, dirs * sp[:, None], np.zeros((N, 3)), nfr, ts=ts, g=gravity, drag=drag,
                                floor=fl, rest=0.35, fric=0.9, radius=0.003)
    P = np.concatenate([p0[None], Pw], 0)
    Vv = np.concatenate([Vw[:1], Vw], 0)
    hit = np.concatenate([hit[:1], hit], 0)
    a = (F - f)[:, None]
    alive = (a >= 0) & (a < life_f[None])
    x = np.clip(a / life_f[None], 0, 1)
    heat = 1.25 * (1 - x) ** 1.5 * np.where(hit, 0.7, 1.0) * (0.8 + 0.2 * _hash(F[:, None].astype(np.int64) * 31 +
                                                                                 np.arange(N), seed))
    heat = heat * alive
    r = math.sqrt(s) * rg.uniform(0.0035, 0.006, N) * np.where(blob, 2.2, 1.0)
    dfr = np.linalg.norm(Vv, axis=-1) * ts / FPS
    rr = r[None] * alive * (0.6 + 0.4 * (1 - x))
    scl = np.stack([rr, rr, rr + dfr * 0.8 * alive], -1)
    Vt, Ft = _uv_sphere(6, 4)
    fx.add_tiled(Vt, Ft, P, rot=_align_euler(Vv), scl=scl, heat=heat)
    sname = "%s_%.2f" % (color, strength)
    mats = [glow_mat("spark_" + sname, color, strength=20.0 * strength, soft=0.9)]
    if flash:
        af = (F - f) / ts
        fh = 2.2 * np.clip(1 - af / 3.0, 0, 1) ** 2 * (af >= 0)
        fr = s * (0.1 + 0.16 * _eo(af / 2.0)) * (fh > 0)
        Vs, Fs = _uv_sphere(12, 8)
        fx.add(Vs, Fs, L[None, None] + 0 * F[:, None, None], size=fr[:, None], heat=fh[:, None], mat=1)
        mats.append(glow_mat("spark_flash_" + sname, color, strength=7.0 * strength, soft=2.4))
    ob = fx.build(mats)
    lights = []
    if light:
        lf = np.arange(f, f + int(6 / ts) + 1)
        e = 260.0 * s * strength * np.clip(1 - (lf - f) / (6.0 / ts), 0, 1) ** 2
        lights.append(_light("spark_light", color, lf, e, loc=L + np.array([0, 0, 0.05]), size=0.1, volume=0.6))
    return _handles(ob, [ob], lights, mats={"spark": mats[0]}, frames=(fx.fa, fx.fb))


# ===================================================================== shockwave
def shockwave(frame, loc, seed=0, scale=1.0, floor=None, dust=True, color=EMBER, strength=1.0):
    f = int(frame)
    s = float(scale)
    L = _vec3(loc)
    fl = _floor(floor, L)
    rg = _rng(seed, "shock")
    fx = _FX("shockwave", f - 1, f + 18)
    F = fx.F
    a = F - f
    on = (a >= 0).astype(float)
    Va, Fa, va = _annulus(128, 4, 0.82, 1.0)
    # floor ring (leading edge bright), slightly irregular via noise in the material
    R1 = s * (0.25 + 4.4 * _eo(a / 12.0)) * on
    h1 = 1.1 * (1 - _ss(0, 13, a)) ** 1.5 * on
    fx.add(Va, Fa, np.array([L[0], L[1], fl + 0.02])[None, None] + 0 * F[:, None, None],
           rot=np.array([0, 0, rg.uniform(0, 6.28)]), scl=np.stack([R1, R1, R1], -1)[:, None], heat=h1[:, None],
           v=va, mat=0)
    # air ring, thinner and faster
    Vb, Fb, vb = _annulus(128, 3, 0.9, 1.0)
    R2 = s * (0.3 + 6.0 * _eo(a / 8.0)) * on
    h2 = 0.5 * (1 - _ss(0, 9, a)) ** 2 * on
    zr = max(L[2], fl + 0.45 * s)
    fx.add(Vb, Fb, np.array([L[0], L[1], zr])[None, None] + 0 * F[:, None, None],
           scl=np.stack([R2, R2, R2], -1)[:, None], heat=h2[:, None], v=vb, mat=0)
    # dome flash
    Vs, Fs = _uv_sphere(16, 10)
    rd = s * (0.15 + 0.5 * _eo(a / 4.0)) * on
    hd = 1.6 * np.clip(1 - a / 6.0, 0, 1) ** 2 * on
    fx.add(Vs, Fs, np.array([L[0], L[1], fl])[None, None] + 0 * F[:, None, None],
           scl=np.stack([rd, rd, rd * 0.7], -1)[:, None], heat=hd[:, None], mat=1)
    ring = glow_mat("shock_ring_%s_%.2f" % (color, strength), color, strength=7.0 * strength, profile="v",
                    stops=[(0.0, (0, 0, 0)), (0.72, (1, 1, 1)), (1.0, (0, 0, 0))], noise=0.95,
                    nscale=1.6 / max(s, 0.3), nspeed=2.0, cull=False)
    dome = glow_mat("shock_dome_%s_%.2f" % (color, strength), color, strength=8.0 * strength, soft=2.2)
    ob = fx.build([ring, dome])
    lf = np.arange(f, f + 10)
    e = 750.0 * s * strength * np.clip(1 - (lf - f) / 9.0, 0, 1) ** 2
    lt = _light("shock_light", "#FFB070", lf, e, loc=(L[0], L[1], fl + 0.5 * s), size=0.4, volume=0.8)
    h = _handles(ob, [ob], [lt], mats={"ring": ring, "dome": dome}, frames=(fx.fa, fx.fb))
    if dust:
        _merge(h, dust_puff(f, (L[0], L[1], fl), seed=seed + 1, scale=2.2 * s, floor=fl, opacity=0.8, grit=False))
    return h


# ===================================================================== debris
def debris(frame, loc, seed=0, scale=1.0, count=None, kind="rock", floor=None, dust=True):
    f = int(frame)
    s = float(scale)
    L = _vec3(loc)
    fl = _floor(floor, L)
    kind = "bone" if kind == "bone" else "rock"
    rg = _rng(seed, "debris_" + kind)
    N = int(count) if count else int(np.clip(28 * s, 8, 140))
    nfr = 80
    fx = _FX("debris_" + kind, f - 1, f + nfr)
    F = fx.F
    size = s * np.exp(rg.uniform(math.log(0.014), math.log(0.13 if kind == "rock" else 0.11), N))
    Vi, Fi = _ico(1)
    Vs, rad = [], []
    for i in range(N):
        jit = rg.uniform(0.72, 1.15, len(Vi))[:, None]
        if kind == "bone":
            sh = np.array([rg.uniform(0.16, 0.28), rg.uniform(0.2, 0.34), 1.0]) * 1.4
        else:
            sh = np.array([1.0, rg.uniform(0.6, 1.0), rg.uniform(0.45, 0.8)])
        v = Vi * jit * sh * size[i]
        Vs.append(v)
        rad.append(float(np.abs(v).max(0).mean()) * 0.7)
    rad = np.array(rad)
    az = rg.uniform(0, 2 * math.pi, N)
    airborne = L[2] - fl > 0.5
    hs = rg.uniform(1.0, 3.8, N) * math.sqrt(s)
    vz = (rg.uniform(-1.0, 4.0, N) if airborne else rg.uniform(2.0, 6.5, N)) * math.sqrt(s)
    v0 = np.stack([np.cos(az) * hs, np.sin(az) * hs, vz], -1)
    p0 = L[None] + rg.normal(0, 0.06 * s, (N, 3))
    p0[:, 2] = np.maximum(p0[:, 2], fl + rad)
    P, _, R, _ = _ballistic(p0, v0, rg.normal(0, 13, (N, 3)), nfr, drag=0.15, floor=fl, rest=0.28, fric=0.62,
                            radius=rad, spin_damp=0.55)
    P = np.concatenate([p0[None], P], 0)
    R = np.concatenate([R[:1], R], 0)
    on = (F >= f).astype(float)[:, None]
    if kind == "rock":
        hot = (rg.random(N) < 0.3) * rg.uniform(0.4, 0.9, N)
        heat = hot[None] * np.exp(-np.clip(F - f, 0, None)[:, None] / 18.0) * on
    else:
        heat = 0.0 * on
    V = np.concatenate(Vs)
    faces = _fgroups(Fi)[3]
    allf = np.concatenate([faces + i * len(Vi) for i in range(N)])
    fx.add(V, {3: allf}, P, rot=R, size=on, heat=heat, vpid=np.repeat(np.arange(N), len(Vi)))
    mat = debris_mat(kind)
    ob = fx.build([mat])
    h = _handles(ob, [ob], mats={"debris": mat}, frames=(fx.fa, fx.fb))
    if dust and not airborne and kind == "rock":
        _merge(h, dust_puff(f, (L[0], L[1], fl), seed=seed + 1, scale=1.3 * s, floor=fl, grit=False))
    return h


# ===================================================================== smoke burst
def smoke_burst(frame, loc, seed=0, scale=1.0, color="#1A1220", glow="#A04DFF", strength=1.0):
    f = int(frame)
    s = float(scale)
    L = _vec3(loc)
    rg = _rng(seed, "smoke")
    fx = _FX("smoke", f - 1, f + 34)
    F = fx.F
    a = (F - f)[:, None]
    on = (a >= 0)
    N = 26
    d = rg.normal(size=(N, 3))
    d[:, 2] = d[:, 2] * 0.7 + 0.2
    d = _unit(d)
    reach = rg.uniform(0.45, 1.0, N)
    ps = rg.integers(1, 2 ** 30, N)
    dist = s * (0.06 + 0.9 * reach * _eo(a / 13.0))
    tur = 0.08 * s * np.stack([_vn(a * 0.15, ps), _vn(a * 0.15, ps + 1), _vn(a * 0.15, ps + 2)], -1)
    P = L[None, None] + d[None] * dist[..., None] + tur * on[..., None]
    P[..., 2] += 0.014 * s * np.clip(a, 0, None)
    rad = s * rg.uniform(0.14, 0.24, N) * (0.6 + 2.3 * _eo(a / 16.0)) * on
    alpha = rg.uniform(0.6, 0.9, N) * _ss(-0.5, 1.5, a) * (1 - _ss(5.0, 22.0, a))
    heat = 1.6 * np.exp(-np.clip(a, 0, None) / 4.0) * (1.3 - 0.9 * reach) * on
    rot = rg.uniform(0, 6.28, (N, 3))[None] + 0.04 * a[..., None]
    Vt, Ft = _uv_sphere(12, 8)
    fx.add_tiled(Vt, Ft, P, rot=rot, size=rad, heat=heat, alpha=alpha, mat=0)
    # glowing core
    ac = F - f
    rc = s * (0.1 + 0.14 * _eo(ac / 3.0)) * (1 - _ss(5.0, 11.0, ac)) * (ac >= 0)
    hc = 1.5 * (1 - _ss(0, 11, ac)) ** 1.3 * (ac >= 0)
    Vs, Fs = _uv_sphere(14, 9)
    fx.add(Vs, Fs, L[None, None] + 0 * F[:, None, None], size=rc[:, None], heat=hc[:, None], mat=1)
    smoke = soft_mat("smoke_%s_%s_%.2f" % (color, glow, s), color, glow=glow, glow_strength=7.0 * strength, soft=1.6,
                     noise=0.95, nscale=5.0 / max(s, 0.3), nspeed=1.2)
    core = glow_mat("smoke_core_%s" % glow, glow, hot=_lighten(glow, 0.75), strength=9.0 * strength, soft=2.0,
                    noise=0.5, nscale=4.0, nspeed=2.0)
    ob = fx.build([smoke, core])
    lf = np.arange(f, f + 14)
    lt = _light("smoke_light", glow, lf, 380.0 * s * strength * np.clip(1 - (lf - f) / 13.0, 0, 1) ** 2, loc=L,
                size=0.3, volume=0.7)
    h = _handles(ob, [ob], [lt], mats={"smoke": smoke, "core": core}, frames=(fx.fa, fx.fb))
    _merge(h, sparks(f, L, seed=seed + 7, scale=0.7 * s, color=glow, gravity=-0.6, speed=(1.2, 4.0),
                     life=(10, 22), count=int(36 * max(s, 0.5)), flash=False, light=False, drag=2.5))
    return h


# ===================================================================== fireball
def fireball(frame, start, end, seed=0, scale=1.0, travel=6, floor=None, color=FIRE, strength=1.0):
    fl_ = int(frame)
    s = float(scale)
    travel = max(1, int(travel))
    fh = fl_ + travel
    S, E = _vec3(start), _vec3(end)
    flz = _floor(floor, E)
    rg = _rng(seed, "fireball")
    fx = _FX("fireball", fl_ - 6, fh + 36)
    F = fx.F
    D = E - S
    dirn = _unit(D)
    wseed = int(rg.integers(1, 2 ** 30))

    def ball(t):
        t = np.asarray(t, float)
        u = np.clip((t - fl_) / travel, 0, 1)
        base = S[None] + D[None] * (u ** 1.1)[:, None]
        wob = 0.05 * s * np.sin(math.pi * u)[:, None] * np.stack([_vn(t * 0.4, wseed + k) for k in range(3)], -1)
        return base + wob
    B = ball(F)
    a = F - fl_
    vis = (a >= -4) & (F < fh)
    charge = np.clip((a + 4) / 4.0, 0, 1)
    Vs, Fs = _uv_sphere(14, 9)
    # core
    rc = s * (0.03 + 0.10 * charge) * (1 + 0.1 * np.sin(F * 2.1)) * vis
    hc = (0.5 + 1.1 * charge) * vis
    fx.add(Vs, Fs, B[:, None], size=rc[:, None], heat=hc[:, None], mat=1)
    # turbulent flame layer orbiting the core
    K = 10
    od = _unit(rg.normal(size=(K, 3)))
    ax = _unit(rg.normal(size=(K, 3)))
    om = rg.uniform(0.25, 0.5, K)
    ang = om[None] * F[:, None]
    ca, sa = np.cos(ang)[..., None], np.sin(ang)[..., None]
    rot_off = od[None] * ca + np.cross(ax, od)[None] * sa + ax[None] * (ax * od).sum(1)[None, :, None] * (1 - ca)
    Pk = B[:, None] + rot_off * (s * 0.1)
    rk = s * rg.uniform(0.12, 0.2, K)[None] * (0.3 + 0.7 * charge[:, None]) * vis[:, None]
    hk = rg.uniform(0.7, 1.0, K)[None] * vis[:, None] * (0.6 + 0.4 * charge[:, None])
    fx.add_tiled(Vs, Fs, Pk, size=rk, heat=hk, rot=rg.uniform(0, 6.28, (K, 3)), mat=0)
    # halo
    fx.add(Vs, Fs, B[:, None], size=(s * 0.45 * (0.4 + 0.6 * charge) * vis)[:, None],
           heat=(0.55 * vis * (0.5 + 0.5 * charge))[:, None], mat=2)
    # trail puffs
    T = travel * 5
    tb = fl_ + np.arange(T) / 5.0
    pb = ball(tb) + rg.normal(0, 0.04 * s, (T, 3))
    lifep = rg.uniform(7, 11, T)
    ag = F[:, None] - tb[None]
    alive = (ag >= 0) & (ag < lifep[None])
    drift = (-dirn * 0.012 * s + np.array([0, 0, 0.01 * s]))[None, None] * np.clip(ag, 0, None)[..., None]
    Pt = pb[None] + drift
    rt = s * rg.uniform(0.8, 1.2, T)[None] * (0.09 + 0.2 * _eo(ag / lifep[None])) * alive
    ht = 0.95 * np.clip(1 - ag / lifep[None], 0, 1) ** 1.6 * alive
    fx.add_tiled(Vs, Fs, Pt, size=rt, heat=ht, rot=rg.uniform(0, 6.28, (T, 3)), mat=0)
    # explosion
    X = 40
    dx = rg.normal(size=(X, 3))
    dx[:, 2] = np.abs(dx[:, 2]) * 0.5 + dx[:, 2] * 0.5 + 0.25
    dx = _unit(dx)
    spd = rg.uniform(0.45, 1.0, X)
    lx = rg.uniform(10, 18, X)
    ae = (F - fh)[:, None]
    onx = (ae >= 0)
    Px = E[None, None] + dx[None] * (s * (0.12 + 1.25 * spd[None] * _eo(ae / 9.0)))[..., None]
    Px[..., 2] += 0.02 * s * np.clip(ae, 0, None)
    if E[2] - flz < 1.0:
        Px[..., 2] = np.maximum(Px[..., 2], flz + 0.15 * s)
    rx = s * rg.uniform(0.14, 0.4, X)[None] * (0.55 + 1.7 * _eo(ae / 10.0)) * onx * (ae < lx[None])
    hx = 1.05 * (1 - _ss(0, 1, ae / lx[None])) ** 1.3 * onx
    fx.add_tiled(Vs, Fs, Px, size=rx, heat=hx, rot=rg.uniform(0, 6.28, (X, 3)), mat=0)
    af = F - fh
    rfl = s * (0.2 + 0.5 * _eo(af / 3.0)) * (af >= 0) * (af < 6)
    hfl = 1.1 * np.clip(1 - af / 5.5, 0, 1) ** 2 * (af >= 0)
    fx.add(Vs, Fs, E[None, None] + 0 * F[:, None, None], size=rfl[:, None], heat=hfl[:, None], mat=3)
    fire = glow_mat("fire_%s_%.2f_%.2f" % (color, s, strength), color, strength=5.0 * strength, hot="#FFE7A8",
                    soft=1.25, noise=0.95, nscale=2.8 / max(s, 0.3), nspeed=1.8)
    core = glow_mat("fire_core_%.2f" % strength, "#FFB040", strength=16.0 * strength, hot=WHITE_HOT, soft=1.2)
    halo = glow_mat("fire_halo_%s_%.2f" % (color, strength), color, strength=1.5 * strength, soft=3.0)
    flash = glow_mat("fire_flash_%.2f" % strength, "#FFA040", strength=7.0 * strength, hot=WHITE_HOT, soft=2.6)
    ob = fx.build([fire, core, halo, flash])
    # smoke after the blast
    fs = _FX("fireball_smoke", fh - 1, fh + 40)
    Fm = fs.F
    am = (Fm - fh)[:, None]
    Q = 14
    dq = _unit(rg.normal(size=(Q, 3)) + np.array([0, 0, 0.6]))
    Pq = E[None, None] + dq[None] * (s * (0.3 + 0.9 * _eo(am / 14.0)))[..., None]
    Pq[..., 2] += 0.03 * s * np.clip(am, 0, None)
    rq = s * rg.uniform(0.3, 0.45, Q)[None] * (0.6 + 1.4 * _eo(am / 20.0)) * (am >= 2)
    aq = 0.6 * _ss(2, 7, am) * (1 - _ss(16, 38, am))
    fs.add_tiled(Vs, Fs, Pq, size=rq, alpha=aq, heat=1.2 * np.exp(-np.clip(am, 0, None) / 5.0),
                 rot=rg.uniform(0, 6.28, (Q, 3)))
    smat = soft_mat("fire_smoke", "#16110E", glow="#FF5A18", glow_strength=5.0, soft=1.1, noise=0.8,
                    nscale=2.0 / max(s, 0.3))
    obs = fs.build([smat])
    # lights
    lf = np.arange(fl_ - 4, fh + 1)
    fb_ = np.array([0.6 + 0.4 * _vn(np.array([k * 0.9]), wseed + 9)[0] for k in lf])
    e1 = 420.0 * s * strength * np.clip((lf - fl_ + 4) / 4.0, 0, 1) * (0.85 + 0.3 * fb_) * (lf < fh)
    l1 = _light("fireball_light", "#FF7A2A", lf, e1, locs=ball(lf.astype(float)), size=0.15, volume=0.8)
    lx_ = np.arange(fh, fh + 16)
    e2 = 1500.0 * s * strength * np.clip(1 - (lx_ - fh) / 15.0, 0, 1) ** 2 * \
        (0.85 + 0.3 * np.array([_hash(np.array([k]), wseed)[0] for k in lx_]))
    l2 = _light("fireball_blast", "#FF8A3A", lx_, e2, loc=E + np.array([0, 0, 0.25 * s]), size=0.5, volume=0.8)
    h = _handles(ob, [ob, obs], [l1, l2], mats={"fire": fire, "core": core, "halo": halo, "smoke": smat},
                 frames=(fx.fa, fx.fb), smoke=obs, light=l1, blast_light=l2)
    _merge(h, sparks(fh, E, seed=seed + 3, scale=1.3 * s, count=int(90 * max(s, 0.4)), color="#FFA040",
                     speed=(3.0, 11.0), flash=False, light=False, floor=floor))
    if E[2] - flz < 0.8:
        _merge(h, shockwave(fh, (E[0], E[1], flz), seed=seed + 4, scale=0.8 * s, floor=flz))
    return h


# ===================================================================== lightning
def _bolt(a, b, rg, levels=6, disp=0.13):
    pts = [np.array(a, float), np.array(b, float)]
    amp = disp
    for _ in range(levels):
        new = [pts[0]]
        for p, q in zip(pts[:-1], pts[1:]):
            d = q - p
            L2 = max(d @ d, 1e-12)
            r = rg.normal(size=3)
            r -= d * (r @ d) / L2
            new += [(p + q) / 2 + r * math.sqrt(L2) * amp, q]
        pts = new
        amp *= 0.78
    return np.array(pts)


def lightning(frame, start, end, seed=0, scale=1.0, duration=8, color=BOLT_GLOW, core=BOLT_CORE, strength=1.0,
              branches=5, impact_sparks=True):
    f = int(frame)
    s = float(scale)
    dur = max(2, int(duration))
    S = _vec3(start)
    ends = [end] if isinstance(end[0], (int, float)) else list(end)
    ends = [_vec3(e) for e in ends]
    rg = _rng(seed, "lightning")
    slots = [(f - 1, f - 1, True)]
    t = f
    while t < f + dur:
        hold = 1 if rg.random() < 0.55 else 2
        slots.append((t, min(t + hold - 1, f + dur - 1), False))
        t += hold
    fx = _FX("lightning", f - 2, f + dur + 1)
    F = fx.F
    inten = np.zeros(fx.NF)
    for k, fr in enumerate(F):
        if fr == f - 1:
            inten[k] = 0.7
        elif f <= fr < f + dur:
            x = 1.7 if fr <= f + 1 else rg.uniform(0.75, 1.3)
            if fr > f + 1 and rg.random() < 0.15:
                x *= 0.25
            x *= np.clip((f + dur - fr) / 2.5, 0.25, 1.0)
            inten[k] = x
    Vsph, Fsph = _uv_sphere(10, 6)
    for (a0, a1, leader) in slots:
        grp = {0: [[], [], [], 0], 1: [[], [], [], 0], 2: [[], [], [], 0]}

        def put(V, Fc, u, m):
            g = grp[m]
            g[0].append(np.asarray(V))
            g[1].extend([tuple(np.asarray(q) + g[3]) for q in Fc])
            g[2].append(np.asarray(u))
            g[3] += len(V)
        for e in ends:
            main = _bolt(S, e, rg, 6, 0.17)
            if leader:
                main = main[:int(len(main) * 0.55)]
            n = len(main)
            taper = np.linspace(1.0, 0.7, n)
            for rr, m in ((0.011 * s, 0), (0.065 * s, 1)):
                V, Fc, u = _tube(main, rr * taper, 5 if m == 0 else 7)
                put(V, Fc, u, m)
            Lm = np.linalg.norm(e - S)
            nb = int(rg.integers(3, branches + 2))
            for _ in range(nb):
                i0 = int(rg.integers(int(n * 0.1), max(int(n * 0.85), int(n * 0.1) + 1)))
                o = main[i0]
                dd = _unit(_unit(e - S) + rg.normal(0, 0.65, 3))
                br = _bolt(o, o + dd * Lm * rg.uniform(0.1, 0.32), rg, 4, 0.16)
                tp = np.linspace(1.0, 0.25, len(br))
                for rr, m in ((0.006 * s, 0), (0.035 * s, 1)):
                    V, Fc, u = _tube(br, rr * tp, 4 if m == 0 else 6)
                    put(V, Fc, u, m)
                if rg.random() < 0.4:
                    j0 = int(rg.integers(1, len(br) - 1))
                    d2 = _unit(dd + rg.normal(0, 0.7, 3))
                    sb = _bolt(br[j0], br[j0] + d2 * Lm * rg.uniform(0.05, 0.14), rg, 3, 0.18)
                    V, Fc, u = _tube(sb, 0.004 * s * np.linspace(1, 0.2, len(sb)), 4)
                    put(V, Fc, u, 0)
            if not leader:
                put(e + Vsph * 0.16 * s, Fsph, np.zeros(len(Vsph)), 2)
        put(S + Vsph * 0.13 * s, Fsph, np.zeros(len(Vsph)), 2)
        act = ((F >= a0) & (F <= a1)).astype(float)
        heat = inten * act * (0.9 + 0.2 * rg.random())
        for m, g in grp.items():
            if g[3]:
                fx.add(np.concatenate(g[0]), g[1], np.zeros((fx.NF, 1, 3)), size=act[:, None],
                       heat=heat[:, None], u=np.concatenate(g[2]), mat=m)
    ob = fx.build([glow_mat("bolt_core_%.2f" % strength, core, strength=40.0 * strength, hot="#FFFFFF",
                            soft=0.45, deep="#2A4FA0"),
                   glow_mat("bolt_glow_%s_%.2f" % (color, strength), color, strength=4.5 * strength,
                            hot=core, soft=2.2, deep="#0E2350"),
                   glow_mat("bolt_ball_%.2f" % strength, color, strength=4.0 * strength, hot="#FFFFFF",
                            soft=2.6, deep="#0E2350")])
    mid = (S + np.mean(ends, 0)) / 2
    lf = F.astype(int)
    e1 = 750.0 * s * strength * inten
    l1 = _light("bolt_light", core, lf, e1, loc=mid, size=0.5, volume=0.8, specular=0.7)
    l2 = _light("bolt_impact", BOLT_CORE, lf, 650.0 * s * strength * inten * (lf >= f), loc=np.mean(ends, 0) +
                np.array([0, 0, 0.3]), size=0.4, volume=0.6)
    h = _handles(ob, [ob], [l1, l2], mats={}, frames=(fx.fa, fx.fb), slots=slots)
    if impact_sparks:
        for i, e in enumerate(ends):
            _merge(h, sparks(f, e, seed=seed + 10 + i, scale=0.6 * s, color=BOLT_CORE, count=int(40 * max(s, 0.5)),
                             flash=False, light=False))
    return h


# ===================================================================== god attack
def god_attack(frame, origin, target, seed=0, scale=1.0, column=False, height=45.0, floor=None, color=GOLD,
               strength=1.0):
    f = int(frame)
    s = float(scale)
    O = _vec3(origin)
    flz = _floor(floor, O)
    rg = _rng(seed, "god%d" % int(bool(column)))
    fx = _FX("god_attack", f - 8, f + 30)
    F = fx.F
    a = F - f
    Vs, Fs = _uv_sphere(16, 10)
    Vb, Fb, ub = _beam(20, 14)
    # build-up glow at origin -> release flash
    bu = _ss(-6, 0, a)
    pre = (a >= -6) & (a < 0)
    post = a >= 0
    r0 = np.where(pre, s * (0.03 + 0.17 * bu), s * (0.2 + 0.3 * _eo(a / 4.0)) * (a < 9))
    h0 = np.where(pre, 0.4 + 0.9 * bu, 1.25 * (1 - _ss(0, 9, a)))
    fx.add(Vs, Fs, O[None, None] + 0 * F[:, None, None], size=(r0 * (a >= -6))[:, None], heat=h0[:, None], mat=4)
    # converging motes (build-up)
    K = 36
    md = _unit(rg.normal(size=(K, 3)))
    mr0 = s * rg.uniform(0.6, 1.5, K)
    ms = rg.uniform(-6, -3, K)
    sp_ = rg.uniform(1.5, 3.0, K) * rg.choice([-1, 1], K)
    u_ = np.clip((a[:, None] - ms[None]) / (0 - ms[None]), 0, 1)
    rr_ = mr0[None] * (1 - u_ ** 1.6)
    ang = sp_[None] * u_
    perp = _unit(np.cross(md, np.array([0, 0, 1.0])) + 1e-6)
    off = md[None] * np.cos(ang)[..., None] + perp[None] * np.sin(ang)[..., None]
    Pm = O[None, None] + off * rr_[..., None]
    alive = (a[:, None] >= ms[None]) & (a[:, None] < 0)
    vm = np.gradient(Pm, axis=0)
    rm = s * 0.012 * alive
    sm = np.stack([rm, rm, rm + np.linalg.norm(vm, axis=-1) * 0.4 * alive], -1)
    fx.add_tiled(*_uv_sphere(6, 4), Pm, rot=_align_euler(vm), scl=sm, heat=(0.5 + 0.6 * u_) * alive, mat=0)
    lights = []
    gold = glow_mat("god_core_%.2f" % strength, color, strength=12.0 * strength, hot="#FFFFFF", soft=1.4,
                    deep="#8A4A08")
    beam = glow_mat("god_beam_%.2f_%.2f" % (s, strength), color, strength=13.0 * strength, hot="#FFFFFF", soft=1.0,
                    noise=0.55, nscale=1.3 / max(s, 0.3), nspeed=3.0, deep="#8A4A08")
    haze = glow_mat("god_haze_%.2f" % strength, GOLD_DEEP, strength=2.2 * strength, hot=color, soft=2.6,
                    deep="#5A2A04")
    flash = glow_mat("god_flash_%.2f" % strength, color, strength=9.0 * strength, hot="#FFFFFF", soft=2.4,
                     deep="#8A4A08")
    shell = glow_mat("god_shell_%.2f" % strength, color, strength=2.5 * strength, hot="#FFFFFF", soft=4.0,
                     profile="shell", deep="#8A4A08")
    lf = np.arange(f - 6, f + 18)
    al = lf - f
    e_o = np.where(al < 0, 600.0 * _ss(-6, 0, al), 1600.0 * np.clip(1 - al / 12.0, 0, 1) ** 2)
    lights.append(_light("god_origin", color, lf, e_o * s * strength, loc=O, size=0.3, volume=0.8))
    sub = []
    if not column:
        T = _vec3(target)
        Dv = T - O
        Ln = float(np.linalg.norm(Dv))
        rotb = _align_euler(Dv[None])[0]
        ext = _eo((a + 1) / 2.0) * (a >= -1)
        pulse = 1 + 0.8 * np.exp(-np.clip(a, 0, None) / 2.0) * post
        fade = 1 - _ss(5, 15, a)
        for rr, hh, m in ((0.075, 2.1, 1), (0.3, 1.1, 1), (0.95, 0.55, 2)):
            rad = s * rr * pulse * (0.35 + 0.65 * fade) * (a >= -1) * (fade > 0)
            fx.add(Vb, Fb, O[None, None] + 0 * F[:, None, None], rot=rotb,
                   scl=np.stack([rad, rad, Ln * ext], -1)[:, None], heat=(hh * fade * (a >= -1))[:, None], u=ub,
                   mat=m)
        ai = a - 1
        rs = s * (0.3 + 2.4 * _eo(ai / 10.0)) * (ai >= 0) * (ai < 12)
        fx.add(Vs, Fs, T[None, None] + 0 * F[:, None, None], size=rs[:, None],
               heat=(1.5 * (1 - _ss(0, 11, ai)) * (ai >= 0))[:, None], mat=3)
        ri = s * (0.25 + 0.55 * _eo(ai / 4.0)) * (ai >= 0) * (ai < 9)
        fx.add(Vs, Fs, T[None, None] + 0 * F[:, None, None], size=ri[:, None],
               heat=(1.25 * (1 - _ss(0, 8, ai)) * (ai >= 0))[:, None], mat=4)
        lt = np.arange(f + 1, f + 18)
        lights.append(_light("god_flood", color, lt, 5500.0 * s * strength * np.clip(1 - (lt - f - 1) / 15.0, 0, 1)
                             ** 2, loc=T - _unit(Dv) * 0.6, size=1.0, volume=0.3))
        sub.append(sparks(f + 1, T, seed=seed + 3, scale=1.4 * s, color=color, count=int(110 * max(s, 0.4)),
                          speed=(3.0, 12.0), flash=False, light=False, floor=floor))
        sun_dir = _unit(_unit(Dv) + np.array([0, 0, -1.0]))
    else:
        base = np.array([O[0], O[1], flz])
        ext = _eo((a + 1) / 4.0) * (a >= -1)
        pulse = 1 + 0.6 * np.exp(-np.clip(a, 0, None) / 3.0) * post
        fade = 1 - _ss(10, 24, a)
        for rr, hh, m in ((0.12, 1.5, 1), (0.42, 0.7, 1), (1.25, 0.32, 2)):
            rad = s * rr * pulse * (0.4 + 0.6 * fade) * (a >= -1) * (fade > 0)
            fx.add(Vb, Fb, base[None, None] + 0 * F[:, None, None],
                   scl=np.stack([rad, rad, height * ext], -1)[:, None], heat=(hh * fade * (a >= -1))[:, None], u=ub,
                   mat=m)
        rs = s * (0.5 + 3.0 * _eo(a / 9.0)) * post * (a < 14)
        fx.add(Vs, Fs, base[None, None] + 0 * F[:, None, None], scl=np.stack([rs, rs, rs * 0.75], -1)[:, None],
               heat=(1.4 * (1 - _ss(0, 13, a)) * post)[:, None], mat=3)
        Q = 60
        qa = rg.uniform(0, 2 * math.pi, Q)
        qr = s * 0.9 * np.sqrt(rg.uniform(0, 1, Q))
        q0 = rg.uniform(0, 12, Q)
        qv = rg.uniform(0.25, 0.6, Q)
        ql = rg.uniform(8, 16, Q)
        aq = a[:, None] - q0[None]
        aliveq = (aq >= 0) & (aq < ql[None])
        Pq = np.stack([base[0] + qr * np.cos(qa + 0.05 * aq), base[1] + qr * np.sin(qa + 0.05 * aq),
                       base[2] + 0.2 + qv * np.clip(aq, 0, None)], -1)
        rq = s * 0.014 * aliveq
        fx.add_tiled(*_uv_sphere(6, 4), Pq, rot=np.zeros(3), scl=np.stack([rq, rq, rq + qv * 0.7 * aliveq], -1),
                     heat=1.3 * (1 - np.clip(aq / ql[None], 0, 1)) * aliveq, mat=0)
        lt = np.arange(f, f + 22)
        lights.append(_light("god_flood", color, lt, 6000.0 * s * strength * np.clip(1 - (lt - f) / 20.0, 0, 1) ** 2,
                             loc=base + np.array([0, 0, 1.8]), size=1.5, volume=0.3))
        sub.append(shockwave(f, base, seed=seed + 5, scale=1.2 * s, floor=flz, color=GOLD_DEEP))
        sun_dir = np.array([0.2, 0.3, -1.0])
    ob = fx.build([gold, beam, haze, shell, flash])
    ls = np.arange(f, f + 12)
    sun_rot = Vector(tuple(_unit(sun_dir))).to_track_quat("-Z", "Y").to_euler()
    lights.append(_light("god_sun", "#FFF1CF", ls, 0.8 * s * strength * np.clip(1 - (ls - f) / 11.0, 0, 1) ** 2,
                         loc=O + np.array([0, 0, 3.0]), kind="SUN", size=0.1, volume=0.6, rot=sun_rot))
    h = _handles(ob, [ob], lights, mats={"core": gold, "beam": beam, "haze": haze, "shell": shell, "flash": flash},
                 frames=(fx.fa, fx.fb), flood=lights[1], sun=lights[-1])
    for sh in sub:
        _merge(h, sh)
    return h


# ===================================================================== ember trail
def _auto_span(obj, width):
    if obj.type != "MESH":
        return None
    bb = np.array([tuple(c) for c in obj.bound_box])
    lo, hi = bb.min(0), bb.max(0)
    dims = hi - lo
    ax = int(np.argmax(dims))
    if dims[ax] < 6 * width:
        return None
    ctr = (lo + hi) / 2
    e0, e1 = ctr.copy(), ctr.copy()
    e0[ax], e1[ax] = lo[ax], hi[ax]
    tip, other = (e1, e0) if np.linalg.norm(e1) >= np.linalg.norm(e0) else (e0, e1)
    root = tip + (other - tip) * 0.4
    return tuple(root), tuple(tip)


def ember_trail(obj, f0, f1, seed=0, color=EMBER, width=0.08, span=None, offset=(0.0, 0.0, 0.0),
                axis=(0.0, 0.0, 1.0), fade=6, substeps=3, sparks=60, strength=1.0):
    sc = bpy.context.scene
    fcur, fsub = sc.frame_current, sc.frame_subframe
    f0, f1 = int(f0), int(f1)
    if f1 <= f0:
        f1 = f0 + 1
    fade = max(2, int(fade))
    sub = max(1, int(substeps))
    if span is None:
        span = _auto_span(obj, width)
    tsamp = f0 + np.arange((f1 - f0) * sub + 1) / sub
    A, W = [], []
    for t in tsamp:
        fi = int(math.floor(t))
        sc.frame_set(fi, subframe=float(t - fi))
        mw = obj.matrix_world.copy()
        if span is not None:
            pa, pb = mw @ Vector(span[0]), mw @ Vector(span[1])
            A.append(tuple(pa))
            W.append(tuple(pb - pa))
        else:
            A.append(tuple(mw @ Vector(offset)))
            W.append(tuple((mw.to_3x3() @ Vector(axis)).normalized() * width))
    sc.frame_set(fcur, subframe=fsub)
    A, W = np.array(A), np.array(W)
    rg = _rng(seed, "trail")
    Mc = fade * sub + 1
    fx = _FX("ember_trail", f0 - 1, f1 + fade + 1)
    F = fx.F
    j = np.arange(Mc)
    te = F[:, None] - j[None] / sub
    valid = (te >= f0) & (te <= f1)
    idx = np.clip(np.round((te - f0) * sub).astype(int), 0, len(tsamp) - 1)
    P = A[idx]
    Wv = W[idx]
    age = j[None] / (Mc - 1)
    ps = int(rg.integers(1, 2 ** 30))
    heat = (1 - age) ** 1.4 * valid * (0.85 + 0.25 * _vn(te * 0.7, ps)) * 0.85
    wl = np.linalg.norm(Wv, axis=-1)
    if span is not None:
        z0, z1 = 0.0, 1.0
        scl = np.stack([np.ones_like(wl), np.ones_like(wl), wl * valid], -1)
        stops = [(0.0, (0, 0, 0)), (0.55, (0.04, 0.04, 0.04)), (0.86, (0.35, 0.35, 0.35)), (0.96, (1, 1, 1)), (1.0, (0, 0, 0))]
    else:
        z0, z1 = -0.5, 0.5
        sw = wl * (0.45 + 0.55 * (1 - age)) * valid
        scl = np.stack([np.ones_like(wl), np.ones_like(wl), sw], -1)
        stops = [(0.0, (0, 0, 0)), (0.5, (1, 1, 1)), (1.0, (0, 0, 0))]
    Vr = np.zeros((2 * Mc, 3))
    Vr[0::2, 2], Vr[1::2, 2] = z0, z1
    vr = np.tile([0.0, 1.0], Mc)
    ur = np.repeat(j / (Mc - 1), 2)
    Fr = [(2 * k, 2 * k + 1, 2 * k + 3, 2 * k + 2) for k in range(Mc - 1)]
    fx.add(Vr, Fr, P, rot=_align_euler(Wv), scl=scl, heat=heat, vpid=np.repeat(j, 2), u=ur, v=vr, mat=0)
    mats = [glow_mat("trail_%s_%.2f_%d" % (color, strength, int(span is not None)), color, strength=12.0 * strength,
                     profile="v", stops=stops, noise=0.85, nscale=7.0, nspeed=2.0, cull=False)]
    if sparks:
        n = int(sparks)
        spd = np.linalg.norm(np.gradient(A, axis=0), axis=1) * sub
        pr = spd + 1e-6
        pick = rg.choice(len(tsamp), n, p=pr / pr.sum())
        tb = tsamp[pick]
        vfrac = rg.uniform(0.3, 1.0, n) if span is not None else rg.uniform(-0.5, 0.5, n)
        pb = A[pick] + W[pick] * vfrac[:, None]
        vel = np.gradient(A, axis=0)[pick] * sub * 0.25 + rg.normal(0, 0.012, (n, 3))
        life = rg.uniform(8, 18, n)
        ag = F[:, None] - tb[None]
        alive = (ag >= 0) & (ag < life[None])
        k_ = 0.12
        dispf = (1 - np.exp(-k_ * np.clip(ag, 0, None))) / k_
        Pk = pb[None] + vel[None] * dispf[..., None]
        Pk[..., 2] += -0.0012 * np.clip(ag, 0, None) ** 2 + 0.004 * np.clip(ag, 0, None)
        vk = vel[None] * np.exp(-k_ * np.clip(ag, 0, None))[..., None]
        rk = rg.uniform(0.004, 0.008, n)[None] * alive
        hk = 1.3 * np.clip(1 - ag / life[None], 0, 1) ** 1.3 * alive
        sk = np.stack([rk, rk, rk + np.linalg.norm(vk, axis=-1) * 0.8 * alive], -1)
        fx.add_tiled(*_uv_sphere(6, 4), Pk, rot=_align_euler(vk), scl=sk, heat=hk, mat=1)
        mats.append(glow_mat("ember_%s_%.2f" % (color, strength), color, strength=34.0 * strength, soft=1.1))
    ob = fx.build(mats)
    return _handles(ob, [ob], mats={"trail": mats[0]}, frames=(fx.fa, fx.fb), span=span)


# ===================================================================== petals
def petals(f0, f1, center, radius=6.0, height=4.0, count=150, seed=0, colors=("#F6E7EA", "#FFF4DC")):
    f0, f1 = int(f0), int(f1)
    if f1 <= f0:
        f1 = f0 + 1
    c = _vec3(center)
    N = max(1, int(count))
    rg = _rng(seed, "petals")
    fx = _FX("petals", f0 - 1, f1)
    F = fx.F
    vz = -rg.uniform(0.008, 0.017, N)
    period = rg.uniform(110, 190, N)
    pos, ps = _drift(rg, N, c, radius, height, vz, period, rg.uniform(0.4, 1.0, N), rg.uniform(0.01, 0.022, N),
                     band=0.5, wind=(0.004, 0.0))
    P, a = pos(F)
    env = _ss(0.0, 0.06, a) * (1 - _ss(0.92, 1.0, a)) * _window(F, f0, f1)
    size = rg.uniform(0.03, 0.045, N)
    rot0 = rg.uniform(0, 2 * math.pi, (N, 3))
    spin = rg.uniform(-0.15, 0.15, (N, 3))
    tt = F[:, None, None]
    rot = rot0[None] + spin[None] * tt + 0.8 * _vn(tt * 0.06, ps[None, :, None] + np.arange(3))
    Vt, Ft = _petal()
    fx.add_tiled(Vt, Ft, P, rot=rot, size=size[None] * env, heat=np.broadcast_to(rg.uniform(0, 1, N), (fx.NF, N)))
    mat = flake_mat("petal", colors[1], translucent=0.35, rough=0.5, tint2=colors[0], sheen=0.3, sss=0.15)
    ob = fx.build([mat])
    return _handles(ob, [ob], mats={"petal": mat}, frames=(fx.fa, fx.fb))
