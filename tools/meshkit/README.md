# meshkit

Convert the catalog's COLLADA (`.dae`) visual meshes to glTF binary (`.glb`), through
the Blender installed on your machine, and refuse to write any file that doesn't
measure the same as its source.

It converts through **kinema's own COLLADA importer**, so a GLB made here is the robot
kinema shows. Every GLB is checked three ways before it leaves staging.

```
uv run meshkit doctor                          # find Blender, check the importer
uv run meshkit scan                            # which .dae files are visual meshes
uv run meshkit convert --fork franka_description
```

Run these from `tools/meshkit`. `uv` looks for the project in the current directory
and the ones above it, never below, so from the catalog root it finds no `meshkit` and
fails with `program not found`. From anywhere else in the checkout, name the project:

```
uv run --project tools/meshkit meshkit doctor  # from the catalog root
```

`uv` creates the environment on first use. The catalog itself is found by walking up
from the current directory, or given with `--root`.

## Blender

meshkit needs **Blender 5.2 or newer**, the same minimum as kinema. It doesn't ship a
`bpy` wheel. It runs your installed Blender headless
(`--background --factory-startup`), and looks for it in this order:

1. **`KINEMA_BLENDER`**, the path to the executable. When it's set, meshkit uses it
   and nothing else: if it's wrong, you get an error, not a silent fallback to some
   other Blender.
2. `blender` on `PATH`.
3. A [Blender Launcher](https://github.com/Victor-IX/Blender-Launcher-V2) library at
   `~/blender/blender_releases/{stable,lts}/*/`.
4. The usual system install locations.

```powershell
$env:KINEMA_BLENDER = "C:\path\to\blender.exe"   # PowerShell
```
```bash
export KINEMA_BLENDER=/path/to/blender           # bash
```

`meshkit doctor` shows which Blender it found and how. Blender 5 has no built-in
COLLADA importer any more. The job loads pycollada from meshkit's own environment
(pinned by `uv.lock`), so it doesn't matter whether kinema is installed in that
Blender.

## scan

A mesh's role comes from where it's **referenced**, not where it sits on disk. Only a
third of the catalog's `.dae` files live under a `visual/` directory. Two passes:

- **Static:** `<visual>`/`<collision>` blocks in URDF and xacro, plus mesh paths in
  YAML (Universal Robots). xacro variables become wildcards. A reference that is
  nothing but variables is reported as unresolved and never allowed to claim files.
- **Rendered:** every robot in `docker/robots.tsv` is evaluated with xacrodoc, the
  engine kinema uses, and gives exact references.

```
uv run meshkit scan                       # table per fork
uv run meshkit scan --unresolved          # plus every reference it could not pin down
uv run meshkit scan --fork abb_ros2 --list visual
uv run meshkit scan --json
```

Unresolved references are mostly upstream problems worth fixing in the fork: a mesh
that doesn't exist, a package the catalog doesn't carry, or a checked-in URDF with
absolute paths from someone's workspace.

## convert

```
uv run meshkit convert --fork franka_description            # next to each .dae
uv run meshkit convert --fork franka_description --out ../../out/try   # a mirror, for review
uv run meshkit convert --file path/to/one.dae --force
```

Each `.glb` is written next to its `.dae` in the fork. The `.dae` is never modified or
deleted, and existing `.glb` files are skipped unless you pass `--force`. Pointing the
descriptions at the new files is a separate step, reviewed as its own PR in each fork.
A JSON report (default `out/meshkit/convert-<time>.json`) records the Blender version,
the importer, every measurement and every problem. Blender's log for each batch sits
next to it.

### The gate

A GLB is promoted out of staging only if all three checks pass:

| check | compares | catches |
|---|---|---|
| round trip | kinema's import of the `.dae` against Blender's re-import of the `.glb`: triangles (exact), area, centroid, bounds | lost node transforms, units, axis rotations, dropped primitives |
| trimesh | the `.glb` read by trimesh, no Blender: triangles, area | an exporter bug that Blender's own importer would mirror |
| shading | the raw `.dae` read by pycollada against the `.glb` read by trimesh: the spread of angles between each corner normal and its face | normals lost or averaged on the way through |

The shading check exists because the first two passed while kinema's importer was
averaging away every file's normals (see below). Tolerances are flags:
`--tolerance-position`, `--tolerance-area`, `--tolerance-normals`.

**Axes:** glTF is Y-up by specification, so the GLB stores Y-up. Blender's glTF
importer converts it back, and the GLB lands in kinema exactly where the `.dae` did.

## The vendored importer

`src/meshkit/blender_side/kinema_dae.py` is kinema's `src/kinema/io/dae.py` at the
commit pinned in `_vendor.py`, plus the patches in `patches/`. `convert` refuses to run
if the file differs from pinned-plus-patches (`--allow-importer-drift` overrides).

- **`0001-dae-keep-custom-normals.patch`**: kinema set each mesh's custom normals and
  *then* marked its faces smooth. That merges Blender's smoothing fans, and the
  authored normals get averaged across every hard edge. That's the dark smearing at
  panel seams and edges. The patch swaps the two steps. It applies to kinema as is,
  and belongs upstream. Once kinema merges it, re-vendor from that commit and delete
  the patch.

## Tests

```
uv run pytest
```

The `blender`-marked tests convert a generated mesh through a real Blender. They're
skipped when no Blender 5.2+ can be found.
