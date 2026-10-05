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
