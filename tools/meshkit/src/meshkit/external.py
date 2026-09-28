"""Second opinions on every GLB, from loaders that are not Blender.

The gate's round trip compares Blender's export with Blender's own import. That
is the right pairing for kinema, but it is one program checking itself: an
exporter bug mirrored by the importer would cancel out and pass. trimesh reads
glTF independently, so the GLB is also loaded here, outside Blender, and its
triangle count and surface area must agree with the source's.

Neither check can see a fault in the *import*, though: the round trip starts
from what kinema's importer produced, so an importer that loses something hands
the loss to both sides. That is not hypothetical -- kinema's importer averaged
every file's authored normals away (patches/0001), and the geometry checks all
passed. So the shading is also compared end to end, the raw .dae read by
pycollada against the GLB read by trimesh, with no Blender in between.

Only frame-independent quantities are compared. trimesh keeps glTF's Y-up
coordinates as stored, and a .dae carries its own units and up axis, so
positions would differ by design and prove nothing. Normals are summarised the
same way -- see ``normal_deviation``.
"""

from __future__ import annotations

import io
from pathlib import Path
from xml.etree import ElementTree

import numpy as np
import trimesh

# Percentiles of the normal-deviation distribution the gate compares.
QUANTILES = (50, 90, 99)


def normal_deviation(triangles: np.ndarray, normals: np.ndarray) -> list[float]:
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
        return [0.0] * len(QUANTILES)
    face = edge[keep] / length[keep, None]
    corner = normals[keep]
    corner_length = np.linalg.norm(corner, axis=2)
    corner = corner / np.where(corner_length > 0, corner_length, 1.0)[..., None]
    cosine = np.clip((corner * face[:, None, :]).sum(axis=2), -1.0, 1.0)
    angles = np.degrees(np.arccos(cosine)).ravel()
    return [float(v) for v in np.percentile(angles, QUANTILES)]


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
    return {
        "triangles": int(len(tri)),
        "area": area,
        "normal_deviation": normal_deviation(tri, np.concatenate(normals)),
        "loader": f"trimesh {trimesh.__version__}",
    }


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


def _corners(primitive, matrix: np.ndarray | None = None
             ) -> tuple[np.ndarray, np.ndarray] | None:
    """(n, 3, 3) triangles and corner normals of one triangle set, or None.

    ``matrix`` places them; only its linear part can change an angle.
    """
    index = getattr(primitive, "vertex_index", None)
    if index is None or index.ndim != 2 or index.shape[1] != 3 or not len(index):
        return None  # lines, or nothing
    tri = primitive.vertex[index]
    normal = getattr(primitive, "normal", None)
    normal_index = getattr(primitive, "normal_index", None)
    has_normals = normal is not None and normal_index is not None and len(normal)
    nor = normal[normal_index] if has_normals else None
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


def _without_bindings(path: Path) -> io.BytesIO:
    """The importer's ``_without_bindings``: every <bind_material> gone, any prefix."""
    root = ElementTree.parse(path).getroot()
    for parent in list(root.iter()):
        for child in list(parent):
            if isinstance(child.tag, str) and child.tag.rpartition("}")[2] == "bind_material":
                parent.remove(child)
    return io.BytesIO(ElementTree.tostring(root, encoding="utf-8"))


def _read_dae(path: Path, *, bind_materials: bool = True):
    """The document, loaded the way the importer's ``_load_collada`` loads it."""
    import collada

    source = str(path)
    if not bind_materials:
        source = _without_bindings(path)
    return collada.Collada(source, ignore=[
        collada.common.DaeUnsupportedError,
        collada.common.DaeBrokenRefError,
    ])


def dae_stats(path: Path) -> dict:
    """Triangle count and normal deviation of a .dae as written, read by pycollada.

    Reads the file the way kinema's importer does, or the check would reject
    meshes the importer converts fine: the same ``ignore`` list and the bound
    scene geometry first. A material that fails to bind -- a texture whose
    image the file never declares -- drops its instances from that walk, so
    when the read reported errors, the file is read again without bindings for
    the instances it lost; and as a last resort the library geometry is placed
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
    if getattr(document, "errors", None):
        for bound in _read_dae(path, bind_materials=False).scene.objects("geometry"):
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
