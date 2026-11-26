# meshkit

Convert the catalog's visual meshes (`.dae`, `.stl` and `.obj`) to glTF binary (`.glb`),
through the Blender installed on your machine, and refuse to write any file that doesn't
measure the same as its source.

A `.dae` converts through **kinema's own COLLADA importer**, so a GLB made here is the
robot kinema shows, normals and colours as the file has them (an instance whose
material fails to bind comes in without it; see *Lost placement* below). An `.stl` or `.obj` is
smoothed by angle on the way, the rule Kinema applies on import. Every GLB is checked
several ways before it leaves staging.

It also builds the catalog's index, `catalog.json`, from `catalog/*.yaml` (see
[`catalog/README.md`](../../catalog/README.md)).

```
uv run meshkit doctor                          # find Blender, check the importer
uv run meshkit index                           # rebuild catalog.json from catalog/*.yaml
uv run meshkit scan                            # which .dae files are visual meshes
uv run meshkit upstream                        # how far each fork is behind upstream
uv run meshkit audit                           # measure and score every robot, ours and candidates
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

## upstream

How far each fork is behind the repository it was forked from, on the branch
`.gitmodules` says the catalog tracks. That is not always upstream's default branch:
xArm's is `humble`, Clearpath's `jazzy`. It reports, and never syncs, merges or
pushes.

```
uv run meshkit upstream                         # Markdown on stdout
uv run meshkit upstream --fork unitree_ros      # one fork (repeatable)
uv run meshkit upstream --previous last.md --markdown report.md --json report.json
```

Per fork it compares three commits through the GitHub API: the pin this repository
records, the fork's branch, and upstream's branch. From those it suggests:

| Action | When |
| --- | --- |
| sync | the fork's branch is behind and has no commits of its own: `gh repo sync` |
| bump | the pin is behind: update the submodule in a pull request, then `--check` |
| reconvert | upstream changed meshes |
| review | the fork has its own commits and is behind, so it needs a merge; the pin has commits the fork's branch no longer has, which a bump would drop; upstream added robot files (`.urdf`, `.urdf.xacro`); or upstream was archived, renamed or moved, or changed its licence, or names a licence the catalog's entries do not; or either side lacks the branch, or the two share no history |
| fork | a repository new in one of the lists below: a candidate for the next audit |

Changed files are sorted into **description** (URDF, xacro, SRDF, SDF),
**meshes** and **config** (YAML under `config/`, or named for limits). GitHub lists
at most 300 files per comparison, and the report says when it has hit that limit.
The Markdown names up to 25 files per kind and 50 new candidates per list, counting
the rest; the JSON has them all. An issue holds at most 65,536 characters, so a
report that would not fit drops the file names, then the candidates' names. The
state is never cut.

The lists are awesome-robot-descriptions, robot_descriptions.py's repositories, and
fiveages-sim/robot_descriptions (its README's robots, and its submodules). The report
names what each gained since the previous report and that the catalog doesn't carry.
The first run has nothing to compare with, so it records a baseline.

The Markdown ends with the run's state in an HTML comment. Passing that report back as
`--previous` is all a later run needs, and is how the weekly workflow works
(`.github/workflows/upstream.yml`): it reads the open issue labelled `upstream-report`,
runs this, and writes the issue back. The JSON report carries the same state; the
workflow keeps it for 90 days as the run's `upstream-report` artifact, and passes the
run's address as `--json-url`, so the issue links to it wherever it leaves names out.

A token comes from `GITHUB_TOKEN` or `GH_TOKEN`, else from `gh auth token`.

## audit

Every robot the catalog has, and every robot it could have, measured the same way and
scored out of 100: what step 5 forks from. It writes `audit/audit.md` and
`audit/audit.json` at the catalog root, which are committed.

```
uv run meshkit audit                            # the forks and every candidate
uv run meshkit audit --forks-only               # the catalog's own entries, no cloning
uv run meshkit audit --only unitreerobotics/unitree_mujoco
uv run meshkit audit --no-fetch                 # measure the clones as they are
uv run meshkit audit --repo kuka-ros/kuka_robot_descriptions --markdown k.md --json k.json
```

**`--repo`** scores a repository the lists don't name, before choosing it as a source:
an `owner/name` or a GitHub URL, repeatable. It is measured like any candidate, its
source shown as `--repo`. One already in the audit as a whole repository (a fork, by its
own name or its upstream's, or a candidate a list names) is marked, not added twice. A
repository the lists name only by folder (fiveages' README rows) gets a whole-repository
row beside those folder rows. `--repo` audits only what it and `--only` name, so it needs
`--markdown` and `--json`: a run written over `audit/audit.md` would drop every other
row. What it doesn't measure still supplies packages, as with `--only`. A name GitHub
doesn't know is refused. A candidate list that can't be read stops a full audit, but
not a `--repo` one: the report names the list, whose candidates then supply no packages.

**What is audited.** Every entry in `catalog.json`, rendered with its own arguments,
and every repository the upstream report's lists name that the catalog doesn't carry
(fiveages' README rows are folders of its one repository). Candidates are shallow-cloned
into a cache outside the repository: `~/.cache/kinema_catalog/audit` (under
`$XDG_CACHE_HOME` if set), or `--cache`. Not `%LOCALAPPDATA%`, which a packaged Windows
app has redirected to a folder of its own. The first run clones about
10 GB; later runs fetch only what changed. Git LFS files are not fetched, and are
reported as such.

**A robot** is a `.urdf`, a `.xacro` whose `<robot>` does more than define macros, or
an MJCF `.xml` with a body of its own (a `scene.xml` that only includes the robot isn't
a second one). A candidate is one row per robot file, evaluated with its default
arguments. The catalog is one row per entry, evaluated with the entry's own arguments,
so two entries rendering one xacro differently are two rows. xacro is evaluated with
xacrodoc, as Kinema does, using the ROS packages of every repository audited. With
`--only`, that is the repositories named, every fork, and every candidate clone
already in the cache: one not yet cloned is not fetched for a narrowed run, so after
a full run the two resolve alike, and before one they may not. Any `--only` name that
matches nothing is refused before anything is written. An MJCF's `<default>` classes are applied, and an
include it lacks is an error. SDF is counted, not measured.

| Part | Points | Full marks when |
| --- | --: | --- |
| licence | 15 | a licence is named (the catalog's for an entry; for a candidate GitHub's, or where GitHub names none, the `<license>` tags of the robot's `package.xml`, joined with AND, each name whole and at most ten, then a count of the rest) and a licence text is beside the robot or above it in its repository: `LICENSE`, `LICENCE` or `COPYING` (also `LICENSE-MIT` and the like), or a REUSE `LICENSES/` folder with a file in it; half for one of the two. The text's presence is checked, not what it says |
| alive | 10 | upstream committed to in the last year; half within three; none when archived |
| flattens | 20 | the xacro evaluates, or the MJCF parses, and every visual mesh exists and can be read (one left in Git LFS cannot). Without this, the parts below score nothing |
| limits | 15 | revolute and prismatic joints have position and velocity limits (MJCF: position only; continuous joints need none) |
| inertia | 10 | every link with geometry has a mass (MJCF: every body with geometry or a joint has an inertial, or geoms to derive one from; a bare frame is not asked) |
| look | 20 | half for visual meshes with authored normals, half for materials: a mesh's own count whole, a whole-part colour in the description half |
| weight | 10 | visual meshes under 200,000 triangles and 50 MB; none from 2,000,000 or 500 MB. Triangles are counted as drawn, once per visual that uses a mesh; megabytes as downloaded, once per file |

The weights are `WEIGHTS` in `audit.py`. Meshes are read from their own structure, not
loaded, and streamed rather than held whole: STL has no normals or materials, a DAE's
polygons count one triangle each, and a `.gltf` weighs what its buffers do too (a
buffer several meshes share, once).

The audit resets, replaces or deletes only what it made, and marks what it makes:
`.git/meshkit-audit` in a clone, `meshkit-audit` in the staging folder a clone is made
in before it is moved into place. Anything unmarked at a clone's place is refused and
left as it is, a clone of the same repository included, since it may be someone's
checkout with changes in it; `--no-fetch` measures such a clone without touching it.
A run removes its own staging folder however it fails. One is left only by a run that
was killed, and is cleared once its mark is older than the clone time limit (30
minutes) plus ten: a younger one may be another audit's, sharing the cache, still
cloning. Two audits that clone the same repository at once both succeed; the first to
finish puts its clone in place, and the other uses it.

**Not measured:** whether Kinema imports the robot, and whether two sources of the same
robot have the same kinematics. Those are checked by hand in step 5, for the robots the
audit puts forward.

Each repository is measured in a subprocess with a time limit (`--timeout`, default 20
minutes), so one that hangs xacro or holds a pathological mesh costs only its own rows.

## convert

```
uv run meshkit convert --fork franka_description            # next to each .dae
uv run meshkit convert --fork franka_description --out ../../out/try   # a mirror, for review
uv run meshkit convert --file path/to/one.dae --force
uv run meshkit convert --file path/to/link.stl --smooth-angle 20
```

Each `.glb` is written next to its source mesh in the fork, or with `--out`, at the same
place under that mirror. The source is never modified or
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

### STL and OBJ

These carry no shading worth keeping: an STL has one normal per face and no material,
and an OBJ has whatever its exporter wrote. So instead of being copied, they are
smoothed on the way:

1. **Imported as the numbers say**, in metres, axes untouched (Y forward, Z up), because
   ROS reads both formats raw in the link's frame. The OBJ importer's default would
   rotate every mesh from Y-up.
2. **Welded:** corners at exactly the same position are joined, so faces share edges.
   Not *nearly* the same: KUKA's KR 16 R2010-2 has 0.1 nm edges that a 1 nm weld
   collapsed. (Blender 5.2's STL importer already shares identical corners.) A
   face on the same corners as an earlier one in its object, in any winding or
   starting corner, is dropped whole, as the `.dae` path drops it; this is done
   before the weld, which would otherwise settle such a pair itself and keep the
   later face. Blender alone is not consistent here: its STL importer drops them,
   its OBJ importer keeps them. An OBJ's quads and larger polygons are then split into triangles, so the
   smoothing works on the faces the GLB holds, and a triangle on the same corners
   as an earlier one is dropped too, such as one the file also writes on its own.
   Always the first in the file stays, with its material. The report counts what
   went in triangles (`doubled_faces`): a doubled quad is two.
3. **Smoothed by angle:** Blender's Shade Smooth by Angle at 30 degrees
   (`--smooth-angle`), so faces meeting at less than that shade as one surface and
   sharper edges stay sharp. Geometry is unchanged; only the normals are new. An OBJ's
   own normals (`vn`) are cleared first, with the sharp edges its importer marks from
   them, and the report says so (`dropped_normals`): otherwise they outrank the
   smoothing, and a faceted OBJ leaves faceted. The angle alone decides.
4. **A material:** an OBJ keeps its own. An STL, having none, gets one named
   `meshkit_neutral` (mid-grey, roughness 0.5), so it can be found and replaced. It is
   always a new material: an OBJ's own material of that name stays as it is, and the
   new one takes Blender's next free suffix (`meshkit_neutral.001`, say).

Two sources that would write the same GLB, a `part.dae` beside a `part.stl`, are both
refused, and the report names the other. Otherwise the second would replace the first.

An OBJ face that names one vertex twice is repaired by Blender's importer before
anything else. Where its loops share one corner and meet nowhere else
(`f 1 2 3 1 4 5`, two triangles), the import check reads it the same way. Otherwise
Blender rebuilds the face with its own constrained triangulation. A loop inside
another becomes a hole, crossing loops can come out as no face at all, and a corner
lying on another loop's edge splits that edge. meshkit's reader does not reproduce
that, so the mesh fails and the report says why, rather than being checked against a
guess. Loops that share two corners or more are refused with them. So does a face naming a vertex the file does not have. The report names the
reader that failed: meshkit's own for an OBJ, trimesh for an STL.

The gate is the same except where the source's normals were the reference:

| check | compares | catches |
|---|---|---|
| round trip, trimesh | as for `.dae` | as for `.dae` |
| import | the raw file, read without Blender (an STL by trimesh, an OBJ object by object by meshkit's own reader) and welded the same way, against Blender's import: triangles (exact), area, centroid, bounds | a rotated or rescaled import, triangles lost in the weld |
| shading | the `.glb`'s corner normals against what smoothing by angle makes of its own triangles, rebuilt without Blender: the 99.9th percentile must be within `--tolerance-normals` | normals averaged across sharp edges, and smoothing lost |

Smoothing by angle is a rule, so the shading check runs it again, from the GLB read by
trimesh. An edge is sharp where its faces meet at more than the angle, or where it is
not shared by exactly two faces wound alike. At each vertex the faces joined by the
other edges form a fan, and each corner's normal is the fan's face normals weighted by
their angles at the vertex, which is Blender's rule. Each corner is measured against
that. Normals averaged across a sharp edge fail, and so do flat normals wherever
smoothing would have changed them: on a curved surface. On a flat one the two are the
same, so there is nothing to lose there and nothing to see. A cone's tip
passes: its normal points up the axis, 84 degrees from every face, which is what the
rule gives it.

Two allowances, both for float32. An edge within 0.01 degrees of the angle may go
either way: a corner whose fan turns on such edges must match them all smooth or all
sharp, and one that matches neither, perhaps a mix, is not checked. And corners beside a face whose normal float32 rounding leaves uncertain by
more than 5 degrees are not checked: next to such slivers, Blender's own choice of
sharp edges is noise, down to marking sharp an edge between coplanar faces. The report
counts them (`smoothing.unchecked`). It is 1.9% of corners across G1's 49 links and the
KR 16's 7, mostly the KR 16's sub-micrometre triangles; under half checked fails the
mesh. On those 56 meshes the 99.9th percentile is at most 0.33 degrees.

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
