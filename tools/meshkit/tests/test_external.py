import ast
from types import SimpleNamespace

import collada
import numpy as np
import pytest

import meshkit.external
from meshkit._vendor import VENDORED_FILE
from meshkit.external import (_corners, _kept_faces, dae_stats, normal_deviation, plain_stats,
                              smoothing_error)
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


def test_plain_stats_read_past_an_inline_comment(tmp_path):
    path = tmp_path / "tri.obj"
    path.write_text("v 0 0 0 # origin\nv 1 0 0\nv 0 1 0\nf 1 2 3 # the only face\n",
                    encoding="utf-8")
    assert plain_stats(path)["triangles"] == 1


def test_plain_stats_cover_a_concave_polygon(tmp_path):
    # A fan from the first corner would cover 3.5, outside the polygon too.
    path = tmp_path / "arrow.obj"
    path.write_text("v 0 0 0\nv 2 0 0\nv 2 2 0\nv 1 0.5 0\nv 0 2 0\nf 1 2 3 4 5\n",
                    encoding="utf-8")
    stats = plain_stats(path)
    assert stats["triangles"] == 3
    assert stats["area"] == pytest.approx(2.5)
    # Two triangles of the notched square's area, centred by hand: the square
    # (centroid 1, 1; area 4) less the notch (corners 0,2 1,0.5 2,2; area 1.5).
    notch = np.array([[0, 2], [1, 0.5], [2, 2]]).mean(axis=0)
    assert stats["centroid"][:2] == pytest.approx(list((4 * np.array([1, 1]) - 1.5 * notch) / 2.5))


def corner_glb(triangles: np.ndarray, normals: np.ndarray, path):
    """A GLB of these (n, 3, 3) triangles with these corner normals, as stored."""
    import trimesh

    mesh = trimesh.Trimesh(triangles.reshape(-1, 3), np.arange(len(triangles) * 3).reshape(-1, 3),
                           process=False)
    mesh.vertex_normals = normals.reshape(-1, 3)
    mesh.export(path)
    return path


def cylinder_corners(sections: int = 32):
    """A cylinder's triangles, and the normals smoothing at 30 deg gives them.

    The sides meet at 360/sections, under 30, the caps at 90: side corners
    point straight out, cap corners straight up or down.
    """
    import trimesh

    mesh = trimesh.creation.cylinder(radius=0.05, height=0.2, sections=sections)
    tri = mesh.vertices[mesh.faces]
    up = np.abs(mesh.face_normals[:, 2]) > 0.99
    radial = tri.copy()
    radial[..., 2] = 0
    radial /= np.linalg.norm(radial, axis=2)[..., None]
    normals = np.where(up[:, None, None], mesh.face_normals[:, None, :], radial)
    return mesh, tri, normals


def test_smoothing_by_angle_is_reproduced(tmp_path):
    _, tri, normals = cylinder_corners()
    measured = smoothing_error(corner_glb(tri, normals, tmp_path / "c.glb"), 30.0)
    assert measured["p99_9"] < 0.01
    assert measured["corners"] == len(tri) * 3 and measured["unchecked"] == 0


def test_smoothing_lost_shows(tmp_path):
    mesh, tri, _ = cylinder_corners()
    flat = np.repeat(mesh.face_normals[:, None, :], 3, axis=1)
    measured = smoothing_error(corner_glb(tri, flat, tmp_path / "c.glb"), 30.0)
    assert measured["p99_9"] == pytest.approx(360 / 32 / 2, abs=0.1)   # half a section


def test_smoothing_across_sharp_edges_shows(tmp_path):
    mesh, tri, _ = cylinder_corners()
    averaged = np.asarray(mesh.vertex_normals)[mesh.faces]     # every face at a vertex
    measured = smoothing_error(corner_glb(tri, averaged, tmp_path / "c.glb"), 30.0)
    assert measured["p99_9"] > 30


def test_a_smaller_angle_makes_the_cylinder_flat(tmp_path):
    mesh, tri, normals = cylinder_corners()
    flat = np.repeat(mesh.face_normals[:, None, :], 3, axis=1)
    assert smoothing_error(corner_glb(tri, flat, tmp_path / "f.glb"), 10.0)["p99_9"] < 0.01
    assert smoothing_error(corner_glb(tri, normals, tmp_path / "s.glb"), 10.0)["p99_9"] > 5


def test_normal_deviation_takes_other_percentiles():
    triangles, normals = cube_corners(flat=False)
    (worst,) = normal_deviation(triangles, normals, (100,))
    assert worst == pytest.approx(54.7356, abs=1e-3)   # a cube corner's diagonal


def test_plain_stats_cover_a_concave_polygon_seen_along_y(tmp_path):
    # The same arrow standing in the XZ plane: its normal is along -Y, and the
    # projection must still turn the way the polygon does.
    path = tmp_path / "arrow.obj"
    path.write_text("v 0 0 0\nv 2 0 0\nv 2 0 2\nv 1 0 0.5\nv 0 0 2\nf 1 2 3 4 5\n",
                    encoding="utf-8")
    assert plain_stats(path)["area"] == pytest.approx(2.5)


def test_plain_stats_cover_a_polygon_whose_notch_touches_a_diagonal(tmp_path):
    # The notch (1, 1) lies on the diagonal from (0, 0) to (2, 2).
    path = tmp_path / "notch.obj"
    path.write_text("v 0 0 0\nv 2 0 0\nv 2 2 0\nv 1 1 0\nv 0 2 0\nf 1 2 3 4 5\n",
                    encoding="utf-8")
    stats = plain_stats(path)
    assert stats["triangles"] == 3
    assert stats["area"] == pytest.approx(3.0)


def rotated(point: np.ndarray, axis: np.ndarray, degrees: float) -> np.ndarray:
    """``point`` turned about ``axis`` (through the origin), by Rodrigues' formula."""
    k = axis / np.linalg.norm(axis)
    t = np.radians(degrees)
    return point * np.cos(t) + np.cross(k, point) * np.sin(t) + k * (k @ point) * (1 - np.cos(t))


def test_edges_either_side_of_the_angle_at_one_corner_are_not_failed(tmp_path):
    # Three triangles fanned round the origin. The first two meet at 29.995
    # degrees, under the angle, so Blender joins them; the last two at
    # 30.005, over it, so it does not. Both edges are within the band, and
    # neither pass -- both smooth, both sharp -- is that mix.
    def ring(degrees):
        return np.array([np.cos(np.radians(degrees)), np.sin(np.radians(degrees)), 0.0])

    p1, p2 = ring(0), ring(60)
    p0 = rotated(ring(-60), p1, 29.995)
    p3 = rotated(ring(120), p2, -30.005)
    origin = np.zeros(3)
    tri = np.array([[origin, p0, p1], [origin, p1, p2], [origin, p2, p3]])
    face = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    face /= np.linalg.norm(face, axis=1)[:, None]
    dihedral = np.degrees(np.arccos([face[0] @ face[1], face[1] @ face[2]]))
    assert dihedral == pytest.approx([29.995, 30.005], abs=1e-6)

    def weighted(faces, corner):
        total = sum(np.arctan2(np.linalg.norm(np.cross(tri[f, (corner[f] + 1) % 3] - tri[f, corner[f]],
                                                       tri[f, (corner[f] + 2) % 3] - tri[f, corner[f]])),
                               (tri[f, (corner[f] + 1) % 3] - tri[f, corner[f]])
                               @ (tri[f, (corner[f] + 2) % 3] - tri[f, corner[f]])) * face[f]
                    for f in faces)
        return total / np.linalg.norm(total)

    normals = np.repeat(face[:, None, :], 3, axis=1)
    joined = weighted([0, 1], {0: 0, 1: 0})            # at the origin, Blender's normal
    normals[0, 0] = normals[1, 0] = joined
    at_p1 = weighted([0, 1], {0: 2, 1: 1})             # p1 is on the smooth edge
    normals[0, 2] = normals[1, 1] = at_p1

    measured = smoothing_error(corner_glb(tri, normals, tmp_path / "fan.glb"), 30.0)
    assert measured["ambiguous_edges"] == 2
    assert measured["p99_9"] < 0.01
    # The joined pair's corners at the origin. The third's is its own face
    # normal, which the all-sharp pass gives, so it is checked.
    assert measured["unchecked"] == 2


SQUARE = "v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\n"


@pytest.mark.parametrize("again", ["2 3 4 1", "4 3 2 1", "3 2 1 4"])
def test_a_quad_written_twice_is_one_square(tmp_path, again):
    # Split first, a quad and its shifted or reversed copy take different
    # diagonals: four distinct triangles, a doubled surface no triangle check sees.
    path = tmp_path / "twice.obj"
    path.write_text(SQUARE + f"f 1 2 3 4\nf {again}\n", encoding="utf-8")
    stats = plain_stats(path)
    assert stats["file_triangles"] == 4
    assert stats["triangles"] == 2
    assert stats["area"] == pytest.approx(1.0)


@pytest.mark.parametrize("faces", ["f 1 2 3 4\nf 1 2 3\n", "f 1 2 3\nf 1 2 3 4\n"])
def test_a_triangle_of_a_quad_written_again_is_counted_once(tmp_path, faces):
    path = tmp_path / "part.obj"
    path.write_text(SQUARE + faces, encoding="utf-8")
    stats = plain_stats(path)
    assert stats["file_triangles"] == 3
    assert stats["triangles"] == 2
    assert stats["area"] == pytest.approx(1.0)


def test_a_polygon_that_repeats_a_corner_is_split_there(tmp_path):
    # Corners 1 2 3 at the square's, then 1 again, then two more: welded, the
    # face is two loops, as Blender's weld splits it -- a triangle each.
    path = tmp_path / "bowtie.obj"
    path.write_text("v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 0 0\nv -1 0 0\nv -1 -1 0\n"
                    "f 1 2 3 4 5 6\n", encoding="utf-8")
    stats = plain_stats(path)
    assert stats["file_triangles"] == 4
    assert stats["triangles"] == 2
    assert stats["area"] == pytest.approx(1.0)


@pytest.mark.parametrize("corners, loops", [
    ([0, 1, 2, 0, 3, 4], [[0, 1, 2], [0, 3, 4]]),
    ([0, 1, 1, 2], [[0, 1, 2]]),          # neighbours welded: one corner fewer
    ([0, 1, 2, 0], [[0, 1, 2]]),          # around the end
    ([0, 1, 0, 3], []),                   # two loops of two: no face at all
    ([0, 1, 2, 0, 4], [[0, 1, 2]]),
])
def test_simple_loops_split_as_blenders_weld_does(corners, loops):
    # Blender 5.2's remove_doubles on each, probed: the same faces, by vertex.
    from meshkit.external import _simple_loops
    assert sorted(map(sorted, _simple_loops(corners))) == sorted(map(sorted, loops))


def test_a_face_naming_a_vertex_twice_around_a_hole_is_refused(tmp_path):
    # Blender's importer rebuilds it by its own triangulation, hole kept:
    # area 12 (probed). Read as two filled loops it would be 20.
    path = tmp_path / "hole.obj"
    path.write_text("v 0 0 0\nv 4 0 0\nv 4 4 0\nv 0 4 0\nv 1 1 0\nv 1 3 0\nv 3 3 0\nv 3 1 0\n"
                    "f 1 2 3 4 1 5 6 7 8 5\n", encoding="utf-8")
    with pytest.raises(ValueError, match="face 1 names a vertex twice, and a corner of one "
                                         "loop lies inside or on another"):
        plain_stats(path)


@pytest.mark.parametrize("extra, face, reason", [
    # Crossing loops turning opposite ways, equal areas: Blender gives no face.
    # Their Newell normal is zero, so judged in its plane they did not cross.
    ("v 1 3 0\nv 2.8 0.4 0\n", "1 2 3 4 1 5 6", "the edges of two of its loops cross"),
    # A corner on the square's edge: Blender splits that edge, a pentagon.
    ("v 1 -1 0\nv 1 0 0\nv 2 -1 0\nv 0 -2 0\n", "1 2 3 4 1 5 6 7 8",
     "a corner of one loop lies inside or on another"),
    # The same loop twice: Blender gives no face.
    ("", "1 2 3 1 2 3", "two of its loops share more than one corner"),
    # Loops sharing an edge (Blender fills both) are refused with it.
    ("v 1 -1 0\n", "1 2 3 4 1 2 5", "two of its loops share more than one corner"),
    # A loop along a line beside one that is not: not probed, so refused.
    ("v -1 0 0\nv -2 0 0\n", "1 2 3 4 1 5 6", "one of its loops lies along a line"),
])
def test_a_face_naming_a_vertex_twice_is_refused_unless_its_loops_are_apart(
        tmp_path, extra, face, reason):
    # Blender 5.2's importer on each, probed.
    path = tmp_path / "part.obj"
    path.write_text(f"v 0 0 0\nv 2 0 0\nv 2 2 0\nv 0 2 0\n{extra}f {face}\n", encoding="utf-8")
    with pytest.raises(ValueError, match=f"face 1 names a vertex twice, and {reason}"):
        plain_stats(path)


@pytest.mark.parametrize("face, triangles, area", [
    ("1 2 3 1 4 5", 2, 1.0),      # two loops touching at vertex 1: a triangle each
    ("1 2 3 1 5 4", 2, 1.0),      # the same turning opposite ways: Newell normal zero
    ("1 2 3 1 7 4", 2, 1.5),      # ... and unequal
    ("1 2 2 3 6", 2, 1.0),        # a neighbour named twice: a quad
    ("1 2 3 6 1", 2, 1.0),        # the first again at the end: a quad
])
def test_a_face_naming_a_vertex_twice_reads_as_blender_repairs_it(tmp_path, face, triangles, area):
    # Blender 5.2's importer on each, probed: the same faces and area.
    path = tmp_path / "part.obj"
    path.write_text("v 0 0 0\nv 1 0 0\nv 1 1 0\nv -1 0 0\nv -1 -1 0\nv 0 1 0\nv -1 -2 0\n"
                    f"f {face}\n", encoding="utf-8")
    stats = plain_stats(path)
    assert stats["triangles"] == triangles
    assert stats["area"] == pytest.approx(area)


@pytest.mark.parametrize("face", [
    "1 2 1 3",            # two loops of two: nothing left
    "1 2 3 1",            # one loop, along a line
    "1 2 3 1 4 5",        # two loops, both along a line
])
def test_a_face_naming_a_vertex_twice_that_collapses_leaves_the_rest(tmp_path, face):
    # Blender 5.2's importer drops each and keeps the triangle beside it, probed.
    path = tmp_path / "part.obj"
    path.write_text("v 0 0 0\nv 1 0 0\nv 2 0 0\nv -1 0 0\nv -2 0 0\nv 0 1 0\n"
                    f"f {face}\nf 1 2 6\n", encoding="utf-8")
    stats = plain_stats(path)
    assert stats["triangles"] == 1
    assert stats["area"] == pytest.approx(0.5)


@pytest.mark.parametrize("face, message", [
    ("1 2 0", "face 2 has vertex index 0"),
    ("1 2 9", "face 2 names vertex 9; the file has 3"),
    ("1 2 -4", "face 2 names vertex -4; only 3 come before it"),
])
def test_an_obj_face_naming_no_vertex_says_which(tmp_path, face, message):
    path = tmp_path / "bad.obj"
    path.write_text(f"v 0 0 0\nv 1 0 0\nv 1 1 0\nf 1 2 3\nf {face}\n", encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        plain_stats(path)
