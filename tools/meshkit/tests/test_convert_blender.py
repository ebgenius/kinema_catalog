"""End to end through a real Blender: skipped where none is installed."""

import numpy as np
import pytest
import collada
from collada import source, geometry, material, scene

from meshkit.convert import convert, plan
from meshkit.external import glb_stats

pytestmark = pytest.mark.blender


def flat_box_dae(path, *, offset_z=0.192, unit_meter=0.01):
    """A 10 x 10 x 20 cm box in centimetres, flat-shaded, placed by its node.

    Three things a careless conversion loses: the node transform (the OBJ
    failure), the unit, and per-face normals (the kinema importer bug).
    """
    mesh = collada.Collada()
    mesh.assetInfo.unitmeter = unit_meter
    mesh.assetInfo.unitname = "centimeter"  # pycollada writes no <unit> without a name
    mesh.assetInfo.upaxis = "Z_UP"
    effect = material.Effect("fx", [], "phong", diffuse=(0.25, 0.25, 0.25))
    mat = material.Material("mat", "mat", effect)
    mesh.effects.append(effect)
    mesh.materials.append(mat)

    lo, hi = np.array([-5.0, -5.0, 0.0]), np.array([5.0, 5.0, 20.0])
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1])
                        for z in (lo[2], hi[2])])
    faces = [((0, 1, 3, 2), (-1, 0, 0)), ((4, 6, 7, 5), (1, 0, 0)), ((0, 4, 5, 1), (0, -1, 0)),
             ((2, 3, 7, 6), (0, 1, 0)), ((0, 2, 6, 4), (0, 0, -1)), ((1, 5, 7, 3), (0, 0, 1))]
    normals = np.array([n for _, n in faces], dtype=float)
    index = []
    for f, (quad, _) in enumerate(faces):
        a, b, c, d = quad
        for tri in ((a, b, c), (a, c, d)):
            for v in tri:
                index += [v, f]
    verts = source.FloatSource("v", corners.ravel(), ("X", "Y", "Z"))
    norms = source.FloatSource("n", normals.ravel(), ("X", "Y", "Z"))
    geom = geometry.Geometry(mesh, "box", "box", [verts, norms])
    inputs = source.InputList()
    inputs.addInput(0, "VERTEX", "#v")
    inputs.addInput(1, "NORMAL", "#n")
    geom.primitives.append(geom.createTriangleSet(np.array(index), inputs, "m"))
    mesh.geometries.append(geom)
    node = scene.Node("box", children=[scene.GeometryNode(geom, [scene.MaterialNode("m", mat, [])])],
                      transforms=[scene.TranslateTransform(0, 0, offset_z / unit_meter)])
    mesh.scenes.append(scene.Scene("scene", [node]))
    mesh.scene = mesh.scenes[0]
    mesh.write(str(path))


def test_convert_keeps_geometry_placement_and_shading(tmp_path, blender):
    root = tmp_path / "catalog"
    dae = root / "src" / "fork" / "pkg" / "meshes" / "visual" / "box.dae"
    dae.parent.mkdir(parents=True)
    flat_box_dae(dae)
    before = dae.read_bytes()

    out = tmp_path / "out"
    report = convert(plan([dae], root, out), blender,
                     report_path=tmp_path / "report.json", progress=lambda _: None)

    (item,) = report["items"]
    assert item["status"] == "converted", item["problems"]
    glb = out / "src" / "fork" / "pkg" / "meshes" / "visual" / "box.glb"
    assert glb.is_file()
    assert dae.read_bytes() == before, "the source must never be touched"

    stats = item["source_stats"]
    assert stats["triangles"] == 12
    assert stats["area"] == pytest.approx(2 * 0.01 + 4 * 0.02)          # m^2, units applied
    assert stats["centroid"][2] == pytest.approx(0.192 + 0.10, abs=1e-6)  # node transform kept
    assert max(glb_stats(glb)["normal_deviation"]) < 1.0                 # still flat-shaded


def test_existing_output_is_skipped_without_force(tmp_path, blender):
    root = tmp_path / "catalog"
    dae = root / "src" / "fork" / "box.dae"
    dae.parent.mkdir(parents=True)
    flat_box_dae(dae)
    dae.with_suffix(".glb").write_bytes(b"not touched")

    report = convert(plan([dae], root, None), blender,
                     report_path=tmp_path / "report.json", progress=lambda _: None)
    assert report["items"][0]["status"] == "skipped"
    assert dae.with_suffix(".glb").read_bytes() == b"not touched"
