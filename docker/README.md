# docker/ — the viewer container

Plumbing behind `./kinema_catalog.sh`. You normally don't run anything in here
directly; the launcher builds and drives it for you.

| File | Purpose |
| --- | --- |
| `Dockerfile` | Thin layer on `osrf/ros:<distro>-desktop-full` adding xacro, robot/joint state publishers, RViz and `ros_gz`. |
| `entrypoint.sh` | Container-side orchestrator: builds the package index, flattens the description, launches RViz or Gazebo. |
| `catalog_rows.py` | Reads `../catalog.json` and prints one tab-separated line per entry, so neither shell script parses JSON. Standard library only; on the host it needs `python3`. |
| `rviz/robot.rviz` | RViz layout (RobotModel + grid + TF). `__FIXED_FRAME__` is substituted per robot at launch. |

## How a description is made loadable without a colcon build

Descriptions refer to each other with `$(find some_pkg)` in xacro and
`package://some_pkg/meshes/x.dae` in URDF, both of which normally require a built
and sourced ROS workspace.

Instead, `entrypoint.sh` scans `/catalog/src` for every `package.xml` and builds a
**synthetic ament index** in `/tmp/kinema_index`: a symlink per package plus a
marker file in `resource_index/packages/`. Prepending that to `AMENT_PREFIX_PATH`
makes every description in the catalog resolvable instantly — no build step, no
wait. The same directory is added to `GZ_SIM_RESOURCE_PATH` so Gazebo resolves
`package://` mesh URIs too.

Consequence worth knowing: a description that depends on a package **not** in this
catalog fails at the xacro step. That is a missing dependency, not a bug in the
tooling, and the fix is to fork the repository that has it into the catalog: TurtleBot
4 needs `irobot_create_description`, which is why `create3_sim` is a submodule.

## ROS 2 / Gazebo pairings

The launcher defaults to the newest LTS. Older distros are one flag away
(`-d humble`), which matters for robots whose descriptions haven't been updated.

| ROS 2 distro | Gazebo | Notes |
| --- | --- | --- |
| `lyrical` | Jetty | LTS, May 2026, Ubuntu 26.04 — **default** |
| `rolling` | Jetty | development branch |
| `kilted` | Ionic | 2025 |
| `jazzy` | Harmonic | LTS, 2024 |
| `humble` | Fortress | LTS, 2022 — best for older descriptions |
| `iron` | Fortress | EOL |

Each distro gets its own image tag (`kinema-catalog:humble`, …), so switching
distros never rebuilds the one you were using.

## Adding a robot

The catalog is described in [`catalog/`](../catalog/), one YAML file per family. Add
an entry to the family's file (or start a new `catalog/<family>.yaml`), then rebuild
`catalog.json` and check the catalog:

```sh
uv run --project tools/meshkit meshkit index           # writes catalog.json, then reports any problem
uv run --project tools/meshkit meshkit index --check   # writes nothing; fails if catalog.json is stale
```

See [`catalog/README.md`](../catalog/README.md) for the fields. Then check that it
resolves:

```sh
./kinema_catalog.sh <id> --viewer none --export
```
