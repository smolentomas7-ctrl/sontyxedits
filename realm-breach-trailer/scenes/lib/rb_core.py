"""Core helpers shared by every Blender scene script.

Scene reset, render settings, cameras (vertical sensor fit + lens presets),
lights, easing curves, per-frame keyframing and seeded randomness.
Everything here is deterministic: a shot is a pure function of its ID and
frame number.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Euler, Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "config"))
import video  # noqa: E402,F401

FPS = video.FPS


# ---------------------------------------------------------------- arguments
def script_args():
    """Arguments after '--' on the blender command line, as a dict.
    --shot ID --frames A B --scale 0.5 --samples 8 --out DIR --still F"""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = {}
    i = 0
    while i < len(argv):
        k = argv[i].lstrip("-")
        vals = []
        i += 1
        while i < len(argv) and not argv[i].startswith("--"):
            vals.append(argv[i])
            i += 1
        out[k] = vals[0] if len(vals) == 1 else (vals if vals else True)
    return out


# ---------------------------------------------------------------- randomness
def rng(shot_id, salt=""):
    return random.Random(video.seed_for(shot_id + salt))


# ---------------------------------------------------------------- scene
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.render.fps = FPS
    return sc


def setup_render(scale=1.0, samples=8, motion_blur=True, volumetrics=True, vol_tile="8",
                 vol_samples=64, vol_end=120.0, bloom=0.08, gtao=True, ssr=True, look="AgX - Medium High Contrast",
                 exposure=0.0, soft_shadows=True, shadow_cube="1024", shadow_cascade="2048", transparent=False):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = int(video.WIDTH * scale)
    sc.render.resolution_y = int(video.HEIGHT * scale)
    sc.render.resolution_percentage = 100
    sc.render.fps = FPS
    sc.render.film_transparent = transparent
    sc.render.dither_intensity = 1.0
    e = sc.eevee
    e.taa_render_samples = samples
    e.use_bloom = bloom > 0
    e.bloom_intensity = bloom
    e.bloom_threshold = 1.0
    e.bloom_radius = 6.0
    e.bloom_knee = 0.5
    e.use_gtao = gtao
    e.gtao_distance = 0.6
    e.use_ssr = ssr
    e.use_ssr_refraction = False
    e.ssr_quality = 0.5
    e.ssr_thickness = 0.2
    e.use_soft_shadows = soft_shadows
    e.shadow_cube_size = shadow_cube
    e.shadow_cascade_size = shadow_cascade
    e.use_shadow_high_bitdepth = True
    e.light_threshold = 0.01
    e.volumetric_start = 0.1
    e.volumetric_end = vol_end
    e.volumetric_tile_size = vol_tile
    e.volumetric_samples = vol_samples
    e.volumetric_sample_distribution = 0.85
    e.use_volumetric_lights = volumetrics
    e.use_volumetric_shadows = volumetrics
    e.volumetric_light_clamp = 0.0
    e.use_motion_blur = False
    sc.render.use_motion_blur = motion_blur
    e.motion_blur_position = "CENTER"
    sc.render.motion_blur_shutter = 0.5
    e.motion_blur_steps = 1
    vs = sc.view_settings
    try:
        sc.display_settings.display_device = "sRGB"
        vs.view_transform = "AgX"
        vs.look = look
    except TypeError:
        vs.view_transform = "Filmic"
        vs.look = "Medium High Contrast"
    vs.exposure = exposure
    vs.gamma = 1.0
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.color_depth = "8"
    sc.render.image_settings.compression = 15
    return sc


def world(color=(0.0, 0.0, 0.0), strength=1.0, volume_density=0.0, volume_color=(0.5, 0.55, 0.6),
          anisotropy=0.3):
    sc = bpy.context.scene
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (*color, 1.0)
    bg.inputs["Strength"].default_value = strength
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    if volume_density > 0:
        pv = nt.nodes.new("ShaderNodeVolumePrincipled")
        pv.inputs["Density"].default_value = volume_density
        pv.inputs["Color"].default_value = (*volume_color, 1.0)
        pv.inputs["Anisotropy"].default_value = anisotropy
        nt.links.new(pv.outputs[0], out.inputs["Volume"])
    return w


def world_gradient(top=(0.32, 0.33, 0.35), bottom=(0.05, 0.05, 0.055), strength=1.0):
    """Studio-style vertical gradient world (for neutral turnarounds / reflections)."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new("WorldGrad")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.3
    mr.inputs["From Max"].default_value = 0.8
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*bottom, 1)
    ramp.color_ramp.elements[1].color = (*top, 1)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    return w


# ---------------------------------------------------------------- camera
def camera(name="Cam", lens=35, fstop=None, focus=None, clip_end=400.0):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = video.SENSOR_HEIGHT_MM
    cd.sensor_width = video.SENSOR_HEIGHT_MM * video.WIDTH / video.HEIGHT
    cd.clip_start = 0.02
    cd.clip_end = clip_end
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        cd.dof.aperture_blades = 7
        if isinstance(focus, bpy.types.Object):
            cd.dof.focus_object = focus
        elif focus is not None:
            cd.dof.focus_distance = focus
    ob = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    return ob


def look_at(ob, target, roll=0.0):
    d = Vector(target) - ob.location
    q = d.to_track_quat("-Z", "Y")
    ob.rotation_euler = q.to_euler()
    if roll:
        ob.rotation_euler.rotate_axis("Z", roll)


def look_at_euler(pos, target, roll=0.0):
    d = Vector(target) - Vector(pos)
    e = d.to_track_quat("-Z", "Y").to_euler()
    if roll:
        e.rotate_axis("Z", roll)
    return e


# ---------------------------------------------------------------- lights
def hexcol(h):
    return video.hex_linear(h)[:3]


def light(kind, name, loc, color=(1, 1, 1), energy=100.0, size=0.2, target=None, rot=None, shadow=True,
          spot_size=math.radians(45), blend=0.3, volume=1.0, specular=1.0):
    ld = bpy.data.lights.new(name, kind)
    ld.color = color if not isinstance(color, str) else hexcol(color)
    ld.energy = energy
    ld.use_shadow = shadow
    if kind in ("POINT", "SPOT"):
        ld.shadow_soft_size = size
    if kind == "AREA":
        ld.size = size
    if kind == "SUN":
        ld.angle = size
    if kind == "SPOT":
        ld.spot_size = spot_size
        ld.spot_blend = blend
    ld.volume_factor = volume
    ld.specular_factor = specular
    try:
        ld.use_contact_shadow = shadow
        ld.contact_shadow_distance = 0.1
    except AttributeError:
        pass
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if target is not None:
        look_at(ob, target)
    elif rot is not None:
        ob.rotation_euler = rot
    return ob


# ---------------------------------------------------------------- easing
def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def ease_in_out(x):
    x = clamp01(x)
    return 4 * x * x * x if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp01(x)
    return x * x * x


def ease_out_back(x, s=1.70158):
    x = clamp01(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def smooth(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def vlerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def remap(x, a, b):
    return clamp01((x - a) / (b - a)) if b != a else 0.0


def decay_shake(frame, start, amp, seed, frames=6, freq=0.9):
    """Seeded camera shake that decays to zero over `frames` frames (returns 3-vector)."""
    k = frame - start
    if k < 0 or k > frames:
        return Vector((0, 0, 0))
    r = random.Random(seed * 1000 + int(k))
    fall = (1 - k / frames) ** 2
    return Vector((r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-1, 1))) * amp * fall


def noise1(t, seed, octaves=3):
    """Smooth deterministic 1-D value noise in [-1, 1]."""
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for o in range(octaves):
        x = t * freq + seed * 17.13 + o * 31.7
        i = math.floor(x)
        f = x - i
        a = random.Random(int(i) * 7919 + seed * 104729 + o).uniform(-1, 1)
        b = random.Random(int(i + 1) * 7919 + seed * 104729 + o).uniform(-1, 1)
        u = f * f * (3 - 2 * f)
        total += amp * (a + (b - a) * u)
        norm += amp
        amp *= 0.5
        freq *= 2.0
    return total / norm


# ---------------------------------------------------------------- keyframes
def key_transform(ob, frame, loc=None, rot=None, scale=None, interp="LINEAR"):
    if loc is not None:
        ob.location = loc
        ob.keyframe_insert("location", frame=frame)
    if rot is not None:
        ob.rotation_euler = rot
        ob.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        ob.scale = scale if hasattr(scale, "__len__") else (scale, scale, scale)
        ob.keyframe_insert("scale", frame=frame)


def set_interp(ob, interp="LINEAR"):
    ad = ob.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = interp


def key_prop(idblock, path, frame, value):
    """Key a custom/RNA property (e.g. a material node input via path)."""
    exec("idblock.%s = value" % path) if "." in path or "[" in path else setattr(idblock, path, value)
    idblock.keyframe_insert(path, frame=frame)


def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def empty(name, loc=(0, 0, 0), parent=None, size=0.05):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_size = size
    ob.location = loc
    link(ob)
    if parent is not None:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    return ob


def parent_keep(child, parent):
    """Parent `child` to `parent` keeping the child's current world transform."""
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = mw


def output_path(out_dir, prefix=""):
    os.makedirs(out_dir, exist_ok=True)
    bpy.context.scene.render.filepath = os.path.join(out_dir, prefix)


def render_frames(frames, out_dir, prefix="f_", sequential_from=None):
    """Render the given frames to out_dir/prefix####.png. If `sequential_from` is set,
    step the scene through every frame from there first (cloth / particle caches)."""
    sc = bpy.context.scene
    os.makedirs(out_dir, exist_ok=True)
    frames = list(frames)
    if sequential_from is not None:
        for f in range(sequential_from, frames[0]):
            sc.frame_set(f)
    for f in frames:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(out_dir, "%s%04d.png" % (prefix, f))
        bpy.ops.render.render(write_still=True)
