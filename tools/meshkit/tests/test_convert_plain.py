"""STL and OBJ through a real Blender: welded, smoothed by angle, gated. Skipped without one."""

from pathlib import Path

import numpy as np
import pytest
import trimesh

from meshkit.convert import convert, plan
from meshkit.external import glb_stats

NEUTRAL = "meshkit_neutral"   # blender_side/job.py's, which needs bpy to import

pytestmark = pytest.mark.blender

OFFSET = np.array([0.1, 0.2, 0.3])   # unequal on every axis: a rotated import moves it


def cylinder_stl(path: Path, sections: int = 32) -> trimesh.Trimesh:
    """A 32-sided cylinder, one STL triangle at a time, off the origin.

    Its sides meet at 11.25 degrees, under the smoothing angle; sides and caps
    meet at 90, over it. So a smoothed GLB has round sides and flat caps.
    """
    mesh = trimesh.creation.cylinder(radius=0.05, height=0.2, sections=sections)
    mesh.apply_translation(OFFSET)
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(path)      # binary STL: every corner written once per triangle
    return mesh


def convert_one(tmp_path: Path, source: Path, blender, **kwargs) -> tuple[dict, Path]:
    root = tmp_path / "catalog"
    out = tmp_path / "out"
    report = convert(plan([source], root, out), blender, report_path=tmp_path / "report.json",
                     progress=lambda _: None, **kwargs)
    (item,) = report["items"]
    return item, (out / source.relative_to(root)).with_suffix(".glb")


def corner_deviation(glb: Path) -> np.ndarray:
    """Each corner's angle from its own face, in degrees, by face orientation.

    Returns (n, 2): the face normal's |z| (1 on a cap, 0 on a side) and the angle.
    """
    scene = trimesh.load(str(glb), force="scene", process=False)
    rows = []
    for node in scene.graph.nodes_geometry:
        transform, name = scene.graph[node]
        geometry = scene.geometry[name]
        vertices = geometry.vertices @ transform[:3, :3].T
        normals = np.asarray(geometry.vertex_normals) @ np.linalg.inv(transform[:3, :3])
        tri = vertices[geometry.faces]
        face = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        face /= np.linalg.norm(face, axis=1)[:, None]
        corner = normals[geometry.faces]
        corner /= np.linalg.norm(corner, axis=2)[..., None]
        angle = np.degrees(np.arccos(np.clip((corner * face[:, None]).sum(axis=2), -1, 1)))
        # glTF is Y-up: the cylinder's axis, Z in the file, is Y in the GLB.
        up = np.abs(face[:, 1])
        rows.append(np.column_stack([np.repeat(up, 3), angle.ravel()]))
    return np.concatenate(rows)


def test_an_stl_is_welded_smoothed_by_angle_and_kept_in_place(tmp_path, blender):
    stl = tmp_path / "catalog" / "src" / "fork" / "meshes" / "cylinder.stl"
    mesh = cylinder_stl(stl)
    before = stl.read_bytes()

    item, glb = convert_one(tmp_path, stl, blender)

    assert item["status"] == "converted", item["problems"]
    assert stl.read_bytes() == before, "the source must never be touched"
    assert item["external_stats"]["source_triangles"] == len(mesh.faces)
    stats = item["source_stats"]
    assert stats["triangles"] == len(mesh.faces)
    assert stats["area"] == pytest.approx(mesh.area, rel=1e-5)
    # In place, axes untouched: an OBJ-style Y-up import would swap y and z.
    assert stats["centroid"] == pytest.approx(list(mesh.center_mass), abs=1e-5)

    deviation = corner_deviation(glb)
    caps, sides = deviation[deviation[:, 0] > 0.99], deviation[deviation[:, 0] < 0.01]
    assert caps[:, 1].max() < 0.5, "a 90 degree edge must stay sharp"
    # Smoothed: each side corner leans half a section (5.6 deg) towards its neighbour.
    assert sides[:, 1].min() > 4.0 and sides[:, 1].max() < 7.0


def test_a_smaller_angle_leaves_the_sides_faceted(tmp_path, blender):
    stl = tmp_path / "catalog" / "src" / "fork" / "cylinder.stl"
    cylinder_stl(stl)

    item, glb = convert_one(tmp_path, stl, blender, smooth_angle=10.0)

    assert item["status"] == "converted", item["problems"]
    assert item["smooth_angle"] == 10.0
    assert corner_deviation(glb)[:, 1].max() < 0.5    # 11.25 deg sides, over 10: all sharp


def test_an_stl_has_the_neutral_material(tmp_path, blender):
    stl = tmp_path / "catalog" / "src" / "fork" / "cylinder.stl"
    cylinder_stl(stl)

    item, glb = convert_one(tmp_path, stl, blender)

    assert item["status"] == "converted", item["problems"]
    scene = trimesh.load(str(glb), force="scene", process=False)
    names = {geometry.visual.material.name for geometry in scene.geometry.values()}
    assert names == {NEUTRAL}


def test_an_obj_keeps_its_material_and_its_axes(tmp_path, blender):
    folder = tmp_path / "catalog" / "src" / "fork" / "meshes"
    folder.mkdir(parents=True)
    (folder / "part.mtl").write_text(
        "newmtl orange\nKd 1.0 0.3 0.0\nKa 0 0 0\nKs 0 0 0\nd 1.0\nillum 1\n", encoding="utf-8")
    box = trimesh.creation.box(extents=(0.1, 0.2, 0.3))
    box.apply_translation(OFFSET)
    lines = ["mtllib part.mtl", "usemtl orange"]
    lines += [f"v {x:.6f} {y:.6f} {z:.6f}" for x, y, z in box.vertices]
    lines += [f"f {a + 1} {b + 1} {c + 1}" for a, b, c in box.faces]
    obj = folder / "part.obj"
    obj.write_text("\n".join(lines) + "\n", encoding="utf-8")

    item, glb = convert_one(tmp_path, obj, blender)

    assert item["status"] == "converted", item["problems"]
    # Raw in the link's frame, as ROS reads an OBJ: not rotated from Y-up.
    assert item["source_stats"]["centroid"] == pytest.approx(list(OFFSET), abs=1e-5)
    scene = trimesh.load(str(glb), force="scene", process=False)
    (material,) = {g.visual.material.name: g.visual.material
                   for g in scene.geometry.values()}.values()
    assert material.name != NEUTRAL
    # glTF stores the base colour linear; Blender's OBJ importer reads Kd as such.
    assert np.asarray(material.baseColorFactor[:3], dtype=float) / 255 == pytest.approx(
        [1.0, 0.3, 0.0], abs=0.02)
    # A box's edges are 90 degrees: nothing to smooth, and it stays flat.
    assert max(glb_stats(glb)["normal_deviation"]) < 0.5


def write_obj(path: Path, objects: dict[str, tuple[np.ndarray, list[tuple[int, ...]], str | None]],
              colours: dict[str, tuple[float, float, float]] | None = None) -> Path:
    """An OBJ of named objects, each its vertices, its faces (local, 0-based) and material."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if colours:
        path.with_suffix(".mtl").write_text("".join(
            f"newmtl {name}\nKd {r} {g} {b}\nKa 0 0 0\nKs 0 0 0\nd 1.0\nillum 1\n"
            for name, (r, g, b) in colours.items()), encoding="utf-8")
        lines.append(f"mtllib {path.with_suffix('.mtl').name}")
    offset = 0
    for name, (vertices, faces, material) in objects.items():
        lines.append(f"o {name}")
        if material:
            lines.append(f"usemtl {material}")
        lines += [f"v {x:.6f} {y:.6f} {z:.6f}" for x, y, z in vertices]
        lines += ["f " + " ".join(str(i + 1 + offset) for i in face) for face in faces]
        offset += len(vertices)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_doubled_faces_go_within_an_object_and_stay_across(tmp_path, blender):
    box = trimesh.creation.box(extents=(0.1, 0.2, 0.3))
    box.apply_translation(OFFSET)
    first = tuple(box.faces[0])
    obj = write_obj(tmp_path / "catalog" / "src" / "fork" / "part.obj", {
        # Blender's OBJ importer keeps a face repeated on the same vertices.
        "a": (box.vertices, [tuple(f) for f in box.faces] + [first[::-1]], None),
        "b": (box.vertices[list(first)], [(0, 1, 2)], None),
    })

    item, _ = convert_one(tmp_path, obj, blender)

    assert item["status"] == "converted", item["problems"]
    assert item["doubled_faces"] == 1
    assert item["source_stats"]["triangles"] == 13
    assert item["external_stats"]["source_file_triangles"] == 14


def test_a_doubled_stl_triangle_is_counted_out_on_both_sides(tmp_path, blender):
    stl = tmp_path / "catalog" / "src" / "fork" / "cylinder.stl"
    mesh = cylinder_stl(stl)
    corners = mesh.vertices[mesh.faces]
    triangles = np.concatenate([corners, corners[:1], corners[1:2, ::-1]])
    trimesh.Trimesh(triangles.reshape(-1, 3), np.arange(len(triangles) * 3).reshape(-1, 3),
                    process=False).export(stl)

    item, _ = convert_one(tmp_path, stl, blender)

    assert item["status"] == "converted", item["problems"]
    assert item["external_stats"]["source_file_triangles"] == len(mesh.faces) + 2
    assert item["source_stats"]["triangles"] == len(mesh.faces)


def test_the_neutral_material_never_takes_over_the_files_own(tmp_path, blender):
    box = trimesh.creation.box(extents=(0.1, 0.2, 0.3))
    faces = [tuple(f) for f in box.faces]
    obj = write_obj(tmp_path / "catalog" / "src" / "fork" / "part.obj", {
        # First: in an OBJ, a usemtl holds on into the objects after it.
        "bare": (box.vertices - OFFSET, faces, None),
        "painted": (box.vertices + OFFSET, faces, NEUTRAL),     # the file's, by that name
    }, colours={NEUTRAL: (1.0, 0.3, 0.0)})

    item, glb = convert_one(tmp_path, obj, blender)

    assert item["status"] == "converted", item["problems"]
    assert item["neutral_material"] is True
    scene = trimesh.load(str(glb), force="scene", process=False)
    colours = {g.visual.material.name: np.asarray(g.visual.material.baseColorFactor[:3]) / 255
               for g in scene.geometry.values()}
    assert len(colours) == 2
    assert colours[NEUTRAL] == pytest.approx([1.0, 0.3, 0.0], abs=0.02)
    (added,) = set(colours) - {NEUTRAL}
    assert added.startswith(NEUTRAL)
    assert colours[added] == pytest.approx([0.7, 0.7, 0.7], abs=0.02)


def test_a_degenerate_stl_triangle_is_counted_out_on_both_sides(tmp_path, blender):
    stl = tmp_path / "catalog" / "src" / "fork" / "cylinder.stl"
    mesh = cylinder_stl(stl)
    corners = mesh.vertices[mesh.faces]
    sliver = corners[:1].copy()
    sliver[0, 1] = sliver[0, 0]                     # two corners at one point
    triangles = np.concatenate([corners, sliver])
    trimesh.Trimesh(triangles.reshape(-1, 3), np.arange(len(triangles) * 3).reshape(-1, 3),
                    process=False).export(stl)

    item, _ = convert_one(tmp_path, stl, blender)

    assert item["status"] == "converted", item["problems"]
    assert item["external_stats"]["source_file_triangles"] == len(mesh.faces) + 1
    assert item["source_stats"]["triangles"] == len(mesh.faces)


def test_a_fine_cone_passes_though_its_tip_is_far_from_every_face(tmp_path, blender):
    # 100 sections, 5.7 degrees from the axis: neighbouring sides meet at about
    # 3.6 degrees, so the tip is smoothed all the way round and its normal
    # points up the axis, 84 degrees from each face. A sixth of the corners
    # are at the tip -- too many for any percentile of that angle to absorb.
    cone = trimesh.creation.cone(radius=0.02, height=0.2, sections=100)
    cone.apply_translation(OFFSET)
    stl = tmp_path / "catalog" / "src" / "fork" / "tip.stl"
    stl.parent.mkdir(parents=True)
    cone.export(stl)

    item, glb = convert_one(tmp_path, stl, blender)

    assert item["status"] == "converted", item["problems"]
    assert glb_stats(glb)["normal_deviation"][-1] > 80     # p99 from the face
    assert item["external_stats"]["smoothing"]["p99_9"] < 0.5


def test_an_objs_own_normals_give_way_to_the_smoothing(tmp_path, blender):
    mesh = trimesh.creation.cylinder(radius=0.05, height=0.2, sections=32)
    lines = [f"v {x:.6f} {y:.6f} {z:.6f}" for x, y, z in mesh.vertices]
    lines += [f"vn {x:.6f} {y:.6f} {z:.6f}" for x, y, z in mesh.face_normals]   # faceted
    lines += [f"f {a + 1}//{i + 1} {b + 1}//{i + 1} {c + 1}//{i + 1}"
              for i, (a, b, c) in enumerate(mesh.faces)]
    obj = tmp_path / "catalog" / "src" / "fork" / "flat.obj"
    obj.parent.mkdir(parents=True)
    obj.write_text("\n".join(lines) + "\n", encoding="utf-8")

    item, glb = convert_one(tmp_path, obj, blender)

    assert item["status"] == "converted", item["problems"]
    assert item["dropped_normals"] is True
    deviation = corner_deviation(glb)
    sides = deviation[deviation[:, 0] < 0.01]
    assert sides[:, 1].min() > 4.0 and sides[:, 1].max() < 7.0      # round, not faceted


def test_a_warped_quad_obj_is_smoothed_as_its_triangles(tmp_path, blender):
    # A saddle of quads, each warped: smoothed whole, a quad has one normal
    # that the two triangles it is exported as do not share.
    size = 6
    xs = np.linspace(-0.1, 0.1, size)
    lines = [f"v {x:.6f} {y:.6f} {30 * x * y:.6f}" for y in xs for x in xs]
    for j in range(size - 1):
        for i in range(size - 1):
            a = j * size + i + 1
            lines.append(f"f {a} {a + 1} {a + size + 1} {a + size}")
    obj = tmp_path / "catalog" / "src" / "fork" / "saddle.obj"
    obj.parent.mkdir(parents=True)
    obj.write_text("\n".join(lines) + "\n", encoding="utf-8")

    item, _ = convert_one(tmp_path, obj, blender, smooth_angle=10.0)

    assert item["status"] == "converted", item["problems"]
    assert item["source_stats"]["triangles"] == 2 * (size - 1) ** 2


def square_obj(path: Path, body: str, colours: dict[str, tuple[float, float, float]] | None = None
               ) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    head = ""
    if colours:
        path.with_suffix(".mtl").write_text("".join(
            f"newmtl {name}\nKd {r} {g} {b}\nKa 0 0 0\nKs 0 0 0\nd 1.0\nillum 1\n"
            for name, (r, g, b) in colours.items()), encoding="utf-8")
        head = f"mtllib {path.with_suffix('.mtl').name}\n"
    path.write_text(head + "v 0 0 0\nv 0.1 0 0\nv 0.1 0.1 0\nv 0 0.1 0\n" + body,
                    encoding="utf-8")
    return path


def test_a_quad_written_twice_leaves_one_square(tmp_path, blender):
    # Shifted and reversed: each split alone takes another diagonal, and
    # four triangles of one square would pass a check of triangles.
    obj = square_obj(tmp_path / "catalog" / "src" / "fork" / "twice.obj",
                     "f 1 2 3 4\nf 2 3 4 1\nf 4 3 2 1\n")

    item, _ = convert_one(tmp_path, obj, blender)

    assert item["status"] == "converted", item["problems"]
    assert item["source_stats"]["triangles"] == 2
    assert item["source_stats"]["area"] == pytest.approx(0.01)
    assert item["doubled_faces"] == 4         # in triangles: two quads' worth
    assert item["external_stats"]["source_file_triangles"] == 6


@pytest.mark.parametrize("first, kept", [
    ("usemtl quad\nf 1 2 3 4\nusemtl tri\nf 1 2 3\n", {"quad": 2}),
    ("usemtl tri\nf 1 2 3\nusemtl quad\nf 1 2 3 4\n", {"tri": 1, "quad": 1}),
])
def test_the_first_face_in_the_file_keeps_its_material(tmp_path, blender, first, kept):
    obj = square_obj(tmp_path / "catalog" / "src" / "fork" / "part.obj", first,
                     colours={"quad": (1.0, 0.0, 0.0), "tri": (0.0, 0.0, 1.0)})

    item, glb = convert_one(tmp_path, obj, blender)

    assert item["status"] == "converted", item["problems"]
    assert item["doubled_faces"] == 1
    scene = trimesh.load(str(glb), force="scene", process=False)
    assert {g.visual.material.name: len(g.faces) for g in scene.geometry.values()} == kept


def test_a_polygon_that_repeats_a_corner_counts_alike_on_both_sides(tmp_path, blender):
    obj = tmp_path / "catalog" / "src" / "fork" / "bowtie.obj"
    obj.parent.mkdir(parents=True)
    obj.write_text("v 0 0 0\nv 0.1 0 0\nv 0.1 0.1 0\nv 0 0 0\nv -0.1 0 0\nv -0.1 -0.1 0\n"
                   "f 1 2 3 4 5 6\n", encoding="utf-8")

    item, _ = convert_one(tmp_path, obj, blender)

    assert item["status"] == "converted", item["problems"]
    assert item["source_stats"]["triangles"] == 2
    assert item["external_stats"]["source_triangles"] == 2
