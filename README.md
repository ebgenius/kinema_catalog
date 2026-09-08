# kinema_catalog

Companion catalog to [kinema](https://github.com/ebgenius/kinema), the Blender add-on for
real robotic animations in Blender.

This repo collects forks of popular public ROS 2 robot description packages (URDF/Xacro,
meshes, configs), with the goal of:

- Improving and cleaning up the descriptions themselves.
- Migrating meshes from `.dae` to better long-term formats.
- Making sure every description is compatible with `kinema`.

## Layout

- `src/` — one submodule per robot description fork (e.g. `franka_description`).
- `docker/` — local, untracked plumbing for launching Docker containers (Windows/Linux) to
  quickly check descriptions in RViz/Gazebo before and after changes. Gitignored for now.

## Getting the submodules

```sh
git submodule update --init --recursive
```
