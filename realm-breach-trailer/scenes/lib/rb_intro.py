"""Scene builder shared by the Act I-III shots (Floor 999 arena + both characters
performing rb_story's intro timeline). Shot scripts only add the camera, light
rig choice and any shot-specific VFX.
"""
import math

import bpy
from mathutils import Euler, Vector

import rb_core as C
import rb_mat as M
import rb_motion as MO
import rb_story as ST


def build(shot, variant="approach", warrior=True, god=True, cape=True, arena_kw=None, act="intro", cloth_goal=None):
    import rb_env_arena as AR
    out = {}
    out["arena"] = AR.build_arena(variant=variant, **(arena_kw or {}))
    if hasattr(AR, "tune_eevee"):
        AR.tune_eevee()
    if warrior:
        import rb_warrior as RW
        if cloth_goal is None:   # violent action (battle, the roar and the charge): soft goal + body-only colliders
            cloth_goal = 0.4 if act == "battle" or shot.id in ("O11a", "O11b", "O12") else 0.0
        w = RW.build_warrior("late", rings=True, cape=cape, cloth_goal=cloth_goal)
        out["w"] = w
        shot.register_cloth(getattr(w, "cloths", []))
    if god:
        import rb_god as RG
        g = RG.build_god()
        out["g"] = g
    out["act"] = act
    animate(shot, out)
    if act == "after" and god:
        out["g"].halo.hide_render = True
    return out


def animate(shot, out, frames=None):
    w, g = out.get("w"), out.get("g")
    frames = frames or shot.frames_all
    act = out.get("act", "intro")
    wfn = {"intro": ST.warrior_intro, "battle": ST.warrior_battle, "after": ST.warrior_after}[act]
    gfn = {"intro": ST.god_intro, "battle": ST.god_battle, "after": ST.god_after}[act]
    cfn = {"intro": ST.intro_ctrl, "battle": ST.battle_ctrl, "after": ST.after_ctrl}[act]
    for f in frames:
        ctrl = cfn(f)
        if w is not None:
            pose, loc, rot = wfn(w, f)
            MO.key_pose(w, f, pose, loc, rot)
            _key_blade(w, f, ctrl["crack_glow"])
            M.key_ctrl(w.mats["eyes"], "eye_glow", f, ctrl["eye_glow"])
        if g is not None:
            pose, loc, rot, piv, prot = gfn(g, f)
            MO.key_pose(g, f, pose, loc, rot)
            MO.key_god_blade(g, f, piv, prot)
            g.halo_pivot.rotation_euler = Euler((0, math.radians(ctrl["halo_spin"]), 0), "XYZ")
            g.halo_pivot.keyframe_insert("rotation_euler", frame=f)
            M.key_ctrl(g.mats["stone"], "ignite", f, ctrl["god_ignite"])
            M.key_ctrl(g.mats["stone"], "glow", f, ctrl["god_glow"])
            M.key_ctrl(g.mats["eyes"], "eye_glow", f, ctrl["god_eyes"])
            hm = bpy.data.materials.get("god_halo")
            if hm is not None:
                M.key_ctrl(hm, "halo", f, ctrl["halo"])
    for ch in (w, g):
        if ch is None:
            continue
        for ob in ch.rig.values():
            C.set_interp(ob, "LINEAR")
    if g is not None:
        C.set_interp(g.blade_pivot, "LINEAR")
        C.set_interp(g.halo_pivot, "LINEAR")


def _key_blade(w, f, v):
    for m in w.sword.data.materials:
        if M.ctrl_node(m, "crack_glow") is not None:
            M.key_ctrl(m, "crack_glow", f, v)


def warrior_pos(f):
    """World position of the warrior's root at video frame f (for cameras)."""
    # the root only depends on the timeline, not on the rig objects
    if f < 700:
        root, _ = ST._walk_at(min(f, ST.bf(8) + 12))
        return Vector(root)
    if f < ST.bf(48) - 1:
        u = ST._seg(f, 700, ST.bf(48) - 1)
        uw = 0.5 * u + 0.5 * u * u
        return Vector((0.15, 2.0 + uw * (ST.CLASH.y - 0.55 - 2.0), 0.0))
    return Vector((0.15, ST.CLASH.y - 0.55, 0.0))


def warrior_pos_battle(f):
    s = ST.WARRIOR_V.at(f) if f < ST.bf(113.0) else None
    if s is not None:
        return Vector(s["root"])
    return Vector(ST._RISE)


def head_pos(f):
    return warrior_pos(f) + Vector((0, 0, 1.76))


def clear_view(cam_positions, target, reach=6.0, margin=0.3, prefixes=("ARENA_col", "ARENA_fallen", "ARENA_far")):
    """'Wild walls': hide (render) any arena pillar/fallen drum whose bounding box sits on the first `reach`
    metres of the camera's line of sight, or contains a camera position. Returns hidden object names."""
    import bpy
    tgt = Vector(target)
    hidden = []
    obs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(prefixes)]
    bpy.context.view_layer.update()
    for o in obs:
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        lo = Vector([min(v[i] for v in bb) - margin for i in range(3)])
        hi = Vector([max(v[i] for v in bb) + margin for i in range(3)])
        for cp in cam_positions:
            cp = Vector(cp)
            d = tgt - cp
            n = int(max(4, reach / 0.25))
            for k in range(n + 1):
                q = cp + d.normalized() * (reach * k / n)
                if all(lo[i] <= q[i] <= hi[i] for i in range(3)):
                    o.hide_render = True
                    hidden.append(o.name)
                    break
            if o.hide_render:
                break
    print("clear_view hid:", hidden)
    return hidden


def cam_samples(cam, shot, n=5):
    """World positions of the rig's camera at n frames across the rendered range."""
    import bpy
    sc = bpy.context.scene
    out = []
    fr = list(shot.frames_render)
    for k in range(n):
        f = fr[int(k * (len(fr) - 1) / max(1, n - 1))]
        sc.frame_set(f)
        out.append(cam.cam.matrix_world.translation.copy())
    return out


def cam_target_sample(cam, shot):
    """A point 12 m along the camera's view axis at the key frame (approximate aim target)."""
    import bpy
    bpy.context.scene.frame_set(shot.key_frame)
    m = cam.cam.matrix_world
    return m.translation + (m.to_3x3() @ Vector((0, 0, -1))) * 12.0
