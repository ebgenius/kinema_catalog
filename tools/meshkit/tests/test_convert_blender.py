"""End to end through a real Blender: skipped where none is installed."""

import re

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


def _break_texture(text):
    """Point the first effect in ``text`` at a texture whose image is never declared."""
    text = text.replace('<technique sid="common">', (
        '<newparam sid="surf"><surface type="2D"><init_from>no_such_image</init_from>'
        '</surface></newparam><newparam sid="samp"><sampler2D><source>surf</source>'
        '</sampler2D></newparam><technique sid="common">'), 1)
    return re.sub(r"<diffuse>.*?</diffuse>",
                  '<diffuse><texture texture="samp" texcoord="UVMap"/></diffuse>', text,
                  count=1, flags=re.S)


def with_second_instance(path, *, broken_material=False, broken_first=False, offset_cm=100):
    """Instance the box's geometry again, from a second node ``offset_cm`` along x.

    ``broken_material`` gives one node -- the second, or with ``broken_first``
    the first -- a material of its own, whose texture names an image the file
    never declares: only that instance fails to bind, and the scene still
    yields the other.
    """
    text = path.read_text(encoding="utf-8")
    node = re.search(r'<node id="box".*?</node>', text, re.S).group(0)
    first = node
    second = re.sub(r"<translate>\S+", f"<translate>{offset_cm}",
                    node.replace('id="box"', 'id="box2"', 1), count=1)
    if broken_material:
        effect = re.search(r'<effect id="fx".*?</effect>', text, re.S).group(0)
        text = text.replace(effect, effect + _break_texture(effect.replace('id="fx"', 'id="fx2"')))
        text = text.replace("</library_materials>", '<material id="mat2" name="mat2">'
                            '<instance_effect url="#fx2"/></material></library_materials>', 1)
        if broken_first:
            first = first.replace('target="#mat"', 'target="#mat2"')
        else:
            second = second.replace('target="#mat"', 'target="#mat2"')
    path.write_text(text.replace(node, first + second), encoding="utf-8")


def with_lines(path):
    """Add a <lines> primitive, three of the box's vertical edges, as some CAD
    exports do.

    Read three indices at a time, (0-1, 2-3, 4-5) make the faces (0, 1, 2) and
    (3, 4, 5): real triangles, which mesh.validate() keeps. Edges that share
    endpoints would repeat a vertex and be dropped anyway.
    """
    text = path.read_text(encoding="utf-8")
    lines = ('<lines count="3"><input offset="0" semantic="VERTEX" source="#v-vertices" />'
             '<p>0 1 2 3 4 5</p></lines>')
    path.write_text(text.replace("</triangles>", "</triangles>" + lines, 1), encoding="utf-8")


def with_degenerate_and_duplicate_faces(path):
    """Add a face that repeats a vertex, and the first face again, reversed and
    facing the other way, as a double-sided export has it.

    CAD exports carry both. Blender's mesh.validate() drops them, so the box
    still imports as 12 triangles.
    """
    text = path.read_text(encoding="utf-8").replace('<triangles count="12"',
                                                    '<triangles count="14"', 1)
    # (0, 0, 1) repeats vertex 0; (3, 1, 0) is face (0, 1, 3) reversed, with
    # normal 1, the box's +x, where face 0 has -x.
    text = re.sub(r"(<triangles\b.*?<p>.*?)(</p>)", r"\1 0 0 0 0 1 0 3 1 1 1 0 1\2", text,
                  count=1, flags=re.S)
    path.write_text(text, encoding="utf-8")


def with_prefixed_bindings(path):
    """Spell every <bind_material> with a namespace prefix: valid, and read the same."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<COLLADA\b", '<COLLADA xmlns:c="http://www.collada.org/2005/11/COLLADASchema"',
                  text, count=1)
    text = text.replace("<bind_material>", "<c:bind_material>")
    path.write_text(text.replace("</bind_material>", "</c:bind_material>"), encoding="utf-8")


def with_broken_texture(path):
    """Point the box's material at a texture whose image the file never declares.

    Common in CAD exports. Strict pycollada refuses such a file; the tolerant
    read cannot bind the material, and drops each <instance_geometry> with it.
    """
    path.write_text(_break_texture(path.read_text(encoding="utf-8")), encoding="utf-8")


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


@pytest.mark.parametrize("prefixed", [False, True], ids=["plain", "prefixed-bindings"])
def test_broken_texture_keeps_every_instance_where_its_node_puts_it(tmp_path, blender, prefixed):
    # The importer used to fall back to the library geometry alone: the node's
    # offset and the second instance were lost, and every check still passed,
    # because they all start from what the importer produced (patches/0002).
    root = tmp_path / "catalog"
    dae = root / "src" / "fork" / "box.dae"
    dae.parent.mkdir(parents=True)
    flat_box_dae(dae)
    with_second_instance(dae)
    with_broken_texture(dae)
    if prefixed:
        with_prefixed_bindings(dae)

    report = convert(plan([dae], root, tmp_path / "out"), blender,
                     report_path=tmp_path / "report.json", progress=lambda _: None)

    (item,) = report["items"]
    assert item["status"] == "converted", item["problems"]
    assert any("material binding failed" in w for w in item["importer_warnings"])
    stats = item["source_stats"]
    assert stats["triangles"] == 24
    assert stats["centroid"] == pytest.approx([0.5, 0.0, 0.192 + 0.10], abs=1e-6)


@pytest.mark.parametrize("broken_first, offset_cm, centroid_x", [
    (False, 100, 0.5),
    (True, 100, 0.5),
    # Same geometry, same place: the two instances share a key, and which of
    # them the recovery counts as lost cannot change a single triangle.
    (True, 0, 0.0),
], ids=["bound-first", "lost-first", "lost-first-same-place"])
def test_one_broken_material_loses_no_instance(tmp_path, blender, broken_first, offset_cm,
                                               centroid_x):
    # Only the second node's material fails to bind. pycollada drops that one
    # instance, the scene walk is not empty, and the recovery must not wait
    # for it to be: the second box was dropped without a warning.
    root = tmp_path / "catalog"
    dae = root / "src" / "fork" / "box.dae"
    dae.parent.mkdir(parents=True)
    flat_box_dae(dae)
    with_second_instance(dae, broken_material=True, broken_first=broken_first,
                         offset_cm=offset_cm)

    report = convert(plan([dae], root, tmp_path / "out"), blender,
                     report_path=tmp_path / "report.json", progress=lambda _: None)

    (item,) = report["items"]
    assert item["status"] == "converted", item["problems"]
    assert any("1 instance(s)" in w for w in item["importer_warnings"])
    stats = item["source_stats"]
    assert stats["triangles"] == 24
    assert stats["centroid"] == pytest.approx([centroid_x, 0.0, 0.192 + 0.10], abs=1e-6)
    assert "mat" in stats["materials"]   # the instance that bound keeps its material


def test_lines_do_not_become_triangles(tmp_path, blender):
    # Read three indices at a time, three edges made two triangles the file
    # never had (franka's link7 carries such a <lines>). The count check is the
    # one that sees it; the others all start from the import.
    root = tmp_path / "catalog"
    dae = root / "src" / "fork" / "box.dae"
    dae.parent.mkdir(parents=True)
    flat_box_dae(dae)
    with_lines(dae)

    report = convert(plan([dae], root, tmp_path / "out"), blender,
                     report_path=tmp_path / "report.json", progress=lambda _: None)

    (item,) = report["items"]
    assert item["status"] == "converted", item["problems"]
    assert item["source_stats"]["triangles"] == 12


def test_faces_blender_drops_do_not_fail_the_count(tmp_path, blender):
    # The .dae says 14 triangles; Blender keeps 12. The count check has to
    # count the way Blender does, or it rejects every CAD mesh that has these.
    root = tmp_path / "catalog"
    dae = root / "src" / "fork" / "box.dae"
    dae.parent.mkdir(parents=True)
    flat_box_dae(dae)
    with_degenerate_and_duplicate_faces(dae)

    report = convert(plan([dae], root, tmp_path / "out"), blender,
                     report_path=tmp_path / "report.json", progress=lambda _: None)

    (item,) = report["items"]
    assert item["status"] == "converted", item["problems"]
    assert item["source_stats"]["triangles"] == 12
