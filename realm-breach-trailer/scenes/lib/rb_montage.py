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
CARRY["mid"] = CARRY["late"]          # mid look = late armour and greatsword


def _ctrl(w, f, crack=None, eyes=None):
    if w.look == "early":
        return
    # default: dark for the mid look; the late blade keeps M407's faint pre-ignition glow (never fully dead)
    dflt = 0.0 if w.look == "mid" else 0.3
    rb_intro._key_blade(w, f, dflt if crack is None else crack(f) if callable(crack) else crack)
    M.key_ctrl(w.mats["eyes"], "eye_glow", f, 28.0 if eyes is None else eyes)


def _finish(w):
    for ob in w.rig.values():
        C.set_interp(ob, "LINEAR")


def walk(w, shot, mark, heading, key_frame=None, stride=0.64, ground=None, carry=True, lean=0.0, crack=None,
         first_beat=None, stop_frame=None):
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
    at, _ = MO.walk_plan(start, heading, f0, shot.render_end + 2 * step, step, stride, stop_frame=stop_frame)
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
          breath=1.0, stance=0.2, extra=None):
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
        if extra:
            p.update(extra)
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


def cold_key(target, cam_loc, side=1.0, dist=2.6, energy=260.0, color=(0.62, 0.72, 0.9), size=2.4):
    """Soft moon-coloured key (area, no shadow) from the camera side so plate armour reads as metal
    (iron reflects only what lights it). side=+1 camera-left of the subject, -1 camera-right."""
    t, c = Vector(target), Vector(cam_loc)
    d = c - t
    d.z = 0
    d.normalize()
    sv = Vector((-d.y, d.x, 0.0)) * side
    loc = t + (d * 0.7 + sv * 0.7).normalized() * dist + Vector((0, 0, 1.0))
    return C.light("AREA", "MT_cold_key", tuple(loc), color=color, energy=energy, size=size,
                   target=tuple(t + Vector((0, 0, 0.3))), shadow=False, volume=0.15)


def ground_mark(forest, xy):
    """(x, y) -> (x, y, ground z) on a forest set."""
    return Vector((xy[0], xy[1], forest.ground_z(xy[0], xy[1])))


# ================================================================== dungeon montage scaffolding
def imp(b, lead=1.5):
    """Impact frame for song beat b: impacts land 1-2 frames before their beat."""
    return int(round(ST.bf(b) - lead))


def scene(shot, depth, look="mid", warrior=True, seed=None):
    """Dungeon set of the given depth + the warrior in `look` (cloth registered; battle cloth settings)."""
    import rb_env_dungeon as DG
    import rb_warrior as RW
    D = DG.build_dungeon(depth, seed=shot.seed if seed is None else seed)
    w = None
    if warrior:
        cape = look == "late"
        w = RW.build_warrior(look, rings=look == "late", cape=cape, cloth_goal=0.4 if cape else 0.0)
        shot.register_cloth(getattr(w, "cloths", []) or [])
    return D, w


def light(shot, depth, D, subject, cam_loc, follow=None):
    import rb_env_dungeon as DG
    shot.scene.frame_set(shot.key_frame)
    return DG.lights_dungeon(depth, D, subject=tuple(subject), cam=tuple(cam_loc), follow=follow)


def fx(name, *a, **k):
    """Call rb_vfx.<name> and never let a missing/failed effect kill the shot (logged)."""
    try:
        import rb_vfx as VFX
        return getattr(VFX, name)(*a, **k)
    except Exception as e:  # noqa: BLE001
        print("VFX FAIL", name, repr(e))
        return None


def enemy(kind, prefix=None, seed=0):
    import rb_enemies as EN
    return EN.build_enemy(kind, prefix=prefix, seed=seed)


def enemy_act(e, shot, action, f_peak, dur, loc, heading, slowmo=1.0):
    import rb_enemies as EN
    EN.perform_enemy(e, list(shot.frames_all), action, f_peak, dur, tuple(loc), heading, slowmo=slowmo)


def enemy_path(e, shot, fn):
    """Re-key the enemy root location along fn(f) -> (x, y, z) (on top of its keyed action)."""
    for f in shot.frames_all:
        e.root.location = tuple(fn(f))
        e.root.keyframe_insert("location", frame=f)
    C.set_interp(e.root, "LINEAR")


def act_pose(w, action, f, f_peak, dur, pos, heading, slowmo=1.0):
    """(pose, loc, rot) of an rb_actions move at frame f (for computing hand / tip positions)."""
    import rb_actions as RA
    return RA.perform(w, f, action, f_peak, dur, pos, heading, slowmo=slowmo)


def joint_world(w, pose_loc_rot, joint):
    pose, loc, rot = pose_loc_rot
    return MO.fk(w, pose, loc, rot)[joint][0]


def tip_empty(w, name="MT_tip"):
    """An empty at the sword tip (parented to the sword) for trails / lightning sources."""
    import bpy
    sw = w.sword
    zmax = max(v[2] for v in sw.bound_box)
    e = bpy.data.objects.new(name, None)
    C.link(e) if hasattr(C, "link") else bpy.context.scene.collection.objects.link(e)
    e.parent = sw
    e.location = (0.0, 0.0, zmax)
    return e


def world_at(obj, f):
    import bpy
    bpy.context.scene.frame_set(f)
    return obj.matrix_world.translation.copy()


def frame_fit(objs, lens, margin=1.35, axis=(0, -1, 0.15)):
    """Camera location framing the objects' world bbox (vertical frame) from direction `axis`."""
    import bpy
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    ctr = (lo + hi) / 2
    w = max(hi.x - lo.x, hi.y - lo.y)
    h = hi.z - lo.z
    sw, sh = C.video.SENSOR_HEIGHT_MM * C.video.WIDTH / C.video.HEIGHT, C.video.SENSOR_HEIGHT_MM
    d = max(w * lens / sw, h * lens / sh) * margin
    return ctr + Vector(axis).normalized() * d, ctr


def whip_in(f, f0, frames=4, yaw=55.0):
    """Yaw offset (deg) finishing an incoming whip pan: decelerates to 0 over `frames` after f0."""
    u = C.clamp01((f - f0) / float(frames))
    return yaw * (1 - C.ease_out(u))


def rot_target(loc, target, yaw_deg):
    from mathutils import Matrix
    d = Vector(target) - Vector(loc)
    return Vector(loc) + Matrix.Rotation(math.radians(yaw_deg), 3, "Z") @ d


def key_glow(obj, keys, name="glow"):
    """Key CTRL_<name> on every material of obj and its children: keys = [(frame, value), ...]."""
    obs = [obj] + list(getattr(obj, "children_recursive", []))
    mats = {m for o in obs if getattr(o, "data", None) is not None and hasattr(o.data, "materials")
            for m in o.data.materials if m is not None}
    for m in mats:
        if M.ctrl_node(m, name) is not None:
            for f, v in keys:
                M.key_ctrl(m, name, f, v)
