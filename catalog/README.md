# catalog/: the index, as written by hand

One YAML file per **family**: a maker's range, which is usually one fork (`franka`,
`universal_robots`, `unitree`). `meshkit index` builds `../catalog.json` from these
files, and that file is what everything reads: the launcher, meshkit, and Kinema. Edit
the YAML, never `catalog.json`.

```yaml
family: universal_robots          # must match the file name
maker: Universal Robots
entries:
  - id: ur5e                      # unique across the catalog; the launcher's argument
    name: Universal Robots UR5e
    category: arm                 # arm | mobile | legged
    submodule: Universal_Robots_ROS2_Description   # directory under src/
    entry: src/Universal_Robots_ROS2_Description/urdf/ur.urdf.xacro
    args:                         # xacro arguments; quote anything YAML reads as a number
      ur_type: ur5e
      name: ur5e
    licence: BSD-3-Clause         # SPDX; LicenseRef-* for terms SPDX doesn't list
```

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Lowercase letters, digits and `_`, starting with a letter. Unique across every family. |
| `name` | yes | Human-readable name. |
| `category` | yes | `arm`, `mobile` or `legged`; the launcher groups by it. |
| `submodule` | yes | The fork under `src/` that holds the description. The launcher clones it on demand. |
| `entry` | yes | The file to open, relative to the repository root, ending in `.xacro` or `.urdf`; the format follows from the suffix. Usually inside the submodule; otherwise a wrapper kept in this repository under `descriptions/` (see the Clearpath platforms). |
| `licence` | yes | The description's licence, as an SPDX expression. |
| `licence_note` | no | What the licence restricts, where it restricts anything (the UR20's and UR30's meshes). |
| `args` | no | xacro arguments, passed as `name:=value`. Values are strings, without whitespace. |
| `mesh_base` | no | For a URDF that names meshes by relative path: the directory they resolve against, relative to the repository root. |
| `kind` | no | `robot` (the default), `end_effector`, `hand`, `base` or `scene`. |
| `tags` | no | A list of strings. |

In `catalog.json` every entry is complete: `family`, `maker` and `format` are filled
in, and optional fields have their defaults (`kind: robot`, `tags: []`, `args: {}`,
`mesh_base: null`). [`../catalog.schema.json`](../catalog.schema.json) describes the
file.

## Rebuilding and checking

```sh
uv run --project tools/meshkit meshkit index           # rebuild catalog.json, then report problems
uv run --project tools/meshkit meshkit index --check   # fail if catalog.json is stale, or anything below
```

The check, which the tests also run, wants:

- `catalog.json` to match these files;
- an entry for every submodule in `.gitmodules`;
- every entry's submodule to be in `.gitmodules`, and its paths inside that
  submodule;
- every `entry` and `mesh_base` to exist. For a submodule that isn't cloned, only
  paths outside `src/` can be checked.

`./kinema_catalog.sh --check` then flattens every entry in a ROS container.
