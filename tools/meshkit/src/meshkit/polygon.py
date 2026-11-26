"""Splitting a polygon into triangles, the same way on both sides of the gate.

numpy only: the Blender job loads this file by path (``job.load_polygon``), and
``external.plain_stats`` imports it, so an OBJ's quads and larger polygons
become the same triangles in the GLB and in the independent reading of the
file.
"""

from __future__ import annotations

import numpy as np


def triangulate(polygon: np.ndarray) -> list[tuple[int, int, int]]:
    """Triangles covering one polygon, as indices into its corners.

    A convex polygon is fanned from its first corner. A concave one is
    ear-clipped in the plane it lies in (its Newell normal), since a fan would
    cover area outside it: corners (0,0) (2,0) (2,2) (1,0.5) (0,2) enclose 2.5,
    and their fan 3.5. One that is not simple has no covering split; what is
    left of it is fanned.

    A planar polygon has the same area and centroid under any covering split.
    One that is not planar -- a warped quad -- has no area of its own: each
    split gives another. So the Blender job splits with this same function
    before it smooths, rather than with Blender's own choice of diagonal, and
    the GLB and the import check hold the same triangles.
    """
    count = len(polygon)
    if count == 3:
        return [(0, 1, 2)]
    normal = np.cross(polygon, np.roll(polygon, -1, axis=0)).sum(axis=0)
    axis = int(np.argmax(np.abs(normal)))
    # The two other axes in cyclic order -- (y, z), (z, x), (x, y) -- so the
    # projection turns the way the normal's own component says.
    flat = polygon[:, [(axis + 1) % 3, (axis + 2) % 3]]
    if normal[axis] < 0:
        flat = flat[:, ::-1]          # counter-clockwise, seen from the normal

    def turn(o: int, a: int, b: int) -> float:
        (ox, oy), (ax, ay), (bx, by) = flat[o], flat[a], flat[b]
        return (ax - ox) * (by - oy) - (ay - oy) * (bx - ox)

    fan = [(0, k, k + 1) for k in range(1, count - 1)]
    if all(turn(k - 1, k, (k + 1) % count) >= 0 for k in range(count)):
        return fan
    left = list(range(count))
    triangles: list[tuple[int, int, int]] = []
    while len(left) > 3:
        for k in range(len(left)):
            a, b, c = left[k - 1], left[k], left[(k + 1) % len(left)]
            if turn(a, b, c) <= 0:
                continue                  # a reflex corner is no ear
            # Another corner inside, or on its edge (a notch touching the
            # diagonal): not an ear. A corner at one of its own corners'
            # positions does not count.
            if any(turn(a, b, p) >= 0 and turn(b, c, p) >= 0 and turn(c, a, p) >= 0
                   for p in left if p not in (a, b, c)
                   and not any(np.array_equal(flat[p], flat[q]) for q in (a, b, c))):
                continue
            triangles.append((a, b, c))
            left.pop(k)
            break
        else:
            return triangles + [(left[0], left[k], left[k + 1])
                                for k in range(1, len(left) - 1)]
    return triangles + [tuple(left)]
