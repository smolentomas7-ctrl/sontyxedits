"""Procedural mesh construction: lofted shells, limb tubes, plate finishing,
edge-wear / mud attributes, rolled edges, rivets, seeded dents.

All shapes are built from parametric grids (rows of rings) so pieces get clean
quad topology and metre-scaled UVs, then finished with solidify + bevel +
subdivision and baked attributes the materials read.
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

from rb_core import link


# ------------------------------------------------------------------ grids
def grid_mesh(name, P, closed_u=False, cap_start=False, cap_end=False, uv=True, smooth=True, skip=None):
    """P: array (rows, cols, 3). Rows run along v, columns along u.
    skip(i, j) -> True removes the quad (i..i+1, j..j+1) (for slits / holes)."""
    P = np.asarray(P, dtype=float)
    R, C = P.shape[:2]
    me = bpy.data.meshes.new(name)
    verts = P.reshape(-1, 3).tolist()
    faces = []
    cu = C if closed_u else C - 1
    for i in range(R - 1):
        for j in range(cu):
            if skip is not None and skip(i, j):
                continue
            j2 = (j + 1) % C
            faces.append((i * C + j, i * C + j2, (i + 1) * C + j2, (i + 1) * C + j))
    nv = len(verts)
    if cap_start:
        c = P[0].mean(0)
        verts.append(c.tolist())
        ci = len(verts) - 1
        for j in range(cu):
            faces.append((ci, (j + 1) % C, j))
    if cap_end:
        c = P[-1].mean(0)
        verts.append(c.tolist())
        ci = len(verts) - 1
        base = (R - 1) * C
        for j in range(cu):
            faces.append((ci, base + j, base + (j + 1) % C))
    me.from_pydata(verts, [], faces)
    me.update()
    if uv:
        # metre-scaled UVs: u = arc length along the row, v = distance along columns
        uvl = me.uv_layers.new(name="UVMap")
        U = np.zeros((R, C))
        V = np.zeros((R, C))
        U[:, 1:] = np.cumsum(np.linalg.norm(np.diff(P, axis=1), axis=2), axis=1)
        V[1:, :] = np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=2), axis=0)
        for poly in me.polygons:
            for li in poly.loop_indices:
                vi = me.loops[li].vertex_index
                if vi < nv:
                    r, c = divmod(vi, C)
                    uvl.data[li].uv = (U[r, c], V[r, c])
                else:
                    uvl.data[li].uv = (0.0, 0.0)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if skip is not None:
        # drop vertices orphaned by skipped faces (loose verts would free-fall in cloth sims)
        bm = bmesh.new()
        bm.from_mesh(me)
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")
            bm.to_mesh(me)
        bm.free()
    ob = bpy.data.objects.new(name, me)
    link(ob)
    return ob


def superellipse(a, b, n, N, t0=0.0, t1=2 * math.pi, closed=True):
    """Points of |x/a|^n + |y/b|^n = 1 (in the XY plane), N samples from angle t0 to t1."""
    ts = np.linspace(t0, t1, N, endpoint=not closed)
    c, s = np.cos(ts), np.sin(ts)
    x = a * np.sign(c) * np.abs(c) ** (2.0 / n)
    y = b * np.sign(s) * np.abs(s) ** (2.0 / n)
    return np.stack([x, y], 1), ts


def frame_from_axis(axis, up_hint=(0, -1, 0)):
    """Orthonormal frame (X, Y, Z=axis) with X roughly toward up_hint."""
    z = Vector(axis).normalized()
    u = Vector(up_hint)
    if abs(z.dot(u.normalized())) > 0.95:
        u = Vector((1, 0, 0)) if abs(z.x) < 0.9 else Vector((0, 0, 1))
    x = (u - z * u.dot(z)).normalized()
    y = z.cross(x)
    return np.array(x), np.array(y), np.array(z)


def tube(name, p0, p1, radius, N=48, M=24, arc=(0, 2 * math.pi), front=(0, -1, 0), shape=None,
         closed=None, **kw):
    """Loft along the segment p0->p1. radius(t, theta) -> r (t in 0..1 along, theta around,
    theta=0 points to `front`). Optional shape(t, theta) -> (dx, dy) extra offset in the ring frame."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    ax = p1 - p0
    X, Y, Z = frame_from_axis(ax, front)
    full = abs((arc[1] - arc[0]) - 2 * math.pi) < 1e-6
    if closed is None:
        closed = full
    ths = np.linspace(arc[0], arc[1], N, endpoint=not closed)
    P = np.zeros((M, N, 3))
    for i, t in enumerate(np.linspace(0, 1, M)):
        c = p0 + ax * t
        for j, th in enumerate(ths):
            r = radius(t, th) if callable(radius) else radius
            dx, dy = (shape(t, th) if shape else (0.0, 0.0))
            P[i, j] = c + X * (math.cos(th) * r + dx) + Y * (math.sin(th) * r + dy)
    return grid_mesh(name, P, closed_u=closed, **kw)


# ------------------------------------------------------------------ finishing
def add_mod(ob, kind, **props):
    m = ob.modifiers.new(kind.lower(), kind)
    for k, v in props.items():
        setattr(m, k, v)
    return m


def apply_all(ob):
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    for m in list(ob.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def finish_plate(ob, thick=0.004, bevel=0.0015, subsurf=1, offset=1.0, apply=True, weighted=True):
    """Give a surface shell real thickness, rounded edges and smooth form."""
    if thick:
        add_mod(ob, "SOLIDIFY", thickness=thick, offset=offset, use_even_offset=True, use_quality_normals=True)
    if bevel:
        add_mod(ob, "BEVEL", width=bevel, segments=2, limit_method="ANGLE", angle_limit=math.radians(40))
    if subsurf:
        add_mod(ob, "SUBSURF", levels=subsurf, render_levels=subsurf, quality=3)
    if apply:
        apply_all(ob)
        if weighted:
            for p in ob.data.polygons:
                p.use_smooth = True
    return ob


def dents(ob, seed, count=6, depth=0.004, radius=(0.02, 0.06)):
    """Seeded shallow dents pushed along vertex normals (call before solidify)."""
    r = random.Random(seed)
    me = ob.data
    if not len(me.vertices):
        return
    me.calc_normals_split() if hasattr(me, "calc_normals_split") else None
    pts = [v.co.copy() for v in me.vertices]
    centers = [pts[r.randrange(len(pts))] for _ in range(count)]
    rads = [r.uniform(*radius) for _ in range(count)]
    deps = [depth * r.uniform(0.4, 1.0) for _ in range(count)]
    for v in me.vertices:
        d = 0.0
        for c, rr, dd in zip(centers, rads, deps):
            q = (v.co - c).length / rr
            if q < 1.5:
                d += dd * math.exp(-q * q * 2.5)
        if d:
            v.co -= v.normal * d
    me.update()


def bake_attributes(ob, mud_top=0.5, mud_floor=0.0, wear_gain=7.0, world=True, wear_scale=1.0):
    """Float point attributes read by the materials:
       wear = convexity (edges / ridges catch bare metal),
       mud  = low parts of the body (dried mud), from world Z,
       cav  = concavity (soot / grime collects)."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.normal_update()
    conv = np.zeros(len(bm.verts))
    for v in bm.verts:
        if not v.link_edges:
            continue
        acc = 0.0
        for e in v.link_edges:
            u = e.other_vert(v)
            d = v.co - u.co
            L = d.length
            if L > 1e-9:
                acc += v.normal.dot(d / L)
        conv[v.index] = acc / len(v.link_edges)
    # one smoothing pass
    sm = conv.copy()
    for v in bm.verts:
        if v.link_edges:
            sm[v.index] = 0.5 * conv[v.index] + 0.5 * np.mean([conv[e.other_vert(v).index] for e in v.link_edges])
    bm.free()
    wear = np.clip(sm * wear_gain, 0, 1) * wear_scale
    cav = np.clip(-sm * wear_gain, 0, 1)
    mw = ob.matrix_world
    z = np.array([(mw @ v.co).z if world else v.co.z for v in me.vertices])
    mud = np.clip((mud_top - z) / max(1e-6, mud_top - mud_floor), 0, 1) if mud_top else np.zeros(len(z))
    for nm, arr in (("wear", wear), ("mud", mud), ("cav", cav)):
        a = me.attributes.get(nm) or me.attributes.new(nm, "FLOAT", "POINT")
        a.data.foreach_set("value", arr.astype(np.float32))
    return ob


# ------------------------------------------------------------------ details
def curve_tube(name, pts, radius=0.003, closed=False, res=6, mat=None):
    """Tube along a polyline (rolled plate edges, straps, rims)."""
    cd = bpy.data.curves.new(name, "CURVE")
    cd.dimensions = "3D"
    cd.bevel_depth = radius
    cd.bevel_resolution = 2
    cd.resolution_u = 2
    sp = cd.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (q[0], q[1], q[2], 1.0)
    sp.use_cyclic_u = closed
    ob = bpy.data.objects.new(name, cd)
    link(ob)
    if mat:
        cd.materials.append(mat)
    # convert to mesh
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.ops.object.convert(target="MESH")
    ob = bpy.context.view_layer.objects.active
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def boundary_loops(ob):
    """Ordered boundary vertex loops (world coords) of an open shell."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    edges = [e for e in bm.edges if e.is_boundary]
    adj = {}
    for e in edges:
        a, b = e.verts
        adj.setdefault(a.index, []).append(b.index)
        adj.setdefault(b.index, []).append(a.index)
    co = {v.index: v.co.copy() for v in bm.verts}
    bm.free()
    loops, seen = [], set()
    for s in adj:
        if s in seen:
            continue
        loop = [s]
        seen.add(s)
        prev, cur = None, s
        while True:
            nxt = [n for n in adj[cur] if n != prev and n not in seen]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            loop.append(cur)
            seen.add(cur)
        mw = ob.matrix_world
        loops.append([tuple(mw @ co[i]) for i in loop])
    return loops


def rivets(name, pts, normals, radius=0.0045, mat=None):
    """Domed rivet heads at points, oriented along normals; one merged object."""
    bm = bmesh.new()
    for p, n in zip(pts, normals):
        m = Matrix.Translation(Vector(p)) @ Vector(n).to_track_quat("Z", "Y").to_matrix().to_4x4()
        geom = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=radius, matrix=m)
        vs = geom["verts"]
        # flatten into a dome (squash along local Z and drop the lower half into the plate)
        for v in vs:
            loc = m.inverted() @ v.co
            loc.z = max(loc.z, -radius * 0.1) * 0.55
            v.co = m @ loc
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    link(ob)
    if mat:
        me.materials.append(mat)
    return ob


def join(objs, name):
    objs = [o for o in objs if o is not None]
    bpy.context.view_layer.objects.active = objs[0]
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    ob.data.name = name
    return ob


def set_mat(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    return ob


def ellipsoid_cap(name, center, radii, axis=(0, 0, 1), up=(0, -1, 0), polar=(0.0, 1.2), N=48, M=20,
                  azim=(0, 2 * math.pi), bump=None, **kw):
    """Part of an ellipsoid: polar angle range from `axis`, azimuth range. radii=(rx, ry, rz) in the cap frame
    (Z along axis, X toward `up`)."""
    X, Y, Z = frame_from_axis(axis, up)
    full = abs(azim[1] - azim[0] - 2 * math.pi) < 1e-6
    phs = np.linspace(azim[0], azim[1], N, endpoint=not full)
    P = np.zeros((M, N, 3))
    for i, th in enumerate(np.linspace(polar[0], polar[1], M)):
        for j, ph in enumerate(phs):
            lx = radii[0] * math.sin(th) * math.cos(ph)
            ly = radii[1] * math.sin(th) * math.sin(ph)
            lz = radii[2] * math.cos(th)
            if bump:
                s = bump(th, ph)
                lx, ly, lz = lx * s, ly * s, lz * s
            P[i, j] = np.array(center) + X * lx + Y * ly + Z * lz
    if polar[0] < 1e-6:
        P[0, :] = P[0, 0]
    return grid_mesh(name, P, closed_u=full, **kw)
