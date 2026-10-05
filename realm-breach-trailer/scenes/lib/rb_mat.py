"""PBR material library (Blender 4.0 Principled BSDF socket names).

Materials read baked point attributes from rb_mesh.bake_attributes:
  wear (convex edges -> bare metal), mud (low parts), cav (grime).
Animated controls are Value nodes named "CTRL_*" whose outputs are keyed by
the shot scripts (e.g. CTRL_crack_glow on the sword, CTRL_ignite on the god).
"""
import bpy

from rb_core import hexcol

_cache = {}


class NB:
    """Tiny node-building helper."""

    def __init__(self, mat):
        self.m = mat
        self.nt = mat.node_tree
        self.nt.nodes.clear()
        self.x = 0

    def n(self, kind, **inputs):
        node = self.nt.nodes.new(kind)
        node.location = (self.x, 0)
        self.x += 180
        for k, v in inputs.items():
            if k.startswith("_"):
                setattr(node, k[1:], v)
            else:
                self.set(node, k, v)
        return node

    def set(self, node, key, v):
        sock = node.inputs[key]
        if hasattr(v, "bl_idname") or (isinstance(v, tuple) and len(v) == 2 and hasattr(v[0], "bl_idname")):
            self.link(v, sock)
        elif hasattr(v, "is_output"):
            self.nt.links.new(v, sock)
        else:
            if isinstance(v, (tuple, list)) and len(v) == 3 and sock.type == "RGBA":
                v = (*v, 1.0)
            sock.default_value = v

    def link(self, src, dst):
        if isinstance(src, tuple):
            src = src[0].outputs[src[1]]
        elif hasattr(src, "outputs"):
            src = src.outputs[0]
        self.nt.links.new(src, dst)

    def math(self, op, a, b=None, clamp=False):
        node = self.n("ShaderNodeMath", _operation=op, _use_clamp=clamp)
        self._in(node, 0, a)
        if b is not None:
            self._in(node, 1, b)
        return node

    def mix(self, fac, a, b, blend="MIX"):
        node = self.n("ShaderNodeMix", _data_type="RGBA", _blend_type=blend)
        self._in(node, "Factor", fac)
        self._in(node, 6, a)
        self._in(node, 7, b)
        return (node, 2)

    def _in(self, node, key, v):
        sock = node.inputs[key]
        if isinstance(v, (int, float)):
            sock.default_value = v
        elif isinstance(v, (tuple, list)) and not hasattr(v[0], "bl_idname"):
            sock.default_value = (*v, 1.0) if len(v) == 3 and sock.type == "RGBA" else v
        else:
            self.link(v, sock)

    def attr(self, name):
        return (self.n("ShaderNodeAttribute", _attribute_name=name, _attribute_type="GEOMETRY"), "Fac")

    def ctrl(self, name, value):
        node = self.n("ShaderNodeValue")
        node.name = "CTRL_" + name
        node.label = name
        node.outputs[0].default_value = value
        return node

    def ramp(self, fac, stops):
        node = self.n("ShaderNodeValToRGB")
        self._in(node, "Fac", fac)
        cr = node.color_ramp
        while len(cr.elements) < len(stops):
            cr.elements.new(0.5)
        for el, (pos, col) in zip(cr.elements, stops):
            el.position = pos
            el.color = (*col, 1.0) if len(col) == 3 else col
        return node

    def bsdf(self, **kw):
        return self.n("ShaderNodeBsdfPrincipled", **kw)

    def out(self, surface=None, volume=None, displacement=None):
        o = self.n("ShaderNodeOutputMaterial")
        if surface is not None:
            self.link(surface, o.inputs["Surface"])
        if volume is not None:
            self.link(volume, o.inputs["Volume"])
        return o


def new(name, blend="OPAQUE"):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.blend_method = blend
    if blend != "OPAQUE":
        m.shadow_method = "CLIP" if blend == "CLIP" else "HASHED"
    return m, NB(m)


def ctrl_node(mat, name):
    return mat.node_tree.nodes.get("CTRL_" + name)


def key_ctrl(mat, name, frame, value):
    node = ctrl_node(mat, name)
    node.outputs[0].default_value = value
    node.outputs[0].keyframe_insert("default_value", frame=frame)


# ------------------------------------------------------------------ steel
def steel(name="steel_black", look="black", seed=0):
    """Blackened (look='black') or worn grey iron (look='iron') plate steel."""
    key = (name, look)
    if key in _cache:
        return _cache[key]
    m, b = new(name)
    tc = b.n("ShaderNodeTexCoord")
    obj = (tc, "Object")
    wear = b.attr("wear")
    mud = b.attr("mud")
    cav = b.attr("cav")
    # break up wear with noise so edges chip unevenly
    nz = b.n("ShaderNodeTexNoise", Vector=obj, Scale=38.0, Detail=6.0, Roughness=0.6)
    nz2 = b.n("ShaderNodeTexNoise", Vector=obj, Scale=7.0, Detail=4.0, Roughness=0.55)
    w1 = b.math("MULTIPLY", wear, (nz, "Fac"))
    w2 = b.math("MULTIPLY", w1, 2.2)
    wearm = b.n("ShaderNodeMapRange", Value=w2, **{"From Min": 0.55, "From Max": 0.9})
    # scratches: noise stretched along one axis
    mp = b.n("ShaderNodeMapping", Vector=obj, Scale=(1.0, 1.0, 22.0))
    mp.inputs["Rotation"].default_value = (0.4, 0.9, 0.2)
    scr = b.n("ShaderNodeTexWave", Vector=mp, Scale=9.0, Distortion=6.0, Detail=4.0, **{"Detail Scale": 2.0})
    scrm = b.n("ShaderNodeMapRange", Value=(scr, "Fac"), **{"From Min": 0.93, "From Max": 0.99})
    scr_gate = b.n("ShaderNodeMapRange", Value=(nz2, "Fac"), **{"From Min": 0.5, "From Max": 0.7})
    scr_mask = b.math("MULTIPLY", scrm, scr_gate)
    if look == "black":
        base = (0.009, 0.009, 0.0105)
        bare = (0.30, 0.295, 0.29)
        rough_base = 0.44
    else:
        base = (0.06, 0.059, 0.058)
        bare = (0.32, 0.315, 0.305)
        rough_base = 0.6
    # tonal variation (heat bluing / soot) on the blackened finish
    tone = b.ramp((nz2, "Fac"), [(0.3, tuple(c * 0.75 for c in base)), (0.7, tuple(c * 1.6 for c in base))])
    col = b.mix(b.math("MULTIPLY", wearm, 0.85), tone, bare)
    col = b.mix(b.math("MULTIPLY", scr_mask, 0.22), col, bare)
    # grime in cavities, dried mud low down
    mudnz = b.n("ShaderNodeTexNoise", Vector=obj, Scale=11.0, Detail=8.0, Roughness=0.7)
    mudm = b.math("MULTIPLY", mud, b.n("ShaderNodeMapRange", Value=(mudnz, "Fac"), **{"From Min": 0.42, "From Max": 0.62}))
    mudc = (0.075, 0.058, 0.042) if look == "black" else (0.09, 0.07, 0.05)
    col = b.mix(b.math("MULTIPLY", cav, 0.7), col, (0.008, 0.007, 0.006))
    col = b.mix(mudm, col, mudc)
    rough = b.math("ADD", rough_base, b.math("MULTIPLY", b.math("SUBTRACT", (nz2, "Fac"), 0.5), 0.35))
    rough = b.mix(wearm, rough, (0.22, 0.22, 0.22))
    rough = b.mix(mudm, rough, (0.92, 0.92, 0.92))
    metal = b.math("SUBTRACT", 1.0, mudm, clamp=True)
    # bump: pitting + scratches + subtle hammer marks
    pit = b.n("ShaderNodeTexNoise", Vector=obj, Scale=260.0, Detail=2.0)
    ham = b.n("ShaderNodeTexVoronoi", Vector=obj, Scale=28.0)
    hgt = b.math("ADD", b.math("MULTIPLY", (pit, "Fac"), 0.25), b.math("MULTIPLY", (ham, "Distance"), 0.6))
    hgt = b.math("SUBTRACT", hgt, b.math("MULTIPLY", scr_mask, 0.3))
    bump = b.n("ShaderNodeBump", Strength=0.12, Distance=0.002, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Metallic": metal, "Roughness": (rough[0], rough[1]),
                  "Normal": bump})
    bs.inputs["Specular IOR Level"].default_value = 0.5
    b.out(bs)
    _cache[key] = m
    return m


def chainmail(name="chainmail", ring=0.009, look="black"):
    if name in _cache:
        return _cache[name]
    m, b = new(name)
    tc = b.n("ShaderNodeTexCoord")
    uv = b.n("ShaderNodeSeparateXYZ", Vector=(tc, "UV"))
    # ring lattice: offset every other row by half a ring
    u = b.math("DIVIDE", (uv, "X"), ring)
    v = b.math("DIVIDE", (uv, "Y"), ring * 0.8)
    row = b.math("FLOOR", v)
    odd = b.math("MODULO", row, 2.0)
    u2 = b.math("ADD", u, b.math("MULTIPLY", odd, 0.5))
    fu = b.math("SUBTRACT", b.math("FRACT", u2), 0.5)
    fv = b.math("SUBTRACT", b.math("FRACT", v), 0.5)
    d = b.math("SQRT", b.math("ADD", b.math("MULTIPLY", fu, fu), b.math("MULTIPLY", fv, fv)))
    band = b.math("SUBTRACT", 1.0, b.math("ABSOLUTE", b.math("MULTIPLY", b.math("SUBTRACT", d, 0.36), 7.0)), clamp=True)
    # fade the ring relief with distance to avoid shimmer
    cam = b.n("ShaderNodeCameraData")
    fade = b.n("ShaderNodeMapRange", Value=(cam, "View Distance"), **{"From Min": 1.5, "From Max": 6.0,
                                                                       "To Min": 1.0, "To Max": 0.15})
    hgt = b.math("MULTIPLY", band, fade)
    bump = b.n("ShaderNodeBump", Strength=0.9, Distance=0.002, Height=hgt)
    base = (0.03, 0.03, 0.032) if look == "black" else (0.12, 0.12, 0.125)
    col = b.mix(band, (0.004, 0.004, 0.004), base)
    bs = b.bsdf(**{"Base Color": col, "Metallic": 1.0, "Roughness": 0.42, "Normal": bump})
    b.out(bs)
    _cache[name] = m
    return m


def leather(name="leather", color=(0.04, 0.025, 0.016), rough=0.62):
    if name in _cache:
        return _cache[name]
    m, b = new(name)
    tc = b.n("ShaderNodeTexCoord")
    nz = b.n("ShaderNodeTexNoise", Vector=(tc, "Object"), Scale=90.0, Detail=6.0, Roughness=0.7)
    big = b.n("ShaderNodeTexNoise", Vector=(tc, "Object"), Scale=9.0, Detail=3.0)
    wear = b.attr("wear")
    col = b.mix(b.math("MULTIPLY", (big, "Fac"), 0.6), color, tuple(c * 1.9 for c in color))
    col = b.mix(b.math("MULTIPLY", wear, 0.6), col, tuple(c * 2.6 for c in color))
    bump = b.n("ShaderNodeBump", Strength=0.25, Distance=0.002, Height=(nz, "Fac"))
    bs = b.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": bump})
    bs.inputs["Specular IOR Level"].default_value = 0.35
    b.out(bs)
    _cache[name] = m
    return m


def cloth(name="cape", top=(0.075, 0.0055, 0.0065), bottom=(0.012, 0.0028, 0.0028), hem_z=(0.35, 1.0),
          holes=True, sheen=0.6, axis="Z"):
    """Heavy wool: crimson fading to near-black and dirt toward the hem; alpha-clipped tears."""
    if name in _cache:
        return _cache[name]
    m, b = new(name, blend="CLIP" if holes else "OPAQUE")
    m.alpha_threshold = 0.5
    m.use_backface_culling = False
    tc = b.n("ShaderNodeTexCoord")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=(tc, "UV"))
    # UV V runs from the top (0) down the cape in metres
    g = b.n("ShaderNodeMapRange", Value=(sep, "Y"), **{"From Min": hem_z[0], "From Max": hem_z[1] + 0.6})
    weave = b.n("ShaderNodeTexWave", Vector=(tc, "UV"), Scale=420.0, _wave_type="BANDS", _bands_direction="X")
    blot = b.n("ShaderNodeTexNoise", Vector=(tc, "UV"), Scale=4.0, Detail=6.0)
    col = b.mix(g, top, bottom)
    col = b.mix(b.math("MULTIPLY", (blot, "Fac"), 0.5), col, tuple(c * 0.5 for c in bottom))
    bump = b.n("ShaderNodeBump", Strength=0.12, Distance=0.001, Height=(weave, "Fac"))
    bs = b.bsdf(**{"Base Color": col, "Roughness": 0.93, "Normal": bump})
    bs.inputs["Sheen Weight"].default_value = sheen
    bs.inputs["Sheen Tint"].default_value = (1.0, 0.55, 0.5, 1.0)
    bs.inputs["Specular IOR Level"].default_value = 0.25
    if holes:
        hn = b.n("ShaderNodeTexNoise", Vector=(tc, "UV"), Scale=5.5, Detail=8.0, Roughness=0.7)
        # holes only near the hem: threshold rises with V
        th = b.n("ShaderNodeMapRange", Value=(sep, "Y"), **{"From Min": hem_z[1] - 0.25, "From Max": hem_z[1] + 0.35,
                                                          "To Min": 0.0, "To Max": 0.12})
        a = b.math("SUBTRACT", (hn, "Fac"), b.math("SUBTRACT", 0.74, th))
        alpha = b.math("LESS_THAN", a, 0.0)
        bs_in = bs.inputs["Alpha"]
        b.link(alpha, bs_in)
    b.out(bs)
    _cache[name] = m
    return m


def emission(name, color, strength=10.0, ctrl=None):
    if name in _cache:
        return _cache[name]
    m, b = new(name)
    col = hexcol(color) if isinstance(color, str) else color
    em = b.n("ShaderNodeEmission", Color=col, Strength=strength)
    if ctrl:
        c = b.ctrl(ctrl, strength)
        b.link(c, em.inputs["Strength"])
    b.out(em)
    _cache[name] = m
    return m


def matte(name, color, rough=0.8, metal=0.0):
    if name in _cache:
        return _cache[name]
    m, b = new(name)
    bs = b.bsdf(**{"Base Color": color, "Roughness": rough, "Metallic": metal})
    b.out(bs)
    _cache[name] = m
    return m


def blade(name="greatsword_blade", glow=1.0):
    """Black steel blade with a thin jagged ember crack along the blade centre.
    Object space: blade length along +Z, width along X, thickness along Y.
    CTRL_crack_glow scales the emission (0 = cold, 1 = faint, 6+ = blazing)."""
    if name in _cache:
        return _cache[name]
    m, b = new(name)
    tc = b.n("ShaderNodeTexCoord")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=(tc, "Object"))
    zv = b.n("ShaderNodeCombineXYZ", X=0.0, Y=0.0, Z=(sep, "Z"))
    n1 = b.n("ShaderNodeTexNoise", Vector=zv, Scale=9.0, Detail=3.0)
    n2 = b.n("ShaderNodeTexNoise", Vector=zv, Scale=48.0, Detail=2.0)
    n3 = b.n("ShaderNodeTexNoise", Vector=zv, Scale=150.0, Detail=0.0)
    off = b.math("ADD", b.math("MULTIPLY", b.math("SUBTRACT", (n1, "Fac"), 0.5), 0.016),
                 b.math("MULTIPLY", b.math("SUBTRACT", (n2, "Fac"), 0.5), 0.008))
    off = b.math("ADD", off, b.math("MULTIPLY", b.math("SUBTRACT", (n3, "Fac"), 0.5), 0.005))
    dx = b.math("ABSOLUTE", b.math("SUBTRACT", (sep, "X"), off))
    core = b.n("ShaderNodeMapRange", Value=dx, **{"From Min": 0.0004, "From Max": 0.0016, "To Min": 1.0, "To Max": 0.0})
    halo = b.n("ShaderNodeMapRange", Value=dx, **{"From Min": 0.001, "From Max": 0.006, "To Min": 1.0, "To Max": 0.0})
    # crack runs from 0.12 m above the guard to 0.18 m before the tip; flickers along length
    span = b.math("MULTIPLY", b.n("ShaderNodeMapRange", Value=(sep, "Z"), **{"From Min": 0.10, "From Max": 0.20}),
                  b.n("ShaderNodeMapRange", Value=(sep, "Z"), **{"From Min": 1.30, "From Max": 1.18}))
    flick = b.n("ShaderNodeTexNoise", Vector=zv, Scale=7.0, Detail=1.0)
    span = b.math("MULTIPLY", span, b.n("ShaderNodeMapRange", Value=(flick, "Fac"), **{"From Min": 0.40, "From Max": 0.5,
                                                                                         "To Min": 0.0, "To Max": 1.0}))
    glow_c = b.ctrl("crack_glow", glow)
    estr = b.math("MULTIPLY", b.math("MULTIPLY", core, span), b.math("MULTIPLY", glow_c, 24.0))
    wear = b.attr("wear")
    col = b.mix(b.math("MULTIPLY", wear, 1.4), (0.014, 0.014, 0.016), (0.45, 0.44, 0.43))
    col = b.mix(b.math("MULTIPLY", halo, span), col, (0.01, 0.003, 0.0))
    nz = b.n("ShaderNodeTexNoise", Vector=(tc, "Object"), Scale=60.0, Detail=4.0)
    rough = b.math("ADD", 0.28, b.math("MULTIPLY", (nz, "Fac"), 0.2))
    bump = b.n("ShaderNodeBump", Strength=0.08, Distance=0.001, Height=(nz, "Fac"))
    bs = b.bsdf(**{"Base Color": col, "Metallic": 1.0, "Roughness": rough, "Normal": bump})
    bs.inputs["Emission Color"].default_value = (*hexcol("#FF6A1A"), 1.0)
    b.link(estr, bs.inputs["Emission Strength"])
    b.out(bs)
    _cache[name] = m
    return m


def stone_god(name="god_stone"):
    """Pale cracked stone; black void and cold blue light inside the cracks.
    CTRL_ignite = world height (m) below which cracks glow; CTRL_glow = intensity."""
    if name in _cache:
        return _cache[name]
    m, b = new(name)
    tc = b.n("ShaderNodeTexCoord")
    obj = (tc, "Object")
    geo = b.n("ShaderNodeNewGeometry")
    wz = b.n("ShaderNodeSeparateXYZ", Vector=(geo, "Position"))
    warp = b.n("ShaderNodeTexNoise", Vector=obj, Scale=1.6, Detail=3.0)
    wv = b.n("ShaderNodeVectorMath", _operation="ADD")
    b.link(obj, wv.inputs[0])
    b.link((warp, "Color"), wv.inputs[1])
    vor = b.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=2.2)
    b.link((wv, "Vector"), vor.inputs["Vector"])
    vor2 = b.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=7.0)
    b.link((wv, "Vector"), vor2.inputs["Vector"])
    big = b.n("ShaderNodeMapRange", Value=(vor, "Distance"), **{"From Min": 0.002, "From Max": 0.012, "To Min": 1.0, "To Max": 0.0})
    small = b.n("ShaderNodeMapRange", Value=(vor2, "Distance"), **{"From Min": 0.0, "From Max": 0.007, "To Min": 0.8, "To Max": 0.0})
    gate = b.n("ShaderNodeTexNoise", Vector=obj, Scale=0.9, Detail=2.0)
    gatem = b.n("ShaderNodeMapRange", Value=(gate, "Fac"), **{"From Min": 0.52, "From Max": 0.62})
    gate2 = b.n("ShaderNodeTexNoise", Vector=obj, Scale=0.6, Detail=1.0)
    gatem2 = b.n("ShaderNodeMapRange", Value=(gate2, "Fac"), **{"From Min": 0.38, "From Max": 0.5})
    crack = b.math("MAXIMUM", b.math("MULTIPLY", big, gatem2), b.math("MULTIPLY", small, gatem))
    crack = b.math("MINIMUM", crack, 1.0)
    # ignite mask from world height
    ig = b.ctrl("ignite", 100.0)
    below = b.math("SUBTRACT", ig, (wz, "Z"))
    igm = b.n("ShaderNodeMapRange", Value=below, **{"From Min": -0.05, "From Max": 0.6})
    gl = b.ctrl("glow", 1.0)
    estr = b.math("MULTIPLY", b.math("MULTIPLY", crack, igm), b.math("MULTIPLY", gl, 14.0))
    snz = b.n("ShaderNodeTexNoise", Vector=obj, Scale=5.0, Detail=10.0, Roughness=0.65)
    stone = b.ramp((snz, "Fac"), [(0.3, (0.2, 0.19, 0.18)), (0.55, (0.4, 0.385, 0.36)), (0.8, (0.5, 0.49, 0.46))])
    # weathering: vertical rain streaks and blotchy grime
    smp = b.n("ShaderNodeMapping", Vector=obj, Scale=(6.0, 6.0, 0.35))
    streak = b.n("ShaderNodeTexNoise", Vector=smp, Scale=4.0, Detail=6.0, Roughness=0.6)
    stk = b.n("ShaderNodeMapRange", Value=(streak, "Fac"), **{"From Min": 0.45, "From Max": 0.7, "To Min": 1.0, "To Max": 0.55})
    stone = b.mix(1.0, stone, stk, blend="MULTIPLY")
    cav = b.attr("cav")
    col = b.mix(b.math("MULTIPLY", cav, 0.8), stone, (0.06, 0.06, 0.065))
    col = b.mix(crack, col, (0.0, 0.0, 0.0))
    fine = b.n("ShaderNodeTexNoise", Vector=obj, Scale=40.0, Detail=8.0)
    pits = b.n("ShaderNodeTexVoronoi", Vector=obj, Scale=60.0)
    pitm = b.n("ShaderNodeMapRange", Value=(pits, "Distance"), **{"From Min": 0.0, "From Max": 0.12, "To Min": -0.5, "To Max": 0.0})
    hgt = b.math("SUBTRACT", b.math("ADD", b.math("MULTIPLY", (fine, "Fac"), 0.4), pitm), b.math("MULTIPLY", crack, 0.9))
    bump = b.n("ShaderNodeBump", Strength=0.45, Distance=0.01, Height=hgt)
    bs = b.bsdf(**{"Base Color": col, "Roughness": 0.86, "Normal": bump})
    bs.inputs["Emission Color"].default_value = (*hexcol("#6FA8FF"), 1.0)
    b.link(estr, bs.inputs["Emission Strength"])
    bs.inputs["Specular IOR Level"].default_value = 0.35
    b.out(bs)
    _cache[name] = m
    return m


def obsidian(name="obsidian"):
    if name in _cache:
        return _cache[name]
    m, b = new(name)
    wear = b.attr("wear")
    tc = b.n("ShaderNodeTexCoord")
    nz = b.n("ShaderNodeTexNoise", Vector=(tc, "Object"), Scale=3.0, Detail=6.0)
    edge = b.math("MULTIPLY", b.math("POWER", wear, 2.0), 3.0)
    bs = b.bsdf(**{"Base Color": (0.004, 0.004, 0.006), "Roughness": b.math("ADD", 0.04, b.math("MULTIPLY", (nz, "Fac"), 0.08))})
    bs.inputs["Specular IOR Level"].default_value = 0.9
    bs.inputs["Coat Weight"].default_value = 1.0
    bs.inputs["Coat Roughness"].default_value = 0.03
    bs.inputs["Emission Color"].default_value = (*hexcol("#6FA8FF"), 1.0)
    gl = b.ctrl("edge_glow", 1.0)
    b.link(b.math("MULTIPLY", edge, gl), bs.inputs["Emission Strength"])
    b.out(bs)
    _cache[name] = m
    return m


def robe(name="god_robe", top=(0.016, 0.018, 0.026), bottom=(0.006, 0.007, 0.01), z_range=(0.0, 3.5)):
    """Tattered dark robe (Object-space height gradient; ragged alpha near the hem)."""
    if name in _cache:
        return _cache[name]
    m, b = new(name, blend="CLIP")
    m.alpha_threshold = 0.5
    m.use_backface_culling = False
    tc = b.n("ShaderNodeTexCoord")
    sep = b.n("ShaderNodeSeparateXYZ", Vector=(tc, "Object"))
    g = b.n("ShaderNodeMapRange", Value=(sep, "Z"), **{"From Min": z_range[0], "From Max": z_range[1]})
    col = b.mix(g, bottom, top)
    nz = b.n("ShaderNodeTexNoise", Vector=(tc, "Object"), Scale=3.0, Detail=8.0, Roughness=0.7)
    hem = b.n("ShaderNodeMapRange", Value=(sep, "Z"), **{"From Min": z_range[0] + 0.05, "From Max": z_range[0] + 0.7,
                                                       "To Min": 0.32, "To Max": 0.0})
    alpha = b.math("GREATER_THAN", (nz, "Fac"), b.math("ADD", 0.5, b.math("MULTIPLY", hem, -1.0)))
    alpha = b.math("SUBTRACT", 1.0, b.math("MULTIPLY", b.math("GREATER_THAN", hem, 0.01),
                                          b.math("LESS_THAN", (nz, "Fac"), b.math("ADD", 0.25, hem))))
    weave = b.n("ShaderNodeTexWave", Vector=(tc, "Object"), Scale=160.0, _wave_type="BANDS")
    # large hanging folds (vertical bands with distortion, two directions around the body) + crumpled wrinkles,
    # so the heavy cloth reads as cloth under the god's hard underlight instead of a smooth sheet
    fx = b.n("ShaderNodeTexWave", Vector=(tc, "Object"), Scale=2.6, Distortion=7.0, **{"Detail": 3.0},
             _wave_type="BANDS", _bands_direction="X")
    fy = b.n("ShaderNodeTexWave", Vector=(tc, "Object"), Scale=2.2, Distortion=6.0, **{"Detail": 3.0},
             _wave_type="BANDS", _bands_direction="Y")
    wr = b.n("ShaderNodeTexNoise", Vector=(tc, "Object"), Scale=9.0, Detail=6.0, Roughness=0.6)
    h = b.math("ADD", b.math("MULTIPLY", b.math("ADD", (fx, "Fac"), (fy, "Fac")), 0.5),
               b.math("ADD", b.math("MULTIPLY", (wr, "Fac"), 0.35), b.math("MULTIPLY", (weave, "Fac"), 0.06)))
    bump = b.n("ShaderNodeBump", Strength=0.45, Distance=0.06, Height=h)
    bs = b.bsdf(**{"Base Color": col, "Roughness": 0.92, "Normal": bump, "Alpha": alpha})
    bs.inputs["Sheen Weight"].default_value = 0.5
    bs.inputs["Specular IOR Level"].default_value = 0.2
    b.out(bs)
    _cache[name] = m
    return m
