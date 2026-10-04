"""Generic warrior actions for the montage (and anywhere else).

Every action is a function act(u) -> state, u = 0..1 normalised action time,
returning a Track-style state (root offset, body pose, sword grip/blade in the
character's local frame, feet, hip drop). `perform(w, f, action, f_peak, ...)`
places the action in the world (position + heading), maps frames to u so the
action's IMPACT lands exactly on f_peak, and solves IK.

Impact fraction of each action (u where the hit lands) is in PEAK.
"""
import math

from mathutils import Matrix, Vector

import rb_core as C
import rb_motion as MO

V3 = Vector
FEET = {"L": V3((0.15, -0.26, 0.092)), "R": V3((-0.15, 0.32, 0.092))}
FEET_WIDE = {"L": V3((0.2, -0.40, 0.092)), "R": V3((-0.18, 0.44, 0.092))}

GUARD = dict(grip=V3((-0.1, -0.35, 1.1)), blade=V3((0.05, -0.6, 0.8)), two=True)
OVERHEAD = dict(grip=V3((-0.05, 0.12, 2.02)), blade=V3((0.1, 0.62, 0.78)), two=True)
CLEAVE_END = dict(grip=V3((-0.05, -0.62, 0.85)), blade=V3((0.0, -0.78, -0.62)), two=True)
SLASH_WIND = dict(grip=V3((-0.45, 0.05, 1.35)), blade=V3((-0.85, 0.45, 0.25)), two=True)
SLASH_END = dict(grip=V3((0.35, -0.45, 1.15)), blade=V3((0.9, -0.3, -0.15)), two=True)
BLOCK_HI = dict(grip=V3((-0.3, -0.28, 1.62)), blade=V3((0.95, -0.25, 0.2)), two=True)
THRUST_WIND = dict(grip=V3((-0.2, 0.25, 1.15)), blade=V3((0.0, -0.95, 0.15)), two=True)
THRUST_END = dict(grip=V3((-0.08, -0.75, 1.25)), blade=V3((0.0, -1.0, 0.05)), two=True)
LOW = dict(grip=V3((-0.3, 0.02, 0.86)), blade=V3((-0.12, 0.45, -0.88)), two=False)
SHORT_GUARD = dict(grip=V3((-0.2, -0.35, 1.05)), blade=V3((0.0, -0.8, 0.6)), two=False)

PEAK = {"cleave": 0.62, "slash": 0.6, "block": 0.55, "thrust": 0.6, "cast": 0.55, "god_attack": 0.7,
        "hit_react": 0.25, "fall": 0.85, "kneel": 1.0, "rise": 1.0, "idle": 0.5, "walk": 0.5, "run": 0.5,
        "short_slash": 0.6}


def _st(cfg, body=None, feet=FEET, drop=0.05, root=(0, 0, 0), pitch=0.0, left=None):
    return dict(grip=V3(cfg["grip"]), blade=V3(cfg["blade"]).normalized(), two=cfg["two"], body=body or {},
                feetL=V3(feet["L"]), feetR=V3(feet["R"]), drop=drop, root=V3(root), pitch=pitch,
                left=V3(left) if left else None)


def _mixst(a, b, t):
    out = {}
    for k in a:
        va, vb = a[k], b[k]
        if isinstance(va, dict):
            out[k] = MO.blend(va, vb, t)
        elif isinstance(va, bool):
            out[k] = vb if t > 0.5 else va
        elif va is None or vb is None:
            out[k] = vb if t > 0.5 else va
        elif isinstance(va, (int, float)):
            out[k] = va + (vb - va) * t
        else:
            out[k] = va.lerp(vb, t)
    if out.get("blade") is not None:
        out["blade"] = out["blade"].normalized()
    return out


def _keys(u, keys):
    """keys: [(u, state, ease)]"""
    if u <= keys[0][0]:
        return keys[0][1]
    for (ua, sa, _), (ub, sb, eb) in zip(keys, keys[1:]):
        if ua <= u <= ub:
            e = {"io": C.ease_in_out, "in": C.ease_in, "out": C.ease_out, "back": lambda x: C.ease_out_back(x, 1.4),
                 "lin": lambda x: x}[eb]
            return _mixst(sa, sb, e((u - ua) / max(1e-6, ub - ua)))
    return keys[-1][1]


B_UP = {"spine": (-6, 0, 0), "chest": (-10, 0, 0), "head": (-6, 0, 0)}
B_DOWN = {"spine": (18, 0, 0), "chest": (12, 0, 0), "head": (4, 0, 0)}
B_TWIST_R = {"spine": (4, 0, 18), "chest": (2, 0, 16)}
B_TWIST_L = {"spine": (8, 0, -18), "chest": (4, 0, -16)}


def cleave(u):
    return _keys(u, [(0.0, _st(GUARD), "io"), (0.12, _st(GUARD, drop=0.1), "io"),          # anticipation dip
                     (0.45, _st(OVERHEAD, B_UP), "io"), (0.62, _st(CLEAVE_END, B_DOWN, FEET_WIDE, 0.16), "in"),
                     (1.0, _st(CLEAVE_END, B_DOWN, FEET_WIDE, 0.14), "out")])


def slash(u):
    return _keys(u, [(0.0, _st(GUARD), "io"), (0.35, _st(SLASH_WIND, B_TWIST_R, drop=0.1), "io"),
                     (0.6, _st(SLASH_END, B_TWIST_L, FEET_WIDE, 0.14), "in"),
                     (1.0, _st(SLASH_END, B_TWIST_L, FEET_WIDE, 0.12), "out")])


def short_slash(u):
    wind = dict(grip=V3((-0.4, 0.1, 1.3)), blade=V3((-0.7, 0.5, 0.5)), two=False)
    end = dict(grip=V3((0.25, -0.45, 1.05)), blade=V3((0.85, -0.45, -0.2)), two=False)
    return _keys(u, [(0.0, _st(SHORT_GUARD), "io"), (0.35, _st(wind, B_TWIST_R), "io"),
                     (0.6, _st(end, B_TWIST_L, FEET_WIDE, 0.12), "in"), (1.0, _st(end, B_TWIST_L, FEET_WIDE, 0.1), "out")])


def block(u):
    return _keys(u, [(0.0, _st(GUARD), "io"), (0.45, _st(BLOCK_HI, {"spine": (4, 0, 0)}, drop=0.1), "out"),
                     (0.55, _st(BLOCK_HI, {"spine": (12, 0, 0), "chest": (8, 0, 0)}, FEET_WIDE, 0.2), "in"),
                     (1.0, _st(BLOCK_HI, {"spine": (6, 0, 0)}, FEET_WIDE, 0.12), "io")])


def thrust(u):
    return _keys(u, [(0.0, _st(GUARD), "io"), (0.35, _st(THRUST_WIND, {"spine": (-4, 0, 10)}, drop=0.08), "io"),
                     (0.6, _st(THRUST_END, {"spine": (16, 0, -6), "chest": (8, 0, 0)}, FEET_WIDE, 0.18), "in"),
                     (1.0, _st(THRUST_END, {"spine": (12, 0, 0)}, FEET_WIDE, 0.15), "out")])


def cast(u):
    """Left palm thrust (Q/E); the sword hangs low in the right hand."""
    a = _st(LOW, {"chest": (0, 0, 0)}, left=(0.2, -0.25, 1.1))
    b = _st(LOW, {"spine": (-4, 0, -10), "chest": (-4, 0, -14)}, FEET_WIDE, 0.1, left=(0.22, 0.05, 1.45))
    c = _st(LOW, {"spine": (10, 0, -16), "chest": (6, 0, -18)}, FEET_WIDE, 0.12, left=(0.22, -0.68, 1.45))
    return _keys(u, [(0.0, a, "io"), (0.35, b, "io"), (0.55, c, "in"), (1.0, c, "out")])


def god_attack(u):
    wind = dict(grip=V3((-0.05, 0.15, 2.05)), blade=V3((0.08, 0.6, 0.8)), two=True)
    end = dict(grip=V3((-0.05, -0.62, 1.45)), blade=V3((0.0, -0.98, 0.18)), two=True)
    return _keys(u, [(0.0, _st(GUARD), "io"), (0.15, _st(GUARD, drop=0.12), "io"),
                     (0.5, _st(wind, B_UP, drop=0.03), "io"), (0.7, _st(end, B_DOWN, FEET_WIDE, 0.16), "in"),
                     (1.0, _st(end, B_DOWN, FEET_WIDE, 0.14), "out")])


def hit_react(u):
    hit = _st(GUARD, {"spine": (-16, 0, 6), "chest": (-14, 0, 8), "head": (-18, 0, 0)}, FEET_WIDE, 0.06,
              root=(0, 0.25, 0))
    back = _st(GUARD, {"spine": (-24, 0, 10), "chest": (-18, 0, 10), "head": (-20, 0, 0)}, FEET_WIDE, 0.04,
               root=(0, 0.55, 0))
    return _keys(u, [(0.0, _st(GUARD), "io"), (0.25, hit, "in"), (1.0, back, "out")])


def fall(u):
    """Knocked backward to the floor (pitch -> -90). Root offset goes back."""
    a = _st(GUARD, {"spine": (-10, 0, 0)}, FEET_WIDE, 0.05)
    b = _st(LOW, {"spine": (-18, 0, 6), "chest": (-14, 0, 6), "head": (-14, 0, 0)}, FEET_WIDE, 0.0,
            root=(0, 0.9, 0.35), pitch=-40)
    c = _st(LOW, {"spine": (-4, 0, 0), "head": (12, 0, 0)}, FEET_WIDE, 0.0, root=(0, 1.7, 0.17), pitch=-90)
    return _keys(u, [(0.0, a, "io"), (0.4, b, "out"), (0.85, c, "in"), (1.0, c, "out")])


def kneel(u):
    stand = _st(GUARD, {"spine": (4, 0, 0)})
    kn = dict(grip=V3((-0.18, -0.48, 0.78)), blade=V3((0.0, -0.12, -1.0)), two=False)
    k = _st(kn, {"spine": (18, 0, 0), "chest": (12, 0, 0), "neck": (10, 0, 0), "head": (16, 0, 0)},
            {"L": V3((0.14, -0.42, 0.092)), "R": V3((-0.13, 0.35, 0.21))}, 0.62)
    return _keys(u, [(0.0, stand, "io"), (1.0, k, "io")])


def rise(u):
    return kneel(1.0 - u)


def idle(u):
    return _st(GUARD, {"spine": (2 * math.sin(u * 6.28), 0, 0)})


ACTIONS = {"cleave": cleave, "slash": slash, "short_slash": short_slash, "block": block, "thrust": thrust,
           "cast": cast, "god_attack": god_attack, "hit_react": hit_react, "fall": fall, "kneel": kneel,
           "rise": rise, "idle": idle}


def perform(w, f, action, f_peak, dur_frames, pos, heading, speed=1.0, slowmo=1.0):
    """Key-ready pose for frame f: the action's impact lands on f_peak. Returns (pose, loc, rot).
    slowmo < 1 stretches the action in time (0.5 = 50% slow motion)."""
    fn = ACTIONS[action]
    pk = PEAK[action]
    dur = dur_frames / (speed * slowmo)
    u = pk + (f - f_peak) / dur
    u = C.clamp01(u)
    s = fn(u)
    R = Matrix.Rotation(math.radians(heading), 3, "Z")
    root = V3(pos) + R @ s["root"]
    rot = (s["pitch"], 0, heading)
    base = MO.add(MO.POSES_W["stand"], s["body"])
    base = {k: v for k, v in base.items() if not k.startswith(("thigh", "shin", "foot", "toe"))}
    p = MO.sword_pose(w, base, root + R @ s["grip"], R @ s["blade"], two_hands=s["two"], root_loc=root, root_rot=rot)
    if s.get("left") is not None and not s["two"]:
        p = MO.two_bone(w, p, ("upperarm_L", "forearm_L", "hand_L"), root + R @ s["left"], R @ V3((0.6, 0.5, -0.4)),
                        root, rot)
    if abs(s["pitch"]) > 5:
        p.update({"thigh_L": (-20, 0, 0), "shin_L": (30, 0, 0), "thigh_R": (-6, 0, 0), "shin_R": (14, 0, 0)})
        return p, root, rot
    feet = {"L": (root + R @ s["feetL"] - R @ V3((0, 0, 0)), 0.0), "R": (root + R @ s["feetR"], 6.0)}
    # feet stay planted relative to the action's start position (no sliding with root offsets)
    feet = {"L": (V3(pos) + R @ s["feetL"], 0.0), "R": (V3(pos) + R @ s["feetR"], 6.0)}
    return MO.solve_walk(w, p, root, heading, feet, hip_drop=s["drop"])
