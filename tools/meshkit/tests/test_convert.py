"""convert()'s bookkeeping, with a stand-in for the Blender job: no Blender needed."""

import json
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
