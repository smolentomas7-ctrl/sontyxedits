"""THE ENEMIES: six original dark-fantasy enemy designs for montage phases 2 and 5.

Locked designs (assets/characters.md), one silhouette + one glow each:
  skeleton       1.85 m  gaunt human skeleton, ember eye sockets, rusted falchion, tattered loincloth
  ghost          2.0 m   hooded legless wraith, translucent pale blue, trailing wisps, long clawed hands
  bad_angel      2.0 m   gaunt ash-skinned humanoid, broken black feathered wings (~4 m span), cracked red halo
  evil           2.4 m   tall hunched horned shadow, smoke-edged, purple eyes + chest core
  morbidious     2.2 m   bloated hulking mass, small sunk head, glowing toxic-green pustules
  skeleton_king  3.5 m   floor-5 boss: armoured skeleton, broken crown, huge bearded axe, ember eyes

Rig: FK hierarchy of empties exactly like rb_warrior (world-aligned at rest, keyed rotation_euler,
root carries location + heading; heading 0 faces -Y, 180 faces +Y). Axis conventions = rb_motion
(spine +X bends forward, thigh -X lifts the leg, shin +X bends the knee, upperarm -X raises forward,
forearm -X bends the elbow, left abduction -Y / right +Y). Extra joints: jaw (+X opens), weapon (child of
hand_R, the weapon's rest direction is forward -Y), wing_L/R + wing2_L/R (bad angel; -Y/+Y raises the
left/right wing, +Z/-Z folds it back), tail1..3 (ghost robe + wisps).

Pose dicts: {joint: (rx, ry, rz) degrees} plus two optional pseudo-joints
  "_off": (x, y, z) metres: pelvis offset in the root frame (forward = -Y): lunges, recoils, falls
  "_wp":  (pitch, 0, 0): weapon pitch relative to the root (0 = forward, +90 = straight down,
          -90 = straight up, -180 = backward); the weapon joint is solved from it.
Every body material carries CTRL_fade (0 solid .. 1 gone: noise + height dissolve with a glowing edge)
and CTRL_char (ash darkening); glow materials carry CTRL_glow (1 = nominal), listed in Enemy.glow_mats.
Everything is deterministic (seeded) and keyed per frame.
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

import rb_core as C
import rb_mat as M
import rb_mesh as G
from rb_core import hexcol, parent_keep

KINDS = ("skeleton", "ghost", "bad_angel", "evil", "morbidious", "skeleton_king")
GLOW = {"skeleton": "#FF6A1A", "ghost": "#9CC8FF", "bad_angel": "#FF2A2A", "evil": "#A04DFF",
        "morbidious": "#6BFF4A", "skeleton_king": "#FF6A1A"}
HEIGHT = {"skeleton": 1.85, "ghost": 2.0, "bad_angel": 2.0, "evil": 2.4, "morbidious": 2.2, "skeleton_king": 3.5}
SHORT = {"skeleton": "SK", "ghost": "GH", "bad_angel": "BA", "evil": "EV", "morbidious": "MB", "skeleton_king": "KG"}
# impact fraction of each action (u at which the hit / contact / apex lands)
ENEMY_PEAK = {"idle": 0.5, "walk": 0.0, "lunge": 0.55, "attack": 0.6, "raise": 0.7, "dive": 0.65,
              "block": 0.5, "hit": 0.3, "death": 0.6}
ACTIONS = tuple(ENEMY_PEAK)

# ------------------------------------------------------------------ joints (1.85 m human, faces -Y)
_HUMAN = {
    "root": (0, 0, 0), "pelvis": (0, 0.0, 0.97), "spine": (0, 0.01, 1.10), "chest": (0, 0.0, 1.30),
    "neck": (0, 0.03, 1.53), "head": (0, 0.02, 1.64), "jaw": (0, 0.005, 1.71),
    "clav_L": (0.03, 0.0, 1.47), "upperarm_L": (0.175, 0.03, 1.455), "forearm_L": (0.2, 0.045, 1.17),
    "hand_L": (0.22, 0.0, 0.925),
    "thigh_L": (0.088, 0.0, 0.93), "shin_L": (0.098, -0.005, 0.515), "foot_L": (0.103, 0.03, 0.085),
}
for _k in list(_HUMAN):
    if _k.endswith("_L"):
        _x, _y, _z = _HUMAN[_k]
        _HUMAN[_k[:-2] + "_R"] = (-_x, _y, _z)

PARENT = {
    "pelvis": "root", "spine": "pelvis", "chest": "spine", "neck": "chest", "head": "neck", "jaw": "head",
    "clav_L": "chest", "upperarm_L": "clav_L", "forearm_L": "upperarm_L", "hand_L": "forearm_L",
    "clav_R": "chest", "upperarm_R": "clav_R", "forearm_R": "upperarm_R", "hand_R": "forearm_R",
    "weapon": "hand_R",
    "thigh_L": "pelvis", "shin_L": "thigh_L", "foot_L": "shin_L",
    "thigh_R": "pelvis", "shin_R": "thigh_R", "foot_R": "shin_R",
    "wing_L": "chest", "wing2_L": "wing_L", "wing_R": "chest", "wing2_R": "wing_R",
    "tail1": "pelvis", "tail2": "tail1", "tail3": "tail2",
}
ORDER = ["root", "pelvis", "spine", "chest", "neck", "head", "jaw",
         "clav_L", "upperarm_L", "forearm_L", "hand_L", "clav_R", "upperarm_R", "forearm_R", "hand_R", "weapon",
         "thigh_L", "shin_L", "foot_L", "thigh_R", "shin_R", "foot_R",
         "wing_L", "wing2_L", "wing_R", "wing2_R", "tail1", "tail2", "tail3"]
LEGS = ("thigh_L", "shin_L", "foot_L", "thigh_R", "shin_R", "foot_R")
# (uniform scale, width factor, arm length factor) per kind; morbidious has its own skeleton
_SPEC = {"skeleton": (1.0, 0.94, 1.0), "skeleton_king": (1.78, 1.12, 1.0), "ghost": (1.08, 0.95, 1.22),
         "bad_angel": (1.08, 0.9, 1.1), "evil": (1.25, 1.02, 1.3)}


class _Map:
    """Canonical 1.85 m human coordinates -> this kind's rest space."""

    def __init__(self, s, wx=1.0):
        self.s, self.wx = s, wx

    def __call__(self, p):
        return np.array((p[0] * self.s * self.wx, p[1] * self.s, p[2] * self.s), float)


def _joints(kind):
    if kind == "morbidious":
        J = {"root": (0, 0, 0), "pelvis": (0, 0.03, 0.84), "spine": (0, 0.02, 1.02), "chest": (0, 0.0, 1.34),
             "neck": (0, -0.14, 1.70), "head": (0, -0.22, 1.76), "jaw": (0, -0.27, 1.79),
             "clav_L": (0.1, 0.0, 1.62), "upperarm_L": (0.54, 0.04, 1.6), "forearm_L": (0.68, 0.0, 1.17),
             "hand_L": (0.74, -0.06, 0.74), "thigh_L": (0.24, 0.02, 0.8), "shin_L": (0.27, -0.02, 0.44),
             "foot_L": (0.28, 0.03, 0.1)}
        for k in list(J):
            if k.endswith("_L"):
                x, y, z = J[k]
                J[k[:-2] + "_R"] = (-x, y, z)
        return {k: np.array(v, float) for k, v in J.items()}, _Map(1.0, 1.0)
    s, wx, arm = _SPEC[kind]
    T = _Map(s, wx)
    J = {k: T(v) for k, v in _HUMAN.items()}
    for sd in "LR":
        sh = J["upperarm_" + sd]
        for k in ("forearm_", "hand_"):
            J[k + sd] = sh + (J[k + sd] - sh) * arm
    J["weapon"] = J["hand_R"] + np.array((0.0, -0.01, -0.065)) * s * arm
    if kind == "bad_angel":
        for sd, sx in (("L", 1), ("R", -1)):
            J["wing_" + sd] = T((sx * 0.07, 0.11, 1.40))
            J["wing2_" + sd] = J["wing_" + sd] + np.array((sx * 0.78, 0.14, 0.46))
    if kind == "ghost":
        J["tail1"] = T((0, 0.04, 0.86))
        J["tail2"] = T((0, 0.12, 0.55))
        J["tail3"] = T((0, 0.22, 0.30))
    return J, T


def _rig_names(kind):
    names = ["root", "pelvis", "spine", "chest", "neck", "head", "jaw",
             "clav_L", "upperarm_L", "forearm_L", "hand_L", "clav_R", "upperarm_R", "forearm_R", "hand_R"]
    if kind != "ghost":
        names += list(LEGS)
    else:
        names += ["tail1", "tail2", "tail3"]
    if kind in ("skeleton", "skeleton_king"):
        names.append("weapon")
    if kind == "bad_angel":
        names += ["wing_L", "wing2_L", "wing_R", "wing2_R"]
    return [n for n in ORDER if n in names]


def _unique_prefix(prefix):
    p, i = prefix, 1
    while bpy.data.objects.get(p + "root") is not None:
        i += 1
        p = "%s%d_" % (prefix.rstrip("_"), i)
    return p


def _build_rig(prefix, J, names):
    rig = {}
    for n in names:
        p = rig.get(PARENT.get(n))
        e = C.empty(prefix + n, tuple(J[n]), size=0.05)
        if p is not None:
            e.parent = p
            e.matrix_parent_inverse = p.matrix_world.inverted()
            bpy.context.view_layer.update()
        e.rotation_mode = "XYZ"
        rig[n] = e
    return rig


class Enemy:
    """kind, rig {joint: empty}, root, parts [objects], mats {name: material}, glow_mats, height, J (rest joints),
    lights [(light object, base energy)], prefix, seed."""
    shared_mats = False


# ------------------------------------------------------------------ geometry helpers
def _catmull(pts, per=3):
    P = [np.asarray(p, float) for p in pts]
    if len(P) < 3 or per <= 1:
        return np.array(P)
    out, n = [], len(P)
    for i in range(n - 1):
        p0, p1, p2, p3 = P[max(0, i - 1)], P[i], P[i + 1], P[min(n - 1, i + 2)]
        for k in range(per):
            t = k / per
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1])
    return np.array(out)


def _sweep(name, pts, radius, N=8, cap=True, up=(0, 0, 1), per=3):
    """Tube along a Catmull-Rom smoothed polyline (parallel-transport frames).
    radius: float | (ra, rb) | fn(t) -> float | (ra, rb); ra lies along the `up`-ish normal."""
    P = _catmull(pts, per)
    n = len(P)
    Tg = np.gradient(P, axis=0)
    Tg /= np.maximum(np.linalg.norm(Tg, axis=1, keepdims=True), 1e-9)
    u = np.array(up, float)
    nr = u - Tg[0] * np.dot(u, Tg[0])
    if np.linalg.norm(nr) < 1e-4:
        alt = np.array((1.0, 0, 0)) if abs(Tg[0][0]) < 0.9 else np.array((0, 1.0, 0))
        nr = alt - Tg[0] * np.dot(alt, Tg[0])
    nr /= np.linalg.norm(nr)
    ths = np.linspace(0, 2 * math.pi, N, endpoint=False)
    R = np.zeros((n, N, 3))
    for i in range(n):
        q = nr - Tg[i] * np.dot(nr, Tg[i])
        if np.linalg.norm(q) > 1e-6:
            nr = q / np.linalg.norm(q)
        b = np.cross(Tg[i], nr)
        r = radius(i / max(1, n - 1)) if callable(radius) else radius
        ra, rb = (r, r) if np.isscalar(r) else r
        R[i] = P[i] + np.outer(np.cos(ths) * ra, nr) + np.outer(np.sin(ths) * rb, b)
    return G.grid_mesh(name, R, closed_u=True, cap_start=cap, cap_end=cap)


def _weld(ob, d=1e-6):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=d)
    bm.to_mesh(ob.data)
    bm.free()
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def _unit_sphere(M_=11, N_=16):
    th = np.linspace(0, math.pi, M_)[:, None]
    ph = np.linspace(0, 2 * math.pi, N_, endpoint=False)[None, :]
    return np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th) * np.ones_like(ph)], -1)


def _blob(name, c, r, N=16, M_=11, rot=(0, 0, 0), bump=None):
    """Ellipsoid (radii r) at c, rotated by Euler degrees; bump(U) -> (M, N) radial factor."""
    U = _unit_sphere(M_, N)
    P = U * np.array(r if not np.isscalar(r) else (r, r, r), float)
    if bump is not None:
        P = P * bump(U)[..., None]
    Rm = np.array(Euler([math.radians(a) for a in rot], "XYZ").to_matrix())
    P = P @ Rm.T + np.asarray(c, float)
    return _weld(G.grid_mesh(name, P, closed_u=True))


def _bone(name, p0, p1, r, knob=1.7, N=10, M_=12, flat=0.12):
    """Long bone: shaft with knobbly epiphyses and rounded ends."""
    def rad(t, th):
        k = 1 + (knob - 1) * (math.exp(-(t / 0.11) ** 2) + math.exp(-((1 - t) / 0.11) ** 2))
        end = max(0.05, 1 - abs(2 * t - 1) ** 7) ** 0.4
        return r * k * end * (1 + flat * math.cos(2 * th))
    return G.tube(name, p0, p1, rad, N=N, M=M_, cap_start=True, cap_end=True)


def _jitter(ob, amt, seed, scale=6.0):
    """Seeded low-frequency vertex displacement along normals (organic irregularity)."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(6)]
    me = ob.data
    for v in me.vertices:
        p = v.co
        d = (math.sin(p.x * scale + ph[0]) * math.sin(p.y * scale * 1.3 + ph[1]) * math.sin(p.z * scale * 0.9 + ph[2])
             + 0.5 * math.sin(p.x * scale * 2.7 + ph[3]) * math.sin(p.z * scale * 2.3 + ph[4]))
        v.co += v.normal * d * amt
    me.update()
    return ob


def _skin(name, nodes, edges, levels=2):
    """Skin-modifier body part. nodes: [((x, y, z), rx, ry)], edges [(i, j)]."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(n[0]) for n in nodes], edges, [])
    ob = bpy.data.objects.new(name, me)
    C.link(ob)
    sk = ob.modifiers.new("skin", "SKIN")
    sk.use_smooth_shade = True
    sk.branch_smoothing = 0.7
    for i, n in enumerate(nodes):
        me.skin_vertices[0].data[i].radius = (n[1], n[2])
    me.skin_vertices[0].data[0].use_root = True
    sub = ob.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = levels
    G.apply_all(ob)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def _chain(name, pts, radii, levels=2):
    """Skin chain through pts with per-point (rx, ry) radii."""
    nodes = [(p, r[0], r[1]) for p, r in zip(pts, radii)]
    return _skin(name, nodes, [(i, i + 1) for i in range(len(nodes) - 1)], levels)


def _bulge(ob, center, radius, amount, axis=None):
    c = Vector(center)
    for v in ob.data.vertices:
        d = (v.co - c).length / radius
        if d < 2.2:
            v.co += (Vector(axis) if axis is not None else v.normal) * amount * math.exp(-d * d * 1.6)
    ob.data.update()


# ------------------------------------------------------------------ skull
def _skull_shape(U, depth=1.0, flesh=0.0):
    x0, y0, z0 = U[..., 0] * 0.74, U[..., 1] * 0.98, U[..., 2] * 0.86
    wf = np.clip((-y0 - 0.1) / 0.6, 0, 1) * np.clip((0.3 - z0) / 0.7, 0, 1)
    x = x0 * (1 - 0.22 * wf)
    z = z0 - 0.32 * wf * np.clip(0.2 - z0, 0, 1)
    y = y0 - 0.06 * wf
    back = np.clip((y0 + 0.2) / 0.4, 0, 1)
    z = np.where(z < -0.5, -0.5 + (z + 0.5) * (1 - 0.7 * back), z)

    def g(cx, cy, cz, rx, ry, rz):
        return np.exp(-(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2))
    dx, dy, dz = np.zeros_like(x), np.zeros_like(x), np.zeros_like(x)
    for sx in (-1, 1):
        dy += 0.45 * depth * g(0.30 * sx, -0.86, -0.05, 0.19, 0.3, 0.16)          # eye sockets
        dx += sx * 0.07 * (1 + flesh) * g(0.5 * sx, -0.6, -0.3, 0.16, 0.2, 0.12)  # cheekbones
        dx -= sx * 0.07 * (1 - flesh) * g(0.7 * sx, -0.25, 0.0, 0.2, 0.25, 0.22)  # temples
        dy -= 0.06 * g(0.3 * sx, -0.92, 0.2, 0.2, 0.2, 0.07)                      # brow ridge
        dx -= sx * 0.09 * flesh * g(0.48 * sx, -0.5, -0.58, 0.14, 0.25, 0.14)     # gaunt cheek hollows
    dy += 0.34 * depth * g(0.0, -0.9, -0.38, 0.08, 0.25, 0.13)                    # nasal cavity
    dz -= 0.03 * g(0.0, 0.2, 0.86, 0.5, 0.5, 0.2)
    return np.stack([x + dx, y + dy, z + dz], -1)


def _teeth(name, c, L, z, y0, n=10, upper=True):
    obs = []
    for i in range(n):
        x = -0.34 + 0.68 * i / (n - 1)
        zz = z - (0.035 if upper else -0.035)
        obs.append(_blob("%s%d" % (name, i), c + np.array((x, y0 + 1.6 * x * x, zz)) * L,
                         (0.045 * L, 0.04 * L, 0.075 * L), N=8, M_=6))
    return G.join(obs, name)


def _skull(name, c, L, depth=1.0, flesh=0.0, teeth=True):
    """Returns (cranium+face object, mandible object). L = half skull length (~0.1 m for a human)."""
    c = np.asarray(c, float)
    X = _skull_shape(_unit_sphere(26, 36), depth, flesh)
    sk = _weld(G.grid_mesh(name, X * L + c, closed_u=True))
    if teeth:
        sk = G.join([sk, _teeth(name + "_tu", c, L, -0.76, -0.80, upper=True)], name)
    pts = [(0.6, -0.12, -0.32), (0.57, -0.2, -0.76), (0.44, -0.58, -0.9), (0.18, -0.82, -0.96), (0.0, -0.87, -0.97)]
    full = pts + [(-x, y, z) for x, y, z in reversed(pts[:-1])]
    jw = _sweep(name + "_jaw", np.array(full) * L + c, lambda t: 0.055 * L * (1 + 0.35 * math.sin(math.pi * t)),
                N=8, per=3)
    obs = [jw, _blob(name + "_chin", c + np.array((0, -0.84, -0.97)) * L, (0.14 * L, 0.07 * L, 0.08 * L), N=10, M_=7)]
    if teeth:
        obs.append(_teeth(name + "_tl", c, L, -0.88, -0.78, upper=False))
    return sk, G.join(obs, name + "_jaw")


# ================================================================== materials
def _mat(name, blend="CLIP"):
    m, b = M.new(name, blend)
    if blend == "CLIP":
        m.alpha_threshold = 0.5
        m.shadow_method = "CLIP"
    return m, b


def _dissolve(b, H, scale=5.0):
    """CTRL_fade dissolve: noise + rest height (Object coords == rest pose world coords, so the top of the body
    goes first). Returns (alpha, edge mask)."""
    tc = b.n("ShaderNodeTexCoord")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=(tc, "Object"))
    nz = b.n("ShaderNodeTexNoise", Vector=(tc, "Object"), Scale=scale, Detail=6.0, Roughness=0.62)
    zn = b.n("ShaderNodeMapRange", Value=(sep, "Z"), **{"From Min": 0.0, "From Max": H})
    e = b.math("ADD", b.math("MULTIPLY", (nz, "Fac"), 0.62), b.math("MULTIPLY", zn, 0.38))
    fade = b.ctrl("fade", 0.0)
    thr = b.math("SUBTRACT", 1.04, b.math("MULTIPLY", fade, 1.12))
    alpha = b.math("LESS_THAN", e, thr)
    edge = b.math("MULTIPLY", alpha, b.math("GREATER_THAN", e, b.math("SUBTRACT", thr, 0.04)))
    edge = b.math("MULTIPLY", edge, b.math("GREATER_THAN", fade, 0.001))
    return alpha, edge


def _pbr(name, H, edge_hex, base, base2=None, rough=(0.55, 0.85), metal=0.0, rust=0.0, wear_col=None, bump=0.3,
         nscale=6.0, sheen=0.0, spec=0.4, veins=None, vein_center=None, coat=0.0, grime=0.6, cav=1.4, mud=True,
         sheen_tint=(1.0, 1.0, 1.0)):
    """Generic dissolvable PBR surface (bone, rusted iron, gaunt skin, flesh, tarnished gold...).
    veins = (hex, strength, voronoi scale) adds emissive veins scaled by CTRL_glow."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m, b = _mat(name)
    tc = b.n("ShaderNodeTexCoord")
    obj = (tc, "Object")
    n1 = b.n("ShaderNodeTexNoise", Vector=obj, Scale=nscale, Detail=8.0, Roughness=0.62)
    n2 = b.n("ShaderNodeTexNoise", Vector=obj, Scale=nscale * 5.5, Detail=4.0, Roughness=0.55)
    col = b.mix(b.n("ShaderNodeMapRange", Value=(n1, "Fac"), **{"From Min": 0.35, "From Max": 0.7}),
                base, base2 or tuple(c * 0.55 for c in base))
    gm = b.n("ShaderNodeMapRange", Value=(n2, "Fac"), **{"From Min": 0.45, "From Max": 0.75})
    col = b.mix(b.math("MULTIPLY", gm, grime * 0.6), col, tuple(c * 0.22 for c in base))
    col = b.mix(b.math("MINIMUM", b.math("MULTIPLY", b.attr("cav"), cav), 1.0), col, (0.006, 0.005, 0.004))
    wear = b.attr("wear")
    if wear_col:
        col = b.mix(b.math("MINIMUM", b.math("MULTIPLY", wear, 1.1), 1.0), col, wear_col)
    rust_m = None
    if rust:
        rn = b.n("ShaderNodeTexNoise", Vector=obj, Scale=nscale * 2.2, Detail=10.0, Roughness=0.7)
        rust_m = b.n("ShaderNodeMapRange", Value=(rn, "Fac"), **{"From Min": 0.6 - rust * 0.22,
                                                                   "From Max": 0.68 - rust * 0.2})
        col = b.mix(rust_m, col, b.mix((n2, "Fac"), (0.12, 0.036, 0.012), (0.04, 0.015, 0.007)))
    if mud:
        col = b.mix(b.math("MULTIPLY", b.attr("mud"), 0.85), col, (0.03, 0.022, 0.015))
    alpha, edge = _dissolve(b, H)
    char = b.ctrl("char", 0.0)
    col = b.mix(char, col, (0.02, 0.018, 0.017))
    r = b.math("ADD", rough[0], b.math("MULTIPLY", (n2, "Fac"), rough[1] - rough[0]))
    met = metal
    if wear_col and metal:
        r = b.mix(b.math("MINIMUM", wear, 1.0), r, (0.28, 0.28, 0.28))
        r = (r[0], 2)
    if rust:
        r = b.math("MAXIMUM", r, b.math("MULTIPLY", rust_m, 0.92))
        met = b.math("MULTIPLY", b.math("SUBTRACT", 1.0, rust_m), metal)
    r = b.math("MAXIMUM", r, b.math("MULTIPLY", char, 0.95))
    vor = b.n("ShaderNodeTexVoronoi", Vector=obj, Scale=nscale * 4.0, _feature="DISTANCE_TO_EDGE")
    crk = b.n("ShaderNodeMapRange", Value=(vor, "Distance"), **{"From Min": 0.0, "From Max": 0.05,
                                                                "To Min": -1.0, "To Max": 0.0})
    pit = b.n("ShaderNodeTexNoise", Vector=obj, Scale=nscale * 30.0, Detail=2.0)
    hgt = b.math("ADD", b.math("MULTIPLY", (pit, "Fac"), 0.5), b.math("MULTIPLY", crk, 0.4))
    hgt = b.math("ADD", hgt, b.math("MULTIPLY", (n2, "Fac"), 0.6))
    bp = b.n("ShaderNodeBump", Strength=bump, Distance=0.004, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Metallic": met, "Roughness": r, "Normal": bp, "Alpha": alpha})
    bs.inputs["Specular IOR Level"].default_value = spec
    if sheen:
        bs.inputs["Sheen Weight"].default_value = sheen
        bs.inputs["Sheen Tint"].default_value = (*sheen_tint, 1.0)
    if coat:
        bs.inputs["Coat Weight"].default_value = coat
        bs.inputs["Coat Roughness"].default_value = 0.2
    estr = b.math("MULTIPLY", edge, 40.0)
    ecol = hexcol(edge_hex)
    if veins:
        vhex, vstr, vsc = veins
        g = b.ctrl("glow", 1.0)
        wv = b.n("ShaderNodeTexNoise", Vector=obj, Scale=vsc * 0.35, Detail=2.0)
        vin = b.n("ShaderNodeVectorMath", _operation="ADD")
        b.link(obj, vin.inputs[0])
        b.link((wv, "Color"), vin.inputs[1])
        vv = b.n("ShaderNodeTexVoronoi", Scale=vsc, _feature="DISTANCE_TO_EDGE")
        b.link((vin, "Vector"), vv.inputs["Vector"])
        vm = b.n("ShaderNodeMapRange", Value=(vv, "Distance"), **{"From Min": 0.0, "From Max": 0.025,
                                                                  "To Min": 1.0, "To Max": 0.0})
        gate = b.n("ShaderNodeMapRange", Value=(n1, "Fac"), **{"From Min": 0.42, "From Max": 0.58})
        vs = b.math("MULTIPLY", b.math("MULTIPLY", vm, gate), b.math("MULTIPLY", g, vstr))
        if vein_center is not None:
            ctr, rad = vein_center
            dv = b.n("ShaderNodeVectorMath", _operation="DISTANCE")
            b.link(obj, dv.inputs[0])
            dv.inputs[1].default_value = tuple(ctr)
            fall = b.n("ShaderNodeMapRange", Value=(dv, "Value"), **{"From Min": rad * 0.15, "From Max": rad,
                                                                    "To Min": 1.0, "To Max": 0.0})
            vs = b.math("MULTIPLY", vs, fall)
        vs = b.math("MULTIPLY", vs, b.math("SUBTRACT", 1.0, char))
        estr = b.math("ADD", estr, vs)
        b.link(b.mix(edge, hexcol(vhex), ecol), bs.inputs["Emission Color"])
    else:
        bs.inputs["Emission Color"].default_value = (*ecol, 1.0)
    b.link(estr, bs.inputs["Emission Strength"])
    b.out(bs)
    return m


def _glow_mat(name, hex_, strength, H, hot=0.5, crack=0.0):
    """Emissive glow (eyes, cores, pustules, halo). CTRL_glow scales it; hot = whiter core when facing camera;
    crack > 0 adds dark fracture lines (cracked halo)."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m, b = _mat(name)
    alpha, _ = _dissolve(b, H)
    g = b.ctrl("glow", 1.0)
    lw = b.n("ShaderNodeLayerWeight", Blend=0.45)
    face = b.n("ShaderNodeMapRange", Value=(lw, "Facing"), **{"From Min": 0.0, "From Max": 1.0,
                                                              "To Min": 1.0, "To Max": 0.0})
    base = hexcol(hex_)
    whiter = tuple(min(1.0, c * 0.5 + 0.5) for c in base)
    col = b.mix(b.math("MULTIPLY", b.math("POWER", face, 3.0), hot), base, whiter)
    k = b.math("ADD", 0.45, b.math("MULTIPLY", face, 0.75))
    if crack:
        tc = b.n("ShaderNodeTexCoord")
        vor = b.n("ShaderNodeTexVoronoi", Vector=(tc, "Object"), Scale=crack, _feature="DISTANCE_TO_EDGE")
        cm = b.n("ShaderNodeMapRange", Value=(vor, "Distance"), **{"From Min": 0.0, "From Max": 0.04,
                                                                   "To Min": 0.08, "To Max": 1.0})
        k = b.math("MULTIPLY", k, cm)
    em = b.n("ShaderNodeEmission", Color=col)
    b.link(b.math("MULTIPLY", k, b.math("MULTIPLY", g, strength)), em.inputs["Strength"])
    tr = b.n("ShaderNodeBsdfTransparent")
    mx = b.n("ShaderNodeMixShader", Fac=alpha)
    b.link(tr, mx.inputs[1])
    b.link(em, mx.inputs[2])
    b.out(mx)
    return m


def _ghost_mat(name, H, hex_="#9CC8FF", opacity=0.32, glow=2.2, dark=(0.012, 0.016, 0.024), rim_glow=0.7):
    """Translucent spectral surface (alpha blend, no shadow): denser at grazing angles, vertical wispy streaks,
    an inner glow (CTRL_glow) and dissolve (CTRL_fade). Also used, darker, for the evil's smoke edge."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m, b = _mat(name, "BLEND")
    m.shadow_method = "NONE"
    m.use_backface_culling = False
    try:
        m.show_transparent_back = True
    except AttributeError:
        pass
    tc = b.n("ShaderNodeTexCoord")
    obj = (tc, "Object")
    alpha_d, edge = _dissolve(b, H)
    lw = b.n("ShaderNodeLayerWeight", Blend=0.4)
    rim = (lw, "Facing")
    mp = b.n("ShaderNodeMapping", Vector=obj, Scale=(5.0, 5.0, 0.8))
    st = b.n("ShaderNodeTexNoise", Vector=mp, Scale=3.0, Detail=7.0, Roughness=0.65)
    stm = b.n("ShaderNodeMapRange", Value=(st, "Fac"), **{"From Min": 0.32, "From Max": 0.72,
                                                         "To Min": 0.15, "To Max": 1.0})
    sep = b.n("ShaderNodeSeparateXYZ", Vector=obj)
    low = b.n("ShaderNodeMapRange", Value=(sep, "Z"), **{"From Min": 0.0, "From Max": 0.55})
    a = b.math("MULTIPLY", b.math("ADD", 0.3, b.math("MULTIPLY", rim, 1.3)), opacity)
    a = b.math("MULTIPLY", b.math("MULTIPLY", a, stm), b.math("MULTIPLY", low, alpha_d), clamp=True)
    g = b.ctrl("glow", 1.0)
    inner = b.n("ShaderNodeTexNoise", Vector=obj, Scale=2.2, Detail=3.0)
    k = b.math("ADD", b.math("MULTIPLY", (inner, "Fac"), 1.1), b.math("MULTIPLY", rim, rim_glow))
    em = b.n("ShaderNodeEmission", Color=hexcol(hex_))
    b.link(b.math("ADD", b.math("MULTIPLY", b.math("MULTIPLY", k, g), glow), b.math("MULTIPLY", edge, 25.0)),
           em.inputs["Strength"])
    bs = b.bsdf(**{"Base Color": dark, "Roughness": 0.3})
    bs.inputs["Specular IOR Level"].default_value = 0.6
    add = b.n("ShaderNodeAddShader")
    b.link(em, add.inputs[0])
    b.link(bs, add.inputs[1])
    tr = b.n("ShaderNodeBsdfTransparent")
    mx = b.n("ShaderNodeMixShader", Fac=a)
    b.link(tr, mx.inputs[1])
    b.link(add, mx.inputs[2])
    b.out(mx)
    return m


def _cloth_mat(name, H, top, bottom, length=0.6, holes=0.55, sheen=0.5):
    """Tattered cloth (UV V = metres from the top edge): darker, dirtier and holed toward the hem."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m, b = _mat(name)
    m.use_backface_culling = False
    tc = b.n("ShaderNodeTexCoord")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=(tc, "UV"))
    g = b.n("ShaderNodeMapRange", Value=(sep, "Y"), **{"From Min": 0.0, "From Max": length})
    blot = b.n("ShaderNodeTexNoise", Vector=(tc, "Object"), Scale=6.0, Detail=6.0)
    col = b.mix(g, top, bottom)
    col = b.mix(b.math("MULTIPLY", (blot, "Fac"), 0.6), col, tuple(c * 0.35 for c in bottom))
    alpha_d, edge = _dissolve(b, H)
    char = b.ctrl("char", 0.0)
    col = b.mix(char, col, (0.012, 0.011, 0.01))
    weave = b.n("ShaderNodeTexWave", Vector=(tc, "UV"), Scale=380.0, _wave_type="BANDS", _bands_direction="X")
    bump = b.n("ShaderNodeBump", Strength=0.15, Distance=0.001, Height=(weave, "Fac"))
    hn = b.n("ShaderNodeTexNoise", Vector=(tc, "UV"), Scale=9.0, Detail=8.0, Roughness=0.7)
    th = b.n("ShaderNodeMapRange", Value=(sep, "Y"), **{"From Min": length * 0.45, "From Max": length,
                                                      "To Min": 0.0, "To Max": holes * 0.3})
    alive = b.math("GREATER_THAN", (hn, "Fac"), b.math("ADD", 0.3, th))
    alpha = b.math("MULTIPLY", b.math("SUBTRACT", 1.0, b.math("MULTIPLY", b.math("GREATER_THAN", th, 0.001),
                                                                          b.math("SUBTRACT", 1.0, alive))), alpha_d)
    bs = b.bsdf(**{"Base Color": col, "Roughness": 0.94, "Normal": bump, "Alpha": alpha})
    bs.inputs["Sheen Weight"].default_value = sheen
    bs.inputs["Specular IOR Level"].default_value = 0.2
    bs.inputs["Emission Color"].default_value = (*hexcol("#FF6A1A"), 1.0)
    b.link(b.math("MULTIPLY", edge, 30.0), bs.inputs["Emission Strength"])
    b.out(bs)
    return m


def _feather_mat(name, H, edge_hex="#FF2A2A"):
    """Glossy crow-black feather vanes: barbs, ragged splits (alpha), oily sheen."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m, b = _mat(name)
    m.use_backface_culling = False
    tc = b.n("ShaderNodeTexCoord")
    uv = (tc, "UV")
    barbs = b.n("ShaderNodeTexWave", Vector=uv, Scale=160.0, Distortion=2.0, _wave_type="BANDS",
                _bands_direction="DIAGONAL")
    mp = b.n("ShaderNodeMapping", Vector=uv, Scale=(26.0, 1.4, 1.0))
    spl = b.n("ShaderNodeTexNoise", Vector=mp, Scale=2.0, Detail=4.0)
    alpha_d, edge = _dissolve(b, H)
    alive = b.math("LESS_THAN", (spl, "Fac"), 0.66)
    nz = b.n("ShaderNodeTexNoise", Vector=(tc, "Object"), Scale=4.0, Detail=4.0)
    col = b.mix((nz, "Fac"), (0.006, 0.006, 0.008), (0.02, 0.018, 0.022))
    char = b.ctrl("char", 0.0)
    col = b.mix(char, col, (0.03, 0.028, 0.026))
    bump = b.n("ShaderNodeBump", Strength=0.3, Distance=0.001, Height=(barbs, "Fac"))
    bs = b.bsdf(**{"Base Color": col, "Roughness": 0.36, "Normal": bump,
                   "Alpha": b.math("MULTIPLY", alive, alpha_d)})
    bs.inputs["Specular IOR Level"].default_value = 0.55
    bs.inputs["Sheen Weight"].default_value = 0.6
    bs.inputs["Sheen Tint"].default_value = (0.55, 0.6, 1.0, 1.0)
    bs.inputs["Coat Weight"].default_value = 0.25
    bs.inputs["Emission Color"].default_value = (*hexcol(edge_hex), 1.0)
    b.link(b.math("MULTIPLY", edge, 30.0), bs.inputs["Emission Strength"])
    b.out(bs)
    return m


def _floor_rest_mud(ob, H):
    G.bake_attributes(ob, mud_top=0.32 * H / 1.85, mud_floor=0.0, wear_gain=6.0)


# ================================================================== build helpers
def _add(e, ob, joint, mat=None, bake=True, wear=6.0):
    """Material + baked wear/cavity attributes, then rigid-parent the part to a joint (keeps rest transform)."""
    if mat is not None:
        G.set_mat(ob, mat)
    if bake:
        G.bake_attributes(ob, mud_top=0.3 * e.s, mud_floor=0.0, wear_gain=wear)
    parent_keep(ob, e.rig[joint])
    e.parts.append(ob)
    return ob


def _light(e, name, joint, loc, hex_, energy, radius=0.12, dist=4.0):
    """Shadowless glow spill light, parented to a joint; base energy kept for set_glow()."""
    ob = C.light("POINT", e.prefix + name, tuple(float(v) for v in loc), color=hex_, energy=energy, size=radius,
                 shadow=False, volume=0.35)
    try:
        ob.data.use_custom_distance = True
        ob.data.cutoff_distance = dist
    except AttributeError:
        pass
    parent_keep(ob, e.rig[joint])
    e.lights.append((ob, energy))
    return ob


def _xform(ob, pivot, deg=(0, 0, 0), scale=None):
    """Rotate / scale mesh data about a pivot (pre-compensated drapes, askew crowns...)."""
    R = Euler([math.radians(a) for a in deg], "XYZ").to_matrix()
    pv = Vector(tuple(pivot))
    for v in ob.data.vertices:
        d = v.co - pv
        if scale is not None:
            d = Vector((d.x * scale[0], d.y * scale[1], d.z * scale[2]))
        v.co = pv + R @ d
    ob.data.update()
    return ob


def _dome(name, c, radii, rot=(0, 0, 0), p0=0.0, p1=1.25, N=28, M_=9):
    """Ellipsoid cap (pauldrons, lames): polar band p0..p1 radians, pole along the rotated +Z."""
    th = np.linspace(max(p0, 1e-3), p1, M_)[:, None]
    ph = np.linspace(0, 2 * math.pi, N, endpoint=False)[None, :]
    U = np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th) * np.ones_like(ph)], -1)
    Rm = np.array(Euler([math.radians(a) for a in rot], "XYZ").to_matrix())
    P = (U * np.asarray(radii, float)) @ Rm.T + np.asarray(c, float)
    return G.grid_mesh(name, P, closed_u=True, cap_start=(p0 <= 1e-3))


def _ring(name, c, axis, R, r, N=20, wob=0.0, seed=0):
    """Closed torus-like ring (shackles, crown band core) around `axis` through c."""
    X, Y, _ = G.frame_from_axis(axis, (0, -1, 0))
    rnd = random.Random(seed)
    ph = rnd.uniform(0, 6.28)
    pts = [np.asarray(c, float) + R * (1 + wob * math.sin(3 * a + ph)) * (math.cos(a) * X + math.sin(a) * Y)
           for a in np.linspace(0, 2 * math.pi, N + 1)]
    pts.append(pts[1])
    return _sweep(name, pts, r, N=6, cap=False, per=1)


def _rag(name, top, length, rnd, rows=10, out=(0.0, 0.0, 0.0), flare=0.0, tear=0.45, wave=0.012):
    """Hanging tattered cloth: `top` (cols, 3) upper edge, drops `length`, drifts by `out` at the hem,
    widens by `flare`, seeded ragged per-column hem (strips) and a soft fold wave."""
    top = np.asarray(top, float)
    nc = len(top)
    cx = top[:, 0].mean()
    Ls = [length * (1.0 - tear * rnd.random() ** 1.4) for _ in range(nc)]
    ph = rnd.uniform(0, 6.28)
    P = np.zeros((rows, nc, 3))
    for i in range(rows):
        v = i / (rows - 1)
        for j in range(nc):
            p = top[j].copy()
            p[0] = cx + (p[0] - cx) * (1 + flare * v)
            p += np.asarray(out, float) * v ** 1.5
            p[1] += wave * math.sin(j * 1.7 + ph + v * 2.5) * (0.4 + v)
            p[2] -= length * v
            P[i, j] = p

    def skip(i, j):
        return (i + 0.5) / (rows - 1) * length > min(Ls[j], Ls[min(j + 1, nc - 1)])
    return G.grid_mesh(name, P, closed_u=False, skip=skip)


def _curl(d0, sx, ang):
    """Rotate d0 about Y toward the palm (-sx X) by ang radians."""
    th = sx * ang
    c, s_ = math.cos(th), math.sin(th)
    return np.array((d0[0] * c + d0[2] * s_, d0[1], -d0[0] * s_ + d0[2] * c))


def _hand(name, wrist, sx, k_, length=1.0, curl=(8, 22, 18), claw=0.0, r=0.0062, spread=1.0, palm=True):
    """Bony hand hanging from the wrist (fingers down, palm medial, curl closes medially).
    claw > 0 adds hooked claws (metres). Returns (hand, claws or None)."""
    wrist = np.asarray(wrist, float)
    obs, cl = [], []
    if palm:
        obs.append(_blob(name + "_palm", wrist + np.array((sx * 0.002, -0.004, -0.042)) * k_,
                         (0.013 * k_, 0.034 * k_ * spread, 0.038 * k_), N=10, M_=8))
    for k in range(5):
        thumb = k == 4
        if thumb:
            base = wrist + np.array((-sx * 0.012, -0.03 * spread, -0.03)) * k_
            d0 = np.array((-sx * 0.35, -0.75, -0.55))
            segs = np.array((0.045, 0.032, 0.026)) * k_ * length
        else:
            base = wrist + np.array((sx * 0.004, (-0.026 + 0.017 * k) * spread, -0.072)) * k_
            d0 = np.array((0.0, (k - 1.5) * 0.08 * spread, -1.0))
            segs = np.array((0.042, 0.027, 0.022)) * (1.0, 1.08, 1.0, 0.82)[k] * k_ * length
        d0 = d0 / np.linalg.norm(d0)
        pts, p, ang, d = [base], base.copy(), 0.0, d0
        for i, Ls in enumerate(segs):
            ang += math.radians(curl[min(i, len(curl) - 1)])
            d = _curl(d0, sx, ang)
            p = p + d * Ls
            pts.append(p.copy())
        rr = r * k_ * (1.25 if thumb else 1.0)
        obs.append(_sweep("%s_f%d" % (name, k), pts, lambda t, rr=rr: rr * (1.0 - 0.35 * t), N=6, per=2))
        if claw:
            cf = claw * (0.7 if thumb else 1.0)
            dc = _curl(d0, sx, ang + math.radians(25))
            dc2 = _curl(d0, sx, ang + math.radians(70))
            cp = [p - d * 0.006 * k_, p + dc * cf * 0.55, p + dc * cf * 0.55 + dc2 * cf * 0.5]
            cl.append(_sweep("%s_c%d" % (name, k), cp, lambda t, rr=rr: rr * 0.95 * (1 - t) ** 1.3 + 0.0004,
                             N=6, per=3))
    return G.join(obs, name), (G.join(cl, name + "_claws") if cl else None)


def _vert(name, c, r, proc):
    """One vertebra: body, spinous process (back/down), two transverse processes."""
    c = np.asarray(c, float)
    obs = [_blob(name, c, tuple(r), N=10, M_=7),
           _blob(name + "p", c + np.array((0, r[1] + proc * 0.55, -proc * 0.35)), (r[0] * 0.28, proc * 0.65, r[2] * 0.55),
                 N=8, M_=6, rot=(28, 0, 0))]
    for sx in (1, -1):
        obs.append(_blob(name + "t%d" % sx, c + np.array((sx * r[0] * 1.35, r[1] * 0.7, 0)),
                         (r[0] * 0.6, r[1] * 0.32, r[2] * 0.4), N=8, M_=6))
    return G.join(obs, name)


def _sword(e, mat, L=0.74):
    """Rusted, notched falchion on the weapon joint (blade forward -Y, edge down)."""
    W, s, P, rnd = e.J["weapon"], e.s, e.prefix, e.rnd
    ys = np.linspace(0.07, -0.075, 12)
    obs = [_sweep(P + "grip", [W + np.array((0, y, 0)) * s for y in ys],
                  lambda t: 0.0135 * s * (1 + 0.1 * math.cos(t * math.pi * 16)), N=8, per=1),
           _blob(P + "pommel", W + np.array((0, 0.088, 0)) * s, (0.02 * s, 0.017 * s, 0.021 * s), N=10, M_=7),
           _sweep(P + "guard", [W + np.array(v) * s for v in ((0, -0.095, 0.07), (0, -0.082, 0.03), (0, -0.08, 0.0),
                                                              (0, -0.082, -0.03), (0, -0.098, -0.07))],
                  lambda t: 0.0085 * s * (1 - 0.3 * abs(2 * t - 1)), N=6)]
    rows, cols = 32, 10
    Pm = np.zeros((rows, cols, 3))
    chips = [rnd.uniform(0, 1) for _ in range(rows)]
    for i in range(rows):
        t = i / (rows - 1)
        ztop = 0.021 - 0.045 * max(0.0, (t - 0.78) / 0.22) ** 1.6
        zbot = -0.025 - 0.018 * math.sin(math.pi * min(1.0, t * 0.9)) + 0.03 * max(0.0, (t - 0.84) / 0.16) ** 1.3
        if 0.1 < t < 0.92 and chips[i] < 0.22:
            zbot += 0.007 * chips[i] / 0.22
        if t > 0.97:
            zbot = ztop = (ztop + zbot) / 2
        mid, half = (ztop + zbot) / 2, (ztop - zbot) / 2
        th = 0.0034 * (1 - 0.55 * t) + 0.0004
        y = -0.1 - L * t
        for j in range(cols):
            a = 2 * math.pi * j / cols
            ca = math.cos(a)
            Pm[i, j] = W + np.array((th * math.sin(a), y, mid + half * math.copysign(abs(ca) ** 0.55, ca))) * s
    obs.append(G.grid_mesh(P + "blade", Pm, closed_u=True, cap_start=True, cap_end=True))
    _add(e, G.join(obs, P + "sword"), "weapon", mat, wear=9.0)


# ------------------------------------------------------------------ skeleton (also the king's body)
def _skeleton_body(e, bone, eyes, rmul=1.0, cloth=None, open_hand=True):
    J, T, s, P, rnd = e.J, e.T, e.s, e.prefix, e.rnd
    rb = s * rmul
    c = T((0, -0.012, 1.758))
    L = 0.1 * s
    e.skull_c, e.skull_L = c, L
    sk, jw = _skull(P + "skull", c, L)
    _add(e, sk, "head", bone)
    _add(e, jw, "jaw", bone)
    ey = G.join([_blob(P + "eye%d" % i, c + np.array((sx * 0.3, -0.62, -0.07)) * L, 0.14 * L, N=10, M_=7)
                 for i, sx in enumerate((1, -1))], P + "eyes")
    _add(e, ey, "head", eyes, bake=False)
    # spine
    cv = [_vert(P + "cv%d" % i, T((0, 0.035, 1.545 + 0.033 * i)), np.array((0.016, 0.014, 0.0095)) * rb, 0.016 * rb)
          for i in range(4)]
    _add(e, G.join(cv, P + "cspine"), "neck", bone)
    tv = [_vert(P + "tv%d" % i, T((0, 0.07 + 0.018 * math.sin(i / 11 * math.pi), 1.51 - 0.026 * i)),
                np.array((0.019 + 0.0012 * i, 0.017 + 0.001 * i, 0.0105)) * rb, 0.026 * rb) for i in range(12)]
    lv = [_vert(P + "lv%d" % i, T((0, 0.045 - 0.012 * math.sin(i / 4 * math.pi), 1.19 - 0.043 * i)),
                np.array((0.027, 0.023, 0.015)) * rb, 0.024 * rb) for i in range(5)]
    _add(e, G.join(lv, P + "lspine"), "spine", bone)
    # ribcage + sternum
    ribs = list(tv)
    A_ = (0.072, 0.093, 0.108, 0.118, 0.126, 0.13, 0.131, 0.128, 0.122, 0.112, 0.098)
    B_ = (0.06, 0.074, 0.084, 0.091, 0.096, 0.098, 0.098, 0.096, 0.092, 0.086, 0.078)
    PE = (0.9, 0.9, 0.9, 0.9, 0.89, 0.88, 0.86, 0.8, 0.74, 0.62, 0.5)
    for k in range(11):
        zk, drop = 1.475 - 0.026 * k, 0.04 + 0.011 * k
        for sx in (1, -1):
            pts = [T((sx * A_[k] * math.sin(ph) * (1 + 0.06 * math.sin(2 * ph)), -0.012 + B_[k] * math.cos(ph),
                      zk - drop * (ph / math.pi) ** 1.4)) for ph in np.linspace(0.06, 1, 13) * PE[k] * math.pi]
            ribs.append(_sweep(P + "rib%d%d" % (k, sx), pts, (0.0085 * rb, 0.0036 * rb), N=6, per=1))
    ribs.append(_blob(P + "sternum", T((0, -0.108, 1.37)), (0.017 * rb, 0.007 * rb, 0.085 * s), N=10, M_=9,
                      rot=(-14, 0, 0)))
    _add(e, G.join(ribs, P + "ribcage"), "chest", bone)
    for sd, sx in (("L", 1), ("R", -1)):
        cl = _sweep(P + "clav" + sd, [T((sx * 0.022, -0.088, 1.462)), T((sx * 0.075, -0.085, 1.476)),
                                      T((sx * 0.13, -0.045, 1.478)), T((sx * 0.168, 0.0, 1.472))], 0.0075 * rb, N=7)
        sc = _blob(P + "scap" + sd, T((sx * 0.095, 0.108, 1.37)), (0.055 * s, 0.011 * s, 0.075 * s), N=12, M_=8,
                   rot=(10, 0, -sx * 20))
        sr = _sweep(P + "scapr" + sd, [T((sx * 0.05, 0.122, 1.415)), T((sx * 0.1, 0.12, 1.432)),
                                       T((sx * 0.155, 0.1, 1.45))], 0.0075 * rb, N=6)
        _add(e, G.join([cl, sc, sr], P + "shoulder" + sd), "clav_" + sd, bone)
        # arm
        ua, fa, hd = J["upperarm_" + sd], J["forearm_" + sd], J["hand_" + sd]
        hum = G.join([_blob(P + "humh" + sd, ua + np.array((0, 0.004, 0.004)) * s, 0.023 * rb, N=12, M_=9),
                      _bone(P + "hum" + sd, ua + np.array((0, 0, -0.02)) * s, fa + np.array((0, 0, 0.01)) * s,
                            0.0125 * rb, knob=1.8)], P + "humerus" + sd)
        _add(e, hum, "upperarm_" + sd, bone)
        fo = G.join([_bone(P + "rad" + sd, fa + np.array((sx * 0.014, -0.006, -0.012)) * s,
                           hd + np.array((sx * 0.016, -0.01, 0.012)) * s, 0.0072 * rb, knob=1.6),
                     _bone(P + "uln" + sd, fa + np.array((-sx * 0.006, 0.014, -0.004)) * s,
                           hd + np.array((-sx * 0.008, 0.008, 0.012)) * s, 0.0068 * rb, knob=1.6),
                     _blob(P + "olec" + sd, fa + np.array((0, 0.016, 0.0)) * s, (0.012 * rb, 0.014 * rb, 0.016 * rb),
                           N=8, M_=6)], P + "forearm" + sd)
        _add(e, fo, "forearm_" + sd, bone)
        grip = (sd == "R" and "weapon" in e.rig) or not open_hand
        hnd, _ = _hand(P + "hand" + sd, hd, sx, s, curl=(55, 70, 60) if grip else (12, 28, 22), r=0.006 * rmul)
        _add(e, hnd, "hand_" + sd, bone)
        # leg
        hip, knee, ank = J["thigh_" + sd], J["shin_" + sd], J["foot_" + sd]
        tro = hip + np.array((sx * 0.035, 0.005, -0.03)) * s
        fem = G.join([_blob(P + "femh" + sd, hip, 0.022 * rb, N=12, M_=9),
                      _sweep(P + "femn" + sd, [hip, (hip + tro) / 2, tro], 0.012 * rb, N=8),
                      _bone(P + "fem" + sd, tro + np.array((0, 0, -0.01)) * s, knee + np.array((0, 0, 0.012)) * s,
                            0.0135 * rb, knob=1.8),
                      _blob(P + "cond" + sd, knee + np.array((0, 0.004, 0.012)) * s, (0.03 * rb, 0.027 * rb, 0.02 * rb),
                            N=10, M_=7)], P + "femur" + sd)
        _add(e, fem, "thigh_" + sd, bone)
        tib = G.join([_blob(P + "pat" + sd, knee + np.array((0, -0.034, 0.008)) * s, (0.017 * rb, 0.008 * rb, 0.021 * rb),
                            N=8, M_=6),
                      _blob(P + "plat" + sd, knee + np.array((0, 0, -0.026)) * s, (0.031 * rb, 0.027 * rb, 0.015 * rb),
                            N=10, M_=7),
                      _bone(P + "tib" + sd, knee + np.array((0, 0, -0.03)) * s, ank + np.array((0, 0, 0.02)) * s,
                            0.0135 * rb, knob=1.6),
                      _bone(P + "fib" + sd, knee + np.array((sx * 0.03, 0.012, -0.045)) * s,
                            ank + np.array((sx * 0.03, 0.01, 0.0)) * s, 0.0055 * rb, knob=1.5)], P + "tibia" + sd)
        _add(e, tib, "shin_" + sd, bone)
        ft = [_blob(P + "talus" + sd, ank + np.array((0, 0.022, -0.035)) * s, (0.024 * rb, 0.045 * s, 0.028 * rb),
                    N=10, M_=7, rot=(12, 0, 0)),
              _blob(P + "tars" + sd, ank + np.array((0, -0.035, -0.045)) * s, (0.03 * rb, 0.03 * s, 0.02 * rb), N=10, M_=7)]
        for k in range(5):
            ox = sx * (-0.022 + 0.012 * k)
            ft.append(_sweep(P + "toe%s%d" % (sd, k), [ank + np.array(v) * s for v in
                                                      ((ox * 0.6, -0.04, -0.045), (ox, -0.105, -0.066),
                                                       (ox * 1.08, -0.15 - (0.02 if k == 0 else 0.004 * (4 - k)), -0.078))],
                             lambda t, k=k: (0.009 if k == 0 else 0.0062) * rb * (1 - 0.35 * t), N=6, per=2))
        _add(e, G.join(ft, P + "foot" + sd), "foot_" + sd, bone)
    # pelvis
    pv = [_blob(P + "sacrum", T((0, 0.06, 0.975)), (0.042 * s, 0.018 * s, 0.065 * s), N=12, M_=9, rot=(-28, 0, 0))]
    for sx in (1, -1):
        pv.append(_blob(P + "ilium%d" % sx, T((sx * 0.09, 0.012, 1.005)), (0.068 * s, 0.02 * s, 0.062 * s), N=14, M_=10,
                        rot=(0, sx * 18, -sx * 38), bump=lambda U: 1 + 0.12 * U[..., 2]))
        pv.append(_blob(P + "acet%d" % sx, T((sx * 0.088, 0.0, 0.935)), 0.024 * rb, N=10, M_=7))
        pv.append(_sweep(P + "pubis%d" % sx, [T(v) for v in ((sx * 0.085, 0.0, 0.935), (sx * 0.075, -0.045, 0.9),
                                                            (sx * 0.02, -0.065, 0.885), (0, -0.066, 0.885))], 0.011 * rb, N=7))
        pv.append(_sweep(P + "isch%d" % sx, [T(v) for v in ((sx * 0.085, 0.0, 0.935), (sx * 0.075, 0.03, 0.885),
                                                           (sx * 0.05, 0.035, 0.86), (sx * 0.03, -0.02, 0.87),
                                                           (sx * 0.02, -0.06, 0.885))], 0.0105 * rb, N=7))
    _add(e, G.join(pv, P + "pelvisb"), "pelvis", bone)
    if cloth is not None:
        belt = [T((0.15 * math.cos(a), 0.005 + 0.115 * math.sin(a), 0.982 - 0.02 * max(0.0, -math.sin(a))))
                for a in np.linspace(0, 2 * math.pi, 25)]
        belt.append(belt[1])
        rags = [_sweep(P + "belt", belt, (0.011 * s, 0.006 * s), N=6, cap=False, per=1)]
        xs = np.linspace(-0.1, 0.1, 9)
        rags.append(_rag(P + "loinF", [T((x, -0.122 + 0.5 * x * x, 0.968)) for x in xs], 0.42 * s, rnd,
                         out=(0, -0.03 * s, 0), flare=0.1))
        xs = np.linspace(-0.125, 0.125, 11)
        rags.append(_rag(P + "loinB", [T((x, 0.112 - 0.5 * x * x, 0.985)) for x in xs], 0.5 * s, rnd,
                         out=(0, 0.05 * s, 0), flare=0.15))
        for sx in (1, -1):
            rags.append(_rag(P + "loinS%d" % sx, [T((sx * 0.148, y, 0.978)) for y in np.linspace(-0.05, 0.05, 4)],
                             0.24 * s, rnd, out=(sx * 0.03 * s, 0, 0), tear=0.6))
        _add(e, G.join(rags, P + "loincloth"), "pelvis", cloth, bake=False)


def _build_skeleton(e):
    P, H = e.prefix, e.height
    bone = _pbr(P + "bone", H, GLOW["skeleton"], base=(0.42, 0.37, 0.29), base2=(0.17, 0.13, 0.085), rough=(0.5, 0.85),
                sheen=0.08, grime=0.85, cav=1.8, nscale=7.0, bump=0.35, spec=0.35)
    iron = _pbr(P + "iron", H, GLOW["skeleton"], base=(0.045, 0.04, 0.036), metal=0.85, rust=1.0,
                wear_col=(0.32, 0.3, 0.27), rough=(0.32, 0.65), nscale=9.0, bump=0.5, mud=False)
    cloth = _cloth_mat(P + "cloth", H, top=(0.032, 0.026, 0.018), bottom=(0.011, 0.008, 0.006), length=0.5, holes=0.7)
    eyes = _glow_mat(P + "eyes", GLOW["skeleton"], 40.0, H, hot=0.7)
    e.mats.update(bone=bone, iron=iron, cloth=cloth, eyes=eyes)
    _skeleton_body(e, bone, eyes, cloth=cloth)
    _sword(e, iron)
    if e.want_lights:
        _light(e, "eyelight", "head", e.skull_c + np.array((0, -0.16, -0.01)) * e.s, GLOW["skeleton"], 2.0, 0.03, 1.5)


def _build_king(e):
    J, T, s, P, rnd, H = e.J, e.T, e.s, e.prefix, e.rnd, e.height
    bone = _pbr(P + "bone", H, GLOW["skeleton_king"], base=(0.3, 0.26, 0.2), base2=(0.1, 0.075, 0.05), rough=(0.5, 0.85),
                sheen=0.06, grime=0.95, cav=2.0, nscale=4.5, bump=0.4, spec=0.35)
    iron = _pbr(P + "armour", H, GLOW["skeleton_king"], base=(0.03, 0.028, 0.026), metal=0.9, rust=0.65,
                wear_col=(0.34, 0.32, 0.29), rough=(0.28, 0.6), nscale=4.0, bump=0.45)
    axe = _pbr(P + "axe", H, GLOW["skeleton_king"], base=(0.035, 0.032, 0.03), metal=0.9, rust=0.45,
               wear_col=(0.42, 0.4, 0.37), rough=(0.25, 0.55), nscale=5.0, bump=0.45, mud=False,
               veins=(GLOW["skeleton_king"], 9.0, 5.0))
    gold = _pbr(P + "gold", H, GLOW["skeleton_king"], base=(0.42, 0.27, 0.075), base2=(0.12, 0.075, 0.025), metal=1.0,
                rust=0.35, wear_col=(0.75, 0.55, 0.22), rough=(0.25, 0.5), nscale=14.0, bump=0.3, mud=False)
    wood = _pbr(P + "wood", H, GLOW["skeleton_king"], base=(0.035, 0.02, 0.011), base2=(0.012, 0.007, 0.004),
                rough=(0.55, 0.85), nscale=3.0, bump=0.4, mud=False)
    cloth = _cloth_mat(P + "cloth", H, top=(0.06, 0.006, 0.007), bottom=(0.012, 0.0028, 0.0028), length=1.9, holes=0.8)
    eyes = _glow_mat(P + "eyes", GLOW["skeleton_king"], 45.0, H, hot=0.7)
    e.mats.update(bone=bone, armour=iron, axe=axe, gold=gold, wood=wood, cloth=cloth, eyes=eyes)
    _skeleton_body(e, bone, eyes, rmul=1.28, cloth=None)
    # --- broken cuirass (hole over the left ribs)
    rows, cols = 9, 24
    zs, ths = np.linspace(1.2, 1.485, rows), np.linspace(-math.pi + 0.28, -0.28, cols)
    Pm = np.zeros((rows, cols, 3))
    for i, z in enumerate(zs):
        v = (z - 1.2) / 0.285
        a = 0.152 + 0.03 * math.sin(math.pi * min(1.0, v * 1.25)) - 0.012 * max(0, v - 0.8) / 0.2
        b = 0.122 + 0.016 * math.sin(math.pi * min(1.0, v * 1.2))
        for j, th in enumerate(ths):
            ridge = 0.012 * math.exp(-((th + math.pi / 2) / 0.16) ** 2)
            Pm[i, j] = T((a * math.cos(th), -0.008 + b * math.sin(th) - ridge, z))
    hole = np.zeros((rows, cols), bool)
    for i in range(rows):
        for j in range(cols):
            th, z = ths[j], zs[i]
            jag = 0.05 * rnd.uniform(-1, 1)
            hole[i, j] = (-1.05 + jag < th < -0.32) and (1.2 <= z < 1.37 + jag)
    cu = G.grid_mesh(P + "cuirass", Pm, skip=lambda i, j: hole[i, j])
    G.finish_plate(cu, thick=0.007 * s, bevel=0.002 * s, subsurf=1)
    G.dents(cu, e.seed + 3, count=7, depth=0.006 * s, radius=(0.03 * s, 0.07 * s))
    _add(e, cu, "chest", iron, wear=8.0)
    # --- pauldrons + lames, bracers, greaves
    for sd, sx in (("L", 1), ("R", -1)):
        ua = J["upperarm_" + sd]
        pa = [_dome(P + "paul" + sd, ua + np.array((sx * 0.02, 0.0, 0.035)) * s, np.array((0.115, 0.125, 0.095)) * s,
                    rot=(0, sx * 38, 0), p1=1.35)]
        for k in range(2):
            pa.append(_dome(P + "lame%s%d" % (sd, k), ua + np.array((sx * (0.03 + 0.012 * k), 0.0, -0.005 - 0.03 * k)) * s,
                            np.array((0.13, 0.135, 0.1)) * s * (1.06 + 0.07 * k), rot=(0, sx * (44 + 6 * k), 0),
                            p0=1.0, p1=1.38))
        for ob in pa:
            G.finish_plate(ob, thick=0.006 * s, bevel=0.002 * s, subsurf=1)
        _add(e, G.join(pa, P + "pauldron" + sd), "upperarm_" + sd, iron, wear=8.0)
        fa, hd = J["forearm_" + sd], J["hand_" + sd]
        br = G.tube(P + "bracer" + sd, fa + (hd - fa) * 0.35, fa + (hd - fa) * 0.92,
                    lambda t, th: 0.034 * s * (1 + 0.25 * t), N=20, M=5)
        G.finish_plate(br, thick=0.005 * s, bevel=0.0015 * s, subsurf=1)
        _add(e, br, "forearm_" + sd, iron, wear=8.0)
        kn, an = J["shin_" + sd], J["foot_" + sd]
        gr = G.tube(P + "greave" + sd, kn + np.array((0, -0.006, -0.05)) * s, an + np.array((0, -0.004, 0.06)) * s,
                    lambda t, th: 0.04 * s * (1 + 0.15 * math.sin(math.pi * t * 0.7)), N=20, M=6, arc=(-2.1, 2.1))
        G.finish_plate(gr, thick=0.005 * s, bevel=0.0015 * s, subsurf=1)
        _add(e, gr, "shin_" + sd, iron, wear=8.0)
    # --- faulds (3 lames) + tattered royal tabard and cape
    fl = []
    for k in range(3):
        z0 = 1.0 - 0.055 * k
        fl.append(G.tube(P + "fauld%d" % k, T((0, 0.0, z0)), T((0, 0.0, z0 - 0.07)),
                         lambda t, th, k=k: (0.17 + 0.012 * k + 0.02 * t) * s * 1.1, N=28, M=3, arc=(-2.5, 2.5)))
    for ob in fl:
        G.finish_plate(ob, thick=0.005 * s, bevel=0.0015 * s, subsurf=1)
    _add(e, G.join(fl, P + "faulds"), "pelvis", iron, wear=8.0)
    tb = [_rag(P + "tabF", [T((x, -0.2 + 0.4 * x * x, 0.88)) for x in np.linspace(-0.11, 0.11, 8)], 0.5 * s, rnd,
               out=(0, -0.04 * s, 0), flare=0.15, tear=0.4),
          _rag(P + "tabB", [T((x, 0.2 - 0.4 * x * x, 0.9)) for x in np.linspace(-0.13, 0.13, 9)], 0.55 * s, rnd,
               out=(0, 0.06 * s, 0), flare=0.2, tear=0.4)]
    _add(e, G.join(tb, P + "tabard"), "pelvis", cloth, bake=False)
    cape = _rag(P + "cape", [T((x, 0.135 + 0.55 * x * x, 1.47 - 0.6 * x * x)) for x in np.linspace(-0.2, 0.2, 13)],
                1.12 * s, rnd, rows=12, out=(0, 0.16 * s, 0), flare=0.55, tear=0.4)
    _add(e, cape, "chest", cloth, bake=False)
    # --- broken crown, askew
    c, L = e.skull_c, e.skull_L
    zb = c[2] + 0.36 * L
    cols, gap = 40, (17, 19)
    band = np.zeros((3, cols, 3))
    for i, dz in enumerate((0.0, 0.12, 0.24)):
        for j in range(cols):
            a = 2 * math.pi * j / cols
            band[i, j] = (c[0] + 0.7 * L * 1.04 * math.cos(a), c[1] - 0.02 * L + 0.9 * L * 1.03 * math.sin(a), zb + dz * L)
    cr = [G.grid_mesh(P + "crownb", band, closed_u=True, skip=lambda i, j: gap[0] <= j < gap[1])]
    G.finish_plate(cr[0], thick=0.004 * s, bevel=0.0012 * s, subsurf=1)
    for k in range(9):
        j = int(round(k * cols / 9 + 2)) % cols
        if gap[0] - 1 <= j <= gap[1]:
            continue
        p0 = band[1, j].copy()
        out = band[1, j] - np.array((c[0], c[1] - 0.02 * L, band[1, j][2]))
        out /= max(1e-6, np.linalg.norm(out))
        h = L * (0.55 if k % 2 == 0 else 0.35) * (0.45 if k in (3, 7) else 1.0)
        tip = p0 + np.array((0, 0, h)) + out * 0.08 * h
        cr.append(_sweep(P + "spike%d" % k, [p0 - np.array((0, 0, 0.1 * L)), (p0 + tip) / 2, tip],
                         lambda t, k=k: 0.035 * L * (1 - t) ** (1.6 if k not in (3, 7) else 0.4) + 0.002 * L, N=6))
    crown = G.join(cr, P + "crown")
    _xform(crown, c, (7, -9, 4))
    _add(e, crown, "head", gold, wear=10.0)
    # --- huge bearded axe
    W = e.J["weapon"]
    ys = np.linspace(0.2, -1.26, 30)
    hf = [_sweep(P + "haft", [W + np.array((0, y, 0)) * s for y in ys],
                 lambda t: 0.019 * s * (1 + 0.12 * (math.cos(t * math.pi * 60) > 0.6) * (t < 0.14)), N=10, per=1)]
    met = [_blob(P + "butt", W + np.array((0, 0.215, 0)) * s, (0.026 * s, 0.03 * s, 0.026 * s), N=10, M_=7),
           _sweep(P + "langet", [W + np.array((0, y, 0.0)) * s for y in np.linspace(-0.88, -1.27, 6)], 0.023 * s, N=8, per=1),
           _sweep(P + "spike", [W + np.array(v) * s for v in ((0, -1.12, 0.02), (0, -1.115, 0.12), (0, -1.08, 0.24))],
                  lambda t: 0.024 * s * (1 - t) ** 1.2 + 0.001, N=8)]
    rows, nv = 12, 14
    Pm = np.zeros((rows, 2 * nv, 3))
    notch = [rnd.uniform(0, 1) for _ in range(nv)]
    for i in range(rows):
        t = i / (rows - 1)
        th = 0.026 * (1 - t) ** 0.8 + 0.0016
        for jj in range(nv):
            v = jj / (nv - 1)
            A = np.array((0.0, -1.215 + 0.22 * v, -0.015))
            E = np.array((0.0, -1.36 + 0.56 * v - 0.08 * math.sin(math.pi * v), -0.05 - 0.4 * v - 0.07 * math.sin(math.pi * v)))
            Q = A + (E - A) * t
            Q[2] += (-0.06 * (1 - v) + 0.07 * v) * math.sin(math.pi * t) * (1 - 0.5 * t)
            if i == rows - 1 and notch[jj] < 0.25:
                Q += (A - E) / np.linalg.norm(A - E) * 0.02
            Pm[i, jj] = W + (Q + np.array((th, 0, 0))) * s
            Pm[i, 2 * nv - 1 - jj] = W + (Q - np.array((th, 0, 0))) * s
    met.append(G.grid_mesh(P + "axehead", Pm, closed_u=True, cap_start=True, cap_end=True))
    G.set_mat(hf[0], wood)
    for ob in met:
        G.set_mat(ob, axe)
    _add(e, G.join(hf + met, P + "axe"), "weapon", None, wear=9.0)
    if e.want_lights:
        _light(e, "eyelight", "head", c + np.array((0, -0.2, 0.0)) * s, GLOW["skeleton_king"], 6.0, 0.05, 2.5)
        _light(e, "axelight", "weapon", W + np.array((0, -1.2, -0.25)) * s, GLOW["skeleton_king"], 8.0, 0.2, 2.5)


# ------------------------------------------------------------------ ghost
def _build_ghost(e):
    J, T, s, P, rnd, H = e.J, e.T, e.s, e.prefix, e.rnd, e.height
    spirit = _ghost_mat(P + "spirit", H, GLOW["ghost"], opacity=0.3, glow=1.6)
    core = _ghost_mat(P + "core", H, GLOW["ghost"], opacity=0.85, glow=3.0, rim_glow=1.2)
    eyes = _glow_mat(P + "eyes", GLOW["ghost"], 45.0, H, hot=0.9)
    void = _pbr(P + "void", H, GLOW["ghost"], base=(0.002, 0.0025, 0.004), rough=(0.9, 1.0), mud=False, grime=0.0, cav=0.0)
    e.mats.update(spirit=spirit, core=core, eyes=eyes, void=void)
    # robe / hood shell: rows top -> hem, front = -Y at theta = -pi/2
    zs = np.concatenate([np.linspace(1.95, 1.62, 9), np.linspace(1.58, 1.0, 10), np.linspace(0.95, 0.4, 12)])
    N = 36
    ths = np.linspace(-math.pi, math.pi, N, endpoint=False)
    ph = [rnd.uniform(0, 6.28) for _ in range(3)]
    Pm = np.zeros((len(zs), N, 3))
    for i, z in enumerate(zs):
        if z > 1.62:
            v = (1.95 - z) / 0.33
            rx = 0.02 + 0.115 * math.sin(math.pi / 2 * v) ** 0.7
            ry = 0.025 + 0.135 * math.sin(math.pi / 2 * v) ** 0.7
            yc = 0.11 * (1 - v) ** 1.5 + 0.02
        elif z > 0.98:
            v = (1.62 - z) / 0.64
            rx = 0.135 + 0.13 * math.sin(math.pi / 2 * min(1.0, v * 3)) - 0.04 * v
            ry = 0.15 + 0.02 * v
            yc = 0.02
        else:
            v = (0.98 - z) / 0.58
            rx, ry, yc = 0.225 + 0.11 * v, 0.17 + 0.09 * v, 0.02 + 0.12 * v ** 1.5
        fold = 1 + (0.03 + 0.07 * max(0.0, (1.3 - z) / 0.9)) * math.sin(np.pi * 0 + 7 * 0 + 0) * 0
        for j, th in enumerate(ths):
            f = 1 + (0.025 + 0.08 * max(0.0, (1.25 - z) / 0.85)) * math.sin(7 * th + ph[0] + z * 2.0)
            Pm[i, j] = T((rx * f * math.cos(th), yc + ry * f * math.sin(th), z))
    hem = [0.4 + 0.33 * rnd.random() ** 1.3 for _ in range(N)]

    def skip_hood(i, j):
        z, th = zs[i], ths[j]
        if 1.6 < z < 1.86 and abs(th + math.pi / 2) < 0.62 - 0.6 * max(0.0, z - 1.78):
            return True
        return False
    up = G.grid_mesh(P + "robeU", Pm[:20], closed_u=True, skip=skip_hood, cap_start=True)
    lo = G.grid_mesh(P + "robeL", Pm[17:], closed_u=True,
                     skip=lambda i, j: zs[17 + i + 1] < max(hem[j], hem[(j + 1) % N]) * s)
    _add(e, up, "chest", spirit, bake=False)
    _add(e, lo, "tail1", spirit, bake=False)
    c = T((0, -0.035, 1.735))
    _add(e, _blob(P + "void", T((0, 0.0, 1.74)), (0.095 * s, 0.1 * s, 0.13 * s), N=14, M_=10), "head", void, bake=False)
    fc, jw = _skull(P + "face", c, 0.088 * s, depth=0.9, flesh=0.6)
    _add(e, fc, "head", core, bake=False)
    _add(e, jw, "jaw", core, bake=False)
    ey = G.join([_blob(P + "eye%d" % i, c + np.array((sx * 0.3, -0.64, -0.07)) * 0.088 * s, 0.15 * 0.088 * s, N=10, M_=7)
                 for i, sx in enumerate((1, -1))], P + "eyes")
    _add(e, ey, "head", eyes, bake=False)
    for sd, sx in (("L", 1), ("R", -1)):
        ua, fa, hd = J["upperarm_" + sd], J["forearm_" + sd], J["hand_" + sd]
        sl = G.tube(P + "sleeveU" + sd, ua + np.array((0, 0, 0.03)) * s, fa, lambda t, th: (0.075 - 0.01 * t) * s, N=16, M=6)
        _add(e, sl, "upperarm_" + sd, spirit, bake=False)
        cut = [rnd.uniform(0.55, 1.0) for _ in range(16)]
        sl2 = G.tube(P + "sleeveL" + sd, fa + np.array((0, 0, 0.03)) * s, hd + np.array((0, 0, -0.03)) * s,
                     lambda t, th: (0.065 + 0.075 * t ** 1.6) * s, N=16, M=8,
                     skip=lambda i, j: (i + 1) / 7.0 > cut[j] and i > 3)
        _add(e, sl2, "forearm_" + sd, spirit, bake=False)
        hnd, cl = _hand(P + "hand" + sd, hd, sx, s * 1.15, length=1.7, curl=(10, 22, 26), claw=0.075 * s, r=0.0055)
        _add(e, G.join([hnd, cl], P + "claw" + sd), "hand_" + sd, core, bake=False)
    wisps2, wisps3 = [], []
    for k in range(9):
        th = math.pi * (0.1 + 0.8 * k / 8) + rnd.uniform(-0.1, 0.1)
        x0, y0 = 0.27 * math.cos(th), 0.12 + 0.22 * math.sin(th)
        z0 = rnd.uniform(0.45, 0.62)
        Lw = rnd.uniform(0.5, 0.95)
        pts = [T((x0, y0, z0)), T((x0 * 1.1, y0 + 0.18 * Lw, z0 - 0.2 * Lw)),
               T((x0 * 1.2 + rnd.uniform(-0.08, 0.08), y0 + 0.5 * Lw, z0 - 0.3 * Lw)),
               T((x0 * 1.25 + rnd.uniform(-0.12, 0.12), y0 + 0.85 * Lw, z0 - 0.26 * Lw + rnd.uniform(-0.05, 0.08)))]
        w = _sweep(P + "wisp%d" % k, pts, lambda t: 0.055 * s * (1 - t) ** 1.2 + 0.002, N=8)
        (wisps3 if Lw > 0.75 else wisps2).append(w)
    if wisps2:
        _add(e, G.join(wisps2, P + "wispsA"), "tail2", spirit, bake=False)
    if wisps3:
        _add(e, G.join(wisps3, P + "wispsB"), "tail3", spirit, bake=False)
    if e.want_lights:
        _light(e, "inner", "chest", T((0, -0.05, 1.35)), GLOW["ghost"], 25.0, 0.3, 3.5)


# ------------------------------------------------------------------ gaunt humanoid body (bad angel, evil)
def _gaunt_body(e, skin, prof, nail=None):
    """Skin-modifier body: prof = dict of radii multipliers (torso, limb) for bulk."""
    J, T, s, P, rnd = e.J, e.T, e.s, e.prefix, e.rnd
    tw, lw = prof.get("torso", 1.0), prof.get("limb", 1.0)
    lo = _chain(P + "abdomen", [T((0, 0.012, 0.93)), T((0, 0.0, 1.06)), T((0, -0.004, 1.2))],
                [(0.12 * tw * s, 0.085 * s), (0.095 * tw * s, 0.07 * s), (0.12 * tw * s, 0.085 * s)])
    _jitter(lo, 0.004 * s, e.seed + 1, 18)
    _add(e, lo, "spine", skin)
    up = _chain(P + "torso", [T((0, -0.004, 1.16)), T((0, -0.006, 1.27)), T((0, 0.0, 1.38)), T((0, 0.012, 1.465)),
                              T((0, 0.03, 1.53))],
                [(0.125 * tw * s, 0.088 * s), (0.14 * tw * s, 0.096 * s), (0.155 * tw * s, 0.1 * s),
                 (0.14 * tw * s, 0.085 * s), (0.05 * s, 0.045 * s)])
    for v in up.data.vertices:          # rib ridges + sunken belly under the skin
        z = v.co.z / s
        if 1.17 < z < 1.43 and v.co.y < 0.06 * s:
            v.co += v.normal * (0.0045 * s * (abs(math.sin((z - 1.17) * math.pi / 0.028)) - 0.55))
    up.data.update()
    _jitter(up, 0.004 * s, e.seed + 2, 16)
    _add(e, up, "chest", skin)
    nk = _chain(P + "neck", [T((0, 0.03, 1.5)), T((0, 0.03, 1.6)), T((0, 0.02, 1.68))],
                [(0.045 * s, 0.045 * s), (0.04 * s, 0.04 * s), (0.04 * s, 0.04 * s)])
    _add(e, nk, "neck", skin)
    for sd, sx in (("L", 1), ("R", -1)):
        sh = _chain(P + "delt" + sd, [T((sx * 0.07, 0.012, 1.475)), J["upperarm_" + sd] + np.array((sx * 0.01, 0, 0.005)) * s],
                    [(0.045 * tw * s, 0.04 * s), (0.05 * lw * s, 0.045 * lw * s)])
        _add(e, sh, "clav_" + sd, skin)
        ua, fa, hd = J["upperarm_" + sd], J["forearm_" + sd], J["hand_" + sd]
        _add(e, _chain(P + "uarm" + sd, [ua + np.array((0, 0, 0.01)) * s, (ua + fa) / 2, fa],
                       [(0.045 * lw * s, 0.043 * lw * s), (0.036 * lw * s, 0.034 * lw * s), (0.03 * lw * s, 0.028 * lw * s)]),
             "upperarm_" + sd, skin)
        _add(e, _chain(P + "farm" + sd, [fa, fa + (hd - fa) * 0.35, hd],
                       [(0.03 * lw * s, 0.028 * lw * s), (0.031 * lw * s, 0.028 * lw * s), (0.02 * lw * s, 0.016 * lw * s)]),
             "forearm_" + sd, skin)
        hnd, cl = _hand(P + "hand" + sd, hd, sx, s * prof.get("hand", 1.0), length=prof.get("finger", 1.4),
                        curl=(14, 28, 24), claw=prof.get("claw", 0.03) * s, r=0.0075)
        _add(e, hnd, "hand_" + sd, skin)
        _add(e, cl, "hand_" + sd, nail or skin, wear=9.0)
        hip, kn, an = J["thigh_" + sd], J["shin_" + sd], J["foot_" + sd]
        _add(e, _chain(P + "thigh" + sd, [hip + np.array((0, 0, 0.04)) * s, hip + (kn - hip) * 0.45, kn],
                       [(0.075 * lw * s, 0.07 * lw * s), (0.058 * lw * s, 0.055 * lw * s), (0.042 * lw * s, 0.042 * lw * s)]),
             "thigh_" + sd, skin)
        _add(e, _chain(P + "shin" + sd, [kn, kn + (an - kn) * 0.3, an + np.array((0, 0, 0.01)) * s],
                       [(0.04 * lw * s, 0.042 * lw * s), (0.04 * lw * s, 0.043 * lw * s), (0.026 * lw * s, 0.026 * lw * s)]),
             "shin_" + sd, skin)
        ft = _chain(P + "foot" + sd, [an + np.array((0, 0.04, -0.055)) * s, an + np.array((0, -0.02, -0.05)) * s,
                                      an + np.array((0, -0.11, -0.068)) * s],
                    [(0.026 * s, 0.026 * s), (0.034 * lw * s, 0.024 * s), (0.036 * lw * s, 0.013 * s)])
        toes = [_sweep(P + "ftoe%s%d" % (sd, k), [an + np.array(v) * s for v in
                                                 ((sx * (-0.022 + 0.011 * k), -0.1, -0.068),
                                                  (sx * (-0.026 + 0.013 * k), -0.15, -0.072),
                                                  (sx * (-0.028 + 0.014 * k), -0.19 + 0.008 * k, -0.082))],
                        lambda t: 0.008 * s * (1 - 0.7 * t), N=6, per=2) for k in range(5)]
        _add(e, ft, "foot_" + sd, skin)
        _add(e, G.join(toes, P + "toes" + sd), "foot_" + sd, nail or skin)


def _feather(name, root, d, L, W, rnd, twist=0.0, curve=0.06):
    """Feather card from root along unit d (length L, half width W), rows along the length; vane in the wing plane."""
    d = np.asarray(d, float)
    d /= np.linalg.norm(d)
    w = np.cross(d, (0.0, 1.0, 0.0))
    w /= max(1e-6, np.linalg.norm(w))
    n = np.cross(w, d)
    ca, sa = math.cos(twist), math.sin(twist)
    w, n = w * ca + n * sa, n * ca - w * sa
    rows = 7
    Pm = np.zeros((rows, 3, 3))
    for i in range(rows):
        t = i / (rows - 1)
        wt = W * math.sin(math.pi * min(1.0, 0.12 + t * 0.95)) ** 0.5 * (1 - 0.55 * t ** 3)
        c = np.asarray(root, float) + d * L * t + n * curve * L * math.sin(math.pi * t * 0.8)
        for j, v in enumerate((-0.8, 0.0, 1.15)):
            Pm[i, j] = c + w * wt * v + n * 0.004 * (1 - abs(v))
    return G.grid_mesh(name, Pm)


def _wing(e, sd, sx, feath, skin):
    J, s, P, rnd = e.J, e.s, e.prefix, e.rnd
    r0, r1 = J["wing_" + sd], J["wing2_" + sd]
    tip = r1 + np.array((sx * 1.02, 0.14, -0.4)) * s
    b1 = _sweep(P + "wb1" + sd, [r0, (r0 + r1) / 2 + np.array((0, 0.02, 0.03)) * s, r1], lambda t: 0.03 * s * (1 - 0.35 * t), N=8)
    b2 = _sweep(P + "wb2" + sd, [r1, r1 + (tip - r1) * 0.5 + np.array((0, 0, 0.07)) * s, tip],
                lambda t: 0.022 * s * (1 - 0.75 * t), N=8)
    inner, outer = [], []
    torn = set(range(rnd.randrange(3, 8), 0) if False else [])
    gap0 = rnd.randrange(3, 8)
    torn = {gap0, gap0 + 1, gap0 + 2} if sd == "L" else {gap0 + 3}

    def flight(group, n, a, b, dA, dB, LA, LB, WW, tag, offy=0.0, brk=True):
        for k in range(n):
            t = k / max(1, n - 1)
            if brk and tag == "p" and k in torn:
                continue
            r = rnd.random()
            if brk and r < 0.1:
                continue
            Lk = (LA + (LB - LA) * t) * s * rnd.uniform(0.92, 1.06)
            if brk and r < 0.32:
                Lk *= rnd.uniform(0.35, 0.7)
            root = a + (b - a) * t + np.array((0, 0.012 * (k % 2) + offy, 0)) * s
            dd = np.asarray(dA) + (np.asarray(dB) - np.asarray(dA)) * t
            dd = dd + np.array((rnd.uniform(-0.07, 0.07), 0, rnd.uniform(-0.07, 0.07)))
            if brk and rnd.random() < 0.12:
                dd = dd + np.array((sx * rnd.uniform(-0.3, 0.3), 0.1, 0))
            group.append(_feather("%sfe%s%s%d" % (P, sd, tag, k), root, dd, Lk, WW * s * rnd.uniform(0.85, 1.1), rnd,
                                  twist=rnd.uniform(-0.25, 0.25)))
    flight(outer, 13, r1, tip, (sx * 0.3, 0.1, -1.0), (sx * 1.0, 0.12, -0.15), 0.78, 1.05, 0.055, "p")
    flight(inner, 12, r0 + (r1 - r0) * 0.2, r1, (sx * 0.05, 0.16, -1.0), (sx * 0.2, 0.14, -1.0), 0.48, 0.7, 0.05, "s")
    flight(outer, 9, r1, tip, (sx * 0.25, 0.04, -1.0), (sx * 0.9, 0.06, -0.3), 0.3, 0.4, 0.04, "c", offy=-0.018)
    flight(inner, 9, r0 + (r1 - r0) * 0.15, r1, (sx * 0.05, 0.06, -1.0), (sx * 0.2, 0.06, -1.0), 0.22, 0.3, 0.04, "d",
           offy=-0.02)
    for ob in inner + outer:
        G.set_mat(ob, feath)
    G.set_mat(b1, skin)
    G.set_mat(b2, skin)
    _add(e, G.join([b1] + inner, P + "wingA" + sd), "wing_" + sd, None, bake=False)
    _add(e, G.join([b2] + outer, P + "wingB" + sd), "wing2_" + sd, None, bake=False)


def _build_angel(e):
    J, T, s, P, rnd, H = e.J, e.T, e.s, e.prefix, e.rnd, e.height
    skin = _pbr(P + "skin", H, GLOW["bad_angel"], base=(0.085, 0.078, 0.075), base2=(0.03, 0.026, 0.028), rough=(0.4, 0.7),
                sheen=0.25, coat=0.12, cav=1.3, grime=0.6, nscale=5.0, bump=0.35, mud=False)
    nail = _pbr(P + "nail", H, GLOW["bad_angel"], base=(0.012, 0.01, 0.01), rough=(0.25, 0.5), coat=0.3, mud=False)
    feath = _feather_mat(P + "feather", H, GLOW["bad_angel"])
    cloth = _cloth_mat(P + "cloth", H, top=(0.01, 0.009, 0.01), bottom=(0.003, 0.003, 0.0035), length=0.7, holes=0.8)
    eyes = _glow_mat(P + "eyes", GLOW["bad_angel"], 45.0, H, hot=0.7)
    halo = _glow_mat(P + "halo", GLOW["bad_angel"], 22.0, H, hot=0.45, crack=22.0)
    e.mats.update(skin=skin, nail=nail, feather=feath, cloth=cloth, eyes=eyes, halo=halo)
    _gaunt_body(e, skin, {"torso": 0.95, "limb": 0.9, "finger": 1.45, "claw": 0.035}, nail)
    c, L = T((0, -0.012, 1.76)), 0.1 * s
    hd, jw = _skull(P + "head", c, L, depth=0.6, flesh=1.0, teeth=False)
    _add(e, hd, "head", skin)
    _add(e, jw, "jaw", skin)
    ey = G.join([_blob(P + "eye%d" % i, c + np.array((sx * 0.3, -0.66, -0.07)) * L, 0.13 * L, N=10, M_=7)
                 for i, sx in enumerate((1, -1))], P + "eyes")
    _add(e, ey, "head", eyes, bake=False)
    hair = []
    for k in range(26):
        a = rnd.uniform(-2.6, 2.6)
        r0 = c + np.array((0.6 * math.sin(a), 0.85 * math.cos(a) * 0.9 + 0.1, 0.62 + 0.15 * math.cos(a))) * L
        r0[1] = max(r0[1], c[1] - 0.2 * L)
        Lh = rnd.uniform(0.28, 0.5) * s
        dirx = math.sin(a) * 0.25
        hair.append(_sweep(P + "hair%d" % k, [r0, r0 + np.array((dirx * 0.3, 0.06, -0.05)) * s,
                                              r0 + np.array((dirx * 0.5 + rnd.uniform(-0.03, 0.03), 0.09, -Lh * 0.5 / s)) * s,
                                              r0 + np.array((dirx * 0.55 + rnd.uniform(-0.05, 0.05), 0.07, -Lh / s)) * s],
                           lambda t: 0.0045 * s * (1 - 0.8 * t), N=5, per=2))
    _add(e, G.join(hair, P + "hair"), "head", nail, bake=False)
    rag = [_rag(P + "skirtF", [T((x, -0.11 + 0.5 * x * x, 0.98)) for x in np.linspace(-0.13, 0.13, 10)], 0.62 * s, rnd,
                out=(0, -0.04 * s, 0), flare=0.25, tear=0.55),
           _rag(P + "skirtB", [T((x, 0.1 - 0.5 * x * x, 0.99)) for x in np.linspace(-0.14, 0.14, 10)], 0.7 * s, rnd,
                out=(0, 0.06 * s, 0), flare=0.3, tear=0.55)]
    _add(e, G.join(rag, P + "skirt"), "pelvis", cloth, bake=False)
    for sd, sx in (("L", 1), ("R", -1)):
        _wing(e, sd, sx, feath, skin)
    # cracked halo: three arcs with jagged gaps, leaning back behind the head
    hc, R = T((0, 0.16, 1.86)), 0.26 * s
    X, Z = np.array((1.0, 0, 0)), np.array((0, math.sin(math.radians(14)), math.cos(math.radians(14))))
    arcs = []
    for k, (a0, a1) in enumerate(((0.3, 1.95), (2.2, 4.0), (4.32, 6.02))):
        pts = [hc + R * (1 + 0.012 * math.sin(a * 11)) * (math.cos(a) * X + math.sin(a) * Z)
               for a in np.linspace(a0, a1, 22)]
        arcs.append(_sweep(P + "halo%d" % k, pts, lambda t: (0.017 * s * (0.55 + 0.45 * math.sin(math.pi * t) ** 0.3),
                                                           0.008 * s), N=6, per=1))
    for k, a in enumerate((2.08, 4.17, 6.15)):
        arcs.append(_blob(P + "halofr%d" % k, hc + R * 1.06 * (math.cos(a) * X + math.sin(a) * Z), 0.012 * s, N=6, M_=5,
                          rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), 0)))
    _add(e, G.join(arcs, P + "halo"), "head", halo, bake=False)
    if e.want_lights:
        _light(e, "halolight", "head", hc + np.array((0, -0.12, 0)), GLOW["bad_angel"], 22.0, 0.25, 3.5)


def _build_evil(e):
    J, T, s, P, rnd, H = e.J, e.T, e.s, e.prefix, e.rnd, e.height
    chest_c = T((0, -0.1, 1.33))
    hide = _pbr(P + "hide", H, GLOW["evil"], base=(0.016, 0.014, 0.018), base2=(0.005, 0.004, 0.006), rough=(0.32, 0.72),
                coat=0.25, sheen=0.2, sheen_tint=(0.6, 0.4, 1.0), veins=(GLOW["evil"], 7.0, 2.6),
                vein_center=(tuple(chest_c), 0.6 * s), bump=0.5, nscale=4.0, mud=False, cav=1.0)
    horn = _pbr(P + "horn", H, GLOW["evil"], base=(0.04, 0.034, 0.03), base2=(0.006, 0.005, 0.005), rough=(0.3, 0.6),
                coat=0.2, nscale=9.0, bump=0.6, mud=False)
    smoke = _ghost_mat(P + "smoke", H, "#3C1C6E", opacity=0.6, glow=0.35, dark=(0.003, 0.002, 0.004), rim_glow=0.5)
    core = _glow_mat(P + "core", GLOW["evil"], 30.0, H, hot=0.8, crack=16.0)
    eyes = _glow_mat(P + "eyes", GLOW["evil"], 50.0, H, hot=0.8)
    cloak = _cloth_mat(P + "cloak", H, top=(0.009, 0.008, 0.01), bottom=(0.0025, 0.0022, 0.003), length=1.8 * s, holes=0.9)
    e.mats.update(hide=hide, horn=horn, smoke=smoke, core=core, eyes=eyes, cloak=cloak)
    _gaunt_body(e, hide, {"torso": 1.35, "limb": 1.25, "finger": 1.6, "claw": 0.07, "hand": 1.1}, horn)
    c, L = T((0, -0.02, 1.755)), 0.105 * s
    hd, jw = _skull(P + "head", c, L, depth=0.95, flesh=0.45)
    _xform(hd, c, scale=(1.0, 1.12, 1.05))
    _add(e, hd, "head", hide)
    _add(e, jw, "jaw", hide)
    ey = G.join([_blob(P + "eye%d" % i, c + np.array((sx * 0.3, -0.62, -0.07)) * L, 0.15 * L, N=10, M_=7)
                 for i, sx in enumerate((1, -1))], P + "eyes")
    _add(e, ey, "head", eyes, bake=False)
    hn = []
    for sx in (1, -1):
        b = c + np.array((sx * 0.48, -0.25, 0.55)) * L
        pts = [b] + [b + np.array(v) * s for v in ((sx * 0.06, 0.03, 0.09), (sx * 0.15, 0.12, 0.17), (sx * 0.21, 0.24, 0.22),
                                                  (sx * 0.24, 0.34, 0.33), (sx * 0.21, 0.36, 0.47), (sx * 0.16, 0.3, 0.56))]
        hn.append(_sweep(P + "horn%d" % sx, pts, lambda t: (0.034 * s * (1 - t) ** 0.85 + 0.0015) *
                         (1 + 0.09 * math.sin(t * 70)), N=10, per=3))
        b2 = c + np.array((sx * 0.32, -0.78, 0.32)) * L
        hn.append(_sweep(P + "brow%d" % sx, [b2, b2 + np.array((sx * 0.02, -0.03, 0.05)) * s,
                                              b2 + np.array((sx * 0.035, -0.02, 0.1)) * s],
                         lambda t: 0.012 * s * (1 - t) + 0.001, N=6))
    _add(e, G.join(hn, P + "horns"), "head", horn, wear=9.0)
    sp = [_sweep(P + "dspike%d" % k, [T((0, 0.13 - 0.004 * k, 1.47 - 0.065 * k)),
                                      T((0, 0.2 - 0.004 * k, 1.5 - 0.065 * k)),
                                      T((0, 0.25 - 0.004 * k, 1.56 - 0.065 * k + 0.02 * (k == 1)))],
                 lambda t, k=k: 0.022 * s * (1 - t) * (1 - 0.1 * k) + 0.001, N=6) for k in range(5)]
    _add(e, G.join(sp, P + "spikes"), "chest", horn, wear=9.0)
    co = _blob(P + "core", chest_c + np.array((0, 0.022, 0.0)) * s, (0.06 * s, 0.03 * s, 0.075 * s), N=14, M_=10,
               bump=lambda U: 1 + 0.15 * np.sin(U[..., 0] * 9) * np.sin(U[..., 2] * 7))
    _add(e, co, "chest", core, bake=False)
    # smoke edge: inflated, noisy copies of the bulk parts in translucent smoke
    for nm, jt in (("torso", "chest"), ("abdomen", "spine"), ("uarmL", "upperarm_L"), ("uarmR", "upperarm_R"),
                   ("farmL", "forearm_L"), ("farmR", "forearm_R"), ("thighL", "thigh_L"), ("thighR", "thigh_R")):
        src = bpy.data.objects.get(P + nm)
        if src is None:
            continue
        sm = bpy.data.objects.new(P + "smk_" + nm, src.data.copy())
        C.link(sm)
        sm.matrix_world = src.matrix_world.copy()
        sm.parent = None
        sm.matrix_world = Matrix.Identity(4)
        _jitter(sm, 0.0, 0)
        for v in sm.data.vertices:
            v.co += v.normal * 0.028 * s * (1 + 0.6 * math.sin(v.co.z * 23 + v.co.x * 17))
        sm.data.update()
        _add(e, sm, jt, smoke, bake=False)
    ws = []
    for k in range(7):
        x0 = rnd.uniform(-0.24, 0.24)
        b = T((x0, 0.06 + rnd.uniform(0, 0.08), 1.48 - abs(x0) * 0.3))
        Lw = rnd.uniform(0.35, 0.7) * s
        ws.append(_sweep(P + "smw%d" % k, [b, b + np.array((x0 * 0.4, 0.1, 0.4)) * Lw,
                                            b + np.array((x0 * 0.8 + rnd.uniform(-0.15, 0.15), 0.35, 0.8)) * Lw,
                                            b + np.array((x0 + rnd.uniform(-0.3, 0.3), 0.65, 1.0)) * Lw],
                         lambda t: 0.07 * s * (1 - t) ** 0.9 + 0.003, N=8))
    _add(e, G.join(ws, P + "smokewisps"), "chest", smoke, bake=False)
    ck = _rag(P + "cloak", [T((x, 0.125 + 0.55 * x * x, 1.5 - 0.5 * x * x)) for x in np.linspace(-0.25, 0.25, 15)],
              1.3 * s, rnd, rows=12, out=(0, 0.1 * s, 0), flare=0.7, tear=0.55)
    _xform(ck, J["chest"], (-30, 0, 0))
    _add(e, ck, "chest", cloak, bake=False)
    if e.want_lights:
        _light(e, "corelight", "chest", chest_c + np.array((0, -0.25, 0)) * s, GLOW["evil"], 35.0, 0.12, 4.0)
        _light(e, "eyelight", "head", c + np.array((0, -0.25, 0)) * L / 0.1, GLOW["evil"], 4.0, 0.05, 2.0)


# ------------------------------------------------------------------ morbidious
def _pustules(e, name, joint, host, c, radii, bump, n, bias, rmin, rmax, glow_mat, flesh):
    rnd, s, P = e.rnd, e.s, e.prefix
    c, radii, bias = np.asarray(c, float), np.asarray(radii, float), np.asarray(bias, float)
    glows, dead = [], []
    tries = 0
    while len(glows) + len(dead) < n and tries < n * 40:
        tries += 1
        d = np.array([rnd.gauss(0, 1) for _ in range(3)])
        d /= np.linalg.norm(d)
        if np.dot(d, bias) < rnd.uniform(-0.5, 0.7) or d[2] < -0.6:
            continue
        f = float(bump(d[None, None, :])[0, 0]) if bump is not None else 1.0
        nrm = d / radii
        nrm /= np.linalg.norm(nrm)
        p = c + radii * d * f
        r = rnd.uniform(rmin, rmax) * s
        k = len(glows) + len(dead)
        pu = _blob("%s%s%d" % (P, name, k), p + nrm * r * 0.2, (r, r, r * 0.9), N=10, M_=8)
        ring = _blob("%s%sr%d" % (P, name, k), p - nrm * r * 0.25, (r * 1.5, r * 1.5, r * 1.5), N=10, M_=7)
        if rnd.random() < 0.82:
            glows.append(pu)
            dead.append(ring)
        else:
            dead += [pu, ring]
    if glows:
        _add(e, G.join(glows, P + name + "_glow"), joint, glow_mat, bake=False)
    if dead:
        _add(e, G.join(dead, P + name + "_base"), joint, flesh)


def _build_morbidious(e):
    J, s, P, rnd, H = e.J, e.s, e.prefix, e.rnd, e.height
    flesh = _pbr(P + "flesh", H, GLOW["morbidious"], base=(0.13, 0.12, 0.075), base2=(0.055, 0.03, 0.045),
                 rough=(0.2, 0.55), coat=0.45, sheen=0.15, veins=(GLOW["morbidious"], 2.4, 2.6), bump=0.55, nscale=3.2,
                 cav=1.6, grime=0.9)
    pus = _glow_mat(P + "pus", GLOW["morbidious"], 18.0, H, hot=0.8)
    iron = _pbr(P + "iron", H, GLOW["morbidious"], base=(0.04, 0.036, 0.033), metal=0.85, rust=1.0,
                wear_col=(0.3, 0.28, 0.25), rough=(0.32, 0.65), nscale=9.0, bump=0.5)
    cloth = _cloth_mat(P + "cloth", H, top=(0.03, 0.027, 0.016), bottom=(0.01, 0.01, 0.005), length=0.5, holes=0.6)
    e.mats.update(flesh=flesh, pus=pus, iron=iron, cloth=cloth)

    def lumpy(seed, a=0.06):
        r2 = random.Random(seed)
        ph = [r2.uniform(0, 6.3) for _ in range(4)]
        return lambda U: (1 + a * np.sin(U[..., 0] * 5 + ph[0]) * np.sin(U[..., 2] * 4 + ph[1])
                          + 0.7 * a * np.sin(U[..., 1] * 7 + ph[2]) * np.cos(U[..., 2] * 6 + ph[3])
                          + 0.07 * np.clip(-U[..., 2], 0, 1) ** 2)
    bb = lumpy(e.seed + 1)
    belly = _blob(P + "belly", (0, -0.1, 1.04), (0.46, 0.44, 0.42), N=40, M_=28, bump=bb)
    _bulge(belly, (0, -0.42, 0.8), 0.2, 0.05, axis=(0, -0.3, -1))
    _jitter(belly, 0.01, e.seed + 1, 9)
    _add(e, belly, "spine", flesh)
    hb = lumpy(e.seed + 2)
    hump = _blob(P + "hump", (0, 0.07, 1.56), (0.5, 0.42, 0.4), N=40, M_=28, bump=hb)
    _bulge(hump, (0, 0.34, 1.84), 0.22, 0.16)
    _bulge(hump, (0.22, 0.26, 1.76), 0.15, 0.08)
    _bulge(hump, (-0.25, 0.2, 1.72), 0.14, 0.07)
    _jitter(hump, 0.01, e.seed + 2, 8)
    _add(e, hump, "chest", flesh)
    neck = _blob(P + "neckfat", (0, -0.16, 1.72), (0.17, 0.15, 0.11), N=16, M_=10)
    _add(e, neck, "neck", flesh)
    c, L = J["head"] + np.array((0, -0.045, 0.085)), 0.088
    hd, jw = _skull(P + "head", c, L, depth=0.55, flesh=1.0)
    _jitter(hd, 0.004, e.seed + 3, 30)
    _add(e, hd, "head", flesh)
    _add(e, jw, "jaw", flesh)
    ey = G.join([_blob(P + "eye%d" % i, c + np.array((sx * 0.3, -0.6, -0.07)) * L, 0.12 * L, N=8, M_=6)
                 for i, sx in enumerate((1, -1))], P + "eyes")
    _add(e, ey, "head", pus, bake=False)
    _pustules(e, "pusB", "spine", belly, (0, -0.1, 1.04), (0.46, 0.44, 0.42), bb, 16, (0.2, -0.6, 0.2), 0.018, 0.05, pus, flesh)
    _pustules(e, "pusH", "chest", hump, (0, 0.07, 1.56), (0.5, 0.42, 0.4), hb, 26, (0.0, 0.6, 0.6), 0.02, 0.065, pus, flesh)
    for sd, sx in (("L", 1), ("R", -1)):
        ua, fa, hn = J["upperarm_" + sd], J["forearm_" + sd], J["hand_" + sd]
        _add(e, _chain(P + "uarm" + sd, [ua + np.array((-sx * 0.06, 0, 0.06)), (ua + fa) / 2, fa],
                       [(0.19, 0.18), (0.15, 0.14), (0.115, 0.105)]), "upperarm_" + sd, flesh)
        _pustules(e, "pusA" + sd, "upperarm_" + sd, None, (ua + fa) / 2 + np.array((sx * 0.02, 0.02, 0)), (0.15, 0.14, 0.22),
                  None, 6, (sx * 0.6, 0.5, 0.4), 0.015, 0.04, pus, flesh)
        _add(e, _chain(P + "farm" + sd, [fa, fa + (hn - fa) * 0.4, hn + np.array((0, 0, 0.03))],
                       [(0.115, 0.105), (0.13, 0.12), (0.085, 0.075)]), "forearm_" + sd, flesh)
        _add(e, _ring(P + "shackle" + sd, fa + (hn - fa) * 0.82, hn - fa, 0.1, 0.018, seed=e.seed), "forearm_" + sd, iron)
        hnd, _ = _hand(P + "hand" + sd, hn, sx, 2.3, length=0.85, curl=(22, 40, 30), r=0.0085, spread=1.1)
        _add(e, hnd, "hand_" + sd, flesh)
        hip, kn, an = J["thigh_" + sd], J["shin_" + sd], J["foot_" + sd]
        _add(e, _chain(P + "thigh" + sd, [hip + np.array((0, 0, 0.08)), kn], [(0.21, 0.2), (0.14, 0.13)]), "thigh_" + sd, flesh)
        _add(e, _chain(P + "shin" + sd, [kn, kn + (an - kn) * 0.4, an + np.array((0, 0, 0.03))],
                       [(0.14, 0.13), (0.145, 0.14), (0.1, 0.09)]), "shin_" + sd, flesh)
        ft = _blob(P + "foot" + sd, an + np.array((0, -0.06, -0.045)), (0.1, 0.16, 0.065), N=14, M_=9,
                   bump=lambda U: 1 + 0.25 * np.clip(-U[..., 2], 0, 1) * 0)
        _add(e, ft, "foot_" + sd, flesh)
    rg = _rag(P + "rag", [(x, -0.47 + 0.6 * x * x, 0.8) for x in np.linspace(-0.25, 0.25, 11)], 0.42, rnd,
              out=(0, -0.05, 0), flare=0.1, tear=0.5)
    belt = [(0.4 * math.cos(a), -0.08 + 0.4 * math.sin(a), 0.82 + 0.03 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 25)]
    belt.append(belt[1])
    _add(e, G.join([rg, _sweep(P + "rope", belt, (0.016, 0.01), N=6, cap=False, per=1)], P + "loin"), "pelvis", cloth, bake=False)
    if e.want_lights:
        _light(e, "pusfront", "chest", (0.0, -0.8, 1.3), GLOW["morbidious"], 30.0, 0.35, 3.5)
        _light(e, "pusback", "chest", (0.0, 0.75, 1.95), GLOW["morbidious"], 25.0, 0.35, 3.5)


BUILDERS = {"skeleton": _build_skeleton, "skeleton_king": _build_king, "ghost": _build_ghost, "bad_angel": _build_angel,
            "evil": _build_evil, "morbidious": _build_morbidious}
STRIDE = {"skeleton": 0.55, "skeleton_king": 0.6, "ghost": 0.5, "bad_angel": 0.55, "evil": 0.6, "morbidious": 0.42}


def build_enemy(kind, prefix=None, seed=0, lights=True):
    """Build one enemy at the origin (rest pose, facing -Y). Returns an Enemy with .kind, .rig, .root, .parts, .mats,
    .glow_mats (materials with CTRL_glow), .fade_mats (CTRL_fade), .lights [(light, base energy)], .height, .J, .s."""
    if kind not in KINDS:
        raise ValueError("unknown enemy kind %r (KINDS = %r)" % (kind, KINDS))
    e = Enemy()
    e.kind, e.seed, e.want_lights = kind, int(seed), bool(lights)
    e.prefix = _unique_prefix(prefix or SHORT[kind] + "_")
    e.J, e.T = _joints(kind)
    e.s = e.T.s
    e.height = HEIGHT[kind]
    e.names = _rig_names(kind)
    e.rig = _build_rig(e.prefix, e.J, e.names)
    e.root = e.rig["root"]
    e.parts, e.mats, e.lights = [], {}, []
    e.rnd = random.Random(e.seed * 7919 + KINDS.index(kind) * 104729 + 17)
    e.scale = 1.0
    e._wprev = None
    BUILDERS[kind](e)
    e.mats = {k: m for k, m in e.mats.items() if m is not None}
    e.glow_mats = [m for m in e.mats.values() if M.ctrl_node(m, "glow") is not None]
    e.fade_mats = [m for m in e.mats.values() if M.ctrl_node(m, "fade") is not None]
    e.glow_color = GLOW[kind]
    for ob in e.parts:
        ob["rb_enemy"] = e.prefix
    bpy.context.view_layer.update()
    return e
