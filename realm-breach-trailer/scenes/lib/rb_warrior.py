"""THE WARRIOR (the Breach Runner) — locked design, see assets/characters.md.

build_warrior(look) returns a Warrior with:
  .rig    dict of FK empties (world-aligned at rest, so rotations read as
          pitch X / roll Y / yaw Z in the parent's frame)
  .root   root empty (move/turn the whole character with it)
  .sword  sword object (parented to hand_R)
  .mats   materials (sword blade has CTRL_crack_glow, eyes CTRL_eye_glow)
  .cape   cloth-simulated cape (late/mid looks) or None
Looks: 'late' (full), 'mid' (late armour, no cape/rings/glow), 'early'
(grey iron, leather hood, short sword, no cape/rings/glow).
"""
import math
import random

import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

import rb_mat as M
import rb_mesh as G
from rb_core import empty, hexcol, link, parent_keep

# ------------------------------------------------------------------ rest joints
J = {
    "root": (0, 0, 0),
    "pelvis": (0, 0.0, 0.98),
    "spine": (0, 0.0, 1.10),
    "chest": (0, 0.01, 1.30),
    "neck": (0, 0.02, 1.565),
    "head": (0, 0.02, 1.655),
    "clav_L": (0.035, 0.015, 1.50), "upperarm_L": (0.205, 0.03, 1.495), "forearm_L": (0.335, 0.055, 1.215),
    "hand_L": (0.405, 0.015, 0.975), "fingers_L": (0.425, -0.005, 0.885),
    "thigh_L": (0.105, 0.0, 0.935), "shin_L": (0.118, -0.005, 0.515), "foot_L": (0.122, 0.03, 0.092),
    "toe_L": (0.128, -0.135, 0.03),
}
for k in list(J):
    if k.endswith("_L"):
        x, y, z = J[k]
        J[k[:-2] + "_R"] = (-x, y, z)

PARENT = {
    "pelvis": "root", "spine": "pelvis", "chest": "spine", "neck": "chest", "head": "neck",
    "thigh_L": "pelvis", "shin_L": "thigh_L", "foot_L": "shin_L", "toe_L": "foot_L",
    "thigh_R": "pelvis", "shin_R": "thigh_R", "foot_R": "shin_R", "toe_R": "foot_R",
    "clav_L": "chest", "upperarm_L": "clav_L", "forearm_L": "upperarm_L", "hand_L": "forearm_L", "fingers_L": "hand_L",
    "clav_R": "chest", "upperarm_R": "clav_R", "forearm_R": "upperarm_R", "hand_R": "forearm_R", "fingers_R": "hand_R",
}
ORDER = ["root", "pelvis", "spine", "chest", "neck", "head",
         "clav_L", "upperarm_L", "forearm_L", "hand_L", "fingers_L",
         "clav_R", "upperarm_R", "forearm_R", "hand_R", "fingers_R",
         "thigh_L", "shin_L", "foot_L", "toe_L", "thigh_R", "shin_R", "foot_R", "toe_R"]


def V(*a):
    return np.array(a, dtype=float)


class Warrior:
    pass


def build_rig(prefix):
    rig = {}
    for n in ORDER:
        p = rig.get(PARENT.get(n))
        e = empty(prefix + n, J[n], size=0.04)
        if p is not None:
            e.parent = p
            e.matrix_parent_inverse = p.matrix_world.inverted()
            bpy.context.view_layer.update()
        rig[n] = e
    for e in rig.values():
        e.rotation_mode = "XYZ"
    return rig


def attach(ob, rig, joint):
    bpy.context.view_layer.update()
    parent_keep(ob, rig[joint])
    return ob


# ------------------------------------------------------------------ pieces
def torso_shell(name, z0, z1, rows, a_fn, b_fn, ridge=0.0, n=2.6, N=72, y_off=0.0, arc=None, seed=0, bb_fn=None):
    """Superelliptic torso shell between heights z0..z1 (front = -Y), optional medial ridge.
    b_fn = front depth; bb_fn = back depth (defaults to b_fn)."""
    zs = np.linspace(z0, z1, rows)
    if arc is None:
        ths = np.linspace(-math.pi, math.pi, N, endpoint=False)
        closed = True
    else:
        ths = np.linspace(arc[0], arc[1], N)
        closed = False
    P = np.zeros((rows, len(ths), 3))
    for i, z in enumerate(zs):
        t = (z - z0) / max(1e-6, (z1 - z0))
        a, bf = a_fn(t), b_fn(t)
        bb = bb_fn(t) if bb_fn else bf
        for j, th in enumerate(ths):
            s, c = math.sin(th), math.cos(th)
            b = bf if c > 0 else bb
            x = a * np.sign(s) * abs(s) ** (2 / n)
            y = -b * np.sign(c) * abs(c) ** (2 / n)
            if ridge and y < 0:
                y -= ridge * math.exp(-(x / 0.045) ** 2) * min(1.0, -y / b * 1.5)
            P[i, j] = (x, y + y_off, z)
    return G.grid_mesh(name, P, closed_u=closed)


def lame_band(name, center, axis, r0, r1, h, arc, front=(0, -1, 0), N=40, M=6, flare=0.0):
    """A single armour lame: a conical band segment around `axis` (arc in radians around `front`)."""
    c = np.array(center, float)
    ax = np.array(axis, float)
    ax = ax / np.linalg.norm(ax)
    p0 = c
    p1 = c + ax * h
    return G.tube(name, p0, p1, lambda t, th: r0 + (r1 - r0) * t + flare * t * t, N=N, M=M, arc=arc, front=front)


def build_warrior(look="late", prefix="W_", rings=False, sword_glow=None, seed=7, cape=None):
    w = Warrior()
    w.look = look
    w.prefix = prefix
    rnd = random.Random(seed)
    early = look == "early"
    if cape is None:
        cape = look == "late"
    rig = build_rig(prefix)
    w.rig = rig
    w.root = rig["root"]
    plate = M.steel("steel_iron" if early else "steel_black", "iron" if early else "black", seed)
    mail = M.chainmail("chainmail_iron" if early else "chainmail", look="iron" if early else "black")
    leath = M.leather("leather_dark", (0.02, 0.013, 0.009))
    leath2 = M.leather("leather_brown", (0.032, 0.019, 0.012), rough=0.7)
    black = M.matte("void_black", (0.002, 0.002, 0.002), rough=1.0)
    w.mats = {"plate": plate, "mail": mail, "leather": leath}
    parts = []

    def fin(ob, joint, mat=plate, thick=0.004, bevel=0.0015, sub=1, dent=0, mud_top=0.55, rolled=None, offset=1.0):
        if dent:
            G.dents(ob, rnd.randrange(1 << 30), count=dent, depth=0.0035)
        loops = G.boundary_loops(ob) if rolled else []
        G.finish_plate(ob, thick=thick, bevel=bevel, subsurf=sub, offset=offset)
        G.bake_attributes(ob, mud_top=mud_top)
        G.set_mat(ob, mat)
        attach(ob, rig, joint)
        parts.append(ob)
        for k, lp in enumerate(loops):
            if len(lp) < 4:
                continue
            closed = np.linalg.norm(np.array(lp[0]) - np.array(lp[-1])) < 0.03
            t = G.curve_tube(ob.name + "_roll%d" % k, lp, radius=rolled, closed=closed)
            G.bake_attributes(t, mud_top=mud_top, wear_gain=3.0, wear_scale=0.55)
            G.set_mat(t, mat)
            attach(t, rig, joint)
            parts.append(t)
        return ob

    # ---------------- under-layer: gambeson torso + chainmail ----------------
    gam = torso_shell(prefix + "gambeson", 0.92, 1.55, 14, lambda t: 0.14 + 0.035 * math.sin(t * 2.6),
                      lambda t: 0.10 + 0.02 * math.sin(t * 2.6), n=2.2, N=48, y_off=0.0)
    G.finish_plate(gam, thick=0.0, bevel=0, subsurf=1)
    G.set_mat(gam, leath)
    attach(gam, rig, "chest")
    parts.append(gam)
    # hauberk skirt panels (front/back per leg) — mail hangs between the tassets
    for side, sx in (("L", 1), ("R", -1)):
        for fb, arc in (("f", (-1.25, 0.15)), ("b", (2.95, 4.25))):
            hip = V(*J["thigh_" + side])
            sk = G.tube(prefix + "mail_skirt_%s%s" % (side, fb), hip + V(0, 0, 0.07), hip + V(0, 0, -0.22),
                        lambda t, th: 0.1 + 0.025 * t, N=20, M=8, arc=arc if sx > 0 else (-arc[1], -arc[0]))
            G.finish_plate(sk, thick=0.003, bevel=0, subsurf=1)
            G.bake_attributes(sk)
            G.set_mat(sk, mail)
            attach(sk, rig, "thigh_" + side)
            parts.append(sk)

    # ---------------- cuirass ----------------
    if early:
        cu = torso_shell(prefix + "cuirass", 1.04, 1.50, 22, lambda t: 0.165 + 0.035 * math.sin(min(1, t * 1.3) * 2.3),
                         lambda t: 0.122 + 0.024 * math.sin(min(1, t * 1.3) * 2.3), ridge=0.006, n=2.4, N=64)
    else:
        ca = lambda t: float(np.interp(t, [0, 0.25, 0.62, 0.85, 1], [0.15, 0.168, 0.214, 0.216, 0.198]))
        cf = lambda t: float(np.interp(t, [0, 0.3, 0.6, 0.85, 1], [0.122, 0.142, 0.168, 0.158, 0.128]))
        cb = lambda t: float(np.interp(t, [0, 0.4, 0.8, 1], [0.112, 0.13, 0.142, 0.134]))
        cu = torso_shell(prefix + "cuirass", 1.03, 1.52, 30, ca, cf, ridge=0.02, n=2.5, N=80, bb_fn=cb)
    fin(cu, "chest", thick=0.005, dent=7, rolled=0.0045)
    if not early:
        # plackart: lower belly plate overlapping the breastplate, pointed top
        cols, rws = 40, 10
        P = np.zeros((rws, cols, 3))
        for j, th in enumerate(np.linspace(-1.55, 1.55, cols)):
            for i in range(rws):
                t = i / (rws - 1)
                ztop = 1.16 + 0.085 * max(0.0, 1 - abs(th) / 1.4) ** 1.5
                z = 1.035 + t * (ztop - 1.035)
                tt = (z - 1.03) / 0.49
                a, b = ca(tt) + 0.006, cf(tt) + 0.007
                s_, c_ = math.sin(th), math.cos(th)
                x = a * np.sign(s_) * abs(s_) ** (2 / 2.5)
                y = -b * np.sign(c_) * abs(c_) ** (2 / 2.5)
                y -= 0.02 * math.exp(-(x / 0.045) ** 2)
                P[i, j] = (x, y, z)
        pk = G.grid_mesh(prefix + "plackart", P)
        fin(pk, "chest", thick=0.0045, dent=2, rolled=0.0038)
    # waist belt (leather) + buckle plate
    belt = G.tube(prefix + "belt", V(0, 0.0, 1.035), V(0, 0.0, 1.075), lambda t, th: 0.183 if not early else 0.172,
                  N=56, M=3)
    G.finish_plate(belt, thick=0.006, bevel=0.001, subsurf=1)
    G.bake_attributes(belt)
    G.set_mat(belt, leath2)
    attach(belt, rig, "spine")
    parts.append(belt)
    # faulds: 3 overlapping lames
    for k in range(3 if not early else 2):
        z = 1.04 - k * 0.042
        f = G.tube(prefix + "fauld%d" % k, V(0, 0.0, z), V(0, 0.0, z - 0.054),
                   lambda t, th, k=k: 0.178 + 0.013 * k + 0.02 * t, N=60, M=4, arc=(-2.45, 2.45))
        fin(f, "pelvis", thick=0.0035, rolled=0.003 if k == 2 else None)
    # tassets on the thighs
    if not early:
        for side in ("L", "R"):
            hip = V(*J["thigh_" + side])
            sx = 1 if side == "L" else -1
            for k in range(2):
                z = hip[2] - 0.02 - k * 0.07
                tz = G.tube(prefix + "tasset_%s%d" % (side, k), V(hip[0], hip[1], z), V(hip[0] + sx * 0.008, hip[1] - 0.004, z - 0.085),
                            lambda t, th, k=k: 0.118 + 0.008 * k + 0.012 * t, N=24, M=4,
                            arc=(-1.15 + (0.35 if sx > 0 else -0.35), 1.15 + (0.35 if sx > 0 else -0.35)))
                fin(tz, "thigh_" + side, thick=0.0035, rolled=0.0028 if k == 1 else None, dent=1)

    # ---------------- gorget ----------------
    for k in range(3):
        z = 1.505 + k * 0.03
        g = G.tube(prefix + "gorget%d" % k, V(0, 0.02, z), V(0, 0.02, z + 0.04),
                   lambda t, th, k=k: 0.105 - 0.017 * k - 0.025 * t, N=48, M=4)
        fin(g, "chest" if k == 0 else "neck", thick=0.0035, rolled=0.0025 if k == 2 else None)

    # ---------------- pauldrons ----------------
    for side in ("L", "R"):
        sx = 1 if side == "L" else -1
        big = 1.18 if (side == "L" and not early) else 1.0
        sh = V(*J["upperarm_" + side])
        axis = V(sx * 0.55, 0.0, 1.0)
        if early:
            dome = G.ellipsoid_cap(prefix + "pauldron_%s" % side, sh + V(0, 0, 0.01), (0.11, 0.115, 0.11),
                                   axis=axis, polar=(0, 1.35), N=40, M=14)
            fin(dome, "upperarm_" + side, thick=0.004, rolled=0.003, dent=2)
            continue
        r = 0.138 * big
        notch = side == "L"

        def bumpf(th, ph, notch=notch):
            # medial keel running front-to-back over the dome
            return 1.0 + 0.045 * math.exp(-(math.sin(ph) / 0.13) ** 2) * math.sin(min(th, 1.2) * 1.3)

        dome = G.ellipsoid_cap(prefix + "pauldron_%s" % side, sh + V(sx * 0.012, 0.005, 0.03), (r * 1.1, r * 1.12, r * 0.74),
                               axis=axis, polar=(0, 1.5), N=60, M=20, bump=bumpf)
        if notch:
            # cracked rim: knock a jagged chunk out of the lower front rim
            me = dome.data
            import bmesh
            bm = bmesh.new()
            bm.from_mesh(me)
            bm.faces.ensure_lookup_table()
            kill = []
            for fc in bm.faces:
                c = fc.calc_center_median()
                rel = Vector(c) - Vector(sh)
                ang = math.atan2(-rel.y, rel.x * sx)
                depth = (Vector(c) - Vector(sh)).dot(Vector(axis / np.linalg.norm(axis)))
                jag = 0.012 * math.sin(ang * 23.0) + 0.006 * math.sin(ang * 51.0)
                if 0.35 < ang < 1.05 and depth < -0.0 + jag:
                    kill.append(fc)
            bmesh.ops.delete(bm, geom=kill, context="FACES")
            bm.to_mesh(me)
            bm.free()
        fin(dome, "upperarm_" + side, thick=0.005, rolled=0.0042, dent=3)
        # descending lames
        down = V(*J["forearm_" + side]) - sh
        down = down / np.linalg.norm(down)
        for k in range(5 if side == "L" else 4):
            c = sh + down * (0.06 + k * 0.042) * big
            ln = lame_band(prefix + "pl_%s%d" % (side, k), c, down, (0.104 - 0.005 * k) * big, (0.1 - 0.005 * k) * big,
                           0.05 * big, arc=(-2.0, 2.0), front=(sx, -0.2, 0))
            fin(ln, "upperarm_" + side, thick=0.0035, rolled=0.0028)
        if side == "L":
            # haute-piece: upright flange guarding the neck (silhouette signature)
            hp = G.tube(prefix + "hautepiece", sh + V(-0.05, 0.0, 0.10), sh + V(-0.05, 0.0, 0.175),
                        lambda t, th: 0.12 - 0.015 * t, N=24, M=5, arc=(-1.0, 1.1), front=(1, 0, 0))
            fin(hp, "upperarm_L", thick=0.004, rolled=0.0035)

    # ---------------- arms ----------------
    for side in ("L", "R"):
        sx = 1 if side == "L" else -1
        sh, el, wr = V(*J["upperarm_" + side]), V(*J["forearm_" + side]), V(*J["hand_" + side])
        # mail sleeve under the plates
        sl = G.tube(prefix + "sleeve_%s" % side, sh, el + (el - sh) * 0.08, lambda t, th: 0.064 - 0.01 * t, N=24, M=8)
        G.finish_plate(sl, thick=0, bevel=0, subsurf=1)
        G.bake_attributes(sl)
        G.set_mat(sl, mail)
        attach(sl, rig, "upperarm_" + side)
        parts.append(sl)
        # rerebrace (lower upper arm)
        rr = G.tube(prefix + "rerebrace_%s" % side, sh + (el - sh) * 0.45, el - (el - sh) * 0.06,
                    lambda t, th: 0.07 - 0.006 * t, N=36, M=6, arc=(-2.7, 2.7), front=(sx, -0.3, 0))
        fin(rr, "upperarm_" + side, thick=0.0035, rolled=0.0026)
        # couter: elbow cup + fan
        cup = G.ellipsoid_cap(prefix + "couter_%s" % side, el + V(0, 0.014, 0), (0.07, 0.07, 0.068),
                              axis=V(sx * 0.35, 0.95, 0.1), polar=(0, 1.35), N=32, M=10)
        fin(cup, "forearm_" + side, thick=0.004, rolled=0.003, dent=1)
        fan = G.ellipsoid_cap(prefix + "couterfan_%s" % side, el + V(sx * 0.052, 0.022, 0.0), (0.07, 0.085, 0.022),
                              axis=V(sx, 0.2, 0), polar=(0, 1.2), N=28, M=8)
        fin(fan, "forearm_" + side, thick=0.003, rolled=0.0025)
        # vambrace
        vb = G.tube(prefix + "vambrace_%s" % side, el + (wr - el) * 0.12, wr - (wr - el) * 0.02,
                    lambda t, th: 0.06 - 0.013 * t + 0.006 * math.sin(t * math.pi), N=40, M=8)
        fin(vb, "forearm_" + side, thick=0.0035, rolled=0.0026, dent=2)
        # gauntlet cuff
        hd = V(*J["fingers_" + side]) - wr
        cuff = G.tube(prefix + "cuff_%s" % side, wr + (el - wr) * 0.22, wr + hd * 0.15,
                      lambda t, th: 0.056 + 0.032 * (1 - t) ** 2, N=40, M=6)
        fin(cuff, "hand_" + side, thick=0.003, rolled=0.0025)
        # hand: leather glove core + back plate + finger lames
        palm = G.tube(prefix + "palm_%s" % side, wr + hd * 0.05, wr + hd * 1.0,
                      lambda t, th: 0.043 + 0.007 * math.sin(t * math.pi), N=20, M=6,
                      shape=lambda t, th: (0.0, 0.0))
        G.finish_plate(palm, thick=0, bevel=0, subsurf=1)
        palm.scale = (1, 1, 1)
        G.set_mat(palm, leath)
        attach(palm, rig, "hand_" + side)
        parts.append(palm)
        back = G.tube(prefix + "handplate_%s" % side, wr + hd * 0.1, wr + hd * 0.95,
                      lambda t, th: 0.05, N=18, M=5, arc=(-1.2, 1.2), front=(sx * 1.0, 0.0, 0))
        fin(back, "hand_" + side, thick=0.003, rolled=0.0022)
        # fingers (in a fist they curl forward); 4 fingers x 3 lames, one rigid fist block per hand
        kn = V(*J["fingers_" + side])
        hdn = hd / np.linalg.norm(hd)
        for f in range(4):
            off = V(0, -0.027 + f * 0.018, 0)
            base = kn + off
            # curl path: down then inward toward the palm (fist)
            segs = [base, base + hdn * 0.035 + V(-sx * 0.012, -0.004, 0), base + hdn * 0.045 + V(-sx * 0.04, -0.006, 0.0),
                    base + hdn * 0.025 + V(-sx * 0.058, -0.004, 0.012)]
            for s in range(3):
                fl = G.tube(prefix + "finger_%s%d%d" % (side, f, s), segs[s], segs[s + 1],
                            lambda t, th: 0.0118 - 0.0012 * s, N=12, M=3)
                fin(fl, "fingers_" + side, thick=0.0018, bevel=0.0008, sub=1)
        th0 = wr + hd * 0.45 + V(-sx * 0.02, -0.035, 0)
        thumb = G.tube(prefix + "thumb_%s" % side, th0, th0 + V(-sx * 0.01, -0.02, -0.05), lambda t, th: 0.011, N=12, M=4)
        fin(thumb, "hand_" + side, thick=0.002, bevel=0.0008)
        if rings and side == "L":
            ring_cols = ["#FF3B3B", "#6BFF4A", "#FFE9A8", "#6FA8FF"]
            for f in range(4):
                c = kn + V(0, -0.024 + f * 0.016, 0) + hdn * 0.02 + V(-sx * 0.004, -0.003, 0)
                rg = G.tube(prefix + "ring%d" % f, c - hdn * 0.006, c + hdn * 0.006, lambda t, th: 0.0125, N=24, M=3)
                G.finish_plate(rg, thick=0.003, bevel=0.0008, subsurf=1)
                G.set_mat(rg, M.matte("ring_gold", (0.85, 0.6, 0.25), rough=0.2, metal=1.0))
                gem = G.ellipsoid_cap(prefix + "gem%d" % f, c + V(sx * 0.012, 0, 0), (0.0055, 0.0055, 0.0055),
                                      axis=V(sx, 0, 0), polar=(0, 3.1), N=12, M=8)
                G.set_mat(gem, M.emission("ringglow%d" % f, ring_cols[f], 30.0, ctrl="ring%d" % f))
                for o in (rg, gem):
                    attach(o, rig, "fingers_L")
                    parts.append(o)

    # ---------------- legs ----------------
    for side in ("L", "R"):
        hip, kn, an, toe = V(*J["thigh_" + side]), V(*J["shin_" + side]), V(*J["foot_" + side]), V(*J["toe_" + side])
        sx = 1 if side == "L" else -1
        # trouser/gambeson core
        core = G.tube(prefix + "leg_%s" % side, hip + V(0, 0, 0.04), kn + V(0, 0, -0.03),
                      lambda t, th: 0.092 - 0.03 * t, N=24, M=10)
        G.finish_plate(core, thick=0, bevel=0, subsurf=1)
        G.bake_attributes(core)
        G.set_mat(core, mail)
        attach(core, rig, "thigh_" + side)
        parts.append(core)
        # lower core follows the shin
        shc = G.tube(prefix + "shincore_%s" % side, kn, an + V(0, 0, 0.02), lambda t, th: 0.055 - 0.015 * t, N=20, M=8)
        G.finish_plate(shc, thick=0, bevel=0, subsurf=1)
        G.set_mat(shc, leath)
        attach(shc, rig, "shin_" + side)
        parts.append(shc)
        # cuisse (front thigh plate)
        cu2 = G.tube(prefix + "cuisse_%s" % side, hip + (kn - hip) * 0.22, kn + (hip - kn) * 0.06,
                     lambda t, th: 0.098 - 0.022 * t, N=36, M=8, arc=(-2.15, 2.15))
        fin(cu2, "thigh_" + side, thick=0.0035, rolled=0.0028, dent=2, mud_top=0.5)
        # poleyn (knee cup + wing)
        pol = G.ellipsoid_cap(prefix + "poleyn_%s" % side, kn + V(0, -0.022, 0.005), (0.07, 0.072, 0.07),
                              axis=V(0, -1, 0.15), polar=(0, 1.3), N=32, M=10)
        fin(pol, "shin_" + side, thick=0.004, rolled=0.003, dent=1, mud_top=0.6)
        wing = G.ellipsoid_cap(prefix + "poleynwing_%s" % side, kn + V(sx * 0.058, -0.012, 0.0), (0.058, 0.07, 0.018),
                               axis=V(sx, -0.3, 0), polar=(0, 1.2), N=24, M=8)
        fin(wing, "shin_" + side, thick=0.003, rolled=0.0024, mud_top=0.6)
        # greave with calf bulge
        gr = G.tube(prefix + "greave_%s" % side, kn + (an - kn) * 0.1, an + V(0, 0, 0.035),
                    lambda t, th: 0.06 + 0.016 * math.sin(min(1, t * 1.6) * math.pi) * (0.5 + 0.5 * math.cos(th - math.pi))
                    - 0.014 * t, N=44, M=12)
        fin(gr, "shin_" + side, thick=0.0035, rolled=0.0026, dent=2, mud_top=0.6)
        # sabaton: arched lames from ankle to toe + sole
        fd = toe - an
        for k in range(5):
            t = k / 5.0
            c = an + fd * (0.1 + t * 0.85) + V(0, 0, -0.012 * t)
            lm = G.tube(prefix + "sab_%s%d" % (side, k), c, c + fd * 0.21, lambda tt, th, k=k: 0.062 - 0.006 * k,
                        N=20, M=3, arc=(-1.7, 1.7), front=(0, 0, 1))
            fin(lm, "foot_" + side, thick=0.003, rolled=0.0022, mud_top=0.6)
        sole = G.tube(prefix + "sole_%s" % side, an + V(0, 0.07, -0.07), toe + V(0, -0.02, -0.015),
                      lambda t, th: 0.052 - 0.012 * t, N=16, M=6, shape=lambda t, th: (0, 0))
        sole.scale = (1.0, 1.0, 1.0)
        G.finish_plate(sole, thick=0, bevel=0, subsurf=1)
        G.bake_attributes(sole, mud_top=0.6)
        G.set_mat(sole, M.leather("leather_sole", (0.03, 0.022, 0.016), rough=0.85))
        attach(sole, rig, "foot_" + side)
        parts.append(sole)

    # ---------------- head ----------------
    if early:
        _early_head(w, rig, prefix, plate, leath2, black, parts)
    else:
        _great_helm(w, rig, prefix, plate, black, parts, rnd, glow=look != "mid" or True)

    # ---------------- weapon ----------------
    w.sword = build_sword(prefix, short=early, glow=(0.0 if look in ("early", "mid") else 1.0) if sword_glow is None else sword_glow)
    _grip_sword(w, rig)
    parts.append(w.sword)

    w.parts = parts
    w.cloths = []
    w.cape = build_cape(w, prefix) if cape else None
    return w


# ------------------------------------------------------------------ head variants
def _great_helm(w, rig, prefix, plate, black, parts, rnd, glow=True):
    hz0, hz1 = 1.58, 1.915
    body_top = hz1 - 0.045
    eye = (1.757, 1.770)
    breath = (1.668, 1.757)
    eye_th = 0.42
    br_th = 0.04
    zs = sorted(set(np.round(np.concatenate([np.linspace(hz0, body_top, 44), [eye[0], eye[1], breath[0]]]), 5)))
    tops = [0.22, 0.45, 0.65, 0.8, 0.91, 0.97]
    zs = list(zs) + [round(body_top + 0.045 * math.sin(t * math.pi / 2), 5) for t in tops]
    ths = sorted(set(np.round(np.concatenate([np.linspace(-math.pi, math.pi, 120, endpoint=False),
                                               [-eye_th, eye_th, -br_th, br_th]]), 5)))
    ths = np.array(ths)

    def a_of(z):
        t = (min(z, body_top) - hz0) / (body_top - hz0)
        return 0.131 - 0.014 * math.sin(min(1, t * 2.0) * 1.3) - 0.006 * t

    def b_of(z):
        t = (min(z, body_top) - hz0) / (body_top - hz0)
        return 0.152 - 0.013 * math.sin(min(1, t * 2.0) * 1.3) - 0.004 * t

    def ring_pt(z, th, top=0.0):
        a, b = a_of(z), b_of(z)
        s, c = math.sin(th), math.cos(th)
        n = 2.4
        x = a * np.sign(s) * abs(s) ** (2 / n)
        y = -b * np.sign(c) * abs(c) ** (2 / n)
        if y < 0:  # prow ridge
            y -= 0.017 * math.exp(-(x / 0.03) ** 2) * min(1.0, (z - hz0) / 0.05) * (1.0 - top)
        if z < hz0 + 0.02:  # flared lower rim
            f = 1 + 0.05 * (1 - (z - hz0) / 0.02)
            x, y = x * f, y * f
        shrink = math.sqrt(max(0.0, 1 - top ** 2)) if top > 0 else 1.0
        return x * shrink, y * shrink + 0.02

    P = np.zeros((len(zs), len(ths), 3))
    for i, z in enumerate(zs):
        top = 0.0
        if z > body_top + 1e-6:
            top = tops[i - (len(zs) - len(tops))]
        for j, th in enumerate(ths):
            x, y = ring_pt(z, th, top)
            P[i, j] = (x, y, z)

    zi = {round(z, 5): i for i, z in enumerate(zs)}
    i_e0, i_e1, i_b0 = zi[round(eye[0], 5)], zi[round(eye[1], 5)], zi[round(breath[0], 5)]

    def skip(i, j):
        if j == len(ths) - 1:
            return False
        th_a, th_b = ths[j], ths[j + 1]
        if i_e0 <= i < i_e1 and th_a >= -eye_th - 1e-6 and th_b <= eye_th + 1e-6:
            return True
        if i_b0 <= i < i_e0 and th_a >= -br_th - 1e-6 and th_b <= br_th + 1e-6:
            return True
        return False

    helm = G.grid_mesh(prefix + "helm", P, closed_u=True, cap_end=True, skip=skip)
    G.dents(helm, rnd.randrange(1 << 30), count=4, depth=0.0025)
    # battle gash across the left cheek plate
    p1, p2 = Vector((0.05, -0.14, 1.815)), Vector((0.115, -0.07, 1.64))
    seg = p2 - p1
    for v in helm.data.vertices:
        tt = max(0.0, min(1.0, (v.co - p1).dot(seg) / seg.length_squared))
        d = (v.co - (p1 + seg * tt)).length
        if d < 0.02:
            v.co -= v.normal * 0.0035 * math.exp(-(d / 0.005) ** 2) * math.sin(tt * math.pi) ** 0.5
    G.finish_plate(helm, thick=0.005, bevel=0.0012, subsurf=1, offset=-1.0)
    G.bake_attributes(helm, mud_top=0)
    G.set_mat(helm, plate)
    attach(helm, rig, "head")
    parts.append(helm)
    # brow reinforcement plate over the eye slit (heavy lip that shadows the eyes)
    bz = np.linspace(eye[1] + 0.0015, eye[1] + 0.03, 6)
    bth = np.linspace(-0.85, 0.85, 34)
    BP = np.zeros((len(bz), len(bth), 3))
    for i, z in enumerate(bz):
        for j, th in enumerate(bth):
            x, y = ring_pt(z, th)
            r = math.hypot(x, y - 0.02)
            k = (r + 0.0035) / r
            BP[i, j] = (x * k, (y - 0.02) * k + 0.02, z)
    brow = G.grid_mesh(prefix + "helm_brow", BP)
    fin_brow = G.finish_plate(brow, thick=0.004, bevel=0.001, subsurf=1)
    G.bake_attributes(brow, mud_top=0)
    G.set_mat(brow, plate)
    attach(brow, rig, "head")
    parts.append(brow)
    # rivets: brow plate ends, crown band and lower rim
    pts, nrm = [], []
    for k in range(28):
        th = -math.pi + (k + 0.5) * 2 * math.pi / 28
        for z in (1.84, 1.598):
            if abs(th) < 0.95 and z > 1.7:
                continue
            x, y = ring_pt(z, th)
            pts.append((x * 1.025, (y - 0.02) * 1.025 + 0.02, z))
            nrm.append((x, y - 0.02, 0))
    for th in (-0.8, -0.45, 0.45, 0.8):
        x, y = ring_pt(eye[1] + 0.016, th)
        pts.append((x * 1.06, (y - 0.02) * 1.06 + 0.02, eye[1] + 0.016))
        nrm.append((x, y - 0.02, 0))
    rv = G.rivets(prefix + "helm_rivets", pts, nrm, radius=0.0048, mat=plate)
    G.bake_attributes(rv, mud_top=0)
    attach(rv, rig, "head")
    parts.append(rv)
    # dark interior + glowing eyes
    inner = G.ellipsoid_cap(prefix + "helm_inner", (0, 0.02, 1.74), (0.098, 0.118, 0.14), axis=(0, 0, 1), polar=(0, 3.1),
                            N=24, M=12)
    G.set_mat(inner, black)
    attach(inner, rig, "head")
    parts.append(inner)
    eyem = M.emission("warrior_eyes", "#FF6A1A", 70.0, ctrl="eye_glow")
    w.mats["eyes"] = eyem
    for sx in (1, -1):
        e = G.ellipsoid_cap(prefix + "eye_%d" % sx, (sx * 0.03, -0.112, 1.7635), (0.0068, 0.004, 0.0031), axis=(0, -1, 0),
                            polar=(0, 3.1), N=12, M=8)
        G.set_mat(e, eyem)
        attach(e, rig, "head")
        parts.append(e)
    w.helm = helm


def _early_head(w, rig, prefix, plate, leath, black, parts):
    """Leather hood with a shoulder capelet over an iron skullcap; the face is lost in shadow."""
    # recessed darkness where the face would be
    face = G.ellipsoid_cap(prefix + "face_shadow", (0, 0.05, 1.70), (0.085, 0.075, 0.11), axis=(0, 0, 1), polar=(0, 3.1),
                           N=20, M=10)
    G.set_mat(face, M.emission("pure_black", (0.0, 0.0, 0.0), 0.0))
    attach(face, rig, "head")
    parts.append(face)
    hood_mat = M.leather("leather_hood", (0.028, 0.019, 0.013), rough=0.85)
    # rows from the hood's crown down to the capelet hem
    zs = np.linspace(1.93, 1.30, 64)
    ths = np.linspace(-math.pi, math.pi, 128, endpoint=False)
    P = np.zeros((len(zs), len(ths), 3))
    for i, z in enumerate(zs):
        # head part (z > 1.6): wraps the skull; below: neck, then flares over the shoulders
        if z > 1.60:
            t = (1.93 - z) / 0.33
            ax = 0.035 + 0.12 * math.sin(min(1.0, t * 1.5) * math.pi / 2)
            by = 0.05 + 0.115 * math.sin(min(1.0, t * 1.5) * math.pi / 2)
            yc = 0.06 - 0.04 * t
        else:
            t = (1.60 - z) / 0.30
            ax = 0.155 + 0.2 * t ** 1.2
            by = 0.165 + 0.04 * t
            yc = 0.02
        for j, th in enumerate(ths):
            sx, cy = math.sin(th), math.cos(th)
            x = ax * np.sign(sx) * abs(sx) ** (2 / 2.2)
            y = -by * np.sign(cy) * abs(cy) ** (2 / 2.2) + yc
            # slight sag of the capelet at the front/back, and a wavy hem
            zz = z - (0.02 * abs(cy) if z < 1.55 else 0.0)
            if z < 1.4:
                zz += (1.4 - z) / 0.1 * 0.02 * math.sin(th * 7 + 0.5)
            P[i, j] = (x, y, zz)
    jf = [j for j, th in enumerate(ths)]

    def skip(i, j):
        z0 = zs[i]
        th = ths[j]
        # oval face opening
        cz, hz = 1.715, 0.105
        if abs(z0 - cz) < hz:
            half = 0.62 * math.sqrt(max(0.0, 1 - ((z0 - cz) / hz) ** 2))
            return abs(th) < half
        return False

    hood = G.grid_mesh(prefix + "hood", P, closed_u=True, skip=skip)
    # rolled leather hem around the face opening (smoothed so the grid steps vanish)
    loops = [lp for lp in G.boundary_loops(hood) if np.mean([q[2] for q in lp]) > 1.55]
    G.finish_plate(hood, thick=0.007, bevel=0, subsurf=1, offset=1.0)
    for k, lp in enumerate(loops):
        pts = np.array(lp)
        for _ in range(12):
            pts = 0.5 * pts + 0.25 * (np.roll(pts, 1, 0) + np.roll(pts, -1, 0))
        hem = G.curve_tube(prefix + "hood_hem%d" % k, [tuple(q) for q in pts], radius=0.011, closed=True)
        G.bake_attributes(hem, mud_top=0)
        G.set_mat(hem, hood_mat)
        attach(hem, rig, "head")
        parts.append(hem)
    G.bake_attributes(hood, mud_top=0)
    G.set_mat(hood, hood_mat)
    attach(hood, rig, "head")
    parts.append(hood)


# ------------------------------------------------------------------ sword
def build_sword(prefix, short=False, glow=1.0):
    """Sword in its own space: grip along +Z from z=-0.30 (pommel) to 0 (guard); blade from 0 up."""
    L = 0.62 if short else 1.38
    W = 0.026 if short else 0.034
    T = 0.0055 if short else 0.0068
    rows = 60
    prof = []
    for i in range(rows):
        t = i / (rows - 1)
        z = 0.012 + t * L
        if t < 0.82:
            w = W * (1 - 0.18 * t)
        else:
            k = (t - 0.82) / 0.18
            w = W * (1 - 0.18 * 0.82) * math.sqrt(max(0.0, 1 - k ** 1.6))
        w = max(w, 0.0006)
        th = T * (1 - 0.35 * t)
        ful = 0.55 if t < (0.55 if short else 0.7) else 1.0
        ring = [(-w, 0, z), (-0.55 * w, 0.8 * th, z), (-0.2 * w, ful * th * 0.85, z), (0, ful * th * 0.8, z),
                (0.2 * w, ful * th * 0.85, z), (0.55 * w, 0.8 * th, z), (w, 0, z),
                (0.55 * w, -0.8 * th, z), (0.2 * w, -ful * th * 0.85, z), (0, -ful * th * 0.8, z),
                (-0.2 * w, -ful * th * 0.85, z), (-0.55 * w, -0.8 * th, z)]
        prof.append(ring)
    bl = G.grid_mesh(prefix + "blade", np.array(prof), closed_u=True, cap_end=True, cap_start=True)
    # keep the edges crisp under subdivision
    me = bl.data
    try:
        cr = me.attributes.get("crease_edge") or me.attributes.new("crease_edge", "FLOAT", "EDGE")
        vals = [1.0 if abs(me.vertices[e.vertices[0]].co.y) < 1e-6 and abs(me.vertices[e.vertices[1]].co.y) < 1e-6 else 0.0
                for e in me.edges]
        cr.data.foreach_set("value", vals)
    except Exception:
        pass
    G.add_mod(bl, "SUBSURF", levels=1, render_levels=1)
    G.apply_all(bl)
    G.bake_attributes(bl, mud_top=0, wear_gain=12)
    bm = M.blade("blade_short" if short else "greatsword_blade", glow=glow)
    G.set_mat(bl, bm)
    steel = M.steel("steel_iron" if short else "steel_black", "iron" if short else "black")
    leath = M.leather("leather_grip", (0.03, 0.018, 0.012), rough=0.75)
    parts = [bl]
    # crossguard: curved bar with flared ends
    gw = 0.11 if short else 0.17
    guard = G.tube(prefix + "guard", (-gw, 0, 0.01), (gw, 0, 0.01),
                   lambda t, th: 0.011 + 0.006 * (2 * t - 1) ** 4, N=16, M=24,
                   shape=lambda t, th: (0.0, 0.0))
    for v in guard.data.vertices:
        v.co.z += 0.03 * (v.co.x / gw) ** 2
    G.finish_plate(guard, thick=0, bevel=0, subsurf=1)
    G.bake_attributes(guard, mud_top=0)
    G.set_mat(guard, steel)
    parts.append(guard)
    gl = 0.13 if short else 0.30
    grip = G.tube(prefix + "grip", (0, 0, 0.0), (0, 0, -gl), lambda t, th: 0.0145 + 0.002 * math.sin(t * math.pi), N=16, M=24)
    G.finish_plate(grip, thick=0, bevel=0, subsurf=1)
    G.set_mat(grip, leath)
    parts.append(grip)
    pom = G.tube(prefix + "pommel", (0, -0.012, -gl - 0.03), (0, 0.012, -gl - 0.03),
                 lambda t, th: 0.034 if not short else 0.026, N=28, M=4, cap_start=True, cap_end=True)
    G.finish_plate(pom, thick=0, bevel=0, subsurf=1)
    G.bake_attributes(pom, mud_top=0)
    G.set_mat(pom, steel)
    parts.append(pom)
    sw = G.join(parts, prefix + "sword")
    sw["blade_len"] = L
    return sw


def _grip_sword(w, rig):
    """Place the sword in the right fist: grip through the fist, blade out of the thumb side."""
    hand = Vector(J["hand_R"])
    kn = Vector(J["fingers_R"])
    hd = (kn - hand).normalized()
    center = hand + hd * 0.075 + Vector((0.022, -0.0, 0))
    # grip axis: forward (-Y) and slightly down; blade points forward
    z = Vector((0.0, -1.0, -0.15)).normalized()
    x = hd.cross(z).normalized()
    y = z.cross(x)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = center + z * 0.06
    w.sword.matrix_world = m
    bpy.context.view_layer.update()
    parent_keep(w.sword, rig["fingers_R"])


# ------------------------------------------------------------------ cape (cloth)
def cloth_panel(w, name, joint, top_z, length, half_top, half_bot, y_fn, cols, rows, seed, mat, tear=9,
                deep=0.14, slit_n=6):
    """A pinned, tattered cloth panel hanging from `joint` (cloth-simulated)."""
    rnd = random.Random(seed)
    P = np.zeros((rows, cols, 3))
    for i in range(rows):
        t = i / (rows - 1)
        half = half_top + (half_bot - half_top) * t
        for j in range(cols):
            u = j / (cols - 1) * 2 - 1
            P[i, j] = (u * half, y_fn(u, t), top_z - t * length)
    cut = []
    for j in range(cols - 1):
        c = rows - 1 - int(rnd.random() ** 1.3 * tear)
        if rnd.random() < deep:
            c -= rnd.randint(int(rows * 0.1), int(rows * 0.24))
        cut.append(c)
    for j in range(1, cols - 2):
        if rnd.random() < 0.3:
            cut[j] = min(cut[j], max(cut[j - 1], cut[j + 1]) - rnd.randint(0, 3))
    slits = {rnd.randrange(2, cols - 3): rnd.randint(4, 10) for _ in range(slit_n)}

    def skip(i, j):
        if i >= cut[j]:
            return True
        if j in slits and cut[j] - slits[j] <= i < cut[j]:
            return (i + j) % 7 != 0 and i > rows * 0.55
        return False

    ob = G.grid_mesh(w.prefix + name, P, skip=skip)
    me = ob.data
    vg = ob.vertex_groups.new(name="pin")
    row_h = length / (rows - 1)
    for v in me.vertices:
        if v.co.z > top_z - 0.5 * row_h:
            vg.add([v.index], 1.0, "REPLACE")
        elif v.co.z > top_z - 1.5 * row_h:
            vg.add([v.index], 0.6, "REPLACE")
    G.set_mat(ob, mat)
    attach(ob, w.rig, joint)
    cl = ob.modifiers.new("Cloth", "CLOTH")
    st = cl.settings
    st.quality = 8
    st.mass = 0.12
    st.tension_stiffness = 80
    st.compression_stiffness = 80
    st.shear_stiffness = 40
    st.bending_stiffness = 2.0
    st.air_damping = 1.0
    st.vertex_group_mass = "pin"
    st.pin_stiffness = 1.0
    cs = cl.collision_settings
    cs.collision_quality = 3
    cs.distance_min = 0.005
    cs.use_self_collision = False
    sol = ob.modifiers.new("Solidify", "SOLIDIFY")
    sol.thickness = 0.006
    sub = ob.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 1
    w.cloths.append(cl)
    return ob


def build_cape(w, prefix, seed=11):
    w.cloths = []
    _collision_proxies(w, prefix)

    def y_cape(u, t):
        # gathered under the gorget/pauldrons: pleats that open up as the cloth falls
        fold = (0.008 + 0.04 * t) * math.sin(u * math.pi * 4.5 + 0.6)
        return 0.2 + 0.03 * (1 - u * u) * (1 - t) + 0.07 * t + fold

    cape = cloth_panel(w, "cape", "chest", 1.525, 1.38, 0.2, 0.44, y_cape, 40, 52, seed, M.cloth("cape"))
    w.cape_cloth = w.cloths[0]

    def y_tab(u, t):
        return -0.255 - 0.02 * t + (0.004 + 0.012 * t) * math.sin(u * math.pi * 2.5 + 1.1)

    w.tabard = cloth_panel(w, "tabard", "pelvis", 1.05, 0.58, 0.1, 0.13, y_tab, 16, 26, seed + 5,
                           M.cloth("cape"), tear=5, deep=0.2, slit_n=2)
    return cape


def _collision_proxies(w, prefix):
    inv = M.new("invisible", blend="CLIP")[0]
    nt = inv.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    nt.links.new(tr.outputs[0], o.inputs["Surface"])
    inv.shadow_method = "NONE"
    rig = w.rig
    specs = [("chest", (0, 0.0, 1.27), (0.2, 0.155, 0.26)), ("pelvis", (0, 0.0, 0.98), (0.2, 0.15, 0.13)),
             ("thigh_L", (0.11, 0.0, 0.72), (0.09, 0.09, 0.24)), ("thigh_R", (-0.11, 0.0, 0.72), (0.09, 0.09, 0.24)),
             ("upperarm_L", (0.27, 0.02, 1.37), (0.09, 0.09, 0.12)), ("upperarm_R", (-0.27, 0.02, 1.37), (0.09, 0.09, 0.12))]
    w.proxies = []
    for joint, c, r in specs:
        ob = G.ellipsoid_cap(prefix + "col_" + joint, c, r, axis=(0, 0, 1), polar=(0, 3.14), N=16, M=10, smooth=True)
        G.set_mat(ob, inv)
        ob.modifiers.new("Collision", "COLLISION")
        ob.collision.thickness_outer = 0.008
        ob.collision.cloth_friction = 8
        attach(ob, rig, joint)
        w.proxies.append(ob)


# ------------------------------------------------------------------ posing
def pose(w, frame, rots, root_loc=None, root_rot=None):
    """rots: {joint: (rx, ry, rz) degrees}; unspecified joints keep their current value.
    Keys every given channel at `frame` (linear; shot scripts key every frame)."""
    for j, r in rots.items():
        e = w.rig[j]
        e.rotation_euler = Euler([math.radians(a) for a in r], "XYZ")
        e.keyframe_insert("rotation_euler", frame=frame)
    if root_loc is not None:
        w.root.location = root_loc
        w.root.keyframe_insert("location", frame=frame)
    if root_rot is not None:
        w.root.rotation_euler = Euler([math.radians(a) for a in root_rot], "XYZ")
        w.root.keyframe_insert("rotation_euler", frame=frame)


def blend_pose(a, b, t):
    out = {}
    for k in set(a) | set(b):
        ra = a.get(k, (0, 0, 0))
        rb = b.get(k, (0, 0, 0))
        out[k] = tuple(x + (y - x) * t for x, y in zip(ra, rb))
    return out
