# meshkit

Convert the catalog's COLLADA (`.dae`) visual meshes to glTF binary (`.glb`), through
the Blender installed on your machine, and refuse to write any file that doesn't
measure the same as its source.

It converts through **kinema's own COLLADA importer**, so a GLB made here is the robot
kinema shows. Every GLB is checked three ways before it leaves staging.

It also builds the catalog's index, `catalog.json`, from `catalog/*.yaml` (see
[`catalog/README.md`](../../catalog/README.md)).

```
uv run meshkit doctor                          # find Blender, check the importer
uv run meshkit index                           # rebuild catalog.json from catalog/*.yaml
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
- **Rendered:** every entry in `catalog.json` is evaluated with xacrodoc, the
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
next to it. If Blender is still on a batch after an hour, it is stopped, and the meshes
it hadn't finished are reported as failed.

### The gate

A GLB is promoted out of staging only if all four checks pass:

| check | compares | catches |
|---|---|---|
| round trip | kinema's import of the `.dae` against Blender's re-import of the `.glb`: triangles (exact), area, centroid, bounds | lost node transforms, units, axis rotations, dropped primitives |
| trimesh | the `.glb` read by trimesh, no Blender: triangles, area | an exporter bug that Blender's own importer would mirror |
| count | the raw `.dae` read by pycollada against kinema's import: triangles, counted as Blender keeps them | geometry the import loses or invents, which every other check inherits |
| shading | the raw `.dae` read by pycollada against the `.glb` read by trimesh: the spread of angles between each corner normal and its face | normals lost or averaged on the way through |

The shading check exists because the geometry checks passed while kinema's importer was
averaging away every file's normals (see below). Tolerances are flags:
`--tolerance-position`, `--tolerance-area`, `--tolerance-normals`.

**Axes:** glTF is Y-up by specification, so the GLB stores Y-up. Blender's glTF
importer converts it back, and the GLB lands in kinema exactly where the `.dae` did.

## The vendored importer

`src/meshkit/blender_side/kinema_dae.py` is kinema's `src/kinema/io/dae.py` at the
commit pinned in `_vendor.py`, unchanged. `convert` refuses to run if the file differs
from the pin (`--allow-importer-drift` overrides). A fix to the importer goes to kinema
first; then re-vendor from the commit that has it and update `COMMIT` and `SHA256`.

The pin is the merge of [kinema#126](https://github.com/ebgenius/kinema/pull/126),
which fixed four importer bugs that meshkit's checks found. Until then meshkit carried
them as patches:

- **Normals averaged away.** kinema set each mesh's custom normals and *then* marked
  its faces smooth. That merges Blender's smoothing fans, and the authored normals got
  averaged across every hard edge: the dark smearing at panel seams and edges. The
  geometry checks all passed, which is why the shading check exists.
- **Lost placement.** When a material fails to bind (a texture whose image the file
  never declares, common in CAD exports), pycollada drops that `<instance_geometry>`
  and the node placing it. If other instances survived, kinema imported those and
  silently lost the rest; if none did, its fallback imported the library geometry
  alone, at the origin, once however many nodes instanced it. No check could see
  either, because they all start from the import. kinema now reads the document again
  without bindings and imports each lost instance where its node puts it, without
  material.
- **`<lines>` as triangles.** Every primitive's indices were read three at a time, so
  franka's `link7.dae`, which has three edges, gained two triangles. The count check
  caught it.
- **Shifted corners.** `mesh.validate()` removes a face that repeats a vertex, and all
  but one of the faces on the same three vertices. CAD exports carry both. kinema read
  the normals and UVs by position after that, so each face after a removed one took the
  next face's. Of the checks, only shading can see it. The count and shading checks
  leave out the same faces Blender does.

## Tests

```
uv run pytest
```

The `blender`-marked tests convert a generated mesh through a real Blender. They're
skipped when no Blender 5.2+ can be found.
