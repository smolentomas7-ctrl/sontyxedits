"""THE GATE OF HEAVEN + THE FLOWER MEADOW (shots E3, E4 — the true ending; the palette flips to peace).

E3  In the dark void of the arena a colossal free-standing gate of pale carved stone with restrained gold
    inlay stands on three broad steps; its two tall doors are partly open and warm white light (#FFF4DC)
    pours through the gap: a shadowed beam behind the gate shines ONLY through the door gap (an invisible
    shadow-caster wall surrounds the aperture), so the light lands as a long wedge across the dark, wet,
    cracked floor, cuts visible shafts through the haze and low ground mist, and throws the warrior's
    shadow back toward the camera. A soft volume-only halo glows around the arch (heaven beyond). Dust motes drift in the beam (frame-driven Geometry Nodes).
E4  Beyond the gate: a soft flower meadow on gentle rolling hills under a warm sky (#FFF4DC at the horizon
    to pale blue). Real instanced grass blades (tufts) that sway with a frame-driven breeze, instanced small
    flowers (white daisies, pale gold buttercups, a little soft pink), floating petals (frame-driven),
    a low warm sun (out of frame, right), valley mist and aerial perspective that fade the far hills into
    luminous haze. Meadow green #8DB580. The upper-middle of the frame is calm sky for the title.

LOCKED LAYOUT (metres, Z up, characters face -Y; heading 180 = facing +Y)
------------------------------------------------------------------------
 Gate (build_gate)
   floor            z = 0 (dark cracked wet stone, 400 x 400 m), ground mist up to ~2 m
   warrior mark     WARRIOR_GATE = (0, 0, 0), heading 180: he walks toward +Y, toward the gate
   gate             door plane y = GATE_Y (32), opening x = +-3.5, doors 12 m tall standing on the
                    landing at z = Z0 (0.6); three steps from y = 28.4; arch crown ~22 m
   doors            hinges at x = +-3.5, swing away from camera (+Y); CTRL_open 0..1 -> 0..80 deg
                    (default 0.45 = ~36 deg, ~1.3 m gap); light box (emissive) behind the doors
   beam             spot 14 m behind the gate, shadowed, its light leaves only through the gap
   marks            warrior, heading, cam (E3 tracking: 3.6 m behind, 1.45 m up), aim, gate, gap,
                    cam_gate / aim_gate (mid shot of the gate alone)
 Meadow (build_meadow)
   warrior mark     on a gentle knoll at (0, 0, ground_z(0, 0)), heading 180 (looking toward +Y)
   view             camera behind him looking +Y over the meadow: a broad valley at y 40-190, rolling
                    hills from y 110, a far ridge at y 330-520; sun low (12 deg) front-right, out of frame
   marks            warrior, heading, cam (pull-back start, 11.5 m behind), cam_far (19.5 m behind),
                    aim (far point that keeps the warrior in the lower-middle third), sun_dir
   instanced grass / flowers are dense only inside the +Y view wedge seen from cam / cam_far.

API
---
 build_gate(seed=0) -> Gate        (also sets the void world + EEVEE settings)
     .objects .doors [left, right] .mats {stone, gold, floor, light, mist, motes, rubble, occluder}
     .ctrls {'open': mat, 'light': mat}  -> rb_mat.key_ctrl(gate.ctrls['open'], 'open', frame, v)
     .key_ctrl(name, frame, value)      (same thing)   .marks (see above)   .lights (after lights_gate)
     CTRL_open (0..1 door opening, default 0.45), CTRL_light (light intensity multiplier, default 1):
     doors, beam, aura, bounce, light box and motes are all driven from them.
 lights_gate(gate, warrior=None, cam=None, follow=None) -> {name: light}
     beam (shadowed spot through the gap), aura (soft volume-only halo around the arch), bounce
     (warm up-light off the lit floor onto the gate face), front (faint cool fill), gate_rim (warm white
     rim on the warrior from the gate side) and ember (ember kicker on his side) — the last two parented
     to `follow` (warrior.root), call with the scene at a frame where he stands at `warrior`.
     1 shadow caster (the beam); a shot may add one more.
 build_meadow(seed=0) -> Meadow    (also sets the sky world + EEVEE settings)
     .objects .mats .marks .ground_z(x, y) .grass .flowers .petals .terrain .world
 lights_meadow(meadow, warrior=None, cam=None, follow=None) -> {name: light}
     sun (the one shadow caster), ember-gold rims on the warrior (parented to `follow`), soft fill.
 tune_gate(scene) / tune_meadow(scene): EEVEE settings each set relies on (called by the builders).
Everything is deterministic: seeded generators, and motion (motes, petals, grass sway, mist drift) is a pure
function of the scene time (Geometry Nodes Scene Time / linear CTRL_time keys).
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import rb_core as C
import rb_env_arena as AR
import rb_env_forest as FO
import rb_mat as M
from rb_core import hexcol, link

HEAVEN = "#FFF4DC"
MEADOW = "#8DB580"
EMBER = "#FF6A1A"
GATE_Y = 32.0
Z0 = 0.6
HW = 3.5            # half opening width
DH = 12.0           # door height
DT = 0.45           # door thickness
JW = 2.2            # jamb width
JD = 1.4            # jamb half depth
ZE = Z0 + DH + 2.75  # arch springing line (top of cornice)
OPEN_MAX = math.radians(80.0)
OPEN0 = 0.45
WARRIOR_GATE = (0.0, 0.0, 0.0)
SUN_DIR = Vector((0.5 * math.cos(math.radians(12)), 0.866 * math.cos(math.radians(12)),
                  math.sin(math.radians(12)))).normalized()


# =================================================================== small helpers
def _lin(h):
    return hexcol(h)


def _sock(socks, name, typ):
    for s in socks:
        if s.name == name and s.type == typ:
            return s
    raise KeyError(name)


def _mr(b, v, f0, f1, t0=0.0, t1=1.0, clamp=True):
    node = b.n("ShaderNodeMapRange", Value=v, **{"From Min": f0, "From Max": f1, "To Min": t0, "To Max": t1})
    node.clamp = clamp
    return node


def _noise(b, vec, scale, detail=4.0, rough=0.55):
    return b.n("ShaderNodeTexNoise", Vector=vec, Scale=scale, Detail=detail, Roughness=rough)


def _pos(b):
    return (b.n("ShaderNodeNewGeometry"), "Position")


def _mapv(b, vec, scale=(1, 1, 1), loc=(0, 0, 0)):
    return b.n("ShaderNodeMapping", Vector=vec, Scale=scale, Location=loc)


def _sep(b, v):
    return b.n("ShaderNodeSeparateXYZ", Vector=v)


def _key_time(mat, node):
    """CTRL_time = frame / fps on every frame (2 linear keys + linear extrapolation)."""
    sock = node.outputs[0]
    for f, v in ((0, 0.0), (C.FPS, 1.0)):
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=f)
    ad = mat.node_tree.animation_data
    for fc in ad.action.fcurves:
        if node.name in fc.data_path:
            fc.extrapolation = "LINEAR"
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
    return mat


def _drive(owner, path, ctrl_mat, ctrl, expr, index=-1):
    """Simple-expression driver (no Python needed) reading CTRL_<ctrl> of ctrl_mat as variable `c`."""
    fc = owner.driver_add(path, index) if index >= 0 else owner.driver_add(path)
    d = fc.driver
    d.type = "SCRIPTED"
    v = d.variables.new()
    v.name = "c"
    v.type = "SINGLE_PROP"
    v.targets[0].id_type = "MATERIAL"
    v.targets[0].id = ctrl_mat
    v.targets[0].data_path = 'node_tree.nodes["CTRL_%s"].outputs[0].default_value' % ctrl
    d.expression = expr
    return fc


def _L(kind, name, loc, color, energy, target=None, size=0.3, shadow=False, spot=45.0, blend=0.3, volume=1.0,
       specular=1.0, diffuse=1.0, cutoff=None, prefix="HEAVEN_"):
    ob = C.light(kind, prefix + name, tuple(loc), color=color, energy=energy, size=size, target=target,
                 shadow=shadow, spot_size=math.radians(spot), blend=blend, volume=volume, specular=specular)
    ob.data.diffuse_factor = diffuse
    if cutoff:
        ob.data.use_custom_distance = True
        ob.data.cutoff_distance = cutoff
    if shadow and kind != "SUN":
        ob.data.shadow_buffer_bias = 0.02
        ob.data.shadow_buffer_clip_start = 0.4
    return ob


# =================================================================== mesh accumulator
CUBE_F = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (3, 0, 4, 7), (1, 2, 6, 5))


class _Acc:
    """Collects vertices / faces / per-face material slot / per-vertex UV; builds one object."""

    def __init__(self):
        self.V, self.UV, self.F, self.Fm = [], [], [], []
        self.n = 0

    def add(self, verts, faces, mat=0, uv=None):
        verts = np.asarray(verts, float).reshape(-1, 3)
        self.V.append(verts)
        self.UV.append(np.zeros((len(verts), 2)) if uv is None else np.asarray(uv, float).reshape(-1, 2))
        for f in faces:
            self.F.append([i + self.n for i in f])
            self.Fm.append(mat)
        self.n += len(verts)

    def hexa(self, P, mat=0, xf=None):
        P = np.asarray(P, float)
        if xf is not None:
            P = np.array([tuple(xf @ Vector(p)) for p in P])
        self.add(P, CUBE_F, mat)

    def box(self, lo, hi, mat=0, xf=None):
        x0, y0, z0 = lo
        x1, y1, z1 = hi
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        z0, z1 = min(z0, z1), max(z0, z1)
        self.hexa([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                   (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], mat, xf)

    def arc(self, cx, cz, r0, r1, y0, y1, a0, a1, n, mat=0, xf=None):
        """Annular sector in the XZ plane (angles from +X toward +Z) extruded along Y; closed (end caps)."""
        P = []
        for i in range(n + 1):
            a = a0 + (a1 - a0) * i / n
            ca, sa = math.cos(a), math.sin(a)
            P += [(cx + r1 * ca, y0, cz + r1 * sa), (cx + r0 * ca, y0, cz + r0 * sa),
                  (cx + r0 * ca, y1, cz + r0 * sa), (cx + r1 * ca, y1, cz + r1 * sa)]
        F = []
        for i in range(n):
            a, b = 4 * i, 4 * (i + 1)
            for k in range(4):
                F.append((a + k, a + (k + 1) % 4, b + (k + 1) % 4, b + k))
        full = abs(abs(a1 - a0) - 2 * math.pi) < 1e-6
        if not full:
            F.append((0, 1, 2, 3))
            F.append((4 * n + 3, 4 * n + 2, 4 * n + 1, 4 * n))
        P = np.asarray(P)
        if xf is not None:
            P = np.array([tuple(xf @ Vector(p)) for p in P])
        self.add(P, F, mat)

    def disc_y(self, cx, cz, r, y0, y1, n=20, mat=0, xf=None):
        """Short cylinder along Y (rosettes, studs)."""
        P = []
        for y in (y0, y1):
            for i in range(n):
                a = 2 * math.pi * i / n
                P.append((cx + r * math.cos(a), y, cz + r * math.sin(a)))
        F = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        F += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        P = np.asarray(P)
        if xf is not None:
            P = np.array([tuple(xf @ Vector(p)) for p in P])
        self.add(P, F, mat)

    def build(self, name, mats, smooth=True, auto=35.0, recalc=True, link_scene=True):
        V = np.concatenate(self.V)
        UV = np.concatenate(self.UV)
        me = bpy.data.meshes.new(name)
        me.from_pydata(V.tolist(), [], self.F)
        loops = np.array([i for f in self.F for i in f], np.int64)
        uvl = me.uv_layers.new(name="UVMap")
        uvl.data.foreach_set("uv", UV[loops].astype(np.float32).ravel())
        for m in mats:
            me.materials.append(m)
        me.polygons.foreach_set("material_index", np.array(self.Fm, np.int32))
        me.polygons.foreach_set("use_smooth", np.full(len(self.F), smooth))
        if auto:
            me.use_auto_smooth = True
            me.auto_smooth_angle = math.radians(auto)
        if recalc:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(me)
            bm.free()
        me.update()
        ob = bpy.data.objects.new(name, me)
        if link_scene:
            link(ob)
        return ob


def _bevel(ob, width=0.035, segments=2, angle=35.0):
    md = ob.modifiers.new("bevel", "BEVEL")
    md.width = width
    md.segments = segments
    md.limit_method = "ANGLE"
    md.angle_limit = math.radians(angle)
    md.harden_normals = True
    md.miter_outer = "MITER_ARC"
    return md


# =================================================================== materials (gate)
def mat_stone(name="heaven_stone", base=(0.60, 0.565, 0.50), dark=0.62, rough=0.6, ao=True):
    """Pale carved stone: large tone patches, vertical weathering streaks, chipped pitting, cavity grime
    (AO), fine grain bump."""
    m, b = M.new(name)
    p = _pos(b)
    n1 = _noise(b, p, 0.22, 5.0, 0.6)
    streak = _noise(b, _mapv(b, p, (2.2, 2.2, 0.18)), 1.0, 6.0, 0.6)
    pit = b.n("ShaderNodeTexVoronoi", Vector=p, Scale=7.0)
    grain = _noise(b, p, 38.0, 8.0, 0.6)
    c0 = b.mix(_mr(b, (n1, "Fac"), 0.35, 0.65), tuple(v * 0.86 for v in base), base)
    c1 = b.mix(_mr(b, (streak, "Fac"), 0.5, 0.72, 0.0, 0.55), c0, tuple(v * dark for v in base))
    col = c1
    if ao:
        aon = b.n("ShaderNodeAmbientOcclusion", Distance=0.6)
        col = b.mix(_mr(b, (aon, "AO"), 0.2, 1.0, 1.0, 0.0), col, tuple(v * 0.32 for v in base), "MIX")
    h = b.math("ADD", b.math("MULTIPLY", (grain, "Fac"), 0.5),
               b.math("MULTIPLY", _mr(b, (pit, "Distance"), 0.0, 0.12, -1.0, 0.0), 0.6))
    bump = b.n("ShaderNodeBump", Strength=0.35, Distance=0.01, Height=h)
    r = _mr(b, (grain, "Fac"), 0.3, 0.7, rough - 0.08, rough + 0.12)
    bs = b.bsdf(**{"Base Color": col, "Roughness": r, "Specular IOR Level": 0.45, "Normal": bump})
    b.out(bs)
    return m


def mat_gold(name="heaven_gold"):
    """Restrained cast-gold inlay: pale warm gold, soft tarnish in the low spots, worn bright on edges."""
    m, b = M.new(name)
    p = _pos(b)
    n1 = _noise(b, p, 3.0, 5.0, 0.6)
    fine = _noise(b, p, 60.0, 4.0, 0.5)
    col = b.mix(_mr(b, (n1, "Fac"), 0.45, 0.7), (0.80, 0.56, 0.24), (0.50, 0.33, 0.12))
    r = _mr(b, (n1, "Fac"), 0.3, 0.7, 0.22, 0.42)
    bump = b.n("ShaderNodeBump", Strength=0.15, Distance=0.005, Height=(fine, "Fac"))
    bs = b.bsdf(**{"Base Color": col, "Metallic": 1.0, "Roughness": r, "Normal": bump})
    b.out(bs)
    return m


def mat_floor(name="heaven_floor"):
    """Dark wet cracked flagstones: Voronoi slabs with grooves, a warped crack network, puddles (glossy,
    mirror the gate light through SSR), per-slab tone."""
    m, b = M.new(name)
    p = _pos(b)
    warp = _noise(b, p, 0.5, 3.0, 0.5)
    pw = b.n("ShaderNodeVectorMath", _operation="ADD")
    b._in(pw, 0, p)
    b._in(pw, 1, (b.n("ShaderNodeVectorMath", _operation="SCALE", Vector=(warp, "Color"), Scale=0.35), 0))
    slab = b.n("ShaderNodeTexVoronoi", Vector=(pw, 0), Scale=0.36, _feature="DISTANCE_TO_EDGE")
    slabc = b.n("ShaderNodeTexVoronoi", Vector=(pw, 0), Scale=0.36)
    groove = _mr(b, (slab, "Distance"), 0.012, 0.045, 1.0, 0.0)
    w2 = _noise(b, p, 1.6, 3.0, 0.6)
    pc = b.n("ShaderNodeVectorMath", _operation="ADD")
    b._in(pc, 0, p)
    b._in(pc, 1, (b.n("ShaderNodeVectorMath", _operation="SCALE", Vector=(w2, "Color"), Scale=0.5), 0))
    crk = b.n("ShaderNodeTexVoronoi", Vector=(pc, 0), Scale=1.25, _feature="DISTANCE_TO_EDGE")
    cmask = _mr(b, (_noise(b, p, 0.22, 2.0, 0.5), "Fac"), 0.48, 0.6)
    crack = b.math("MULTIPLY", _mr(b, (crk, "Distance"), 0.004, 0.016, 1.0, 0.0), cmask)
    cut = b.math("MAXIMUM", groove, crack)
    tone = _mr(b, (b.n("ShaderNodeSeparateColor", Color=(slabc, "Color")), 0), 0.0, 1.0, 0.65, 1.35)
    grain = _noise(b, p, 9.0, 6.0, 0.6)
    base = b.mix(_mr(b, (grain, "Fac"), 0.3, 0.7), (0.020, 0.022, 0.024), (0.045, 0.046, 0.047))
    base = b.mix(1.0, base, tone, "MULTIPLY")
    col = b.mix(cut, base, (0.006, 0.006, 0.007))
    wet = _mr(b, (_noise(b, p, 0.09, 3.0, 0.55), "Fac"), 0.47, 0.56)
    r = b.math("ADD", b.math("MULTIPLY", wet, -0.5), 0.6)
    r = b.math("MAXIMUM", r, b.math("MULTIPLY", cut, 0.55))
    h = b.math("ADD", b.math("MULTIPLY", cut, -1.0), b.math("MULTIPLY", (grain, "Fac"), b.math("SUBTRACT", 1.0, wet)))
    bump = b.n("ShaderNodeBump", Strength=0.3, Distance=0.012, Height=h)
    bs = b.bsdf(**{"Base Color": col, "Roughness": r, "Specular IOR Level": 0.55, "Normal": bump})
    b.out(bs)
    return m


def mat_light(name="heaven_light"):
    """The light beyond the gate (emissive light box). Holds the gate's animated controls CTRL_open and
    CTRL_light (everything else is driven from these two)."""
    m, b = M.new(name)
    m.shadow_method = "NONE"
    b.ctrl("open", OPEN0)
    k = b.ctrl("light", 1.0)
    p = _pos(b)
    nz = _noise(b, _mapv(b, p, (0.6, 0.6, 0.25)), 0.5, 3.0, 0.5)
    s = b.math("MULTIPLY", k, _mr(b, (nz, "Fac"), 0.3, 0.7, 22.0, 34.0))
    em = b.n("ShaderNodeEmission", Color=_lin(HEAVEN), Strength=s)
    b.out(em)
    return m


def mat_occluder(name="heaven_occluder"):
    """Invisible to the camera, casts full shadows (keeps the beam inside the door gap)."""
    m, b = M.new(name, "CLIP")
    m.shadow_method = "OPAQUE"
    tr = b.n("ShaderNodeBsdfTransparent")
    b.out(tr)
    return m


def mat_fog(name, density, height, color, anisotropy=0.4, scale=0.12, wind=(0.12, 0.05, 0.0), z0=0.0,
            contrast=(0.35, 0.7, 0.15, 1.25)):
    """Ground / valley mist: density falls off above z0 over `height`, drifting noise (CTRL_time)."""
    m, b = M.new(name)
    p = _pos(b)
    t = b.ctrl("time", 0.0)
    off = b.n("ShaderNodeCombineXYZ", X=b.math("MULTIPLY", t, wind[0]), Y=b.math("MULTIPLY", t, wind[1]),
              Z=b.math("MULTIPLY", t, wind[2]))
    pv = b.n("ShaderNodeVectorMath", _operation="ADD")
    b._in(pv, 0, p)
    b._in(pv, 1, (off, 0))
    nz = _noise(b, (pv, 0), scale, 3.0, 0.55)
    z = (_sep(b, p), "Z")
    hm = _mr(b, z, z0, z0 + height, 1.0, 0.0)
    hm = b.math("POWER", hm, 1.6)
    d = b.ctrl("density", density)
    dens = b.math("MULTIPLY", b.math("MULTIPLY", d, hm), _mr(b, (nz, "Fac"), *contrast))
    vol = b.n("ShaderNodeVolumePrincipled", Color=color, Density=dens, Anisotropy=anisotropy)
    b.out(volume=vol)
    return _key_time(m, t)


def mat_motes(name, gap_half=0.75):
    """Dust motes: warm emissive specks, bright inside the beam wedge (computed from world position: the
    beam leaves the gap from a source 14 m behind the gate), dim outside; seeded twinkle (attr phase)."""
    m, b = M.new(name)
    m.shadow_method = "NONE"
    p = _pos(b)
    sp = _sep(b, p)
    t = b.ctrl("time", 0.0)
    k = b.ctrl("light", 1.0)
    dist = b.math("SUBTRACT", GATE_Y + 14.0, (sp, "Y"))
    w = b.math("ADD", b.math("MULTIPLY", dist, gap_half / 12.0), 0.25)
    ax = b.math("ABSOLUTE", (sp, "X"))
    inb = _mr(b, b.math("DIVIDE", ax, w), 0.55, 1.15, 1.0, 0.0)
    near_gate = _mr(b, (sp, "Y"), GATE_Y - 26.0, GATE_Y - 2.0, 0.6, 1.4)
    ph = b.attr("phase")
    tw = b.n("ShaderNodeMath", _operation="SINE")
    b._in(tw, 0, b.math("ADD", b.math("MULTIPLY", t, 2.1), b.math("MULTIPLY", ph, 61.0)))
    twk = _mr(b, tw, -1.0, 1.0, 0.45, 1.0)
    s = b.math("MULTIPLY", b.math("MULTIPLY", b.math("ADD", b.math("MULTIPLY", inb, 5.0), 0.03), twk),
               b.math("MULTIPLY", near_gate, k))
    em = b.n("ShaderNodeEmission", Color=_lin("#FFE9C4"), Strength=s)
    b.out(em)
    return _key_time(m, t)


# =================================================================== geometry nodes
def _gn_new(name):
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    return ng


class _G:
    """Tiny GN builder (math on sockets / constants)."""

    def __init__(self, ng):
        self.ng, self.N, self.Lk = ng, ng.nodes, ng.links.new

    def inp(self, node, i, v):
        if isinstance(v, (int, float)):
            node.inputs[i].default_value = v
        elif isinstance(v, tuple):
            node.inputs[i].default_value = v
        else:
            self.Lk(v, node.inputs[i])

    def m(self, op, a, c=None):
        n = self.N.new("ShaderNodeMath")
        n.operation = op
        self.inp(n, 0, a)
        if c is not None:
            self.inp(n, 1, c)
        return n.outputs[0]

    def vm(self, op, a, c=None, s=None):
        n = self.N.new("ShaderNodeVectorMath")
        n.operation = op
        self.inp(n, 0, a)
        if c is not None:
            self.inp(n, 1, c)
        if s is not None:
            self.inp(n, 3, s)
        return n.outputs[0]

    def xyz(self, x, y, z):
        n = self.N.new("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)):
            self.inp(n, i, v)
        return n.outputs[0]

    def attr(self, nm, vec=False, typ=None):
        n = self.N.new("GeometryNodeInputNamedAttribute")
        n.data_type = typ or ("FLOAT_VECTOR" if vec else "FLOAT")
        n.inputs["Name"].default_value = nm
        st = {"FLOAT_VECTOR": "VECTOR", "FLOAT": "VALUE", "INT": "INT"}[n.data_type]
        return _sock(n.outputs, "Attribute", st)

    def link_rot(self, vec, sock):
        """Euler vector -> rotation socket (4.0 may use a ROTATION socket type)."""
        if sock.type == "ROTATION":
            try:
                e2r = self.N.new("FunctionNodeEulerToRotation")
                self.Lk(vec, e2r.inputs[0])
                self.Lk(e2r.outputs[0], sock)
                return
            except RuntimeError:
                pass
        self.Lk(vec, sock)


def _drift_tree(name, shape, mat):
    """Points carry phase / spd / len / sz / sway / sfq and vectors dir / spin. Each frame (Scene Time t):
    life = fract(phase + t*spd/len); the point slides along dir by len*(life-0.5) with a lazy sway, the
    shape is instanced with tumbling rotation spin*(t + 20*phase) and grows in / dies out with life (so
    the wrap is invisible). Pure function of the frame."""
    ng = _gn_new(name)
    g = _G(ng)
    gi, go = g.N.new("NodeGroupInput"), g.N.new("NodeGroupOutput")
    t = g.N.new("GeometryNodeInputSceneTime").outputs["Seconds"]
    ph, spd, ln, sz, sw, sfq = (g.attr(k) for k in ("phase", "spd", "len", "sz", "sway", "sfq"))
    dr, spin = g.attr("dir", True), g.attr("spin", True)
    life = g.m("FRACT", g.m("ADD", ph, g.m("DIVIDE", g.m("MULTIPLY", t, spd), ln)))
    off = g.vm("SCALE", dr, s=g.m("MULTIPLY", g.m("SUBTRACT", life, 0.5), ln))
    ts = g.m("MULTIPLY", t, sfq)
    sx = g.m("SINE", g.m("ADD", g.m("MULTIPLY", ts, 1.3), g.m("MULTIPLY", ph, 40.0)))
    sy = g.m("COSINE", g.m("ADD", g.m("MULTIPLY", ts, 0.9), g.m("MULTIPLY", ph, 23.0)))
    sz2 = g.m("MULTIPLY", g.m("SINE", g.m("ADD", g.m("MULTIPLY", ts, 1.7), g.m("MULTIPLY", ph, 11.0))), 0.6)
    tot = g.vm("ADD", off, g.vm("SCALE", g.xyz(sx, sy, sz2), s=sw))
    sp = g.N.new("GeometryNodeSetPosition")
    g.Lk(gi.outputs[0], sp.inputs["Geometry"])
    g.Lk(tot, sp.inputs["Offset"])
    rot = g.vm("SCALE", spin, s=g.m("ADD", t, g.m("MULTIPLY", ph, 20.0)))
    grow = g.m("MINIMUM", g.m("MULTIPLY", life, 8.0), 1.0)
    die = g.m("MINIMUM", g.m("MULTIPLY", g.m("SUBTRACT", 1.0, life), 8.0), 1.0)
    scl = g.m("MULTIPLY", sz, g.m("MULTIPLY", grow, die))
    oi = g.N.new("GeometryNodeObjectInfo")
    oi.inputs["Object"].default_value = shape
    iop = g.N.new("GeometryNodeInstanceOnPoints")
    g.Lk(sp.outputs[0], iop.inputs["Points"])
    g.Lk(oi.outputs["Geometry"], iop.inputs["Instance"])
    g.link_rot(rot, iop.inputs["Rotation"])
    g.Lk(scl, iop.inputs["Scale"])
    real = g.N.new("GeometryNodeRealizeInstances")
    g.Lk(iop.outputs[0], real.inputs[0])
    sm = g.N.new("GeometryNodeSetMaterial")
    sm.inputs["Material"].default_value = mat
    g.Lk(real.outputs[0], sm.inputs["Geometry"])
    g.Lk(sm.outputs[0], go.inputs[0])
    return ng


def _scatter_tree(name, coll, sway=(0.0, 0.0)):
    """Instance the children of `coll` on the points: attr idx picks the child, rot (euler) / scl place it;
    optional frame-driven breeze: extra tilt sway[0]*sin(1.4 t + 0.3 x + 0.17 y), sway[1]*sin(1.9 t + 0.23 y)."""
    ng = _gn_new(name)
    g = _G(ng)
    gi, go = g.N.new("NodeGroupInput"), g.N.new("NodeGroupOutput")
    ci = g.N.new("GeometryNodeCollectionInfo")
    ci.transform_space = "ORIGINAL"
    ci.inputs["Collection"].default_value = coll
    ci.inputs["Separate Children"].default_value = True
    ci.inputs["Reset Children"].default_value = True
    rot = g.attr("rot", True)
    if sway[0] or sway[1]:
        t = g.N.new("GeometryNodeInputSceneTime").outputs["Seconds"]
        ps = g.N.new("ShaderNodeSeparateXYZ")
        g.Lk(g.N.new("GeometryNodeInputPosition").outputs[0], ps.inputs[0])
        a = g.m("SINE", g.m("ADD", g.m("MULTIPLY", t, 1.4), g.m("ADD", g.m("MULTIPLY", ps.outputs[0], 0.3),
                                                                  g.m("MULTIPLY", ps.outputs[1], 0.17))))
        c = g.m("SINE", g.m("ADD", g.m("MULTIPLY", t, 1.9), g.m("MULTIPLY", ps.outputs[1], 0.23)))
        rot = g.vm("ADD", rot, g.xyz(g.m("MULTIPLY", a, sway[0]), g.m("MULTIPLY", c, sway[1]), 0.0))
    iop = g.N.new("GeometryNodeInstanceOnPoints")
    g.Lk(gi.outputs[0], iop.inputs["Points"])
    g.Lk(ci.outputs[0], iop.inputs["Instance"])
    iop.inputs["Pick Instance"].default_value = True
    g.Lk(g.attr("idx", typ="INT"), iop.inputs["Instance Index"])
    g.link_rot(rot, iop.inputs["Rotation"])
    g.Lk(g.attr("scl"), iop.inputs["Scale"])
    g.Lk(iop.outputs[0], go.inputs[0])
    return ng


def _points(name, P, attrs):
    """Vertex-only mesh object with point attributes {name: (n,) float | (n,3) vector | ('INT', (n,))}."""
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(P))
    me.vertices.foreach_set("co", np.asarray(P, np.float32).ravel())
    for k, v in attrs.items():
        if isinstance(v, tuple) and v[0] == "INT":
            me.attributes.new(k, "INT", "POINT").data.foreach_set("value", np.asarray(v[1], np.int32))
            continue
        a = np.asarray(v, np.float32)
        if a.ndim == 2:
            me.attributes.new(k, "FLOAT_VECTOR", "POINT").data.foreach_set("vector", a.ravel())
        else:
            me.attributes.new(k, "FLOAT", "POINT").data.foreach_set("value", a)
    me.update()
    ob = bpy.data.objects.new(name, me)
    link(ob)
    return ob


def _shape(name, V, F, mats=(), uv=None):
    """Mesh object NOT linked to the scene (instance source for Geometry Nodes)."""
    acc = _Acc()
    acc.add(V, F, 0, uv)
    ob = acc.build(name, mats, smooth=True, auto=None, recalc=False, link_scene=False)
    return ob


# =================================================================== handles
class Gate:
    """Handles of the Gate of Heaven set (see module docstring)."""

    def __init__(self, seed):
        self.seed = seed
        self.objects, self.doors = [], []
        self.mats, self.ctrls, self.lights, self.marks = {}, {}, {}, {}
        self.world = None

    def key_ctrl(self, name, frame, value):
        """Key CTRL_<name> ('open' 0..1, 'light' multiplier) at `frame`."""
        M.key_ctrl(self.ctrls[name], name, frame, value)

    def door_angle(self, open_value):
        return open_value * OPEN_MAX


class Meadow:
    """Handles of the heaven meadow set (see module docstring)."""

    def __init__(self, seed):
        self.seed = seed
        self.objects, self.mats, self.lights, self.marks, self.ctrls = [], {}, {}, {}, {}
        self.world = self.terrain = self.grass = self.flowers = self.petals = None
        self.h = lambda X, Y: np.zeros(np.shape(X))

    def ground_z(self, x, y):
        """Terrain height (m) at world (x, y) — the same function the ground mesh / grass were built from."""
        return float(np.asarray(self.h(np.array([[float(x)]]), np.array([[float(y)]])))[0, 0])


# =================================================================== E3 — world / eevee
def world_void(density=0.005, color=(0.93, 0.89, 0.82), anisotropy=0.62):
    """Teal-black void with a thin warm haze (forward-scattering, so shafts read toward the light).
    CTRL_fog = uniform volume density."""
    w = bpy.data.worlds.new("HEAVEN_void")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.0016, 0.0020, 0.0024, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    fog = nt.nodes.new("ShaderNodeValue")
    fog.name, fog.label = "CTRL_fog", "fog"
    fog.outputs[0].default_value = density
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = (*color, 1.0)
    pv.inputs["Anisotropy"].default_value = anisotropy
    nt.links.new(fog.outputs[0], pv.inputs["Density"])
    nt.links.new(pv.outputs[0], out.inputs["Volume"])
    return w


def tune_gate(sc=None):
    """EEVEE settings the gate set relies on (bloom on the light, SSR on the wet floor, volumetric shafts)."""
    sc = sc or bpy.context.scene
    e = sc.eevee
    e.use_bloom = True
    e.bloom_intensity = 0.09
    e.bloom_threshold = 0.95
    e.bloom_radius = 6.5
    e.bloom_knee = 0.55
    e.bloom_color = (1.0, 0.93, 0.82)
    e.use_ssr = True
    e.ssr_max_roughness = 0.45
    e.ssr_thickness = 0.4
    e.ssr_border_fade = 0.06
    e.ssr_firefly_fac = 5.0
    e.use_ssr_halfres = True
    e.use_gtao = True
    e.gtao_distance = 0.8
    e.volumetric_start = 0.1
    e.volumetric_end = 110.0
    e.volumetric_tile_size = "8"
    e.volumetric_samples = 64
    e.volumetric_sample_distribution = 0.8
    e.use_volumetric_lights = True
    e.use_volumetric_shadows = True
    e.volumetric_shadow_samples = 16
    e.use_soft_shadows = True
    e.shadow_cube_size = "1024"
    e.shadow_cascade_size = "2048"
    e.light_threshold = 0.01
    return sc


# =================================================================== E3 — geometry
def _jamb(acc, s, rnd):
    """One pilaster (s = -1 left, +1 right): plinth, panelled shaft with a gold inlay frame and a column
    of carved rosettes, stepped capital with a gold band."""
    def X(a, c):
        return (s * a, s * c)

    y_f = GATE_Y - JD
    za, zb = Z0 + 1.5, Z0 + DH - 0.4
    xa, xb = X(HW - 0.08, HW + JW + 0.3)
    acc.box((xa, GATE_Y - JD - 0.3, Z0), (xb, GATE_Y + JD + 0.2, Z0 + 1.3))
    xa, xb = X(HW - 0.04, HW + JW + 0.2)
    acc.box((xa, GATE_Y - JD - 0.2, Z0 + 1.3), (xb, GATE_Y + JD + 0.1, Z0 + 1.5))
    xa, xb = X(HW + 0.1, HW + JW + 0.1)
    acc.box((xa, GATE_Y - JD - 0.34, Z0 + 0.92), (xb, GATE_Y - JD - 0.28, Z0 + 1.0), 1)
    xa, xb = X(HW, HW + JW)
    acc.box((xa, GATE_Y - JD, za), (xb, GATE_Y + JD, zb))
    # raised frame (stiles + rails) around a recessed field
    for a, c in ((HW, HW + 0.32), (HW + JW - 0.32, HW + JW)):
        xa, xb = X(a, c)
        acc.box((xa, y_f - 0.12, za), (xb, y_f, zb))
    for z0, z1 in ((za, za + 0.35), (zb - 0.35, zb)):
        xa, xb = X(HW + 0.32, HW + JW - 0.32)
        acc.box((xa, y_f - 0.12, z0), (xb, y_f, z1))
    # gold inlay rectangle inside the field
    fx0, fx1, fz0, fz1 = HW + 0.32 + 0.13, HW + JW - 0.32 - 0.13, za + 0.35 + 0.13, zb - 0.35 - 0.13
    for a, c in ((fx0, fx0 + 0.05), (fx1 - 0.05, fx1)):
        xa, xb = X(a, c)
        acc.box((xa, y_f - 0.025, fz0), (xb, y_f, fz1), 1)
    for z0, z1 in ((fz0, fz0 + 0.05), (fz1 - 0.05, fz1)):
        xa, xb = X(fx0, fx1)
        acc.box((xa, y_f - 0.025, z0), (xb, y_f, z1), 1)
    # rosettes + diamonds down the field
    xc = s * (HW + JW / 2)
    zs = np.linspace(fz0 + 1.0, fz1 - 1.0, 5)
    for i, z in enumerate(zs):
        acc.disc_y(xc, z, 0.36, y_f - 0.11, y_f, 24)
        acc.disc_y(xc, z, 0.26, y_f - 0.16, y_f - 0.1, 24)
        for k in range(8):
            a = k * math.pi / 4
            xf = Matrix.Translation((xc, 0, z)) @ Matrix.Rotation(-a, 4, "Y")
            acc.box((0.27, y_f - 0.13, -0.035), (0.4, y_f - 0.08, 0.035), 0, xf)
        acc.disc_y(xc, z, 0.085, y_f - 0.2, y_f - 0.15, 16, 1)
        if i < len(zs) - 1:
            zm = 0.5 * (z + zs[i + 1])
            xf = Matrix.Translation((xc, 0, zm)) @ Matrix.Rotation(math.radians(45), 4, "Y")
            acc.box((-0.17, y_f - 0.08, -0.17), (0.17, y_f, 0.17), 0, xf)
    # capital
    for (a, c, y0, z0, z1, mt) in ((HW - 0.05, HW + JW + 0.05, JD + 0.12, zb, zb + 0.3, 0),
                                   (HW - 0.15, HW + JW + 0.15, JD + 0.28, zb + 0.3, zb + 0.66, 0),
                                   (HW - 0.17, HW + JW + 0.17, JD + 0.31, zb + 0.66, zb + 0.73, 1),
                                   (HW - 0.27, HW + JW + 0.27, JD + 0.45, zb + 0.73, zb + 1.2, 0)):
        xa, xb = X(a, c)
        acc.box((xa, GATE_Y - y0, z0), (xb, GATE_Y + JD + 0.1, z1), mt)


def _arch(acc, rnd):
    """Entablature, cornice, archivolt rings, tympanum with a gold sunburst, keystone."""
    zl = Z0 + DH + 0.8
    acc.box((-HW - JW - 0.3, GATE_Y - 1.6, zl), (HW + JW + 0.3, GATE_Y + 1.5, ZE - 0.55))
    acc.box((-HW - JW - 0.2, GATE_Y - 1.72, zl), (HW + JW + 0.2, GATE_Y - 1.6, zl + 0.3))
    acc.box((-HW - JW, GATE_Y - 1.64, ZE - 0.97), (HW + JW, GATE_Y - 1.6, ZE - 0.92), 1)
    for k in range(9):
        x = -5.0 + 1.25 * k
        acc.disc_y(x, zl + 0.82, 0.17, GATE_Y - 1.7, GATE_Y - 1.6, 18, 1 if k % 2 == 0 else 0)
    acc.box((-6.3, GATE_Y - 1.95, ZE - 0.55), (6.3, GATE_Y + 1.7, ZE - 0.3))
    acc.box((-6.5, GATE_Y - 2.15, ZE - 0.3), (6.5, GATE_Y + 1.85, ZE))
    pi = math.pi
    acc.arc(0.0, ZE, 0.0, 4.0, GATE_Y - 0.5, GATE_Y + 0.9, 0.0, pi, 48)
    acc.arc(0.0, ZE, 4.0, 4.55, GATE_Y - 1.0, GATE_Y + 1.0, 0.0, pi, 64)
    acc.arc(0.0, ZE, 4.55, 4.63, GATE_Y - 1.1, GATE_Y + 0.9, 0.0, pi, 64, 1)
    acc.arc(0.0, ZE, 4.63, 5.35, GATE_Y - 1.35, GATE_Y + 1.2, 0.0, pi, 72)
    acc.arc(0.0, ZE, 5.35, 5.9, GATE_Y - 1.1, GATE_Y + 1.0, 0.0, pi, 72)
    # voussoir joints on the outer ring (shallow gold-free grooves read as blocks: thin stone ribs)
    for k in range(1, 15):
        a = pi * k / 15
        xf = Matrix.Translation((0, 0, ZE)) @ Matrix.Rotation(-a, 4, "Y")
        acc.box((4.66, GATE_Y - 1.39, -0.025), (5.32, GATE_Y - 1.34, 0.025), 0, xf)
    # sunburst
    acc.arc(0.0, ZE, 0.0, 0.85, GATE_Y - 0.58, GATE_Y - 0.5, 0.0, pi, 32, 1)
    acc.arc(0.0, ZE, 0.95, 1.01, GATE_Y - 0.56, GATE_Y - 0.5, 0.0, pi, 40, 1)
    nr = 13
    for k in range(nr):
        a = pi * (k + 0.5) / nr
        r0, r1 = 1.12, (3.7 if k % 2 == 0 else 2.75)
        w0, w1 = 0.085, 0.018
        y0, y1 = GATE_Y - 0.56, GATE_Y - 0.5
        P = [(r0, y0, -w0), (r1, y0, -w1), (r1, y1, -w1), (r0, y1, -w0),
             (r0, y0, w0), (r1, y0, w1), (r1, y1, w1), (r0, y1, w0)]
        P = [(p[0], p[1], p[2]) for p in P]
        xf = Matrix.Translation((0, 0, ZE)) @ Matrix.Rotation(-a, 4, "Y")
        acc.hexa(P, 1, xf)
    # keystone (tapered)
    P = [(-0.5, GATE_Y - 1.55, ZE + 5.0), (0.5, GATE_Y - 1.55, ZE + 5.0), (0.5, GATE_Y + 1.3, ZE + 5.0),
         (-0.5, GATE_Y + 1.3, ZE + 5.0), (-0.72, GATE_Y - 1.55, ZE + 6.5), (0.72, GATE_Y - 1.55, ZE + 6.5),
         (0.72, GATE_Y + 1.3, ZE + 6.5), (-0.72, GATE_Y + 1.3, ZE + 6.5)]
    acc.hexa(P)
    acc.box((-0.8, GATE_Y - 1.65, ZE + 6.5), (0.8, GATE_Y + 1.4, ZE + 6.72))
    acc.disc_y(0.0, ZE + 5.75, 0.22, GATE_Y - 1.62, GATE_Y - 1.55, 20, 1)


def _steps(acc):
    for k in range(3):
        acc.box((-7.6 + 0.05 * k, GATE_Y - 3.6 + 0.65 * k, 0.0), (7.6 - 0.05 * k, GATE_Y + 8.0, 0.2 * (k + 1)))


def _walls(rnd):
    """Ruined ashlar wall stubs either side of the gate, stepping down and breaking off into the dark."""
    acc = _Acc()
    for s in (-1, 1):
        x_in, x_out = HW + JW, 15.5
        for c in range(16):
            z0, z1 = c * 0.9, (c + 1) * 0.9
            x = x_in
            while x < x_out:
                L = rnd.uniform(1.1, 2.3)
                x1 = min(x + L, x_out)
                xm = 0.5 * (x + x1)
                top = 13.5 - (xm - x_in) * 1.05 + rnd.uniform(-1.6, 1.0)
                if z1 <= top or (z0 < top and rnd.random() < 0.5):
                    jy = rnd.uniform(-0.04, 0.04)
                    acc.box((s * (x + 0.012), GATE_Y - 0.85 + jy, z0 + 0.012),
                            (s * (x1 - 0.012), GATE_Y + 0.85, z1 - 0.012))
                x = x1
    return acc


def _door(name, side, rnd, mats):
    """One door leaf, origin at its hinge (back-outer corner). side=+1: left leaf (extends +X from its hinge),
    -1: right leaf (mirrored). Raised stiles / rails, three raised fields with gold inlay frames, carved
    diamonds, and half of the sun emblem at the meeting edge."""
    acc = _Acc()
    yf = -DT
    acc.box((0.02, -DT, 0.02), (HW - 0.02, 0.0, DH))
    for a, c in ((0.02, 0.4), (HW - 0.4, HW - 0.02)):
        acc.box((a, yf - 0.1, 0.02), (c, yf, DH))
    rails = ((0.02, 0.6), (3.9, 4.25), (7.75, 8.1), (DH - 0.5, DH))
    for z0, z1 in rails:
        acc.box((0.4, yf - 0.1, z0), (HW - 0.4, yf, z1))
    rows = ((0.6, 3.9), (4.25, 7.75), (8.1, DH - 0.5))
    for i, (r0, r1) in enumerate(rows):
        fx0, fx1, fz0, fz1 = 0.56, HW - 0.56, r0 + 0.16, r1 - 0.16
        acc.box((fx0, yf - 0.07, fz0), (fx1, yf, fz1))
        gx0, gx1, gz0, gz1 = fx0 + 0.14, fx1 - 0.14, fz0 + 0.14, fz1 - 0.14
        for a, c in ((gx0, gx0 + 0.045), (gx1 - 0.045, gx1)):
            acc.box((a, yf - 0.09, gz0), (c, yf - 0.07, gz1), 1)
        for z0, z1 in ((gz0, gz0 + 0.045), (gz1 - 0.045, gz1)):
            acc.box((gx0, yf - 0.09, z0), (gx1, yf - 0.07, z1), 1)
        if i != 1:
            cx, cz = 0.5 * (fx0 + fx1) - 0.25, 0.5 * (fz0 + fz1)
            xf = Matrix.Translation((cx, 0, cz)) @ Matrix.Rotation(math.radians(45), 4, "Y")
            acc.box((-0.42, yf - 0.13, -0.42), (0.42, yf - 0.07, 0.42), 0, xf)
            acc.box((-0.3, yf - 0.15, -0.3), (0.3, yf - 0.13, 0.3), 0, xf)
            acc.disc_y(cx, cz, 0.07, yf - 0.19, yf - 0.14, 16, 1)
    # half sun emblem at the meeting edge (a full sun when the doors are shut)
    cx, cz = HW - 0.02, 6.0
    acc.arc(cx, cz, 0.95, 1.03, yf - 0.14, yf - 0.1, math.pi / 2, 3 * math.pi / 2, 28, 1)
    acc.arc(cx, cz, 0.0, 0.2, yf - 0.15, yf - 0.1, math.pi / 2, 3 * math.pi / 2, 12, 1)
    for k in range(7):
        a = math.pi / 2 + math.pi * (k + 0.5) / 7
        xf = Matrix.Translation((cx, 0, cz)) @ Matrix.Rotation(-a, 4, "Y")
        acc.box((0.3, yf - 0.14, -0.03), (0.82 if k % 2 == 0 else 0.62, yf - 0.1, 0.03), 1, xf)
    acc.box((HW - 0.09, yf - 0.12, 0.6), (HW - 0.03, yf - 0.1, DH - 0.5), 1)
    # back face: plain stiles and rails (lit by the beam, seen through the gap)
    for a, c in ((0.02, 0.35), (HW - 0.35, HW - 0.02)):
        acc.box((a, 0.0, 0.02), (c, 0.06, DH))
    for z0, z1 in rails:
        acc.box((0.35, 0.0, z0), (HW - 0.35, 0.06, z1))
    if side < 0:
        for k in range(len(acc.V)):
            acc.V[k] = acc.V[k] * np.array([-1.0, 1.0, 1.0])
    ob = acc.build(name, mats)
    _bevel(ob, 0.03)
    return ob


def _occluder(name, mat):
    """Invisible shadow-casting 'light room' around the lights behind the gate: its only opening is the door
    aperture, so the beam lights the haze only through the gap (the void around the gate stays dark)."""
    acc = _Acc()
    y = GATE_Y + JD + 0.05
    yb, xr, zr = GATE_Y + 18.0, 7.5, Z0 + DH + 2.0
    for lo, hi in (((-xr, y, -2), (-HW, y + 0.02, zr)), ((HW, y, -2), (xr, y + 0.02, zr)),
                   ((-HW, y, -2), (HW, y + 0.02, Z0)), ((-HW, y, Z0 + DH), (HW, y + 0.02, zr)),
                   ((-xr - 0.02, y, -2), (-xr, yb, zr)), ((xr, y, -2), (xr + 0.02, yb, zr)),
                   ((-xr, yb, -2), (xr, yb + 0.02, zr)), ((-xr, y, zr), (xr, yb, zr + 0.02))):
        acc.box(lo, hi)
    ob = acc.build(name, [mat], smooth=False, auto=None)
    ob.visible_diffuse = False
    ob.visible_glossy = False
    return ob


def _lightbox(name, mat):
    acc = _Acc()
    x, y0, y1, z1 = 5.6, GATE_Y + 1.6, GATE_Y + 8.0, Z0 + DH + 1.6
    acc.box((-x, y1, -1.0), (x, y1 + 0.1, z1))
    acc.box((-x - 0.1, y0, -1.0), (-x, y1, z1))
    acc.box((x, y0, -1.0), (x + 0.1, y1, z1))
    acc.box((-x, y0, z1), (x, y1, z1 + 0.1))
    ob = acc.build(name, [mat], smooth=False, auto=None)
    ob.visible_shadow = False
    return ob


def _motes(name, seed, mat, n=900):
    rnd = random.Random(seed)
    P, A = [], {k: [] for k in ("phase", "spd", "len", "sz", "sway", "sfq", "dir", "spin")}
    for _ in range(n):
        y = -3.5 + (GATE_Y - 2.0 + 3.5) * rnd.random() ** 0.85
        w = (GATE_Y + 14.0 - y) * 0.75 / 12.0 + 0.25
        x = rnd.gauss(0.0, w * 0.55)
        z = 0.05 + min(7.0, 0.8 + (GATE_Y - y) * 0.18) * rnd.random() ** 1.6
        P.append((x, y, z))
        A["phase"].append(rnd.random())
        A["spd"].append(rnd.uniform(0.02, 0.07))
        A["len"].append(rnd.uniform(0.6, 1.6))
        A["sz"].append(rnd.uniform(0.004, 0.009) * (1.8 if rnd.random() < 0.05 else 1.0))
        A["sway"].append(rnd.uniform(0.05, 0.2))
        A["sfq"].append(rnd.uniform(0.15, 0.35))
        d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 0.6), rnd.uniform(-0.3, 0.8))).normalized()
        A["dir"].append(tuple(d))
        A["spin"].append((0.0, 0.0, 0.0))
    ob = _points(name, P, A)
    ico = bmesh.new()
    bmesh.ops.create_icosphere(ico, subdivisions=1, radius=1.0)
    me = bpy.data.meshes.new(name + "_shape")
    ico.to_mesh(me)
    ico.free()
    shape = bpy.data.objects.new(name + "_shape", me)
    mod = ob.modifiers.new("drift", "NODES")
    mod.node_group = _drift_tree(name + "_gn", shape, mat)
    ob.visible_shadow = False
    return ob


def build_gate(seed=0):
    """Build the Gate of Heaven set in the void (see module docstring). Also sets the world + EEVEE."""
    G = Gate(seed)
    rnd = random.Random(seed * 7919 + 31)
    G.world = world_void()
    tune_gate()
    stone = mat_stone("heaven_stone", base=(0.5, 0.47, 0.415), dark=0.5)
    gold = mat_gold("heaven_gold")
    floor = mat_floor("heaven_floor")
    light = mat_light("heaven_light")
    occ = mat_occluder("heaven_occluder")
    rub = mat_stone("heaven_rubble", base=(0.07, 0.068, 0.066), dark=0.6, rough=0.7, ao=False)
    wall = mat_stone("heaven_wall", base=(0.47, 0.44, 0.39), dark=0.55)
    mist = mat_fog("heaven_mist", 0.035, 1.6, (0.9, 0.88, 0.84), anisotropy=0.55, scale=0.11)
    motes = mat_motes("heaven_motes")
    G.mats = dict(stone=stone, gold=gold, floor=floor, light=light, occluder=occ, rubble=rub, wall=wall, mist=mist,
                  motes=motes)
    G.ctrls = {"open": light, "light": light}
    # frame + steps
    acc = _Acc()
    _steps(acc)
    for s in (-1, 1):
        _jamb(acc, s, rnd)
    _arch(acc, rnd)
    frame = acc.build("HEAVEN_gate_frame", [stone, gold])
    _bevel(frame, 0.035)
    walls = _walls(rnd).build("HEAVEN_gate_walls", [wall])
    _bevel(walls, 0.03)
    # doors
    for side, nm, hx in ((1, "HEAVEN_door_L", -HW), (-1, "HEAVEN_door_R", HW)):
        d = _door(nm, side, rnd, [stone, gold])
        d.location = (hx, GATE_Y + 0.2, Z0)
        _drive(d, "rotation_euler", light, "open", "c*%.5f" % (side * OPEN_MAX), index=2)
        G.doors.append(d)
    lb = _lightbox("HEAVEN_lightbox", light)
    oc = _occluder("HEAVEN_occluder", occ)
    # floor
    acc = _Acc()
    acc.add([(-200, -200, 0), (200, -200, 0), (200, 200, 0), (-200, 200, 0)], [(0, 1, 2, 3)])
    fl = acc.build("HEAVEN_floor", [floor], smooth=False, auto=None, recalc=False)
    # rubble: broken flags along the approach (long shadows in the beam), pale fragments by the walls
    r1 = AR.scatter_rubble("HEAVEN_rubble", (0.0, 13.0), 17.0, 300, seed + 11, size=(0.02, 0.38), mat=rub,
                           avoid=[(0.0, y, 1.3) for y in range(-6, 30, 2)])
    r2 = AR.scatter_rubble("HEAVEN_fragments", (0.0, GATE_Y - 3.5), 13.0, 70, seed + 12, size=(0.04, 0.7),
                           mat=wall, ring=8.0, avoid=[(0.0, GATE_Y - 3.0, 7.8)])
    # mist + motes
    mb = AR._box("HEAVEN_mist", (-45, -20, -0.2), (45, GATE_Y + 3.0, 4.0), mist)
    mo = _motes("HEAVEN_motes", seed + 5, motes)
    for nd in (M.ctrl_node(motes, "light"),):
        _drive(nd.outputs[0], "default_value", light, "light", "c")
    G.objects = [frame, walls] + G.doors + [lb, oc, fl, r1, r2, mb, mo]
    G.frame, G.walls, G.floor, G.lightbox, G.occluder, G.mist, G.motes = frame, walls, fl, lb, oc, mb, mo
    G.marks = dict(warrior=WARRIOR_GATE, heading=180.0, cam=(0.35, -3.6, 1.45), aim=(0.0, 8.0, 2.6),
                   gate=(0.0, GATE_Y, Z0), gap=(0.0, GATE_Y, Z0 + DH * 0.5), steps=(0.0, GATE_Y - 3.6, 0.0),
                   cam_gate=(-6.5, GATE_Y - 27.0, 2.4), aim_gate=(0.0, GATE_Y, 9.6))
    return G


def lights_gate(gate, warrior=None, cam=None, follow=None):
    """Lights for E3 (see module docstring). Energies follow CTRL_light (drivers). 2 shadow casters."""
    mk = gate.marks
    W = Vector(warrior if warrior is not None else mk["warrior"])
    if len(W) == 2:
        W = Vector((W.x, W.y, 0.0))
    Cm = Vector(cam if cam is not None else mk["cam"])
    lm = gate.ctrls["light"]
    L = {}
    L["beam"] = _L("SPOT", "beam", (0.0, GATE_Y + 14.0, Z0 + 8.0), HEAVEN, 7.0e4, target=(0.0, GATE_Y, Z0 + 4.0),
                   size=0.5, shadow=True, spot=95.0, blend=0.2, volume=1.0, specular=1.0)
    L["aura"] = _L("POINT", "aura", (0.0, GATE_Y - 1.0, Z0 + DH + 1.0), HEAVEN, 5000.0, size=3.0, shadow=False,
                   volume=1.0, diffuse=0.0, specular=0.0, cutoff=22.0)
    bo = _L("AREA", "bounce", (0.0, GATE_Y - 9.0, 0.03), "#FFE4BE", 900.0, size=8.0, volume=0.0, specular=0.35)
    bo.data.shape = "RECTANGLE"
    bo.data.size, bo.data.size_y = 8.0, 14.0
    bo.rotation_euler = (math.pi, 0.0, 0.0)
    L["bounce"] = bo
    L["front"] = _L("AREA", "front", (0.0, GATE_Y - 30.0, 16.0), "#8C9BAD", 450.0, target=(0.0, GATE_Y, 8.0),
                    size=16.0, volume=0.0, specular=0.5)
    # warrior: warm white rim from the gate side + ember kicker on his side (both follow him)
    t = W + Vector((0, 0, 1.3))
    d = t - Cm
    d.z = 0
    d.normalize()
    sv = Vector((-d.y, d.x, 0.0))
    L["gate_rim"] = _L("SPOT", "gate_rim", t + d * 3.2 + sv * 0.8 + Vector((0, 0, 1.4)), HEAVEN, 450.0, target=t,
                       size=0.5, spot=32.0, blend=0.5, volume=0.0, diffuse=0.25, specular=1.3, cutoff=6.0)
    L["ember"] = _L("POINT", "ember", W + sv * 0.62 + d * 0.1 + Vector((0, 0, 1.35)), EMBER, 14.0, size=0.1,
                    volume=0.0, cutoff=1.15)
    L["ember2"] = _L("POINT", "ember2", W - sv * 0.58 + d * 0.15 + Vector((0, 0, 1.55)), EMBER, 6.0, size=0.1,
                     volume=0.0, cutoff=1.0)
    for k in ("beam", "aura", "bounce", "front", "gate_rim"):
        _drive(L[k].data, "energy", lm, "light", "c*%.1f" % L[k].data.energy)
    if follow is not None:
        for k in ("gate_rim", "ember", "ember2"):
            C.parent_keep(L[k], follow)
    gate.lights = L
    return L


# =================================================================== E4 — sky / eevee
def sky_world(sun_dir=SUN_DIR, fog=0.0004):
    """Soft warm sky: warm white #FFF4DC at the horizon -> pale blue zenith, a broad sun glow (sun out of
    frame), a few faint low wisps. CTRL_fog = uniform volume density (light haze), CTRL_sky = brightness."""
    w = bpy.data.worlds.new("MEADOW_sky")
    bpy.context.scene.world = w
    w.use_nodes = True
    b = M.NB(w)
    out = b.n("ShaderNodeOutputWorld")
    D = (b.n("ShaderNodeTexCoord"), "Generated")
    Dn = b.n("ShaderNodeVectorMath", _operation="NORMALIZE", Vector=D)
    e = (_sep(b, (Dn, 0)), "Z")
    hz = _lin(HEAVEN)
    sky = b.ramp(_mr(b, e, -0.08, 0.75), [(0.0, (0.66, 0.6, 0.5)), (0.1, (hz[0], hz[1] * 0.96, hz[2] * 0.86)),
                                         (0.26, (0.58, 0.66, 0.74)), (1.0, (0.24, 0.38, 0.62))])
    dot = b.n("ShaderNodeVectorMath", _operation="DOT_PRODUCT", Vector=(Dn, 0))
    dot.inputs[1].default_value = tuple(sun_dir)
    g = b.math("MAXIMUM", (dot, "Value"), 0.0)
    glow = b.math("ADD", b.math("MULTIPLY", b.math("POWER", g, 5.0), 0.55),
                  b.math("MULTIPLY", b.math("POWER", g, 48.0), 1.6))
    glow = b.math("ADD", glow, b.math("MULTIPLY", b.math("GREATER_THAN", g, 0.99985), 60.0))
    wisp = _noise(b, _mapv(b, (Dn, 0), (2.2, 2.2, 16.0)), 1.6, 5.0, 0.55)
    band = b.math("MULTIPLY", _mr(b, e, 0.015, 0.06), _mr(b, e, 0.12, 0.2, 1.0, 0.0))
    wk = b.math("MULTIPLY", _mr(b, (wisp, "Fac"), 0.52, 0.72, 0.0, 0.22), band)
    c1 = b.mix(wk, sky, (1.0, 0.95, 0.88), "ADD")
    c2 = b.n("ShaderNodeMix", _data_type="RGBA", _blend_type="ADD", _clamp_factor=False)
    b._in(c2, "Factor", glow)
    b._in(c2, 6, c1)
    b._in(c2, 7, (1.0, 0.84, 0.6))
    k = b.ctrl("sky", 1.05)
    bg = b.n("ShaderNodeBackground", Color=(c2, 2), Strength=k)
    b.link(bg, out.inputs["Surface"])
    f = b.ctrl("fog", fog)
    pv = b.n("ShaderNodeVolumePrincipled", Color=(0.96, 0.93, 0.88), Density=f, Anisotropy=0.45)
    b.link(pv, out.inputs["Volume"])
    return w


def tune_meadow(sc=None):
    sc = sc or bpy.context.scene
    e = sc.eevee
    e.use_bloom = True
    e.bloom_intensity = 0.045
    e.bloom_threshold = 1.0
    e.bloom_radius = 6.5
    e.bloom_knee = 0.5
    e.bloom_color = (1.0, 0.95, 0.88)
    e.use_ssr = False
    e.use_gtao = True
    e.gtao_distance = 0.3
    e.gtao_factor = 1.0
    e.volumetric_start = 0.5
    e.volumetric_end = 320.0
    e.volumetric_tile_size = "16"
    e.volumetric_samples = 32
    e.volumetric_sample_distribution = 0.8
    e.use_volumetric_lights = True
    e.use_volumetric_shadows = False
    e.use_soft_shadows = True
    e.shadow_cascade_size = "2048"
    e.light_threshold = 0.01
    return sc


# =================================================================== E4 — materials
def _aerial(b, shader, k=1.0, scale=420.0, color=(0.97, 0.9, 0.78), strength=0.98):
    """Aerial perspective: blend toward a luminous warm haze with view distance."""
    cd = b.n("ShaderNodeCameraData")
    fac = b.math("SUBTRACT", 1.0, b.math("EXPONENT", b.math("MULTIPLY", (cd, "View Distance"), -k / scale)))
    em = b.n("ShaderNodeEmission", Color=color, Strength=strength)
    mx = b.n("ShaderNodeMixShader", Fac=fac)
    b.link(shader, mx.inputs[1])
    b.link(em, mx.inputs[2])
    return mx


def mat_meadow_ground(name="meadow_ground"):
    """Distant / under-grass meadow: green patches (#8DB580), drier warm patches, fine blade striation,
    flower speckles that fade in with distance (stand-ins where instances thin out), aerial perspective."""
    m, b = M.new(name)
    p = _pos(b)
    mg = _lin(MEADOW)
    big = _noise(b, p, 0.035, 4.0, 0.55)
    mid = _noise(b, p, 0.25, 4.0, 0.55)
    fine = _noise(b, _mapv(b, p, (9.0, 9.0, 3.0)), 1.0, 6.0, 0.65)
    c = b.mix(_mr(b, (big, "Fac"), 0.35, 0.68), (mg[0] * 0.3, mg[1] * 0.4, mg[2] * 0.22), (mg[0] * 0.62, mg[1] * 0.7, mg[2] * 0.48))
    c = b.mix(_mr(b, (mid, "Fac"), 0.55, 0.75, 0.0, 0.5), c, (0.3, 0.29, 0.1))
    c = b.mix(_mr(b, (fine, "Fac"), 0.3, 0.7, 0.6, 0.0), c, (0.025, 0.045, 0.012))
    vor = b.n("ShaderNodeTexVoronoi", Vector=p, Scale=5.0)
    dots = _mr(b, (vor, "Distance"), 0.05, 0.11, 1.0, 0.0)
    patch = _mr(b, (_noise(b, p, 0.12, 3.0, 0.5), "Fac"), 0.45, 0.62, 0.15, 1.0)
    cd = b.n("ShaderNodeCameraData")
    far = _mr(b, (cd, "View Distance"), 25.0, 55.0, 0.0, 1.0)
    fcol = b.ramp((b.n("ShaderNodeSeparateColor", Color=(vor, "Color")), 0),
                  [(0.0, (0.8, 0.79, 0.74)), (0.55, (0.86, 0.68, 0.3)), (0.82, (0.84, 0.56, 0.6))])
    fcol.color_ramp.interpolation = "CONSTANT"
    c = b.mix(b.math("MULTIPLY", b.math("MULTIPLY", dots, patch), far), c, (fcol, "Color"))
    bump = b.n("ShaderNodeBump", Strength=0.4, Distance=0.02, Height=(fine, "Fac"))
    bs = b.bsdf(**{"Base Color": c, "Roughness": 0.88, "Specular IOR Level": 0.2, "Sheen Weight": 0.25,
                   "Sheen Roughness": 0.5, "Normal": bump})
    b.out(_aerial(b, bs))
    return m


def mat_grass(name="meadow_grass"):
    """Grass blades: root -> tip ramp (UV v), patchy hue variation in world space, translucent (backlit)."""
    m, b = M.new(name)
    m.shadow_method = "NONE"
    m.use_backface_culling = False
    p = _pos(b)
    mg = _lin(MEADOW)
    v = (_sep(b, (b.n("ShaderNodeUVMap", _uv_map="UVMap"), "UV")), "Y")
    col = b.ramp(v, [(0.0, (0.012, 0.024, 0.006)), (0.45, (mg[0] * 0.42, mg[1] * 0.52, mg[2] * 0.3)),
                     (1.0, (0.3, 0.4, 0.13))])
    n1 = _noise(b, p, 0.18, 3.0, 0.5)
    n2 = _noise(b, p, 1.3, 2.0, 0.5)
    c = b.mix(_mr(b, (n1, "Fac"), 0.55, 0.72, 0.0, 0.6), (col, "Color"), (0.34, 0.32, 0.11))
    c = b.mix(_mr(b, (n2, "Fac"), 0.3, 0.7, 0.25, 0.0), c, (0.03, 0.05, 0.02))
    bs = b.bsdf(**{"Base Color": c, "Roughness": 0.5, "Specular IOR Level": 0.35})
    tr = b.n("ShaderNodeBsdfTranslucent", Color=c)
    mx = b.n("ShaderNodeMixShader", Fac=0.28)
    b.link(bs, mx.inputs[1])
    b.link(tr, mx.inputs[2])
    b.out(_aerial(b, mx))
    return m


def mat_petal(name, color, translucent=0.35, rough=0.45):
    m, b = M.new(name)
    m.shadow_method = "NONE"
    m.use_backface_culling = False
    bs = b.bsdf(**{"Base Color": color, "Roughness": rough, "Specular IOR Level": 0.3, "Sheen Weight": 0.3})
    tr = b.n("ShaderNodeBsdfTranslucent", Color=color)
    mx = b.n("ShaderNodeMixShader", Fac=translucent)
    b.link(bs, mx.inputs[1])
    b.link(tr, mx.inputs[2])
    b.out(_aerial(b, mx))
    return m


def mat_drift_petals(name="meadow_drift_petals"):
    """Floating petals: white / soft pink / pale gold by the per-petal attr rnd, translucent."""
    m, b = M.new(name)
    m.shadow_method = "NONE"
    m.use_backface_culling = False
    r = b.attr("rnd")
    col = b.ramp(r, [(0.0, (0.86, 0.84, 0.8)), (0.55, (0.88, 0.62, 0.66)), (0.85, (0.9, 0.76, 0.48))])
    col.color_ramp.interpolation = "CONSTANT"
    bs = b.bsdf(**{"Base Color": (col, "Color"), "Roughness": 0.45, "Specular IOR Level": 0.3})
    tr = b.n("ShaderNodeBsdfTranslucent", Color=(col, "Color"))
    mx = b.n("ShaderNodeMixShader", Fac=0.4)
    b.link(bs, mx.inputs[1])
    b.link(tr, mx.inputs[2])
    b.out(mx)
    return m


# =================================================================== E4 — instance shapes
def _blade(V, F, UV, rnd, bx, by, h, lean, wid, d_ang, segs=3):
    base = len(V)
    fa = d_ang + math.pi / 2 + rnd.uniform(-0.35, 0.35)
    cf, sf = math.cos(fa), math.sin(fa)
    for s in range(segs + 1):
        u = s / segs
        off = lean * h * u * u
        cx, cy = bx + math.cos(d_ang) * off, by + math.sin(d_ang) * off
        cz = h * u * (1.0 - 0.3 * lean * u)
        if s < segs:
            w = wid * (1.0 - 0.85 * u) * 0.5
            V += [(cx - cf * w, cy - sf * w, cz), (cx + cf * w, cy + sf * w, cz)]
            UV += [(0.0, u), (1.0, u)]
        else:
            V.append((cx, cy, cz))
            UV.append((0.5, 1.0))
    for s in range(segs - 1):
        a = base + 2 * s
        F.append((a, a + 1, a + 3, a + 2))
    a = base + 2 * (segs - 1)
    F.append((a, a + 1, base + 2 * segs))


def _tuft(rnd, nb, hgt, lean, wid, spread=0.06):
    V, F, UV = [], [], []
    for _ in range(nb):
        a = rnd.uniform(0, 2 * math.pi)
        r = spread * math.sqrt(rnd.random())
        _blade(V, F, UV, rnd, r * math.cos(a), r * math.sin(a), hgt * rnd.uniform(0.55, 1.15),
               lean * rnd.uniform(0.3, 1.2), wid * rnd.uniform(0.75, 1.25), a + rnd.uniform(-0.7, 0.7))
    return V, F, UV


def _seed_stalk(rnd):
    V, F, UV = [], [], []
    h = rnd.uniform(0.6, 0.8)
    _blade(V, F, UV, rnd, 0.0, 0.0, h, 0.12, 0.006, rnd.uniform(0, 6.28), segs=3)
    tx, ty, tz = V[-1]
    for k in range(2):
        a = k * math.pi / 2
        b0 = len(V)
        ca, sa = math.cos(a) * 0.012, math.sin(a) * 0.012
        V += [(tx - ca, ty - sa, tz - 0.1), (tx + ca, ty + sa, tz - 0.1), (tx + ca * 0.4, ty + sa * 0.4, tz + 0.02),
              (tx - ca * 0.4, ty - sa * 0.4, tz + 0.02)]
        UV += [(0, 0.85), (1, 0.85), (1, 1.0), (0, 1.0)]
        F.append((b0, b0 + 1, b0 + 2, b0 + 3))
    return V, F, UV


def _flower(rnd, kind):
    """Small flower: stem ribbon (mat 0 = grass), centre (mat 1), petals (mat 2). Returns V, F, UV, Fm."""
    V, F, UV, Fm = [], [], [], []
    hs = {"daisy": rnd.uniform(0.3, 0.45), "cup": rnd.uniform(0.26, 0.4), "pink": rnd.uniform(0.32, 0.48)}[kind]
    n0 = len(F)
    _blade(V, F, UV, rnd, 0.0, 0.0, hs, 0.1, 0.006, rnd.uniform(0, 6.28), segs=2)
    Fm += [0] * (len(F) - n0)
    # head frame: tilt toward +Y (the sun) a little
    tilt = Matrix.Rotation(rnd.uniform(-0.45, -0.1), 3, "X") @ Matrix.Rotation(rnd.uniform(-0.3, 0.3), 3, "Y")
    top = Vector(V[-1])          # stem tip

    def put(p):
        return tuple(top + tilt @ Vector(p))

    cr = {"daisy": 0.0075, "cup": 0.005, "pink": 0.0055}[kind]
    b0 = len(V)
    V.append(put((0, 0, 0.004)))
    UV.append((0.5, 1.0))
    for i in range(6):
        a = 2 * math.pi * i / 6
        V.append(put((cr * math.cos(a), cr * math.sin(a), 0.0)))
        UV.append((0.5, 1.0))
    for i in range(6):
        F.append((b0, b0 + 1 + i, b0 + 1 + (i + 1) % 6))
        Fm.append(1)
    npet, L, Wd, cup = {"daisy": (12, 0.03, 0.0065, 0.15), "cup": (5, 0.017, 0.0125, 0.7),
                        "pink": (8, 0.028, 0.012, 0.25)}[kind]
    ph = rnd.uniform(0, 6.28)
    for i in range(npet):
        a = ph + 2 * math.pi * i / npet + rnd.uniform(-0.08, 0.08)
        ca, sa = math.cos(a), math.sin(a)
        ln = L * rnd.uniform(0.85, 1.1)
        r0 = cr * 0.8
        el = cup + rnd.uniform(-0.1, 0.1)
        pts = []
        for (r, w, z) in ((r0, Wd * 0.35, 0.0), (r0 + ln * 0.5, Wd * 0.5, ln * 0.5 * el),
                          (r0 + ln, Wd * 0.2, ln * el * 1.1)):
            pts.append((r * ca - sa * w, r * sa + ca * w, z))
            pts.append((r * ca + sa * w, r * sa - ca * w, z))
        b1 = len(V)
        for p in pts:
            V.append(put(p))
            UV.append((0.5, 1.0))
        F.append((b1, b1 + 1, b1 + 3, b1 + 2))
        F.append((b1 + 2, b1 + 3, b1 + 5, b1 + 4))
        Fm += [2, 2]
    return V, F, UV, Fm


def _shape_multi(name, V, F, UV, Fm, mats):
    acc = _Acc()
    acc.V, acc.UV = [np.asarray(V, float)], [np.asarray(UV, float)]
    acc.F, acc.Fm, acc.n = [list(f) for f in F], list(Fm), len(V)
    return acc.build(name, mats, smooth=True, auto=None, recalc=False, link_scene=False)


# =================================================================== E4 — terrain
def _meadow_height(nz):
    S = FO._smooth

    def h(X, Y):
        X = np.asarray(X, float)
        Y = np.asarray(Y, float)
        z = 0.5 * nz.fbm(X / 26.0, Y / 26.0, 0.37, 3) + 0.04 * nz.fbm(X / 6.0, Y / 6.0, 2.7, 2)
        z = z + 2.2 * nz.fbm(X / 55.0, Y / 45.0, 4.2, 2) * S(10.0, 45.0, np.hypot(X, Y))
        z = z + 0.6 * np.exp(-((X / 18.0) ** 2 + ((Y - 3.0) / 15.0) ** 2))
        z = z - 4.0 * S(30.0, 85.0, Y) * (1.0 - S(100.0, 190.0, Y))
        z = z + S(110.0, 260.0, Y) * (16.0 + 12.0 * nz.fbm(X / 120.0, Y / 90.0, 5.1, 4))
        z = z + S(330.0, 520.0, Y) * (40.0 + 28.0 * nz.fbm(X / 260.0, Y / 200.0, 9.3, 3))
        z = z + 9.0 * S(70.0, 260.0, np.abs(X)) * S(-40.0, 60.0, Y)
        return z
    return h


def _wedge(X, Y, cam, half_deg=31.0, d0=3.0, d1=75.0, margin=3.0):
    dx, dy = X - cam[0], Y - cam[1]
    return (dy > d0) & (np.abs(dx) < dy * math.tan(math.radians(half_deg)) + margin) & (np.hypot(dx, dy) < d1)


def build_meadow(seed=0):
    """Build the heaven meadow set (see module docstring). Also sets the sky world + EEVEE."""
    Mw = Meadow(seed)
    nz = FO.VNoise(seed * 31 + 7)
    rng = np.random.default_rng(seed * 977 + 13)
    rnd = random.Random(seed * 131 + 5)
    h = _meadow_height(nz)
    Mw.h = h
    Mw.world = sky_world()
    tune_meadow()
    W = Vector((0.0, 0.0, Mw.ground_z(0.0, 0.0)))
    cam = Vector((1.6, -11.5, 0.0))
    cam.z = max(W.z + 3.2, Mw.ground_z(cam.x, cam.y) + 1.6)
    camf = Vector((2.4, -19.5, 0.0))
    camf.z = max(W.z + 4.8, Mw.ground_z(camf.x, camf.y) + 1.8)
    aim = W + Vector((0.0, 200.0, 31.0))
    Mw.marks = dict(warrior=tuple(W), heading=180.0, cam=tuple(cam), cam_far=tuple(camf), aim=tuple(aim),
                    sun_dir=tuple(SUN_DIR))
    ground = mat_meadow_ground()
    grass = mat_grass()
    stem = grass
    centre = mat_petal("meadow_flower_centre", (0.5, 0.33, 0.04), translucent=0.1, rough=0.7)
    pw = mat_petal("meadow_petal_white", (0.80, 0.79, 0.74))
    pg = mat_petal("meadow_petal_gold", (0.86, 0.67, 0.26))
    pk = mat_petal("meadow_petal_pink", (0.83, 0.52, 0.58))
    drift = mat_drift_petals()
    mist = mat_fog("meadow_mist", 0.0035, 9.0, (0.97, 0.94, 0.9), anisotropy=0.5, scale=0.02,
                   wind=(0.4, 0.2, 0.0), z0=W.z - 7.0, contrast=(0.3, 0.75, 0.35, 1.2))
    Mw.mats = dict(ground=ground, grass=grass, centre=centre, petal_white=pw, petal_gold=pg, petal_pink=pk,
                   drift=drift, mist=mist)
    # terrain
    xs = FO._axis(0.0, 700.0, 241, k=3.4)
    ys = FO._axis(40.0, 700.0, 281, k=3.4)
    Xg, Yg = np.meshgrid(xs, ys)
    terr = FO.heightfield("MEADOW_terrain", xs, ys, h(Xg, Yg), mats=[ground])
    Mw.terrain = terr
    # grass: tuft variants (idx 0-5 tufts, 6 seed stalk) in an unlinked collection
    gcol = bpy.data.collections.new("MEADOW_grass_src")
    specs = [(7, 0.34, 0.35, 0.011), (6, 0.42, 0.45, 0.012), (8, 0.28, 0.25, 0.010), (5, 0.5, 0.55, 0.013),
             (7, 0.38, 0.6, 0.011), (6, 0.24, 0.3, 0.009)]
    for i, (nb, hg, ln, wd) in enumerate(specs):
        V, F, UV = _tuft(random.Random(seed * 17 + i), nb, hg, ln, wd)
        gcol.objects.link(_shape("MEADOW_g%02d" % i, V, F, [grass], UV))
    V, F, UV = _seed_stalk(random.Random(seed * 17 + 99))
    gcol.objects.link(_shape("MEADOW_g%02d" % len(specs), V, F, [grass], UV))
    # scatter grass inside the view wedge
    x0, x1, y0, y1 = camf.x - 48.0, camf.x + 48.0, camf.y + 3.0, camf.y + 78.0
    rho_max = 30.0
    n = int((x1 - x0) * (y1 - y0) * rho_max)
    X = rng.uniform(x0, x1, n)
    Y = rng.uniform(y0, y1, n)
    keep = _wedge(X, Y, camf) | _wedge(X, Y, cam)
    X, Y = X[keep], Y[keep]
    dc = np.hypot(X - camf.x, Y - camf.y)
    rw = np.hypot(X - W.x, Y - W.y)
    rho = np.where(dc < 32.0, 13.0, np.interp(dc, [32.0, 75.0], [13.0, 2.5]))
    rho = np.maximum(rho, np.interp(rw, [3.0, 7.0], [28.0, 0.0]))
    acc_ = rng.random(len(X)) < rho / rho_max
    X, Y = X[acc_], Y[acc_]
    dc = np.hypot(X - camf.x, Y - camf.y)
    ng = len(X)
    Z = h(X, Y) - 0.03
    idx = rng.integers(0, len(specs), ng)
    idx = np.where(rng.random(ng) < 0.035, len(specs), idx)
    scl = rng.uniform(0.8, 1.25, ng) * (1.0 + np.maximum(dc - 22.0, 0.0) / 45.0)
    rot = np.column_stack([rng.normal(0, 0.08, ng), rng.normal(0, 0.08, ng), rng.uniform(0, 2 * math.pi, ng)])
    gp = _points("MEADOW_grass", np.column_stack([X, Y, Z]), dict(idx=("INT", idx), scl=scl, rot=rot))
    gp.modifiers.new("scatter", "NODES").node_group = _scatter_tree("MEADOW_grass_gn", gcol, sway=(0.07, 0.05))
    gp.visible_shadow = False
    Mw.grass = gp
    # flowers: 0-1 daisy (white), 2-3 buttercup (pale gold), 4 soft pink
    fcol = bpy.data.collections.new("MEADOW_flower_src")
    kinds = [("daisy", pw), ("daisy", pw), ("cup", pg), ("cup", pg), ("pink", pk)]
    for i, (kd, pm) in enumerate(kinds):
        V, F, UV, Fm = _flower(random.Random(seed * 23 + i), kd)
        fcol.objects.link(_shape_multi("MEADOW_f%02d" % i, V, F, UV, Fm, [stem, centre, pm]))
    rho_fmax = 9.0
    n = int((x1 - x0) * (y1 - y0) * rho_fmax)
    X = rng.uniform(x0, x1, n)
    Y = rng.uniform(y0, y1, n)
    keep = (_wedge(X, Y, camf, d1=62.0) | _wedge(X, Y, cam, d1=62.0))
    X, Y = X[keep], Y[keep]
    patch = FO._smooth(0.0, 0.45, nz.fbm(X / 7.0, Y / 7.0, 3.3, 3))
    rw = np.hypot(X - W.x, Y - W.y)
    rho = 0.4 + 8.6 * patch + np.interp(rw, [1.0, 6.0], [3.0, 0.0])
    acc_ = rng.random(len(X)) < rho / rho_fmax
    X, Y = X[acc_], Y[acc_]
    nf = len(X)
    pinkz = FO._smooth(0.25, 0.55, nz.fbm(X / 11.0, Y / 11.0, 7.7, 2))
    u = rng.random(nf)
    idx = np.where(u < 0.55, rng.integers(0, 2, nf), rng.integers(2, 4, nf))
    idx = np.where(rng.random(nf) < 0.07 + 0.3 * pinkz, 4, idx)
    dc = np.hypot(X - camf.x, Y - camf.y)
    scl = rng.uniform(1.0, 1.45, nf) * (1.0 + np.maximum(dc - 16.0, 0.0) / 30.0)
    rot = np.column_stack([rng.normal(0, 0.06, nf), rng.normal(0, 0.06, nf), rng.uniform(0, 2 * math.pi, nf)])
    fp = _points("MEADOW_flowers", np.column_stack([X, Y, h(X, Y) - 0.02]), dict(idx=("INT", idx), scl=scl, rot=rot))
    fp.modifiers.new("scatter", "NODES").node_group = _scatter_tree("MEADOW_flowers_gn", fcol, sway=(0.06, 0.05))
    fp.visible_shadow = False
    Mw.flowers = fp
    # floating petals (frame-driven)
    npt = 420
    P, A = [], {k: [] for k in ("phase", "spd", "len", "sz", "sway", "sfq", "dir", "spin", "rnd")}
    wind = Vector((0.8, 0.52, 0.16)).normalized()
    for _ in range(npt):
        px = W.x + rnd.uniform(-12.0, 12.0)
        py = W.y + (-17.0 + 34.0 * rnd.random() ** 1.6)
        pz = Mw.ground_z(px, py) + rnd.uniform(0.25, 5.5) ** 1.0
        P.append((px, py, pz))
        A["phase"].append(rnd.random())
        A["spd"].append(rnd.uniform(0.45, 0.95))
        A["len"].append(rnd.uniform(16.0, 24.0))
        A["sz"].append(rnd.uniform(1.3, 2.0))
        A["sway"].append(rnd.uniform(0.25, 0.55))
        A["sfq"].append(rnd.uniform(0.6, 1.1))
        d = (wind + Vector((rnd.uniform(-0.15, 0.15), rnd.uniform(-0.15, 0.15), rnd.uniform(-0.08, 0.08)))).normalized()
        A["dir"].append(tuple(d))
        A["spin"].append((rnd.uniform(-4, 4), rnd.uniform(-4, 4), rnd.uniform(-2, 2)))
        A["rnd"].append(rnd.random())
    pp = _points("MEADOW_petals", P, A)
    pv = [(0, -0.004, 0), (0.008, 0.002, 0.002), (0, 0.014, 0.003), (-0.008, 0.002, 0.002), (0, 0.006, -0.001)]
    pshape = _shape("MEADOW_petal_shape", pv, [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], [drift])
    pp.modifiers.new("drift", "NODES").node_group = _drift_tree("MEADOW_petals_gn", pshape, drift)
    pp.visible_shadow = False
    Mw.petals = pp
    # valley mist
    mb = AR._box("MEADOW_mist", (-260.0, 30.0, W.z - 12.0), (260.0, 320.0, W.z + 4.0), mist)
    Mw.mist = mb
    Mw.objects = [terr, gp, fp, pp, mb]
    for m in (mist,):
        for nd in m.node_tree.nodes:
            if nd.name.startswith("CTRL_"):
                Mw.ctrls.setdefault(nd.name[5:], []).append(m)
    Mw.counts = dict(grass=ng, flowers=nf, petals=npt)
    return Mw


def lights_meadow(meadow, warrior=None, cam=None, follow=None):
    """E4: low warm sun (the one shadow caster), ember-gold rim on the warrior (parented to `follow`),
    soft cool fill from the camera side. The sky world does the rest."""
    mk = meadow.marks
    W = Vector(warrior if warrior is not None else mk["warrior"])
    if len(W) == 2:
        W = Vector((W.x, W.y, meadow.ground_z(W.x, W.y)))
    Cm = Vector(cam if cam is not None else mk["cam"])
    L = {}
    sd = Vector(mk.get("sun_dir", SUN_DIR))
    sun = _L("SUN", "sun", W + sd * 100.0, "#FFDDB0", 4.6, target=tuple(W), size=math.radians(2.2), shadow=True,
             volume=0.6, prefix="MEADOW_")
    s = sun.data
    s.shadow_cascade_count = 4
    s.shadow_cascade_max_distance = 70.0
    s.shadow_cascade_exponent = 0.75
    s.shadow_cascade_fade = 0.12
    s.shadow_buffer_bias = 0.03
    L["sun"] = sun
    d = W - Cm
    d.z = 0
    d.normalize()
    sv = Vector((-d.y, d.x, 0.0))
    for nm, off, z, e in (("rimL", 0.55, 1.38, 1.0), ("rimR", -0.55, 1.38, 1.0), ("rimH", 0.15, 1.95, 0.5)):
        L[nm] = _L("POINT", nm, W + d * 0.45 + sv * off + Vector((0, 0, z)), "#FF8A3C", 9.0 * e, size=0.1,
                   volume=0.0, cutoff=1.15, prefix="MEADOW_")
    L["fill"] = _L("AREA", "fill", W - d * 4.0 + sv * 1.5 + Vector((0, 0, 2.4)), (0.82, 0.88, 1.0), 45.0,
                   target=tuple(W + Vector((0, 0, 1.0))), size=4.0, volume=0.0, specular=0.3, prefix="MEADOW_")
    if follow is not None:
        for k in ("rimL", "rimR", "rimH", "fill"):
            C.parent_keep(L[k], follow)
    meadow.lights = L
    return L
