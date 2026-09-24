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

from pathlib import Path

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


def dae_stats(path: Path) -> dict:
    """Normal deviation of a .dae as written, read by pycollada.

    Walks the same bound scene geometry kinema's importer does. Triangle sets
    without normals are given their face normals -- which is what Blender shows
    for them, since the importer leaves such faces flat.
    """
    import collada

    document = collada.Collada(str(path))
    triangles: list[np.ndarray] = []
    normals: list[np.ndarray] = []
    for bound in document.scene.objects("geometry"):
        for primitive in bound.primitives():
            converter = getattr(primitive, "triangleset", None)
            if callable(converter):
                primitive = converter()
            index = getattr(primitive, "vertex_index", None)
            if index is None or index.ndim != 2 or index.shape[1] != 3 or not len(index):
                continue  # lines, or nothing
            tri = primitive.vertex[index]
            normal = getattr(primitive, "normal", None)
            normal_index = getattr(primitive, "normal_index", None)
            if normal is not None and normal_index is not None and len(normal):
                nor = normal[normal_index]
            else:
                face = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
                nor = np.repeat(face[:, None, :], 3, axis=1)
            triangles.append(tri)
            normals.append(nor)
    if not triangles:
        return {"normal_deviation": None, "loader": f"pycollada {getattr(collada, '__version__', 'unknown')}"}
    return {
        "normal_deviation": normal_deviation(np.concatenate(triangles), np.concatenate(normals)),
        "loader": f"pycollada {getattr(collada, '__version__', 'unknown')}",
    }
