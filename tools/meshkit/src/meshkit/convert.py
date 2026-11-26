"""``meshkit convert``: .dae, .stl and .obj visual meshes to .glb, gated.

For an .stl or .obj, checks 3 and 4 read the file without pycollada
(``external.plain_stats``), and the shading check holds the new normals to what
smoothing by angle makes instead of to the file's (``_judge_plain``).

Every GLB is produced in a staging directory and only moved next to its source
once it has passed all four checks:

1. the round trip inside Blender (``gate.compare``),
2. the independent trimesh reading of the GLB (``external.glb_stats``),
3. the triangle count of the raw .dae against the import's -- the one count
   that does not start from the import (``external.dae_stats``), and
4. the shading, raw .dae against GLB with no Blender in between
   (``gate.compare_normals``).

A file that fails any of them stays out of the tree, and the report says why. So
do two sources that would write the same GLB (``part.dae`` beside ``part.stl``):
neither is converted, rather than one silently replacing the other. Nothing
is ever deleted: the .dae stays where it is, because rewriting references to
the new file is a separate, reviewable step.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import collada

from meshkit import __version__
from meshkit._vendor import VENDORED_FILE, importer_provenance
from meshkit.blender import TIMED_OUT, Blender, run_script
from meshkit.external import dae_stats, glb_stats, plain_stats, smoothing_error
from meshkit.gate import (DEFAULT, SMOOTH_ANGLE, Tolerance, check_smoothed, compare,
                          compare_normals)

JOB_SCRIPT = Path(__file__).parent / "blender_side" / "job.py"


def site_packages() -> Path:
    """The directory holding meshkit's pinned pycollada, for the Blender job."""
    return Path(collada.__file__).resolve().parent.parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class Target:
    id: str
    source: Path
    output: Path


@dataclass
class Item:
    id: str
    source: str
    output: str
    status: str                     # converted | failed | skipped
    reason: str | None = None
    problems: list[str] = field(default_factory=list)
    source_sha256: str | None = None
    output_sha256: str | None = None
    up_axis: str | None = None
    unit_meter: float | None = None
    # STL and OBJ only: what was done to the mesh on its way to the GLB.
    smooth_angle: float | None = None
    welded_vertices: int | None = None
    doubled_faces: int | None = None
    dropped_normals: bool | None = None     # an OBJ's own, replaced by the smoothing
    neutral_material: bool | None = None
    importer_warnings: list[str] = field(default_factory=list)
    # glTF export options this Blender does not have, so the export ran without them.
    dropped_export_options: list[str] = field(default_factory=list)
    traceback: str | None = None    # of a Blender job that raised
    source_stats: dict | None = None
    roundtrip_stats: dict | None = None
    external_stats: dict | None = None
    seconds: float | None = None


def plan(sources: list[Path], root: Path, out_dir: Path | None) -> list[Target]:
    """Where each GLB goes: next to its source, or mirrored under ``out_dir``."""
    targets = []
    for index, source in enumerate(sorted(set(sources))):
        if out_dir is None:
            output = source.with_suffix(".glb")
        else:
            output = (out_dir / source.relative_to(root)).with_suffix(".glb")
        targets.append(Target(f"{index:05d}", source, output))
    return targets


def _publish(staged: Path, output: Path) -> None:
    """Put a verified GLB at ``output`` whole, or leave ``output`` as it was.

    Staging sits in the system temp directory, often another filesystem, where
    a move is a copy -- and a copy that dies half-way leaves a truncated .glb
    that the next run skips as done, or under --force, a good one truncated.
    So the copy is made beside the destination, and renamed over it once whole.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp",
                                    dir=output.parent)
    os.close(handle)
    temporary = Path(name)
    try:
        shutil.copy2(staged, temporary)   # copy2: the mode too, not mkstemp's 0600
        os.replace(temporary, output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _same_file(path: Path) -> str:
    """One key for every spelling of a path, case included.

    Case-folded everywhere, not only where the filesystem ignores case
    (Windows, and macOS by default): ``Part.glb`` and ``part.glb`` are two
    files on Linux but one in a clone on either of the others, and a fork is
    cloned on all three. The directory is resolved, so a symlinked folder
    meets its target; the file name is not, since ``_publish`` replaces the
    entry itself rather than what it points to.
    """
    resolved = os.path.join(os.path.realpath(path.parent), path.name)
    return os.path.normcase(resolved).casefold()


def _judge(result: dict, tolerance: Tolerance) -> tuple[list[str], dict | None]:
    """The checks for one Blender result: problems found, and the outside numbers."""
    if not result.get("ok"):
        return [result.get("error", "Blender job failed without a message")], None
    problems = [f"round trip: {p}" for p in
                compare(result["source_stats"], result["roundtrip_stats"], tolerance)]
    external = None
    try:
        external = glb_stats(Path(result["staged"]))
        problems += [f"trimesh: {p}" for p in
                     compare(result["source_stats"], external, tolerance, check_frame=False)]
    except Exception as exc:  # noqa: BLE001 - an unreadable GLB is a failure, not a crash
        problems.append(f"trimesh could not read the GLB: {type(exc).__name__}: {exc}")
        return problems, external
    if Path(result["source"]).suffix.lower() != ".dae":
        return problems + _judge_plain(result, external, tolerance), external
    try:
        source = dae_stats(Path(result["source"]))
        external["source_normal_deviation"] = source["normal_deviation"]
        external["source_triangles"] = source["triangles"]
        # Every other count starts from the import; this one is the file's own.
        imported = (result.get("source_stats") or {}).get("triangles")
        if source["triangles"] != imported:
            problems.append(f"import: the .dae holds {source['triangles']} triangles, "
                            f"kinema's import {imported}")
        problems += [f"shading: {p}" for p in compare_normals(
            source["normal_deviation"], external["normal_deviation"], tolerance)]
    except Exception as exc:  # noqa: BLE001
        problems.append(f"pycollada could not read the .dae: {type(exc).__name__}: {exc}")
    return problems, external


def _judge_plain(result: dict, external: dict, tolerance: Tolerance) -> list[str]:
    """The STL and OBJ checks that start from the file rather than the import.

    * **the file against the import:** ``plain_stats`` reads the file raw,
      welds it as the job does, and its triangles, area, centroid and bounds must match
      what Blender imported -- positions included, since both read it in the
      link's frame. Geometry unchanged means this.
    * **the shading:** the normals are new on purpose, so they cannot be held
      against the file's. Instead they must be what smoothing by angle makes
      of the GLB's own triangles (``external.smoothing_error``,
      ``gate.check_smoothed``).
    """
    problems: list[str] = []
    try:
        source = plain_stats(Path(result["source"]))
    except Exception as exc:  # noqa: BLE001
        return [f"trimesh could not read the source: {type(exc).__name__}: {exc}"]
    external["source_triangles"] = source["triangles"]
    external["source_file_triangles"] = source["file_triangles"]
    problems += [f"import: {p}" for p in compare(source, result["source_stats"], tolerance)]
    try:
        external["smoothing"] = smoothing_error(Path(result["staged"]), result["smooth_angle"])
    except Exception as exc:  # noqa: BLE001
        return problems + [f"shading: could not measure the smoothing: "
                           f"{type(exc).__name__}: {exc}"]
    problems += [f"shading: {p}" for p in check_smoothed(
        external["smoothing"], result["smooth_angle"], tolerance)]
    return problems


def convert(
    targets: list[Target],
    blender: Blender,
    *,
    report_path: Path,
    batch_size: int = 25,
    force: bool = False,
    dry_run: bool = False,
    tolerance: Tolerance = DEFAULT,
    smooth_angle: float = SMOOTH_ANGLE,
    progress=print,
) -> dict:
    provenance = importer_provenance()
    report: dict = {
        "meshkit": __version__,
        "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "blender": {"path": str(blender.path), "version": blender.version_string},
        "importer": provenance,
        "tolerance": asdict(tolerance),
        "dry_run": dry_run,
        "environment": None,
        "items": [],
    }
    items: list[Item] = []

    # Two sources, one GLB: part.dae and part.stl side by side. Both would pass
    # and the second would replace the first, so neither goes.
    claims: dict[str, list[Target]] = {}
    for target in targets:
        claims.setdefault(_same_file(target.output), []).append(target)

    pending: list[Target] = []
    for target in targets:
        rivals = [t for t in claims[_same_file(target.output)] if t is not target]
        if rivals:
            items.append(Item(target.id, str(target.source), str(target.output), "failed",
                              reason="the same GLB is the output of "
                                     + ", ".join(str(t.source) for t in rivals)
                                     + "; neither is converted"))
        elif target.output.exists() and not force:
            items.append(Item(target.id, str(target.source), str(target.output),
                              "skipped", reason="output exists (use --force to redo)"))
        else:
            pending.append(target)

    if dry_run:
        for target in pending:
            items.append(Item(target.id, str(target.source), str(target.output),
                              "skipped", reason="dry run"))
        report["items"] = [asdict(i) for i in items]
        return _finish(report, report_path)

    logs = report_path.parent / (report_path.stem + "-logs")
    with tempfile.TemporaryDirectory(prefix="meshkit-") as staging_root:
        staging = Path(staging_root)
        for number, start in enumerate(range(0, len(pending), batch_size), start=1):
            batch = pending[start:start + batch_size]
            progress(f"batch {number}: {len(batch)} mesh(es)")
            jobs = [{"id": t.id, "source": str(t.source), "smooth_angle": smooth_angle,
                     "staged": str(staging / f"{t.id}.glb")} for t in batch]
            jobs_file = staging / f"jobs-{number}.json"
            results_file = staging / f"results-{number}.json"
            jobs_file.write_text(json.dumps(jobs, indent=2), encoding="utf-8")

            began = time.perf_counter()
            code = run_script(
                blender, JOB_SCRIPT,
                ["--importer", str(VENDORED_FILE), "--site", str(site_packages()),
                 "--jobs", str(jobs_file), "--results", str(results_file)],
                log_path=logs / f"batch-{number}.log",
            )
            progress(f"  blender exited {code} after {time.perf_counter() - began:.1f}s")

            payload = (json.loads(results_file.read_text(encoding="utf-8"))
                       if results_file.is_file() else {"results": []})
            report["environment"] = report["environment"] or payload.get("environment")
            by_id = {r["id"]: r for r in payload.get("results", [])}

            for target in batch:
                result = by_id.get(target.id)
                item = Item(target.id, str(target.source), str(target.output), "failed",
                            source_sha256=sha256(target.source))
                if result is None:
                    timed_out = " (timed out)" if code == TIMED_OUT else ""
                    item.reason = (f"no result -- Blender exited {code}{timed_out}; "
                                   f"see {logs / f'batch-{number}.log'}")
                    items.append(item)
                    continue
                item.up_axis = result.get("up_axis")
                item.unit_meter = result.get("unit_meter")
                item.smooth_angle = result.get("smooth_angle")
                item.welded_vertices = result.get("welded_vertices")
                item.doubled_faces = result.get("doubled_faces")
                item.dropped_normals = result.get("dropped_normals")
                item.neutral_material = result.get("neutral_material")
                item.importer_warnings = result.get("importer_warnings", [])
                item.dropped_export_options = result.get("dropped_export_options", [])
                item.traceback = result.get("traceback")
                item.source_stats = result.get("source_stats")
                item.roundtrip_stats = result.get("roundtrip_stats")
                item.seconds = result.get("seconds")

                problems, external = _judge(result, tolerance)
                item.external_stats = external
                item.problems = problems
                if problems:
                    item.reason = "failed verification"
                    if item.dropped_export_options:
                        # A renamed option (export_yup, say) fails every mesh the
                        # same way; this is the line that says why.
                        item.reason += ("; this Blender has no glTF export option(s) "
                                        + ", ".join(item.dropped_export_options))
                else:
                    try:
                        _publish(Path(result["staged"]), target.output)
                    except OSError as exc:
                        # One unwritable destination must not end the run: the
                        # GLBs already in place need their report.
                        item.reason = f"passed verification, but could not be written: {exc}"
                    else:
                        item.status = "converted"
                        item.output_sha256 = sha256(target.output)
                items.append(item)
                mark = "ok  " if item.status == "converted" else "FAIL"
                detail = problems[0] if problems else item.reason
                progress(f"  {mark} {target.source.name}"
                         + (f" -- {detail}" if item.status != "converted" else ""))

    report["items"] = [asdict(i) for i in sorted(items, key=lambda i: i.id)]
    return _finish(report, report_path)


def _finish(report: dict, report_path: Path) -> dict:
    counts: dict[str, int] = {}
    for item in report["items"]:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    report["summary"] = counts
    report["finished"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
