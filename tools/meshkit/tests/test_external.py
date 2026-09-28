import ast
from types import SimpleNamespace

import collada
import numpy as np
import pytest

from meshkit._vendor import VENDORED_FILE
from meshkit.external import _corners, _kept_faces, dae_stats, normal_deviation
from test_convert_blender import (flat_box_dae, with_broken_texture,
                                  with_degenerate_and_duplicate_faces, with_lines,
                                  with_prefixed_bindings, with_second_instance)


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
    # Strict pycollada refuses the file, and the tolerant read binds no
    # geometry at all. kinema's importer reads it again without bindings, and
    # the shading check has to as well, or the mesh could never pass.
    intact = tmp_path / "intact.dae"
    flat_box_dae(intact)
    with_second_instance(intact)
    broken = tmp_path / "broken.dae"
    broken.write_bytes(intact.read_bytes())
    with_broken_texture(broken)

    with pytest.raises(collada.common.DaeBrokenRefError):
        collada.Collada(str(broken))
    expected, found = dae_stats(intact), dae_stats(broken)
    assert expected["triangles"] == found["triangles"] == 24   # both instances
    assert found["normal_deviation"] == pytest.approx(expected["normal_deviation"], abs=1e-9)


@pytest.mark.parametrize("broken_first, offset_cm", [(False, 100), (True, 100), (True, 0)])
def test_one_broken_material_is_measured_like_the_rest(tmp_path, broken_first, offset_cm):
    # pycollada drops only the instance whose material fails to bind; the
    # scene walk still finds the other, and must not stop there.
    path = tmp_path / "box.dae"
    flat_box_dae(path)
    with_second_instance(path, broken_material=True, broken_first=broken_first,
                         offset_cm=offset_cm)
    assert dae_stats(path)["triangles"] == 24


def test_prefixed_bindings_are_removed_too(tmp_path):
    # <c:bind_material> is the same element; missing it, the re-read loses
    # the instances again and only the last resort's one unplaced copy is left.
    path = tmp_path / "box.dae"
    flat_box_dae(path)
    with_second_instance(path)
    with_broken_texture(path)
    with_prefixed_bindings(path)
    assert dae_stats(path)["triangles"] == 24


def test_count_is_of_the_triangles_blender_keeps(tmp_path):
    # 14 in the file; mesh.validate() drops the one repeating a vertex and the
    # reversed duplicate, so an exact comparison has to count 12.
    path = tmp_path / "box.dae"
    flat_box_dae(path)
    with_degenerate_and_duplicate_faces(path)
    assert dae_stats(path)["triangles"] == 12


def test_shading_is_of_the_triangles_blender_keeps(tmp_path):
    # The unflipped copy is 180 degrees off its normals at every corner. The
    # import keeps face 0 in its place, so the measurement must as well, or it
    # fails a GLB that is exactly right.
    path = tmp_path / "box.dae"
    flat_box_dae(path)
    with_degenerate_and_duplicate_faces(path, flipped=False)
    assert max(dae_stats(path)["normal_deviation"]) < 1e-6


def test_kept_faces_are_the_first_on_each_set_of_vertices():
    faces = np.array([[0, 0, 1], [0, 1, 3], [3, 1, 0], [1, 3, 0], [1, 2, 1], [2, 3, 4]])
    assert _kept_faces(faces).tolist() == [False, True, False, False, False, True]


def test_the_importer_keeps_the_same_faces():
    # Its copy runs inside Blender, but needs only numpy: run its own source
    # on the same faces, so the two copies cannot drift apart unseen.
    tree = ast.parse(VENDORED_FILE.read_text(encoding="utf-8"))
    (node,) = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_kept_faces"]
    namespace = {"np": np}
    exec(compile(ast.Module([node], type_ignores=[]), str(VENDORED_FILE), "exec"), namespace)
    # Six vertices: most faces repeat one, or share their three with another.
    faces = np.random.default_rng(0).integers(0, 6, size=(400, 3))
    expected = _kept_faces(faces)
    assert expected.sum() == 20   # one face per set of three distinct vertices
    assert namespace["_kept_faces"](faces).tolist() == expected.tolist()


def test_lines_are_not_triangles(tmp_path):
    path = tmp_path / "box.dae"
    flat_box_dae(path)
    with_lines(path)
    assert dae_stats(path)["triangles"] == 12
