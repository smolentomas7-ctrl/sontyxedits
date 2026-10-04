"""Motion library for the warrior and the Fallen God (FK empties, world-aligned at rest).

Axis conventions (empties keep world-aligned axes at rest; angles in degrees):
  spine / chest / neck / head : +X bends forward, Y side-bend, Z twist
  thigh : -X lifts the leg forward          shin : +X bends the knee
  foot  : -X toes up, +X toes down
  upperarm : -X raises the arm forward/up   forearm : -X bends the elbow
  upperarm abduction : left -Y, right +Y    hand : X flex, Z twist
  root  : Z heading; 0 = facing -Y, 180 = facing +Y (toward the Fallen God in the arena)

Poses are dicts {joint: (rx, ry, rz)}; missing joints are 0. Motion is keyed one
key per frame by the shot scripts through play()/key_pose().
"""
import math

from mathutils import Euler, Vector

import rb_core as C

W_JOINTS = ["pelvis", "spine", "chest", "neck", "head", "clav_L", "upperarm_L", "forearm_L", "hand_L", "fingers_L",
            "clav_R", "upperarm_R", "forearm_R", "hand_R", "fingers_R", "thigh_L", "shin_L", "foot_L", "toe_L",
            "thigh_R", "shin_R", "foot_R", "toe_R"]
G_JOINTS = ["pelvis", "spine", "chest", "neck", "head", "clav_L", "upperarm_L", "forearm_L", "hand_L",
            "clav_R", "upperarm_R", "forearm_R", "hand_R", "thigh_L", "shin_L", "foot_L", "thigh_R", "shin_R", "foot_R"]

# ------------------------------------------------------------------ warrior poses
POSES_W = {
    "rest": {},
    "stand": {"spine": (3, 0, 0), "chest": (2, 0, 0), "upperarm_L": (-4, -7, 0), "forearm_L": (-12, 0, 0),
              "upperarm_R": (-6, 7, 0), "forearm_R": (-18, 0, 0), "hand_R": (35, 0, 0),
              "thigh_L": (-4, 0, 0), "shin_L": (6, 0, 0), "foot_L": (-2, 0, 0),
              "thigh_R": (-4, 0, 0), "shin_R": (6, 0, 0), "foot_R": (-2, 0, 0)},
    "raise": {"spine": (-2, 0, 0), "chest": (-4, 0, 6), "upperarm_L": (-10, -10, 0), "forearm_L": (-20, 0, 0),
              "upperarm_R": (-95, 10, 0), "forearm_R": (-60, 0, 0), "hand_R": (-20, 0, 0),
              "thigh_L": (-6, 0, 0), "shin_L": (8, 0, 0), "thigh_R": (2, 0, 0), "shin_R": (4, 0, 0)},
    "point": {"spine": (2, 0, -8), "chest": (2, 0, -10), "neck": (-2, 0, 6), "head": (-4, 0, 8),
              "upperarm_L": (-6, -10, 0), "forearm_L": (-15, 0, 0),
              "upperarm_R": (-80, 2, 0), "forearm_R": (-5, 0, 0), "hand_R": (-10, 0, 0),
              "thigh_L": (-14, 0, 0), "shin_L": (16, 0, 0), "foot_L": (-4, 0, 0),
              "thigh_R": (8, 0, 0), "shin_R": (10, 0, 0), "foot_R": (6, 0, 0)},
    "roar": {"spine": (-6, 0, 0), "chest": (-10, 0, 0), "neck": (-8, 0, 0), "head": (-14, 0, 0),
             "upperarm_L": (-20, -35, 0), "forearm_L": (-40, 0, 0),
             "upperarm_R": (-30, 30, 0), "forearm_R": (-45, 0, 0), "hand_R": (10, 0, 0),
             "thigh_L": (-10, 0, 0), "shin_L": (12, 0, 0), "thigh_R": (6, 0, 0), "shin_R": (10, 0, 0)},
    "overhead": {"spine": (-8, 0, 0), "chest": (-10, 0, 0), "head": (-6, 0, 0),
                 "upperarm_L": (-150, -12, 0), "forearm_L": (-40, 0, 0),
                 "upperarm_R": (-160, 12, 0), "forearm_R": (-40, 0, 0), "hand_R": (-30, 0, 0),
                 "thigh_L": (-14, 0, 0), "shin_L": (14, 0, 0), "thigh_R": (8, 0, 0), "shin_R": (12, 0, 0)},
    "strike": {"spine": (18, 0, 0), "chest": (14, 0, 0), "head": (6, 0, 0),
               "upperarm_L": (-60, -10, 0), "forearm_L": (-20, 0, 0),
               "upperarm_R": (-70, 8, 0), "forearm_R": (-10, 0, 0), "hand_R": (30, 0, 0),
               "thigh_L": (-38, 0, 0), "shin_L": (40, 0, 0), "foot_L": (-6, 0, 0),
               "thigh_R": (16, 0, 0), "shin_R": (22, 0, 0), "foot_R": (10, 0, 0)},
    "kneel": {"spine": (14, 0, 0), "chest": (10, 0, 0), "neck": (8, 0, 0), "head": (16, 0, 0),
              "upperarm_L": (-30, -6, 0), "forearm_L": (-50, 0, 0),
              "upperarm_R": (-40, 6, 0), "forearm_R": (-40, 0, 0), "hand_R": (40, 0, 0),
              "thigh_L": (-80, 0, 0), "shin_L": (82, 0, 0), "foot_L": (-2, 0, 0),
              "thigh_R": (10, 0, 0), "shin_R": (110, 0, 0), "foot_R": (40, 0, 0)},
}

# ------------------------------------------------------------------ god poses
POSES_G = {
    "rest": {},
    "stand": {"spine": (2, 0, 0), "chest": (2, 0, 0), "head": (6, 0, 0)},
    "tilt": {"spine": (2, 0, 0), "chest": (2, 0, 0), "neck": (4, 10, 0), "head": (8, 14, 4)},
}


def blend(a, b, t):
    out = {}
    for k in set(a) | set(b):
        ra, rb = a.get(k, (0, 0, 0)), b.get(k, (0, 0, 0))
        out[k] = tuple(x + (y - x) * t for x, y in zip(ra, rb))
    return out


def add(a, b, w=1.0):
    out = dict(a)
    for k, r in b.items():
        ra = out.get(k, (0, 0, 0))
        out[k] = tuple(x + y * w for x, y in zip(ra, r))
    return out


def key_pose(ch, frame, pose, root_loc=None, root_rot=None, joints=None):
    """Key every joint (unspecified -> 0) so poses never leak between keys."""
    names = joints or [j for j in ch.rig if j != "root"]
    for j in names:
        e = ch.rig[j]
        r = pose.get(j, (0, 0, 0))
        e.rotation_euler = Euler([math.radians(v) for v in r], "XYZ")
        e.keyframe_insert("rotation_euler", frame=frame)
    if root_loc is not None:
        ch.root.location = root_loc
        ch.root.keyframe_insert("location", frame=frame)
    if root_rot is not None:
        ch.root.rotation_euler = Euler([math.radians(v) for v in root_rot], "XYZ")
        ch.root.keyframe_insert("rotation_euler", frame=frame)


def play(ch, frames, fn):
    """fn(f) -> (pose, root_loc or None, root_rot or None). One key per frame, linear."""
    for f in frames:
        pose, loc, rot = fn(f)
        key_pose(ch, f, pose, loc, rot)
    for ob in list(ch.rig.values()):
        C.set_interp(ob, "LINEAR")


def keyed(track, f, ease=C.ease_in_out):
    """Evaluate a pose track [(frame, pose), ...] at frame f with eased blends between keys."""
    if f <= track[0][0]:
        return track[0][1]
    for (fa, pa), (fb, pb) in zip(track, track[1:]):
        if fa <= f <= fb:
            return blend(pa, pb, ease((f - fa) / max(1e-6, fb - fa)))
    return track[-1][1]


# ------------------------------------------------------------------ gait
def walk_pose(phase, who="warrior", heavy=1.0):
    """Gait at phase 0..1 (one full stride = two steps). Left heel strikes at 0, right at 0.5."""
    p = 2 * math.pi * phase
    s = math.sin(p)
    c = math.cos(p)
    if who == "god":
        a = 0.6
    else:
        a = 1.0
    hipL = -22 * a * c                       # thigh swing (left forward at phase 0)
    hipR = 22 * a * c
    # knee: bends in swing (when the leg moves forward) and slightly at contact
    kneeL = (10 + 32 * max(0.0, math.sin(p + math.pi * 0.95))) * a + 6
    kneeR = (10 + 32 * max(0.0, math.sin(p - math.pi * 0.05))) * a + 6
    footL = -8 * c * a
    footR = 8 * c * a
    bob = 3 * abs(s) * heavy
    pose = {
        "pelvis": (0, 0, 6 * c * a), "spine": (4 + bob * 0.3, 0, -4 * c * a), "chest": (2, 0, -6 * c * a),
        "head": (-2, 0, 4 * c * a),
        "thigh_L": (hipL, 0, 0), "shin_L": (kneeL, 0, 0), "foot_L": (footL, 0, 0),
        "thigh_R": (hipR, 0, 0), "shin_R": (kneeR, 0, 0), "foot_R": (footR, 0, 0),
        "upperarm_L": (14 * c * a - 4, -7, 0), "forearm_L": (-14 - 6 * max(0, -c), 0, 0),
        "upperarm_R": (-6 - 4 * c * a, 8, 0), "forearm_R": (-18, 0, 0), "hand_R": (35, 0, 0),
    }
    return pose


def walk_root(phase, start, heading_deg, stride, cycles_done):
    """Root position for a walk: advances `stride` metres per step (two per cycle), with a heavy bob."""
    h = math.radians(heading_deg)
    dist = (cycles_done + phase) * 2 * stride
    fwd = Vector((math.sin(h), -math.cos(h), 0.0))      # heading 0 faces -Y
    bob = -0.018 * abs(math.cos(2 * math.pi * phase)) ** 2
    return Vector(start) + fwd * dist + Vector((0, 0, bob))


# ================================================================== kinematics
from mathutils import Matrix, Quaternion  # noqa: E402


def _module_for(ch):
    import rb_god
    import rb_warrior
    return rb_warrior if ch.__class__.__name__ == "Warrior" else rb_god


def fk(ch, pose, root_loc=(0, 0, 0), root_rot=(0, 0, 0)):
    """Analytic forward kinematics -> {joint: (world_pos Vector, world_rot Matrix3)}."""
    mod = _module_for(ch)
    J, P = mod.J, mod.PARENT
    out = {"root": (Vector(root_loc), Euler([math.radians(v) for v in root_rot], "XYZ").to_matrix())}
    order = mod.ORDER
    for j in order:
        if j == "root":
            continue
        p = P[j]
        pp, pr = out[p]
        lr = Euler([math.radians(v) for v in pose.get(j, (0, 0, 0))], "XYZ").to_matrix()
        pos = pp + pr @ (Vector(J[j]) - Vector(J[p]))
        out[j] = (pos, pr @ lr)
    return out


def _frame(d, n):
    d = d.normalized()
    n = (n - d * n.dot(d)).normalized()
    return Matrix((d, n, d.cross(n))).transposed()


def _align(rest_dir, rest_bend, new_dir, new_bend):
    """World rotation taking (rest_dir, rest_bend-axis) onto (new_dir, new_bend-axis)."""
    return _frame(new_dir, new_bend) @ _frame(rest_dir, rest_bend).transposed()


def _to_local_deg(parent_rot, world_rot, prev=None):
    m = parent_rot.transposed() @ world_rot
    e = m.to_euler("XYZ", Euler([math.radians(v) for v in prev], "XYZ")) if prev else m.to_euler("XYZ")
    return tuple(math.degrees(v) for v in e)


def two_bone(ch, pose, chain, target, pole, root_loc=(0, 0, 0), root_rot=(0, 0, 0)):
    """Solve a two-bone chain (e.g. ('thigh_L','shin_L','foot_L') or ('upperarm_R','forearm_R','hand_R'))
    so the end joint reaches `target`, bending toward `pole` (world direction). Returns an updated pose."""
    mod = _module_for(ch)
    J, P = mod.J, mod.PARENT
    a, b, c = chain
    W = fk(ch, pose, root_loc, root_rot)
    pa, _ = W[a]
    parent_rot = W[P[a]][1]
    L1 = (Vector(J[b]) - Vector(J[a])).length
    L2 = (Vector(J[c]) - Vector(J[b])).length
    d = Vector(target) - pa
    dist = max(abs(L1 - L2) + 1e-3, min(L1 + L2 - 1e-4, d.length))
    dn = d.normalized()
    pole = Vector(pole)
    pp = (pole - dn * pole.dot(dn))
    if pp.length < 1e-6:
        pp = Vector((0, -1, 0)) - dn * dn.y * -1
    pp.normalize()
    cos_a = (L1 * L1 + dist * dist - L2 * L2) / (2 * L1 * dist)
    ang = math.acos(max(-1.0, min(1.0, cos_a)))
    mid = pa + dn * (L1 * math.cos(ang)) + pp * (L1 * math.sin(ang))
    end = pa + dn * dist
    bend = dn.cross(pp)
    # rest bend axis: the plane in which the joint bulges at rest (knees forward, elbows back)
    rest_d1 = Vector(J[b]) - Vector(J[a])
    rest_d2 = Vector(J[c]) - Vector(J[b])
    rest_pole = Vector((0, -1, 0)) if a.startswith("thigh") else Vector((0, 1, 0))
    rest_bend1 = rest_d1.normalized().cross((rest_pole - rest_d1.normalized() * rest_pole.dot(rest_d1.normalized())).normalized())
    rest_bend2 = rest_d2.normalized().cross((rest_pole - rest_d2.normalized() * rest_pole.dot(rest_d2.normalized())).normalized())
    Ra = _align(rest_d1, rest_bend1, mid - pa, bend)
    Rb = _align(rest_d2, rest_bend2, end - mid, bend)
    new = dict(pose)
    new[a] = _to_local_deg(parent_rot, Ra, pose.get(a))
    new[b] = _to_local_deg(Ra, Rb, pose.get(b))
    return new


# rest grip frame of the right fist (from rb_warrior._grip_sword), in hand-local = world-at-rest axes
def _rest_grip():
    import rb_warrior as RW
    hand = Vector(RW.J["hand_R"])
    kn = Vector(RW.J["fingers_R"])
    hd = (kn - hand).normalized()
    z = Vector((0.0, -1.0, -0.15)).normalized()
    x = hd.cross(z).normalized()
    y = z.cross(x)
    center = hand + hd * 0.075 + Vector((0.022, 0, 0))
    return Matrix((x, y, z)).transposed(), center - hand


GRIP_ROT, GRIP_OFF = None, None


def aim_hand(ch, pose, side, blade_dir, edge_up=(0, 0, 1), root_loc=(0, 0, 0), root_rot=(0, 0, 0)):
    """Rotate hand_<side> so the fist's grip axis (= the sword's +Z) points along blade_dir,
    with the sword's local +X (flat face normal) as close as possible to `edge_up` x blade_dir."""
    global GRIP_ROT, GRIP_OFF
    if GRIP_ROT is None:
        GRIP_ROT, GRIP_OFF = _rest_grip()
    W = fk(ch, pose, root_loc, root_rot)
    parent_rot = W["forearm_" + side][1]
    z = Vector(blade_dir).normalized()
    up = Vector(edge_up)
    x = up.cross(z)
    if x.length < 1e-4:
        x = Vector((1, 0, 0)).cross(z)
    x.normalize()
    y = z.cross(x)
    want = Matrix((x, y, z)).transposed()          # desired sword axes in world
    hand_world = want @ GRIP_ROT.transposed()      # hand rotation that carries the rest grip onto `want`
    new = dict(pose)
    new["hand_" + side] = _to_local_deg(parent_rot, hand_world, pose.get("hand_" + side))
    return new


def sword_pose(ch, pose, grip_pos, blade_dir, edge_up=(0, 0, 1), elbow_pole=(-0.6, 0.4, -0.6), two_hands=True,
               left_pole=(0.6, 0.4, -0.6), root_loc=(0, 0, 0), root_rot=(0, 0, 0), left_slide=0.13):
    """Place the right fist's grip centre at grip_pos (world) with the blade along blade_dir; optionally
    bring the left fist onto the grip `left_slide` metres further toward the pommel."""
    global GRIP_ROT, GRIP_OFF
    if GRIP_ROT is None:
        GRIP_ROT, GRIP_OFF = _rest_grip()
    z = Vector(blade_dir).normalized()
    # wrist target = grip centre minus the (rotated) palm offset; iterate twice (hand rotation changes it)
    p = dict(pose)
    for _ in range(3):
        p = aim_hand(ch, p, "R", z, edge_up, root_loc, root_rot)
        W = fk(ch, p, root_loc, root_rot)
        hand_rot = W["hand_R"][1]
        wrist = Vector(grip_pos) - hand_rot @ GRIP_OFF
        p = two_bone(ch, p, ("upperarm_R", "forearm_R", "hand_R"), wrist, Vector(elbow_pole), root_loc, root_rot)
    if two_hands:
        lg = Vector(grip_pos) - z * left_slide
        for _ in range(3):
            p = aim_hand(ch, p, "L", z, edge_up, root_loc, root_rot)
            W = fk(ch, p, root_loc, root_rot)
            off = Vector((-GRIP_OFF.x, GRIP_OFF.y, GRIP_OFF.z))   # mirrored palm offset for the left fist
            wrist = lg - W["hand_L"][1] @ off
            p = two_bone(ch, p, ("upperarm_L", "forearm_L", "hand_L"), wrist, Vector(left_pole), root_loc, root_rot)
    return p


def heading_vec(deg):
    h = math.radians(deg)
    return Vector((math.sin(h), -math.cos(h), 0.0))


def foot_pose(ch, pose, side, ankle_target, heading_deg, pitch_deg=0.0, root_loc=(0, 0, 0), root_rot=(0, 0, 0)):
    """Leg IK to put the ankle at ankle_target, knee toward the heading; foot sole level (+pitch)."""
    fwd = heading_vec(heading_deg)
    p = two_bone(ch, pose, ("thigh_" + side, "shin_" + side, "foot_" + side), ankle_target, fwd, root_loc, root_rot)
    W = fk(ch, p, root_loc, root_rot)
    want = Euler((math.radians(pitch_deg), 0, math.radians(heading_deg)), "XYZ").to_matrix() if False else \
        (Matrix.Rotation(math.radians(heading_deg), 3, "Z") @ Matrix.Rotation(math.radians(pitch_deg), 3, "X"))
    p["foot_" + side] = _to_local_deg(W["shin_" + side][1], want, p.get("foot_" + side))
    return p


# ================================================================== walking with planted feet
def walk_plan(start, heading_deg, f0, f1, step_frames, stride, first="L", foot_w=0.115, lift=0.085,
              stop_frame=None, lead=0.2):
    """Plan a heavy walk along a straight line starting from a standstill at f0.
    Returns at(f) -> (pelvis_root_loc, {side: (ankle_pos, pitch_deg)}), plus the plant list.
    Feet are planted (no sliding): stance = fixed foothold, swing = eased arc to the next one.
    One foot lands every `step_frames` (put that on the beat); each step advances `stride` metres."""
    h = math.radians(heading_deg)
    fwd = Vector((math.sin(h), -math.cos(h), 0.0))
    left = Vector((math.cos(h), math.sin(h), 0.0))
    start = Vector(start)
    swing = 0.82 * step_frames
    ankle_h = 0.092
    other = "R" if first == "L" else "L"
    plants = {first: [(start + left * (foot_w if first == "L" else -foot_w) + Vector((0, 0, ankle_h)), -1e9)],
              other: [(start + left * (foot_w if other == "L" else -foot_w) + Vector((0, 0, ankle_h)), -1e9)]}
    k = 1
    while f0 + (k - 1) * step_frames <= f1 + step_frames:
        side = first if k % 2 == 1 else other
        lat = foot_w if side == "L" else -foot_w
        land = f0 + (k - 1) * step_frames + swing
        pos = start + fwd * ((k + lead) * stride) + left * lat + Vector((0, 0, ankle_h))
        if stop_frame is not None and land - swing > stop_frame:
            break
        plants[side].append((pos, land))
        k += 1

    def pelvis_dist(fe):
        prog = (fe - f0) / step_frames
        if prog <= 0:
            return 0.0
        # ease in over the first step
        return (prog - 0.5 * (1 - C.smooth(min(1.0, prog)))) * stride if prog < 1 else (prog - 0.0) * stride

    def at(f):
        fe = f if stop_frame is None else min(f, stop_frame)
        prog = (fe - f0) / step_frames
        bob = -0.018 * (0.5 + 0.5 * math.cos(2 * math.pi * prog)) if prog > 0 else 0.0
        root = start + fwd * pelvis_dist(fe) + Vector((0, 0, bob))
        feet = {}
        for side in ("L", "R"):
            mine = plants[side]
            i = max(i for i in range(len(mine)) if mine[i][1] <= f or i == 0)
            cur = mine[i]
            nxt = mine[i + 1] if i + 1 < len(mine) else None
            if nxt is not None and nxt[1] - swing <= f < nxt[1]:
                u = (f - (nxt[1] - swing)) / swing
                pos = cur[0].lerp(nxt[0], C.ease_in_out(u)) + Vector((0, 0, lift * math.sin(math.pi * u) ** 1.2))
                pitch = 16 * math.sin(math.pi * min(1.0, u * 2)) * (1 - u) - 14 * math.sin(math.pi * u) * u
                feet[side] = (pos, pitch)
            else:
                pitch = 0.0
                if nxt is not None:
                    before = (nxt[1] - swing) - f
                    if 0 <= before < step_frames * 0.3:
                        pitch = 14 * (1 - before / (step_frames * 0.3))
                feet[side] = (cur[0], pitch)
        return root, feet

    return at, plants


def solve_walk(ch, upper_pose, root, heading_deg, feet, hip_drop=0.0):
    """Full pose for a walk frame: upper body from `upper_pose`, legs by IK to the planned feet."""
    root_rot = (0, 0, heading_deg)
    loc = Vector(root) + Vector((0, 0, -hip_drop))
    p = dict(upper_pose)
    for side in ("L", "R"):
        pos, pitch = feet[side]
        p = foot_pose(ch, p, side, pos, heading_deg, pitch, loc, root_rot)
    return p, loc, root_rot


# ================================================================== Fallen God: blade-driven arms
def god_blade_matrix(pivot_loc, pivot_rot_deg):
    """World matrix of the god's blade for a blade_pivot location/rotation (rest: point-down)."""
    R = Euler([math.radians(v) for v in pivot_rot_deg], "XYZ").to_matrix().to_4x4()
    M = Matrix.Translation(Vector(pivot_loc)) @ R @ Matrix.Rotation(math.pi, 4, "X")
    return M


def god_grip_pose(g, pose, pivot_loc, pivot_rot_deg, root_loc=(0, 0, 0), root_rot=(0, 0, 0),
                  right_s=0.14, left_s=0.42, poles=((-0.8, 0.5, -0.4), (0.8, 0.5, -0.4)), one_hand=None):
    """IK the god's fists onto the obsidian grip (grip runs 0..1 m from the guard along blade -Z).
    pivot_* are WORLD values of g.blade_pivot. one_hand='R'|'L' frees the other arm."""
    M = god_blade_matrix(pivot_loc, pivot_rot_deg)
    p = dict(pose)
    for side, s, pole in (("R", right_s, poles[0]), ("L", left_s, poles[1])):
        if one_hand and side != one_hand:
            continue
        grip = M @ Vector((0, 0, -s))
        W = fk(g, p, root_loc, root_rot)
        sh = W["upperarm_" + side][0]
        wrist = grip + (sh - grip).normalized() * 0.16
        p = two_bone(g, p, ("upperarm_" + side, "forearm_" + side, "hand_" + side), wrist, Vector(pole), root_loc, root_rot)
    return p


def key_god_blade(g, frame, pivot_loc, pivot_rot_deg):
    g.blade_pivot.location = pivot_loc
    g.blade_pivot.rotation_euler = Euler([math.radians(v) for v in pivot_rot_deg], "XYZ")
    g.blade_pivot.keyframe_insert("location", frame=frame)
    g.blade_pivot.keyframe_insert("rotation_euler", frame=frame)
