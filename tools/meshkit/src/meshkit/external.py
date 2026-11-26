"""Second opinions on every GLB, from loaders that are not Blender.

The gate's round trip compares Blender's export with Blender's own import. That
is the right pairing for kinema, but it is one program checking itself: an
exporter bug mirrored by the importer would cancel out and pass. trimesh reads
glTF independently, so the GLB is also loaded here, outside Blender, and its
triangle count and surface area must agree with the source's.

Neither check can see a fault in the *import*, though: the round trip starts
from what kinema's importer produced, so an importer that loses something hands
the loss to both sides. That is not hypothetical -- kinema's importer averaged
every file's authored normals away (fixed in kinema#126), and the geometry checks all
passed. So the shading is also compared end to end, the raw .dae read by
pycollada against the GLB read by trimesh, with no Blender in between.

Only frame-independent quantities are compared. trimesh keeps glTF's Y-up
coordinates as stored, and a .dae carries its own units and up axis, so
positions would differ by design and prove nothing. Normals are summarised the
same way -- see ``normal_deviation``.
"""

from __future__ import annotations

import copy
import io
from pathlib import Path

import numpy as np
import trimesh

from meshkit.polygon import triangulate

# Percentiles of the normal-deviation distribution the gate compares.
QUANTILES = (50, 90, 99)


def normal_deviation(triangles: np.ndarray, normals: np.ndarray,
                     quantiles: tuple[int, ...] = QUANTILES) -> list[float]:
    """Percentiles of the angle, in degrees, between each corner normal and its face.

    ``triangles`` and ``normals`` are (n, 3, 3): three corners per triangle. The
    angle between a corner's normal and its own triangle's geometric normal does
    not change under rotation, uniform scale or a change of up axis, so a .dae
    and its GLB can be compared without agreeing on a frame, and without
    matching vertices up. Averaging normals across hard edges moves it a lot: a
    flat-shaded link goes from ~0 degrees everywhere to tens of degrees.

    Degenerate triangles have no face normal and are left out.
    """
    edge = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    length = np.linalg.norm(edge, axis=1)
    keep = length > 1e-12
    if not keep.any():
        return [0.0] * len(quantiles)
    face = edge[keep] / length[keep, None]
    corner = normals[keep]
    corner_length = np.linalg.norm(corner, axis=2)
    corner = corner / np.where(corner_length > 0, corner_length, 1.0)[..., None]
    cosine = np.clip((corner * face[:, None, :]).sum(axis=2), -1.0, 1.0)
    angles = np.degrees(np.arccos(cosine)).ravel()
    return [float(v) for v in np.percentile(angles, quantiles)]


def plain_stats(path: Path) -> dict:
    """An STL or OBJ as written, read without Blender: the mesh a weld leaves of it.

    The same quantities as Blender's ``world_stats`` -- triangle count, area,
    area-weighted centroid and bounds -- so the import can be checked against
    the file with no Blender in between. Both formats are read raw, in the
    link's frame, as ROS reads them, so positions compare directly.

    The count is of the triangles the job keeps (``job.weld``): in each object,
    corners at the same position are joined, and a triangle left with a
    repeated corner, or on the same three corners as an earlier one, is
    dropped (``_kept_faces``). Per object, because Blender welds each object
    on its own: two OBJ objects may each keep a face where they touch. An STL
    is one object, read by trimesh; an OBJ's objects are read by
    ``_obj_objects``. ``file_triangles`` is the count before any of that.
    """
    if path.suffix.lower() == ".obj":
        objects = _obj_objects(path)
        loader = "meshkit OBJ reader"
    else:
        scene = trimesh.load(str(path), force="scene", process=False)
        pieces: list[np.ndarray] = []
        for node_name in scene.graph.nodes_geometry:
            transform, geometry_name = scene.graph[node_name]
            geometry = scene.geometry[geometry_name]
            faces = getattr(geometry, "faces", None)
            if faces is None or len(faces) == 0:
                continue
            vertices = np.asarray(geometry.vertices, dtype=np.float64)
            vertices = vertices @ transform[:3, :3].T + transform[:3, 3]
            pieces.append(vertices[faces])
        objects = [np.concatenate(pieces)] if pieces else []
        loader = f"trimesh {trimesh.__version__}"
    if not objects:
        return {"triangles": 0, "file_triangles": 0, "area": 0.0, "centroid": None,
                "aabb_min": None, "aabb_max": None, "loader": loader}
    kept = []
    for corners in objects:
        _, index = np.unique(corners.reshape(-1, 3), axis=0, return_inverse=True)
        kept.append(corners[_kept_faces(index.reshape(-1, 3))])
    tri = np.concatenate(kept)
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    each = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    area = float(each.sum())
    points = tri.reshape(-1, 3)
    centroid = ((each[:, None] * (a + b + c) / 3.0).sum(axis=0) / area if area > 0
                else points.mean(axis=0))
    return {
        "triangles": int(len(tri)),
        "file_triangles": int(sum(len(o) for o in objects)),
        "area": area,
        "centroid": [float(v) for v in centroid],
        "aabb_min": [float(v) for v in points.min(axis=0)],
        "aabb_max": [float(v) for v in points.max(axis=0)],
        "loader": loader,
    }


def _obj_objects(path: Path) -> list[np.ndarray]:
    """An OBJ's triangles as Blender's importer groups them: (n, 3, 3) per object.

    trimesh regroups an OBJ's faces by material and does not keep its objects
    apart, so the file is read here: ``v`` and ``f`` lines, negative indices
    counted back from the latest vertex, and a new object at each ``o``, as
    the job imports with ``use_split_objects`` (``g`` does not split, since
    ``use_split_groups`` is off). A ``#`` starts a comment anywhere on a line.
    A polygon is split into triangles by ``polygon.triangulate``, the function
    the job splits it with, so a concave one keeps its area and a warped one
    becomes the same triangles on both sides.
    """
    # A trailing backslash continues the line, as in Blender's reader.
    text = path.read_text(encoding="utf-8", errors="replace").replace("\\\n", " ")
    vertices: list[list[float]] = []
    objects: list[list[list[int]]] = [[]]
    for line in text.splitlines():
        parts = line.split("#", 1)[0].split()
        if not parts:
            continue
        if parts[0] == "v":
            vertices.append([float(x) for x in parts[1:4]])
        elif parts[0] == "o":
            if objects[-1]:
                objects.append([])
        elif parts[0] == "f":
            corners = []
            for token in parts[1:]:
                number = int(token.split("/")[0])
                corners.append(number - 1 if number > 0 else len(vertices) + number)
            if len(corners) >= 3:
                objects[-1].append(corners)
    points = np.asarray(vertices, dtype=np.float64).reshape(-1, 3)
    result = []
    for polygons in objects:
        faces = [(polygon[a], polygon[b], polygon[c]) for polygon in polygons
                 for a, b, c in triangulate(points[polygon])]
        if faces:
            result.append(points[np.asarray(faces)])
    return result


def glb_stats(path: Path) -> dict:
    """Triangle count, surface area and normal deviation of a GLB, transforms applied."""
    # process=False: no vertex merging or cleanup, so the numbers describe the
    # file as written rather than a repaired copy of it.
    scene = trimesh.load(str(path), force="scene", process=False)
    triangles: list[np.ndarray] = []
    normals: list[np.ndarray] = []
    for node_name in scene.graph.nodes_geometry:
        transform, geometry_name = scene.graph[node_name]
        geometry = scene.geometry[geometry_name]
        faces = getattr(geometry, "faces", None)
        if faces is None or len(faces) == 0:
            continue
        linear = transform[:3, :3]
        vertices = geometry.vertices @ linear.T + transform[:3, 3]
        # Normals transform by the inverse transpose; row vectors, so no .T.
        vertex_normals = np.asarray(geometry.vertex_normals) @ np.linalg.inv(linear)
        triangles.append(vertices[faces])
        normals.append(vertex_normals[faces])
    if not triangles:
        return {"triangles": 0, "area": 0.0, "normal_deviation": None,
                "loader": f"trimesh {trimesh.__version__}"}
    tri = np.concatenate(triangles)
    area = float(0.5 * np.linalg.norm(
        np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1).sum())
    corner_normals = np.concatenate(normals)
    return {
        "triangles": int(len(tri)),
        "area": area,
        "normal_deviation": normal_deviation(tri, corner_normals),
        "normal_deviation_max": normal_deviation(tri, corner_normals, (100,))[0],
        "loader": f"trimesh {trimesh.__version__}",
    }


# Degrees. A face whose normal float32 arithmetic can leave this uncertain
# (``_fan_error``) says nothing reliable about the normals next to it.
UNCERTAIN_FACE = 5.0
# Degrees either side of the smoothing angle: an edge this close to it could
# go either way, so both are allowed.
ANGLE_BAND = 0.01
# Degrees. A corner whose fan depends on such edges is checked against all of
# them smooth and all of them sharp; it counts as matching one within this.
# One that matches neither may be a mix of the two, which is not rebuilt, so
# it is left unchecked rather than failed.
BAND_MATCH = 1.0


def smoothing_error(path: Path, angle: float) -> dict:
    """How far each corner normal of a GLB lies from what smoothing at ``angle`` makes.

    Smoothing by angle is a rule that can be reproduced: an edge is sharp
    where its two faces meet at more than ``angle`` (or where it is not shared
    by exactly two consistently wound faces); at each vertex, faces joined by
    edges that are not sharp form a fan; and each corner's normal is the fan's
    face normals, weighted by each face's angle at the vertex -- Blender's rule.
    This rebuilds that from the GLB's own triangles, read by trimesh, and
    measures every corner against it. Normals left flat and normals averaged
    across sharp edges both show, and a cone's tip is no exception: there the
    rule itself points the normal up the axis.

    Each glTF mesh is rebuilt whole, its primitives (one per material) joined,
    since Blender smoothed it as one object.

    Corners at a vertex of a face whose float32 normal is uncertain by more
    than ``UNCERTAIN_FACE`` degrees are left out (``unchecked``): Blender's
    sharp-edge choices next to such slivers are rounding noise. So is a corner
    whose fan turns on edges within ``ANGLE_BAND`` of the angle and which
    matches neither all of them smooth nor all of them sharp. On G1 and the
    KR 16 that is 2% of corners, most of them on the KR 16's sub-micrometre
    triangles.
    """
    scene = trimesh.load(str(path), force="scene", process=False)
    parents = scene.graph.transforms.parents
    meshes: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {}
    for node_name in scene.graph.nodes_geometry:
        transform, geometry_name = scene.graph[node_name]
        geometry = scene.geometry[geometry_name]
        faces = getattr(geometry, "faces", None)
        if faces is None or len(faces) == 0:
            continue
        # trimesh hangs a glTF mesh's primitives under the mesh's node.
        key = (parents.get(node_name, node_name)
               if geometry.metadata.get("from_gltf_primitive") else node_name)
        linear = transform[:3, :3]
        vertices = np.asarray(geometry.vertices, dtype=np.float64) @ linear.T + transform[:3, 3]
        normals = np.asarray(geometry.vertex_normals, dtype=np.float64) @ np.linalg.inv(linear)
        meshes.setdefault(key, []).append((vertices[faces], normals[faces]))
    errors, unchecked, ambiguous = [], 0, 0
    for parts in meshes.values():
        error, skipped, unsure = _fan_error(np.concatenate([t for t, _ in parts]),
                                            np.concatenate([n for _, n in parts]), angle)
        errors.append(error)
        unchecked += skipped
        ambiguous += unsure
    error = np.concatenate(errors) if errors else np.zeros(0)
    return {
        "corners": int(len(error)),
        "unchecked": unchecked,
        "ambiguous_edges": ambiguous,
        "p99_9": float(np.percentile(error, 99.9)) if len(error) else None,
        "max": float(error.max()) if len(error) else None,
    }


def _fan_error(tri: np.ndarray, normals: np.ndarray, angle: float
               ) -> tuple[np.ndarray, int, int]:
    """Per checked corner, degrees from the smoothed normal; corners left out; edges unsure.

    ``tri`` and ``normals`` are (n, 3, 3), one mesh. See ``smoothing_error``.
    """
    count = len(tri)
    _, vertex = np.unique(tri.reshape(-1, 3), axis=0, return_inverse=True)
    vertex = vertex.reshape(count, 3)
    cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    length = np.linalg.norm(cross, axis=1)
    valid = length > 0
    face = np.where(valid[:, None], cross / np.where(valid, length, 1.0)[:, None], 0.0)

    # How far float32 rounding can turn each face's normal: the cross product's
    # error, from its edges and from where they lie, over its length.
    sides = np.sort(np.stack([np.linalg.norm(tri[:, (i + 1) % 3] - tri[:, i], axis=1)
                              for i in range(3)], axis=1), axis=1)
    reach = np.abs(tri).max(axis=(1, 2))
    eps = float(np.finfo(np.float32).eps)
    with np.errstate(divide="ignore", invalid="ignore"):
        doubt = np.degrees(eps * sides[:, 2] * (sides[:, 1] + 4 * reach) / length)
    unsure_face = ~valid | (doubt > UNCERTAIN_FACE)

    weight = np.empty((count, 3))
    for i in range(3):
        a, b = tri[:, (i + 1) % 3] - tri[:, i], tri[:, (i + 2) % 3] - tri[:, i]
        weight[:, i] = np.arctan2(np.linalg.norm(np.cross(a, b), axis=1), (a * b).sum(axis=1))

    # Directed edge e = face * 3 + i runs from corner e to corner next(e).
    start, end = vertex.ravel(), vertex[:, [1, 2, 0]].ravel()
    low, high = np.minimum(start, end), np.maximum(start, end)
    order = np.lexsort((high, low))
    new = np.r_[True, (low[order][1:] != low[order][:-1]) | (high[order][1:] != high[order][:-1])]
    group = np.cumsum(new) - 1
    first = np.flatnonzero(new)
    twin = np.bincount(group)[group[first]] == 2
    e1, e2 = order[first[twin]], order[first[twin] + 1]
    wound = start[e1] == end[e2]                 # the two faces agree on orientation
    e1, e2 = e1[wound], e2[wound]
    f1, f2 = e1 // 3, e2 // 3
    dihedral = np.degrees(np.arccos(np.clip((face[f1] * face[f2]).sum(axis=1), -1.0, 1.0)))
    dihedral = np.where(valid[f1] & valid[f2], dihedral, 180.0)
    unsure_edges = int((np.abs(dihedral - angle) <= ANGLE_BAND).sum())

    def following(e: np.ndarray) -> np.ndarray:
        return e - e % 3 + (e % 3 + 1) % 3

    corners = count * 3
    pull = (weight[..., None] * face[:, None, :]).reshape(corners, 3)
    stored = normals.reshape(corners, 3)
    stored = stored / np.maximum(np.linalg.norm(stored, axis=1), 1e-300)[:, None]
    def angle_between(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return np.degrees(np.arccos(np.clip((x * y).sum(axis=1), -1.0, 1.0)))

    expected = []
    for smooth in (dihedral < angle - ANGLE_BAND, dihedral <= angle + ANGLE_BAND):
        a, b = e1[smooth], e2[smooth]
        # Across a smooth edge, the corners at each end join one fan.
        fan = _components(corners, np.r_[a, following(a)], np.r_[following(b), b])
        total = np.zeros((corners, 3))
        np.add.at(total, fan, pull)
        normal = total[fan]
        expected.append(normal / np.maximum(np.linalg.norm(normal, axis=1), 1e-300)[:, None])
    sharp, smooth = (angle_between(e, stored) for e in expected)
    error = np.minimum(sharp, smooth)
    # Where edges near the angle change a corner's fan, Blender may have taken
    # some each way, and neither pass is that mix.
    mixed = (angle_between(*expected) > ANGLE_BAND) & (error > BAND_MATCH)
    doubtful = np.zeros(int(vertex.max()) + 1, dtype=bool)
    doubtful[vertex[unsure_face].ravel()] = True
    checked = ~doubtful[vertex].ravel() & ~mixed
    return error[checked], int((~checked).sum()), unsure_edges


def _components(size: int, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Connected components of ``size`` nodes joined by edges u-v: the lowest node of each."""
    label = np.arange(size)
    while True:
        before = label
        label = label.copy()
        np.minimum.at(label, u, label[v])
        np.minimum.at(label, v, label[u])
        label = label[label]
        if np.array_equal(label, before):
            return label


def _triangle_sets(primitives):
    """Polylists converted to triangle sets; one that will not convert, as it is.

    The importer's ``_iter_triangle_sets`` does the same, so a polylist whose
    ``triangleset()`` raises is measured rather than failing the whole file.
    """
    for primitive in primitives:
        converter = getattr(primitive, "triangleset", None)
        if callable(converter):
            try:
                yield converter()
                continue
            except Exception:  # noqa: BLE001 - fall through to the raw primitive
                pass
        yield primitive


def _node_transforms(document) -> dict[int, np.ndarray]:
    """``id()`` of each library geometry -> world matrix of the node instancing it.

    The importer's ``_node_transforms`` in numpy, for the unbound walk below.
    """
    transforms: dict[int, np.ndarray] = {}

    def walk(nodes, parent: np.ndarray) -> None:
        for node in nodes:
            matrix = parent
            raw = getattr(node, "matrix", None)
            if raw is not None:
                try:
                    matrix = parent @ np.asarray(raw, dtype=np.float64).reshape(4, 4)
                except Exception:  # noqa: BLE001
                    matrix = parent
            geometry = getattr(node, "geometry", None)
            if geometry is not None:
                transforms.setdefault(id(geometry), matrix)
            walk(getattr(node, "children", ()) or (), matrix)

    try:
        walk(getattr(document.scene, "nodes", ()) or (), np.identity(4))
    except Exception:  # noqa: BLE001
        pass
    return transforms


def _kept_faces(index: np.ndarray) -> np.ndarray:
    """The importer's ``_kept_faces``: which of these (n, 3) faces a Blender mesh keeps.

    ``mesh.validate()`` removes a face that repeats a vertex, and all but one
    of the faces on the same three vertices, in any order or winding. CAD
    exports carry both. The importer leaves them out before building the mesh,
    keeping the first of each, and with them their normals.
    """
    ordered = np.sort(index, axis=1)
    keep = np.zeros(len(index), dtype=bool)
    keep[np.unique(ordered, axis=0, return_index=True)[1]] = True
    return keep & (ordered[:, 0] != ordered[:, 1]) & (ordered[:, 1] != ordered[:, 2])


def _corners(primitive, matrix: np.ndarray | None = None
             ) -> tuple[np.ndarray, np.ndarray] | None:
    """(n, 3, 3) triangles and corner normals of one triangle set, or None.

    Only the faces the import keeps (``_kept_faces``), so the count and the
    shading are both of the mesh Blender builds. ``matrix`` places them; only
    its linear part can change an angle.
    """
    index = getattr(primitive, "vertex_index", None)
    if index is None or index.ndim != 2 or index.shape[1] != 3 or not len(index):
        return None  # lines, or nothing
    kept = _kept_faces(index)
    tri = primitive.vertex[index[kept]]
    normal = getattr(primitive, "normal", None)
    normal_index = getattr(primitive, "normal_index", None)
    has_normals = normal is not None and normal_index is not None and len(normal)
    nor = normal[normal_index[kept]] if has_normals else None
    if matrix is not None:
        linear = matrix[:3, :3]
        tri = tri @ linear.T
        if nor is not None:
            # Normals transform by the inverse transpose; row vectors, so no .T.
            nor = nor @ np.linalg.inv(linear)
    if nor is None:
        face = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        nor = np.repeat(face[:, None, :], 3, axis=1)
    return tri, nor


def _instance_key(bound) -> tuple:
    """Which geometry, placed where: the importer's ``_instance_key``."""
    return (getattr(bound.original, "id", None),
            tuple(round(float(v), 9) for v in np.asarray(bound.matrix).flat))


def _without_bindings(document) -> io.BytesIO:
    """The importer's ``_without_bindings``: every <bind_material> gone, any prefix.

    From the tree pycollada already parsed, as the importer does, not from the
    file: a zipped COLLADA file is an archive, not XML.
    """
    from collada import xmlutil

    root = copy.deepcopy(document.xmlnode.getroot())
    for parent in list(root.iter()):
        for child in list(parent):
            if isinstance(child.tag, str) and child.tag.rpartition("}")[2] == "bind_material":
                parent.remove(child)
    return io.BytesIO(xmlutil.etree.tostring(root))


def _read_dae(path: Path, source=None):
    """The document, loaded the way the importer's ``_load_collada`` loads it."""
    import collada

    return collada.Collada(str(path) if source is None else source, ignore=[
        collada.common.DaeUnsupportedError,
        collada.common.DaeBrokenRefError,
    ])


def dae_stats(path: Path) -> dict:
    """Triangle count and normal deviation of a .dae as written, read by pycollada.

    Both are of the triangles a Blender import keeps (``_kept_faces``), so the
    count can be held against the import's exactly.

    Reads the file the way kinema's importer does, or the check would reject
    meshes the importer converts fine: the same ``ignore`` list and the bound
    scene geometry first. A material that fails to bind -- a texture whose
    image the file never declares -- drops its instances from that walk, so
    when the read reported errors, the document is read again without bindings
    for the instances it lost (if that re-read fails, the importer keeps its
    first read, and so does this); and as a last resort the library geometry is placed
    by whatever nodes survived, as in the importer's fallbacks.
    Triangle sets without normals are given their face normals -- which is
    what Blender shows for them, since the importer leaves such faces flat.
    """
    import collada

    document = _read_dae(path)
    triangles: list[np.ndarray] = []
    normals: list[np.ndarray] = []

    def add(primitives, matrix: np.ndarray | None = None) -> None:
        for primitive in _triangle_sets(primitives):
            corners = _corners(primitive, matrix)
            if corners is not None:
                triangles.append(corners[0])
                normals.append(corners[1])

    placed = []
    for bound in document.scene.objects("geometry"):
        placed.append(_instance_key(bound))
        add(bound.primitives())
    unbound = None
    if getattr(document, "errors", None):
        try:
            unbound = _read_dae(path, source=_without_bindings(document))
        except Exception:  # noqa: BLE001 - the importer keeps its first read too
            pass
    if unbound is not None:
        for bound in unbound.scene.objects("geometry"):
            key = _instance_key(bound)
            if key in placed:
                placed.remove(key)
            else:
                add(bound.primitives())
    geometries = getattr(document, "geometries", ()) or ()
    if not triangles and geometries:
        transforms = _node_transforms(document)
        for geometry in geometries:
            add(getattr(geometry, "primitives", ()) or (), transforms.get(id(geometry)))

    loader = f"pycollada {getattr(collada, '__version__', 'unknown')}"
    if not triangles:
        return {"triangles": 0, "normal_deviation": None, "loader": loader}
    tri = np.concatenate(triangles)
    return {
        "triangles": int(len(tri)),
        "normal_deviation": normal_deviation(tri, np.concatenate(normals)),
        "loader": loader,
    }
