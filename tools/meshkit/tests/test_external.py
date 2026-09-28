import re
from types import SimpleNamespace

import collada
import numpy as np
import pytest

from meshkit.external import _corners, dae_stats, normal_deviation
from test_convert_blender import flat_box_dae


def cube_corners(flat: bool):
    """A unit cube's 12 triangles, with face normals (flat) or averaged ones."""
    v = np.array([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)], dtype=float)
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    tris = []
    for a, b, c, d in quads:
        tris += [(a, b, c), (a, c, d)]
    tris = np.array(tris)
    # orient outward
    centre = v.mean(axis=0)
    for i, t in enumerate(tris):
        p = v[t]
        if np.dot(np.cross(p[1] - p[0], p[2] - p[0]), p.mean(axis=0) - centre) < 0:
            tris[i] = t[[0, 2, 1]]
    triangles = v[tris]
    if flat:
        face = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        normals = np.repeat(face[:, None, :], 3, axis=1)
    else:
        normals = (v - centre)[tris]
    return triangles, normals


def test_flat_normals_deviate_nowhere():
    assert max(normal_deviation(*cube_corners(flat=True))) < 1e-6


def test_averaged_normals_deviate_a_lot():
    # Corner normals of a smoothed cube sit ~54.7 degrees off every face.
    assert min(normal_deviation(*cube_corners(flat=False))) > 50


def test_invariant_under_rotation_scale_and_up_axis():
    triangles, normals = cube_corners(flat=False)
    y_up = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)
    theta = 0.7
    spin = np.array([[np.cos(theta), -np.sin(theta), 0], [np.sin(theta), np.cos(theta), 0], [0, 0, 1]])
    m = 0.001 * y_up @ spin
    moved_t = triangles @ m.T + [3.0, -2.0, 1.0]
    moved_n = normals @ np.linalg.inv(m)
    assert np.allclose(normal_deviation(triangles, normals), normal_deviation(moved_t, moved_n))


def test_degenerate_triangles_are_ignored():
    triangles, normals = cube_corners(flat=True)
    sliver = np.zeros((1, 3, 3))
    assert max(normal_deviation(np.concatenate([triangles, sliver]),
                                np.concatenate([normals, np.ones((1, 3, 3))]))) < 1e-6


def test_node_transform_keeps_flat_normals_flat():
    # A shear and a non-uniform scale: normals must move by the inverse
    # transpose, or a flat face's normal would no longer be square to it.
    triangles, normals = cube_corners(flat=True)
    order = np.arange(len(triangles) * 3).reshape(-1, 3)
    primitive = SimpleNamespace(vertex=triangles.reshape(-1, 3), vertex_index=order,
                                normal=normals.reshape(-1, 3), normal_index=order)
    matrix = np.array([[1.0, 0.5, 0, 0], [0, 3.0, 0, 0], [0, 0, 0.5, 0], [0, 0, 0, 1.0]])
    moved = _corners(primitive, matrix)
    assert max(normal_deviation(*moved)) < 1e-6


def test_broken_texture_is_read_the_way_the_importer_reads_it(tmp_path):
    # A texture whose image the file never declares, common in CAD exports:
    # strict pycollada refuses the file, and the tolerant read binds no
    # geometry at all. kinema's importer falls back to the library geometry,
    # and the shading check has to as well, or the mesh can never pass.
    intact = tmp_path / "intact.dae"
    flat_box_dae(intact)
    text = intact.read_text(encoding="utf-8")
    text = text.replace('<technique sid="common">', (
        '<newparam sid="surf"><surface type="2D"><init_from>no_such_image</init_from>'
        '</surface></newparam><newparam sid="samp"><sampler2D><source>surf</source>'
        '</sampler2D></newparam><technique sid="common">'), 1)
    text = re.sub(r"<diffuse>.*?</diffuse>",
                  '<diffuse><texture texture="samp" texcoord="UVMap"/></diffuse>', text,
                  count=1, flags=re.S)
    broken = tmp_path / "broken.dae"
    broken.write_text(text, encoding="utf-8")

    with pytest.raises(collada.common.DaeBrokenRefError):
        collada.Collada(str(broken))
    expected = dae_stats(intact)["normal_deviation"]
    assert expected is not None
    assert dae_stats(broken)["normal_deviation"] == pytest.approx(expected, abs=1e-9)
