"""Camera grammar for shot scripts. Every move is a pure function of the frame
and is keyed per frame (linear between per-frame keys, so motion blur is right).

    cam = rb_cam.Rig(lens=35, fstop=4.0)
    cam.key_range(shot.frames_all, lambda f: dict(loc=..., target=..., lens=..., focus=...))
    cam.handheld(amp=0.004, freq=1.3, seed=shot.seed)   # optional, applied inside key_range
Composition is checked against the 9:16 safe zones by eye in the stills.
"""
import math

import bpy
from mathutils import Euler, Vector

import rb_core as C


class Rig:
    def __init__(self, lens=35, fstop=None, name="Cam", clip_end=600.0):
        self.cam = C.camera(name, lens=lens, fstop=fstop, focus=None, clip_end=clip_end)
        self.cam.rotation_mode = "XYZ"
        self.hh = None
        self.shakes = []           # (frame, amplitude_m, seed)
        self.whips = []            # (f_start, f_end, yaw_deg)

    # ----------------------------------------------------------- modifiers
    def handheld(self, amp=0.006, rot_deg=0.35, freq=1.1, seed=1):
        """Low-frequency 'heavy handheld' drift (position metres, rotation degrees)."""
        self.hh = (amp, rot_deg, freq, seed)

    def shake(self, frame, amp=0.03, seed=7):
        """Impact shake decaying to zero over 6 frames, starting at `frame`."""
        self.shakes.append((frame, amp, seed))

    def whip(self, f0, f1, yaw_deg):
        """Fast eased yaw (with motion blur) between f0 and f1 — whip pans between scenes."""
        self.whips.append((f0, f1, yaw_deg))

    # ----------------------------------------------------------- keying
    def key_range(self, frames, fn):
        """fn(f) -> dict(loc, target | rot, lens=None, focus=None (Vector/obj/float), fstop=None, roll=0)."""
        cd = self.cam.data
        for f in frames:
            s = fn(f)
            loc = Vector(s["loc"])
            if "target" in s:
                rot = C.look_at_euler(loc, s["target"], math.radians(s.get("roll", 0.0)))
            else:
                rot = Euler(s["rot"], "XYZ")
            if self.hh:
                amp, rdeg, freq, seed = self.hh
                t = f / C.FPS * freq
                loc = loc + Vector((C.noise1(t, seed), C.noise1(t, seed + 1), C.noise1(t, seed + 2))) * amp
                rot = Euler((rot.x + math.radians(rdeg) * C.noise1(t * 1.3, seed + 3),
                             rot.y + math.radians(rdeg) * 0.5 * C.noise1(t * 1.1, seed + 4),
                             rot.z + math.radians(rdeg) * C.noise1(t * 1.2, seed + 5)), "XYZ")
            for fr, amp, seed in self.shakes:
                d = C.decay_shake(f, fr, amp, seed)
                loc = loc + d
                rot = Euler((rot.x + d.z * 0.6, rot.y + d.x * 0.3, rot.z + d.y * 0.6), "XYZ")
            for f0, f1, yaw in self.whips:
                if f >= f0:
                    u = C.ease_in_out(C.remap(f, f0, f1))
                    rot = Euler((rot.x, rot.y, rot.z + math.radians(yaw) * u), "XYZ")
            self.cam.location = loc
            self.cam.rotation_euler = rot
            self.cam.keyframe_insert("location", frame=f)
            self.cam.keyframe_insert("rotation_euler", frame=f)
            if s.get("lens"):
                cd.lens = s["lens"]
                cd.keyframe_insert("lens", frame=f)
            foc = s.get("focus")
            if foc is not None:
                cd.dof.use_dof = True
                if isinstance(foc, bpy.types.Object):
                    foc = foc.matrix_world.translation
                if hasattr(foc, "__len__"):
                    foc = (Vector(foc) - loc).length
                cd.dof.focus_distance = max(0.05, float(foc))
                cd.dof.keyframe_insert("focus_distance", frame=f)
            if s.get("fstop"):
                cd.dof.use_dof = True
                cd.dof.aperture_fstop = s["fstop"]
                cd.dof.keyframe_insert("aperture_fstop", frame=f)
        C.set_interp(self.cam, "LINEAR")
        if cd.animation_data and cd.animation_data.action:
            for fc in cd.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "LINEAR"


# ----------------------------------------------------------- path helpers
def along(points, u, ease=C.ease_in_out):
    """Position along a polyline of control points at eased progress u (0..1), Catmull-Rom smoothed."""
    u = ease(C.clamp01(u))
    pts = [Vector(p) for p in points]
    if len(pts) == 2:
        return pts[0].lerp(pts[1], u)
    n = len(pts) - 1
    x = u * n
    i = min(int(x), n - 1)
    t = x - i
    p0 = pts[max(0, i - 1)]
    p1, p2 = pts[i], pts[i + 1]
    p3 = pts[min(n, i + 2)]
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


def orbit(center, radius, height, ang_deg):
    a = math.radians(ang_deg)
    c = Vector(center)
    return Vector((c.x + radius * math.sin(a), c.y - radius * math.cos(a), c.z + height))


def world_pos(ob, local=(0, 0, 0)):
    bpy.context.view_layer.update()
    return ob.matrix_world @ Vector(local)
