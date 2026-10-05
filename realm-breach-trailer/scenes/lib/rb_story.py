"""The performance: one deterministic action timeline per act, shared by every
shot that shows that moment (so cuts match). Everything is a function of the
VIDEO frame f; beat timing comes from config/timing.json.

ACT I-III (intro, frames ~-40 .. 760) in the Floor 999 arena:
  warrior_intro(w, f) -> (pose, root_loc, root_rot)
  god_intro(g, f)     -> (pose, root_loc, root_rot, blade_pivot_world_loc, blade_pivot_rot_deg)
  intro_ctrl(f)       -> dict(crack_glow, eye_glow, god_ignite, god_glow, god_eyes, halo)
"""
import json
import math
import os

from mathutils import Euler, Matrix, Vector

import rb_core as C
import rb_motion as MO

_tm = json.load(open(os.path.join(C.ROOT, "config", "timing.json")))


def bf(b):
    """Exact (fractional) video frame of song beat b."""
    return (_tm["song_grid_t0"] + b * _tm["beat_sec"] - _tm["song_offset"]) * C.FPS


STEP = bf(1) - bf(0)                     # frames per beat (~15.05)

# arena layout (mirrors rb_env_arena's locked layout)
GOD_POS = Vector((0.0, 14.0, 0.0))
CLASH = Vector((0.0, 9.0, 0.0))
STOP = Vector((0.0, -2.0, 0.0))
HEAD_W = 180.0                           # warrior faces +Y (toward the god)


def wl(local, root_loc, heading=HEAD_W):
    """Character-local point (rest frame: facing -Y) -> world."""
    return Vector(root_loc) + Matrix.Rotation(math.radians(heading), 3, "Z") @ Vector(local)


def wd(local_dir, heading=HEAD_W):
    return Matrix.Rotation(math.radians(heading), 3, "Z") @ Vector(local_dir)


# the charge starts on O11b's first frame (the roar close-up O11a holds him at the stop through its last frame).
# Shots that start inside the charge (O11b, O12) set CHARGE_PREROLL so their cloth pre-roll before CHARGE_F0 sees the
# charge extrapolated backwards at its initial speed instead of a 4 m teleport.
CHARGE_F0 = next(s["start_frame"] for s in json.load(open(os.path.join(C.ROOT, "edit", "timeline.json")))["shots"]
                 if s["id"] == "O11b")
CHARGE_PREROLL = False


def charging(f):
    return f >= CHARGE_F0 or CHARGE_PREROLL


def charge_y(f):
    f1 = bf(48) - 1
    d = CLASH.y - 0.55 - 2.0
    if f < CHARGE_F0:
        return 2.0 + 0.5 * d / (f1 - CHARGE_F0) * (f - CHARGE_F0)
    u = _seg(f, CHARGE_F0, f1)
    return 2.0 + (0.5 * u + 0.5 * u * u) * d


def _seg(f, a, b):
    return C.clamp01((f - a) / max(1e-6, b - a))


# ------------------------------------------------------------------ walk (O2-O4)
STRIDE = 0.72
N_STEPS = 12                              # steps landing on beats -3 .. 8; the last is the plant on beat 8
SWING = 0.82 * STEP
_F0 = bf(8) - (N_STEPS - 1) * STEP - SWING
_LEAD = 0.2
_START = STOP - Vector((0, (N_STEPS + _LEAD) * STRIDE, 0))
_walk_at, _plants = MO.walk_plan(_START, HEAD_W, _F0, bf(8) + 40, STEP, STRIDE, first="L", stop_frame=bf(8) - 1,
                                 lead=_LEAD)
PLANT_FRAME = bf(8)
PLANT_FOOT = "L" if N_STEPS % 2 == 1 else "R"


def _plant_pos():
    side = PLANT_FOOT
    return max(_plants[side], key=lambda q: q[1])[0]


# carried-low greatsword (right hand, blade angled down and back), char-local targets
LOW_GRIP = Vector((-0.30, 0.02, 0.86))
LOW_BLADE = Vector((-0.12, 0.45, -0.88))


def _upper_walk(f, phase):
    up = MO.blend(MO.POSES_W["stand"], MO.walk_pose(phase % 1.0), 0.6)
    return {k: v for k, v in up.items() if not k.startswith(("thigh", "shin", "foot", "toe"))}


def _legs_planted(w, pose, root, f):
    """Keep the final stance after the walk (feet on their last footholds)."""
    _, feet = _walk_at(f)
    return MO.solve_walk(w, pose, root, HEAD_W, feet)


def _breath(f, amp=1.0):
    return {"spine": (0.8 * amp * math.sin(f / 30 * 2 * math.pi / 3.6), 0, 0),
            "chest": (1.2 * amp * math.sin(f / 30 * 2 * math.pi / 3.6 + 0.4), 0, 0)}


def _sword(w, pose, root, grip_local, blade_local, two=True, heading=HEAD_W):
    return MO.sword_pose(w, pose, wl(grip_local, root, heading), wd(blade_local, heading), two_hands=two,
                         root_loc=root, root_rot=(0, 0, heading))


# key sword configurations (char-local, warrior facing -Y in his own frame)
SALUTE = (Vector((-0.10, -0.34, 1.40)), Vector((0.04, -0.22, 1.0)))
GUARD_LOW = (Vector((-0.24, -0.18, 0.95)), Vector((-0.2, -0.55, 0.8)))
CHARGE = (Vector((-0.28, 0.05, 1.05)), Vector((-0.35, 0.55, 0.75)))
CLASH_HI = (Vector((-0.05, -0.42, 1.62)), Vector((0.55, -0.55, 0.62)))


def point_cfg(root):
    """Blade aimed at the Fallen God's head from the warrior's grip."""
    grip_l = Vector((-0.14, -0.58, 1.42))
    grip_w = wl(grip_l, root)
    head = GOD_POS + Vector((0, 0, 5.15))
    d_w = (head - grip_w).normalized()
    d_l = Matrix.Rotation(math.radians(-HEAD_W), 3, "Z") @ d_w
    return grip_l, d_l


def warrior_intro(w, f):
    """Pose / root for the warrior across Acts I-III (video frames)."""
    # ---- position
    if not charging(f):
        root, feet = _walk_at(min(f, bf(8) + 12))
        heading = HEAD_W
    else:
        # the charge: from y=2 to the clash at D, speed-ramped 0.5x -> 1.5x
        root = Vector((0.15, charge_y(f), 0.0))
        feet = None
        heading = HEAD_W
    rot = (0, 0, heading)
    phase = (f - _F0) / (2 * STEP)

    # ---- body
    if f < bf(8) + 6:                                   # walking (O2, O3, O4)
        up = _upper_walk(f, phase)
        p = _sword(w, up, root, LOW_GRIP, LOW_BLADE, two=False)
        p, loc, rot = MO.solve_walk(w, p, root, heading, feet)
        return p, loc, rot
    base = MO.add(MO.POSES_W["stand"], _breath(f))
    base = {k: v for k, v in base.items() if not k.startswith(("thigh", "shin", "foot", "toe"))}
    if not charging(f):
        # standing at the stop: idle -> raise (O8) -> salute hold (O9) -> point (O10) -> roar (O11a)
        a0, a1 = bf(27.0), bf(34.0)                    # raise
        p0, p1 = bf(39.2), bf(40.6)                    # point
        r0, r1 = bf(44.0), bf(44.6)                    # roar snap
        g_low = (LOW_GRIP + Vector((0.04, -0.06, 0.02)), LOW_BLADE)
        pt = point_cfg(root)
        if f < a0:
            cfg, two = g_low, False
            pose = base
        elif f < a1:
            # 8-frame anticipation dip, then a slow deliberate raise
            u = _seg(f, a0 + 8, a1)
            dip = math.sin(math.pi * _seg(f, a0, a0 + 10)) * 0.04
            e = C.ease_in_out(u)
            cfg = (g_low[0].lerp(SALUTE[0], e) + Vector((0, 0, -dip)), g_low[1].lerp(SALUTE[1], e).normalized())
            two = e > 0.55
            pose = MO.add(base, {"chest": (-4 * e, 0, 4 * e), "head": (-3 * e, 0, 0)})
        elif f < p0:
            cfg, two = SALUTE, True
            pose = MO.add(base, {"chest": (-4, 0, 4), "head": (-3, 0, 0)})
        elif f < r0:
            e = C.ease_in_out(_seg(f, p0, p1))
            cfg = (SALUTE[0].lerp(pt[0], e), SALUTE[1].lerp(pt[1], e).normalized())
            two = e < 0.4
            pose = MO.add(base, MO.blend({"chest": (-4, 0, 4)}, {"spine": (2, 0, -8), "chest": (2, 0, -10),
                                                                   "head": (-4, 0, 8)}, e))
        else:
            e = C.ease_out_back(_seg(f, r0, r1), 1.4)
            cfg = (pt[0].lerp(GUARD_LOW[0], C.clamp01(e)), pt[1].lerp(GUARD_LOW[1], C.clamp01(e)).normalized())
            two = True
            roar = {"spine": (-6, 0, 0), "chest": (-10, 0, 0), "neck": (-8, 0, 0), "head": (-14, 0, 0)}
            pose = MO.add(base, roar, C.clamp01(e))
        p = _sword(w, pose, root, cfg[0], cfg[1], two=two)
        _, feet = _walk_at(bf(8) + 12)
        if f >= bf(44.0):
            # widen the stance for the roar: shift the trailing foot back
            feet = dict(feet)
        return MO.solve_walk(w, p, root, heading, feet)
    # ---- the charge (O11b) and the clash (O12)
    if f < bf(48) - 1:
        run_phase = (f - CHARGE_F0) / 15.0
        up = _upper_walk(f, run_phase)
        lean = {"spine": (14, 0, 0), "chest": (8, 0, 0), "head": (-10, 0, 0)}
        up = MO.add(up, lean)
        # blade comes up from the charge carry into the clash guard over the last 8 frames
        e = C.ease_in(_seg(f, bf(48) - 9, bf(48) - 1))
        cfg = (CHARGE[0].lerp(CLASH_HI[0], e), CHARGE[1].lerp(CLASH_HI[1], e).normalized())
        p = _sword(w, up, root, cfg[0], cfg[1], two=True)
        # running legs: exaggerated gait, FK
        g = MO.walk_pose(run_phase % 1.0)
        legs = {k: (v[0] * 1.8 + (8 if k.startswith("shin") else 0), v[1], v[2]) for k, v in g.items()
                if k.startswith(("thigh", "shin", "foot"))}
        p.update(legs)
        return p, root + Vector((0, 0, 0.03 * abs(math.sin(math.pi * run_phase * 2)))), rot
    # clash: frozen on contact for 2 frames, then driven back a little
    fc = bf(48) - 1
    k = max(0.0, f - (fc + 2))
    push = 0.35 * C.ease_out(min(1.0, k / 10.0))
    rootc = Vector((0.15, CLASH.y - 0.55 - push, 0.0))
    up = MO.add(MO.POSES_W["strike"], {"spine": (-6, 0, 0), "chest": (-8, 0, 0)})
    up = {kk: v for kk, v in up.items() if not kk.startswith(("thigh", "shin", "foot", "toe"))}
    p = _sword(w, up, rootc, CLASH_HI[0], CLASH_HI[1], two=True)
    feet = {"L": (wl((0.13, -0.42, 0.092), rootc), 0.0), "R": (wl((-0.12, 0.38, 0.092), rootc), 8.0)}
    return MO.solve_walk(w, p, rootc + Vector((0, 0, -0.06)), HEAD_W, feet)


# ------------------------------------------------------------------ the Fallen God
_PIV_REST = Vector((0.0, -0.72, 3.15))         # blade pivot at rest (god-local)


def _blade_dir_to_rot(d):
    q = Vector((0, 0, -1)).rotation_difference(Vector(d).normalized())
    e = q.to_euler("XYZ")
    return tuple(math.degrees(v) for v in e)


def god_intro(g, f):
    """Pose/root and blade pivot (god-local = relative to its root) for Acts I-III."""
    root = GOD_POS
    breath = 1.2 * math.sin(f / 30 * 2 * math.pi / 5.5)
    pose = {"spine": (2 + 0.4 * breath, 0, 0), "chest": (3 + 0.6 * breath, 0, 0), "head": (10, 0, 0),
            "neck": (4, 0, 0)}
    # O7: the head tilt (slow, inevitable), held
    t = C.ease_in_out(_seg(f, bf(23.4), bf(25.6)))
    pose = MO.add(pose, {"neck": (2, 8, 0), "head": (2, 12, 6)}, t)
    # blade: planted -> lifted to a high guard (O10-O11a) -> overhead -> strike down to the clash (D)
    piv = _PIV_REST.copy()
    rot = (0.0, 0.0, 0.0)
    l0, l1 = bf(41.0), bf(46.6)
    s0, s1 = bf(46.8), bf(48) - 1
    if f >= l0:
        e = C.ease_in_out(_seg(f, l0, l1))
        hi_piv = Vector((-0.55, -0.35, 4.75))
        hi_dir = Vector((0.25, 0.35, 0.9))
        piv = _PIV_REST.lerp(hi_piv, e)
        rot = _blade_dir_to_rot(Vector((0, 0, -1)).lerp(hi_dir, e))
        pose = MO.add(pose, {"chest": (-6 * e, 0, 10 * e), "head": (-6 * e, 0, 0)})
    if f >= s0:
        e = C.ease_in(_seg(f, s0, s1))
        hi_piv = Vector((-0.55, -0.35, 4.75))
        hit_piv = Vector((-0.2, -1.25, 3.6))
        clash_pt = CLASH + Vector((0.1, 0.0, 2.05)) - GOD_POS     # god-local
        hit_dir = (clash_pt - hit_piv).normalized()
        d = Vector((0.25, 0.35, 0.9)).lerp(hit_dir, e)
        piv = hi_piv.lerp(hit_piv, e)
        rot = _blade_dir_to_rot(d)
        pose = MO.add(pose, {"chest": (-6 + 16 * e, 0, 10 - 16 * e), "spine": (8 * e, 0, 0), "head": (-6 + 10 * e, 0, 0)})
    if f >= bf(48) - 1:
        # recoil after the clash
        k = C.ease_out(min(1.0, (f - (bf(48) + 1)) / 12.0)) if f > bf(48) + 1 else 0.0
        hit_piv = Vector((-0.2, -1.25, 3.6))
        clash_pt = CLASH + Vector((0.1, 0.0, 2.05)) - GOD_POS
        hit_dir = (clash_pt - hit_piv).normalized()
        piv = hit_piv + Vector((0, 0.15, 0.25)) * k
        rot = _blade_dir_to_rot(hit_dir + Vector((0, 0.1, 0.25)) * k)
        pose = MO.add(pose, {"chest": (10 - 4 * k, 0, -6), "spine": (8, 0, 0), "head": (4, 0, 0)})
    world_piv = root + piv
    pose = MO.god_grip_pose(g, pose, world_piv, rot, root_loc=root, root_rot=(0, 0, 0))
    return pose, root, (0, 0, 0), piv, rot


def intro_ctrl(f):
    """Material controls over the intro (video frames)."""
    ign0, ign1 = 160, bf(16) - 12
    ignite = -0.5 + 6.6 * C.ease_in(_seg(f, ign0, ign1)) if f >= ign0 else -0.5
    eyes = 60.0 * C.ease_out(_seg(f, bf(16) - 10, bf(16) - 2))
    # the warrior: eyes steady ember, flare on O9 and the roar; the crack wakes on the raise
    eye = 28.0 + 30.0 * C.smooth(_seg(f, bf(36.6), bf(37.6))) + 40.0 * C.smooth(_seg(f, bf(44.0), bf(44.5)))
    crack = 0.0 + 1.2 * C.smooth(_seg(f, bf(29), bf(34))) + 2.5 * C.smooth(_seg(f, bf(44.0), bf(44.8))) + \
        3.0 * C.smooth(_seg(f, bf(47.3), bf(48)))
    halo = 9.0 * C.smooth(_seg(f, bf(16) - 20, bf(16)))
    return dict(crack_glow=crack, eye_glow=eye, god_ignite=ignite, god_glow=1.0, god_eyes=eyes, halo=halo,
                halo_spin=f * 0.12)


# ====================================================================== ACT V — THE LAST LIFE
class Track:
    """Eased interpolation between keyed states. keys: [(beat, state_dict, ease_name)].
    State values: Vector/tuple (lerped), pose dicts (blended), floats, bools (step)."""
    EASES = {"io": C.ease_in_out, "in": C.ease_in, "out": C.ease_out, "lin": lambda x: x,
             "back": lambda x: C.ease_out_back(x, 1.3), "hold": lambda x: 0.0}

    def __init__(self, keys):
        self.keys = [(kf(b), s, e) for b, s, e in keys]

    def at(self, f):
        ks = self.keys
        if f <= ks[0][0]:
            return dict(ks[0][1])
        for (fa, sa, _), (fb, sb, eb) in zip(ks, ks[1:]):
            if fa <= f <= fb:
                t = self.EASES[eb]((f - fa) / max(1e-6, fb - fa))
                return _mix(sa, sb, t)
        return dict(ks[-1][1])


def _mix(a, b, t):
    out = {}
    for k in set(a) | set(b):
        va, vb = a.get(k, b.get(k)), b.get(k, a.get(k))
        if isinstance(va, dict):
            out[k] = MO.blend(va, vb, t)
        elif isinstance(va, bool) or va is None or isinstance(va, str):
            out[k] = vb if t >= 0.5 else va
        elif isinstance(va, (int, float)):
            out[k] = va + (vb - va) * t
        else:
            out[k] = Vector(va).lerp(Vector(vb), t)
    return out


V3 = Vector
# warrior stances (local frame: facing -Y). feet: local ankle positions.
FEET_GUARD = {"L": V3((0.15, -0.26, 0.092)), "R": V3((-0.15, 0.32, 0.092))}
FEET_WIDE = {"L": V3((0.2, -0.38, 0.092)), "R": V3((-0.18, 0.42, 0.092))}
B_GUARD = {"spine": (8, 0, 0), "chest": (4, 0, 0), "head": (-6, 0, 0)}


def W(root, heading=HEAD_W, body=None, grip=(-0.1, -0.35, 1.1), blade=(0.05, -0.6, 0.8), two=True, feet=None,
      drop=0.05, pitch=0.0, left_free=None):
    return dict(root=V3(root), heading=float(heading), body=body or B_GUARD, grip=V3(grip), blade=V3(blade),
                two=two, feetL=V3((feet or FEET_GUARD)["L"]), feetR=V3((feet or FEET_GUARD)["R"]), drop=drop,
                pitch=pitch, left=V3(left_free) if left_free else V3((0, 0, 0)), lf=1.0 if left_free else 0.0)


def to_local(pw, root, heading=HEAD_W):
    return Matrix.Rotation(math.radians(-heading), 3, "Z") @ (V3(pw) - V3(root))


def W_hit(root, grip, contact, **kw):
    """Warrior state whose blade passes through the world contact point."""
    d = (to_local(contact, root) - V3(grip)).normalized()
    return W(root, grip=grip, blade=d, **kw)


# contact points (world) of every blade-on-blade beat, shared by both performers
CONTACT = {
    88.5: V3((-0.55, 9.75, 1.85)),
    93.5: V3((-0.2, 10.75, 1.9)),
    94.5: V3((0.4, 10.65, 1.6)),
    95.2: V3((0.05, 10.55, 2.1)),
    98.0: V3((-0.6, 9.4, 1.72)),
    99.62: V3((0.4, 9.45, 1.4)),
}
# blade contacts (and the F1b floor smash) are keyed on the frame the sparks, shake and SFX fire: 1-2 frames before
# their beat, instead of exactly on it (the bursts used to fire while the blades were still swinging)
IMPACT = set(CONTACT) | {90.3}


def kf(b):
    return (int(bf(b)) - 1) if b in IMPACT else bf(b)


SLAM = V3((0.3, 9.4, 0.02))
_A5 = (0.05, 8.9, 0.0)
_KNOCK = (-0.35, 4.6, 0.17)
WARRIOR_V = Track([
    (87.6, W(_A5, grip=(0.25, -0.3, 1.15), blade=(0.25, -0.4, 0.88)), "io"),
    (88.5, W_hit(_A5, (0.3, -0.36, 1.2), CONTACT[88.5], drop=0.09), "out"),
    (89.4, W((0.0, 8.85, 0), grip=(0.0, -0.3, 1.15), blade=(0.1, -0.3, 0.95)), "io"),
    (90.2, W((-1.2, 8.95, 0), body={"spine": (14, 8, 0), "chest": (8, 6, 0)}, grip=(-0.25, -0.2, 1.0),
             blade=(-0.2, -0.5, 0.85), feet=FEET_WIDE, drop=0.16), "out"),                 # dodge sideways
    (90.9, W((-1.2, 9.0, 0), body={"spine": (4, 0, 0), "chest": (0, 0, -16)}, grip=(-0.3, 0.05, 0.9),
             blade=(-0.2, 0.6, -0.75), two=False, left_free=(0.24, -0.62, 1.42)), "io"),  # cast Q
    (91.9, W((-1.2, 9.0, 0), body={"spine": (4, 0, 0), "chest": (0, 0, -18)}, grip=(-0.3, 0.05, 0.9),
             blade=(-0.2, 0.6, -0.75), two=False, left_free=(0.22, -0.6, 1.5)), "io"),    # cast E
    (93.0, W((-0.5, 9.3, 0), grip=(-0.05, 0.12, 2.0), blade=(0.1, 0.6, 0.8), body={"spine": (-6, 0, 0), "chest": (-8, 0, 0)}), "io"),
    (93.5, W_hit((-0.35, 9.55, 0), (-0.05, -0.55, 1.35), CONTACT[93.5], body={"spine": (16, 0, 0), "chest": (10, 0, 0)},
                 feet=FEET_WIDE, drop=0.12), "in"),                                         # strike 1 (parried)
    (94.1, W((-0.3, 9.5, 0), grip=(-0.1, 0.05, 1.9), blade=(0.6, 0.45, 0.6)), "io"),
    (94.5, W_hit((-0.1, 9.6, 0), (-0.15, -0.5, 1.3), CONTACT[94.5], body={"spine": (10, 0, -14), "chest": (6, 0, -12)},
                 feet=FEET_WIDE, drop=0.12), "in"),                                         # strike 2 (parried)
    (95.2, W_hit((0.0, 9.45, 0), (-0.1, -0.5, 1.5), CONTACT[95.2], feet=FEET_WIDE, drop=0.1), "in"),
    (96.0, W((-0.15, 9.2, 0), grip=(-0.1, -0.35, 1.1), blade=(0.05, -0.6, 0.8)), "io"),
    (97.6, W_hit((-0.2, 9.0, 0), (-0.3, -0.28, 1.62), CONTACT[98.0] + V3((0, 0, 0.12)), drop=0.1), "io"),
    (98.0, W_hit((-0.2, 9.0, 0), (-0.3, -0.26, 1.48), CONTACT[98.0], drop=0.22,
                 body={"spine": (12, 0, 0), "chest": (8, 0, 0)}), "in"),                   # crushed down
    (99.3, W((-0.2, 8.95, 0), grip=(-0.3, -0.3, 1.3), blade=(0.1, -0.2, 1.0), drop=0.12), "io"),
    (99.62, W_hit((-0.15, 8.9, 0.0), (0.25, -0.3, 1.25), CONTACT[99.62], drop=0.1), "in"),       # struck
    (99.95, W((-0.25, 7.4, 0.35), grip=(-0.3, -0.1, 1.4), blade=(0.3, 0.2, 0.9), pitch=-35,
              body={"spine": (-14, 0, 8), "chest": (-12, 0, 6), "head": (-10, 0, 0)}), "out"),   # thrown
    (100.4, W(_KNOCK, grip=(-0.42, 0.25, 0.25), blade=(-0.6, 0.6, -0.1), two=False, pitch=-90,
              body={"spine": (-4, 0, 0), "head": (12, 0, 0), "upperarm_L": (-30, -40, 0)}), "out"),   # on his back
    (113.0, W(_KNOCK, grip=(-0.42, 0.25, 0.25), blade=(-0.6, 0.6, -0.1), two=False, pitch=-90,
              body={"spine": (-4, 0, 0), "head": (14, 0, 0), "upperarm_L": (-30, -40, 0)}), "hold"),
])
# F4: kneel and rise using the planted sword (beats 114.5 -> 120); F5/F6 standing; F7 god attack.
_RISE = (-0.35, 5.0, 0.0)


def _kneel_state(u):
    """0 = turning onto a knee, 1 = standing in guard."""
    root = V3(_RISE)
    kneel = {"spine": (18, 0, 0), "chest": (12, 0, 0), "neck": (10, 0, 0), "head": (14, 0, 0)}
    stand = {"spine": (4, 0, 0), "chest": (-2, 0, 0), "head": (-4, 0, 0)}
    body = MO.blend(kneel, stand, u)
    grip = V3((-0.18, -0.48, 0.78)).lerp(V3((-0.12, -0.4, 1.05)), u)
    blade = V3((0.0, -0.12, -1.0)).lerp(V3((0.05, -0.35, 0.93)), C.smooth(min(1.0, u * 1.4)))
    return dict(root=root, body=body, grip=grip, blade=blade, drop=0.62 * (1 - u))


def warrior_battle(w, f):
    """Act V pose for video frame f."""
    if f < bf(113.0):
        s = WARRIOR_V.at(f)
        heading = s["heading"]
        root = s["root"]
        pitch = s["pitch"]
        rot = (pitch, 0, heading)
        body = dict(s["body"])
        if pitch < -40:
            # lying on his back after the throw: FK only, body relaxed
            p = MO.add(MO.POSES_W["stand"], body)
            p.update({"thigh_L": (-20, 0, 0), "shin_L": (30, 0, 0), "thigh_R": (-6, 0, 0), "shin_R": (10, 0, 0),
                      "upperarm_R": (-20, 40, 0), "forearm_R": (-30, 0, 0)})
            return p, root, rot
        base = MO.add(MO.POSES_W["stand"], body)
        base = {k: v for k, v in base.items() if not k.startswith(("thigh", "shin", "foot", "toe"))}
        p = MO.sword_pose(w, base, wl(s["grip"], root, heading), wd(s["blade"], heading), two_hands=s["two"],
                          root_loc=root, root_rot=rot)
        if s["lf"] > 0.5:
            p = MO.two_bone(w, p, ("upperarm_L", "forearm_L", "hand_L"), wl(s["left"], root, heading),
                            V3((0.6, 0.6, -0.4)), root, rot)
        feet = {"L": (wl(s["feetL"], root, heading), 0.0), "R": (wl(s["feetR"], root, heading), 6.0)}
        if pitch > -5:
            return MO.solve_walk(w, p, root, heading, feet, hip_drop=s["drop"])
        return p, root, rot
    # F4 rise: lying -> rolled to a knee by 114.6 -> stands by 119.5
    if f < bf(119.5):
        u = C.ease_in_out(_seg(f, bf(114.6), bf(119.5)))
        s = _kneel_state(u)
        roll = 1.0 - C.ease_out(_seg(f, bf(113.0), bf(114.6)))
        root = s["root"]
        base = MO.add(MO.POSES_W["stand"], s["body"])
        base = {k: v for k, v in base.items() if not k.startswith(("thigh", "shin", "foot", "toe"))}
        p = MO.sword_pose(w, base, wl(s["grip"], root), wd(s["blade"]), two_hands=False, root_loc=root,
                          root_rot=(0, 0, HEAD_W))
        p = MO.two_bone(w, p, ("upperarm_L", "forearm_L", "hand_L"), wl(V3((0.18, -0.35, 0.62 + 0.5 * u)), root),
                        V3((0.6, 0.4, -0.5)), root, (0, 0, HEAD_W))
        knee = 1 - u
        feet = {"L": (wl(V3((0.14, -0.42, 0.092)), root), 0.0),
                "R": (wl(V3((-0.13, 0.1 + 0.25 * knee, 0.092 + 0.12 * knee)), root), 40 * knee)}
        p, loc, rot = MO.solve_walk(w, p, root, HEAD_W, feet, hip_drop=s["drop"])
        if roll > 0:
            rot = (-90 * roll, 0, HEAD_W)
            loc = loc.lerp(V3(_KNOCK), roll)
        return p, loc, rot
    # F5/F6 stand, gripping, then the God Attack (F7, U = beat 128)
    root = V3(_RISE)
    a0, a1, a2 = bf(126.6), bf(127.6), bf(128.0)
    guard = (V3((-0.12, -0.4, 1.05)), V3((0.05, -0.35, 0.93)))
    wind = (V3((-0.05, 0.12, 2.02)), V3((0.1, 0.62, 0.78)))
    gtar = GOD_POS + V3((0, 0, 3.4))
    gl = V3((-0.05, -0.62, 1.45))
    gdir_w = (gtar - wl(gl, root)).normalized()
    gdir = Matrix.Rotation(math.radians(-HEAD_W), 3, "Z") @ gdir_w
    body = {"spine": (4, 0, 0), "chest": (-2, 0, 0), "head": (-4, 0, 0)}
    if f < a0:
        grip, blade = guard
        br = _breath(f, 1.6)
        body = MO.add(body, br)
    elif f < a1:
        e = C.ease_in_out(_seg(f, a0, a1))
        grip, blade = guard[0].lerp(wind[0], e), guard[1].lerp(wind[1], e).normalized()
        body = MO.add(body, {"spine": (-8 * e, 0, 0), "chest": (-10 * e, 0, 0), "head": (-6 * e, 0, 0)})
    else:
        e = C.ease_in(_seg(f, a1, a2 - 1))
        grip, blade = wind[0].lerp(gl, e), wind[1].lerp(gdir, e).normalized()
        body = MO.add(body, {"spine": (-8 + 26 * e, 0, 0), "chest": (-10 + 20 * e, 0, 0), "head": (-6 + 2 * e, 0, 0)})
    base = MO.add(MO.POSES_W["stand"], body)
    base = {k: v for k, v in base.items() if not k.startswith(("thigh", "shin", "foot", "toe"))}
    p = MO.sword_pose(w, base, wl(grip, root), wd(blade), two_hands=True, root_loc=root, root_rot=(0, 0, HEAD_W))
    lunge = C.ease_in(_seg(f, a1, a2))
    feet = {"L": (wl(V3((0.15, -0.3 - 0.25 * lunge, 0.092)), root), 0.0), "R": (wl(V3((-0.15, 0.35, 0.092)), root), 6.0)}
    return MO.solve_walk(w, p, root, HEAD_W, feet, hip_drop=0.05 + 0.12 * lunge)


def god_battle(g, f):
    """Act V: (pose, root, root_rot, pivot_local, pivot_rot)."""
    root = GOD_POS
    breath = 1.2 * math.sin(f / 30 * 2 * math.pi / 5.5)
    pose = {"spine": (2 + 0.4 * breath, 0, 0), "chest": (3 + 0.6 * breath, 0, 0), "head": (14, 0, 0), "neck": (6, 0, 0)}
    # blade keys: (beat, pivot_local, blade_dir, body add, ease)
    def hit(piv_l, c):
        return (V3(c) - (root + V3(piv_l))).normalized()
    K = [
        (87.6, V3((0.9, -0.6, 3.9)), V3((-0.95, -0.25, 0.15)), {"chest": (0, 0, 22)}, "io"),
        (88.5, V3((0.35, -1.15, 3.55)), hit((0.35, -1.15, 3.55), CONTACT[88.5]), {"chest": (6, 0, -10)}, "in"),
        (89.5, V3((-0.4, -0.5, 4.8)), V3((0.1, 0.4, 0.9)), {"chest": (-8, 0, 6)}, "io"),
        (90.3, V3((-0.3, -1.5, 2.6)), hit((-0.3, -1.5, 2.6), SLAM), {"chest": (18, 0, 0), "spine": (8, 0, 0)}, "in"),
        (91.5, V3((-0.3, -1.45, 2.7)), hit((-0.3, -1.45, 2.7), SLAM + V3((0, 0.2, 0))), {"chest": (12, 0, 0), "spine": (6, 0, 0)}, "io"),
        (92.6, V3((0.0, -0.9, 3.5)), V3((0.0, -0.5, 0.85)), {}, "io"),
        (93.5, V3((-0.2, -1.3, 3.4)), hit((-0.2, -1.3, 3.4), CONTACT[93.5]), {"chest": (6, 0, 0)}, "out"),
        (94.5, V3((0.3, -1.3, 3.3)), hit((0.3, -1.3, 3.3), CONTACT[94.5]), {"chest": (6, 0, 6)}, "out"),
        (95.2, V3((0.0, -1.25, 3.6)), hit((0.0, -1.25, 3.6), CONTACT[95.2]), {"chest": (8, 0, 0)}, "out"),
        (96.2, V3((0.0, -0.8, 3.6)), V3((0.0, -0.2, 0.98)), {}, "io"),
        (97.7, V3((-0.3, -0.2, 5.1)), V3((0.1, 0.45, 0.85)), {"chest": (-10, 0, 0), "head": (-6, 0, 0)}, "io"),
        (98.0, V3((-0.05, -1.3, 4.1)), hit((-0.05, -1.3, 4.1), CONTACT[98.0]), {"chest": (14, 0, 0), "spine": (8, 0, 0)}, "in"),
        (99.1, V3((1.0, -0.4, 3.9)), V3((0.9, 0.3, 0.3)), {"chest": (0, 0, 28)}, "io"),
        (99.62, V3((-0.4, -1.3, 3.3)), hit((-0.4, -1.3, 3.3), CONTACT[99.62]), {"chest": (6, 0, -18)}, "in"),
        (101.5, V3((-0.2, -0.9, 3.3)), V3((-0.1, -0.2, -0.97)), {"chest": (4, 0, 0)}, "io"),
        (103.0, V3((0.0, -0.75, 3.2)), V3((0.0, -0.05, -1.0)), {"head": (14, 0, 0)}, "io"),   # blade planted again
        (126.6, V3((0.0, -0.75, 3.2)), V3((0.0, -0.05, -1.0)), {"head": (18, 0, 0)}, "hold"),
        (127.8, V3((-0.4, -0.3, 4.9)), V3((0.1, 0.35, 0.92)), {"chest": (-8, 0, 0)}, "io"),   # too late
        (128.4, V3((-0.3, 0.2, 4.6)), V3((0.3, 0.6, 0.7)), {"chest": (-22, 0, 0), "spine": (-10, 0, 0),
                                                             "head": (-20, 0, 0)}, "out"),     # blasted back
    ]
    if f <= kf(K[0][0]):
        piv, d, add, ease = K[0][1], K[0][2], K[0][3], "io"
    elif f >= kf(K[-1][0]):
        piv, d, add = K[-1][1], K[-1][2], K[-1][3]
    else:
        for (ba, pa, da, aa, _), (bb, pb, db, ab, eb) in zip(K, K[1:]):
            if kf(ba) <= f <= kf(bb):
                t = Track.EASES[eb](_seg(f, kf(ba), kf(bb)))
                piv = pa.lerp(pb, t)
                d = da.lerp(db, t).normalized()
                add = MO.blend(aa, ab, t)
                break
    pose = MO.add(pose, add)
    # F3: he looks down at the fallen warrior while he speaks
    look = C.smooth(_seg(f, bf(103.0), bf(106.0))) * (1 - C.smooth(_seg(f, bf(126.0), bf(127.0))))
    pose = MO.add(pose, {"neck": (8, 0, 0), "head": (16, -4, 0)}, look)
    rot = _blade_dir_to_rot(d)
    pose = MO.god_grip_pose(g, pose, root + piv, rot, root_loc=root, root_rot=(0, 0, 0))
    return pose, root, (0, 0, 0), piv, rot


def battle_ctrl(f):
    """Act V material controls."""
    crack = 1.5 + 2.0 * C.smooth(_seg(f, bf(124.6), bf(125.6))) + 4.0 * C.smooth(_seg(f, bf(126.8), bf(128.0)))
    crack *= 1.0 - 0.6 * C.smooth(_seg(f, bf(100.4), bf(101.0))) * (1 - C.smooth(_seg(f, bf(114.0), bf(120.0))))
    eye = 28 + 45 * C.smooth(_seg(f, bf(124.6), bf(126.0))) + 70 * C.smooth(_seg(f, bf(127.0), bf(128.0)))
    god_glow = 1.0 + 1.5 * C.smooth(_seg(f, bf(103.0), bf(105.0))) * (1 - C.smooth(_seg(f, bf(124.6), bf(126.0)))) \
        + 6.0 * C.smooth(_seg(f, bf(128.0), bf(128.4)))
    return dict(crack_glow=crack, eye_glow=eye, god_ignite=8.0, god_glow=god_glow, god_eyes=60.0, halo=9.0,
                halo_spin=f * 0.12)


# ====================================================================== ACT VI — AFTER
def warrior_after(w, f):
    """E2: exhausted, leaning on the planted greatsword, heavy breathing."""
    root = V3(_RISE)
    br = math.sin(f / 30 * 2 * math.pi / 2.2)
    body = {"spine": (14 + 3 * br, 0, 0), "chest": (8 + 4 * br, 0, 0), "neck": (6, 0, 0), "head": (16 - 3 * br, 0, 4)}
    base = MO.add(MO.POSES_W["stand"], body)
    base = {k: v for k, v in base.items() if not k.startswith(("thigh", "shin", "foot", "toe"))}
    grip = V3((-0.12, -0.42, 0.98 + 0.01 * br))
    p = MO.sword_pose(w, base, wl(grip, root), wd(V3((0.0, -0.18, -1.0))), two_hands=True, root_loc=root,
                      root_rot=(0, 0, HEAD_W), left_slide=0.1)
    feet = {"L": (wl(V3((0.16, -0.12, 0.092)), root), 0.0), "R": (wl(V3((-0.15, 0.2, 0.092)), root), 0.0)}
    return MO.solve_walk(w, p, root, HEAD_W, feet, hip_drop=0.06 + 0.01 * br)


def god_after(g, f):
    """E2: the Fallen God collapsed onto his knees, head bowed, blade fallen on the floor."""
    root = GOD_POS + V3((0.0, -0.4, -1.45))
    pose = {"spine": (24, 0, 4), "chest": (16, 0, 6), "neck": (14, 0, 0), "head": (30, 0, 8),
            "thigh_L": (-78, 0, 4), "shin_L": (96, 0, 0), "foot_L": (40, 0, 0),
            "thigh_R": (-30, 0, -6), "shin_R": (112, 0, 0), "foot_R": (50, 0, 0),
            "upperarm_L": (-12, -6, 0), "forearm_L": (-20, 0, 0), "upperarm_R": (-6, 10, 0), "forearm_R": (-12, 0, 0)}
    piv = V3((1.7, -1.0, 1.55))           # local to the (lowered) root -> lying on the floor
    rot = _blade_dir_to_rot(V3((0.35, -0.94, 0.0)))
    return pose, root, (0, 0, 0), piv, rot


def after_ctrl(f):
    flick = 0.5 + 0.5 * math.sin(f * 0.37) * math.sin(f * 0.11)
    return dict(crack_glow=0.9, eye_glow=22.0, god_ignite=8.0, god_glow=0.25 + 0.25 * flick, god_eyes=6.0,
                halo=0.0, halo_spin=0.0)

