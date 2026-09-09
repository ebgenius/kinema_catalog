# kinema_catalog

Companion catalog to [kinema](https://github.com/ebgenius/kinema), the Blender add-on for
real robotic animations in Blender.

This repo collects **forks of popular public ROS 2 robot description packages** (URDF/Xacro,
meshes, configs) as submodules, so they can be worked on with three goals:

1. **Improve the descriptions** — fix joint limits, inertias, collision geometry, naming.
2. **Modernise the meshes** — migrate away from `.dae` (COLLADA) toward better long-term
   formats, with cleaner materials and sane scale/orientation.
3. **Guarantee kinema compatibility** — every description here should import into Blender
   through kinema and animate correctly.

Each entry under `src/` is a fork owned by [@ebgenius](https://github.com/ebgenius), tracked
as a git submodule pinned to a commit, so upstream history stays intact and changes can be
proposed back upstream.

## Catalog

### Arms / manipulators

| Package | Upstream | Branch | Robots |
| --- | --- | --- | --- |
| `franka_description` | [frankarobotics/franka_description](https://github.com/frankarobotics/franka_description) | `main` | FR3, Panda |
| `Universal_Robots_ROS2_Description` | [UniversalRobots/…](https://github.com/UniversalRobots/Universal_Robots_ROS2_Description) | `rolling` | UR3/5/10/16/20/30 |
| `xarm_ros2` | [xArm-Developer/xarm_ros2](https://github.com/xArm-Developer/xarm_ros2) | `humble` | UFACTORY xArm 5/6/7, Lite 6 |
| `open_manipulator` | [ROBOTIS-GIT/open_manipulator](https://github.com/ROBOTIS-GIT/open_manipulator) | `main` | OpenMANIPULATOR-X / -Y |
| `ros2_kortex` | [Kinovarobotics/ros2_kortex](https://github.com/Kinovarobotics/ros2_kortex) | `main` | Kinova Gen3 / Gen3 lite |
| `lbr_fri_ros2_stack` | [lbr-stack/lbr_fri_ros2_stack](https://github.com/lbr-stack/lbr_fri_ros2_stack) | `jazzy` | KUKA LBR iiwa 7/14, Med 7/14 |
| `abb_ros2` | [PickNikRobotics/abb_ros2](https://github.com/PickNikRobotics/abb_ros2) | `rolling` | ABB IRB series |
| `interbotix_ros_manipulators` | [Interbotix/…](https://github.com/Interbotix/interbotix_ros_manipulators) | `main` | ViperX, WidowX, PincherX |
| `SO-ARM100` | [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) | `main` | SO-ARM100 / SO-101 |
| `moveit_resources` | [moveit/moveit_resources](https://github.com/moveit/moveit_resources) | `ros2` | Panda, Fanuc, dual-arm test models |

### Mobile bases

| Package | Upstream | Branch | Robots |
| --- | --- | --- | --- |
| `turtlebot3` | [ROBOTIS-GIT/turtlebot3](https://github.com/ROBOTIS-GIT/turtlebot3) | `main` | Burger, Waffle, Waffle Pi |
| `turtlebot4` | [turtlebot/turtlebot4](https://github.com/turtlebot/turtlebot4) | `jazzy` | TurtleBot 4 / 4 Lite |
| `clearpath_common` | [clearpathrobotics/clearpath_common](https://github.com/clearpathrobotics/clearpath_common) | `jazzy` | Husky, Jackal, Ridgeback, Warthog, Dingo (current ROS 2 fleet) |
| `husky` | [husky/husky](https://github.com/husky/husky) | `humble-devel` | Clearpath Husky (standalone, legacy) |
| `jackal` | [jackal/jackal](https://github.com/jackal/jackal) | `foxy-devel` | Clearpath Jackal (standalone, legacy) |
| `linorobot2` | [linorobot/linorobot2](https://github.com/linorobot/linorobot2) | `jazzy` | 2WD, 4WD, Mecanum |

### Legged

| Package | Upstream | Branch | Robots |
| --- | --- | --- | --- |
| `unitree_ros` | [unitreerobotics/unitree_ros](https://github.com/unitreerobotics/unitree_ros) | `master` | Go1/Go2, A1, B1/B2, H1, G1, Z1 |
| `anymal_b_simple_description` | [ANYbotics/…](https://github.com/ANYbotics/anymal_b_simple_description) | `master` | ANYmal B |
| `anymal_c_simple_description` | [ANYbotics/…](https://github.com/ANYbotics/anymal_c_simple_description) | `master` | ANYmal C |
| `spot_description` | [rai-opensource/spot_description](https://github.com/rai-opensource/spot_description) | `main` | Boston Dynamics Spot |

## Layout

- `src/` — one submodule per robot description fork.
- `docker/` — local, untracked plumbing for launching Docker containers (Windows/Linux) to
  quickly check descriptions in RViz/Gazebo before and after changes. Gitignored for now.

## Working with the submodules

```sh
# first checkout
git submodule update --init --recursive

# pull the latest upstream-tracked branch of every fork
git submodule update --remote

# work on one fork
cd src/<package>
git checkout -b my-improvement
# ... edit, commit, push to the ebgenius fork ...
```

Each submodule records the fork's default branch in `.gitmodules`, so `--remote` follows the
right branch (several ROS repos use `ros2`, `humble`, or `main` rather than `master`).

Upstream licenses apply to each fork; see the `LICENSE` file inside each package.
