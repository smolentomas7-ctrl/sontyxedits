"""Shot harness used by every scenes/<SHOT>.py script.

    import rb_shot
    shot = rb_shot.Shot("O2")          # reads edit/timeline.json + CLI args
    ... build environment / characters / camera, key every frame via shot.frames_all ...
    shot.render()

CLI (after `--`):
  --mode still|preview|final   still = one key frame (default), preview = 50% res, final = 100%
  --frame N                    still frame (video frame number); default = shot.key_frame
  --scale S --samples N        override resolution scale / TAA samples
  --out DIR                    override output directory

Frame numbering: scene frame == video frame. A shot covers [start_frame, end_frame)
plus HANDLE_FRAMES on each side. Cloth / particle sims start PREROLL frames before
the first rendered frame so they are settled.
"""
import math
import os
import sys

import bpy

import rb_core as C

HANDLES = C.video.HANDLE_FRAMES
PREROLL = 30


class Shot:
    def __init__(self, sid, key_frame=None, scale=None, samples=None, motion_blur=True, volumetrics=True, **render_kw):
        import json
        self.id = sid
        self.args = C.script_args()
        tl = json.load(open(os.path.join(C.ROOT, "edit", "timeline.json")))
        rec = {s["id"]: s for s in tl["shots"]}[sid]
        self.rec = rec
        self.f0, self.f1 = rec["start_frame"], rec["end_frame"]
        self.mode = self.args.get("mode", "still")
        self.render_start = self.f0 - HANDLES
        self.render_end = self.f1 + HANDLES          # exclusive
        self.sim_start = self.render_start - PREROLL
        self.key_frame = int(self.args.get("frame", key_frame if key_frame is not None else (self.f0 + self.f1) // 2))
        if scale is None:
            scale = {"still": 0.5, "preview": 0.5, "final": 1.0}[self.mode]
        if samples is None:
            samples = {"still": 16, "preview": 8, "final": 12}[self.mode]
        scale = float(self.args.get("scale", scale))
        samples = int(self.args.get("samples", samples))
        self.scale = scale
        self.rng = C.rng(sid)
        self.seed = C.video.seed_for(sid)
        C.reset_scene()
        sc = C.setup_render(scale=scale, samples=samples, motion_blur=motion_blur, volumetrics=volumetrics, **render_kw)
        sc.frame_start = self.sim_start
        sc.frame_end = self.render_end
        self.scene = sc
        default_out = os.path.join(C.ROOT, "build", "stills" if self.mode == "still" else "shots", sid
                                   if self.mode == "still" else os.path.join(sid, self.mode))
        self.out = self.args.get("out", default_out)
        if not os.path.isabs(self.out):
            self.out = os.path.join(C.ROOT, self.out)
        self.cloths = []

    # ---------------------------------------------------------------- time
    @property
    def frames_all(self):
        """Every frame that must be keyed: sim preroll through the last handle."""
        return range(self.sim_start, self.render_end)

    @property
    def frames_render(self):
        return range(self.render_start, self.render_end)

    def t(self, f):
        """Seconds since the shot's first (cut) frame; negative inside the head handle/preroll."""
        return (f - self.f0) / C.FPS

    def u(self, f):
        """Normalised shot progress: 0 at the cut-in frame, 1 at the cut-out frame (can exceed in handles)."""
        return (f - self.f0) / max(1, (self.f1 - self.f0))

    @staticmethod
    def video_frame_of_beat(b):
        import json
        tm = json.load(open(os.path.join(C.ROOT, "config", "timing.json")))
        t = tm["song_grid_t0"] + b * tm["beat_sec"] - tm["song_offset"]
        return t * C.FPS

    # ---------------------------------------------------------------- sims
    def register_cloth(self, cloth_mods, time_scale=1.0):
        for cl in cloth_mods:
            cl.point_cache.frame_start = self.sim_start
            cl.point_cache.frame_end = self.render_end
            cl.settings.time_scale = time_scale
            self.cloths.append(cl)

    # ---------------------------------------------------------------- render
    def _step_to(self, f):
        sc = self.scene
        if self.cloths or self.args.get("sequential"):
            for k in range(self.sim_start, f):
                sc.frame_set(k)
        sc.frame_set(f)

    def _apply_overrides(self):
        """CLI render-quality overrides applied after the scene is built (sets may tune EEVEE themselves):
        --vol_tile 4|8|16 --vol_samples N --shadow_cube 512.. --shadow_cascade 1024.. --soft_shadows 0|1
        --gtao 0|1 --ssr 0|1 --motion_blur 0|1."""
        e, a = self.scene.eevee, self.args
        if "vol_tile" in a:
            e.volumetric_tile_size = str(a["vol_tile"])
        if "vol_samples" in a:
            e.volumetric_samples = int(a["vol_samples"])
        if "shadow_cube" in a:
            e.shadow_cube_size = str(a["shadow_cube"])
        if "shadow_cascade" in a:
            e.shadow_cascade_size = str(a["shadow_cascade"])
        for k, attr in (("soft_shadows", "use_soft_shadows"), ("gtao", "use_gtao"), ("ssr", "use_ssr")):
            if k in a:
                setattr(e, attr, str(a[k]) == "1")
        if "motion_blur" in a:
            self.scene.render.use_motion_blur = str(a["motion_blur"]) == "1"

    def render(self, frames=None):
        sc = self.scene
        self._apply_overrides()
        os.makedirs(self.out, exist_ok=True)
        if self.mode == "still":
            frames = [self.key_frame] if frames is None else list(frames)
            first = True
            for f in frames:
                if first:
                    self._step_to(f)
                    first = False
                else:
                    sc.frame_set(f)
                sc.render.filepath = os.path.join(self.out, "%s_f%04d.png" % (self.id, f))
                bpy.ops.render.render(write_still=True)
                print("WROTE", sc.render.filepath)
            return
        frames = list(self.frames_render) if frames is None else list(frames)
        a = self.args.get("range")
        if a:  # --range A B (render a sub-range, for parallel workers)
            lo, hi = int(a[0]), int(a[1])
            frames = [f for f in frames if lo <= f < hi]
        self._step_to(frames[0])
        for f in frames:
            path = os.path.join(self.out, "f_%04d.png" % f)
            sc.frame_set(f)
            if os.path.exists(path) and not self.args.get("force"):
                continue
            sc.render.filepath = path
            bpy.ops.render.render(write_still=True)
        print("DONE", self.id, len(frames), "frames ->", self.out)


def lens_preset(name):
    return C.video.LENSES[name]
