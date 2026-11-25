"""convert()'s bookkeeping, with a stand-in for the Blender job: no Blender needed."""

import json
import sys
from pathlib import Path

from meshkit import convert as convert_module
from meshkit.blender import TIMED_OUT, Blender
from meshkit.convert import Target, convert, plan

BLENDER = Blender(Path("blender"), (5, 2, 0), "Blender 5.2.0", "test")
STATS = {"triangles": 12, "area": 1.0, "centroid": [0.0, 0.0, 0.0],
         "aabb_min": [-1.0, -1.0, -1.0], "aabb_max": [1.0, 1.0, 1.0]}


def source(root: Path, name: str) -> Path:
    path = root / "src" / "fork" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("<COLLADA/>", encoding="utf-8")
    return path


def fake_job(monkeypatch, result):
    """Stand in for the Blender job: ``result(job)`` is what it reports for each job."""
    def run_script(blender, script, args, *, log_path, **_):
        jobs = json.loads(Path(args[args.index("--jobs") + 1]).read_text(encoding="utf-8"))
        for job in jobs:
            Path(job["staged"]).write_bytes(b"glb")
        payload = {"environment": {}, "results": [result(job) for job in jobs]}
        Path(args[args.index("--results") + 1]).write_text(json.dumps(payload), encoding="utf-8")
        return 0
    monkeypatch.setattr(convert_module, "run_script", run_script)


def run(targets, tmp_path):
    return convert(targets, BLENDER, report_path=tmp_path / "report.json",
                   progress=lambda _: None)


def test_two_sources_of_one_glb_are_both_refused(tmp_path, monkeypatch):
    root = tmp_path / "catalog"
    dae, stl, other = source(root, "part.dae"), source(root, "part.stl"), source(root, "arm.dae")
    seen = []

    def result(job):
        seen.append(Path(job["source"]).name)
        return {"id": job["id"], "ok": False, "error": "stand-in"}
    fake_job(monkeypatch, result)

    report = run(plan([dae, stl, other], root, None), tmp_path)

    assert seen == ["arm.dae"], "neither part may reach Blender"
    by_name = {Path(i["source"]).name: i for i in report["items"]}
    assert by_name["part.dae"]["status"] == by_name["part.stl"]["status"] == "failed"
    assert str(stl) in by_name["part.dae"]["reason"]
    assert str(dae) in by_name["part.stl"]["reason"]
    assert not (root / "src" / "fork" / "part.glb").exists()


def test_dropped_export_options_and_traceback_reach_the_report(tmp_path, monkeypatch):
    # An export option this Blender does not have (renamed, say) moves every
    # mesh; the report has to say which option went, not only that it failed.
    moved = dict(STATS, centroid=[0.0, 0.5, 0.0])
    fake_job(monkeypatch, lambda job: dict(
        job, ok=True, source_stats=STATS, roundtrip_stats=moved,
        dropped_export_options=["export_yup"], traceback=None))
    (item,) = run(plan([source(tmp_path, "a.dae")], tmp_path, None), tmp_path)["items"]
    assert item["status"] == "failed"
    assert item["dropped_export_options"] == ["export_yup"]
    assert "export_yup" in item["reason"]

    fake_job(monkeypatch, lambda job: dict(job, ok=False, error="RuntimeError: boom",
                                           traceback="Traceback: boom"))
    (item,) = run(plan([source(tmp_path, "b.dae")], tmp_path, None), tmp_path)["items"]
    assert item["traceback"] == "Traceback: boom"
    saved = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert saved["items"][0]["traceback"] == "Traceback: boom"


def test_unwritable_destination_fails_that_mesh_not_the_run(tmp_path, monkeypatch):
    fake_job(monkeypatch, lambda job: dict(job, ok=True))
    monkeypatch.setattr(convert_module, "_judge", lambda result, tolerance: ([], None))
    blocker = tmp_path / "blocker"
    blocker.write_text("a file where a directory should be", encoding="utf-8")
    targets = [Target("00000", source(tmp_path, "a.dae"), blocker / "a.glb"),
               Target("00001", source(tmp_path, "b.dae"), tmp_path / "out" / "b.glb")]

    report = run(targets, tmp_path)
    first, second = report["items"]
    assert first["status"] == "failed" and "could not be written" in first["reason"]
    assert second["status"] == "converted"
    assert (tmp_path / "out" / "b.glb").read_bytes() == b"glb"
    assert (tmp_path / "report.json").is_file()


def test_timed_out_batch_says_so(tmp_path, monkeypatch):
    monkeypatch.setattr(convert_module, "run_script", lambda *args, **kwargs: TIMED_OUT)
    (item,) = run(plan([source(tmp_path, "a.dae")], tmp_path, None), tmp_path)["items"]
    assert item["status"] == "failed" and "timed out" in item["reason"]


def test_failed_copy_leaves_the_previous_glb_whole(tmp_path, monkeypatch):
    # Staging is often on another filesystem, where a move is a copy. One that
    # dies half-way must leave the old .glb as it was -- never a truncated one
    # that the next run would skip as done.
    fake_job(monkeypatch, lambda job: dict(job, ok=True))
    monkeypatch.setattr(convert_module, "_judge", lambda result, tolerance: ([], None))

    def copy_half(source, destination, **_):
        Path(destination).write_bytes(Path(source).read_bytes()[:1])
        raise OSError(28, "No space left on device")
    monkeypatch.setattr(convert_module.shutil, "copy2", copy_half)

    (target,) = plan([source(tmp_path, "a.dae")], tmp_path, None)
    target.output.write_bytes(b"the previous, verified glb")
    report = convert([target], BLENDER, report_path=tmp_path / "report.json", force=True,
                     progress=lambda _: None)

    (item,) = report["items"]
    assert item["status"] == "failed" and "No space left" in item["reason"]
    assert target.output.read_bytes() == b"the previous, verified glb"
    assert sorted(p.name for p in target.output.parent.iterdir()) == ["a.dae", "a.glb"]


def test_an_import_that_lost_triangles_fails_the_count(tmp_path, monkeypatch):
    # Round trip and trimesh agree with an import that lost an instance --
    # they start from it. The .dae's own count is what shows the loss.
    sys.path.insert(0, str(Path(__file__).parent))
    from test_convert_blender import flat_box_dae, with_second_instance

    dae = tmp_path / "src" / "fork" / "box.dae"
    dae.parent.mkdir(parents=True)
    flat_box_dae(dae)
    with_second_instance(dae)                  # 24 triangles in the file
    one_box = dict(STATS, triangles=12)
    monkeypatch.setattr(convert_module, "glb_stats", lambda path: dict(
        one_box, normal_deviation=[0.0, 0.0, 0.0]))
    result = {"ok": True, "source": str(dae), "staged": str(tmp_path / "x.glb"),
              "source_stats": one_box, "roundtrip_stats": one_box}

    problems, external = convert_module._judge(result, convert_module.DEFAULT)
    assert problems == ["import: the .dae holds 24 triangles, kinema's import 12"]
    assert external["source_triangles"] == 24


def plain_result(tmp_path, stats, *, angle=30.0):
    """A Blender result for an STL: a 1 x 1 x 1 cube at the origin, one triangle at a time."""
    import numpy as np
    import trimesh

    cube = trimesh.creation.box(extents=(1, 1, 1))
    triangles = cube.vertices[cube.faces]
    stl = tmp_path / "src" / "fork" / "cube.stl"
    stl.parent.mkdir(parents=True, exist_ok=True)
    trimesh.Trimesh(triangles.reshape(-1, 3), np.arange(36).reshape(-1, 3),
                    process=False).export(stl)
    return {"ok": True, "source": str(stl), "staged": str(tmp_path / "x.glb"),
            "smooth_angle": angle, "source_stats": stats, "roundtrip_stats": stats}


CUBE = {"triangles": 12, "area": 6.0, "centroid": [0.0, 0.0, 0.0],
        "aabb_min": [-0.5, -0.5, -0.5], "aabb_max": [0.5, 0.5, 0.5]}


def glb_reading(monkeypatch, stats, deviation, *, p99_9=0.0):
    monkeypatch.setattr(convert_module, "glb_stats", lambda path: dict(
        stats, normal_deviation=deviation, normal_deviation_max=max(deviation)))
    monkeypatch.setattr(convert_module, "smoothing_error", lambda path, angle: {
        "corners": 36, "unchecked": 0, "ambiguous_edges": 0, "p99_9": p99_9, "max": p99_9})


def test_an_stl_that_imported_as_it_is_passes(tmp_path, monkeypatch):
    glb_reading(monkeypatch, CUBE, [0.0, 0.0, 0.0])
    problems, external = convert_module._judge(plain_result(tmp_path, CUBE),
                                               convert_module.DEFAULT)
    assert problems == []
    assert external["source_triangles"] == external["source_file_triangles"] == 12


def test_an_stl_import_that_moved_fails_against_the_file(tmp_path, monkeypatch):
    # Blender's round trip agrees with an import rotated from Y-up -- it
    # starts from it. The file, read raw, is what shows it.
    rotated = dict(CUBE, centroid=[0.0, 0.3, 0.0])
    glb_reading(monkeypatch, rotated, [0.0, 0.0, 0.0])
    problems, _ = convert_module._judge(plain_result(tmp_path, rotated), convert_module.DEFAULT)
    assert problems and all(p.startswith("import: centroid moved") for p in problems)


def test_an_stl_not_smoothed_as_the_angle_says_fails_the_shading(tmp_path, monkeypatch):
    glb_reading(monkeypatch, CUBE, [30.0, 50.0, 54.7], p99_9=54.7)
    problems, external = convert_module._judge(plain_result(tmp_path, CUBE, angle=30.0),
                                               convert_module.DEFAULT)
    assert problems == ["shading: normals: p99.9 corner is 54.7 deg from what smoothing "
                        "at 30 deg makes (limit 2)"]
    assert external["smoothing"]["p99_9"] == 54.7


def test_case_is_one_file_everywhere():
    same = convert_module._same_file
    assert same(Path("fork/Part.glb")) == same(Path("fork/part.glb"))


def test_the_smoothing_angle_reaches_the_job(tmp_path, monkeypatch):
    seen = []

    def result(job):
        seen.append(job["smooth_angle"])
        return {"id": job["id"], "ok": False, "error": "stand-in"}
    fake_job(monkeypatch, result)
    convert(plan([source(tmp_path, "a.dae")], tmp_path, None), BLENDER,
            report_path=tmp_path / "report.json", smooth_angle=12.5, progress=lambda _: None)
    assert seen == [12.5]
