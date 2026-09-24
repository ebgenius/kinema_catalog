"""The ``meshkit`` command line."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path

from meshkit import __version__
from meshkit._vendor import COMMIT, SHA256, importer_provenance
from meshkit.blender import ENV_VAR, BlenderNotFound, find_blender, run_script
from meshkit.gate import Tolerance


def find_root(start: Path) -> Path:
    """The catalog checkout: the nearest ancestor with src/ and docker/robots.tsv."""
    for candidate in (start, *start.parents):
        if (candidate / "src").is_dir() and (candidate / "docker" / "robots.tsv").is_file():
            return candidate
    raise SystemExit(f"meshkit: {start} is not inside a kinema_catalog checkout (use --root)")


def _root(args) -> Path:
    return (args.root or find_root(Path.cwd())).resolve()


# ----------------------------------------------------------------------- doctor

def cmd_doctor(args) -> int:
    from meshkit.convert import JOB_SCRIPT, site_packages
    from meshkit._vendor import VENDORED_FILE

    ok = True
    print(f"meshkit {__version__}")
    try:
        blender = find_blender()
        print(f"  blender   {blender.describe()}")
    except BlenderNotFound as exc:
        print(f"  blender   NOT FOUND -- {exc}")
        return 2

    provenance = importer_provenance()
    drift = "" if provenance["matches_pinned"] else "   <-- DIFFERS from the pinned copy"
    patches = f" + {len(provenance['patches'])} patch(es)" if provenance["patches"] else ""
    print(f"  importer  kinema {COMMIT[:12]}{patches} {provenance['path']}{drift}")
    ok &= bool(provenance["matches_pinned"])

    with tempfile.TemporaryDirectory(prefix="meshkit-doctor-") as tmp:
        results = Path(tmp) / "probe.json"
        code = run_script(blender, JOB_SCRIPT,
                          ["--importer", str(VENDORED_FILE), "--site", str(site_packages()),
                           "--probe", "--results", str(results)],
                          log_path=Path(tmp) / "probe.log")
        if code != 0 or not results.is_file():
            print(f"  probe     FAILED (Blender exited {code})")
            print((Path(tmp) / "probe.log").read_text(encoding="utf-8", errors="replace")[-2000:])
            return 1
        env = json.loads(results.read_text(encoding="utf-8"))["environment"]

    print(f"  python    {env['python']} (numpy {env['numpy']})")
    print(f"  pycollada {env['collada_version']} from {env['collada_path']}")
    print(f"  glTF      export={env['gltf_export']} import={env['gltf_import']}")
    ok &= env["gltf_export"] and env["gltf_import"]
    print("ready" if ok else "NOT ready")
    return 0 if ok else 1


# ------------------------------------------------------------------------- scan

def cmd_scan(args) -> int:
    from meshkit.scan import scan

    root = _root(args)
    inventory = scan(root)
    forks = args.fork or inventory.forks()

    if args.json:
        payload = {
            fork: {
                "visual": [str(m.path) for m in inventory.visual(fork)],
                "meshes": [{"path": str(m.path), "roles": sorted(m.roles), "up_axis": m.up_axis}
                           for m in inventory.in_fork(fork)],
                "unresolved": [{"source": str(r.source), "line": r.line, "raw": r.raw,
                                "role": r.role, "problem": r.problem}
                               for r in inventory.unresolved(fork)],
            }
            for fork in forks
        }
        json.dump(payload, sys.stdout, indent=2)
        print()
        return 0

    if args.list:
        for fork in forks:
            for mesh in inventory.in_fork(fork):
                wanted = {
                    "visual": mesh.is_visual,
                    "collision": mesh.is_collision and not mesh.is_visual,
                    "unreferenced": not mesh.roles,
                }[args.list]
                if wanted:
                    print(mesh.path.relative_to(root).as_posix())
        return 0

    header = f"{'fork':36} {'.dae':>5} {'visual':>7} {'coll.':>6} {'both':>5} {'unref':>6} {'Y_UP':>5} {'unres.':>7}"
    print(header)
    print("-" * len(header))
    totals: Counter = Counter()
    for fork in forks:
        meshes = inventory.in_fork(fork)
        row = Counter(
            dae=len(meshes),
            visual=sum(m.is_visual for m in meshes),
            collision=sum(m.is_collision and not m.is_visual for m in meshes),
            both=sum(m.is_visual and m.is_collision for m in meshes),
            unreferenced=sum(not m.roles for m in meshes),
            y_up=sum(m.up_axis == "Y_UP" for m in meshes),
            unresolved=len(inventory.unresolved(fork)),
        )
        totals.update(row)
        if row["dae"] or row["unresolved"]:
            print(f"{fork:36} {row['dae']:>5} {row['visual']:>7} {row['collision']:>6} "
                  f"{row['both']:>5} {row['unreferenced']:>6} {row['y_up']:>5} {row['unresolved']:>7}")
    print("-" * len(header))
    print(f"{'total':36} {totals['dae']:>5} {totals['visual']:>7} {totals['collision']:>6} "
          f"{totals['both']:>5} {totals['unreferenced']:>6} {totals['y_up']:>5} {totals['unresolved']:>7}")

    if args.unresolved:
        print()
        for fork in forks:
            for ref in inventory.unresolved(fork):
                print(f"{ref.source.relative_to(root).as_posix()}:{ref.line}  [{ref.role}]  "
                      f"{ref.raw!r}  -- {ref.problem}")
    return 0


# ---------------------------------------------------------------------- convert

def cmd_convert(args) -> int:
    from meshkit.convert import convert, plan
    from meshkit.scan import scan

    root = _root(args)
    if args.file:
        sources = [Path(f).resolve() for f in args.file]
        missing = [s for s in sources if not s.is_file()]
        if missing:
            raise SystemExit("meshkit: no such file: " + ", ".join(map(str, missing)))
    else:
        if not args.fork:
            raise SystemExit("meshkit convert: name at least one --fork, or --file")
        inventory = scan(root)
        unknown = sorted(set(args.fork) - set(inventory.forks()))
        if unknown:
            raise SystemExit("meshkit: unknown fork(s): " + ", ".join(unknown))
        sources = [m.path for fork in args.fork for m in inventory.visual(fork)]

    if not sources:
        print("nothing to convert")
        return 0

    try:
        blender = find_blender()
    except BlenderNotFound as exc:
        raise SystemExit(f"meshkit: {exc}")

    provenance = importer_provenance()
    if not provenance["matches_pinned"] and not args.allow_importer_drift:
        raise SystemExit(
            f"meshkit: the vendored importer no longer matches kinema {COMMIT[:12]} "
            f"(sha256 {provenance['sha256'][:12]} != {SHA256[:12]}). Re-vendor it, or pass "
            "--allow-importer-drift to convert with the modified copy knowingly.")

    out_dir = args.out.resolve() if args.out else None
    targets = plan(sources, root, out_dir)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = (args.report or root / "out" / "meshkit" / f"convert-{stamp}.json").resolve()

    print(f"{len(targets)} mesh(es); {blender.describe()}")
    print("writing next to each source" if out_dir is None else f"writing under {out_dir}")
    report = convert(
        targets, blender,
        report_path=report_path,
        batch_size=args.batch_size,
        force=args.force,
        dry_run=args.dry_run,
        tolerance=Tolerance(position=args.tolerance_position, area=args.tolerance_area,
                            normals=args.tolerance_normals),
    )
    summary = ", ".join(f"{count} {status}" for status, count in sorted(report["summary"].items()))
    print(f"{summary}\nreport: {report_path}")
    return 1 if report["summary"].get("failed") else 0


# ------------------------------------------------------------------------- main

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meshkit",
        description="Convert and verify robot description meshes in the kinema catalog.")
    parser.add_argument("--version", action="version", version=f"meshkit {__version__}")
    parser.add_argument("--root", type=Path, help="catalog checkout (default: found from cwd)")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help=f"check Blender ({ENV_VAR}), importer and glTF support")
    doctor.set_defaults(func=cmd_doctor)

    scan_p = sub.add_parser("scan", help="classify .dae files as visual / collision")
    scan_p.add_argument("--fork", action="append", help="limit to a submodule (repeatable)")
    scan_p.add_argument("--list", choices=["visual", "collision", "unreferenced"])
    scan_p.add_argument("--unresolved", action="store_true",
                        help="also list references that could not be resolved")
    scan_p.add_argument("--json", action="store_true")
    scan_p.set_defaults(func=cmd_scan)

    conv = sub.add_parser("convert", help="convert visual .dae meshes to verified .glb")
    conv.add_argument("--fork", action="append", help="convert a submodule's visual meshes")
    conv.add_argument("--file", action="append", help="convert specific .dae files")
    conv.add_argument("--out", type=Path, help="write under this directory instead of in place")
    conv.add_argument("--report", type=Path, help="report path (default: out/meshkit/)")
    conv.add_argument("--batch-size", type=int, default=25)
    conv.add_argument("--force", action="store_true", help="redo meshes whose .glb exists")
    conv.add_argument("--dry-run", action="store_true")
    conv.add_argument("--tolerance-position", type=float, default=Tolerance().position)
    conv.add_argument("--tolerance-area", type=float, default=Tolerance().area)
    conv.add_argument("--tolerance-normals", type=float, default=Tolerance().normals,
                      help="degrees, per percentile of normal deviation")
    conv.add_argument("--allow-importer-drift", action="store_true")
    conv.set_defaults(func=cmd_convert)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
