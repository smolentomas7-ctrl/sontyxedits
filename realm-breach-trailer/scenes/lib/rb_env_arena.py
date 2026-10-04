"""THE FLOOR 999 ARENA — an endless void dimension (shots O2-O12, M510, F1-F7, E2).

A vast floor of wet, cracked dark stone slabs (ember-glowing cracks, puddles
that mirror the light via SSR), two loose colonnades of colossal fluted
pillars rising out of frame into darkness, fallen drums and rubble, layered
volumetric haze, a distant ember glow on the horizon behind the Fallen God and
a cold blue zone where he stands.

LOCKED LAYOUT (metres, Z up, characters face -Y)
------------------------------------------------
  floor top           z = 0. Real slab geometry in HERO = x[-34, 34] x y[-58, 46];
                      a procedural slab plane continues to +-FAR (150 m): no edge in any shot.
  approach axis       x = 0. The warrior walks from y = -40 toward +Y
                      (O2 walk around y = -16 .. -10, stops at WARRIOR_STOP = (0, -2, 0)).
  Fallen God          GOD_POS = (0, 14, 0), facing -Y (rb_god.build_god(); move g.root there).
  clash point         CLASH = (0, 9, 0); warrior duels around y = 7.5 .. 9.5.
  colonnades          pillars at x = +-NAVE_X (6.5 m, jittered) every 9 m from y = -54 to +54
                      (radius ~1.8 m, 70-95 m tall or broken off at 3-18 m); clear nave ~9 m wide.
                      Pillars standing on the axis at y = 9 / 18 are kept intact so the duel
                      is framed; broken ones get rubble piles.
  scattered pillars   |x| 15..85 m, y -80..100 m, receding into the fog.
  fallen pillars      left aisle  (-15..-8, -30..-22) and right court (+9..+17, +20..+27).
  impact crater       IMPACT = (1.3, 10.8): smashed slabs + rubble ('duel' and 'after').
  halo shards         'after' only, scattered around HALO_REST = (0.4, 16.8, 0).
  ember horizon       glow lights + emissive haze at y = +65 .. +100 (behind the god).
  blue zone           floor cracks turn blue within CTRL_blue_radius (default 7.5 m) of GOD_POS.

API
---
  build_arena(variant='approach'|'duel'|'after', seed=999) -> Arena
      .floor (slab geometry) .floor_far (procedural plane) .underglow
      .pillars [objects] .rubble [objects] .fallen [objects] .shards (after) .fog {name: object}
      .world .mats {floor, pillar, underglow, fog_ground, fog_blue, fog_horizon, shard}
      .layout (dict of the locked positions above)
    Material controls (rb_mat.key_ctrl(arena.mats['floor'], name, frame, value)):
      floor:     CTRL_crack_glow (1), CTRL_blue_radius (7.5 m), CTRL_blue_glow (1), CTRL_wet (1),
                 CTRL_time (auto: = frame / 30, linear keys)
      pillar:    CTRL_crack_glow (1), CTRL_fade (1 = tops dissolve into darkness)
      underglow: CTRL_glow (1)
      fog_*:     CTRL_density, CTRL_emit, CTRL_time (auto)
      shard:     CTRL_shard_glow (4)
      world:     CTRL_fog (world volume density), CTRL_horizon (ember band in the background)
  RENDER_KW                 -> pass to rb_shot.Shot(..., **RENDER_KW) / rb_core.setup_render (volumetric range)
  tune_eevee(scene)         -> SSR / shadow / volume settings this set relies on (call after setup_render)
  lights_walk(warrior, cam) / lights_god_reveal(cam) / lights_duel(warrior, cam) / lights_after(warrior, cam)
      -> dict name -> light object. Each rig casts at most 2 shadows.
  rim_light(name, target, cam, ...)  -> a rim placed opposite the camera (for per-shot rims)
  scatter_rubble(name, center, radius, count, seed, ...)  -> one joined rubble object
  fallen_pillar(name, start, yaw, seed, ...)              -> one joined object of toppled drums
  halo_shards(center, seed, ...)                          -> broken halo arcs lying on the floor
  make_pillar(name, base, radius, height, seed, broken=...)-> one fluted pillar
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

import rb_core as C
import rb_mat as M
import rb_mesh as G
from rb_core import hexcol, link

# ------------------------------------------------------------------ locked layout
GOD_POS = (0.0, 14.0, 0.0)
CLASH = (0.0, 9.0, 0.0)
WARRIOR_STOP = (0.0, -2.0, 0.0)
WALK_START = (0.0, -40.0, 0.0)
IMPACT = (1.3, 10.8)
HALO_REST = (0.4, 16.8, 0.0)
NAVE_X = 6.5
COL_Y = [-54.0 + 9.0 * k for k in range(13)]
HERO = (-34.0, 34.0, -58.0, 46.0)
FAR = 150.0
HOTSPOTS = ((WARRIOR_STOP[0], WARRIOR_STOP[1], 4.5), (CLASH[0], CLASH[1], 5.0), (0.0, -14.0, 4.0))
EMBER = "#FF6A1A"
BLUE = "#6FA8FF"
BLUE_KEY = "#4A6C8F"

RENDER_KW = dict(vol_end=170.0, vol_tile="8", vol_samples=48)


class Arena:
    pass


# ------------------------------------------------------------------ small node helpers
def _lerp(b, f, x, y):
    """x + (y - x) * f   (float sockets / constants)."""
    return b.math("ADD", x, b.math("MULTIPLY", b.math("SUBTRACT", y, x), f))


def _mr(b, v, f0, f1, t0=0.0, t1=1.0, clamp=True):
    node = b.n("ShaderNodeMapRange", Value=v, **{"From Min": f0, "From Max": f1, "To Min": t0, "To Max": t1})
    node.clamp = clamp
    return node


def _noise(b, vec, scale, detail=4.0, rough=0.55, dims="3D", w=None):
    nz = b.n("ShaderNodeTexNoise", Vector=vec, Scale=scale, Detail=detail, Roughness=rough)
    nz.noise_dimensions = dims
    if w is not None:
        b._in(nz, "W", w)
    return nz


def _vadd(b, a, c, op="ADD"):
    node = b.n("ShaderNodeVectorMath", _operation=op)
    b._in(node, 0, a)
    b._in(node, 1, c)
    return (node, "Vector")


def _key_time(ntree_owner, ctrl_node, fps=C.FPS):
    """Make a CTRL Value node equal frame / fps on every frame (2 linear keys + linear extrapolation)."""
    sock = ctrl_node.outputs[0]
    for f, v in ((0, 0.0), (fps, 1.0)):
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=f)
    ad = ntree_owner.animation_data
    for fc in ad.action.fcurves:
        if ctrl_node.name in fc.data_path:
            fc.extrapolation = "LINEAR"
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"


# ------------------------------------------------------------------ materials
def floor_material(name="arena_floor", god=GOD_POS, hot=HOTSPOTS):
    """Wet cracked dark stone slabs. Reads point attributes from the slab geometry
    (geo=1, slab=per-slab random, rim=0 top..1 joint edge, sink=how low the slab sits);
    the far plane has none of them and falls back to a procedural brick slab pattern."""
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=(geo, "Position"))
    xy = b.n("ShaderNodeCombineXYZ", X=(sep, "X"), Y=(sep, "Y"), Z=0.0)
    tm = b.ctrl("time", 0.0)
    glow = b.ctrl("crack_glow", 1.0)
    wet = b.ctrl("wet", 1.0)
    blue_r = b.ctrl("blue_radius", 7.5)
    blue_k = b.ctrl("blue_glow", 1.0)
    a_geo, a_slab, a_rim, a_sink = b.attr("geo"), b.attr("slab"), b.attr("rim"), b.attr("sink")
    # far-field slab pattern (matches the hero slab sizes)
    brick = b.n("ShaderNodeTexBrick", Vector=xy, Color1=(0, 0, 0), Color2=(1, 1, 1), Mortar=(0, 0, 0), Scale=1.0,
                **{"Mortar Size": 0.035, "Mortar Smooth": 0.4, "Bias": 0.0, "Brick Width": 2.7, "Row Height": 2.35})
    brick.offset, brick.offset_frequency, brick.squash, brick.squash_frequency = 0.37, 2, 1.0, 1
    slab = _lerp(b, a_geo, (brick, "Color"), a_slab)
    rim_j = _mr(b, a_rim, 0.45, 1.0)
    joint = _lerp(b, a_geo, (brick, "Fac"), rim_j)
    # tonal noise
    n_big = _noise(b, xy, 0.035, 4.0)
    n_mid = _noise(b, xy, 0.55, 6.0, 0.6)
    n_fine = _noise(b, xy, 9.0, 8.0, 0.65)
    n_wet = _noise(b, xy, 0.13, 4.0, 0.55)
    tone = b.math("ADD", b.math("MULTIPLY", slab, 0.55), b.math("MULTIPLY", (n_big, "Fac"), 0.6))
    col = b.ramp(tone, [(0.25, (0.016, 0.016, 0.018)), (0.62, (0.045, 0.043, 0.041)), (0.9, (0.085, 0.078, 0.07))])
    var = b.ramp((n_mid, "Fac"), [(0.3, (0.7, 0.72, 0.75)), (0.7, (1.15, 1.1, 1.05))])
    col = b.mix(1.0, col, var, blend="MULTIPLY")
    spk = _mr(b, (n_fine, "Fac"), 0.6, 0.7)
    col = b.mix(b.math("MULTIPLY", spk, 0.25), col, (0.12, 0.115, 0.11))
    col = b.mix(b.math("MULTIPLY", joint, 0.85), col, (0.005, 0.005, 0.005))
    # ---- cracks: domain-warped voronoi edges, clustered by a gate noise + hot spots
    warp = _noise(b, xy, 0.25, 3.0)
    wsub = _vadd(b, (warp, "Color"), (0.5, 0.5, 0.5), "SUBTRACT")
    wsc = b.n("ShaderNodeVectorMath", _operation="SCALE")
    b._in(wsc, 0, wsub)
    wsc.inputs["Scale"].default_value = 1.3
    wv = _vadd(b, (wsc, "Vector"), xy)
    v1 = b.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=0.42)
    b._in(v1, "Vector", wv)
    v2 = b.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=1.7)
    b._in(v2, "Vector", wv)
    core1 = _mr(b, (v1, "Distance"), 0.0012, 0.006, 1.0, 0.0)
    core2 = _mr(b, (v2, "Distance"), 0.0, 0.011, 0.85, 0.0)
    halo = _mr(b, (v1, "Distance"), 0.0, 0.05, 1.0, 0.0)
    halo = b.math("MULTIPLY", halo, halo)
    gate1 = _mr(b, (_noise(b, _vadd(b, xy, (13.0, 7.0, 0.0)), 0.07, 2.0), "Fac"), 0.47, 0.57)
    gate2 = _mr(b, (_noise(b, _vadd(b, xy, (5.0, 31.0, 0.0)), 0.11, 2.0), "Fac"), 0.55, 0.63)
    for (hx, hy, hr) in hot:
        d = b.n("ShaderNodeVectorMath", _operation="DISTANCE")
        b._in(d, 0, xy)
        d.inputs[1].default_value = (hx, hy, 0.0)
        gate1 = b.math("MAXIMUM", gate1, _mr(b, (d, "Value"), hr, hr * 0.35))
    crack = b.math("MAXIMUM", b.math("MULTIPLY", core1, gate1),
                   b.math("MULTIPLY", core2, b.math("MULTIPLY", gate2, gate1)))
    col = b.mix(crack, col, (0.0, 0.0, 0.0))
    # ---- wetness: damp sheen everywhere, puddles in low spots
    wn = b.math("ADD", (n_wet, "Fac"), b.math("MULTIPLY", a_sink, 0.12))
    damp = b.math("MULTIPLY", _mr(b, wn, 0.36, 0.56), wet)
    puddle = b.math("MULTIPLY", _mr(b, wn, 0.585, 0.605), wet)
    col = b.mix(b.math("MULTIPLY", damp, 0.45), col, (0.0, 0.0, 0.0))
    col = b.mix(b.math("MULTIPLY", puddle, 0.35), col, (0.0, 0.0, 0.0))
    rough = b.math("ADD", 0.6, b.math("MULTIPLY", b.math("SUBTRACT", (n_fine, "Fac"), 0.5), 0.3))
    rough = _lerp(b, damp, rough, 0.3)
    rough = _lerp(b, b.math("MULTIPLY", joint, 0.5), rough, 0.18)
    rough = _lerp(b, puddle, rough, 0.025)
    # ---- emission: crack cores + glow spill + glowing joints, ember -> blue near the god
    flick = _noise(b, b.n("ShaderNodeVectorMath", _operation="SCALE", Vector=xy, Scale=0.5), 1.0, 2.0, dims="4D",
                   w=b.math("MULTIPLY", tm, 0.5))
    flick = _mr(b, (flick, "Fac"), 0.3, 0.7, 0.4, 1.0)
    jg = _mr(b, (_noise(b, _vadd(b, xy, (21.0, 3.0, 0.0)), 0.12, 2.0), "Fac"), 0.54, 0.64)
    jglow = b.math("MULTIPLY", _mr(b, joint, 0.55, 1.0), b.math("MAXIMUM", jg, b.math("MULTIPLY", gate1, 0.5)))
    estr = b.math("ADD", b.math("MULTIPLY", crack, 16.0), b.math("MULTIPLY", b.math("MULTIPLY", halo, gate1), 0.5))
    estr = b.math("ADD", estr, b.math("MULTIPLY", jglow, 2.2))
    estr = b.math("MULTIPLY", b.math("MULTIPLY", estr, flick), glow)
    dg = b.n("ShaderNodeVectorMath", _operation="DISTANCE")
    b._in(dg, 0, xy)
    dg.inputs[1].default_value = (god[0], god[1], 0.0)
    dgn = b.math("ADD", (dg, "Value"), b.math("MULTIPLY", b.math("SUBTRACT", (n_mid, "Fac"), 0.5), 3.0))
    bz = b.math("SUBTRACT", 1.0, b.math("DIVIDE", b.math("SUBTRACT", dgn, b.math("SUBTRACT", blue_r, 3.0)), 3.0),
                clamp=True)
    bz = b.math("MULTIPLY", bz, b.math("MINIMUM", blue_k, 1.0))
    ecol = b.mix(bz, hexcol(EMBER), hexcol(BLUE))
    estr = b.math("MULTIPLY", estr, _lerp(b, bz, 1.0, b.math("MAXIMUM", blue_k, 0.0)))
    # ---- bump: pitting, crack grooves, joint grooves on the far plane; puddles are flat
    hgt = b.math("ADD", b.math("MULTIPLY", (n_fine, "Fac"), 0.5), b.math("MULTIPLY", (n_mid, "Fac"), 0.3))
    hgt = b.math("SUBTRACT", hgt, b.math("MULTIPLY", crack, 0.8))
    hgt = b.math("SUBTRACT", hgt, b.math("MULTIPLY", b.math("MULTIPLY", (brick, "Fac"),
                                                             b.math("SUBTRACT", 1.0, a_geo)), 1.2))
    bstr = b.math("MULTIPLY", 0.32, b.math("SUBTRACT", 1.0, puddle))
    bump = b.n("ShaderNodeBump", Strength=bstr, Distance=0.012, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump, "Emission Color": ecol,
                   "Emission Strength": estr})
    bs.inputs["Specular IOR Level"].default_value = 0.5
    b.out(bs)
    _key_time(m.node_tree, M.ctrl_node(m, "time"))
    return m


def underglow_material(name="arena_underglow"):
    """Ember light under the slabs, seen through joints and broken slabs (clustered, flickering)."""
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    g = b.ctrl("glow", 1.0)
    tm = b.ctrl("time", 0.0)
    nz = _noise(b, (geo, "Position"), 0.09, 3.0, dims="4D", w=b.math("MULTIPLY", tm, 0.1))
    k = _mr(b, (nz, "Fac"), 0.45, 0.62, 0.05, 1.0)
    em = b.n("ShaderNodeEmission", Color=hexcol(EMBER), Strength=b.math("MULTIPLY", b.math("MULTIPLY", k, g), 3.0))
    b.out(em)
    _key_time(m.node_tree, M.ctrl_node(m, "time"))
    return m


def pillar_material(name="arena_pillar"):
    """Weathered dark stone: rain streaks, worn arrises (wear), grime in the flutes (cav), fresh chips
    (chip), water wicking up from the wet floor, faint ember hairline cracks at the base and a height
    fade (CTRL_fade) so the shafts dissolve into the dark above."""
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    pos = (geo, "Position")
    wz = b.n("ShaderNodeSeparateXYZ", Vector=pos)
    wear, cav, chip = b.attr("wear"), b.attr("cav"), b.attr("chip")
    fade_k = b.ctrl("fade", 1.0)
    glow = b.ctrl("crack_glow", 1.0)
    n1 = _noise(b, pos, 0.3, 6.0, 0.6)
    n2 = _noise(b, pos, 2.6, 8.0, 0.62)
    smp = b.n("ShaderNodeMapping", Vector=pos, Scale=(2.2, 2.2, 0.07))
    streak = _noise(b, smp, 3.0, 6.0, 0.6)
    col = b.ramp((n1, "Fac"), [(0.28, (0.03, 0.029, 0.027)), (0.55, (0.07, 0.065, 0.058)), (0.8, (0.12, 0.108, 0.094))])
    stk = _mr(b, (streak, "Fac"), 0.42, 0.72, 1.0, 0.4)
    col = b.mix(1.0, col, b.n("ShaderNodeCombineColor", Red=stk, Green=stk, Blue=stk), blend="MULTIPLY")
    col = b.mix(b.math("MULTIPLY", (n2, "Fac"), 0.25), col, (0.0, 0.0, 0.0))
    col = b.mix(b.math("MULTIPLY", wear, 0.55), col, (0.2, 0.185, 0.165))
    col = b.mix(b.math("MULTIPLY", cav, 0.75), col, (0.008, 0.008, 0.008))
    col = b.mix(b.math("MULTIPLY", chip, 0.85), col, (0.15, 0.135, 0.115))
    # wet foot (water wicking up from the floor, ragged edge)
    wzn = b.math("ADD", (wz, "Z"), b.math("MULTIPLY", b.math("SUBTRACT", (n2, "Fac"), 0.5), 1.6))
    wetz = _mr(b, wzn, 2.4, 0.7)
    col = b.mix(b.math("MULTIPLY", wetz, 0.55), col, (0.0, 0.0, 0.0))
    # dissolve into the dark above (scaled by CTRL_fade)
    fz = _mr(b, (wz, "Z"), 14.0, 55.0, 0.0, 0.92)
    col = b.mix(b.math("MULTIPLY", fz, fade_k), col, (0.0, 0.0, 0.0))
    rough = b.math("ADD", 0.8, b.math("MULTIPLY", b.math("SUBTRACT", (n2, "Fac"), 0.5), 0.2))
    rough = _lerp(b, wetz, rough, 0.3)
    rough = _lerp(b, chip, rough, 0.9)
    # ember hairline cracks near the base
    warp = _noise(b, pos, 0.8, 2.0)
    wv = _vadd(b, pos, (warp, "Color"))
    vor = b.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=0.8)
    b._in(vor, "Vector", wv)
    core = _mr(b, (vor, "Distance"), 0.001, 0.0045, 1.0, 0.0)
    gate = b.math("MULTIPLY", _mr(b, (_noise(b, pos, 0.25, 2.0), "Fac"), 0.52, 0.6), _mr(b, (wz, "Z"), 3.2, 0.8))
    estr = b.math("MULTIPLY", b.math("MULTIPLY", core, gate), b.math("MULTIPLY", glow, 9.0))
    col = b.mix(b.math("MULTIPLY", core, gate), col, (0.0, 0.0, 0.0))
    fine = _noise(b, pos, 22.0, 6.0, 0.7)
    hgt = b.math("ADD", b.math("MULTIPLY", (fine, "Fac"), 0.35), b.math("MULTIPLY", (n2, "Fac"), 0.5))
    hgt = b.math("SUBTRACT", hgt, b.math("MULTIPLY", b.math("SUBTRACT", 1.0, stk), 0.2))
    bump = b.n("ShaderNodeBump", Strength=0.38, Distance=0.02, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump, "Emission Color": hexcol(EMBER),
                   "Emission Strength": estr})
    bs.inputs["Specular IOR Level"].default_value = 0.4
    b.out(bs)
    return m


def fog_material(name, density=0.05, height=1.4, color=(0.5, 0.55, 0.6), anisotropy=0.35, scale=0.08,
                 wind=(0.45, 0.15, 0.0), emit_color=None, emit=0.0, center=None, radius=None, z0=0.0):
    """Drifting ground haze: density = CTRL_density * exp(-(z-z0)/height) * noise (wind-advected by
    CTRL_time). Optional radial falloff around `center` and emission that follows the density."""
    m, b = M.new(name)
    geo = b.n("ShaderNodeNewGeometry")
    pos = (geo, "Position")
    tm = b.ctrl("time", 0.0)
    dk = b.ctrl("density", density)
    ek = b.ctrl("emit", emit)
    sep = b.n("ShaderNodeSeparateXYZ", Vector=pos)
    drift = b.n("ShaderNodeCombineXYZ", X=b.math("MULTIPLY", tm, -wind[0]), Y=b.math("MULTIPLY", tm, -wind[1]),
                Z=b.math("MULTIPLY", tm, -wind[2]))
    p = _vadd(b, pos, drift)
    nz = _noise(b, p, scale, 3.0, 0.55, dims="4D", w=b.math("MULTIPLY", tm, 0.04))
    nz2 = _noise(b, p, scale * 4.0, 2.0, 0.5)
    n = b.math("ADD", b.math("MULTIPLY", (nz, "Fac"), 0.75), b.math("MULTIPLY", (nz2, "Fac"), 0.25))
    nk = _mr(b, n, 0.36, 0.66, 0.08, 1.45)
    hz = b.math("EXPONENT", b.math("MULTIPLY", b.math("SUBTRACT", (sep, "Z"), z0), -1.0 / height))
    hz = b.math("MINIMUM", hz, 1.0)
    d = b.math("MULTIPLY", b.math("MULTIPLY", hz, nk), dk)
    if center is not None:
        dc = b.n("ShaderNodeVectorMath", _operation="DISTANCE")
        b._in(dc, 0, b.n("ShaderNodeCombineXYZ", X=(sep, "X"), Y=(sep, "Y"), Z=0.0))
        dc.inputs[1].default_value = (center[0], center[1], 0.0)
        rk = _mr(b, (dc, "Value"), radius, radius * 0.25)
        d = b.math("MULTIPLY", d, b.math("MULTIPLY", rk, rk))
    vol = b.n("ShaderNodeVolumePrincipled", Color=color, Density=d, Anisotropy=anisotropy)
    if emit_color is not None:
        vol.inputs["Emission Color"].default_value = (*hexcol(emit_color), 1.0)
        b.link(b.math("MULTIPLY", b.math("DIVIDE", d, max(density, 1e-6)), ek), vol.inputs["Emission Strength"])
    b.out(volume=vol)
    _key_time(m.node_tree, M.ctrl_node(m, "time"))
    return m


def shard_material(name="arena_halo_shard"):
    """Broken halo pieces: blue-white emissive core that dies out in patches (CTRL_shard_glow)."""
    m, b = M.new(name)
    tc = b.n("ShaderNodeTexCoord")
    g = b.ctrl("shard_glow", 4.0)
    nz = _noise(b, (tc, "Object"), 1.7, 3.0)
    k = _mr(b, (nz, "Fac"), 0.36, 0.6, 0.04, 1.0)
    bs = b.bsdf(**{"Base Color": (0.5, 0.6, 0.7), "Roughness": 0.25,
                   "Emission Color": (0.62, 0.8, 1.0), "Emission Strength": b.math("MULTIPLY", k, g)})
    b.out(bs)
    return m


# ------------------------------------------------------------------ world
def arena_world(density=0.012, color=(0.52, 0.57, 0.63), anisotropy=0.5, horizon=1.0):
    """Void background with a faint ember band low on the +Y horizon; uniform world haze.
    Controls: CTRL_fog (volume density), CTRL_horizon (background band)."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new("ArenaWorld")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")

    def node(kind, **kw):
        n = nt.nodes.new(kind)
        for k, v in kw.items():
            n.inputs[k].default_value = v
        return n

    def ctrl(nm, v):
        n = nt.nodes.new("ShaderNodeValue")
        n.name, n.label = "CTRL_" + nm, nm
        n.outputs[0].default_value = v
        return n

    def math(op, a, bb):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for i, v in enumerate((a, bb)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]

    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    hz = ctrl("horizon", horizon)
    fog = ctrl("fog", density)
    band = math("MULTIPLY", math("SUBTRACT", 1.0, math("MINIMUM", math("MULTIPLY", math("ABSOLUTE", sep.outputs["Z"], 0), 7.0), 1.0)),
                math("MAXIMUM", math("MULTIPLY", sep.outputs["Y"], 1.4), 0.0))
    band = math("MULTIPLY", math("POWER", band, 2.0), hz.outputs[0])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(math("MULTIPLY", band, 0.06), mix.inputs["Factor"])
    mix.inputs[6].default_value = (*hexcol("#07080A"), 1.0)
    mix.inputs[7].default_value = (*hexcol(EMBER), 1.0)
    bg = node("ShaderNodeBackground", Strength=1.0)
    nt.links.new(mix.outputs[2], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    pv = node("ShaderNodeVolumePrincipled", Color=(*color, 1.0), Anisotropy=anisotropy)
    nt.links.new(fog.outputs[0], pv.inputs["Density"])
    nt.links.new(pv.outputs[0], out.inputs["Volume"])
    return w


def tune_eevee(sc=None):
    """Settings this environment relies on (call after rb_core.setup_render)."""
    sc = sc or bpy.context.scene
    e = sc.eevee
    e.ssr_max_roughness = 0.42
    e.ssr_thickness = 0.35
    e.ssr_border_fade = 0.05
    e.ssr_firefly_fac = 6.0
    e.use_ssr_halfres = True
    e.volumetric_end = max(e.volumetric_end, RENDER_KW["vol_end"])
    e.shadow_cascade_size = "2048"
    e.gtao_distance = 1.2
    e.gtao_factor = 1.0
    return sc


# ------------------------------------------------------------------ floor geometry
def _inset(poly, d):
    """Inset a convex CCW polygon (n x 2) by distance d (uniform edge offset)."""
    P = np.asarray(poly, float)
    E = np.roll(P, -1, 0) - P
    L = np.linalg.norm(E, axis=1, keepdims=True)
    N = np.stack([-E[:, 1], E[:, 0]], 1) / np.maximum(L, 1e-9)
    out = []
    n = len(P)
    for i in range(n):
        p1, d1 = P[i - 1] + N[i - 1] * d, E[i - 1]
        p2, d2 = P[i] + N[i] * d, E[i]
        A = np.array([[d1[0], -d2[0]], [d1[1], -d2[1]]])
        if abs(np.linalg.det(A)) < 1e-9:
            out.append(p2)
            continue
        t, _ = np.linalg.solve(A, p2 - p1)
        out.append(p1 + t * d1)
    return np.array(out)


def _clean(poly, eps=0.03):
    """Drop near-duplicate and collinear vertices."""
    P = [np.asarray(p, float) for p in poly]
    out = []
    for p in P:
        if not out or np.linalg.norm(p - out[-1]) > eps:
            out.append(p)
    if len(out) > 1 and np.linalg.norm(out[0] - out[-1]) < eps:
        out.pop()
    res = []
    n = len(out)
    for i in range(n):
        a, b2, c = out[i - 1], out[i], out[(i + 1) % n]
        cr = (b2[0] - a[0]) * (c[1] - b2[1]) - (b2[1] - a[1]) * (c[0] - b2[0])
        if abs(cr) > 1e-4:
            res.append(b2)
    return np.array(res)


def _split(poly, p, nrm):
    """Split a convex polygon by the line through p with normal nrm -> (a, b)."""
    a, bb = [], []
    n = len(poly)
    for i in range(n):
        P, Q = poly[i], poly[(i + 1) % n]
        sp, sq = np.dot(P - p, nrm), np.dot(Q - p, nrm)
        if sp >= 0:
            a.append(P)
        if sp <= 0:
            bb.append(P)
        if sp * sq < 0:
            X = P + (Q - P) * (sp / (sp - sq))
            a.append(X)
            bb.append(X)
    return np.array(a), np.array(bb)


def _area(poly):
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * (np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


class _MeshAcc:
    """Accumulates verts/faces/point attributes for one big mesh (built with from_pydata)."""

    def __init__(self, attrs=()):
        self.v, self.f = [], []
        self.a = {k: [] for k in attrs}

    def add(self, verts, faces, **attrs):
        base = len(self.v)
        self.v.extend(map(tuple, verts))
        self.f.extend([tuple(i + base for i in fc) for fc in faces])
        for k in self.a:
            val = attrs.get(k, 0.0)
            self.a[k].extend(list(val) if hasattr(val, "__len__") else [val] * len(verts))

    def build(self, name, mat=None, smooth=True, auto=35.0):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.v, [], self.f)
        me.update()
        for k, vals in self.a.items():
            at = me.attributes.new(k, "FLOAT", "POINT")
            at.data.foreach_set("value", np.asarray(vals, np.float32))
        if smooth:
            me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
            if auto and hasattr(me, "use_auto_smooth"):
                me.use_auto_smooth = True
                me.auto_smooth_angle = math.radians(auto)
        ob = bpy.data.objects.new(name, me)
        link(ob)
        if mat is not None:
            me.materials.append(mat)
        return ob


def _slab_piece(acc, poly, z_top, thick, cham, rot, center, slab_id, sink):
    """Extruded convex slab with a rounded 2-segment chamfer. rot: 3x3 tilt about its centroid."""
    rings = []
    for inset, drop in ((cham, 0.0), (cham * 0.293, cham * 0.293), (0.0, cham), (0.0, thick)):
        r = _inset(poly, inset) if inset > 0 else np.asarray(poly, float)
        rings.append(np.column_stack([r, np.full(len(r), -drop)]))
    n = len(poly)
    V = np.vstack(rings) - np.array([center[0], center[1], 0.0])
    V = V @ rot.T + np.array([center[0], center[1], z_top])
    faces = [tuple(range(n))]
    for k in range(3):
        for i in range(n):
            j = (i + 1) % n
            faces.append((k * n + i, (k + 1) * n + i, (k + 1) * n + j, k * n + j))
    rim = [0.0] * n + [0.5] * n + [1.0] * n + [1.0] * n
    acc.add(V, faces, geo=1.0, slab=slab_id, rim=rim, sink=sink)


def _tilt(rx, ry, rz=0.0):
    return np.array(Euler((rx, ry, rz), "XYZ").to_matrix())


def build_floor(seed=999, zone=HERO, impact=None, mat=None, name="ARENA_floor"):
    """Hand-laid slab floor: running-bond rows of random-width slabs, some cracked into pieces
    (one piece sunk/tilted), small per-slab tilts. `impact`=(x, y, r) smashes the slabs there."""
    rnd = random.Random(seed)
    acc = _MeshAcc(("geo", "slab", "rim", "sink"))
    x0, x1, y0, y1 = zone
    y = y0
    while y < y1:
        d = rnd.uniform(1.9, 2.8)
        x = x0 - rnd.uniform(0.0, 2.6)
        while x < x1:
            w = rnd.uniform(1.6, 2.6) if rnd.random() < 0.55 else rnd.uniform(2.6, 3.9)
            rect = np.array([(x, y), (x + w, y), (x + w, y + d), (x, y + d)])
            cx, cy = x + w / 2, y + d / 2
            sid = rnd.random()
            dist_imp = math.hypot(cx - impact[0], cy - impact[1]) if impact else 1e9
            smash = impact is not None and dist_imp < impact[2]
            pieces = [rect]
            nsplit = 0
            r_ = rnd.random()
            if smash:
                nsplit = rnd.randint(2, 4)
            elif r_ < 0.2:
                nsplit = 1
            elif r_ < 0.27:
                nsplit = 2
            for _ in range(nsplit):
                pieces.sort(key=lambda p: -abs(_area(p)))
                big = pieces.pop(0)
                c = big.mean(0) + np.array([rnd.uniform(-0.3, 0.3) * w, rnd.uniform(-0.3, 0.3) * d])
                ang = rnd.uniform(0, math.pi)
                a, bpart = _split(big, c, np.array([math.cos(ang), math.sin(ang)]))
                pieces += [p for p in (a, bpart) if len(p) >= 3]
            base_dz = rnd.gauss(0.0, 0.006)
            base_t = (rnd.gauss(0, 0.004), rnd.gauss(0, 0.004))
            for k, pc in enumerate(pieces):
                pc = _clean(pc)
                if len(pc) < 3 or abs(_area(pc)) < 0.04:
                    continue
                gap = rnd.uniform(0.012, 0.02)
                pc = _inset(pc, gap)
                if len(pc) < 3 or abs(_area(pc)) < 0.03:
                    continue
                ctr = pc.mean(0)
                dz, (rx, ry) = base_dz, base_t
                if nsplit and not smash and k == len(pieces) - 1:
                    dz -= rnd.uniform(0.015, 0.05)
                    rx += rnd.gauss(0, 0.02)
                    ry += rnd.gauss(0, 0.02)
                if smash:
                    v = ctr - np.array(impact[:2])
                    dn = max(np.linalg.norm(v), 1e-3)
                    fall = 1.0 - dn / impact[2]
                    tilt = rnd.uniform(0.04, 0.2) * (0.4 + fall)
                    # pieces tip away from the impact centre: inner edge down, outer edge up
                    rx += -v[1] / dn * tilt
                    ry += v[0] / dn * tilt
                    dz -= rnd.uniform(0.02, 0.12) * (0.3 + fall)
                cham = rnd.uniform(0.018, 0.04) if not smash else rnd.uniform(0.008, 0.02)
                _slab_piece(acc, pc, dz, 0.22, cham, _tilt(rx, ry), ctr, sid, max(0.0, -dz * 25.0))
            x += w
        y += d
    ob = acc.build(name, mat)
    return ob


def build_far_floor(mat, zone=HERO, far=FAR, name="ARENA_floor_far"):
    """Big procedural slab plane around the hero zone (4 quads leaving a hole for the slabs)."""
    x0, x1, y0, y1 = zone
    z = -0.004
    V = [(-far, -far, z), (far, -far, z), (far, far, z), (-far, far, z),
         (x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    F = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(V, [], F)
    me.update()
    ob = bpy.data.objects.new(name, me)
    link(ob)
    me.materials.append(mat)
    return ob


def build_underglow(mat, zone=HERO, z=-0.075, name="ARENA_underglow"):
    x0, x1, y0, y1 = zone
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new(name, me)
    link(ob)
    me.materials.append(mat)
    ob.visible_shadow = False
    return ob


# ------------------------------------------------------------------ pillars
def _flute(theta, flutes, depth):
    """Concave flute depth profile (sharp arrises between flutes). Returns (depth, phase-centre 0..1)."""
    ph = np.mod(theta * flutes / (2 * math.pi), 1.0)
    q = (ph - 0.5) / 0.44
    d = np.where(np.abs(q) < 1.0, np.sqrt(np.clip(1.0 - q * q, 0.0, 1.0)), 0.0)
    return depth * d, d


def _lathe_rows(radius, height, z_start, seed, broken, detail_top=14.0):
    """Row table for a fluted shaft: list of (z, r_scale, groove, drum_index)."""
    rnd = random.Random(seed)
    rows = []
    z = z_start
    top = broken if broken else height
    di = 0
    c = 0.045
    while z < top - 0.05:
        dh = rnd.uniform(1.8, 2.6) if z < detail_top else rnd.uniform(3.2, 4.4)
        z1 = min(z + dh, top)
        nint = max(1, int((z1 - z) / 0.32)) if z < detail_top else 1
        rows.append((z + (c if di else 0.0), 1.0, 0.0, di))
        for k in range(1, nint):
            rows.append((z + (z1 - z) * k / nint, 1.0, 0.0, di))
        if z1 < top - 0.05:
            rows.append((z1 - c, 1.0, 0.0, di))
            rows.append((z1, 1.0, 1.0, di))       # seam groove between drums
        else:
            rows.append((z1, 1.0, 0.0, di))
        z = z1
        di += 1
    return rows


def make_pillar(name, base, radius=1.85, height=85.0, flutes=20, seed=0, broken=None, lean=(0.0, 0.0),
                mat=None, cols_per_flute=5, chips=True, plinth=True, mouldings=True, cap_bottom=False):
    """One colossal fluted pillar standing at base (x, y): square plinth, round base mouldings,
    a drum-stacked fluted shaft with entasis, planar chips at drum edges, optional broken top
    (jagged, cratered) and lean. Point attributes wear / cav / chip for pillar_material()."""
    rnd = random.Random(seed)
    NC = flutes * cols_per_flute
    th = np.linspace(0, 2 * math.pi, NC, endpoint=False)
    R = radius
    pz = 1.0 if plinth else 0.0
    # (z, radius multiplier, flute factor) for the mouldings
    mould = [] if not mouldings else [(pz, 1.3, 0), (pz + 0.12, 1.36, 0), (pz + 0.3, 1.33, 0), (pz + 0.42, 1.22, 0), (pz + 0.48, 1.13, 0),
             (pz + 0.62, 1.11, 0), (pz + 0.72, 1.2, 0), (pz + 0.86, 1.18, 0), (pz + 0.94, 1.07, 0),
             (pz + 1.06, 1.06, 0)]
    shaft0 = pz + 1.12 if mouldings else 0.0
    rows = _lathe_rows(R, height, shaft0, seed + 1, broken)
    fd = 0.065 * R
    P, wear, cav, chip, ztab = [], [], [], [], []
    for z, s, f in mould:
        ring = np.column_stack([R * s * np.cos(th), R * s * np.sin(th), np.full(NC, z)])
        P.append(ring)
        wear.append(np.full(NC, 0.35 if s > 1.2 else 0.0))
        cav.append(np.full(NC, 0.5 if s < 1.12 else 0.0))
        ztab.append(-1)
    for z, s, groove, di in rows:
        taper = 1.0 - 0.07 * min(1.0, (z - shaft0) / 60.0)
        fade_in = min(1.0, (z - shaft0) / 0.35 + 0.15)
        dep, d01 = _flute(th, flutes, fd * fade_in)
        r = R * taper - dep - groove * 0.05
        ring = np.column_stack([r * np.cos(th), r * np.sin(th), np.full(NC, z)])
        P.append(ring)
        wear.append(np.where(d01 < 0.05, 1.0, 0.0) * (1 - groove))
        cav.append(d01 * 0.6 + groove)
        ztab.append(di)
    P = np.array(P)
    wear, cav = np.array(wear), np.array(cav)
    chipm = np.zeros(P.shape[:2])
    # ---- broken top: jagged rim + cratered cap
    if broken:
        k0 = int(np.searchsorted([r[0] for r in rows], broken - 1.3)) + len(mould)
        zb0 = P[k0, 0, 2]
        jag = np.zeros(NC)
        for _ in range(5):
            a0 = rnd.uniform(0, 2 * math.pi)
            w_ = rnd.uniform(0.3, 1.2)
            amp = rnd.uniform(-1.2, 0.9)
            dd = np.angle(np.exp(1j * (th - a0)))
            jag += amp * np.exp(-(dd / w_) ** 2)
        jag += np.array([rnd.uniform(-0.12, 0.12) for _ in range(NC)])
        ztop = broken + np.clip(jag, -1.0, 1.1)
        for k in range(k0, P.shape[0]):
            t = (P[k, 0, 2] - zb0) / max(1e-6, broken - zb0)
            P[k, :, 2] = zb0 + t * (ztop - zb0)
        chipm[-1] = 1.0
        # cap rings toward the centre (broken, uneven surface)
        for rr in (0.75, 0.45, 0.18):
            ring = P[-1].copy()
            ring[:, 0] *= rr
            ring[:, 1] *= rr
            ring[:, 2] = ring[:, 2] * 0.6 + (broken + rnd.uniform(-0.5, 0.2)) * 0.4 + \
                np.array([rnd.uniform(-0.12, 0.12) for _ in range(NC)])
            P = np.concatenate([P, ring[None]], 0)
            wear = np.concatenate([wear, np.zeros((1, NC))], 0)
            cav = np.concatenate([cav, np.zeros((1, NC))], 0)
            chipm = np.concatenate([chipm, np.ones((1, NC))], 0)
            ztab.append(-2)
    # ---- planar chips on drum edges (lower drums only: never seen above ~15 m)
    if chips:
        ztab_a = np.array(ztab)
        ndr = max([r[3] for r in rows] + [0]) + 1
        for di in range(ndr):
            sel = np.where(ztab_a == di)[0]
            if not len(sel):
                continue
            zlo, zhi = P[sel[0], 0, 2], P[sel[-1], 0, 2]
            if zlo > 16.0:
                break
            for _ in range(rnd.randint(1, 4)):
                tc = rnd.uniform(0, 2 * math.pi)
                edge = rnd.random() < 0.65
                zc = (zhi if rnd.random() < 0.5 else zlo) if edge else rnd.uniform(zlo, zhi)
                alpha = (rnd.uniform(0.5, 0.95) * (1 if zc == zhi else -1)) if edge else rnd.uniform(-0.3, 0.3)
                n = np.array([math.cos(tc) * math.cos(alpha), math.sin(tc) * math.cos(alpha), math.sin(alpha)])
                depth = rnd.uniform(0.05, 0.22) if edge else rnd.uniform(0.03, 0.12)
                q = np.array([R * math.cos(tc), R * math.sin(tc), zc]) - n * depth
                for i in sel:
                    s = (P[i] - q) @ n
                    m_ = s > 0
                    if m_.any():
                        P[i][m_] -= np.outer(s[m_], n)
                        chipm[i][m_] = np.maximum(chipm[i][m_], np.clip(s[m_] / 0.02, 0, 1))
    # ---- mesh
    nr = P.shape[0]
    acc = _MeshAcc(("wear", "cav", "chip"))
    faces = []
    for i in range(nr - 1):
        for j in range(NC):
            j2 = (j + 1) % NC
            faces.append((i * NC + j, i * NC + j2, (i + 1) * NC + j2, (i + 1) * NC + j))
    V = P.reshape(-1, 3)
    cen = np.array([[0.0, 0.0, P[-1, :, 2].mean() + (rnd.uniform(-0.3, 0.1) if broken else 0.0)]])
    faces += [((nr - 1) * NC + j, (nr - 1) * NC + (j + 1) % NC, nr * NC) for j in range(NC)]
    if cap_bottom:
        faces += [((j + 1) % NC, j, nr * NC + 1) for j in range(NC)]
        cen = np.vstack([cen, [[0.0, 0.0, P[0, :, 2].mean()]]])
    ncen = len(cen)
    acc.add(np.vstack([V, cen]), faces, wear=np.append(wear.ravel(), [0.0] * ncen),
            cav=np.append(cav.ravel(), [0.0] * ncen), chip=np.append(chipm.ravel(), [1.0 if broken else 0.0] * ncen))
    # plinth (square block, chamfered, chipped corners)
    if plinth:
        hw = R * 1.45
        sq = np.array([(-hw, -hw), (hw, -hw), (hw, hw), (-hw, hw)])
        _slab_piece(_PlAcc(acc), sq, pz, pz + 0.25, 0.07, np.eye(3), (0.0, 0.0), 0, 0)
    rot = Euler((lean[0], lean[1], rnd.uniform(0, 2 * math.pi)), "XYZ").to_matrix()
    acc.v = [tuple(rot @ Vector(v)) for v in acc.v]
    ob = acc.build(name, mat, auto=50.0)
    ob.location = (base[0], base[1], 0.0)
    return ob


class _PlAcc:
    """Adapter: lets _slab_piece write into a pillar accumulator (maps slab attrs -> wear/cav/chip)."""

    def __init__(self, acc):
        self.acc = acc

    def add(self, verts, faces, **attrs):
        rim = attrs.get("rim", [0] * len(verts))
        self.acc.add(verts, faces, wear=[0.6 if r == 0.5 else 0.0 for r in rim], cav=0.0, chip=0.0)


# ------------------------------------------------------------------ rubble / fallen pillars / shards
_ICO = None


def _ico():
    global _ICO
    if _ICO is None:
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        V = np.array([v.co[:] for v in bm.verts])
        F = [tuple(v.index for v in f.verts) for f in bm.faces]
        bm.free()
        _ICO = (V, F)
    return _ICO


def _rock(acc, rnd, center, size, flat=0.6, sink=0.25):
    """Angular broken-stone chunk: icosphere + 4-7 random planar cuts, anisotropic scale."""
    V, F = _ico()
    V = V.copy()
    chip = np.zeros(len(V))
    for _ in range(rnd.randint(4, 7)):
        n = np.array([rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1)])
        n /= np.linalg.norm(n)
        dd = rnd.uniform(0.35, 0.8)
        s = V @ n - dd
        m_ = s > 0
        V[m_] -= np.outer(s[m_], n)
        chip[m_] = 1.0
    V *= np.array([rnd.uniform(0.7, 1.3), rnd.uniform(0.7, 1.3), rnd.uniform(flat * 0.7, flat * 1.2)])
    rot = np.array(Euler((rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), rnd.uniform(0, 6.3))).to_matrix())
    V = (V @ rot.T) * size
    V += np.array([center[0], center[1], -V[:, 2].min() - sink * size + center[2]])
    acc.add(V, F, wear=0.0, cav=0.0, chip=chip * 0.7)


def scatter_rubble(name, center, radius, count, seed, size=(0.05, 0.7), mat=None, bias=2.2, avoid=(), flat=0.6,
                   ring=0.0):
    """Seeded pile of broken stone around `center` (x, y): power-law sizes (many small, few big),
    denser toward the centre (or around a `ring` radius). avoid = [(x, y, r)] circles kept clear."""
    rnd = random.Random(seed)
    acc = _MeshAcc(("wear", "cav", "chip"))
    n = 0
    tries = 0
    while n < count and tries < count * 20:
        tries += 1
        s = size[0] * (size[1] / size[0]) ** (rnd.random() ** bias)
        a = rnd.uniform(0, 2 * math.pi)
        rr = ring + (radius - ring) * rnd.random() ** 1.5 if ring else radius * rnd.random() ** 0.8
        x, y = center[0] + rr * math.cos(a), center[1] + rr * math.sin(a)
        if any(math.hypot(x - ax, y - ay) < ar + s for ax, ay, ar in avoid):
            continue
        _rock(acc, rnd, (x, y, 0.0), s, flat=flat)
        n += 1
    return acc.build(name, mat or pillar_material(), auto=40.0)


def fallen_pillar(name, start, yaw, seed, radius=1.7, drums=6, flutes=20, mat=None):
    """A toppled pillar: a run of fluted drums lying on the floor along `yaw` from `start`, spreading
    apart and rolling like dominoes, half-sunk, with chunks of rubble around."""
    rnd = random.Random(seed)
    mat = mat or pillar_material()
    objs = []
    d = 0.0
    for k in range(drums):
        L = rnd.uniform(1.6, 2.5)
        broken = None
        dr = make_pillar(name + "_d%d" % k, (0, 0), radius=radius * (1 - 0.012 * k), height=L, flutes=flutes,
                         seed=seed * 31 + k, broken=(L if rnd.random() < 0.35 else None), mat=mat,
                         cols_per_flute=4, plinth=False, mouldings=False, cap_bottom=True, chips=True)
        gap = rnd.uniform(0.05, 0.9)
        yk = yaw + rnd.gauss(0, 0.12) + 0.04 * k
        cx = start[0] + math.cos(yaw) * (d + L / 2)
        cy = start[1] + math.sin(yaw) * (d + L / 2)
        m = Matrix.Translation((cx, cy, radius * 0.9 - rnd.uniform(0.0, 0.25))) @ \
            Matrix.Rotation(yk + math.pi / 2, 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "X") @ \
            Matrix.Rotation(rnd.uniform(0, 6.3), 4, "Z") @ Matrix.Translation((0, 0, -L / 2))
        dr.matrix_world = m
        objs.append(dr)
        d += L + gap
    end = (start[0] + math.cos(yaw) * d * 0.5, start[1] + math.sin(yaw) * d * 0.5)
    rub = scatter_rubble(name + "_rubble", end, d * 0.55 + radius, int(40 + d * 6), seed + 7, size=(0.06, 0.9),
                         mat=mat)
    objs.append(rub)
    return objs


def halo_shards(center=HALO_REST, seed=13, count=11, radius=0.95, tube=0.032, mat=None, spread=3.2,
                name="ARENA_halo_shards"):
    """The shattered halo lying on the floor: arc pieces of the god's ring (radius 0.95, tube 0.032)
    scattered around `center`, plus small glowing fragments. One object, material CTRL_shard_glow."""
    rnd = random.Random(seed)
    mat = mat or shard_material()
    objs = []
    for k in range(count):
        span = rnd.uniform(0.18, 0.75)
        a0 = rnd.uniform(0, 2 * math.pi)
        pts = []
        for i in range(18):
            a = a0 + span * i / 17
            r = radius + 0.012 * math.sin(a * 13 + k)
            pts.append((r * math.cos(a), r * math.sin(a), 0.0))
        t = G.curve_tube(name + "_arc%d" % k, pts, radius=tube * rnd.uniform(0.9, 1.1))
        # recentre on the arc midpoint, then lay it on the floor
        mid = Vector(pts[len(pts) // 2])
        for v in t.data.vertices:
            v.co -= mid
        rr = spread * rnd.random() ** 0.7
        aa = rnd.uniform(0, 2 * math.pi)
        t.location = (center[0] + rr * math.cos(aa), center[1] + rr * math.sin(aa), tube * 0.8)
        t.rotation_euler = (rnd.uniform(-0.15, 0.15), rnd.uniform(-0.15, 0.15), rnd.uniform(0, 6.3))
        objs.append(t)
    for k in range(count * 2):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rnd.uniform(0.012, 0.035))
        rr = spread * 1.2 * rnd.random() ** 0.6
        aa = rnd.uniform(0, 2 * math.pi)
        c = Vector((center[0] + rr * math.cos(aa), center[1] + rr * math.sin(aa), 0.015))
        for v in bm.verts:
            v.co.x *= 1.8
            v.co += c
        me = bpy.data.meshes.new(name + "_frag%d" % k)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(name + "_frag%d" % k, me)
        link(o)
        objs.append(o)
    bpy.context.view_layer.update()
    for o in objs:
        o.data.materials.clear()
        o.data.materials.append(mat)
    ob = G.join(objs, name)
    return ob


# ------------------------------------------------------------------ fog volumes
def _box(name, lo, hi, mat):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector([lo[i] + (v.co[i] + 0.5) * (hi[i] - lo[i]) for i in range(3)])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    link(ob)
    me.materials.append(mat)
    ob.visible_shadow = False
    return ob


# ------------------------------------------------------------------ the arena
def _pillar_plan(seed):
    """Deterministic pillar list: (name, x, y, radius, height, broken, lean) for colonnades + scattered."""
    rnd = random.Random(seed * 7 + 1)
    plan = []
    for side in (-1, 1):
        for k, y in enumerate(COL_Y):
            if rnd.random() < 0.08 and abs(y - GOD_POS[1]) > 12 and y < -20:
                continue                                    # a gap in the colonnade
            x = side * (NAVE_X + rnd.uniform(-0.5, 0.7))
            yy = y + rnd.uniform(-1.0, 1.0)
            r = rnd.uniform(1.7, 2.0)
            keep = abs(y - CLASH[1]) < 1 or abs(y - 18.0) < 1 or abs(y - (-18.0)) < 1
            broken = None
            if not keep and rnd.random() < 0.32:
                broken = rnd.uniform(3.5, 17.0)
            lean = (rnd.gauss(0, 0.03), rnd.gauss(0, 0.03)) if broken else (0.0, 0.0)
            plan.append(("ARENA_col%s%02d" % ("L" if side < 0 else "R", k), x, yy, r, rnd.uniform(75, 95), broken,
                         lean, 5))
    # scattered pillars in the far dark (outer aisles and beyond), none on the axis corridor
    n = 0
    while n < 30:
        x = rnd.uniform(-85, 85)
        y = rnd.uniform(-80, 100)
        if abs(x) < 15 or any(math.hypot(x - p[1], y - p[2]) < 9 for p in plan):
            continue
        r = rnd.uniform(1.6, 2.8)
        broken = rnd.uniform(5, 30) if rnd.random() < 0.35 else None
        plan.append(("ARENA_far%02d" % n, x, y, r, rnd.uniform(80, 110), broken,
                     (rnd.gauss(0, 0.03), rnd.gauss(0, 0.03)) if broken else (0, 0), 3))
        n += 1
    return plan


def build_arena(variant="approach", seed=999, pillars=True, far_pillars=True, rubble=True, fog=True):
    """Build the whole Floor 999 arena. variant: 'approach' (intact floor), 'duel' (smashed crater at
    IMPACT + extra debris), 'after' (duel + shattered halo on the floor). Returns an Arena handle."""
    A = Arena()
    A.variant = variant
    A.layout = dict(god=GOD_POS, clash=CLASH, warrior_stop=WARRIOR_STOP, walk_start=WALK_START, impact=IMPACT,
                    halo_rest=HALO_REST, nave_x=NAVE_X, hero=HERO, far=FAR)
    A.world = arena_world()
    fm = floor_material()
    pm = pillar_material()
    um = underglow_material()
    A.mats = {"floor": fm, "pillar": pm, "underglow": um, "world": A.world}
    impact = (IMPACT[0], IMPACT[1], 3.4) if variant in ("duel", "after") else None
    A.floor = build_floor(seed, impact=impact, mat=fm)
    A.floor_far = build_far_floor(fm)
    A.underglow = build_underglow(um)
    A.pillars, A.rubble, A.fallen = [], [], []
    if pillars:
        for nm, x, y, r, h, broken, lean, cpf in _pillar_plan(seed):
            if nm.startswith("ARENA_far") and not far_pillars:
                continue
            ob = make_pillar(nm, (x, y), radius=r, height=h, seed=sum(map(ord, nm)) * 13 + seed, broken=broken, lean=lean, mat=pm, cols_per_flute=cpf,
                             chips=nm.startswith("ARENA_col"))
            A.pillars.append(ob)
            if broken and rubble and nm.startswith("ARENA_col"):
                A.rubble.append(scatter_rubble(nm + "_rubble", (x, y), r * 2.6, int(30 + broken * 3), seed + len(A.rubble),
                                               size=(0.05, 0.8), mat=pm, ring=r * 1.3,
                                               avoid=[(0.0, y, 2.5)]))
    if rubble:
        A.fallen += fallen_pillar("ARENA_fallenL", (-15.5, -30.5), math.radians(35), seed + 3, radius=1.75, drums=7,
                                  mat=pm)
        A.fallen += fallen_pillar("ARENA_fallenR", (17.0, 27.5), math.radians(200), seed + 5, radius=1.85, drums=5,
                                  mat=pm)
        # loose debris along the approach and around the court
        A.rubble.append(scatter_rubble("ARENA_debris_path", (0.0, -10.0), 26.0, 220, seed + 11, size=(0.03, 0.35),
                                       mat=pm, avoid=[(0.0, yy, 1.4) for yy in range(-44, 14, 2)]))
        A.rubble.append(scatter_rubble("ARENA_debris_court", (0.0, 14.0), 13.0, 140, seed + 12, size=(0.03, 0.4),
                                       mat=pm, ring=4.0, avoid=[(0.0, 14.0, 3.5), (0.0, 9.0, 2.5)]))
    if variant in ("duel", "after"):
        A.rubble.append(scatter_rubble("ARENA_impact_rubble", IMPACT, 4.2, 90, seed + 21, size=(0.03, 0.45), mat=pm,
                                       ring=1.2, avoid=[(0.0, 8.8, 0.9), (0.0, 14.0, 1.6)]))
    if variant == "after":
        sm = shard_material()
        A.mats["shard"] = sm
        A.shards = halo_shards(mat=sm)
        A.rubble.append(scatter_rubble("ARENA_after_debris", (0.0, 13.0), 9.0, 160, seed + 31, size=(0.03, 0.5),
                                       mat=pm, ring=2.0, avoid=[(0.0, 9.0, 1.2)]))
    else:
        A.shards = None
    A.fog = {}
    if fog:
        A.mats["fog_ground"] = fog_material("arena_fog_ground", density=0.06, height=1.3, color=(0.5, 0.55, 0.6),
                                            anisotropy=0.4, scale=0.07)
        A.fog["ground"] = _box("ARENA_fog_ground", (-70, -75, -0.3), (70, 75, 9.0), A.mats["fog_ground"])
        A.mats["fog_blue"] = fog_material("arena_fog_blue", density=0.07, height=2.2, color=(0.6, 0.75, 1.0),
                                          anisotropy=0.2, scale=0.12, emit_color=BLUE, emit=0.06, center=GOD_POS[:2],
                                          radius=9.0, wind=(0.2, -0.3, 0.05))
        A.fog["blue"] = _box("ARENA_fog_blue", (-10, 4, -0.3), (10, 24, 10.0), A.mats["fog_blue"])
        A.mats["fog_horizon"] = fog_material("arena_fog_horizon", density=0.012, height=9.0, color=(0.8, 0.6, 0.5),
                                             anisotropy=0.3, scale=0.03, emit_color=EMBER, emit=0.5,
                                             wind=(0.6, 0.0, 0.0))
        A.fog["horizon"] = _box("ARENA_fog_horizon", (-140, 62, -0.5), (140, 125, 40.0), A.mats["fog_horizon"])
    return A


# ------------------------------------------------------------------ lights
def _L(kind, name, loc, color, energy, target=None, size=0.3, shadow=False, spot=45.0, blend=0.3, volume=1.0,
       specular=1.0):
    ob = C.light(kind, "ARENA_" + name, tuple(loc), color=color, energy=energy, size=size, target=target,
                 shadow=shadow, spot_size=math.radians(spot), blend=blend, volume=volume, specular=specular)
    if shadow:
        ob.data.shadow_buffer_bias = 0.02
        ob.data.shadow_buffer_clip_start = 0.5
    return ob


def rim_light(name, target, cam, color=EMBER, energy=400.0, dist=3.2, height=1.4, side=1.0, spot=40.0, size=0.6,
              volume=0.3):
    """Shadowless spot placed behind `target` as seen from `cam` (offset sideways by `side` m),
    aimed at the target: an edge light for that camera."""
    t, c = Vector(target), Vector(cam)
    d = t - c
    d.z = 0
    d.normalize()
    sidev = Vector((-d.y, d.x, 0.0))
    loc = t + d * dist + sidev * side + Vector((0, 0, height))
    return _L("SPOT", name, loc, color, energy, target=t, size=size, spot=spot, blend=0.5, volume=volume)


def horizon_glows(k=1.0):
    """Ember fire glow far behind the god: big soft shadowless point lights lighting the haze."""
    specs = [(-38, 80, 6, 1.0), (-9, 94, 3.5, 1.4), (14, 76, 8, 0.8), (46, 88, 5, 1.0), (-78, 100, 6, 0.8),
             (80, 104, 4, 0.7)]
    return {"horizon%d" % i: _L("POINT", "horizon%d" % i, (x, y, z), EMBER, 2.2e5 * e * k, size=8.0, volume=1.0,
                                specular=0.6) for i, (x, y, z, e) in enumerate(specs)}


def god_rays(specs, color="#AFC2D6", k=1.0):
    """Narrow shadowless spots from high above: visible shafts in the haze. specs: [(top, floor, deg, energy)]."""
    out = {}
    for i, (top, floor, deg, e) in enumerate(specs):
        out["ray%d" % i] = _L("SPOT", "ray%d" % i, top, color, e * k, target=floor, size=1.5, spot=deg, blend=0.15,
                              volume=1.0, specular=0.3)
    return out


def lights_walk(warrior=(0.0, -14.0, 0.0), cam=None, god=GOD_POS):
    """O2-O4: ember backlight through the fog, ember rim on the warrior, a cold moon from above-behind
    the god (shadowed: pillar shadows and shafts in the haze), the blue zone around the god (shadowed
    top shaft), god rays down the nave. 2 shadow casters: moon + god_top."""
    W = Vector(warrior)
    Gp = Vector(god)
    cam = Vector(cam) if cam is not None else W + Vector((-0.6, -3.0, 0.6))
    L = {}
    L["moon"] = _L("SUN", "moon", (0, 0, 50), "#8DA4BD", 0.35, target=(-0.35, -1.0, 47.9), size=math.radians(2.0),
                   shadow=True, volume=1.0, specular=1.0)
    L["moon"].data.shadow_cascade_max_distance = 160.0
    L["moon"].data.shadow_cascade_count = 4
    L["moon"].data.shadow_cascade_exponent = 0.75
    L["rim"] = rim_light("rim", W + Vector((0, 0, 1.25)), cam, EMBER, 650.0, dist=3.0, height=1.3, side=1.2)
    L["rim2"] = rim_light("rim2", W + Vector((0, 0, 1.0)), cam, "#FF7A2E", 300.0, dist=2.5, height=0.2, side=-1.4)
    L["bounce"] = _L("AREA", "bounce", W + Vector((0, 0.8, 0.05)), EMBER, 70.0, size=5.0, volume=0.0, specular=0.2)
    L["bounce"].rotation_euler = (math.pi, 0, 0)
    L["god_top"] = _L("SPOT", "god_top", Gp + Vector((-4.0, 7.0, 34.0)), "#7FA9E6", 26000.0, target=Gp + Vector((0, 0, 2.5)),
                      size=0.8, spot=13.0, blend=0.25, shadow=True, volume=1.0)
    L["god_under"] = _L("POINT", "god_under", Gp + Vector((0.0, -2.6, 0.5)), BLUE, 260.0, size=0.5, volume=0.4)
    L.update(god_rays([((-7.0, -2.0, 90.0), (-2.0, -9.0, 0.0), 4.0, 70000.0),
                       ((9.0, 30.0, 90.0), (2.5, 5.0, 0.0), 3.5, 60000.0),
                       ((-14.0, 40.0, 90.0), (-4.0, 26.0, 0.0), 3.0, 50000.0)]))
    L.update(horizon_glows())
    return L


def lights_god_reveal(cam=None, god=GOD_POS):
    """O5/O7/F2a/F3: cold blue underlight (shadowed, sculpts the face from below), a blue shaft from above
    (shadowed), cool rims behind the god, blue pool on the wet floor, ember horizon, god rays."""
    Gp = Vector(god)
    cam = Vector(cam) if cam is not None else Gp + Vector((0.4, -4.0, 0.3))
    L = {}
    L["under"] = _L("SPOT", "under", Gp + Vector((0.7, -3.1, 0.25)), BLUE, 2600.0, target=Gp + Vector((0, 0, 4.4)),
                    size=0.35, spot=55.0, blend=0.4, shadow=True, volume=0.6)
    L["top"] = _L("SPOT", "top", Gp + Vector((-3.0, 6.0, 34.0)), "#9CBEEB", 24000.0, target=Gp + Vector((0, 0, 3.2)),
                  size=0.8, spot=12.0, blend=0.25, shadow=True, volume=1.0)
    L["rimL"] = rim_light("rimL", Gp + Vector((0, 0, 4.2)), cam, "#CFE2FF", 2600.0, dist=4.5, height=3.0, side=3.0,
                          spot=35.0, volume=0.2)
    L["rimR"] = rim_light("rimR", Gp + Vector((0, 0, 4.2)), cam, "#9CC4FF", 2000.0, dist=4.5, height=2.0, side=-3.2,
                          spot=35.0, volume=0.2)
    L["pool"] = _L("POINT", "pool", Gp + Vector((0.0, -2.4, 0.35)), BLUE, 420.0, size=0.6, volume=0.5)
    L["key"] = _L("AREA", "key", Gp + Vector((-5.5, -6.0, 3.0)), BLUE_KEY, 900.0, target=Gp + Vector((0, 0, 3.5)),
                  size=4.0, volume=0.0)
    L.update(god_rays([((6.0, 34.0, 95.0), (1.5, 18.0, 0.0), 3.2, 65000.0),
                       ((-10.0, 40.0, 95.0), (-3.5, 22.0, 0.0), 2.8, 55000.0),
                       ((14.0, 10.0, 95.0), (5.0, 12.0, 0.0), 3.0, 40000.0)], color="#B4CBE6"))
    L.update(horizon_glows())
    return L


def lights_duel(warrior=(0.0, 8.8, 0.0), cam=None, god=GOD_POS):
    """O10-O12, F1, F2, F7: ember key from the warrior's side vs blue key from the god's side (the 2
    shadow casters), ember rim on the warrior and cold rims on the god (placed against `cam`),
    floor bounce, blue pool, ember horizon, god rays."""
    W, Gp = Vector(warrior), Vector(god)
    cam = Vector(cam) if cam is not None else W + Vector((-4.5, -8.0, 1.5))
    mid = (W + Gp) * 0.5
    L = {}
    L["ember_key"] = _L("SPOT", "ember_key", W + Vector((-6.0, -7.5, 8.0)), "#FF8236", 9000.0,
                        target=mid + Vector((0, -1.0, 1.6)), size=1.2, spot=42.0, blend=0.4, shadow=True, volume=0.5)
    L["blue_key"] = _L("SPOT", "blue_key", Gp + Vector((5.5, 4.0, 16.0)), "#7DA6E0", 16000.0,
                       target=mid + Vector((0, 1.0, 2.0)), size=1.0, spot=36.0, blend=0.35, shadow=True, volume=0.7)
    L["rim_w"] = rim_light("rim_w", W + Vector((0, 0, 1.3)), cam, EMBER, 700.0, dist=2.6, height=1.0, side=1.0)
    L["rim_g"] = rim_light("rim_g", Gp + Vector((0, 0, 4.0)), cam, "#BFD8FF", 2600.0, dist=4.5, height=2.5, side=2.5,
                           spot=35.0, volume=0.2)
    L["under"] = _L("SPOT", "under", Gp + Vector((0.6, -3.0, 0.25)), BLUE, 1400.0, target=Gp + Vector((0, 0, 4.2)),
                    size=0.35, spot=55.0, blend=0.4, volume=0.5)
    L["bounce"] = _L("AREA", "bounce", W + Vector((0, 0, 0.05)), EMBER, 60.0, size=4.0, volume=0.0, specular=0.2)
    L["bounce"].rotation_euler = (math.pi, 0, 0)
    L["pool"] = _L("POINT", "pool", Gp + Vector((0.0, -2.6, 0.35)), BLUE, 380.0, size=0.6, volume=0.5)
    L.update(god_rays([((-7.0, 2.0, 90.0), (-1.5, 6.0, 0.0), 3.5, 55000.0),
                       ((9.0, 34.0, 95.0), (2.0, 17.0, 0.0), 3.2, 60000.0),
                       ((-12.0, 42.0, 95.0), (-4.0, 25.0, 0.0), 2.8, 45000.0)]))
    L.update(horizon_glows())
    return L


def lights_after(warrior=(0.0, 8.5, 0.0), cam=None, god=GOD_POS):
    """E2: dim and ember. The cold light is gone; a single warm shaft from above (shadowed), the horizon
    fire brighter, faint blue from the dying halo shards, ember rim + bounce on the warrior."""
    W, Gp = Vector(warrior), Vector(god)
    cam = Vector(cam) if cam is not None else W + Vector((-3.0, -7.0, 4.0))
    L = {}
    L["top"] = _L("SPOT", "top", (W + Gp) * 0.5 + Vector((-5.0, 4.0, 38.0)), "#FFB27A", 15000.0,
                  target=(W + Gp) * 0.5 + Vector((0, 0, 0.5)), size=1.5, spot=16.0, blend=0.35, shadow=True,
                  volume=1.0)
    L["ember_fill"] = _L("SPOT", "ember_fill", W + Vector((-5.0, -6.0, 5.0)), "#FF7A2E", 2400.0,
                         target=W + Vector((0, 2.5, 0.8)), size=1.5, spot=55.0, blend=0.5, shadow=True, volume=0.4)
    L["rim_w"] = rim_light("rim_w", W + Vector((0, 0, 1.2)), cam, EMBER, 600.0, dist=2.6, height=1.0, side=1.0)
    L["bounce"] = _L("AREA", "bounce", W + Vector((0, 0, 0.05)), EMBER, 70.0, size=5.0, volume=0.0, specular=0.2)
    L["bounce"].rotation_euler = (math.pi, 0, 0)
    L["shards"] = _L("POINT", "shards", Vector(HALO_REST) + Vector((0, 0, 0.4)), BLUE, 120.0, size=1.0, volume=0.3)
    L.update(god_rays([((-6.0, 3.0, 90.0), (-1.0, 7.0, 0.0), 3.5, 35000.0),
                       ((10.0, 32.0, 95.0), (2.5, 16.0, 0.0), 3.0, 30000.0)], color="#E8C6A0"))
    L.update(horizon_glows(1.3))
    return L
