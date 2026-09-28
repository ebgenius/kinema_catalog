"""``meshkit convert``: .dae visual meshes to .glb, gated.

Every GLB is produced in a staging directory and only moved next to its source
once it has passed all three checks:

1. the round trip inside Blender (``gate.compare``),
2. the independent trimesh reading of the GLB (``external.glb_stats``), and
3. the shading, raw .dae against GLB with no Blender in between
   (``gate.compare_normals``).

A file that fails any of them stays out of the tree, and the report says why. Nothing
is ever deleted: the .dae stays where it is, because rewriting references to
the new file is a separate, reviewable step.
"""

from __future__ import annotations

import hashlib
import json
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
from meshkit.external import dae_stats, glb_stats
from meshkit.gate import DEFAULT, Tolerance, compare, compare_normals

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


def _judge(result: dict, tolerance: Tolerance) -> tuple[list[str], dict | None]:
    """Both checks for one Blender result: problems found, and trimesh's numbers."""
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
    try:
        source = dae_stats(Path(result["source"]))
        external["source_normal_deviation"] = source["normal_deviation"]
        problems += [f"shading: {p}" for p in compare_normals(
            source["normal_deviation"], external["normal_deviation"], tolerance)]
    except Exception as exc:  # noqa: BLE001
        problems.append(f"pycollada could not read the .dae: {type(exc).__name__}: {exc}")
    return problems, external


def convert(
    targets: list[Target],
    blender: Blender,
    *,
    report_path: Path,
    batch_size: int = 25,
    force: bool = False,
    dry_run: bool = False,
    tolerance: Tolerance = DEFAULT,
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

    pending: list[Target] = []
    for target in targets:
        if target.output.exists() and not force:
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
            jobs = [{"id": t.id, "source": str(t.source),
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
                    staged = Path(result["staged"])
                    try:
                        target.output.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(staged), target.output)
                    except OSError as exc:
                        # One unwritable destination must not end the run: the
                        # GLBs already moved into place need their report.
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
