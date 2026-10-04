"""Shared staging for the Act IV montage shots (M1xx-M5xx): beat-locked walks on uneven ground,
idle stands and one-off actions for either warrior look. Everything is a pure function of the frame.

    import rb_montage as MT
    MT.walk(w, shot, mark=(x, y, z), heading=180, ground=forest.ground_z)   # passes `mark` at shot.key_frame
    MT.stand(w, shot, pos, heading)
    MT.act(w, shot, "slash", f_peak, dur, pos, heading)
"""
import math

from mathutils import Vector

import rb_core as C
import rb_intro
import rb_mat as M
import rb_motion as MO
import rb_story as ST

# short-sword / greatsword low carry (char-local, facing -Y): grip beside the right thigh, tip forward-down
CARRY = {"early": (Vector((-0.27, -0.07, 0.86)), Vector((-0.08, -0.55, -0.83))),
         "late": (Vector((-0.26, -0.10, 0.92)), Vector((-0.10, -0.62, -0.78)))}


def _ctrl(w, f, crack=None, eyes=None):
    if w.look == "early":
        return
    rb_intro._key_blade(w, f, 0.0 if crack is None else crack(f) if callable(crack) else crack)
    M.key_ctrl(w.mats["eyes"], "eye_glow", f, 28.0 if eyes is None else eyes)


def _finish(w):
    for ob in w.rig.values():
        C.set_interp(ob, "LINEAR")


def walk(w, shot, mark, heading, key_frame=None, stride=0.64, ground=None, carry=True, lean=0.0, crack=None,
         first_beat=None):
    """Heavy walk, one footfall per song beat, passing `mark` (feet) at key_frame (default shot.key_frame).
    ground(x, y) -> z keeps the planted feet on uneven terrain."""
    kf = shot.key_frame if key_frame is None else key_frame
    step = ST.STEP
    swing = 0.82 * step
    b0 = math.floor((shot.sim_start - 2 * step - ST.bf(0)) / step)
    if first_beat is not None:
        b0 = first_beat
    f0 = ST.bf(b0) - swing
    fwd = MO.heading_vec(heading)
    mark = Vector(mark)
    mz = mark.z
    start = Vector((mark.x, mark.y, 0.0)) - fwd * ((kf - f0) / step * stride)
    at, _ = MO.walk_plan(start, heading, f0, shot.render_end + 2 * step, step, stride)
    gz = (lambda x, y: mz) if ground is None else ground
    grip, blade = CARRY[w.look]
    for f in shot.frames_all:
        root, feet = at(f)
        phase = ((f - (f0 + swing)) / (2 * step)) % 1.0
        feet = {s: (Vector((p.x, p.y, p.z + gz(p.x, p.y))), pitch) for s, (p, pitch) in feet.items()}
        root = Vector((root.x, root.y, root.z + gz(root.x, root.y)))
        up = MO.blend(MO.POSES_W["stand"], MO.walk_pose(phase), 0.6)
        up = {k: v for k, v in up.items() if not k.startswith(("thigh", "shin", "foot", "toe"))}
        if lean:
            up = MO.add(up, {"spine": (lean, 0, 0), "chest": (lean * 0.6, 0, 0)})
        if carry:
            sway = 0.05 * math.sin(2 * math.pi * phase)
            g = grip + Vector((0, -sway, 0.015 * math.cos(4 * math.pi * phase)))
            up = MO.sword_pose(w, up, ST.wl(g, root, heading), ST.wd(blade, heading), two_hands=False,
                               root_loc=root, root_rot=(0, 0, heading))
        p, loc, rot = MO.solve_walk(w, up, root, heading, feet)
        MO.key_pose(w, f, p, loc, rot)
        _ctrl(w, f, crack)
    _finish(w)
    return at


def stand(w, shot, pos, heading, ground=None, look_up=0.0, crack=None, grip=None, blade=None, two=False,
          breath=1.0, stance=0.2):
    """Idle stand with breathing; sword low (or at grip/blade, char-local). Feet planted on the ground."""
    pos = Vector(pos)
    gz = (lambda x, y: pos.z) if ground is None else ground
    cg, cb = CARRY[w.look]
    grip = cg if grip is None else Vector(grip)
    blade = cb if blade is None else Vector(blade)
    for f in shot.frames_all:
        br = math.sin(f / C.FPS * 2 * math.pi / 3.4)
        body = {"spine": (1.0 * breath * br, 0, 0), "chest": (-2 + 1.4 * breath * br, 0, 0),
                "neck": (-look_up * 0.4, 0, 0), "head": (-look_up * 0.6, 0, 0)}
        base = MO.add(MO.POSES_W["stand"], body)
        base = {k: v for k, v in base.items() if not k.startswith(("thigh", "shin", "foot", "toe"))}
        fl = ST.wl(Vector((0.13, -0.5 * stance, 0.092)), pos, heading)
        fr = ST.wl(Vector((-0.14, 0.5 * stance, 0.092)), pos, heading)
        feet = {"L": (Vector((fl.x, fl.y, gz(fl.x, fl.y) + 0.092)), 0.0),
                "R": (Vector((fr.x, fr.y, gz(fr.x, fr.y) + 0.092)), 0.0)}
        root = Vector((pos.x, pos.y, 0.5 * (feet["L"][0].z + feet["R"][0].z) - 0.092 + 0.004 * breath * br))
        p = MO.sword_pose(w, base, ST.wl(grip, root, heading), ST.wd(blade, heading), two_hands=two,
                          root_loc=root, root_rot=(0, 0, heading))
        pose, loc, rot = MO.solve_walk(w, p, root, heading, feet, hip_drop=0.02)
        MO.key_pose(w, f, pose, loc, rot)
        _ctrl(w, f, crack)
    _finish(w)


def act(w, shot, action, f_peak, dur, pos, heading, slowmo=1.0, crack=None, then=None):
    """One rb_actions move whose impact lands on f_peak (frames before/after hold the start/end pose)."""
    import rb_actions as RA
    for f in shot.frames_all:
        pose, loc, rot = RA.perform(w, f, action, f_peak, dur, pos, heading, slowmo=slowmo)
        MO.key_pose(w, f, pose, loc, rot)
        _ctrl(w, f, crack)
    _finish(w)


def ground_mark(forest, xy):
    """(x, y) -> (x, y, ground z) on a forest set."""
    return Vector((xy[0], xy[1], forest.ground_z(xy[0], xy[1])))
