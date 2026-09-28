"""The verification gate: does the GLB hold the same geometry as the .dae?

A conversion tool that trusts its own exit status ships broken robots. The
experiment that led here converted FER's meshes to OBJ with assimp: the tool
exited 0, RViz logged no mesh errors, and every link rendered in the wrong
place, because OBJ cannot carry the node transform the COLLADA files use.
Nothing complained. Only a measurement would have.

So every GLB is measured against its source before it may replace anything:

* **triangle count** -- exact. A glTF round trip may re-split vertices, but
  never adds or drops faces.
* **surface area** -- relative. Catches scale errors (a lost ``<unit>`` is a
  1000x factor) and missing or duplicated primitives.
* **area-weighted centroid** and **axis-aligned bounds** -- relative to the
  mesh's own bounding-box diagonal. Catch lost node transforms and axis
  rotations, which leave the count and area untouched.

Positions are compared in Blender's Z-up world on both sides: the source as
kinema's importer lays it out, the GLB as Blender's glTF importer does. That is
the pair kinema itself will produce, so "equal here" means "looks the same in
kinema".
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Tolerance:
    # float32 vertex storage in glTF is ~7 significant digits; 1e-5 of the
    # diagonal leaves room for that while still catching a 0.1 mm shift on a
    # 1 m link.
    position: float = 1e-5
    area: float = 1e-4
    # degrees, on each percentile of the normal-deviation distribution
    # (external.normal_deviation). Blender stores custom normals compressed, so
    # a faithful copy drifts by a fraction of a degree; losing them moves the
    # median by tens of degrees.
    normals: float = 2.0


DEFAULT = Tolerance()


def compare_normals(source: list[float] | None, candidate: list[float] | None,
                    tolerance: Tolerance = DEFAULT) -> list[str]:
    """Reasons the GLB's shading departs from the .dae's; empty means it does not."""
    from meshkit.external import QUANTILES

    if source is None or candidate is None:
        return ["normal deviation missing"]
    problems = []
    for q, a, b in zip(QUANTILES, source, candidate):
        if abs(a - b) > tolerance.normals:
            problems.append(
                f"normals: p{q} deviation from the face is {b:.1f} deg, the .dae's is "
                f"{a:.1f} deg (limit {tolerance.normals:g} deg)")
    return problems


def _diagonal(stats: dict) -> float:
    lo, hi = stats.get("aabb_min"), stats.get("aabb_max")
    if lo is None or hi is None:
        return 0.0
    return math.dist(lo, hi)


def compare(source: dict, candidate: dict, tolerance: Tolerance = DEFAULT,
            *, check_frame: bool = True) -> list[str]:
    """Return the reasons ``candidate`` does not match ``source``; empty means it does.

    ``check_frame=False`` compares only what is independent of position and
    orientation -- triangle count and area -- for loaders that do not share
    Blender's world frame.
    """
    problems: list[str] = []

    if not source or not candidate:
        return ["missing measurement"]

    if source.get("triangles", 0) == 0:
        problems.append("source has no triangles")
    if candidate.get("triangles") != source.get("triangles"):
        problems.append(
            f"triangle count {candidate.get('triangles')} != {source.get('triangles')}"
        )

    src_area, cand_area = source.get("area") or 0.0, candidate.get("area") or 0.0
    if src_area > 0:
        rel = abs(cand_area - src_area) / src_area
        if rel > tolerance.area:
            problems.append(f"surface area differs by {rel:.2e} (limit {tolerance.area:.0e})")
    elif cand_area > 0:
        problems.append("source has zero area but candidate does not")

    if not check_frame:
        return problems

    diagonal = _diagonal(source)
    if diagonal <= 0:
        problems.append("source bounding box is empty")
        return problems
    limit = tolerance.position * diagonal

    for key in ("centroid", "aabb_min", "aabb_max"):
        a, b = source.get(key), candidate.get(key)
        if a is None or b is None:
            problems.append(f"{key} missing")
            continue
        offset = math.dist(a, b)
        if offset > limit:
            problems.append(
                f"{key} moved by {offset:.3e} m ({offset / diagonal:.2e} of the diagonal, "
                f"limit {tolerance.position:.0e})"
            )
    return problems
