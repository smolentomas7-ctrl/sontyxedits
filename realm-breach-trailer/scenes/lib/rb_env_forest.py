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
    "spire": dict(h=(12.0, 16.5), r0=(0.20, 0.27), lean=0.08, limbs=(10, 15), limb_t=(0.22, 0.97), limb_len=(0.09, 0.2),
                  spread=(78, 112), gnarl=0.20, kink=0.10, up=-0.02, roots=(3, 5), flare=1.0, kids=((1, 3), (0, 2)),
                  kid_spread=(30, 60), furrow=0.14, top="taper"),
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
    if broken:   # splintered top: jagged last rings
        jag = np.array([rnd.uniform(0, 0.35) for _ in range(sides)] + [0.0])
        jag[-1] = jag[0]
        P = P.copy()
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
    wet = b.attr("wet")
    path = b.attr("path")
    burn = b.attr("burn")
    col = b.mix(path, col, (0.016, 0.014, 0.012))
    col = b.mix(wet, col, (0.007, 0.0068, 0.0065))
    char = b.ramp((mid, "Fac"), [(0.3, (0.004, 0.0035, 0.003)), (0.7, (0.02, 0.016, 0.012))])
    col = b.mix(burn, col, char)
    rough = b.math("SUBTRACT", 0.92, b.math("MULTIPLY", wet, 0.62))
    rough = b.math("SUBTRACT", rough, b.math("MULTIPLY", path, 0.3))
    hgt = b.math("ADD", b.math("MULTIPLY", (lv, "Distance"), 0.6), b.math("MULTIPLY", (mid, "Fac"), 0.6))
    hgt = b.math("ADD", hgt, b.math("MULTIPLY", (lv2, "Distance"), 0.3))
    bump = b.n("ShaderNodeBump", Strength=0.55, Distance=0.04, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump})
    # scorched fissures glowing near the hellgate
    fis = b.n("ShaderNodeTexVoronoi", Vector=_mapping(b, P, (1.0, 1.0, 1.0)), Scale=0.9, _feature="DISTANCE_TO_EDGE")
    fl = _mr(b, (fis, "Distance"), 0.0, 0.035, 1.0, 0.0)
    heat = b.ctrl("heat", 1.0)
    em = b.math("MULTIPLY", b.math("MULTIPLY", fl, b.math("POWER", burn, 3.0)), b.math("MULTIPLY", heat, 3.0))
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
    wet = _mr(b, (wp, "Z"), wet_z + 0.5, wet_z - 0.2)
    col = b.mix(b.math("MULTIPLY", wet, 0.5), col, (0.004, 0.004, 0.0045))
    rough = b.math("ADD", 0.6, b.math("MULTIPLY", (n2, "Fac"), 0.3))
    rough = b.math("SUBTRACT", rough, b.math("MULTIPLY", wet, 0.45))
    rough = b.math("ADD", rough, b.math("MULTIPLY", mm, 0.25))
    hgt = b.math("SUBTRACT", b.math("ADD", b.math("MULTIPLY", (n1, "Fac"), 0.5), b.math("MULTIPLY", (n2, "Fac"), 0.35)),
                 b.math("MULTIPLY", crk, 0.5))
    bump = b.n("ShaderNodeBump", Strength=0.6, Distance=0.05, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump})
    bs.inputs["Specular IOR Level"].default_value = 0.5
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
    """Falling sheet (alpha blend). UV: U across (m), V down the fall (m). Point attrs: fall (0 lip ->
    1 base), edge (0 centre -> 1 side). Streaks scroll with CTRL_time; glassy black at the lip,
    aerated pale grey streaks lower down."""
    if _get(name):
        return _get(name)
    m, b = M.new(name, blend="BLEND")
    m.shadow_method = "NONE"
    m.show_transparent_back = False
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
    alpha = b.math("ADD", b.math("MULTIPLY", streak, 0.9), b.math("MULTIPLY", _mr(b, fall, 0.12, 0.0), 0.75))
    alpha = b.math("MULTIPLY", alpha, _mr(b, edge, 0.55, 1.0, 1.0, 0.0))
    alpha = b.math("MULTIPLY", alpha, 0.7 if back else 0.95, clamp=True)
    col = b.mix(white, (0.012, 0.015, 0.018), (0.42, 0.46, 0.49))
    rough = b.math("ADD", 0.06, b.math("MULTIPLY", white, 0.5))
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Alpha": alpha})
    bs.inputs["Emission Color"].default_value = (*MOON_COL, 1.0)
    b.link(b.math("MULTIPLY", white, 0.05), bs.inputs["Emission Strength"])
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
             wind=(0.5, -0.25, 0.04), aniso=0.35, radial=None, emission=None, z0=0.0):
    """Drifting ground-mist volume. Object coordinates must be metres (mesh built at true size).
    Density falls off above z0 over `height`, broken up by noise advected by `wind` * CTRL_time.
    radial=(cx, cy, r): extra horizontal falloff from a point (waterfall spray plume)."""
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
    blob = _mr(b, nn, 0.36, 0.66)
    hf = b.math("POWER", _mr(b, (Os, "Z"), z0 + height, z0 - 0.4), 1.6)
    dens = b.math("MULTIPLY", b.math("MULTIPLY", blob, hf), density)
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
    col = b.ramp((grain, "Fac"), [(0.3, (0.030, 0.027, 0.023)), (0.55, (0.070, 0.064, 0.056)), (0.8, (0.125, 0.12, 0.11))])
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
        lit_slot = b.math("MULTIPLY", slot, b.math("MAXIMUM", top, b.math("GREATER_THAN", h2, 0.8)))
        gc = b.ctrl("glow", 1.0)
        ecol = b.mix(b.math("GREATER_THAN", h1, 0.75), hexcol("#F2B544"), hexcol(EMBER))
        ecol = b.mix(b.math("MULTIPLY", b.math("LESS_THAN", h1, 0.12), b.math("GREATER_THAN", ri, 2.5)), ecol,
                     hexcol("#6FA8FF"))
        flick = _noise(b, _comb(b, ri, b.math("MULTIPLY", b.ctrl("time", 0.0), 1.3), 0.0), 2.0, 1.0)
        estr = b.math("ADD", b.math("MULTIPLY", b.math("MULTIPLY", glyph, top), 0.55), b.math("MULTIPLY", lit_slot, 2.2))
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
    col = b.ramp((n1, "Fac"), [(0.3, (0.006, 0.0055, 0.0055)), (0.7, (0.026, 0.024, 0.023))])
    col = b.mix(crack, col, (0.02, 0.003, 0.0))
    fl = _noise(b, _comb(b, b.math("MULTIPLY", t, 1.7), 0.0, 0.0), 1.0, 2.0)
    flk = b.n("ShaderNodeTexNoise", Vector=O, W=0.0, Scale=0.9, Detail=1.0, _noise_dimensions="4D")
    b.link(b.math("MULTIPLY", t, 0.9), flk.inputs["W"])
    hc = b.ctrl("heat", 1.0)
    h = b.math("POWER", heat, 1.6)
    estr = b.math("MULTIPLY", b.math("MULTIPLY", crack, h), b.math("MULTIPLY", hc, 9.0))
    estr = b.math("MULTIPLY", estr, b.math("ADD", _mr(b, (flk, "Fac"), 0.35, 0.65, 0.35, 1.2),
                                           b.math("MULTIPLY", (fl, "Fac"), 0.2)))
    ecol = b.ramp(heat, [(0.2, (0.6, 0.03, 0.0)), (0.75, (1.0, 0.22, 0.02)), (1.0, (1.0, 0.45, 0.08))])
    rough = b.mix(gloss, (0.55, 0.55, 0.55), (0.12, 0.12, 0.12))
    hgt = b.math("SUBTRACT", b.math("MULTIPLY", (n1, "Fac"), 0.5), crack)
    bump = b.n("ShaderNodeBump", Strength=0.5, Distance=0.04, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Roughness": (rough[0], rough[1]), "Normal": bump})
    bs.inputs["Specular IOR Level"].default_value = 0.6
    b.link(ecol, bs.inputs["Emission Color"])
    b.link(estr, bs.inputs["Emission Strength"])
    b.out(bs)
    return _key_time(m)


def mat_portal(name="hellgate_vortex", radius=3.0, spin=1.1, twist=2.6):
    """Swirling fire vortex on a disc in object XZ (normal -Y). Polar swirl + inward-flowing noise +
    spiral arms (seam-free), bright core, ragged licking rim (alpha blend). CTRL_portal = intensity."""
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
    sa = b.math("ADD", b.math("ADD", a, b.math("MULTIPLY", b.math("POWER", inv, 2.0), twist)), b.math("MULTIPLY", t, spin))
    cs = b.math("COSINE", sa)
    sn = b.math("SINE", sa)
    q = _comb(b, b.math("MULTIPLY", cs, b.math("MULTIPLY", r, 2.6)), b.math("MULTIPLY", sn, b.math("MULTIPLY", r, 2.6)),
              b.math("ADD", b.math("MULTIPLY", r, 2.2), b.math("MULTIPLY", t, 0.9)))
    n1 = _noise(b, q, 1.5, 8.0, 0.62, 0.5)
    q2 = _comb(b, b.math("MULTIPLY", cs, b.math("MULTIPLY", r, 7.0)), b.math("MULTIPLY", sn, b.math("MULTIPLY", r, 7.0)),
               b.math("ADD", b.math("MULTIPLY", r, 5.0), b.math("MULTIPLY", t, 2.0)))
    n2 = _noise(b, q2, 1.0, 4.0, 0.55)
    arms = b.math("SINE", b.math("SUBTRACT", b.math("MULTIPLY", b.math("ADD", a, b.math("MULTIPLY", inv, 3.2)), 5.0),
                                 b.math("MULTIPLY", t, 3.0)))
    fire = b.math("ADD", b.math("MULTIPLY", (n1, "Fac"), 0.75), b.math("MULTIPLY", (n2, "Fac"), 0.35))
    fire = b.math("ADD", fire, b.math("MULTIPLY", arms, 0.12))
    fire = _mr(b, fire, 0.38, 0.85)
    core = b.math("POWER", _mr(b, r, 0.42, 0.0), 1.6)
    val = b.math("ADD", b.math("MULTIPLY", fire, b.math("ADD", 0.5, b.math("MULTIPLY", core, 0.7))),
                 b.math("MULTIPLY", core, 0.55), clamp=True)
    rimn = _noise(b, _comb(b, b.math("MULTIPLY", cs, 2.0), b.math("MULTIPLY", sn, 2.0), b.math("MULTIPLY", t, 1.4)), 2.0, 3.0)
    edge = _mr(b, r, 1.0, 0.8)
    lick = _mr(b, b.math("SUBTRACT", r, b.math("MULTIPLY", (rimn, "Fac"), 0.18)), 0.98, 0.86)
    alpha = b.math("MAXIMUM", edge, lick)
    ecol = b.ramp(val, [(0.0, (0.0, 0.0, 0.0)), (0.28, (0.28, 0.012, 0.004)), (0.52, (1.0, 0.13, 0.015)),
                        (0.75, (1.0, 0.36, 0.05)), (0.95, (1.0, 0.75, 0.38))])
    pc = b.ctrl("portal", 1.0)
    estr = b.math("MULTIPLY", b.math("ADD", 1.5, b.math("MULTIPLY", b.math("POWER", val, 2.2), 38.0)), pc)
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
def world_night(moon_dir=(0.05, 1.0, 0.45), density=0.012, horizon=(0.030, 0.036, 0.046),
                zenith=(0.004, 0.0055, 0.008), moon=True, vol_color=(0.62, 0.68, 0.76), aniso=0.55):
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
    mr.inputs["From Min"].default_value = -0.05
    mr.inputs["From Max"].default_value = 0.7
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
        disc.inputs["To Max"].default_value = 60.0
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
