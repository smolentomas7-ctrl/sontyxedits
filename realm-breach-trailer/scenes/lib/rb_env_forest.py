"""THE HAUNTED FOREST LOBBY + HELLGATE (shots M101-M104, Phase 1 of the montage).

Night, cold grey-blue moonlight, heavy drifting mist. Everything is procedural:

  trees      gnarled dead trees (seeded recursive branching, buttress root flare,
             surface roots, real lofted bark furrows + bark shader), instanced as
             linked duplicates; far ones cast no shadow (cheap shadow maps)
  ground     heightfield terrain with a carved river / lake basin, wet banks,
             leaf litter, moss, a trodden path and a scorch mask (hellgate)
  water      one dark reflective water plane per set; per-vertex `flow` / `depth`
             attributes drive frame-driven streaks, ripples and bank foam
  waterfall  displaced strata cliff + three falling sheets (scrolling streaks),
             foam disc and a rising spray-mist volume at the base
  boards     weathered wooden ranking boards on log posts: rows of carved runic
             marks (illegible by construction), a few dim glowing slots, iron
             fittings and a hanging lantern
  hellgate   broken jagged black-rock ring with shards and ember fissures, a
             swirling fire-vortex disc, an emissive heat-haze volume and
             Geometry-Nodes embers (positions are a pure function of scene time)

API
  build_forest(variant='trees'|'waterfall'|'boards'|'hellgate', seed) -> Forest
      .objects, .mats, .trees, .rocks, .water, .falls, .boards, .gate, .embers,
      .mist, .marks (warrior / cam / aim positions), .ground_z(x, y), .ctrls
  lights_forest(variant, forest=None) -> {name: light}   (moon + fill [+ lantern / portal])
  ember_rim(target, cam_loc)                             (warrior ember rim, no shadow)
  animate(forest, frame)                                 (keys light flicker + CTRL_time)
Animated controls are Value nodes named CTRL_<name> (rb_mat convention):
  CTRL_time (seconds; every water / fire / mist material, linear in the frame),
  CTRL_portal (vortex intensity), CTRL_heat (gate fissure glow), CTRL_glow (board slots).
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Vector

import rb_core as C
import rb_mat as M
import rb_mesh as G
from rb_core import hexcol, link

VARIANTS = ("trees", "waterfall", "boards", "hellgate")
WATER_Z = -0.32
MOON_COL = (0.60, 0.70, 0.88)
EMBER = "#FF6A1A"


# =================================================================== noise
class VNoise:
    """Seeded 3-D value noise (numpy, smoothstep lattice) with fBm / ridged helpers. Range ~[-1, 1]."""

    def __init__(self, seed):
        r = np.random.default_rng(int(seed) & 0xFFFFFFFF)
        p = r.permutation(256)
        self.p = np.concatenate([p, p])
        self.v = r.uniform(-1.0, 1.0, 256)

    def _h(self, i, j, k):
        p = self.p
        return self.v[p[p[p[i & 255] + (j & 255)] + (k & 255)]]

    def __call__(self, x, y, z=0.0):
        x, y, z = np.broadcast_arrays(*(np.asarray(a, dtype=float) for a in (x, y, z)))
        xi, yi, zi = (np.floor(a).astype(np.int64) for a in (x, y, z))
        u, v, w = ((a - b) * (a - b) * (3 - 2 * (a - b)) for a, b in ((x, xi), (y, yi), (z, zi)))
        h = self._h
        x00 = h(xi, yi, zi) + (h(xi + 1, yi, zi) - h(xi, yi, zi)) * u
        x10 = h(xi, yi + 1, zi) + (h(xi + 1, yi + 1, zi) - h(xi, yi + 1, zi)) * u
        x01 = h(xi, yi, zi + 1) + (h(xi + 1, yi, zi + 1) - h(xi, yi, zi + 1)) * u
        x11 = h(xi, yi + 1, zi + 1) + (h(xi + 1, yi + 1, zi + 1) - h(xi, yi + 1, zi + 1)) * u
        y0 = x00 + (x10 - x00) * v
        y1 = x01 + (x11 - x01) * v
        return y0 + (y1 - y0) * w

    def fbm(self, x, y, z=0.0, octaves=4, lac=2.03, gain=0.5):
        x, y, z = (np.asarray(a, dtype=float) for a in (x, y, z))
        tot, amp, norm, f = 0.0, 1.0, 0.0, 1.0
        for o in range(octaves):
            tot = tot + amp * self(x * f + o * 17.31, y * f + o * 9.13, z * f + o * 5.71)
            norm += amp
            amp *= gain
            f *= lac
        return tot / norm

    def ridged(self, x, y, z=0.0):
        return 1.0 - np.abs(self(x, y, z))


def _unit(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def _smooth(e0, e1, x):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# =================================================================== mesh assembly
class MeshAcc:
    """Accumulates lofted grids and fans into ONE mesh: per-loop metre UVs (seams handled),
    float point attributes, material indices and per-face smooth flags. Much faster than
    building and joining hundreds of objects."""

    def __init__(self):
        self.V, self.Q, self.QUV, self.QM, self.QS = [], [], [], [], []
        self.T, self.TUV, self.TM, self.TS = [], [], [], []
        self.A = []
        self.n = 0

    def grid(self, P, U, V, closed=False, mat=0, attrs=None, smooth=True):
        """P (R, C, 3). U, V (R, C+1) if closed (seam column) else (R, C). Returns base vertex index."""
        P = np.asarray(P, float)
        R, Cc = P.shape[:2]
        b = self.n
        self.V.append(P.reshape(-1, 3))
        self.n += R * Cc
        cu = Cc if closed else Cc - 1
        ii, jj = np.meshgrid(np.arange(R - 1), np.arange(cu), indexing="ij")
        ii, jj = ii.ravel(), jj.ravel()
        jn = (jj + 1) % Cc
        self.Q.append(np.stack([b + ii * Cc + jj, b + ii * Cc + jn, b + (ii + 1) * Cc + jn, b + (ii + 1) * Cc + jj], 1))
        U, V = np.asarray(U, float), np.asarray(V, float)
        uv = np.stack([np.stack([U[a, c], V[a, c]], 1) for a, c in
                       ((ii, jj), (ii, jj + 1), (ii + 1, jj + 1), (ii + 1, jj))], 1)
        self.QUV.append(uv)
        self.QM.append(np.full(len(ii), mat))
        self.QS.append(np.full(len(ii), smooth))
        if attrs:
            self.A.append((b, R * Cc, {k: np.broadcast_to(np.asarray(v, float), (R, Cc)).reshape(-1)
                                       for k, v in attrs.items()}))
        return b

    def fan(self, ring, center, mat=0, end=True, attrs=None, smooth=True):
        """Triangle fan closing a ring of existing vertex indices (end=True: normal along the loft)."""
        ci = self.n
        self.V.append(np.asarray(center, float).reshape(1, 3))
        self.n += 1
        ring = np.asarray(ring)
        k = len(ring)
        nxt = np.roll(ring, -1)
        tri = np.stack([np.full(k, ci), ring, nxt], 1) if end else np.stack([np.full(k, ci), nxt, ring], 1)
        self.T.append(tri)
        self.TUV.append(np.zeros((k, 3, 2)))
        self.TM.append(np.full(k, mat))
        self.TS.append(np.full(k, smooth))
        if attrs:
            self.A.append((ci, 1, {kk: np.asarray([vv], float) for kk, vv in attrs.items()}))
        return ci

    def box(self, corners, mat=0, smooth=False, attrs=None):
        """Closed hexahedron from 8 corners ordered (x0y0z0, x1y0z0, x1y1z0, x0y1z0, then z1 ring)."""
        c = np.asarray(corners, float)
        b = self.n
        self.V.append(c)
        self.n += 8
        f = np.array([(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]) + b
        self.Q.append(f)
        uv = np.zeros((6, 4, 2))
        for i, face in enumerate(f - b):
            p = c[face]
            e1 = p[1] - p[0]
            e2 = p[3] - p[0]
            uv[i] = [(0, 0), (np.linalg.norm(e1), 0), (np.linalg.norm(e1), np.linalg.norm(e2)), (0, np.linalg.norm(e2))]
        self.QUV.append(uv)
        self.QM.append(np.full(6, mat))
        self.QS.append(np.full(6, smooth))
        if attrs:
            self.A.append((b, 8, {k: np.full(8, float(v)) for k, v in attrs.items()}))
        return b

    def build(self, name, mats=(), collection=None):
        V = np.concatenate(self.V)
        quads = np.concatenate(self.Q) if self.Q else np.zeros((0, 4), int)
        tris = np.concatenate(self.T) if self.T else np.zeros((0, 3), int)
        me = bpy.data.meshes.new(name)
        me.from_pydata(V.tolist(), [], quads.tolist() + tris.tolist())
        uv = [np.concatenate(self.QUV).reshape(-1)] if self.Q else []
        if self.T:
            uv.append(np.concatenate(self.TUV).reshape(-1))
        uvl = me.uv_layers.new(name="UVMap")
        uvl.data.foreach_set("uv", np.concatenate(uv).astype(np.float32))
        mi = np.concatenate(self.QM + self.TM).astype(np.int32)
        me.polygons.foreach_set("material_index", mi)
        me.polygons.foreach_set("use_smooth", np.concatenate(self.QS + self.TS).astype(bool))
        names = sorted({k for _, _, d in self.A for k in d})
        for nm in names:
            arr = np.zeros(len(V), np.float32)
            for b, cnt, d in self.A:
                if nm in d:
                    arr[b:b + cnt] = d[nm]
            me.attributes.new(nm, "FLOAT", "POINT").data.foreach_set("value", arr)
        for m in mats:
            me.materials.append(m)
        me.update()
        ob = bpy.data.objects.new(name, me)
        link(ob, collection)
        return ob


# =================================================================== polylines / lofts
def _catmull(pts, step):
    """Resample a polyline with a Catmull-Rom spline at roughly `step` spacing (smooth gnarled bends)."""
    P = np.asarray(pts, float)
    if len(P) < 2:
        return P
    ext = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = ext[i:i + 4]
        n = max(1, int(math.ceil(np.linalg.norm(p2 - p1) / step)))
        t = (np.arange(n) / n)[:, None]
        out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1:])
    return np.vstack(out)


def _frames(P):
    """Parallel-transport frames (T, N, B) along a polyline."""
    T = _unit(np.gradient(P, axis=0))
    N = np.zeros_like(P)
    a = np.array([1.0, 0, 0]) if abs(T[0][2]) > 0.9 else np.array([0, 0, 1.0])
    N[0] = _unit(np.cross(T[0], a))
    for i in range(1, len(P)):
        v = N[i - 1] - T[i] * np.dot(N[i - 1], T[i])
        N[i] = v / (np.linalg.norm(v) + 1e-12)
    return T, N, np.cross(T, N)


def _arclen(P):
    return np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])


def _tube(acc, P, r, mat=0, attrs=None, cap_start=False, cap_end=False, smooth=True, frames=None, end_center=None):
    """Loft rings along polyline P (n, 3). r: (n, sides+1) radii, column k at angle 2*pi*k/sides
    (last column = seam copy of the first). U = arc length around (m), V = length along (m)."""
    n, k1 = r.shape
    sides = k1 - 1
    T, N, B = frames if frames is not None else _frames(P)
    th = np.linspace(0, 2 * np.pi, k1)
    ring = N[:, None, :] * np.cos(th)[None, :, None] + B[:, None, :] * np.sin(th)[None, :, None]
    pos = P[:, None, :] + ring * r[..., None]
    s = _arclen(P)
    U = th[None, :] * r.mean(1)[:, None]
    V = np.repeat(s[:, None], k1, 1)
    at = {k: np.broadcast_to(np.asarray(v, float), (n, k1))[:, :-1] for k, v in (attrs or {}).items()}
    b = acc.grid(pos[:, :-1], U, V, closed=True, mat=mat, attrs=at, smooth=smooth)
    cat = {k: float(np.asarray(v[-1]).mean()) for k, v in at.items()}
    if cap_end:
        acc.fan(b + (n - 1) * sides + np.arange(sides), P[-1] if end_center is None else end_center, mat, True, cat,
                smooth)
    if cap_start:
        acc.fan(b + np.arange(sides), P[0], mat, False, {k: float(np.asarray(v[0]).mean()) for k, v in at.items()},
                smooth)
    return b, pos


def _grow(rnd, p0, d0, length, nseg, gnarl, kink, trop):
    """Crooked random-walk polyline: direction jitter (gnarl), occasional sharp kinks, tropism vector."""
    d = _unit(d0)
    pts = [np.asarray(p0, float)]
    step = length / nseg
    trop = np.asarray(trop, float)
    for _ in range(nseg):
        j = np.array([rnd.gauss(0, 1) for _ in range(3)]) * gnarl
        if rnd.random() < kink:
            j *= 3.2
        d = _unit(d + j + trop)
        pts.append(pts[-1] + d * step)
    return np.array(pts)


# =================================================================== trees
TREE_KINDS = {
    # massive gnarled dead oak: thick flared trunk, wide twisting limbs
    "oak": dict(h=(6.5, 9.0), r0=(0.42, 0.58), lean=0.12, limbs=(4, 6), limb_t=(0.32, 0.72), limb_len=(0.5, 0.8),
                spread=(48, 80), gnarl=0.30, kink=0.16, up=0.035, roots=(5, 7), flare=1.7, kids=((3, 4), (3, 5)),
                kid_spread=(28, 62), furrow=0.20, top="taper"),
    # tall leaning tree whose limbs rise then curl like reaching claws
    "claw": dict(h=(10.0, 13.5), r0=(0.30, 0.40), lean=0.22, limbs=(4, 6), limb_t=(0.42, 0.85), limb_len=(0.35, 0.6),
                 spread=(30, 62), gnarl=0.26, kink=0.14, up=0.085, roots=(4, 6), flare=1.4, kids=((3, 4), (4, 6)),
                 kid_spread=(25, 55), furrow=0.17, top="taper"),
    # snapped dead trunk with a few broken stubs
    "snag": dict(h=(3.5, 6.0), r0=(0.32, 0.46), lean=0.10, limbs=(1, 3), limb_t=(0.35, 0.8), limb_len=(0.18, 0.4),
                 spread=(45, 80), gnarl=0.26, kink=0.2, up=0.02, roots=(4, 6), flare=1.5, kids=((1, 2), (2, 3)),
                 kid_spread=(30, 60), furrow=0.22, top="broken"),
    # dead conifer spire: thin tall trunk, whorls of short drooping dead limbs
    "spire": dict(h=(12.0, 16.5), r0=(0.20, 0.27), lean=0.08, limbs=(26, 36), limb_t=(0.18, 0.97),
                  limb_len=(0.07, 0.2), spread=(72, 112), gnarl=0.22, kink=0.12, up=-0.03, roots=(3, 5), flare=1.0,
                  kids=((1, 3), (0, 2)), kid_spread=(30, 65), furrow=0.14, top="taper"),
}


def _bark_radii(nz, P, radii, sides, furrow, seed_z, lumps=0.07, flare=None):
    """Ring radii with lofted bark furrows (ridged noise, periodic around, stretched along) and burls.
    Returns (r, groove) arrays of shape (n, sides+1)."""
    th = np.linspace(0, 2 * np.pi, sides + 1)
    ct, st = np.cos(th)[None, :], np.sin(th)[None, :]
    s = _arclen(P)[:, None] + seed_z
    a = 1.15 if sides > 8 else 0.6
    g = (1.0 - np.abs(nz(ct * a + seed_z, st * a - seed_z, s * 0.5))) ** 6
    lmp = nz.fbm(ct * 0.6 + 3.1, st * 0.6, s * 0.33 + 11.0, octaves=2)
    r = radii[:, None] * (1.0 - furrow * g + lumps * lmp)
    if flare is not None:
        r = r * flare
    return r, g


def _sides_for(r):
    return int(np.clip(round(r * 52), 4, 26))


def _twigs(acc, rnd, P, radii, count, length=(0.25, 0.75)):
    """Crooked hair-thin twigs sprouting from the outer part of a fine branch (scary silhouette detail)."""
    T, N, B = _frames(P)
    n = len(P)
    for _ in range(count):
        i = rnd.randint(int(n * 0.35), n - 1)
        phi = rnd.uniform(0, 2 * math.pi)
        perp = N[i] * math.cos(phi) + B[i] * math.sin(phi)
        ang = math.radians(rnd.uniform(25, 70))
        d = T[i] * math.cos(ang) + perp * math.sin(ang)
        L = rnd.uniform(*length)
        ctrl = _grow(rnd, P[i], d, L, 4, 0.45, 0.25, (0, 0, 0.05))
        Pt = _catmull(ctrl, 0.07)
        r0 = min(radii[i] * 0.6, 0.011)
        rr = 0.0012 + (r0 - 0.0012) * (1 - np.linspace(0, 1, len(Pt)))
        _tube(acc, Pt, np.repeat(rr[:, None], 5, 1), 0, {"groove": 0.2, "lvl": 3.0})


def _branch(acc, rnd, nz, k, p0, d0, L, r0, level, tips, broken=False):
    seg = (0.8, 0.55, 0.32)[min(level - 1, 2)]
    nseg = max(2, int(L / seg))
    up = k["up"] * (1.0, 0.55, -0.4)[min(level - 1, 2)]
    ctrl = _grow(rnd, p0, d0, L, nseg, k["gnarl"] * (1.0 + 0.35 * level), k["kink"], (0, 0, up))
    P = _catmull(ctrl, float(np.clip(r0 * 1.6, 0.06, 0.26)))
    n = len(P)
    t = np.linspace(0, 1, n)
    tip_r = r0 * rnd.uniform(0.35, 0.55) if broken else 0.0025
    radii = tip_r + (r0 - tip_r) * (1 - t) ** (0.6 if broken else 0.95)
    sides = _sides_for(r0)
    fr = _frames(P)
    r, g = _bark_radii(nz, P, radii, sides, k["furrow"] * (0.8 if level == 1 else 0.4), rnd.uniform(0, 50), 0.05)
    _tube(acc, P, r, 0, {"groove": g, "lvl": float(level)}, cap_end=broken, frames=fr,
          end_center=P[-1] - fr[0][-1] * r0 * 0.3 if broken else None)
    if level >= 2 and not broken:
        _twigs(acc, rnd, P, radii, rnd.randint(3, 5) if level >= 3 else rnd.randint(1, 3))
    if level >= 3 or broken:
        tips.append(P[-1])
        return
    lo, hi = k["kids"][level - 1]
    T, N, B = fr
    for _ in range(rnd.randint(lo, hi)):
        tc = rnd.uniform(0.3, 0.95)
        i = min(n - 1, int(tc * (n - 1)))
        phi = rnd.uniform(0, 2 * math.pi)
        perp = N[i] * math.cos(phi) + B[i] * math.sin(phi)
        ang = math.radians(rnd.uniform(*k["kid_spread"]))
        d = T[i] * math.cos(ang) + perp * math.sin(ang)
        cl = L * (1 - tc * 0.45) * rnd.uniform(0.35, 0.68)
        cr = min(radii[i] * 0.72, r0 * rnd.uniform(0.38, 0.58))
        if cr < 0.006 or cl < 0.15:
            continue
        _branch(acc, rnd, nz, k, P[i] - perp * radii[i] * 0.3, d, cl, cr, level + 1, tips,
                broken=(k["top"] == "broken" and rnd.random() < 0.6))


def tree_mesh(name, seed, kind="oak", mat=None):
    """One unique dead tree mesh (origin at the ground point of the trunk). Point attrs: groove (bark
    furrow depth 0..1), lvl (0 trunk/roots .. 3 twigs). Returns the object (with .['tips'] count)."""
    k = TREE_KINDS[kind]
    rnd = random.Random(seed)
    nz = VNoise(seed)
    acc = MeshAcc()
    tips = []
    H = rnd.uniform(*k["h"])
    r0 = rnd.uniform(*k["r0"])
    az = rnd.uniform(0, 2 * math.pi)
    lean = np.array([math.cos(az), math.sin(az), 0.0]) * k["lean"]
    ctrl = _grow(rnd, (0, 0, -0.7), (lean[0], lean[1], 1.0), H + 0.7, max(5, int(H / 1.2)), k["gnarl"] * 0.55,
                 k["kink"] * 0.5, (0, 0, 0.035))
    P = _catmull(ctrl, 0.15)
    n = len(P)
    t = np.linspace(0, 1, n)
    broken = k["top"] == "broken"
    rt = r0 * 0.5 if broken else 0.006
    radii = rt + (r0 - rt) * (1 - t) ** (0.75 if broken else 1.25)
    sides = 26
    fr = _frames(P)
    T, N, B = fr
    hz = _arclen(P) - 0.7                       # height above ground along the trunk
    th = np.linspace(0, 2 * np.pi, sides + 1)
    phis = sorted(rnd.uniform(0, 2 * math.pi) for _ in range(rnd.randint(*k["roots"])))
    lobes = np.zeros_like(th)
    for ph in phis:
        lobes += np.clip(np.cos(th - ph), 0, 1) ** 10 * rnd.uniform(0.7, 1.2)
    F = k["flare"] * np.exp(-np.clip(hz, 0, None) / 0.55)
    flare = 1.0 + F[:, None] * (0.16 + 0.95 * np.clip(lobes, 0, 1.3)[None, :])
    r, g = _bark_radii(nz, P, radii, sides, k["furrow"], rnd.uniform(0, 50), 0.08, flare)
    _tube(acc, P, r, 0, {"groove": g, "lvl": 0.0}, cap_end=broken, frames=fr,
          end_center=P[-1] - T[-1] * r0 * 0.35 if broken else None)
    if broken:   # splinters standing up from the snapped top
        for _ in range(rnd.randint(3, 6)):
            phi = rnd.uniform(0, 2 * math.pi)
            perp = N[-1] * math.cos(phi) + B[-1] * math.sin(phi)
            base = P[-1] + perp * radii[-1] * rnd.uniform(0.5, 0.9) - T[-1] * 0.1
            sp = np.array([base, base + _unit(T[-1] + perp * 0.25) * rnd.uniform(0.3, 0.9)])
            sp = _catmull(np.vstack([sp[0], (sp[0] + sp[1]) / 2 + rnd.uniform(-0.03, 0.03), sp[1]]), 0.1)
            rr = np.linspace(radii[-1] * 0.32, 0.004, len(sp))
            _tube(acc, sp, np.repeat(rr[:, None], 6, 1), 0, {"groove": 0.3, "lvl": 1.0})
    # surface roots, aligned with the buttress lobes
    i0 = int(np.searchsorted(hz, 0.15))
    for ph in phis:
        d = N[i0] * math.cos(ph) + B[i0] * math.sin(ph)
        d = _unit(np.array([d[0], d[1], 0.0]))
        L = rnd.uniform(1.4, 3.0) * r0 / 0.45
        ctrl_r = _grow(rnd, P[i0] + d * r0 * 0.55 + np.array([0, 0, 0.05]), d + np.array([0, 0, -0.18]), L,
                       max(3, int(L / 0.5)), 0.22, 0.1, (0, 0, -0.04))
        Pr = _catmull(ctrl_r, 0.12)
        tr = np.linspace(0, 1, len(Pr))
        rr = 0.02 + (r0 * 0.42 - 0.02) * (1 - tr) ** 1.3
        rr_m, gr = _bark_radii(nz, Pr, rr, 12, 0.12, rnd.uniform(0, 50), 0.1)
        _tube(acc, Pr, rr_m, 0, {"groove": gr, "lvl": 0.0})
    # limbs
    nl = rnd.randint(*k["limbs"])
    ts = sorted(rnd.uniform(*k["limb_t"]) for _ in range(nl))
    golden = math.radians(137.5)
    phi0 = rnd.uniform(0, 2 * math.pi)
    for li, tc in enumerate(ts):
        i = min(n - 2, int(tc * (n - 1)))
        phi = phi0 + li * golden + rnd.uniform(-0.4, 0.4)
        perp = N[i] * math.cos(phi) + B[i] * math.sin(phi)
        ang = math.radians(rnd.uniform(*k["spread"]))
        d = T[i] * math.cos(ang) + perp * math.sin(ang)
        L = H * rnd.uniform(*k["limb_len"]) * (1.0 - 0.35 * tc if kind != "spire" else 1.25 - tc)
        lr = min(radii[i] * 0.78, r0 * rnd.uniform(0.38, 0.55)) if kind != "spire" else radii[i] * 0.4
        _branch(acc, rnd, nz, k, P[i] - perp * radii[i] * 0.3, d, L, lr, 1, tips,
                broken=(broken and rnd.random() < 0.5) or (kind == "spire" and rnd.random() < 0.3))
    if not broken:  # crown: the trunk tip continues as a crooked leader with twigs
        _branch(acc, rnd, nz, k, P[-3], T[-3], H * 0.18, radii[-3] * 0.9, 2, tips)
    ob = acc.build(name, [mat] if mat else [])
    ob["height"] = H
    return ob


def place_instance(src, name, loc, rot_z=0.0, scale=1.0, tilt=(0.0, 0.0), far_mat=None):
    """Linked duplicate of a tree / rock mesh. far_mat: object-linked no-shadow material."""
    ob = bpy.data.objects.new(name, src.data)
    link(ob)
    ob.location = loc
    ob.rotation_euler = (tilt[0], tilt[1], rot_z)
    ob.scale = (scale, scale, scale)
    if far_mat is not None:
        for slot in ob.material_slots:
            slot.link = "OBJECT"
            slot.material = far_mat
    return ob


# =================================================================== shader helpers
def _mr(b, v, a, c, lo=0.0, hi=1.0):
    return b.n("ShaderNodeMapRange", Value=v, **{"From Min": a, "From Max": c, "To Min": lo, "To Max": hi})


def _vm(b, op, a, c=None, scale=None):
    node = b.n("ShaderNodeVectorMath", _operation=op)
    b._in(node, 0, a)
    if c is not None:
        b._in(node, 1, c)
    if scale is not None:
        b._in(node, 3, scale)
    return node


def _sep(b, v):
    return b.n("ShaderNodeSeparateXYZ", Vector=v)


def _comb(b, x=0.0, y=0.0, z=0.0):
    node = b.n("ShaderNodeCombineXYZ")
    for k, v in (("X", x), ("Y", y), ("Z", z)):
        b._in(node, k, v)
    return node


def _noise(b, vec, scale, detail=4.0, rough=0.5, dist=0.0):
    return b.n("ShaderNodeTexNoise", Vector=vec, Scale=scale, Detail=detail, Roughness=rough, Distortion=dist)


def _mapping(b, vec, scale=(1, 1, 1), loc=(0, 0, 0)):
    return b.n("ShaderNodeMapping", Vector=vec, Scale=scale, Location=loc)


def _get(name):
    return bpy.data.materials.get(name)


def _key_time(mat):
    """CTRL_time = frame / FPS seconds: two linear keys + linear extrapolation (pure function of the frame)."""
    s = M.ctrl_node(mat, "time").outputs[0]
    for f, v in ((0, 0.0), (C.FPS, 1.0)):
        s.default_value = v
        s.keyframe_insert("default_value", frame=f)
    fc = mat.node_tree.animation_data.action.fcurves.find('nodes["CTRL_time"].outputs[0].default_value')
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"
    fc.extrapolation = "LINEAR"
    return mat


# =================================================================== materials
def mat_bark(name="forest_bark", shadow=True, tint=(1.0, 1.0, 1.0)):
    """Dead grey-brown bark: lofted furrows (attr groove) + UV-stretched plates and cracks, pale lichen
    on upward faces, dark moss and wet sheen near the ground. UV: U around (m), V along the branch (m)."""
    if _get(name):
        return _get(name)
    m, b = M.new(name)
    if not shadow:
        m.shadow_method = "NONE"
    tc = b.n("ShaderNodeTexCoord")
    geo = b.n("ShaderNodeNewGeometry")
    wp = _sep(b, (geo, "Position"))
    wn = _sep(b, (geo, "Normal"))
    bk = _noise(b, _mapping(b, (tc, "UV"), (7.0, 1.0, 1.0)), 2.4, 8.0, 0.62, 0.5)
    pl = b.n("ShaderNodeTexVoronoi", Vector=_mapping(b, (tc, "UV"), (5.0, 0.8, 1.0)), Scale=1.7, _feature="DISTANCE_TO_EDGE")
    crk = _mr(b, (pl, "Distance"), 0.0, 0.06, 1.0, 0.0)
    groove = b.attr("groove")
    col = b.ramp((bk, "Fac"), [(0.28, tuple(0.016 * c for c in tint)), (0.52, tuple(0.040 * c for c in tint)),
                               (0.78, tuple(0.088 * c for c in tint))])
    col = b.mix(b.math("MULTIPLY", groove, 0.92), col, (0.005, 0.005, 0.005))
    col = b.mix(b.math("MULTIPLY", crk, 0.75), col, (0.004, 0.004, 0.004))
    ln = _noise(b, (geo, "Position"), 1.1, 5.0, 0.6)
    lich = b.math("MULTIPLY", _mr(b, (ln, "Fac"), 0.55, 0.68), _mr(b, (wn, "Z"), 0.0, 0.75))
    lich = b.math("MULTIPLY", lich, b.math("SUBTRACT", 1.0, groove))
    col = b.mix(b.math("MULTIPLY", lich, 0.85), col, (0.15, 0.158, 0.145))
    mn = _noise(b, (geo, "Position"), 2.3, 4.0)
    moss = b.math("MULTIPLY", _mr(b, (wp, "Z"), 1.3, 0.1), _mr(b, (mn, "Fac"), 0.38, 0.6))
    col = b.mix(moss, col, (0.013, 0.019, 0.008))
    rough = b.math("ADD", 0.78, b.math("MULTIPLY", (bk, "Fac"), 0.18))
    rough = b.math("SUBTRACT", rough, b.math("MULTIPLY", _mr(b, (wp, "Z"), 0.6, 0.0), 0.3))
    hgt = b.math("SUBTRACT", b.math("MULTIPLY", (bk, "Fac"), 0.55), b.math("MULTIPLY", groove, 0.8))
    hgt = b.math("SUBTRACT", hgt, b.math("MULTIPLY", crk, 0.4))
    bump = b.n("ShaderNodeBump", Strength=0.75, Distance=0.035, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump})
    bs.inputs["Specular IOR Level"].default_value = 0.4
    b.out(bs)
    return m


def mat_ground(name="forest_ground"):
    """Night forest floor: leaf litter cells, dark moss, wet mud near water (attr wet), trodden path
    (attr path), scorched earth with faint ember fissures (attr burn, CTRL_heat)."""
    if _get(name):
        return _get(name)
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    P = (geo, "Position")
    big = _noise(b, P, 0.09, 3.0)
    mid = _noise(b, P, 0.7, 6.0, 0.6)
    lv = b.n("ShaderNodeTexVoronoi", Vector=P, Scale=7.0)
    lv2 = b.n("ShaderNodeTexVoronoi", Vector=P, Scale=19.0)
    lf = b.math("ADD", b.math("MULTIPLY", _sep(b, (lv, "Color")), 0.6), b.math("MULTIPLY", _sep(b, (lv2, "Color")), 0.4))
    litter = b.ramp(lf, [(0.2, (0.020, 0.016, 0.012)), (0.55, (0.046, 0.036, 0.026)), (0.9, (0.085, 0.07, 0.052))])
    col = b.mix(_mr(b, (mid, "Fac"), 0.38, 0.62), (0.012, 0.011, 0.010), litter)
    moss = _mr(b, (big, "Fac"), 0.46, 0.62)
    col = b.mix(b.math("MULTIPLY", moss, 0.85), col, (0.012, 0.018, 0.009))
    wet, path, burn = b.attr("wet"), b.attr("path"), b.attr("burn")
    col = b.mix(path, col, (0.022, 0.019, 0.016))
    col = b.mix(wet, col, (0.008, 0.0075, 0.007))
    ash = _noise(b, P, 2.2, 5.0, 0.6)
    char = b.ramp((ash, "Fac"), [(0.3, (0.0035, 0.003, 0.0028)), (0.62, (0.012, 0.010, 0.009)),
                                 (0.8, (0.05, 0.048, 0.046))])
    col = b.mix(burn, col, char)
    rough = b.math("SUBTRACT", 0.92, b.math("MULTIPLY", wet, 0.5))
    rough = b.math("SUBTRACT", rough, b.math("MULTIPLY", path, 0.12))
    pn = _noise(b, P, 0.45, 3.0, 0.5)
    puddle = b.math("MULTIPLY", _mr(b, (pn, "Fac"), 0.55, 0.59), b.math("MINIMUM", b.math("MULTIPLY", path, 1.6), 1.0))
    puddle = b.math("MULTIPLY", puddle, b.math("SUBTRACT", 1.0, b.math("MINIMUM", b.math("MULTIPLY", burn, 4.0), 1.0)))
    col = b.mix(puddle, col, (0.0035, 0.0035, 0.004))
    rough = b.math("ADD", b.math("MULTIPLY", rough, b.math("SUBTRACT", 1.0, puddle)), b.math("MULTIPLY", puddle, 0.04))
    hgt = b.math("ADD", b.math("MULTIPLY", (lv, "Distance"), 0.6), b.math("MULTIPLY", (mid, "Fac"), 0.6))
    hgt = b.math("ADD", hgt, b.math("MULTIPLY", (lv2, "Distance"), 0.3))
    bump = b.n("ShaderNodeBump", Distance=0.04, Height=hgt)
    b.link(b.math("MULTIPLY", b.math("SUBTRACT", 1.0, puddle), 0.55), bump.inputs["Strength"])
    # scorched fissures glowing near the hellgate
    warp = _noise(b, P, 0.35, 3.0, 0.5)
    wpos = _vm(b, "ADD", P, _vm(b, "SCALE", (warp, "Color"), scale=1.6))
    fis = b.n("ShaderNodeTexVoronoi", Vector=(wpos, "Vector"), Scale=0.55, _feature="DISTANCE_TO_EDGE")
    fl = _mr(b, (fis, "Distance"), 0.0, 0.022, 1.0, 0.0)
    gate = _mr(b, (_noise(b, P, 0.8, 2.0), "Fac"), 0.48, 0.6)
    heat = b.ctrl("heat", 1.0)
    em = b.math("MULTIPLY", b.math("MULTIPLY", b.math("MULTIPLY", fl, gate), b.math("POWER", burn, 2.5)),
                b.math("MULTIPLY", heat, 4.0))
    col = b.mix(b.math("MULTIPLY", b.math("MULTIPLY", fl, burn), 0.9), col, (0.03, 0.004, 0.0))
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump})
    bs.inputs["Emission Color"].default_value = (*hexcol(EMBER), 1.0)
    b.link(em, bs.inputs["Emission Strength"])
    bs.inputs["Specular IOR Level"].default_value = 0.4
    b.out(bs)
    return m


def mat_rock(name="forest_rock", moss=1.0, base=0.05, wet_z=0.15):
    """Dark wet stone: tonal noise, crevice grime (attr cav), pale worn edges (attr wear), moss on top
    faces, glossy wet band near the water line. Object-space texture (stable on linked duplicates)."""
    if _get(name):
        return _get(name)
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    geo = b.n("ShaderNodeNewGeometry")
    O = (tc, "Object")
    wn = _sep(b, (geo, "Normal"))
    wp = _sep(b, (geo, "Position"))
    n1 = _noise(b, O, 1.4, 8.0, 0.62)
    n2 = _noise(b, O, 7.0, 6.0, 0.6)
    vc = b.n("ShaderNodeTexVoronoi", Vector=O, Scale=2.2, _feature="DISTANCE_TO_EDGE")
    crk = _mr(b, (vc, "Distance"), 0.0, 0.025, 1.0, 0.0)
    col = b.ramp((n1, "Fac"), [(0.3, (base * 0.45,) * 3), (0.55, (base, base * 0.98, base * 0.95)),
                               (0.8, (base * 1.9, base * 1.85, base * 1.8))])
    col = b.mix(b.math("MULTIPLY", b.attr("wear"), 0.5), col, (base * 2.6, base * 2.6, base * 2.5))
    col = b.mix(b.math("MULTIPLY", b.attr("cav"), 0.9), col, (0.004, 0.004, 0.004))
    col = b.mix(b.math("MULTIPLY", crk, 0.8), col, (0.003, 0.003, 0.003))
    mm = b.math("MULTIPLY", _mr(b, (wn, "Z"), 0.35, 0.8), _mr(b, (n2, "Fac"), 0.35, 0.55))
    mm = b.math("MULTIPLY", mm, moss)
    col = b.mix(mm, col, (0.011, 0.017, 0.007))
    wet = b.math("MAXIMUM", _mr(b, (wp, "Z"), wet_z + 0.5, wet_z - 0.2), b.attr("wet"))
    col = b.mix(b.math("MULTIPLY", wet, 0.5), col, (0.004, 0.004, 0.0045))
    rough = b.math("ADD", 0.6, b.math("MULTIPLY", (n2, "Fac"), 0.3))
    rough = b.math("SUBTRACT", rough, b.math("MULTIPLY", wet, 0.3))
    rough = b.math("ADD", rough, b.math("MULTIPLY", mm, 0.25))
    hgt = b.math("SUBTRACT", b.math("ADD", b.math("MULTIPLY", (n1, "Fac"), 0.5), b.math("MULTIPLY", (n2, "Fac"), 0.35)),
                 b.math("MULTIPLY", crk, 0.5))
    bump = b.n("ShaderNodeBump", Strength=0.6, Distance=0.05, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump})
    bs.inputs["Specular IOR Level"].default_value = 0.4
    b.out(bs)
    return m


def mat_water(name="forest_water", speed=0.8):
    """Black moving water. Point attrs on the plane: flow (unit XY vector), speed (0..1), depth (m),
    ring (0..1, impact ripples), rd (m from the impact). Frame-driven streaks advect along `flow`,
    pale foam lines collect in fast / shallow water; SSR-friendly low roughness."""
    if _get(name):
        return _get(name)
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    P = (geo, "Position")
    t = b.ctrl("time", 0.0)
    fl = b.n("ShaderNodeAttribute", _attribute_name="flow", _attribute_type="GEOMETRY")
    sp = b.attr("speed")
    dep = b.attr("depth")
    ring = b.attr("ring")
    rd = b.attr("rd")
    perp = _vm(b, "CROSS_PRODUCT", (fl, "Vector"), (0.0, 0.0, 1.0))
    along = _vm(b, "DOT_PRODUCT", P, (fl, "Vector"))
    across = _vm(b, "DOT_PRODUCT", P, (perp, "Vector"))
    adv = b.math("SUBTRACT", (along, "Value"), b.math("MULTIPLY", t, b.math("MULTIPLY", sp, speed)))
    q1 = _comb(b, b.math("MULTIPLY", (across, "Value"), 1.8), b.math("MULTIPLY", adv, 0.33), b.math("MULTIPLY", t, 0.08))
    st = _noise(b, q1, 1.0, 6.0, 0.62, 0.3)
    q2 = _comb(b, b.math("MULTIPLY", (across, "Value"), 6.0), b.math("MULTIPLY", adv, 2.2), b.math("MULTIPLY", t, 0.5))
    rp = _noise(b, q2, 1.0, 4.0, 0.55)
    # concentric impact ripples (waterfall lake)
    wave = b.math("SINE", b.math("SUBTRACT", b.math("MULTIPLY", rd, 5.0), b.math("MULTIPLY", t, 7.0)))
    hgt = b.math("ADD", b.math("MULTIPLY", (st, "Fac"), 0.5), b.math("MULTIPLY", (rp, "Fac"), 0.35))
    hgt = b.math("ADD", hgt, b.math("MULTIPLY", b.math("MULTIPLY", wave, ring), 0.25))
    bump = b.n("ShaderNodeBump", Strength=0.22, Distance=0.02, Height=hgt)
    # foam: streak crests in fast water + shallow bank lines
    crest = _mr(b, (st, "Fac"), 0.6, 0.74)
    shallow = _mr(b, dep, 0.12, 0.0)
    foam = b.math("MULTIPLY", crest, b.math("ADD", b.math("MULTIPLY", sp, 0.55), b.math("MULTIPLY", shallow, 0.6)),
                  clamp=True)
    foam = b.math("MAXIMUM", foam, b.math("MULTIPLY", b.math("MULTIPLY", _mr(b, (rp, "Fac"), 0.5, 0.7), ring), 0.8))
    col = b.mix(foam, (0.0035, 0.0042, 0.005), (0.16, 0.175, 0.185))
    col = b.mix(b.math("MULTIPLY", shallow, 0.5), col, (0.012, 0.011, 0.009))
    rough = b.math("ADD", 0.035, b.math("MULTIPLY", foam, 0.5))
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump})
    bs.inputs["Specular IOR Level"].default_value = 0.55
    b.out(bs)
    return _key_time(m)


def mat_falls(name="falls_water", speed=5.5, back=False):
    """Falling sheet (alpha hashed). UV: U across (m), V down the fall (m). Point attrs: fall (0 lip ->
    1 base), edge (0 centre -> 1 side). Streaks scroll with CTRL_time; glassy black at the lip,
    aerated pale grey streaks lower down."""
    if _get(name):
        return _get(name)
    # alpha HASHED (not blend): the sheets write depth, so screen-space reflections mirror them in the lake
    m, b = M.new(name, blend="HASHED")
    m.shadow_method = "NONE"
    m.use_backface_culling = False
    tc = b.n("ShaderNodeTexCoord")
    uv = _sep(b, (tc, "UV"))
    t = b.ctrl("time", 0.0)
    vs = b.math("SUBTRACT", (uv, "Y"), b.math("MULTIPLY", t, speed))
    q1 = _comb(b, b.math("MULTIPLY", (uv, "X"), 2.6), b.math("MULTIPLY", vs, 0.22), 3.0 if back else 0.0)
    n1 = _noise(b, q1, 1.0, 8.0, 0.6, 0.2)
    q2 = _comb(b, b.math("MULTIPLY", (uv, "X"), 9.0), b.math("MULTIPLY", vs, 0.7), 7.0)
    n2 = _noise(b, q2, 1.0, 5.0, 0.55)
    fall = b.attr("fall")
    edge = b.attr("edge")
    dens = b.math("ADD", b.math("MULTIPLY", (n1, "Fac"), 0.65), b.math("MULTIPLY", (n2, "Fac"), 0.35))
    streak = _mr(b, dens, 0.42, 0.66)
    white = b.math("MULTIPLY", streak, _mr(b, fall, 0.02, 0.45, 0.25, 1.0))
    alpha = b.math("ADD", b.math("MULTIPLY", streak, b.math("ADD", 0.6, b.math("MULTIPLY", fall, 0.4))),
                   b.math("MULTIPLY", _mr(b, fall, 0.12, 0.0), 0.75))
    alpha = b.math("MULTIPLY", alpha, _mr(b, edge, 0.55, 1.0, 1.0, 0.0))
    alpha = b.math("MULTIPLY", alpha, 0.7 if back else 0.95, clamp=True)
    col = b.mix(white, (0.012, 0.015, 0.018), (0.62, 0.66, 0.7))
    rough = b.math("ADD", 0.06, b.math("MULTIPLY", white, 0.5))
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Alpha": alpha})
    bs.inputs["Emission Color"].default_value = (*MOON_COL, 1.0)
    b.link(b.math("MULTIPLY", b.math("POWER", white, 1.5), b.ctrl("glow", 0.35)), bs.inputs["Emission Strength"])
    bs.inputs["Specular IOR Level"].default_value = 0.6
    b.out(bs)
    return _key_time(m)


def mat_foam(name="falls_foam"):
    """Churning foam disc at the waterfall base: noise advected radially outward (alpha blend)."""
    if _get(name):
        return _get(name)
    m, b = M.new(name, blend="BLEND")
    m.shadow_method = "NONE"
    m.show_transparent_back = False
    tc = b.n("ShaderNodeTexCoord")
    O = _sep(b, (tc, "Object"))
    t = b.ctrl("time", 0.0)
    r = _vm(b, "LENGTH", _comb(b, (O, "X"), (O, "Y"), 0.0))
    ang_c = b.math("DIVIDE", (O, "X"), b.math("ADD", (r, "Value"), 0.01))
    ang_s = b.math("DIVIDE", (O, "Y"), b.math("ADD", (r, "Value"), 0.01))
    rr = b.math("SUBTRACT", (r, "Value"), b.math("MULTIPLY", t, 0.9))
    q = _comb(b, b.math("MULTIPLY", ang_c, 3.0), b.math("MULTIPLY", ang_s, 3.0), b.math("MULTIPLY", rr, 1.4))
    n1 = _noise(b, q, 1.3, 7.0, 0.62)
    n2 = _noise(b, _comb(b, (O, "X"), (O, "Y"), b.math("MULTIPLY", t, 1.5)), 2.6, 4.0)
    dens = b.math("MULTIPLY", _mr(b, (n1, "Fac"), 0.4, 0.62), _mr(b, (n2, "Fac"), 0.3, 0.6, 0.5, 1.0))
    fall = _mr(b, (r, "Value"), 1.0, 5.5, 1.0, 0.0)
    alpha = b.math("MULTIPLY", dens, b.math("POWER", fall, 1.5), clamp=True)
    alpha = b.math("MAXIMUM", alpha, _mr(b, (r, "Value"), 1.6, 0.6))
    bs = b.bsdf(**{"Base Color": (0.38, 0.41, 0.44), "Roughness": 0.55, "Alpha": alpha})
    bs.inputs["Emission Color"].default_value = (*MOON_COL, 1.0)
    bs.inputs["Emission Strength"].default_value = 0.04
    b.out(bs)
    return _key_time(m)


def mat_mist(name="forest_mist", density=0.08, height=3.0, color=(0.62, 0.68, 0.75), scale=0.09,
             wind=(0.5, -0.25, 0.04), aniso=0.35, radial=None, emission=None, z0=0.0, cover=(0.36, 0.66),
             ramp=None):
    """Drifting mist volume. Object coordinates must be metres (mesh built at true size).
    Density falls off above z0 over `height`, broken up by noise (thresholds `cover`: higher = patchier)
    advected by `wind` * CTRL_time. radial=(cx, cy, r): horizontal falloff from a point (spray plume);
    ramp=(axis 0|1|2, a, b): density fades in from coordinate a to b (haze walls that thicken with depth).
    CTRL_density scales the whole volume."""
    if _get(name):
        return _get(name)
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    O = (tc, "Object")
    Os = _sep(b, O)
    t = b.ctrl("time", 0.0)
    off = _vm(b, "SCALE", wind, scale=t)
    q = _vm(b, "SUBTRACT", O, (off, "Vector"))
    n1 = _noise(b, (q, "Vector"), scale, 5.0, 0.6, 0.4)
    n2 = _noise(b, _vm(b, "MULTIPLY", (q, "Vector"), (1.0, 1.0, 2.5)), scale * 3.7, 3.0)
    nn = b.math("ADD", b.math("MULTIPLY", (n1, "Fac"), 0.7), b.math("MULTIPLY", (n2, "Fac"), 0.3))
    blob = _mr(b, nn, cover[0], cover[1])
    hf = b.math("POWER", _mr(b, (Os, "Z"), z0 + height, z0 - 0.4), 1.6)
    dens = b.math("MULTIPLY", b.math("MULTIPLY", blob, hf), b.ctrl("density", density))
    if ramp is not None:
        dens = b.math("MULTIPLY", dens, _mr(b, (Os, "XYZ"[ramp[0]]), ramp[1], ramp[2]))
    if radial is not None:
        cx, cy, rr = radial
        d = _vm(b, "DISTANCE", _comb(b, (Os, "X"), (Os, "Y"), 0.0), (cx, cy, 0.0))
        dens = b.math("MULTIPLY", dens, b.math("POWER", _mr(b, (d, "Value"), rr, 0.0), 1.4))
    pv = b.n("ShaderNodeVolumePrincipled", Color=color, Anisotropy=aniso)
    b.link(dens, pv.inputs["Density"])
    if emission is not None:
        pv.inputs["Emission Color"].default_value = (*emission[0], 1.0)
        b.link(b.math("MULTIPLY", dens, emission[1]), pv.inputs["Emission Strength"])
    b.out(volume=pv)
    return _key_time(m)


def mat_wood(name="board_wood", seed=3, glow_rows=(0, 1, 2), board_w=1.7, z_top=3.5, row_h=0.115,
             n_rows=22, carve=True):
    """Weathered silver-grey planks (grain along object X), rot / moss low down. With carve=True the
    front faces (object -Y) carry rows of carved runic marks: rank / name / score runs whose glyphs are
    Voronoi cell edges (angular, illegible by construction) and a recessed slot at the right of each row.
    Top rows' marks and a few seeded slots glow dim gold / ember / cold blue (CTRL_glow)."""
    if _get(name):
        return _get(name)
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    geo = b.n("ShaderNodeNewGeometry")
    O = (tc, "Object")
    Os = _sep(b, O)
    on = _sep(b, (tc, "Normal"))
    wp = _sep(b, (geo, "Position"))
    grain = _noise(b, _mapping(b, O, (0.5, 3.0, 26.0)), 2.0, 9.0, 0.62, 1.2)
    rings = b.n("ShaderNodeTexWave", Vector=_mapping(b, O, (0.35, 1.0, 9.0)), Scale=3.0, Distortion=7.0, Detail=4.0,
                _bands_direction="Z")
    blot = _noise(b, O, 1.6, 4.0)
    cr = b.n("ShaderNodeTexVoronoi", Vector=_mapping(b, O, (0.25, 1.0, 6.0)), Scale=3.0, _feature="DISTANCE_TO_EDGE")
    crk = _mr(b, (cr, "Distance"), 0.0, 0.035, 1.0, 0.0)
    col = b.ramp((grain, "Fac"), [(0.3, (0.05, 0.046, 0.04)), (0.55, (0.12, 0.112, 0.1)), (0.8, (0.2, 0.19, 0.175))])
    col = b.mix(b.math("MULTIPLY", (rings, "Fac"), 0.3), col, (0.02, 0.017, 0.013))
    col = b.mix(_mr(b, (blot, "Fac"), 0.45, 0.75, 0.0, 0.5), col, (0.022, 0.02, 0.016))
    col = b.mix(b.math("MULTIPLY", crk, 0.85), col, (0.004, 0.0035, 0.003))
    rot = b.math("MULTIPLY", _mr(b, (wp, "Z"), 1.4, 0.2), _mr(b, (blot, "Fac"), 0.35, 0.6))
    col = b.mix(rot, col, (0.012, 0.016, 0.008))
    hgt = b.math("SUBTRACT", b.math("MULTIPLY", (grain, "Fac"), 0.4), b.math("MULTIPLY", crk, 0.6))
    emis = None
    if carve:
        front = _mr(b, (on, "Y"), -0.6, -0.9)
        x0 = -board_w / 2
        xl = b.math("SUBTRACT", (Os, "X"), x0)
        rf = b.math("DIVIDE", b.math("SUBTRACT", z_top, (Os, "Z")), row_h)
        ri = b.math("FLOOR", rf)
        fy = b.math("FRACT", rf)
        inrows = b.math("MULTIPLY", b.math("GREATER_THAN", ri, -0.5), b.math("LESS_THAN", ri, n_rows - 0.5))
        band = b.math("MULTIPLY", _mr(b, fy, 0.2, 0.26), _mr(b, fy, 0.8, 0.74))
        wn = b.n("ShaderNodeTexWhiteNoise", _noise_dimensions="2D")
        b.link(_comb(b, ri, seed * 1.37, 0.0), wn.inputs["Vector"])
        h1 = (wn, "Value")
        wn2 = b.n("ShaderNodeTexWhiteNoise", _noise_dimensions="2D")
        b.link(_comb(b, ri, seed * 2.11 + 5.0, 0.0), wn2.inputs["Vector"])
        h2 = (wn2, "Value")
        name_end = b.math("ADD", 0.26 + 0.25, b.math("MULTIPLY", h1, board_w * 0.42))

        def _run(a, c):
            return b.math("MULTIPLY", b.math("GREATER_THAN", xl, a), b.math("LESS_THAN", xl, c))

        rank = _run(0.06, 0.17)
        nm = b.math("MULTIPLY", b.math("GREATER_THAN", xl, 0.26), b.math("LESS_THAN", xl, name_end))
        score = _run(board_w - 0.52, board_w - 0.3)
        runs = b.math("MAXIMUM", b.math("MAXIMUM", rank, nm), score)
        gv = _comb(b, b.math("DIVIDE", xl, 0.032), b.math("MULTIPLY", fy, 2.0), b.math("MULTIPLY", ri, 3.7))
        gl = b.n("ShaderNodeTexVoronoi", Vector=gv, Scale=1.0, _feature="DISTANCE_TO_EDGE", Randomness=0.9)
        stroke = _mr(b, (gl, "Distance"), 0.03, 0.075, 1.0, 0.0)
        gl2 = b.n("ShaderNodeTexVoronoi", Vector=gv, Scale=1.0, Randomness=0.9)
        keep = b.math("GREATER_THAN", _sep(b, (gl2, "Color")), 0.32)
        glyph = b.math("MULTIPLY", b.math("MULTIPLY", stroke, keep), b.math("MULTIPLY", band, runs))
        glyph = b.math("MULTIPLY", b.math("MULTIPLY", glyph, inrows), front)
        slot = b.math("MULTIPLY", _run(board_w - 0.2, board_w - 0.06), _mr(b, fy, 0.16, 0.2))
        slot = b.math("MULTIPLY", b.math("MULTIPLY", slot, _mr(b, fy, 0.84, 0.8)), b.math("MULTIPLY", inrows, front))
        col = b.mix(b.math("MULTIPLY", glyph, 0.9), col, (0.006, 0.005, 0.004))
        col = b.mix(b.math("MULTIPLY", slot, 0.95), col, (0.004, 0.0035, 0.003))
        hgt = b.math("SUBTRACT", hgt, b.math("ADD", b.math("MULTIPLY", glyph, 0.9), b.math("MULTIPLY", slot, 1.2)))
        # glow: top rows' glyphs (gold), seeded slots (ember / gold / cold blue)
        top = b.math("LESS_THAN", ri, len(glow_rows) - 0.5)
        ember_n = _noise(b, O, 38.0, 3.0, 0.6)
        lit_row = b.math("MAXIMUM", b.math("MULTIPLY", top, b.math("GREATER_THAN", h2, 0.3)), b.math("GREATER_THAN", h2, 0.9))
        gscore = b.math("MULTIPLY", b.math("MULTIPLY", stroke, keep), b.math("MULTIPLY", band, score))
        gscore = b.math("MULTIPLY", b.math("MULTIPLY", gscore, inrows), b.math("MULTIPLY", front, lit_row))
        lit_slot = b.math("MULTIPLY", b.math("MULTIPLY", slot, lit_row), _mr(b, (ember_n, "Fac"), 0.4, 0.7, 0.0, 1.0))
        gc = b.ctrl("glow", 1.0)
        ecol = b.mix(b.math("GREATER_THAN", h1, 0.75), hexcol("#F2B544"), hexcol(EMBER))
        ecol = b.mix(b.math("MULTIPLY", b.math("LESS_THAN", h1, 0.12), b.math("GREATER_THAN", ri, 2.5)), ecol,
                     hexcol("#6FA8FF"))
        flick = _noise(b, _comb(b, ri, b.math("MULTIPLY", b.ctrl("time", 0.0), 1.3), 0.0), 2.0, 1.0)
        estr = b.math("ADD", b.math("MULTIPLY", b.math("MULTIPLY", glyph, top), 0.16), b.math("MULTIPLY", gscore, 0.75))
        estr = b.math("ADD", estr, b.math("MULTIPLY", lit_slot, 0.12))
        estr = b.math("MULTIPLY", b.math("MULTIPLY", estr, gc), _mr(b, (flick, "Fac"), 0.3, 0.7, 0.6, 1.15))
        emis = (ecol, estr)
    bump = b.n("ShaderNodeBump", Strength=0.65, Distance=0.012, Height=hgt)
    rough = b.math("ADD", 0.78, b.math("MULTIPLY", (grain, "Fac"), 0.18))
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump})
    bs.inputs["Specular IOR Level"].default_value = 0.35
    if emis:
        b.link(emis[0], bs.inputs["Emission Color"])
        b.link(emis[1], bs.inputs["Emission Strength"])
    b.out(bs)
    if carve:
        _key_time(m)
    return m


def mat_gate_rock(name="gate_rock"):
    """Black basalt / obsidian of the Hellgate: glossy facets, ember fissures whose glow follows the
    point attr `heat` (1 on the inner rim facing the fire) and flickers with CTRL_time; CTRL_heat scales."""
    if _get(name):
        return _get(name)
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    O = (tc, "Object")
    t = b.ctrl("time", 0.0)
    heat = b.attr("heat")
    warp = _noise(b, O, 0.8, 3.0)
    wv = _vm(b, "ADD", O, _vm(b, "SCALE", (warp, "Color"), scale=0.6))
    v1 = b.n("ShaderNodeTexVoronoi", Vector=(wv, "Vector"), Scale=1.3, _feature="DISTANCE_TO_EDGE")
    v2 = b.n("ShaderNodeTexVoronoi", Vector=(wv, "Vector"), Scale=4.5, _feature="DISTANCE_TO_EDGE")
    c1 = _mr(b, (v1, "Distance"), 0.0, 0.03, 1.0, 0.0)
    c2 = _mr(b, (v2, "Distance"), 0.0, 0.02, 0.7, 0.0)
    crack = b.math("MAXIMUM", c1, c2)
    n1 = _noise(b, O, 2.5, 6.0, 0.6)
    gloss = _mr(b, (n1, "Fac"), 0.5, 0.56)
    col = b.ramp((n1, "Fac"), [(0.3, (0.0025, 0.0024, 0.0024)), (0.7, (0.011, 0.0105, 0.01))])
    col = b.mix(b.math("MULTIPLY", c1, 0.8), col, (0.012, 0.002, 0.0))
    fl = _noise(b, _comb(b, b.math("MULTIPLY", t, 1.7), 0.0, 0.0), 1.0, 2.0)
    # the W socket only exists once the node is 4D: set the dimensions first
    flk = b.n("ShaderNodeTexNoise", _noise_dimensions="4D", Vector=O, Scale=0.9, Detail=1.0)
    b.link(b.math("MULTIPLY", t, 0.9), flk.inputs["W"])
    hc = b.ctrl("heat", 1.0)
    h = b.math("POWER", heat, 1.6)
    estr = b.math("MULTIPLY", b.math("MULTIPLY", crack, h), b.math("MULTIPLY", hc, 6.0))
    estr = b.math("MULTIPLY", estr, b.math("ADD", _mr(b, (flk, "Fac"), 0.35, 0.65, 0.35, 1.2),
                                           b.math("MULTIPLY", (fl, "Fac"), 0.2)))
    ecol = b.ramp(heat, [(0.2, (0.6, 0.03, 0.0)), (0.75, (1.0, 0.22, 0.02)), (1.0, (1.0, 0.45, 0.08))])
    rough = b.mix(gloss, (0.32, 0.32, 0.32), (0.07, 0.07, 0.07))
    hgt = b.math("SUBTRACT", b.math("MULTIPLY", (n1, "Fac"), 0.5), crack)
    bump = b.n("ShaderNodeBump", Strength=0.5, Distance=0.04, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Roughness": (rough[0], rough[1]), "Normal": bump})
    bs.inputs["Specular IOR Level"].default_value = 0.6
    b.link(ecol, bs.inputs["Emission Color"])
    b.link(estr, bs.inputs["Emission Strength"])
    b.out(bs)
    return _key_time(m)


def mat_portal(name="hellgate_vortex", radius=3.0, spin=0.9, twist=2.3, flow=0.32):
    """Swirling fire vortex on a disc in object XZ (normal -Y). Log-polar swirl: flame streaks wind into a
    spiral and are sucked toward a white-hot core (features drift inward with CTRL_time), dark smoke lanes
    break it up, the rim is ragged licking flame (alpha blend). CTRL_portal = intensity."""
    if _get(name):
        return _get(name)
    m, b = M.new(name, blend="BLEND")
    m.shadow_method = "NONE"
    m.show_transparent_back = False
    m.use_backface_culling = False
    tc = b.n("ShaderNodeTexCoord")
    O = _sep(b, (tc, "Object"))
    t = b.ctrl("time", 0.0)
    x, z = (O, "X"), (O, "Z")
    r = b.math("DIVIDE", (_vm(b, "LENGTH", _comb(b, x, z, 0.0)), "Value"), radius)
    a = b.math("ARCTAN2", z, x)
    inv = b.math("SUBTRACT", 1.0, r, clamp=True)
    sw = b.math("ADD", b.math("ADD", a, b.math("MULTIPLY", b.math("POWER", inv, 1.6), twist)), b.math("MULTIPLY", t, spin))
    cs, sn = b.math("COSINE", sw), b.math("SINE", sw)
    lr = b.math("ADD", b.math("LOGARITHM", b.math("ADD", r, 0.04), 2.718), b.math("MULTIPLY", t, flow))

    def polar(ka, kr, off):
        return _comb(b, b.math("MULTIPLY", cs, ka), b.math("MULTIPLY", sn, ka), b.math("ADD", b.math("MULTIPLY", lr, kr), off))

    n1 = _noise(b, polar(1.3, 3.2, 0.0), 1.0, 7.0, 0.62, 1.1)
    n2 = _noise(b, polar(3.4, 9.0, 4.0), 1.0, 4.0, 0.58, 0.6)
    smoke = _noise(b, polar(2.0, 2.2, 9.0), 1.0, 4.0, 0.55, 0.4)
    fire = b.math("ADD", b.math("MULTIPLY", (n1, "Fac"), 0.62), b.math("MULTIPLY", (n2, "Fac"), 0.38))
    fire = b.math("SUBTRACT", fire, b.math("MULTIPLY", _mr(b, (smoke, "Fac"), 0.5, 0.68), 0.3))
    n3 = _noise(b, _comb(b, b.math("MULTIPLY", x, 0.9), b.math("MULTIPLY", z, 0.9), b.math("MULTIPLY", t, 0.7)), 1.0,
                6.0, 0.6, 1.5)
    fire = b.math("ADD", fire, b.math("MULTIPLY", b.math("SUBTRACT", (n3, "Fac"), 0.5), 0.45))
    fire = _mr(b, fire, 0.33, 0.74)
    band = b.math("MULTIPLY", _mr(b, r, 0.62, 0.9), _mr(b, r, 1.0, 0.9))
    fire = b.math("ADD", fire, b.math("MULTIPLY", band, b.math("MULTIPLY", _mr(b, (n3, "Fac"), 0.5, 0.72), 0.55)))
    core = b.math("POWER", _mr(b, r, 0.42, 0.0), 1.7)
    val = b.math("ADD", b.math("MULTIPLY", fire, b.math("ADD", 0.45, b.math("MULTIPLY", core, 0.55))),
                 b.math("MULTIPLY", core, 0.5), clamp=True)
    val = b.math("MULTIPLY", val, _mr(b, r, 1.02, 0.8, 0.7, 1.0))
    rimn = _noise(b, _comb(b, b.math("MULTIPLY", b.math("COSINE", a), 2.4), b.math("MULTIPLY", b.math("SINE", a), 2.4),
                           b.math("MULTIPLY", t, 1.3)), 1.4, 4.0)
    lick = _mr(b, b.math("SUBTRACT", r, b.math("MULTIPLY", (rimn, "Fac"), 0.2)), 0.96, 0.82)
    alpha = b.math("MULTIPLY", lick, b.math("ADD", 0.5, b.math("MULTIPLY", _mr(b, val, 0.05, 0.35), 0.5)))
    ecol = b.ramp(val, [(0.0, (0.0, 0.0, 0.0)), (0.2, (0.10, 0.004, 0.0)), (0.42, (0.62, 0.05, 0.004)),
                        (0.62, (1.0, 0.22, 0.02)), (0.82, (1.0, 0.47, 0.09)), (1.0, (1.0, 0.78, 0.42))])
    pc = b.ctrl("portal", 1.0)
    estr = b.math("MULTIPLY", b.math("ADD", 0.25, b.math("MULTIPLY", b.math("POWER", val, 2.2), 15.0)), pc)
    em = b.n("ShaderNodeEmission", Color=ecol, Strength=estr)
    tr = b.n("ShaderNodeBsdfTransparent")
    mix = b.n("ShaderNodeMixShader")
    b.link(alpha, mix.inputs[0])
    b.link(tr, mix.inputs[1])
    b.link(em, mix.inputs[2])
    b.out(mix)
    return _key_time(m)


def mat_emit(name, color, strength, attr=None, ramp=None):
    """Plain emission (embers / lantern flame); optional per-point attr scaling + colour ramp."""
    if _get(name):
        return _get(name)
    m, b = M.new(name)
    if attr:
        a = b.attr(attr)
        col = b.ramp(a, ramp) if ramp else color
        em = b.n("ShaderNodeEmission", Color=col, Strength=b.math("MULTIPLY", a, strength))
    else:
        em = b.n("ShaderNodeEmission", Color=color, Strength=strength)
    b.out(em)
    return m


# =================================================================== world
def world_night(moon_dir=(0.05, 1.0, 0.45), density=0.006, horizon=(0.055, 0.066, 0.084),
                zenith=(0.0035, 0.005, 0.0075), moon=True, vol_color=(0.62, 0.68, 0.76), aniso=0.55,
                moon_strength=24.0):
    """Night sky gradient + moon disc and halo (behind the world volume), grey-blue world fog."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new("WorldNight")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    md = Vector(moon_dir).normalized()
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.45
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*horizon, 1)
    ramp.color_ramp.elements[1].color = (*zenith, 1)
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    bg = nt.nodes.new("ShaderNodeBackground")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    col = ramp.outputs["Color"]
    if moon:
        dot = nt.nodes.new("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        nt.links.new(tc.outputs["Generated"], dot.inputs[0])
        dot.inputs[1].default_value = tuple(md)
        disc = nt.nodes.new("ShaderNodeMapRange")
        disc.inputs["From Min"].default_value = math.cos(math.radians(1.25))
        disc.inputs["From Max"].default_value = math.cos(math.radians(1.05))
        disc.inputs["To Max"].default_value = moon_strength
        nt.links.new(dot.outputs["Value"], disc.inputs["Value"])
        halo = nt.nodes.new("ShaderNodeMath")
        halo.operation = "POWER"
        clampd = nt.nodes.new("ShaderNodeMath")
        clampd.operation = "MAXIMUM"
        clampd.inputs[1].default_value = 0.0
        nt.links.new(dot.outputs["Value"], clampd.inputs[0])
        nt.links.new(clampd.outputs[0], halo.inputs[0])
        halo.inputs[1].default_value = 90.0
        hs = nt.nodes.new("ShaderNodeMath")
        hs.operation = "MULTIPLY_ADD"
        nt.links.new(halo.outputs[0], hs.inputs[0])
        hs.inputs[1].default_value = 0.35
        nt.links.new(disc.outputs["Result"], hs.inputs[2])
        add = nt.nodes.new("ShaderNodeMix")
        add.data_type = "RGBA"
        add.blend_type = "ADD"
        add.inputs[0].default_value = 1.0
        nt.links.new(col, add.inputs[6])
        mc = nt.nodes.new("ShaderNodeMix")
        mc.data_type = "RGBA"
        mc.blend_type = "MULTIPLY"
        mc.inputs[0].default_value = 1.0
        mc.inputs[6].default_value = (0.85, 0.9, 1.0, 1.0)
        val = nt.nodes.new("ShaderNodeCombineXYZ")
        for i in range(3):
            nt.links.new(hs.outputs[0], val.inputs[i])
        nt.links.new(val.outputs[0], mc.inputs[7])
        nt.links.new(mc.outputs[2], add.inputs[7])
        col = add.outputs[2]
    nt.links.new(col, bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    if density > 0:
        pv = nt.nodes.new("ShaderNodeVolumePrincipled")
        pv.inputs["Density"].default_value = density
        pv.inputs["Color"].default_value = (*vol_color, 1.0)
        pv.inputs["Anisotropy"].default_value = aniso
        nt.links.new(pv.outputs[0], out.inputs["Volume"])
    return w


def tune_eevee(sc=None):
    """Render settings this environment relies on (build_forest calls it; call again after setup_render)."""
    sc = sc or bpy.context.scene
    e = sc.eevee
    e.use_ssr = True
    e.ssr_max_roughness = 0.35
    e.ssr_thickness = 0.4
    e.ssr_border_fade = 0.06
    e.ssr_firefly_fac = 4.0
    e.use_ssr_halfres = True
    e.volumetric_end = max(e.volumetric_end, 150.0)
    # volume SELF-shadowing: a low moon through ~150 m of world fog would black out the haze. Shadow maps
    # (trees, terrain) still cut shafts into the fog without it.
    e.use_volumetric_shadows = False
    e.gtao_distance = 1.0
    e.shadow_cascade_size = "2048"
    e.light_threshold = 0.02
    return sc


# =================================================================== heightfields
def _axis(c, half, n, k=2.4):
    """n coordinates over [c-half, c+half], densest at the centre (sinh spacing)."""
    u = np.linspace(-1.0, 1.0, n)
    return c + half * np.sinh(k * u) / math.sinh(k)


def heightfield(name, xs, ys, Z, attrs=None, keep=None, mats=(), smooth=True):
    """Grid mesh over coordinate vectors xs (nx) and ys (ny) with heights Z (ny, nx).
    attrs {name: (ny, nx) float | (ny, nx, 3) vector} -> point attributes; keep (ny, nx) bool keeps a quad
    when any corner is kept (unused vertices dropped). UVs = world XY in metres."""
    X, Y = np.meshgrid(xs, ys)
    ny, nx = X.shape
    idx = np.arange(nx * ny).reshape(ny, nx)
    q = np.stack([idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]], -1).reshape(-1, 4)
    if keep is not None:
        kq = (keep[:-1, :-1] | keep[:-1, 1:] | keep[1:, 1:] | keep[1:, :-1]).reshape(-1)
        q = q[kq]
    V = np.stack([X, Y, np.broadcast_to(Z, X.shape)], -1).reshape(-1, 3)
    used = np.zeros(len(V), bool)
    used[q.ravel()] = True
    remap = np.full(len(V), -1)
    remap[used] = np.arange(int(used.sum()))
    q = remap[q]
    Vu = V[used]
    me = bpy.data.meshes.new(name)
    me.from_pydata(Vu.tolist(), [], q.tolist())
    uvl = me.uv_layers.new(name="UVMap")
    uvl.data.foreach_set("uv", Vu[q.ravel(), :2].astype(np.float32).ravel())
    me.polygons.foreach_set("use_smooth", np.full(len(q), smooth))
    for nm, arr in (attrs or {}).items():
        a = np.asarray(arr, np.float32)
        if a.ndim == 3:
            at = me.attributes.new(nm, "FLOAT_VECTOR", "POINT")
            at.data.foreach_set("vector", a.reshape(-1, 3)[used].ravel())
        else:
            at = me.attributes.new(nm, "FLOAT", "POINT")
            at.data.foreach_set("value", np.broadcast_to(a, X.shape).reshape(-1)[used])
    for m in mats:
        me.materials.append(m)
    me.update()
    ob = bpy.data.objects.new(name, me)
    link(ob)
    return ob


def _poly_dist(X, Y, pts):
    """Distance from points (X, Y arrays) to a 2-D polyline, the arc length of the nearest point and the
    polyline's unit tangent there (tx, ty)."""
    P = np.asarray(pts, float)[:, :2]
    best = np.full(np.shape(X), 1e9)
    sb, tx, ty = np.zeros(np.shape(X)), np.zeros(np.shape(X)), np.zeros(np.shape(X))
    acc = 0.0
    for a, c in zip(P[:-1], P[1:]):
        d = c - a
        L = float(np.hypot(*d))
        if L < 1e-9:
            continue
        u = d / L
        t = np.clip((X - a[0]) * u[0] + (Y - a[1]) * u[1], 0.0, L)
        dist = np.hypot(X - (a[0] + u[0] * t), Y - (a[1] + u[1] * t))
        m = dist < best
        best = np.where(m, dist, best)
        sb = np.where(m, acc + t, sb)
        tx = np.where(m, u[0], tx)
        ty = np.where(m, u[1], ty)
        acc += L
    return best, sb, tx, ty


def _seg_dist(x, y, a, c):
    """Distance from (x, y) to the 2-D segment a-c (scalars or arrays)."""
    a, c = np.asarray(a, float)[:2], np.asarray(c, float)[:2]
    d = c - a
    L2 = max(1e-9, float(d @ d))
    t = np.clip(((x - a[0]) * d[0] + (y - a[1]) * d[1]) / L2, 0.0, 1.0)
    return np.hypot(x - (a[0] + d[0] * t), y - (a[1] + d[1] * t))


# =================================================================== rocks
def rock_mesh(name, seed, size=(1.0, 1.0, 0.7), facets=12, rough=0.07, subdiv=4, flat_top=None, mat=None):
    """Chiselled boulder: an icosphere clipped by seeded half-spaces (planar facets, flat base), fBm
    displacement and baked wear / cav attributes (pale worn edges, dark crevices). Origin at the base."""
    rnd = random.Random(seed)
    nz = VNoise(seed + 7)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    co = np.array([v.co[:] for v in bm.verts])
    d = _unit(co)
    r = np.full(len(d), 1.25)
    planes = [(_unit(np.array([rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1) * 0.7 + 0.25])), rnd.uniform(0.68, 0.97))
              for _ in range(facets)]
    planes.append((np.array([0.0, 0.0, -1.0]), 0.42))
    if flat_top:
        planes.append((_unit(np.array([rnd.uniform(-0.08, 0.08), rnd.uniform(-0.08, 0.08), 1.0])), flat_top))
    for n, o in planes:
        dn = d @ n
        r = np.where(dn > 0.02, np.minimum(r, o / np.maximum(dn, 0.02)), r)
    p = d * r[:, None]
    p = p + d * (rough * nz.fbm(p[:, 0] * 1.8, p[:, 1] * 1.8, p[:, 2] * 1.8, 4))[:, None]
    p = p + d * (rough * 0.35 * nz.fbm(p[:, 0] * 6.0, p[:, 1] * 6.0, p[:, 2] * 6.0, 3))[:, None]
    p[:, 2] += 0.42
    p = p * np.asarray(size, float)
    for v, q in zip(bm.verts, p):
        v.co = q
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
    ob = bpy.data.objects.new(name, me)
    link(ob)
    G.bake_attributes(ob, mud_top=0, wear_gain=5.0)
    if mat:
        me.materials.append(mat)
    return ob


# =================================================================== mist volumes
def mist_box(name, lo, hi, mat):
    """Axis-aligned volume box built at true size (object coords = world metres)."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    acc = MeshAcc()
    acc.box([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1),
             (x0, y1, z1)], 0)
    ob = acc.build(name, [mat])
    ob.visible_shadow = False
    return ob


# =================================================================== embers (geometry nodes)
def _gn_sock(socks, name, typ):
    for s in socks:
        if s.name == name and s.type == typ:
            return s
    raise KeyError(name)


def _ember_tree(name):
    """GN tree: points carry phase / spd / hgt / sz / dx / dy; each frame (Scene Time) an ember rises
    life = fract(phase + t * spd / hgt) of its column height with a lazy sway and drift, then is
    instanced as a tiny icosphere whose size grows in and dies out (so wrap-around is invisible).
    Stores `life` for the shader."""
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes
    L = ng.links.new
    gi = N.new("NodeGroupInput")
    go = N.new("NodeGroupOutput")
    t = N.new("GeometryNodeInputSceneTime").outputs["Seconds"]

    def attr(nm):
        n = N.new("GeometryNodeInputNamedAttribute")
        n.data_type = "FLOAT"
        n.inputs["Name"].default_value = nm
        return _gn_sock(n.outputs, "Attribute", "VALUE")

    def mth(op, a, c=None):
        n = N.new("ShaderNodeMath")
        n.operation = op
        for i, v in enumerate((a, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L(v, n.inputs[i])
        return n.outputs[0]

    ph, spd, hh, sz, dx, dy = (attr(k) for k in ("phase", "spd", "hgt", "sz", "dx", "dy"))
    life = mth("FRACT", mth("ADD", ph, mth("DIVIDE", mth("MULTIPLY", t, spd), hh)))
    z = mth("MULTIPLY", life, hh)
    wob = mth("SINE", mth("ADD", mth("MULTIPLY", t, 2.3), mth("MULTIPLY", ph, 40.0)))
    wob2 = mth("COSINE", mth("ADD", mth("MULTIPLY", t, 1.7), mth("MULTIPLY", ph, 23.0)))
    x = mth("ADD", mth("MULTIPLY", dx, z), mth("MULTIPLY", wob, mth("MULTIPLY", life, 0.5)))
    y = mth("ADD", mth("MULTIPLY", dy, z), mth("MULTIPLY", wob2, mth("MULTIPLY", life, 0.4)))
    cmb = N.new("ShaderNodeCombineXYZ")
    L(x, cmb.inputs[0])
    L(y, cmb.inputs[1])
    L(z, cmb.inputs[2])
    sp = N.new("GeometryNodeSetPosition")
    L(gi.outputs[0], sp.inputs["Geometry"])
    L(cmb.outputs[0], sp.inputs["Offset"])
    st = N.new("GeometryNodeStoreNamedAttribute")
    st.data_type = "FLOAT"
    st.domain = "POINT"
    st.inputs["Name"].default_value = "life"
    L(sp.outputs[0], st.inputs["Geometry"])
    L(life, _gn_sock(st.inputs, "Value", "VALUE"))
    ico = N.new("GeometryNodeMeshIcoSphere")
    ico.inputs["Radius"].default_value = 1.0
    ico.inputs["Subdivisions"].default_value = 1
    grow = mth("MINIMUM", mth("MULTIPLY", life, 14.0), 1.0)
    die = mth("MINIMUM", mth("MULTIPLY", mth("SUBTRACT", 1.0, life), 6.0), 1.0)
    s = mth("MULTIPLY", sz, mth("MULTIPLY", grow, die))
    inst = N.new("GeometryNodeInstanceOnPoints")
    L(st.outputs[0], inst.inputs["Points"])
    L(ico.outputs["Mesh"], inst.inputs["Instance"])
    L(s, inst.inputs["Scale"])
    real = N.new("GeometryNodeRealizeInstances")
    L(inst.outputs[0], real.inputs[0])
    sm = N.new("GeometryNodeSetMaterial")
    L(real.outputs[0], sm.inputs["Geometry"])
    L(sm.outputs[0], go.inputs[0])
    return ng, sm


def mat_ember(name="forest_embers", strength=40.0):
    """Ember sparks: white-gold when young -> orange -> dull red as they rise (attr life), seeded
    flicker (attr phase + CTRL_time). CTRL_embers scales the brightness."""
    if _get(name):
        return _get(name)
    m, b = M.new(name)
    m.shadow_method = "NONE"
    life = b.attr("life")
    ph = b.attr("phase")
    t = b.ctrl("time", 0.0)
    col = b.ramp(life, [(0.0, (1.0, 0.62, 0.22)), (0.3, (1.0, 0.30, 0.04)), (0.75, (0.75, 0.07, 0.01)),
                        (1.0, (0.3, 0.02, 0.005))])
    fl = _noise(b, _comb(b, b.math("MULTIPLY", ph, 91.0), b.math("MULTIPLY", t, 7.0), 0.0), 1.0, 1.0)
    k = b.ctrl("embers", 1.0)
    estr = b.math("MULTIPLY", b.math("POWER", b.math("SUBTRACT", 1.0, life), 1.3), strength)
    estr = b.math("MULTIPLY", estr, b.math("MULTIPLY", _mr(b, (fl, "Fac"), 0.3, 0.7, 0.35, 1.3), k))
    em = b.n("ShaderNodeEmission", Color=col, Strength=estr)
    b.out(em)
    return _key_time(m)


def embers(name, seed, n, center, radius, height=(4.0, 10.0), rise=(0.7, 1.8), drift=((-0.25, 0.25), (-0.45, -0.05)),
           size=(0.009, 0.022), z_jit=1.5, squash_y=0.6, mat=None):
    """Rising ember sparks around `center` (disc of `radius`, squashed in Y). Positions are a pure
    function of the scene time (GN Scene Time) -> deterministic for any frame, no cache."""
    rnd = random.Random(seed)
    pts, A = [], {k: [] for k in ("phase", "spd", "hgt", "sz", "dx", "dy")}
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r = radius * math.sqrt(rnd.random())
        pts.append((center[0] + r * math.cos(a), center[1] + r * math.sin(a) * squash_y,
                    center[2] + rnd.uniform(0.0, z_jit)))
        A["phase"].append(rnd.random())
        A["spd"].append(rnd.uniform(*rise))
        A["hgt"].append(rnd.uniform(*height))
        A["sz"].append(rnd.uniform(*size) * (2.2 if rnd.random() < 0.06 else 1.0))
        A["dx"].append(rnd.uniform(*drift[0]))
        A["dy"].append(rnd.uniform(*drift[1]))
    me = bpy.data.meshes.new(name)
    me.from_pydata(pts, [], [])
    for k, v in A.items():
        me.attributes.new(k, "FLOAT", "POINT").data.foreach_set("value", np.asarray(v, np.float32))
    ob = bpy.data.objects.new(name, me)
    link(ob)
    ng, sm = _ember_tree(name + "_gn")
    sm.inputs["Material"].default_value = mat or mat_ember()
    mod = ob.modifiers.new("embers", "NODES")
    mod.node_group = ng
    ob.visible_shadow = False
    return ob


# =================================================================== dead reeds
def mat_reed(name="forest_reeds"):
    """Dead dry reeds / tall grass: pale grey-ochre stems, darker and wet at the root (UV V = height, m),
    sheen so they catch the moon backlight."""
    if _get(name):
        return _get(name)
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    uv = _sep(b, (tc, "UV"))
    geo = b.n("ShaderNodeNewGeometry")
    n1 = _noise(b, (geo, "Position"), 3.0, 3.0)
    col = b.ramp((n1, "Fac"), [(0.3, (0.03, 0.028, 0.022)), (0.7, (0.085, 0.075, 0.055))])
    col = b.mix(_mr(b, (uv, "Y"), 0.25, 0.0), col, (0.012, 0.011, 0.009))
    bs = b.bsdf(**{"Base Color": col, "Roughness": 0.62})
    bs.inputs["Sheen Weight"].default_value = 0.3
    bs.inputs["Specular IOR Level"].default_value = 0.25
    b.out(bs)
    return m


def reeds(name, seed, spots, mat, n=(10, 24), h=(0.45, 1.3), radius=0.35):
    """Clumps of dead reeds at spots [(x, y, z)]: thin tapering blades that lean and droop, a few snapped."""
    rnd = random.Random(seed)
    acc = MeshAcc()
    t = np.linspace(0.0, 1.0, 6)
    for x, y, z in spots:
        for _ in range(rnd.randint(*n)):
            b0 = np.array([x + rnd.gauss(0, radius), y + rnd.gauss(0, radius), z - 0.03])
            H = rnd.uniform(*h)
            az = rnd.uniform(0, 2 * math.pi)
            dv = np.array([math.cos(az), math.sin(az), 0.0])
            bend = rnd.uniform(0.05, 0.45) * H
            P = b0[None, :] + dv[None, :] * (bend * t ** 2)[:, None] + np.array([0, 0, 1.0])[None, :] * (H * t)[:, None]
            if rnd.random() < 0.18:                       # snapped: the top folds over
                k = rnd.uniform(0.45, 0.75)
                over = t > k
                P[over, 2] = b0[2] + H * k - (t[over] - k) * H * 0.8
                P[over, :2] += dv[:2] * ((t[over] - k) * H * 0.6)[:, None]
            r = 0.0007 + rnd.uniform(0.004, 0.008) * (1.0 - t)
            _tube(acc, P, np.repeat(r[:, None], 4, 1), 0)
    return acc.build(name, [mat])


def debris(name, seed, F, center, radius, n, mat, length=(0.25, 1.3), r=(0.007, 0.03), avoid=None):
    """Fallen dead sticks and branch pieces lying on the ground around `center` (crooked, partly sunk)."""
    rnd = random.Random(seed)
    acc = MeshAcc()
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        d = radius * math.sqrt(rnd.random())
        x, y = center[0] + d * math.cos(a), center[1] + d * math.sin(a)
        if avoid is not None and avoid(x, y):
            continue
        L = rnd.uniform(*length)
        ang = rnd.uniform(0, 2 * math.pi)
        ctrl = _grow(rnd, (x, y, 0.0), (math.cos(ang), math.sin(ang), 0.0), L, 4, 0.3, 0.2, (0, 0, 0))
        P = _catmull(ctrl, 0.06)
        rr = rnd.uniform(*r)
        P[:, 2] = F.h(P[:, 0:1], P[:, 1:2])[:, 0] + rr * 0.6
        rad = rr * (1.0 - 0.6 * np.linspace(0, 1, len(P))) + 0.002
        _tube(acc, P, np.repeat(rad[:, None], 6, 1), 0, {"groove": 0.4, "lvl": 2.0})
        if rnd.random() < 0.5:                      # a side twig
            i = rnd.randrange(1, len(P) - 1)
            side = _grow(rnd, P[i], (math.cos(ang + 1.2), math.sin(ang + 1.2), 0.15), L * 0.35, 3, 0.4, 0.2, (0, 0, 0))
            Ps = _catmull(side, 0.05)
            _tube(acc, Ps, np.repeat((rad[i] * 0.45 * (1 - 0.7 * np.linspace(0, 1, len(Ps))) + 0.0015)[:, None], 5, 1),
                  0, {"groove": 0.3, "lvl": 3.0})
    return acc.build(name, [mat])


# =================================================================== trees in the set
def _tree_pool(seed, kinds, mat):
    """Unique dead-tree meshes {kind: [mesh objects]} (unlinked from the scene; instanced as linked dupes)."""
    pool = {}
    for i, (kind, cnt) in enumerate(kinds.items()):
        pool[kind] = []
        for j in range(cnt):
            ob = tree_mesh("TREE_%s_%d" % (kind, j), seed * 31 + i * 97 + j * 13, kind, mat)
            bpy.context.scene.collection.objects.unlink(ob)
            pool[kind].append(ob)
    return pool


def _plant(F, pool, rnd, kind, x, y, scale=1.0, rot=None, far_mat=None, tilt=0.06, sink=0.06, var=None):
    srcs = pool[kind]
    src = srcs[var % len(srcs)] if var is not None else srcs[rnd.randrange(len(srcs))]
    z = F.ground_z(x, y) - sink
    ob = place_instance(src, "%s_%03d" % (src.name, len(F.trees)), (x, y, z),
                        rot if rot is not None else rnd.uniform(0, 2 * math.pi), scale,
                        (rnd.uniform(-tilt, tilt), rnd.uniform(-tilt, tilt)), far_mat)
    F.trees.append(ob)
    return ob


def _scatter_trees(F, pool, rnd, n, region, avoid, weights, far_mat, cam, far_d=24.0, min_d=2.6, scale=(0.8, 1.25),
                   tries=40):
    """Rejection-sampled scatter (Poisson-ish, deterministic). avoid(X, Y) -> bool array (vectorised);
    weights: {kind: w}; trees farther than far_d from `cam` use the shadowless far material."""
    x0, x1, y0, y1 = region
    kinds = list(weights)
    wsum = sum(weights.values())
    placed = [(o.location.x, o.location.y) for o in F.trees]
    cand = np.array([(rnd.uniform(x0, x1), rnd.uniform(y0, y1)) for _ in range(n * tries)])
    ok = ~np.asarray(avoid(cand[:, 0], cand[:, 1]), bool)
    cnt = 0
    for x, y in cand[ok]:
        if cnt >= n:
            break
        x, y = float(x), float(y)
        dm = min_d * (1.0 + 0.04 * max(0.0, math.hypot(x - cam[0], y - cam[1]) - 15.0))
        if any((x - px) ** 2 + (y - py) ** 2 < dm * dm for px, py in placed):
            continue
        u = rnd.uniform(0, wsum)
        for kind in kinds:
            u -= weights[kind]
            if u <= 0:
                break
        far = math.hypot(x - cam[0], y - cam[1]) > far_d
        _plant(F, pool, rnd, kind, x, y, rnd.uniform(*scale), far_mat=far_mat if far else None)
        placed.append((x, y))
        cnt += 1
    return cnt


def _fix_normals(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


# =================================================================== cliff + waterfall
CLIFF = dict(c=(0.0, 6.0), r=(25.0, 16.5), a=(math.radians(12.0), math.radians(168.0)), z0=-2.8, top=15.0)
FALLS_A = math.pi / 2


def _cliff_top(nz, a):
    """Cliff crest height along the cliff ellipse angle a (tapers into the ground at both ends,
    dips into a notch where the waterfall pours over)."""
    a = np.asarray(a, float)
    a0, a1 = CLIFF["a"]
    taper = _smooth(a0, a0 + 0.55, a) * _smooth(a1, a1 - 0.55, a)
    top = (CLIFF["top"] + 2.2 * nz.fbm(a * 3.5, 2.2, 0.7, 3) + 1.6 * nz.fbm(a * 16.0, 5.1, 0.2, 3)
           + 5.0 * np.clip(nz(a * 9.0, 8.8, 1.0), 0, None) ** 1.5
           - 1.4 * np.exp(-((a - FALLS_A) / 0.075) ** 2) * (1.0 + 0.0 * a))
    return CLIFF["z0"] + (top - CLIFF["z0"]) * taper


def _cliff_ellipse(X, Y):
    cx, cy = CLIFF["c"]
    rx, ry = CLIFF["r"]
    ex, ey = (X - cx) / rx, (Y - cy) / ry
    return np.hypot(ex, ey), np.arctan2(ey, ex)


def cliff_mesh(name, seed, nz, mat):
    """Strata cliff wall along the upper arc of the CLIFF ellipse, facing the lake: tilted sedimentary beds
    (each recedes toward its top -> ledges and overhangs), vertical joints, a grotto behind the falls
    under an overhanging lip, and a rounded brow rolling back onto the plateau.
    Returns (object, lip) where lip = (x, y, z) at the centre of the waterfall lip."""
    rs = np.random.default_rng(seed)
    cx, cy = CLIFF["c"]
    rx, ry = CLIFF["r"]
    a0, a1 = CLIFF["a"]
    z0 = CLIFF["z0"]
    na, nv = 360, 124
    a = np.linspace(a1, a0, na)                       # left -> right as seen from the lake
    px, py = cx + rx * np.cos(a), cy + ry * np.sin(a)
    nrm = _unit(np.stack([np.cos(a) / rx, np.sin(a) / ry], 1))    # into the cliff
    s = _arclen(np.stack([px, py, np.zeros(na)], 1))
    s_f = float(np.interp(FALLS_A, a[::-1], s[::-1]))
    top = _cliff_top(nz, a)
    v = np.linspace(0, 1, nv)
    Z = z0 + (top[None, :] - z0) * v[:, None]
    S = np.broadcast_to(s[None, :], Z.shape)
    th = rs.uniform(0.45, 1.7, 60)
    zb = z0 - 2.0 + np.concatenate([[0.0], np.cumsum(th)])
    out = rs.uniform(-0.3, 0.9, len(zb))
    ze = Z + 0.03 * (S - s_f)
    k = np.clip(np.searchsorted(zb, ze) - 1, 0, len(zb) - 2)
    tl = (ze - zb[k]) / (zb[k + 1] - zb[k])
    D = out[k] + 0.45 * tl ** 1.5
    for _ in range(2):                                 # soften bed steps a little
        D[1:-1] = 0.25 * D[:-2] + 0.5 * D[1:-1] + 0.25 * D[2:]
    D = D + 0.65 * nz.fbm(S / 5.0, Z / 5.0, 1.7, 4) + 0.22 * nz.fbm(S / 1.1, Z / 1.3, 5.5, 3)
    D = D + 0.7 * (1.0 - np.abs(nz(S / 2.3, 3.3, Z / 16.0))) ** 8          # vertical joints
    g = np.exp(-((S - s_f) / 2.7) ** 2)
    D = D + 2.8 * g * _smooth(top[None, :] - 0.6, top[None, :] - 4.0, Z)    # grotto under the lip
    D = D - 0.5 * g * _smooth(top[None, :] - 1.6, top[None, :] - 0.2, Z)    # lip juts out
    brow_d = np.array([0.35, 0.8, 1.35, 2.1, 3.0, 4.4])
    brow_z = np.array([0.16, 0.27, 0.31, 0.29, 0.22, 0.12])
    Db = D[-1][None, :] + brow_d[:, None] + 0.12 * nz.fbm(S[0][None, :] / 1.5, brow_d[:, None], 9.0, 2)
    Zb = top[None, :] + brow_z[:, None]
    D = np.vstack([D, Db])
    Z = np.vstack([Z, Zb])
    Sx = np.broadcast_to(s[None, :], Z.shape)
    P = np.stack([px[None, :] + nrm[None, :, 0] * D, py[None, :] + nrm[None, :, 1] * D, Z], -1)
    wet = np.clip(1.5 * np.exp(-((Sx - s_f) / 5.5) ** 2) * _smooth(top[None, :] + 0.5, top[None, :] - 2.0, Z), 0, 1)
    acc = MeshAcc()
    acc.grid(P, Sx, Z, attrs={"wet": wet})
    ob = acc.build(name, [mat])
    G.bake_attributes(ob, mud_top=0, wear_gain=4.0)
    j = int(np.argmin(np.abs(s - s_f)))
    lip = (float(P[nv - 1, j, 0]), float(P[nv - 1, j, 1]) - 0.05, float(top[j]) + 0.1)
    return ob, lip


def falls_sheet(name, lip, width, v0, z_end, mat, x_off=0.0, back=0.0, cols=24, rows=64, seed=0, spread=0.6,
                wob=0.18, dirv=(0.0, -1.0)):
    """Ballistic falling sheet thrown from the lip along dirv at v0 m/s, widening as it falls.
    UV: U across (m), V down the fall (m). Point attrs: fall (0 lip -> 1 base), edge (0 centre -> 1 side)."""
    nzz = VNoise(seed + 5)
    g = 9.81
    lip = np.array(lip, float)
    H = lip[2] - z_end
    T = math.sqrt(2.0 * H / g)
    t = T * np.linspace(0.0, 1.0, rows) ** 0.8
    d = np.array([dirv[0], dirv[1], 0.0])
    side = np.array([-dirv[1], dirv[0], 0.0])
    u = np.linspace(-0.5, 0.5, cols)
    fall = t / T
    w = width * (1.0 + spread * fall)
    lat = u[None, :] * w[:, None] + x_off + wob * nzz.fbm(u[None, :] * 2.5, fall[:, None] * 3.0, 1.0, 2) * fall[:, None]
    fwd = (v0 * t)[:, None] - back + 0.1 * nzz(u[None, :] * 4.0, fall[:, None] * 5.0, 3.0) * fall[:, None]
    P = (lip[None, None, :] + d[None, None, :] * fwd[..., None] + side[None, None, :] * lat[..., None]
         + np.array([0.0, 0.0, 1.0])[None, None, :] * (-0.5 * g * t * t)[:, None, None])
    U = np.broadcast_to(u[None, :] * w[:, None], (rows, cols))
    V = np.broadcast_to(_arclen(P[:, cols // 2])[:, None], (rows, cols))
    acc = MeshAcc()
    acc.grid(P, U, V, attrs={"fall": np.broadcast_to(fall[:, None], (rows, cols)),
                             "edge": np.broadcast_to(np.abs(u)[None, :] * 2.0, (rows, cols))})
    ob = acc.build(name, [mat])
    ob.visible_shadow = False
    return ob


def disc(name, center, radius, mat, rings=24, segs=64, plane="XY", r0=0.04):
    """Polar disc mesh (object origin at its centre): plane 'XY' (water foam) or 'XZ' (portal, normal -Y)."""
    r = np.linspace(r0, radius, rings)
    a = np.linspace(0.0, 2 * np.pi, segs, endpoint=False)
    c, s = r[:, None] * np.cos(a)[None, :], r[:, None] * np.sin(a)[None, :]
    P = np.stack([c, s, np.zeros_like(c)], -1) if plane == "XY" else np.stack([c, np.zeros_like(c), s], -1)
    U = np.hstack([c, c[:, :1]])
    V = np.hstack([s, s[:, :1]])
    acc = MeshAcc()
    acc.grid(P, U, V, closed=True)
    ob = acc.build(name, [mat])
    ob.location = center
    ob.visible_shadow = False
    return ob


# =================================================================== ranking boards
BOARDS = [  # x, y, yaw (deg), width, z_top (first carved row, above the post foot), seed
    (-2.6, 3.9, 16.0, 2.05, 3.4, 11),
    (1.0, 6.1, -4.0, 2.3, 4.0, 12),
    (4.5, 3.2, -21.0, 1.9, 3.15, 13),
]


def mat_iron(name="forest_iron"):
    """Old black iron with rust blooms (fittings, nails, lantern cage)."""
    if _get(name):
        return _get(name)
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    O = (tc, "Object")
    n1 = _noise(b, O, 14.0, 6.0, 0.6)
    n2 = _noise(b, O, 60.0, 3.0)
    rust = _mr(b, (n1, "Fac"), 0.5, 0.66)
    col = b.mix(rust, (0.02, 0.019, 0.018), (0.11, 0.045, 0.018))
    rough = b.math("ADD", 0.5, b.math("MULTIPLY", rust, 0.4))
    bump = b.n("ShaderNodeBump", Strength=0.3, Distance=0.003, Height=b.math("ADD", (n2, "Fac"), rust))
    bs = b.bsdf(**{"Base Color": col, "Metallic": b.math("SUBTRACT", 0.85, rust, clamp=True), "Roughness": rough,
                   "Normal": bump})
    b.out(bs)
    return m


def _box8(x0, x1, y0, y1, z0, z1, sag=0.0):
    return [(x0, y0, z0 + sag * x0), (x1, y0, z0 + sag * x1), (x1, y1, z0 + sag * x1), (x0, y1, z0 + sag * x0),
            (x0, y0, z1 + sag * x0), (x1, y0, z1 + sag * x1), (x1, y1, z1 + sag * x1), (x0, y1, z1 + sag * x0)]


def _slab(acc, x0, x1, pa, pb, thick, mat):
    """Box spanning x0..x1 whose bottom face runs from pa to pb in the YZ plane, `thick` along its normal."""
    pa, pb = np.array(pa, float), np.array(pb, float)
    d = _unit(pb - pa)
    n = np.array([-d[1], d[0]]) * thick
    yz = [pa, pa, pb, pb]
    xs = [x0, x1, x1, x0]
    lo = [(x, p[0], p[1]) for x, p in zip(xs, yz)]
    hi = [(x, p[0] + n[0], p[1] + n[1]) for x, p in zip(xs, yz)]
    acc.box(lo + hi, mat)


def ranking_board(F, i, x, y, yaw, w, z_top, seed, bark, iron, flame=None, lantern=False):
    """One weathered leaderboard: horizontal planks (carved runic rows + dim glowing slots, see mat_wood),
    a header plank, back battens, two log posts with split tops, a small gable roof, iron straps and nails,
    optionally an iron lantern on a bracket. All parts share the board's local frame (origin at the
    ground, X along the board, front = -Y). Returns {planks, frame, iron, flame, lantern_pos}."""
    rnd = random.Random(seed)
    nz = VNoise(seed)
    gz = F.ground_z(x, y)
    n_rows = int((z_top - 1.3) / 0.112)
    wood = mat_wood("board_wood_%d" % i, seed=seed, board_w=w, z_top=z_top, row_h=0.112, n_rows=n_rows)
    rot = (rnd.uniform(-0.025, 0.025), rnd.uniform(-0.035, 0.035), math.radians(yaw))
    acc = MeshAcc()
    z, th = 1.08, 0.07
    while z < z_top + 0.12:
        h = rnd.uniform(0.21, 0.31)
        zt = min(z + h, z_top + 0.14)
        xl = -w / 2 - rnd.uniform(0.03, 0.1)
        xr = w / 2 + rnd.uniform(0.03, 0.1)
        if rnd.random() < 0.22:
            xr -= rnd.uniform(0.05, 0.16)
        if rnd.random() < 0.15:
            xl += rnd.uniform(0.05, 0.14)
        sag, yo = rnd.uniform(-0.01, 0.01), rnd.uniform(-0.008, 0.008)
        acc.box(_box8(xl, xr, -th / 2 + yo, th / 2 + yo, z, zt, sag), 0)
        z = zt + rnd.uniform(0.006, 0.018)
    acc.box(_box8(-w / 2 - 0.17, w / 2 + 0.15, -0.055, 0.045, z_top + 0.2, z_top + 0.47, rnd.uniform(-0.02, 0.02)), 0)
    for xb in (-w * 0.3, w * 0.3):
        acc.box(_box8(xb - 0.055, xb + 0.055, th / 2, th / 2 + 0.05, 0.95, z_top + 0.42), 0)
    planks = acc.build("BOARD_%d_planks" % i, [wood])
    _fix_normals(planks)
    G.add_mod(planks, "BEVEL", width=0.007, segments=2, limit_method="ANGLE")
    # posts + roof (log bark)
    fr = MeshAcc()
    xp = w / 2 + 0.15
    for sx in (-1, 1):
        p0 = np.array([sx * xp, 0.08, -0.6])
        p1 = np.array([sx * xp + rnd.uniform(-0.04, 0.04), 0.08 + rnd.uniform(-0.03, 0.03), z_top + 0.95])
        ctrl = np.array([p0, (p0 + p1) / 2 + np.array([rnd.uniform(-0.04, 0.04), rnd.uniform(-0.03, 0.03), 0]), p1])
        P = _catmull(ctrl, 0.08)
        rad = np.full(len(P), rnd.uniform(0.12, 0.15))
        rr, gg = _bark_radii(nz, P, rad, 12, 0.18, rnd.uniform(0, 30), 0.05)
        _tube(fr, P, rr, 0, {"groove": gg, "lvl": 1.0}, cap_end=True,
              end_center=P[-1] + np.array([0, 0, 0.09]))
    zr = z_top + 0.92
    for side in (-1, 1):
        _slab(fr, -w / 2 - 0.42, w / 2 + 0.42, (side * 0.46, zr - 0.3), (0.0, zr), 0.04, 0)
    fr.box(_box8(-w / 2 - 0.3, w / 2 + 0.3, -0.06, 0.06, z_top + 0.5, z_top + 0.62), 0)
    frame = fr.build("BOARD_%d_frame" % i, [bark])
    _fix_normals(frame)
    # iron: straps over the header ends, nail heads on every plank at the battens
    ir = MeshAcc()
    for sx in (-1, 1):
        x0 = sx * (w / 2 + 0.02)
        ir.box(_box8(min(x0, x0 - sx * 0.22), max(x0, x0 - sx * 0.22), -0.068, -0.052, z_top + 0.25, z_top + 0.29), 0)
    zz = 1.2
    while zz < z_top:
        for xb in (-w * 0.3, w * 0.3):
            ir.box(_box8(xb - 0.012, xb + 0.012, -0.05, -0.034, zz - 0.012, zz + 0.012), 0)
        zz += rnd.uniform(0.24, 0.3)
    lantern_pos, fl_ob = None, None
    if lantern:
        bx = xp + 0.02
        bz = z_top + 0.3
        ir.box(_box8(bx - 0.018, bx + 0.018, -0.46, 0.06, bz - 0.018, bz + 0.018), 0)
        lx, ly, lz = bx, -0.42, bz - 0.36
        for cx_, cy_ in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            ir.box(_box8(lx + cx_ * 0.07 - 0.008, lx + cx_ * 0.07 + 0.008, ly + cy_ * 0.07 - 0.008,
                         ly + cy_ * 0.07 + 0.008, lz - 0.13, lz + 0.13), 0)
        ir.box(_box8(lx - 0.095, lx + 0.095, ly - 0.095, ly + 0.095, lz - 0.16, lz - 0.13), 0)
        ir.box(_box8(lx - 0.09, lx + 0.09, ly - 0.09, ly + 0.09, lz + 0.13, lz + 0.17), 0)
        ir.box(_box8(lx - 0.035, lx + 0.035, ly - 0.035, ly + 0.035, lz + 0.17, lz + 0.33), 0)
        fa = MeshAcc()
        fa.box(_box8(lx - 0.022, lx + 0.022, ly - 0.022, ly + 0.022, lz - 0.08, lz + 0.03), 0)
        fl_ob = fa.build("BOARD_%d_flame" % i, [flame])
        G.add_mod(fl_ob, "SUBSURF", levels=2, render_levels=2)
        fl_ob.visible_shadow = False
        lantern_pos = (lx, ly, lz)
    iron_ob = ir.build("BOARD_%d_iron" % i, [iron])
    _fix_normals(iron_ob)
    parts = [planks, frame, iron_ob] + ([fl_ob] if fl_ob else [])
    for ob in parts:
        ob.location = (x, y, gz)
        ob.rotation_euler = rot
    out = {"planks": planks, "frame": frame, "iron": iron_ob, "flame": fl_ob, "wood": wood, "lantern_pos": None}
    if lantern_pos:
        bpy.context.view_layer.update()
        out["lantern_pos"] = tuple(planks.matrix_world @ Vector(lantern_pos))
    return out


# =================================================================== hellgate
GATE = dict(c=(0.0, 6.0), zc=3.45, R=3.95, gap=(math.radians(26.0), math.radians(60.0)), portal_r=3.45)


def gate_ring(name, seed, base_z, mat):
    """Broken ring of jagged black rock standing in the XZ plane (faces -Y): faceted, chunky cross-section
    (heavier at the foot), a broken gap upper-right with eroded ends, outward thorn shards and small hot
    shards on the inner rim. Point attr heat = 1 on the inner rim facing the fire."""
    rnd = random.Random(seed)
    nz = VNoise(seed)
    cx, cy = GATE["c"]
    zc = base_z + GATE["zc"]
    R = GATE["R"]
    g0, g1 = GATE["gap"]
    th = np.linspace(g1, g0 + 2 * math.pi, 320)
    Tn = np.stack([-np.sin(th), np.zeros_like(th), np.cos(th)], 1)
    Nn = np.stack([np.cos(th), np.zeros_like(th), np.sin(th)], 1)
    Bn = np.cross(Tn, Nn)
    C0 = np.array([cx, cy, zc])
    P = C0 + Nn * R
    sides = 11
    ph = np.linspace(0, 2 * np.pi, sides + 1)
    low = _smooth(-0.1, -0.95, np.sin(th))
    a_r = 0.58 + 0.5 * low + 0.3 * nz.fbm(th * 1.9, 0.3, 0.0, 3)
    b_r = 0.48 + 0.32 * low + 0.12 * nz.fbm(th * 2.3, 4.1, 0.0, 2)
    cph, sph = np.cos(ph)[None, :], np.sin(ph)[None, :]
    ell = 1.0 / np.sqrt((cph / a_r[:, None]) ** 2 + (sph / b_r[:, None]) ** 2)
    jag = 1.0 + 0.42 * nz.fbm(cph * 1.4 + th[:, None] * 2.6, sph * 1.4, th[:, None] * 0.7, 4) \
        + 0.28 * (1.0 - np.abs(nz(cph * 2.5 + th[:, None] * 7.0, sph * 2.5, 4.0))) ** 3
    saw = ((th * 11.0 / (2 * np.pi) + 0.5 * nz(th * 3.0, 1.0, 2.0)) % 1.0)
    blocks = (1.0 - 0.22 * saw ** 6 + 0.08 * np.sign(np.sin(th * 5.0 + nz(th, 1.0, 2.0))))[:, None]
    ends = 0.4 + 0.6 * _smooth(0.0, 0.3, th - th[0]) * _smooth(0.0, 0.3, th[-1] - th)
    r = ell * jag * blocks * ends[:, None]
    r[:, -1] = r[:, 0]
    pos = P[:, None, :] + (Nn[:, None, :] * cph[..., None] + Bn[:, None, :] * sph[..., None]) * r[..., None]
    rxz = np.hypot(pos[..., 0] - cx, pos[..., 2] - zc)
    inner = R - a_r[:, None] * 0.9
    heat = np.clip(1.0 - (rxz - inner) / 0.5, 0, 1) ** 2 * _smooth(0.8, 0.2, np.abs(pos[..., 1] - cy))
    acc = MeshAcc()
    _tube(acc, P, r, 0, {"heat": heat}, cap_start=True, cap_end=True, smooth=False, frames=(Tn, Nn, Bn),
          end_center=P[-1] + Tn[-1] * 0.35 + Nn[-1] * 0.2)
    # thorn shards: outward, longer toward the crown
    for k in range(30):
        i = rnd.randrange(12, len(th) - 12)
        if math.sin(th[i]) < -0.55:
            continue
        ang = rnd.uniform(0, 2 * math.pi)
        base = P[i] + (Nn[i] * math.cos(ang) * 0.5 + Bn[i] * math.sin(ang) * 0.35) * a_r[i]
        dirn = _unit(Nn[i] * 1.0 + Tn[i] * rnd.uniform(-0.7, 0.7) + Bn[i] * rnd.uniform(-0.55, 0.55))
        L = rnd.uniform(0.6, 1.5) * (1.0 + 0.8 * max(0.0, math.sin(th[i])))
        mid = base + dirn * L * 0.5 + np.array([rnd.uniform(-0.1, 0.1), rnd.uniform(-0.1, 0.1), rnd.uniform(0, 0.15)])
        Ps = _catmull(np.array([base - dirn * 0.3, mid, base + dirn * L]), 0.1)
        tt = np.linspace(0, 1, len(Ps))
        rad = rnd.uniform(0.15, 0.3) * (1 - tt) ** 1.2 + 0.004
        sd = 5
        wob = np.array([rnd.uniform(0.75, 1.25) for _ in range(sd)] + [0.0])
        wob[-1] = wob[0]
        _tube(acc, Ps, rad[:, None] * wob[None, :], 0, {"heat": 0.0}, smooth=False)
    for k in range(10):                                   # small hot shards on the inner rim
        i = rnd.randrange(12, len(th) - 12)
        base = P[i] - Nn[i] * a_r[i] * 0.55
        dirn = _unit(-Nn[i] + Tn[i] * rnd.uniform(-0.5, 0.5) + Bn[i] * rnd.uniform(-0.4, 0.4))
        L = rnd.uniform(0.25, 0.6)
        Ps = _catmull(np.array([base + dirn * -0.15, base + dirn * L * 0.5, base + dirn * L]), 0.06)
        tt = np.linspace(0, 1, len(Ps))
        rad = rnd.uniform(0.07, 0.13) * (1 - tt) + 0.003
        _tube(acc, Ps, np.repeat(rad[:, None], 6, 1), 0, {"heat": 0.85}, smooth=False)
    ob = acc.build(name, [mat])
    return ob, (cx, cy, zc)


# =================================================================== sets
# Locked layout per variant (metres, Z up, characters face -Y). marks: warrior foot position and
# heading (deg, rb_motion convention: 0 faces -Y, 180 faces +Y), suggested camera / aim, pose.
MARKS = {
    "trees": dict(warrior=(1.45, 1.6), heading=194.0, cam=(0.35, -15.0, 2.3), aim=(0.5, 6.0, 3.7), pose="walk"),
    "waterfall": dict(warrior=(-0.55, -2.35), heading=168.0, cam=(0.9, -12.0, 3.6), aim=(-1.8, 14.0, 1.7),
                      pose="stand"),
    "boards": dict(warrior=(-0.7, -0.35), heading=92.0, cam=(-2.0, -6.9, 0.42), aim=(0.5, 4.0, 2.45), pose="walk"),
    "hellgate": dict(warrior=(0.2, -0.3), heading=180.0, cam=(0.5, -9.5, 1.6), aim=(0.0, 6.0, 2.7), pose="walk"),
}
MOON = {  # direction toward the moon, sun strength, world fog density
    "trees": ((0.24, 1.0, 0.49), 0.75, 0.005),
    "waterfall": ((-0.62, -0.55, 0.62), 1.3, 0.005),
    "boards": ((-0.55, 1.0, 0.5), 0.8, 0.005),
    "hellgate": ((-0.35, 1.0, 1.05), 0.7, 0.005),
}
RIVER = [(18, 112), (12, 74), (7.0, 45), (3.0, 26), (-1.0, 13), (-2.6, 3.0), (-1.6, -5.0), (-0.4, -11.0),
         (-0.8, -20.0), (-3.5, -34), (-8, -50)]
RIVER_PATH = [(4.8, -30), (3.5, -12), (1.6, 1.5), (2.4, 11), (5.5, 22), (9, 40)]
LAKE = dict(c=(0.0, 10.5), r=(19.0, 14.0))
BOARD_PATH = [(-16, -2.0), (-6, -0.9), (0, -0.35), (6, 0.15), (16, 1.6)]
GATE_PATH = [(0.6, -25), (0.35, -8), (0.05, 0.0), (0.0, 6.0)]


class Forest:
    """Handles of one built forest set (see module docstring)."""

    def __init__(self, variant, seed):
        self.variant, self.seed = variant, seed
        self.objects, self.trees, self.rocks, self.mist, self.falls, self.boards, self.portal = [], [], [], [], [], [], []
        self.mats, self.ctrls, self.lights = {}, {}, {}
        self.ground = self.water = self.cliff = self.foam = self.gate = self.embers = self.world = None
        self.marks = dict(MARKS[variant])
        self.h = lambda X, Y: np.zeros(np.shape(X))

    def ground_z(self, x, y):
        """Terrain height (m) at world (x, y) — the same function the ground mesh was built from."""
        return float(np.asarray(self.h(np.array([[float(x)]]), np.array([[float(y)]])))[0, 0])

    def key_ctrl(self, name, frame, value):
        """Key CTRL_<name> on every material of this set that has it (e.g. 'portal', 'heat', 'glow')."""
        for m in self.ctrls.get(name, []):
            M.key_ctrl(m, name, frame, value)


def _ground_base(nz, X, Y, cx, cy, hills=7.0):
    z = 0.3 * nz.fbm(X / 10.0, Y / 10.0, 0.5, 3) + 0.09 * nz.fbm(X / 2.4, Y / 2.4, 3.3, 3)
    R = np.hypot(X - cx, Y - cy)
    return z + hills * _smooth(28.0, 120.0, R) * (0.55 + 0.45 * nz.fbm(X / 26.0, Y / 26.0, 9.1, 2))


def _terrain(F, cx, cy, attr_fn=None, half=100.0, n=257):
    xs, ys = _axis(cx, half, n), _axis(cy, half, n)
    X, Y = np.meshgrid(xs, ys)
    Z = F.h(X, Y)
    attrs = attr_fn(X, Y, Z) if attr_fn else {}
    attrs.setdefault("wet", _smooth(WATER_Z + 0.2, WATER_Z - 0.02, Z))
    for k in ("path", "burn"):
        attrs.setdefault(k, np.zeros_like(Z))
    F.ground = heightfield("FOREST_ground", xs, ys, Z, attrs, mats=[F.mats["ground"]])
    return xs, ys, X, Y, Z


def _water(F, xs, ys, Zg, box, flow, speed, ring=None, rd=None):
    """Water plane at WATER_Z over the terrain cells under water inside box=(x0, x1, y0, y1)."""
    sx = (xs > box[0]) & (xs < box[1])
    sy = (ys > box[2]) & (ys < box[3])
    Zs = Zg[np.ix_(sy, sx)]
    keep = Zs < WATER_Z + 0.03
    sub = lambda a: a[np.ix_(sy, sx)] if np.ndim(a) == 2 else a[np.ix_(sy, sx, np.arange(3))]
    attrs = {"flow": sub(flow), "speed": sub(speed), "depth": np.clip(WATER_Z - Zs, 0, 5),
             "ring": sub(ring) if ring is not None else np.zeros_like(Zs),
             "rd": sub(rd) if rd is not None else np.full_like(Zs, 99.0)}
    F.water = heightfield("FOREST_water", xs[sx], ys[sy], WATER_Z, attrs, keep, [F.mats["water"]])
    F.water.visible_shadow = False
    return F.water


def _rock_pool(seed, mat, n=6, sub=4):
    pool = []
    for i in range(n):
        r = random.Random(seed * 7 + i)
        ob = rock_mesh("ROCK_%d" % i, seed * 7 + i, (r.uniform(0.9, 1.3), r.uniform(0.8, 1.1), r.uniform(0.55, 0.9)),
                       facets=r.randint(9, 14), subdiv=sub, mat=mat)
        bpy.context.scene.collection.objects.unlink(ob)
        pool.append(ob)
    return pool


def _put_rock(F, pool, rnd, x, y, s, sink=0.25, z=None, mat=None):
    src = pool[rnd.randrange(len(pool))]
    zz = (F.ground_z(x, y) if z is None else z) - sink * s
    ob = place_instance(src, "%s_%03d" % (src.name, len(F.rocks)), (x, y, zz), rnd.uniform(0, 2 * math.pi),
                        s, (rnd.uniform(-0.15, 0.15), rnd.uniform(-0.15, 0.15)))
    if mat is not None:
        for slot in ob.material_slots:
            slot.link = "OBJECT"
            slot.material = mat
    F.rocks.append(ob)
    return ob


def _corridor(F, extra=4.0, width=2.6):
    """Vectorised 'keep the view clear' test: near the camera -> warrior sight line (+extra m beyond)."""
    c = np.array(F.marks["cam"][:2], float)
    w = np.array(F.marks["warrior"][:2], float)
    w2 = w + _unit(w - c) * extra
    return lambda X, Y: (_seg_dist(X, Y, c, w2) < width) | (np.hypot(X - c[0], Y - c[1]) < 4.5)


def _fog(F, ground=0.08, height=3.0, z0=0.0, haze=0.022, haze_y=None):
    """Patchy drifting ground mist + a tall haze wall that thickens with depth (camera looks along +Y):
    dark crisp foreground, moonlit fog layers behind -> silhouettes."""
    cy = F.marks["cam"][1]
    a, b = haze_y if haze_y else (cy + 12.0, cy + 45.0)
    F.mist.append(mist_box("FOREST_mist", (-70, cy - 5, z0 - 1.0), (70, 110, z0 + 7.0),
                           mat_mist("forest_mist", density=ground, height=height, z0=z0, cover=(0.42, 0.72),
                                    scale=0.07)))
    F.mist.append(mist_box("FOREST_haze", (-90, a - 2, z0 - 1.0), (90, 140, z0 + 45.0),
                           mat_mist("forest_haze", density=haze, height=40.0, z0=z0, scale=0.025, cover=(0.2, 0.8),
                                    wind=(0.35, 0.0, 0.0), aniso=0.5, ramp=(1, a, b))))


def _set_trees(F, nz, rnd):
    """M101: a slow black river winding out of the fog between twisted dead trees; a trodden path on the
    right bank where the warrior walks."""
    riv = _catmull(np.array(RIVER, float), 1.0)
    pth = _catmull(np.array(RIVER_PATH, float), 1.0)
    cx, cy = 0.0, 8.0

    def hw_of(s):
        return 3.0 + 0.8 * nz(s * 0.045, 7.7, 1.3)

    def h(X, Y):
        z = _ground_base(nz, X, Y, cx, cy)
        d, s, _, _ = _poly_dist(X, Y, riv)
        hw = hw_of(s)
        bank = 2.4 + 0.12 * np.clip(np.hypot(X - cx, Y - cy) - 20.0, 0, None)
        edge = WATER_Z - 0.18
        bed = edge - 0.6 * np.clip(1 - (d / hw) ** 2, 0, 1)
        z = np.where(d < hw, bed, edge + (z - edge) * _smooth(hw, hw + bank, d))
        return z - 0.05 * _smooth(1.2, 0.3, _poly_dist(X, Y, pth)[0])

    F.h = h

    def attrs(X, Y, Z):
        dp = _poly_dist(X, Y, pth)[0]
        return {"path": _smooth(1.3, 0.35, dp) * (0.55 + 0.45 * _smooth(-0.3, 0.3, nz(X * 0.7, Y * 0.7, 5.0)))}

    xs, ys, X, Y, Zg = _terrain(F, cx, cy, attrs)
    d, s, tx, ty = _poly_dist(X, Y, riv)
    flow = np.stack([tx, ty, np.zeros_like(tx)], -1)
    speed = 0.2 + 0.8 * np.clip(1 - (d / hw_of(s)) ** 2, 0, 1)
    _water(F, xs, ys, Zg, (-30, 40, -45, 120), flow, speed)
    rp = _rock_pool(F.seed, F.mats["rock"])
    for _ in range(26):                                   # boulders along both banks, a few in the stream
        k = rnd.randrange(30, len(riv) - 40)
        side = rnd.choice((-1, 1))
        t = _unit(riv[min(k + 1, len(riv) - 1)] - riv[k])
        nrm = np.array([-t[1], t[0]])
        off = side * (hw_of(np.array([k * 1.0]))[0] + rnd.uniform(-0.8, 1.6))
        x, y = riv[k] + nrm * off
        if math.hypot(x - F.marks["warrior"][0], y - F.marks["warrior"][1]) < 1.6:
            continue
        _put_rock(F, rp, rnd, x, y, rnd.uniform(0.35, 1.1))
    spots = []
    for k in range(0, len(riv) - 1, 2):
        if not (-14.0 < riv[k][1] < 16.0):
            continue
        t = _unit(riv[k + 1] - riv[k])
        nrm = np.array([-t[1], t[0]])
        for side in (-1, 1):
            if rnd.random() < 0.45:
                continue
            x, y = riv[k] + nrm * side * (hw_of(np.array([float(k)]))[0] + rnd.uniform(-0.4, 0.9))
            if math.hypot(x - F.marks["warrior"][0], y - F.marks["warrior"][1]) > 1.2:
                spots.append((x, y, F.ground_z(x, y)))
    F.objects.append(reeds("FOREST_reeds", F.seed + 21, spots, mat_reed()))
    F.objects.append(debris("FOREST_debris", F.seed + 23, F, (2.5, -3.0), 9.0, 80, F.mats["bark"],
                            avoid=lambda x, y: _poly_dist(np.array([x]), np.array([y]), riv)[0][0] < hw_of(np.array([0.0]))[0] + 0.3))
    pool = _tree_pool(F.seed, {"oak": 2, "claw": 2, "snag": 2, "spire": 2}, F.mats["bark"])
    fm = F.mats["bark_far"]
    for kind, x, y, sc, rot in (("oak", 4.1, -6.2, 1.25, 2.4), ("claw", -6.8, 8.0, 1.3, 5.3), ("oak", 5.4, 4.6, 1.05, 4.1),
                                ("snag", -4.6, -3.0, 1.05, 1.0), ("claw", 7.0, 13.5, 1.05, 5.3),
                                ("spire", 0.6, 20.0, 1.1, 0.3), ("spire", -6.0, 25.0, 1.15, 1.2),
                                ("oak", -8.5, 17.0, 1.1, 3.0), ("claw", 4.5, 29.0, 1.0, 0.9)):
        _plant(F, pool, rnd, kind, x, y, sc, rot)
    cor = _corridor(F)
    river_d = lambda X, Y: _poly_dist(X, Y, riv)[0]
    pathd = lambda X, Y: _poly_dist(X, Y, pth)[0]
    avoid = lambda X, Y: cor(X, Y) | (river_d(X, Y) < 4.4) | (pathd(X, Y) < 1.5)
    _scatter_trees(F, pool, rnd, 78, (-48, 48, -20, 88), avoid, {"oak": 3, "claw": 3, "snag": 1.5, "spire": 2.5}, fm,
                   F.marks["cam"])
    _fog(F, 0.08, 3.0)


def _set_waterfall(F, nz, rnd):
    """M102: a dark waterfall pouring off a strata cliff into a black lake; the warrior on a rock outcrop at
    the near shore; dead trees on the lake sides and silhouetted on the cliff top."""
    cx, cy = 0.0, 9.0
    lx, ly = LAKE["c"]
    lrx, lry = LAKE["r"]
    a0, a1 = CLIFF["a"]

    def h(X, Y):
        z = _ground_base(nz, X, Y, cx, cy, hills=4.0)
        el = np.hypot((X - lx) / lrx, (Y - ly) / lry)
        edge = WATER_Z - 0.3
        bed = edge - 1.9 * _smooth(0.92, 0.35, el)
        z = np.where(el < 0.92, bed, edge + (z - edge) * _smooth(0.92, 1.14, el))
        ec, ac = _cliff_ellipse(X, Y)
        e_start = 1.16 + 0.26 * np.exp(-((ac - FALLS_A) / 0.13) ** 2)
        plat = _cliff_top(nz, ac) - 0.12 + 0.18 * nz.fbm(X / 3.0, Y / 3.0, 4.4, 2)
        inarc = (ac > a0) & (ac < a1) & (ec > e_start)
        return np.where(inarc, np.maximum(z, plat), z)

    F.h = h
    xs, ys, X, Y, Zg = _terrain(F, cx, cy)
    F.cliff, lip = cliff_mesh("FOREST_cliff", F.seed + 3, nz, F.mats["cliff"])
    F.marks["lip"] = lip
    imp = (lip[0], lip[1] - 2.4, WATER_Z)
    F.marks["impact"] = imp
    for nm, w, v0, xo, back, sd in (("main", 3.0, 1.45, 0.0, 0.0, 1), ("back", 3.8, 0.95, 0.15, -0.35, 2),
                                    ("strandL", 0.9, 1.05, -2.2, -0.1, 3), ("strandR", 0.7, 1.2, 2.0, -0.05, 4)):
        mat = F.mats["falls_back"] if nm == "back" else F.mats["falls"]
        F.falls.append(falls_sheet("FALLS_" + nm, (lip[0], lip[1], lip[2] - (0.05 if nm == "main" else 0.15)), w, v0,
                                   WATER_Z - 0.3, mat, x_off=xo, back=back, seed=sd))
    rdv = np.hypot(X - imp[0], Y - imp[1])
    flow = np.stack([(X - imp[0]) / (rdv + 1e-3), (Y - imp[1]) / (rdv + 1e-3), np.zeros_like(X)], -1)
    ring = _smooth(11.0, 0.0, rdv)
    _water(F, xs, ys, Zg, (-30, 30, -10, 32), flow, 0.05 + 0.35 * ring, ring, rdv)
    F.foam = disc("FALLS_foam", (imp[0], imp[1], WATER_Z + 0.03), 6.5, F.mats["foam"], rings=30, segs=72)
    F.mist.append(mist_box("FALLS_spray", (imp[0] - 10, imp[1] - 9, WATER_Z - 0.3), (imp[0] + 10, imp[1] + 4, 13.0),
                           mat_mist("falls_spray", density=0.9, height=8.0, color=(0.75, 0.8, 0.85), scale=0.35,
                                    wind=(0.1, -0.35, 1.3), aniso=0.55, radial=(imp[0], imp[1] + 0.6, 6.0), z0=WATER_Z,
                                    emission=(MOON_COL, 0.08), cover=(0.4, 0.75))))

    _fog(F, 0.04, 2.2, z0=WATER_Z, haze_y=(4.0, 30.0))
    # the warrior's outcrop + shore rocks + boulders at the cliff foot
    rp = _rock_pool(F.seed, F.mats["rock"])
    wx, wy = F.marks["warrior"]
    out = rock_mesh("ROCK_outcrop", F.seed + 41, (2.5, 2.1, 1.35), facets=13, flat_top=0.55, mat=F.mats["rock"])
    out.location = (wx + 0.15, wy - 0.1, F.ground_z(wx, wy) - 0.32)
    out.rotation_euler = (0.03, -0.02, 0.4)
    F.rocks.append(out)
    bpy.context.view_layer.update()
    hit, loc, _, _ = out.ray_cast(out.matrix_world.inverted() @ Vector((wx, wy, 20.0)),
                                  (out.matrix_world.inverted().to_3x3() @ Vector((0, 0, -1))).normalized())
    F.marks["warrior_z"] = (out.matrix_world @ loc).z if hit else 0.4
    for x, y, s in ((wx - 2.4, wy - 1.0, 1.1), (wx + 2.6, wy + 0.4, 0.9), (wx - 1.2, wy + 1.9, 0.55), (wx + 1.6, wy - 2.4, 0.7),
                    (wx + 4.4, wy - 1.0, 1.3), (wx - 4.6, wy + 0.8, 1.2), (-8.5, 4.0, 1.6), (8.0, 6.5, 1.7),
                    (-6.0, 19.5, 2.4), (5.5, 20.2, 2.1), (-3.6, 21.4, 1.5), (3.4, 21.0, 1.2), (9.5, 17.0, 2.0),
                    (-10.5, 15.0, 2.2), (1.2, 12.0, 0.6), (-2.8, 8.0, 0.5)):
        _put_rock(F, rp, rnd, x, y, s, sink=0.3)
    spots = []
    for k in range(70):
        ang = math.radians(rnd.uniform(200, 340))
        e = rnd.uniform(0.97, 1.1)
        x, y = lx + lrx * e * math.cos(ang), ly + lry * e * math.sin(ang)
        if math.hypot(x - wx, y - wy) > 1.8 and rnd.random() < 0.6:
            spots.append((x, y, F.ground_z(x, y)))
    F.objects.append(reeds("FOREST_reeds", F.seed + 21, spots, mat_reed()))
    pool = _tree_pool(F.seed, {"oak": 2, "claw": 2, "snag": 1, "spire": 2}, F.mats["bark"])
    fm = F.mats["bark_far"]
    for kind, x, y, sc in (("claw", -7.6, -1.0, 1.15), ("oak", 7.4, -3.5, 1.1), ("spire", -11.0, 9.0, 1.1),
                           ("claw", 11.5, 10.0, 1.1), ("snag", -6.6, -7.5, 1.0)):
        _plant(F, pool, rnd, kind, x, y, sc)
    lake_e = lambda X, Y: np.hypot((X - lx) / lrx, (Y - ly) / lry)
    cor = _corridor(F, extra=12.0, width=2.2)
    _scatter_trees(F, pool, rnd, 40, (-42, 42, -16, 22),
                   lambda X, Y: cor(X, Y) | (lake_e(X, Y) < 1.08) | (_cliff_ellipse(X, Y)[0] > 0.93),
                   {"oak": 3, "claw": 3, "snag": 1, "spire": 3}, fm, F.marks["cam"])

    def on_top(X, Y):
        ec, ac = _cliff_ellipse(X, Y)
        return ~((ac > a0 + 0.3) & (ac < a1 - 0.3) & (ec > 1.42) & (ec < 2.4))
    _scatter_trees(F, pool, rnd, 34, (-30, 30, 20, 50), on_top, {"claw": 3, "spire": 3, "oak": 2, "snag": 1}, fm,
                   F.marks["cam"], min_d=3.0)


def _set_boards(F, nz, rnd):
    """M103: three tall weathered ranking boards on log posts in a clearing beside the path."""
    pth = _catmull(np.array(BOARD_PATH, float), 1.0)
    cx, cy = 0.5, 4.0

    def h(X, Y):
        z = _ground_base(nz, X, Y, cx, cy, hills=6.0)
        R = np.hypot(X - cx, Y - cy)
        z = z * (0.45 + 0.55 * _smooth(6.0, 16.0, R))
        return z - 0.05 * _smooth(1.2, 0.3, _poly_dist(X, Y, pth)[0])

    F.h = h

    def attrs(X, Y, Z):
        dp = _poly_dist(X, Y, pth)[0]
        return {"path": _smooth(1.3, 0.35, dp) * (0.55 + 0.45 * _smooth(-0.3, 0.3, nz(X * 0.7, Y * 0.7, 5.0)))}

    _terrain(F, cx, cy, attrs)
    bark = F.mats["post"]
    for i, (x, y, yaw, w, zt, sd) in enumerate(BOARDS):
        bd = ranking_board(F, i, x, y, yaw, w, zt, sd, bark, F.mats["iron"], F.mats["flame"], lantern=(i == 1))
        F.boards.append(bd)
        F.mats["wood_%d" % i] = bd["wood"]
        if bd["lantern_pos"]:
            F.marks["lantern"] = bd["lantern_pos"]
    spots = []
    for (x, y, yaw, w, zt, sd) in BOARDS:
        c, sn = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        for sx in (-1, 1):
            px, py = x + c * sx * (w / 2 + 0.2), y + sn * sx * (w / 2 + 0.2)
            spots.append((px, py, F.ground_z(px, py)))
    for k in range(10):
        x = rnd.uniform(-9, 10)
        y = float(np.interp(x, pth[:, 0], pth[:, 1])) + rnd.uniform(2.0, 4.0)
        spots.append((x, y, F.ground_z(x, y)))
    F.objects.append(reeds("FOREST_reeds", F.seed + 21, spots, mat_reed(), n=(5, 12), h=(0.3, 0.8), radius=0.25))
    F.objects.append(debris("FOREST_debris", F.seed + 23, F, (-0.5, -2.5), 7.5, 90, F.mats["bark"]))
    rp = _rock_pool(F.seed, F.mats["rock"])
    for x, y, s in ((-3.6, 2.8, 0.45), (-1.4, 4.6, 0.3), (2.6, 5.0, 0.38), (5.6, 2.2, 0.5), (-5.2, -2.6, 0.7),
                    (3.4, -2.2, 0.35), (7.5, 4.5, 0.9), (-7.0, 6.0, 1.0)):
        _put_rock(F, rp, rnd, x, y, s)
    pool = _tree_pool(F.seed, {"oak": 2, "claw": 2, "snag": 1, "spire": 2}, F.mats["bark"])
    fm = F.mats["bark_far"]
    for kind, x, y, sc in (("oak", -5.8, 8.5, 1.15), ("claw", 3.0, 11.0, 1.15), ("spire", -1.2, 14.0, 1.1),
                           ("claw", 8.0, 7.5, 1.0), ("snag", -6.8, 1.6, 1.0), ("oak", 6.5, 15.0, 1.0)):
        _plant(F, pool, rnd, kind, x, y, sc)
    cor = _corridor(F, extra=3.0, width=2.0)
    near_boards = lambda X, Y: np.min([np.hypot(X - b[0], Y - b[1]) for b in BOARDS], 0) < 3.2
    _scatter_trees(F, pool, rnd, 70, (-45, 45, -18, 80),
                   lambda X, Y: cor(X, Y) | near_boards(X, Y) | (_poly_dist(X, Y, pth)[0] < 1.6),
                   {"oak": 3, "claw": 3, "snag": 1.5, "spire": 2.5}, fm, F.marks["cam"])
    _fog(F, 0.07, 2.6)


def _set_hellgate(F, nz, rnd):
    """M104: the Hellgate — a broken ring of jagged black rock in a scorched clearing, filled with a
    swirling fire vortex, embers rising, the fog lit red."""
    pth = _catmull(np.array(GATE_PATH, float), 1.0)
    gx, gy = GATE["c"]
    cx, cy = 0.0, 5.0

    def h(X, Y):
        z = _ground_base(nz, X, Y, cx, cy)
        Rg = np.hypot(X - gx, Y - gy)
        z = z * (0.35 + 0.65 * _smooth(7.0, 16.0, Rg)) + 0.35 * np.exp(-(Rg / 3.6) ** 2)
        return z - 0.05 * _smooth(1.2, 0.3, _poly_dist(X, Y, pth)[0])

    F.h = h

    def attrs(X, Y, Z):
        Rg = np.hypot(X - gx, Y - gy)
        dp = _poly_dist(X, Y, pth)[0]
        burn = _smooth(10.5, 2.0, Rg) * (0.6 + 0.4 * _smooth(-0.4, 0.4, nz(X * 0.4, Y * 0.4, 8.0)))
        return {"path": _smooth(1.3, 0.35, dp) * 0.7, "burn": np.clip(burn, 0, 1)}

    _terrain(F, cx, cy, attrs)
    gz = F.ground_z(gx, gy)
    F.gate, ctr = gate_ring("GATE_ring", F.seed + 5, gz, F.mats["gate"])
    F.marks["gate"] = ctr
    pr = GATE["portal_r"]
    F.portal.append(disc("GATE_vortex", ctr, pr, F.mats["portal"], rings=40, segs=96, plane="XZ"))
    F.portal.append(disc("GATE_vortex_back", (ctr[0], ctr[1] + 0.55, ctr[2]), pr * 1.02, F.mats["portal_back"], rings=30,
                         segs=80, plane="XZ"))
    F.mist.append(mist_box("GATE_heat", (gx - 9, gy - 8, gz - 0.6), (gx + 9, gy + 5, gz + 12.0),
                           mat_mist("gate_heat", density=0.06, height=8.0, color=(1.0, 0.55, 0.35), scale=0.22,
                                    wind=(0.0, -0.15, 0.9), aniso=0.25, radial=(gx, gy - 0.9, 6.5),
                                    emission=(hexcol(EMBER), 0.7), z0=gz - 0.4, cover=(0.3, 0.75))))
    _fog(F, 0.05, 2.4, haze_y=(8.0, 40.0))
    F.embers = embers("GATE_embers", F.seed + 9, 420, (gx, gy - 0.4, gz + 0.2), 4.6, height=(4.0, 11.0),
                      rise=(0.8, 2.1), drift=((-0.3, 0.3), (-0.5, -0.08)), mat=F.mats["embers"])
    F.objects.append(embers("GATE_embers_wide", F.seed + 10, 160, (gx, gy - 4.0, gz), 9.0, height=(2.5, 7.0),
                            rise=(0.5, 1.2), drift=((-0.2, 0.2), (-0.3, 0.1)), size=(0.006, 0.014),
                            mat=F.mats["embers"]))
    F.objects.append(debris("FOREST_debris", F.seed + 23, F, (0.0, 1.0), 8.0, 70, F.mats["gate"], r=(0.006, 0.02),
                            avoid=lambda x, y: abs(x) < 0.9 and y < 5.0))
    rp = _rock_pool(F.seed, F.mats["rock"])
    for k in range(14):                                     # black rubble at the gate foot + a fallen piece
        a = rnd.uniform(-0.3, math.pi + 0.3) + math.pi
        r = rnd.uniform(3.2, 5.6)
        x, y = gx + r * math.cos(a), gy + rnd.uniform(-1.6, 1.6)
        if abs(x - gx) < 2.6 and y < gy:
            continue
        _put_rock(F, rp, rnd, x, y, rnd.uniform(0.3, 0.9), mat=F.mats["gate"])
    _put_rock(F, rp, rnd, gx + 3.9, gy - 1.6, 1.25, sink=0.2, mat=F.mats["gate"])
    _put_rock(F, rp, rnd, gx - 4.8, gy - 2.6, 0.55, mat=F.mats["gate"])
    pool = _tree_pool(F.seed, {"oak": 2, "claw": 2, "snag": 2, "spire": 2}, F.mats["bark"])
    fm = F.mats["bark_far"]
    for kind, x, y, sc in (("claw", -9.0, 5.0, 1.2), ("oak", 9.2, 7.5, 1.15), ("snag", -6.5, 11.5, 1.0),
                           ("spire", 5.5, 15.0, 1.15), ("claw", -3.5, 17.0, 1.1), ("snag", 7.0, 1.0, 0.95),
                           ("oak", -8.0, -4.5, 1.1), ("claw", 6.8, -7.0, 1.15)):
        _plant(F, pool, rnd, kind, x, y, sc)
    cor = _corridor(F, extra=0.0, width=2.0)
    _scatter_trees(F, pool, rnd, 70, (-45, 45, -20, 80),
                   lambda X, Y: cor(X, Y) | (np.hypot(X - gx, Y - gy) < 10.0) | (_poly_dist(X, Y, pth)[0] < 1.5),
                   {"oak": 3, "claw": 3, "snag": 1.5, "spire": 2.5}, fm, F.marks["cam"])


def build_forest(variant="trees", seed=101):
    """Build one set of the haunted-forest lobby (see module docstring) and return its Forest handle.
    Also sets the night world (moon + grey-blue fog) and the EEVEE settings it relies on."""
    assert variant in VARIANTS, variant
    F = Forest(variant, seed)
    nz = VNoise(seed)
    rnd = random.Random(seed * 1009 + VARIANTS.index(variant))
    md, _, dens = MOON[variant]
    F.world = world_night(moon_dir=md, density=dens)
    tune_eevee()
    F.mats.update(bark=mat_bark(), bark_far=mat_bark("forest_bark_far", shadow=False), ground=mat_ground(),
                  rock=mat_rock(), water=mat_water())
    if variant == "waterfall":
        F.mats.update(cliff=mat_rock("cliff_rock", moss=0.55, base=0.06, wet_z=WATER_Z + 0.3), falls=mat_falls(),
                      falls_back=mat_falls("falls_water_back", speed=4.6, back=True), foam=mat_foam())
    if variant == "boards":
        F.mats.update(post=mat_bark("post_bark", tint=(1.35, 1.3, 1.2)), iron=mat_iron(),
                      flame=mat_emit("lantern_flame", (1.0, 0.45, 0.12), 60.0))
    if variant == "hellgate":
        F.mats.update(gate=mat_gate_rock(), portal=mat_portal(radius=GATE["portal_r"]),
                      portal_back=mat_portal("hellgate_vortex_back", radius=GATE["portal_r"] * 1.02, spin=-0.7,
                                             twist=3.4),
                      embers=mat_ember())
        M.ctrl_node(F.mats["portal_back"], "portal").outputs[0].default_value = 0.55
    {"trees": _set_trees, "waterfall": _set_waterfall, "boards": _set_boards, "hellgate": _set_hellgate}[variant](F, nz, rnd)
    wz = F.marks.get("warrior_z")
    wx, wy = F.marks["warrior"]
    F.marks["warrior"] = (wx, wy, wz if wz is not None else F.ground_z(wx, wy))
    for m in bpy.data.materials:
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.name.startswith("CTRL_"):
                    F.ctrls.setdefault(n.name[5:], []).append(m)
    F.mats.update({m.name: m for m in bpy.data.materials if m.name.startswith(("forest_mist", "falls_spray", "gate_heat"))})
    return F


# =================================================================== lights
def _L(kind, name, loc, color, energy, target=None, size=0.3, shadow=False, spot=45.0, blend=0.3, volume=1.0,
       specular=1.0):
    ob = C.light(kind, "FOREST_" + name, tuple(loc), color=color, energy=energy, size=size, target=target,
                 shadow=shadow, spot_size=math.radians(spot), blend=blend, volume=volume, specular=specular)
    if shadow and kind != "SUN":
        ob.data.shadow_buffer_bias = 0.02
        ob.data.shadow_buffer_clip_start = 0.3
    return ob


def flicker(light, base, amp=0.12, speed=1.0, phase=0.0):
    """Drive light energy with a pure function of the frame (simple-expression driver, no Python needed)."""
    fc = light.data.driver_add("energy")
    fc.driver.type = "SCRIPTED"
    fc.driver.expression = ("%.4f*(1+%.4f*sin(frame*%.4f+%.3f)+%.4f*sin(frame*%.4f+%.3f)+%.4f*sin(frame*%.4f+%.3f))"
                            % (base, amp, 0.71 * speed, phase, amp * 0.6, 1.93 * speed, phase * 2.1 + 1.3,
                               amp * 0.4, 4.37 * speed, phase * 0.7 + 0.4))
    return light


def ember_rim(warrior, cam, energy=14.0, follow=None, color=EMBER, cutoff=1.15):
    """Ember rim on the warrior (feet position `warrior`) as seen from `cam`: two small point lights just
    behind his shoulders and one behind the hood (on the far side from the camera), with a custom cutoff
    distance so the light dies before it reaches the ground (no orange pool on wet ground / rocks).
    follow: object (e.g. warrior.root) to parent them to, keeping their current world transform — call
    while the warrior stands at `warrior`. Returns [lights]."""
    w, c = Vector(warrior), Vector(cam)
    d = w - c
    d.z = 0
    d.normalize()
    sv = Vector((-d.y, d.x, 0.0))
    out = []
    for nm, off, z, e in (("rimL", 0.55, 1.38, 1.0), ("rimR", -0.55, 1.38, 1.0), ("rimH", 0.15, 1.95, 0.5)):
        ob = _L("POINT", nm, w + d * 0.45 + sv * off + Vector((0, 0, z)), color, energy * e, size=0.1, volume=0.0,
                specular=1.0)
        ob.data.use_custom_distance = True
        ob.data.cutoff_distance = cutoff
        if follow is not None:
            C.parent_keep(ob, follow)
        out.append(ob)
    return out


def lights_forest(variant, forest=None, warrior=None, cam=None, follow=None):
    """Lights for one set: shadowed moon (sun), ember rim on the warrior, faint cold fill from the camera side,
    plus the set's practicals (board lantern; Hellgate fire: shadowed key + spill + ground glow + kickers,
    all flickering by driver). At most 2 shadow casters. follow: parent the rim lights to this object
    (warrior.root) — call with the scene at a frame where the warrior stands at `warrior`.
    Returns {name: light object}."""
    mk = dict(MARKS[variant])
    if forest is not None:
        mk.update(forest.marks)
    W = Vector(warrior if warrior is not None else mk["warrior"])
    if len(W) == 2:
        W = Vector((W.x, W.y, 0.0))
    Cm = Vector(cam if cam is not None else mk["cam"])
    md, me, _ = MOON[variant]
    L = {}
    L["moon"] = _L("SUN", "moon", Vector(md).normalized() * 80.0, MOON_COL, me, target=(0, 0, 0),
                   size=math.radians(1.2), shadow=True)
    sd = L["moon"].data
    sd.shadow_cascade_count = 4
    sd.shadow_cascade_max_distance = 90.0
    sd.shadow_cascade_exponent = 0.8
    sd.shadow_cascade_fade = 0.15
    for ob in ember_rim(W, Cm, follow=follow):
        L[ob.name.replace("FOREST_", "")] = ob
    off = (W - Cm)
    off.z = 0
    off.normalize()
    L["fill"] = _L("POINT", "fill", Cm + off * 1.5 + Vector((-off.y * 2.0, off.x * 2.0, 1.2)), (0.5, 0.6, 0.8), 45.0,
                   size=3.0, volume=0.0, specular=0.25)
    if variant == "waterfall" and "impact" in mk:
        ip = Vector(mk["impact"])
        bl = _L("SPOT", "spray_back", ip + Vector((-3.0, 9.0, 14.0)), MOON_COL, 9000.0, target=ip + Vector((0, -1.0, 2.5)),
                size=2.0, spot=34.0, blend=0.6, volume=1.0)
        bl.data.diffuse_factor = 0.0
        bl.data.specular_factor = 0.0
        L["spray_back"] = bl
        hz = _L("SUN", "haze_back", Vector((0.2, 1.0, 0.3)).normalized() * 80.0, MOON_COL, 0.7, target=(0, 0, 0),
                size=math.radians(2.0), volume=1.0)
        hz.data.diffuse_factor = 0.0
        hz.data.specular_factor = 0.0
        L["haze_back"] = hz

    if variant == "boards":
        if "lantern" in mk:
            L["lantern"] = flicker(_L("POINT", "lantern", mk["lantern"], (1.0, 0.48, 0.16), 55.0, size=0.08,
                                      volume=0.5), 55.0, 0.1, 1.6, 0.5)
        sky = _L("SPOT", "sky_fill", (-5.0, -9.0, 7.5), (0.55, 0.65, 0.85), 4500.0, target=(0.9, 4.6, 2.7), size=3.0,
                 spot=36.0, blend=0.45, volume=0.0, specular=0.4)
        L["sky_fill"] = sky
    if variant == "hellgate":
        g = Vector(mk["gate"])
        L["portal"] = flicker(_L("POINT", "portal", g + Vector((0, -0.9, -0.4)), (1.0, 0.3, 0.07), 1500.0, size=2.0,
                                 shadow=True, volume=0.8), 1500.0, 0.14, 1.0, 0.0)
        sp = _L("AREA", "portal_spill", g + Vector((0, -0.6, -0.3)), (1.0, 0.26, 0.06), 300.0, size=5.0, volume=0.3,
                specular=0.5)
        sp.rotation_euler = (math.radians(90), 0, 0)
        L["portal_spill"] = flicker(sp, 300.0, 0.16, 1.2, 1.1)
        L["ground_glow"] = flicker(_L("POINT", "ground_glow", g + Vector((0, -1.8, -3.0)), (1.0, 0.25, 0.05), 90.0,
                                      size=1.5, volume=0.2), 90.0, 0.2, 1.5, 2.0)
        for nm, p in (("kickL", (-8.0, 7.0, 3.0)), ("kickR", (8.5, 8.0, 3.5))):
            L[nm] = flicker(_L("POINT", nm, Vector(p), (1.0, 0.3, 0.08), 220.0, size=1.0, volume=0.5, specular=0.4),
                            220.0, 0.15, 0.9, len(nm))
    if forest is not None:
        forest.lights = L
    return L
