import ast
from types import SimpleNamespace

import collada
import numpy as np
import pytest

import meshkit.external
from meshkit._vendor import VENDORED_FILE
from meshkit.external import _corners, _kept_faces, dae_stats, normal_deviation, plain_stats
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


def test_a_zipped_file_with_a_broken_material_is_measured_whole(tmp_path):
    # pycollada reads a zipped COLLADA file; the binding-free re-read starts
    # from its parsed tree, as the importer's does, so it can read one too.
    import zipfile

    path = tmp_path / "box.dae"
    flat_box_dae(path)
    with_second_instance(path, broken_material=True)
    zipped = tmp_path / "box.zae"
    with zipfile.ZipFile(zipped, "w") as archive:
        archive.write(path, "box.dae")
    assert dae_stats(zipped)["triangles"] == 24


def test_a_failed_reread_keeps_what_the_first_read_gave(tmp_path, monkeypatch):
    # The importer warns and keeps its first read; the gate must count the same.
    def fail(document):
        raise ValueError("stand-in parse failure")

    monkeypatch.setattr(meshkit.external, "_without_bindings", fail)
    path = tmp_path / "box.dae"
    flat_box_dae(path)
    with_second_instance(path, broken_material=True)
    assert dae_stats(path)["triangles"] == 12


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


def stl_from(triangles: np.ndarray, path):
    """An STL holding exactly these (n, 3, 3) triangles, each corner written out."""
    import trimesh

    trimesh.Trimesh(triangles.reshape(-1, 3), np.arange(len(triangles) * 3).reshape(-1, 3),
                    process=False).export(path)
    return path


def test_plain_stats_measure_an_stl_where_it_is(tmp_path):
    triangles, _ = cube_corners(flat=True)
    triangles = triangles + [1.0, 2.0, 3.0]
    stats = plain_stats(stl_from(triangles, tmp_path / "cube.stl"))
    assert stats["triangles"] == stats["file_triangles"] == 12
    assert stats["area"] == pytest.approx(6.0)
    assert stats["centroid"] == pytest.approx([1.5, 2.5, 3.5])
    assert stats["aabb_min"] == pytest.approx([1.0, 2.0, 3.0])
    assert stats["aabb_max"] == pytest.approx([2.0, 3.0, 4.0])


def test_plain_stats_count_what_a_weld_keeps(tmp_path):
    triangles, _ = cube_corners(flat=True)
    sliver = triangles[:1].copy()
    sliver[0, 1] = sliver[0, 0]                    # a repeated corner
    twin = triangles[1:2][:, [0, 2, 1]]            # the same corners, wound the other way
    stats = plain_stats(stl_from(np.concatenate([triangles, sliver, twin]), tmp_path / "c.stl"))
    assert stats["file_triangles"] == 14
    assert stats["triangles"] == 12
    assert stats["area"] == pytest.approx(6.0)


def obj_from(objects: dict[str, tuple[np.ndarray, list[str]]], path):
    """An OBJ of named objects: each its vertices and its ``f`` lines, indices local."""
    lines, offset = [], 0
    for name, (vertices, faces) in objects.items():
        lines.append(f"o {name}")
        lines += [f"v {x} {y} {z}" for x, y, z in vertices]
        for face in faces:
            lines.append("f " + " ".join(
                t if t.startswith("-") else str(int(t) + offset) for t in face.split()))
        offset += len(vertices)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_plain_stats_drop_doubled_faces_within_an_obj_object_not_across(tmp_path):
    import trimesh

    box = trimesh.creation.box(extents=(1.0, 1.0, 1.0))
    faces = [f"{a + 1} {b + 1} {c + 1}" for a, b, c in box.faces]
    first = box.faces[0]
    stats = plain_stats(obj_from({
        # The same face twice, on the same vertices, the second wound the other way.
        "a": (box.vertices, faces + [f"{first[0] + 1} {first[2] + 1} {first[1] + 1}"]),
        # A face of a's, again, in an object of its own: Blender keeps it there.
        "b": (box.vertices[first], ["-3 -2 -1"]),
    }, tmp_path / "part.obj"))
    assert stats["file_triangles"] == 14
    assert stats["triangles"] == 13
    assert stats["area"] == pytest.approx(6.5)
    assert stats["loader"] == "meshkit OBJ reader"


def test_plain_stats_read_obj_polygons_and_continued_lines(tmp_path):
    path = tmp_path / "quad.obj"
    path.write_text("v 0 0 0\nv 2 0 0\nv 2 1 0\nv 0 1 0\nf 1/1/1 2/2/1 \\\n 3/3/1 4/4/1\n",
                    encoding="utf-8")
    stats = plain_stats(path)
    assert stats["triangles"] == stats["file_triangles"] == 2
    assert stats["area"] == pytest.approx(2.0)
    assert stats["centroid"] == pytest.approx([1.0, 0.5, 0.0])


def test_normal_deviation_takes_other_percentiles():
    triangles, normals = cube_corners(flat=False)
    (worst,) = normal_deviation(triangles, normals, (100,))
    assert worst == pytest.approx(54.7356, abs=1e-3)   # a cube corner's diagonal
