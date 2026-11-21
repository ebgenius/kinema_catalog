# Robot description audit

Written by `meshkit audit` on 2026-11-21 01:20 UTC. Every robot in the catalog's forks, and every robot in the repositories the upstream report's lists name, measured the same way and scored out of 100. [`audit.json`](audit.json) has every measurement.

- **The catalog:** 128 entries in 23 forks.
- **Candidates:** 3482 robots in 154 of 164 repositories or folders; 3 could not be audited (listed at the end).

## How a robot is scored

| Part | Points | Full marks when |
|---|--:|---|
| Licence | 15 | A licence is named (by GitHub, else by the robot's package.xml) and there is a licence text: a LICENSE, LICENCE or COPYING file (LICENSE-MIT and the like too) or a LICENSES/ folder with a file in it (present, not read; half for one of the two) |
| Alive | 10 | Upstream committed to in the last year (half: in three); not archived |
| Flattens | 20 | xacro evaluates (or the MJCF parses) and every visual mesh is there. Without it the parts below score nothing |
| Limits | 15 | Every moving joint has position and velocity limits (MJCF: position only) |
| Inertia | 10 | Every link with geometry has a mass (MJCF: every body with geometry or a joint) |
| Look | 20 | Half for meshes with authored normals, half for materials (a whole-part colour counts half) |
| Weight | 10 | Under 200,000 triangles and 50 MB of visual meshes, none from 2,000,000 or 500 MB (triangles as drawn, once per visual; megabytes once per file) |

Not measured: whether Kinema imports the robot, and whether its kinematics match the maker's own description. A xacro is evaluated with its default arguments, using packages from every repository audited; one that needs a package none of them carries does not flatten. A DAE's polygons count as one triangle each.

## The catalog's entries

| Entry | Fork | Score | Licence | Limits | Inertia | Normals | Materials | Triangles | MB |
|---|---|--:|---|--:|--:|--:|--:|--:|--:|
| irb1200 | abb_ros2 | 100 | Apache-2.0 | 100% | 100% | 100% | 100% | 92,893 | 7.13 |
| irb4600 | abb_ros2 | 85 | Apache-2.0 | 100% | 0% | 100% | 50% | 38,491 | 2.65 |
| anymal_b | anymal_b_simple_description | 86 | BSD-3-Clause | 100% | 76% | 100% | 100% | 481,370 | 21.24 |
| anymal_c | anymal_c_simple_description | 90 | BSD-3-Clause | 100% | 98% | 100% | 98% | 58,320 | 5.07 |
| dingo_o | clearpath_common | 99 | BSD-3-Clause | 100% | 100% | 100% | 100% | 322,314 | 20.63 |
| dingo_o150 | clearpath_common | 99 | BSD-3-Clause | 100% | 100% | 100% | 100% | 322,314 | 20.63 |
| husky | clearpath_common | 97 | BSD-3-Clause | 100% | 67% | 100% | 100% | 123,884 | 4.94 |
| dingo_d | clearpath_common | 90 | BSD-3-Clause | 100% | 100% | 33% | 62% | 8,428 | 0.47 |
| dingo_d150 | clearpath_common | 90 | BSD-3-Clause | 100% | 100% | 33% | 62% | 8,428 | 0.47 |
| jackal | clearpath_common | 83 | BSD-3-Clause | 100% | 83% | 0% | 50% | 11,680 | 0.18 |
| warthog | clearpath_common | 81 | BSD-3-Clause | 100% | 58% | 0% | 50% | 58,712 | 0.91 |
| husky_a300 | clearpath_common | 80 | BSD-3-Clause | 100% | 38% | 20% | 60% | 592,090 | 15.77 |
| ridgeback | clearpath_common | 79 | BSD-3-Clause | 100% | 44% | 0% | 50% | 4,228 | 0.12 |
| create3 | create3_sim | 90 | BSD-3-Clause | 100% | 100% | 100% | 70% | 11,828 | 1.58 |
| a0509 | doosan-robot2 | 100 | Apache-2.0 | 100% | 100% | 100% | 100% | 89,962 | 6.38 |
| a0912 | doosan-robot2 | 100 | Apache-2.0 | 100% | 100% | 100% | 100% | 92,121 | 7.43 |
| h2017 | doosan-robot2 | 100 | Apache-2.0 | 100% | 100% | 100% | 100% | 89,394 | 6.41 |
| h2515 | doosan-robot2 | 100 | Apache-2.0 | 100% | 100% | 100% | 100% | 89,542 | 6.47 |
| m0609 | doosan-robot2 | 100 | Apache-2.0 | 100% | 100% | 100% | 100% | 59,380 | 4.15 |
| m0617 | doosan-robot2 | 100 | Apache-2.0 | 100% | 100% | 100% | 100% | 57,412 | 4.01 |
| m1013 | doosan-robot2 | 100 | Apache-2.0 | 100% | 100% | 100% | 100% | 102,928 | 7.47 |
| m1509 | doosan-robot2 | 100 | Apache-2.0 | 100% | 100% | 100% | 100% | 58,382 | 4.12 |
| e0509 | doosan-robot2 | 95 | Apache-2.0 | 100% | 100% | 100% | 50% | 84,002 | 6.22 |
| p3020 | doosan-robot2 | 85 | Apache-2.0 | 100% | 100% | 0% | 50% | 79,070 | 3.96 |
| fer | franka_description | 100 | Apache-2.0 | 100% | 100% | 100% | 100% | 134,924 | 10.53 |
| fp3 | franka_description | 100 | Apache-2.0 | 100% | 100% | 100% | 100% | 240,624 | 27.29 |
| fr3 | franka_description | 100 | Apache-2.0 | 100% | 100% | 100% | 100% | 240,624 | 27.28 |
| px100 | interbotix_ros_manipulators | 80 | BSD-3-Clause | 100% | 100% | 0% | 50% | 7,076 | 0.33 |
| vx300s | interbotix_ros_manipulators | 80 | BSD-3-Clause | 100% | 100% | 0% | 50% | 28,664 | 1.39 |
| wx250s | interbotix_ros_manipulators | 80 | BSD-3-Clause | 100% | 100% | 0% | 50% | 11,310 | 0.54 |
| kr10_r1100_2 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 38,512 | 2.91 |
| kr10_r1100_3 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 72,518 | 5.68 |
| kr10_r900_2 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 38,838 | 2.93 |
| kr120_r2700_2 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 223,143 | 17.75 |
| kr12_r1450_3_hw | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 230,567 | 16.86 |
| kr13_r900_3 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 71,177 | 5.59 |
| kr16_r1100_3 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 108,415 | 8.31 |
| kr16_r1610_2 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 196,221 | 16.74 |
| kr20_r1810_2 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 198,183 | 16.84 |
| kr20_r1820_2_e | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 293,570 | 25.43 |
| kr20_r3100 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 169,354 | 13.6 |
| kr210_r2700_extra | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 110,970 | 8.58 |
| kr210_r3100_2 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 242,510 | 19.18 |
| kr240_r2900_2 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 277,212 | 40.39 |
| kr240_r3330 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 211,378 | 14.72 |
| kr300_r2700_2 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 242,498 | 19.24 |
| kr300_r2800_2_mt | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 298,601 | 24.18 |
| kr30_r2100 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 156,202 | 12.51 |
| kr340_r3400_2 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 214,771 | 17.66 |
| kr35_r1840_3 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 216,067 | 23.21 |
| kr35_r1840_3_hw | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 174,323 | 14.18 |
| kr360_r2830 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 201,555 | 15.63 |
| kr4_r600 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 46,921 | 3.67 |
| kr500_r2800_2 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 227,769 | 18.66 |
| kr50_r2100 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 156,202 | 12.49 |
| kr50_r2500 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 157,186 | 12.54 |
| kr600_r2830 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 207,064 | 16.03 |
| kr6_r700_2 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 121,481 | 9.23 |
| kr6_r900_2 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 38,838 | 2.93 |
| kr70_r2100 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 156,293 | 12.48 |
| kr7_r900_3 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 61,482 | 4.81 |
| kr8_r1440_2_arc_hw | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 149,177 | 11.54 |
| kr8_r2100_2_arc_hw | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 97,934 | 7.77 |
| lbr_iisy8_r930 | kuka_robot_descriptions | 90 | Apache-2.0 | 100% | 100% | 100% | 100% | 237,327 | 18.48 |
| kr560_r3100_2 | kuka_robot_descriptions | 89 | Apache-2.0 | 100% | 100% | 100% | 100% | 357,953 | 30.28 |
| kr800_r2800_2 | kuka_robot_descriptions | 89 | Apache-2.0 | 100% | 100% | 100% | 100% | 351,658 | 28.06 |
| lbr_iico12_r1260 | kuka_robot_descriptions | 89 | Apache-2.0 | 100% | 100% | 100% | 100% | 414,874 | 31.62 |
| lbr_iico7_r900 | kuka_robot_descriptions | 89 | Apache-2.0 | 100% | 100% | 100% | 100% | 450,989 | 34.97 |
| kr210_r3300_2_k | kuka_robot_descriptions | 88 | Apache-2.0 | 100% | 100% | 100% | 100% | 650,804 | 50.95 |
| kr210_r3100_ultra | kuka_robot_descriptions | 87 | Apache-2.0 | 100% | 71% | 100% | 100% | 123,671 | 9.6 |
| kr150_r3100_2 | kuka_robot_descriptions | 80 | Apache-2.0 | 100% | 100% | 0% | 100% | 264,444 | 28.27 |
| lbr_iisy11_r1300 | kuka_robot_descriptions | 75 | Apache-2.0 | 100% | 100% | 0% | 50% | 222,811 | 11.14 |
| lbr_iisy15_r930 | kuka_robot_descriptions | 75 | Apache-2.0 | 100% | 100% | 0% | 50% | 216,277 | 10.81 |
| lbr_iisy3_r760 | kuka_robot_descriptions | 75 | Apache-2.0 | 100% | 100% | 0% | 50% | 56,525 | 2.83 |
| kr210_r2700_2 | kuka_robot_descriptions | 70 | Apache-2.0 | 100% | 100% | 0% | 0% | 248,928 | 12.45 |
| kr16_r2010_2 | kuka_robot_descriptions | 59 | Apache-2.0 | 100% | 0% | 0% | 0% | 311,642 | 15.58 |
| iiwa14 | lbr_iiwa14_r820_description | 92 | Apache-2.0 | 100% | 100% | 100% | 100% | 68,224 | 9.1 |
| iiwa7 | lbr_iiwa7_r800_description | 92 | Apache-2.0 | 100% | 100% | 100% | 100% | 74,738 | 9.99 |
| med14 | lbr_med14_r820_description | 92 | Apache-2.0 | 100% | 100% | 100% | 100% | 61,781 | 8.22 |
| med7 | lbr_med7_r800_description | 92 | Apache-2.0 | 100% | 100% | 100% | 100% | 70,553 | 9.41 |
| lino_2wd | linorobot2 | 85 | Apache-2.0 | 100% | 100% | - | 50% | 0 | 0 |
| lino_4wd | linorobot2 | 85 | Apache-2.0 | 100% | 100% | - | 50% | 0 | 0 |
| lino_mecanum | linorobot2 | 85 | Apache-2.0 | 100% | 100% | - | 50% | 0 | 0 |
| omx | open_manipulator | 84 | Apache-2.0 | 100% | 88% | 0% | 50% | 81,644 | 4.08 |
| omy_3m | open_manipulator | 83 | Apache-2.0 | 100% | 88% | 0% | 50% | 367,696 | 18.39 |
| gen3 | ros2_kortex | 100 | BSD-3-Clause | 100% | 100% | 100% | 100% | 75,529 | 5.09 |
| gen3_lite | ros2_kortex | 85 | BSD-3-Clause | 100% | 100% | 0% | 50% | 187,176 | 9.36 |
| so100 | SO-ARM100 | 85 | Apache-2.0 | 100% | 100% | 0% | 50% | 60,682 | 3.04 |
| so101 | SO-ARM100 | 84 | Apache-2.0 | 100% | 100% | 0% | 50% | 398,884 | 16.13 |
| spot | spot_description | 99 | MIT | 100% | 92% | 100% | 100% | 127,509 | 21.19 |
| spot_arm | spot_description | 99 | MIT | 100% | 95% | 100% | 98% | 167,758 | 25.46 |
| tb3_waffle | turtlebot3 | 86 | Apache-2.0 | 100% | 86% | 20% | 60% | 385,320 | 19.4 |
| tb3_burger | turtlebot3 | 85 | Apache-2.0 | 100% | 100% | 0% | 50% | 154,434 | 7.72 |
| tb3_waffle_pi | turtlebot3 | 84 | Apache-2.0 | 100% | 86% | 0% | 50% | 215,486 | 10.77 |
| tb4 | turtlebot4 | 86 | Apache-2.0 | 100% | 100% | 100% | 92% | 277,861 | 21.2 |
| tb4_lite | turtlebot4 | 86 | Apache-2.0 | 100% | 100% | 100% | 81% | 90,420 | 7.97 |
| aliengo | unitree_ros | 97 | BSD-3-Clause | 100% | 97% | 100% | 69% | 87,050 | 6.15 |
| a1 | unitree_ros | 96 | BSD-3-Clause | 100% | 78% | 100% | 82% | 216,116 | 9.01 |
| b2 | unitree_ros | 96 | BSD-3-Clause | 100% | 97% | 100% | 70% | 288,093 | 51.95 |
| b2w | unitree_ros | 95 | BSD-3-Clause | 100% | 97% | 100% | 74% | 603,984 | 75.38 |
| aliengo_z1 | unitree_ros | 94 | BSD-3-Clause | 100% | 98% | 100% | 54% | 331,442 | 26.81 |
| laikago | unitree_ros | 94 | BSD-3-Clause | 100% | 78% | 100% | 60% | 44,030 | 4.99 |
| b1 | unitree_ros | 91 | BSD-3-Clause | 100% | 97% | 100% | 48% | 779,959 | 39.63 |
| go1 | unitree_ros | 90 | BSD-3-Clause | 100% | 97% | 100% | 46% | 1,061,010 | 72.21 |
| z1 | unitree_ros | 90 | BSD-3-Clause | 100% | 100% | 100% | 0% | 177,936 | 15.07 |
| go2 | unitree_ros | 25 | BSD-3-Clause | 100% | 97% | 100% | 58% | 303,088 | 13.57 |
| ur10 | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause | 100% | 100% | 100% | 100% | 116,072 | 9.04 |
| ur10e | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause | 100% | 100% | 100% | 100% | 129,621 | 10.0 |
| ur10g_1750 | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause AND LicenseRef-UR-Graphical-Documentation | 100% | 100% | 100% | 100% | 15,838 | 1.18 |
| ur12e | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause | 100% | 100% | 100% | 100% | 129,621 | 10.0 |
| ur15 | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause AND LicenseRef-UR-Graphical-Documentation | 100% | 100% | 100% | 100% | 12,534 | 2.05 |
| ur16e | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause | 100% | 100% | 100% | 100% | 129,620 | 9.89 |
| ur17g_1300 | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause AND LicenseRef-UR-Graphical-Documentation | 100% | 100% | 100% | 100% | 18,180 | 1.39 |
| ur18 | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause AND LicenseRef-UR-Graphical-Documentation | 100% | 100% | 100% | 100% | 12,470 | 2.04 |
| ur18g_950 | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause AND LicenseRef-UR-Graphical-Documentation | 100% | 100% | 100% | 100% | 18,238 | 1.38 |
| ur20 | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause AND LicenseRef-UR-Graphical-Documentation | 100% | 100% | 100% | 100% | 16,987 | 3.14 |
| ur3 | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause | 100% | 100% | 100% | 100% | 68,588 | 6.92 |
| ur30 | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause AND LicenseRef-UR-Graphical-Documentation | 100% | 100% | 100% | 100% | 17,179 | 3.22 |
| ur3e | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause | 100% | 100% | 100% | 100% | 131,817 | 10.22 |
| ur5 | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause | 100% | 100% | 100% | 100% | 95,694 | 6.66 |
| ur5e | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause | 100% | 100% | 100% | 100% | 121,789 | 9.34 |
| ur7e | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause | 100% | 100% | 100% | 100% | 121,789 | 9.34 |
| ur8long | Universal_Robots_ROS2_Description | 100 | BSD-3-Clause AND LicenseRef-UR-Graphical-Documentation | 100% | 100% | 100% | 100% | 12,534 | 2.05 |
| lite6 | xarm_ros2 | 85 | BSD-3-Clause | 100% | 100% | 0% | 50% | 55,468 | 2.77 |
| uf850 | xarm_ros2 | 85 | BSD-3-Clause | 100% | 100% | 0% | 50% | 48,262 | 2.41 |
| xarm5 | xarm_ros2 | 85 | BSD-3-Clause | 100% | 100% | 0% | 50% | 51,421 | 2.57 |
| xarm6 | xarm_ros2 | 85 | BSD-3-Clause | 100% | 100% | 0% | 50% | 51,423 | 2.57 |
| xarm7 | xarm_ros2 | 85 | BSD-3-Clause | 100% | 100% | 0% | 50% | 41,096 | 2.06 |

## The 100 best-scoring candidates

One row per ROS package: 2531 packages (or files outside any) hold the 3482 candidate robots. Each row shows the package's most complete robot (the file with the most links among those that flatten) and how many robot files the package has; its components and other variants are in the repository's details below.

| Score | Package | Robot | Links | Files | Repository | Licence | Formats | Triangles |
|--:|---|---|--:|--:|---|---|---|--:|
| 100 | freedom_description | `dexhands/freedom_description/xacro/ros2_control/hand.xacro` | 20 | 2 | [fiveages-sim/robot-descriptions-common](https://github.com/fiveages-sim/robot-descriptions-common) | Apache-2.0 | 9 GLB | 127,888 |
| 100 | wuji_description | `dexhands/wuji_description/xacro/ros2_control/hands2.xacro` | 67 | 3 | [fiveages-sim/robot-descriptions-common](https://github.com/fiveages-sim/robot-descriptions-common) | Apache-2.0 | 14 GLB | 210,688 |
| 100 | xhand1_description | `dexhands/xhand1_description/xacro/ros2_control/hand.xacro` | 31 | 2 | [fiveages-sim/robot-descriptions-common](https://github.com/fiveages-sim/robot-descriptions-common) | Apache-2.0 | 13 GLB | 172,496 |
| 100 | hitbot_description | `gripper/hitbot_description/xacro/gripper.xacro` | 8 | 1 | [fiveages-sim/robot-descriptions-common](https://github.com/fiveages-sim/robot-descriptions-common) | Apache-2.0 | 7 GLB | 79,528 |
| 100 | cr5_description | `cr5_description/xacro/ros2_control/robot.xacro` | 9 | 3 | [fiveages-sim/robot-descriptions-dobot](https://github.com/fiveages-sim/robot-descriptions-dobot) | Apache-2.0 | 7 OBJ | 63,960 |
| 100 | dexforce_w1_description | `humanoid/dexforce/dexfoce_w1_description/urdf/dexforce_w1_pro.urdf` | 34 | 4 | [fiveages-sim/robot_descriptions/humanoid/dexforce/dexfoce_w1_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/humanoid/dexforce/dexfoce_w1_description) | Apache-2.0 | 14 GLB | 275,290 |
| 100 | sa01_description | `humanoid/engineai/sa01_description/xacro/robot.xacro` | 13 | 1 | [fiveages-sim/robot_descriptions/humanoid/engineai/sa01_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/humanoid/engineai/sa01_description) | Apache-2.0 | 7 OBJ | 194,233 |
| 100 | piper_description | `manipulator/agilex/piper_description/xacro/ros2_control/robot.xacro` | 12 | 3 | [fiveages-sim/robot_descriptions/manipulator/agilex/piper_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/manipulator/agilex/piper_description) | Apache-2.0 | 3 GLB, 5 OBJ | 293,073 |
| 100 | airbot_play_description | `manipulator/airbot/airbot_play_description/xacro/ros2_control/robot.xacro` | 12 | 3 | [fiveages-sim/robot_descriptions/manipulator/airbot/airbot_play_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/manipulator/airbot/airbot_play_description) | Apache-2.0 | 8 OBJ | 112,256 |
| 100 | galaxea_a1_description | `manipulator/galaxea/galaxea_a1_description/xacro/ros2_control/robot.xacro` | 12 | 3 | [fiveages-sim/robot_descriptions/manipulator/galaxea/galaxea_a1_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/manipulator/galaxea/galaxea_a1_description) | Apache-2.0 | 9 GLB | 113,501 |
| 100 | rm75_description | `manipulator/realman/rm75_description/xacro/ros2_control/robot.xacro` | 11 | 3 | [fiveages-sim/robot_descriptions/manipulator/realman/rm75_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/manipulator/realman/rm75_description) | Apache-2.0 | 8 GLB | 43,032 |
| 100 | lbr_dual_arm | `lbr_demos/lbr_dual_arm/lbr_dual_arm/urdf/lbr_dual_arm.xacro` | 19 | 1 | [lbr-stack/lbr_fri_ros2_stack](https://github.com/lbr-stack/lbr_fri_ros2_stack) | Apache-2.0 | 8 DAE | 149,476 |
| 100 | lbr_ros2_control | `lbr_ros2_control/system_integration/med7/med7.xacro` | 10 | 4 | [lbr-stack/lbr_fri_ros2_stack](https://github.com/lbr-stack/lbr_fri_ros2_stack) | Apache-2.0 | 8 DAE | 70,553 |
| 100 | - | `gym_pybullet_drones/assets/cf2p.urdf` | 6 | 1 | [learnsyslab/gym-pybullet-drones](https://github.com/learnsyslab/gym-pybullet-drones) | MIT | 1 DAE | 7,058 |
| 100 | - | `gym_pybullet_drones/assets/cf2x.urdf` | 6 | 1 | [learnsyslab/gym-pybullet-drones](https://github.com/learnsyslab/gym-pybullet-drones) | MIT | 1 DAE | 7,058 |
| 100 | - | `gym_pybullet_drones/assets/racer.urdf` | 6 | 1 | [learnsyslab/gym-pybullet-drones](https://github.com/learnsyslab/gym-pybullet-drones) | MIT | 1 DAE | 7,058 |
| 100 | ur_description | `ur_description/urdf/ur3.xacro` | 11 | 15 | [ros-industrial/universal_robot](https://github.com/ros-industrial/universal_robot) | BSD AND Universal Robots A/S' Terms and Conditions for Use of Graphical Documentation | 7 DAE | 68,588 |
| 100 | schunk_svh_description | `schunk_svh_description/urdf/svh-standalone.urdf.xacro` | 32 | 1 | [SCHUNK-SE-Co-KG/schunk_svh_ros_driver](https://github.com/SCHUNK-SE-Co-KG/schunk_svh_ros_driver) | GPL-3.0 | 23 DAE | 18,247 |
| 100 | schunk_svh_driver | `schunk_svh_driver/urdf/schunk_svh_driver.xacro` | 32 | 10 | [SCHUNK-SE-Co-KG/schunk_svh_ros_driver](https://github.com/SCHUNK-SE-Co-KG/schunk_svh_ros_driver) | GPL-3.0 | 23 DAE | 18,247 |
| 100 | schunk_svh_simulation | `schunk_svh_simulation/urdf/schunk_svh_simulation.xacro` | 32 | 2 | [SCHUNK-SE-Co-KG/schunk_svh_ros_driver](https://github.com/SCHUNK-SE-Co-KG/schunk_svh_ros_driver) | GPL-3.0 | 23 DAE | 18,247 |
| 99 | dh_description | `gripper/dh_description/xacro/ros2_control/hand.xacro` | 9 | 3 | [fiveages-sim/robot-descriptions-common](https://github.com/fiveages-sim/robot-descriptions-common) | Apache-2.0 | 8 GLB | 310,376 |
| 99 | cr5_dual_description | `cr5_dual_description/xacro/ros2_control/robot.xacro` | 19 | 4 | [fiveages-sim/robot-descriptions-dobot](https://github.com/fiveages-sim/robot-descriptions-dobot) | Apache-2.0 | 8 OBJ | 147,838 |
| 99 | t1_description | `humanoid/booster/t1_description/xacro/robot.xacro` | 25 | 2 | [fiveages-sim/robot_descriptions/humanoid/booster/t1_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/humanoid/booster/t1_description) | Apache-2.0 | 22 OBJ | 168,479 |
| 99 | unitree_g1_description | `humanoid/unitree/unitree_g1_description/xacro/robot.xacro` | 39 | 5 | [fiveages-sim/robot_descriptions/humanoid/unitree/unitree_g1_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/humanoid/unitree/unitree_g1_description) | Apache-2.0 | 20 OBJ | 391,023 |
| 99 | agilex_aloha_description | `manipulator/agilex/agilex_aloha_description/xacro/base/tracer.xacro` | 13 | 15 | [fiveages-sim/robot_descriptions/manipulator/agilex/agilex_aloha_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/manipulator/agilex/agilex_aloha_description) | Apache-2.0 | 4 OBJ | 269,141 |
| 99 | elite_ec_description | `manipulator/elite/elite_ec_description/xacro/ros2_control/robot.xacro` | 9 | 3 | [fiveages-sim/robot_descriptions/manipulator/elite/elite_ec_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/manipulator/elite/elite_ec_description) | Apache-2.0 | 7 OBJ | 341,740 |
| 99 | galaxea_r1lite_description | `manipulator/galaxea/galaxea_r1lite_description/xacro/robot.xacro` | 38 | 3 | [fiveages-sim/robot_descriptions/manipulator/galaxea/galaxea_r1lite_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/manipulator/galaxea/galaxea_r1lite_description) | Apache-2.0 | 17 GLB | 298,033 |
| 98 | arx5_description | `arx5_description/xacro/ros2_control/robot.xacro` | 16 | 8 | [fiveages-sim/robot-descriptions-arx](https://github.com/fiveages-sim/robot-descriptions-arx) | BSD | 11 GLB | 181,430 |
| 98 | airbot_mmk2_description | `humanoid/airbot/airbot_mmk2_description/xacro/robot.xacro` | 32 | 4 | [fiveages-sim/robot_descriptions/humanoid/airbot/airbot_mmk2_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/humanoid/airbot/airbot_mmk2_description) | Apache-2.0 | 14 OBJ | 582,770 |
| 98 | hsrb_description | `hsrb_description/robots/hsrb4s.urdf.xacro` | 48 | 2 | [hsr-project/hsrb_common](https://github.com/hsr-project/hsrb_common) | BSD-3-Clause-Clear | 22 DAE | 42,322 |
| 97 | agibot_g1_description | `humanoid/agibot/agibot_g1_description/xacro/robot.xacro` | 52 | 5 | [fiveages-sim/robot_descriptions/humanoid/agibot/agibot_g1_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/humanoid/agibot/agibot_g1_description) | Apache-2.0 | 21 GLB | 513,773 |
| 97 | aidal_description | `humanoid/realman/aidal_description/xacro/robot.xacro` | 44 | 4 | [fiveages-sim/robot_descriptions/humanoid/realman/aidal_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/humanoid/realman/aidal_description) | Apache-2.0 | 21 GLB | 538,788 |
| 97 | - | `model/plugin/sdf/mug.xml` | 2 | 1 | [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco) | Apache-2.0 | 1 OBJ | 24,544 |
| 97 | hsrc_description | `hsrc_description/robots/hsrc1s.urdf.xacro` | 46 | 2 | [hsr-project/hsrb_common](https://github.com/hsr-project/hsrb_common) | BSD-3-Clause-Clear | 20 DAE | 24,834 |
| 96 | arx_x7s_description | `arx_x7s_description/urdf/arx_x7s.urdf` | 30 | 5 | [fiveages-sim/robot-descriptions-arx](https://github.com/fiveages-sim/robot-descriptions-arx) | BSD | 1 GLB, 15 OBJ | 840,446 |
| 96 | zsl1_description | `zsibot/zsl1_description/xacro/robot.xacro` | 17 | 1 | [fiveages-sim/robot-descriptions-quadruped](https://github.com/fiveages-sim/robot-descriptions-quadruped) | BSD3 | 5 OBJ | 837,007 |
| 96 | zerith_h1_description | `humanoid/zerith/zerith_h1_description/xacro/robot.xacro` | 36 | 3 | [fiveages-sim/robot_descriptions/humanoid/zerith/zerith_h1_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/humanoid/zerith/zerith_h1_description) | Apache-2.0 | 19 GLB | 745,926 |
| 96 | openarm_description | `manipulator/openarm/openarm_description/xacro/ros2_control/robot.xacro` | 26 | 5 | [fiveages-sim/robot_descriptions/manipulator/openarm/openarm_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/manipulator/openarm/openarm_description) | Apache-2.0 | 11 OBJ | 927,072 |
| 95 | anymal_d_simple_description | `urdf/anymal.urdf` | 96 | 1 | [ANYbotics/anymal_d_simple_description](https://github.com/ANYbotics/anymal_d_simple_description) | BSD-3-Clause | 17 DAE | 19,584 |
| 95 | - | `v2/cell/cell.xml` | 1 | 1 | [enactic/openarm_mujoco](https://github.com/enactic/openarm_mujoco) | Apache-2.0 | 22 OBJ, 8 STL | 56,457 |
| 95 | unitree_go2_description | `unitree/unitree_go2_description/xacro/robot.xacro` | 21 | 5 | [fiveages-sim/robot-descriptions-quadruped](https://github.com/fiveages-sim/robot-descriptions-quadruped) | BSD | 5 DAE | 381,016 |
| 95 | agibot_a2_description | `humanoid/agibot/agibot_a2_description/xacro/robot.xacro` | 57 | 2 | [fiveages-sim/robot_descriptions/humanoid/agibot/agibot_a2_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/humanoid/agibot/agibot_a2_description) | Apache-2.0 | 25 OBJ | 709,462 |
| 95 | - | `model/cards/cards.xml` | 53 | 1 | [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco) | Apache-2.0 | 1 OBJ | 4,028 |
| 95 | - | `model/cards/house_of_cards.xml` | 26 | 1 | [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco) | Apache-2.0 | 1 OBJ | 1,976 |
| 95 | jvrc_description | `urdf/jvrc1.urdf` | 60 | 1 | [jrl-umi3218/jvrc_description](https://github.com/jrl-umi3218/jvrc_description) | BSD-2-Clause | 35 DAE | 8,733 |
| 95 | egp_description | `egp_description/urdf/egp.urdf.xacro` | 3 | 2 | [SCHUNK-SE-Co-KG/schunk_description](https://github.com/SCHUNK-SE-Co-KG/schunk_description) | GPL-3.0 | 3 DAE | 12,075 |
| 95 | egu_description | `egu_description/urdf/egu_50.urdf.xacro` | 15 | 4 | [SCHUNK-SE-Co-KG/schunk_description](https://github.com/SCHUNK-SE-Co-KG/schunk_description) | GPL-3.0 | 15 DAE | 34,794 |
| 95 | pzn_plus_description | `pzn_plus_description/urdf/pzn_plus.urdf.xacro` | 7 | 2 | [SCHUNK-SE-Co-KG/schunk_description](https://github.com/SCHUNK-SE-Co-KG/schunk_description) | GPL-3.0 | 3 DAE | 18,870 |
| 95 | - | `unitree_robots/go2/go2.xml` | 17 | 1 | [unitreerobotics/unitree_mujoco](https://github.com/unitreerobotics/unitree_mujoco) | BSD-3-Clause | 16 OBJ | 398,432 |
| 95 | - | `models/rby1a/urdf/model.urdf` | 34 | 1 | [uynitsuj/rby1_description](https://github.com/uynitsuj/rby1_description) | MIT | 29 DAE | 262,104 |
| 95 | - | `models/rby1t5/urdf/model.urdf` | 34 | 1 | [uynitsuj/rby1_description](https://github.com/uynitsuj/rby1_description) | MIT | 29 DAE | 262,104 |
| 94 | arx_lift_description | `arx_lift_description/xacro/robot.xacro` | 41 | 3 | [fiveages-sim/robot-descriptions-arx](https://github.com/fiveages-sim/robot-descriptions-arx) | BSD | 12 GLB, 5 OBJ | 924,728 |
| 94 | galbot_zero_description | `galbot_zero_description/xacro/robot.xacro` | 63 | 3 | [fiveages-sim/robot-descriptions-galbot](https://github.com/fiveages-sim/robot-descriptions-galbot) | Apache-2.0 | 19 GLB, 4 OBJ | 1,166,425 |
| 94 | unitree_b2_description | `unitree/unitree_b2_description/xacro/robot.xacro` | 34 | 6 | [fiveages-sim/robot-descriptions-quadruped](https://github.com/fiveages-sim/robot-descriptions-quadruped) | BSD | 5 DAE | 288,093 |
| 94 | galaxea_r1_description | `humanoid/galaxea/galaxea_r1_description/xacro/robot.xacro` | 45 | 3 | [fiveages-sim/robot_descriptions/humanoid/galaxea/galaxea_r1_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/humanoid/galaxea/galaxea_r1_description) | Apache-2.0 | 21 GLB | 957,744 |
| 94 | galaxea_r1pro_description | `humanoid/galaxea/galaxea_r1pro_description/xacro/robot.xacro` | 45 | 3 | [fiveages-sim/robot_descriptions/humanoid/galaxea/galaxea_r1pro_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/humanoid/galaxea/galaxea_r1pro_description) | Apache-2.0 | 22 GLB | 913,226 |
| 94 | - | `galaxea_sim/assets/r1_lite/robot.urdf` | 34 | 1 | [OpenGalaxea/GalaxeaManipSim](https://github.com/OpenGalaxea/GalaxeaManipSim) | Apache-2.0 | 32 OBJ | 305,819 |
| 94 | - | `galaxea_sim/assets/r1_lite/robot_origin.urdf` | 34 | 1 | [OpenGalaxea/GalaxeaManipSim](https://github.com/OpenGalaxea/GalaxeaManipSim) | Apache-2.0 | 32 OBJ | 305,819 |
| 94 | pzv_64_description | `pzv_64_description/urdf/pzv_64.urdf.xacro` | 9 | 2 | [SCHUNK-SE-Co-KG/schunk_description](https://github.com/SCHUNK-SE-Co-KG/schunk_description) | GPL-3.0 | 3 DAE | 22,838 |
| 94 | ur_schunk_gripper_description | `ur_schunk_gripper_description/urdf/ur_schunk_gripper.urdf.xacro` | 22 | 1 | [SCHUNK-SE-Co-KG/schunk_description](https://github.com/SCHUNK-SE-Co-KG/schunk_description) | GPL-3.0 | 10 DAE | 152,459 |
| 94 | - | `unitree_robots/b2/b2.xml` | 13 | 1 | [unitreerobotics/unitree_mujoco](https://github.com/unitreerobotics/unitree_mujoco) | BSD-3-Clause | 28 OBJ, 3 STL | 499,366 |
| 94 | - | `models/rby1m/urdf/model.urdf` | 36 | 1 | [uynitsuj/rby1_description](https://github.com/uynitsuj/rby1_description) | MIT | 30 DAE | 381,839 |
| 93 | lite3_description | `deep_robotics/lite3_description/urdf/lite3.urdf` | 19 | 5 | [fiveages-sim/robot-descriptions-quadruped](https://github.com/fiveages-sim/robot-descriptions-quadruped) | MIT | 4 OBJ | 1,179,234 |
| 93 | pm01_description | `humanoid/engineai/pm01_description/xacro/robot.xacro` | 29 | 1 | [fiveages-sim/robot_descriptions/humanoid/engineai/pm01_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/humanoid/engineai/pm01_description) | Apache-2.0 | 14 OBJ | 1,347,049 |
| 93 | franka_gazebo | `franka_gazebo/test/launch/panda-gazebo.urdf` | 11 | 1 | [frankarobotics/franka_ros](https://github.com/frankarobotics/franka_ros) | Apache-2.0 | 8 DAE | 126,598 |
| 93 | - | `galaxea_sim/assets/r1_pro/robot.urdf` | 36 | 1 | [OpenGalaxea/GalaxeaManipSim](https://github.com/OpenGalaxea/GalaxeaManipSim) | Apache-2.0 | 36 OBJ | 519,306 |
| 93 | - | `galaxea_sim/assets/r1_pro/robot_origin.urdf` | 36 | 1 | [OpenGalaxea/GalaxeaManipSim](https://github.com/OpenGalaxea/GalaxeaManipSim) | Apache-2.0 | 36 OBJ | 519,306 |
| 92 | - | `data/cloth_z_up.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 32 |
| 92 | - | `data/cube.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `data/cube_collisionfilter.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `data/cube_concave.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `data/cube_convex.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `data/cube_gripper_left.urdf` | 2 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `data/cube_gripper_right.urdf` | 2 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `data/cube_no_friction.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `data/cube_small.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `data/cube_soft.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `data/dinnerware/cup/cup_small.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 8,192 |
| 92 | - | `data/dinnerware/plate.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 540 |
| 92 | - | `data/duck_vhacd.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 4,212 |
| 92 | - | `data/jenga/jenga.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `data/kuka_iiwa/model_free_base.urdf` | 8 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 8 OBJ | 14,758 |
| 92 | - | `data/sphere2.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 1,792 |
| 92 | - | `data/sphere2_rolling_friction.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 1,792 |
| 92 | - | `data/sphere2red.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 1,792 |
| 92 | - | `data/sphere_small.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 1,792 |
| 92 | - | `data/sphere_small_zeroinertia.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 1,792 |
| 92 | - | `data/sphere_transparent.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 1,792 |
| 92 | - | `data/sphere_with_restitution.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 1,792 |
| 92 | - | `data/torus/torus.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 1,152 |
| 92 | - | `data/torus/torus_with_plane.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 6,354 |
| 92 | - | `data/torus/torus_with_separate_plane.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 2 OBJ | 6,354 |
| 92 | - | `data/user_data_test_object.urdf` | 2 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 24 |
| 92 | - | `examples/pybullet/gym/pybullet_data/cloth_z_up.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 32 |
| 92 | - | `examples/pybullet/gym/pybullet_data/cube.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `examples/pybullet/gym/pybullet_data/cube_collisionfilter.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `examples/pybullet/gym/pybullet_data/cube_rotate.urdf` | 2 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `examples/pybullet/gym/pybullet_data/cube_small.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |
| 92 | - | `examples/pybullet/gym/pybullet_data/domino/domino.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 48 |
| 92 | - | `examples/pybullet/gym/pybullet_data/jenga/jenga.urdf` | 1 | 1 | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | NOASSERTION | 1 OBJ | 12 |

## Every candidate, by repository

Best score first. Each repository lists its robots, best first.

<details><summary><b>agilexrobotics/piper_ros</b>: best 100, 13 robot(s), MIT, last commit 2026-03-04</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `ac41fcbcdda5`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `src/piper_description/urdf/piper_description_v100.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 9.7 |  |
| 100 | `src/piper_description/urdf/piper_description_with_camera.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.6 |  |
| 99 | `src/piper_description/urdf/piper_description_v100_camera.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 19 · 9.6 |  |
| 85 | `src/piper_description/mujoco_model/piper_description.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `src/piper_description/mujoco_model/piper_no_gripper_description.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `src/piper_description/urdf/piper_description.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `src/piper_description/urdf/piper_description.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `src/piper_description/urdf/piper_description_gazebo.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `src/piper_description/urdf/piper_description_old.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `src/piper_description/urdf/piper_no_gripper_description.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `src/piper_description/urdf/piper_no_gripper_description.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `src/piper_description/urdf/piper_no_gripper_description_gazebo.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `src/piper_description/urdf/piper_no_gripper_description_old.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |

</details>

<details><summary><b>enactic/openarm_description</b>: best 100, 7 robot(s), Apache-2.0, last commit 2026-11-19</summary>

From: robot_descriptions.py. Commit `1677e5040ad9`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `assets/end_effector/parallel_link/urdf/parallel_link_standalone.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.5 |  |
| 100 | `assets/end_effector/pinch_gripper/urdf/pinch_gripper_standalone.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 90 | `assets/robot/openarm_v1.0/urdf/example/v1.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 0 |  |
| 90 | `assets/robot/openarm_v1.0/urdf/openarm_v10.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 0 |  |
| 25 | `assets/robot/openarm_v2.0/urdf/example/v2.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `assets/robot/openarm_v2.0/urdf/openarm_v20.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: zed_description Package not found: zed_description |
| 25 | `urdf/openarm.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: zed_description Package not found: zed_description |

</details>

<details><summary><b>fiveages-sim/robot-descriptions-arx</b>: best 100, 22 robot(s), no licence named, last commit 2026-11-16</summary>

From: fiveages submodules. Commit `b7ae0bea9ab8`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `arx_lift_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 98 | `arx5_description/urdf/arx5.urdf` | urdf | 15 · 10 · 20 · 15 · 8.2 · 20 · 10 |  |
| 98 | `arx5_description/urdf/arx5_ac1.urdf` | urdf | 15 · 10 · 20 · 15 · 8.2 · 20 · 10 |  |
| 98 | `arx5_description/urdf/arx5_agilex.urdf` | urdf | 15 · 10 · 20 · 15 · 8.2 · 20 · 10 |  |
| 98 | `arx5_description/urdf/arx5_r5.urdf` | urdf | 15 · 10 · 20 · 15 · 8.2 · 20 · 10 |  |
| 98 | `arx5_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 8.2 · 20 · 10 |  |
| 98 | `arx5_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 8.2 · 20 · 10 |  |
| 98 | `arx_x7s_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 8.3 · 20 · 9.9 |  |
| 96 | `arx_x7s_description/urdf/arx_x7s.urdf` | urdf | 15 · 10 · 20 · 15 · 9.6 · 20 · 6.4 |  |
| 96 | `arx_x7s_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.6 · 20 · 6.4 |  |
| 96 | `arx_x7s_description/xacro/robot_full.xacro` | xacro | 15 · 10 · 20 · 15 · 9.6 · 20 · 6.4 |  |
| 96 | `arx_x7s_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.6 · 20 · 6.4 |  |
| 94 | `arx_lift_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 8.4 · 20 · 6 |  |
| 94 | `arx_lift_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 8.4 · 20 · 6 |  |
| 89 | `arx_acone_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 7.6 · 20 · 8.9 |  |
| 89 | `arx_acone_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 7.6 · 20 · 8.9 |  |
| 89 | `arx_lift2s_description/xacro/component.xacro` | xacro | 7.5 · 10 · 20 · 15 · 6.7 · 20 · 10 |  |
| 86 | `arx_acone_description/xacro/component.xacro` | xacro | 7.5 · 10 · 20 · 15 · 3.3 · 20 · 10 |  |
| 83 | `arx_lift2s_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 7.7 · 20 · 2.9 |  |
| 83 | `arx_lift2s_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 7.7 · 20 · 2.9 |  |
| 60 | `arx5_description/xacro/gripper.xacro` | xacro | 15 · 10 · 20 · 15 · 0 · 0 · 0 |  |
| 25 | `arx5_description/xacro/component.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>fiveages-sim/robot-descriptions-common</b>: best 100, 28 robot(s), Apache-2.0, last commit 2026-11-17</summary>

From: fiveages submodules. Commit `3464e5484c73`. Also 4 SDF file(s), not measured.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `dexhands/freedom_description/xacro/hand.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `dexhands/freedom_description/xacro/ros2_control/hand.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `dexhands/wuji_description/xacro/hand.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `dexhands/wuji_description/xacro/ros2_control/hand.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `dexhands/wuji_description/xacro/ros2_control/hands2.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.9 |  |
| 100 | `dexhands/xhand1_description/xacro/hand.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `dexhands/xhand1_description/xacro/ros2_control/hand.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `gripper/hitbot_description/xacro/gripper.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 99 | `gripper/dh_description/xacro/hand.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.4 |  |
| 99 | `gripper/dh_description/xacro/ros2_control/hand.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.4 |  |
| 60 | `dexhands/brainco_description/xacro/ros2_control/hand.xacro` | xacro | 15 · 10 · 20 · 15 · 0 · 0 · 0 |  |
| 60 | `dexhands/linkerhand_description/xacro/ros2_control/hand.xacro` | xacro | 15 · 10 · 20 · 15 · 0 · 0 · 0 |  |
| 60 | `dexhands/theohand_description/xacro/ros2_control/hand.xacro` | xacro | 15 · 10 · 20 · 15 · 0 · 0 · 0 |  |
| 60 | `gripper/changingtek_description/xacro/ros2_control/gripper.xacro` | xacro | 15 · 10 · 20 · 15 · 0 · 0 · 0 |  |
| 25 | `dexhands/brainco_description/xacro/hand.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `dexhands/linkerhand_description/xacro/hand.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `dexhands/oymotion_description/xacro/hand.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `dexhands/theohand_description/xacro/hand.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `gripper/changingtek_description/xacro/gripper.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `gripper/dh_description/xacro/gripper.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `gripper/eincinx_description/xacro/gripper.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `gripper/inspire_description/xacro/gripper.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `gripper/inspire_description/xacro/hand.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `gripper/inspire_description/xacro/ros2_control/hand.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `gripper/jodell_description/xacro/gripper.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `gripper/marvin_gripper_description/xacro/gripper.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `gripper/robotiq_gripper_description/xacro/gripper.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotiq_description Package not found: robotiq_description |
| 25 | `gripper/robotiq_gripper_description/xacro/ros2_control/gripper.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotiq_description Package not found: robotiq_description |

</details>

<details><summary><b>fiveages-sim/robot-descriptions-dobot</b>: best 100, 7 robot(s), Apache-2.0, last commit 2026-11-16</summary>

From: fiveages submodules. Commit `ac62a415469b`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `cr5_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `cr5_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 99 | `cr5_dual_description/urdf/cr5_dual.urdf` | urdf | 15 · 10 · 20 · 15 · 9.3 · 20 · 10 |  |
| 99 | `cr5_dual_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.3 · 20 · 10 |  |
| 99 | `cr5_dual_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.3 · 20 · 10 |  |
| 25 | `cr5_description/xacro/grippers.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: name 'selected_gripper_type' is not defined when evaluating expression 'selected_gripper_type == 'empty' and kinematic_only' |
| 25 | `cr5_dual_description/xacro/grippers.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: name 'selected_gripper_type' is not defined when evaluating expression 'selected_gripper_type == 'robotiq85'' |

</details>

<details><summary><b>fiveages-sim/robot-descriptions-galbot</b>: best 100, 24 robot(s), Apache-2.0, last commit 2026-10-10</summary>

From: fiveages submodules. Commit `11a1a1f0d20d`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `galbot_foxtrot_description/xacro/gripper.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `galbot_golf_description/xacro/gripper.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `galbot_one_description/xacro/gripper.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `galbot_zero_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 97 | `galbot_foxtrot_description/xacro/components/body.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 6.6 |  |
| 97 | `galbot_golf_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 6.6 |  |
| 96 | `galbot_s1_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 8 · 20 · 7.7 |  |
| 94 | `galbot_one_description/xacro/components/body.xacro` | xacro | 15 · 10 · 20 · 15 · 6.9 · 20 · 7.2 |  |
| 94 | `galbot_zero_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.2 · 20 · 4.6 |  |
| 94 | `galbot_zero_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.2 · 20 · 4.6 |  |
| 92 | `galbot_charlie_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 6.7 · 20 · 5.5 |  |
| 92 | `galbot_foxtrot_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 6.7 · 20 · 5.5 |  |
| 92 | `galbot_one_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 6.7 · 20 · 5.5 |  |
| 89 | `galbot_charlie_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 8.7 · 20 · 0 |  |
| 89 | `galbot_charlie_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 8.7 · 20 · 0 |  |
| 89 | `galbot_foxtrot_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.2 · 20 · 0 |  |
| 89 | `galbot_foxtrot_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.2 · 20 · 0 |  |
| 89 | `galbot_golf_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.4 · 20 · 0 |  |
| 89 | `galbot_golf_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.4 · 20 · 0 |  |
| 89 | `galbot_one_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 8.7 · 20 · 0 |  |
| 89 | `galbot_one_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 8.7 · 20 · 0 |  |
| 88 | `galbot_s1_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 7.8 · 20 · 0 |  |
| 88 | `galbot_s1_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 7.8 · 20 · 0 |  |
| 25 | `galbot_foxtrot_description/xacro/components/suction_cup.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/agibot/agibot_g1_description</b>: best 100, 5 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `humanoid/agibot/agibot_g1_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.8 |  |
| 100 | `humanoid/agibot/agibot_g1_description/xacro/g1_base.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.8 |  |
| 97 | `humanoid/agibot/agibot_g1_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.1 · 20 · 8.3 |  |
| 97 | `humanoid/agibot/agibot_g1_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.1 · 20 · 8.3 |  |
| 25 | `humanoid/agibot/agibot_g1_description/xacro/gazebo.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/astribot/astribot_s1_description</b>: best 100, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `humanoid/astribot/astribot_s1_description/xacro/gripper.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `humanoid/astribot/astribot_s1_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 2.1 |  |
| 92 | `humanoid/astribot/astribot_s1_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 2.1 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/booster/t1_description</b>: best 100, 2 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `humanoid/booster/t1_description/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 99 | `humanoid/booster/t1_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.6 · 19.6 · 10 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/dexforce/dexfoce_w1_description</b>: best 100, 4 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `humanoid/dexforce/dexfoce_w1_description/urdf/dexforce_w1_pro.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 9.6 |  |
| 99 | `humanoid/dexforce/dexfoce_w1_description/urdf/dexforce_w1.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 9.4 |  |
| 99 | `humanoid/dexforce/dexfoce_w1_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.4 |  |
| 99 | `humanoid/dexforce/dexfoce_w1_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.4 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/engineai/sa01_description</b>: best 100, 1 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `humanoid/engineai/sa01_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/galaxea/galaxea_r1pro_description</b>: best 100, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `humanoid/galaxea/galaxea_r1pro_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 94 | `humanoid/galaxea/galaxea_r1pro_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 8.4 · 20 · 6 |  |
| 94 | `humanoid/galaxea/galaxea_r1pro_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 8.4 · 20 · 6 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/realman/aidal_description</b>: best 100, 4 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `humanoid/realman/aidal_description/xacro/components/body.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.7 |  |
| 98 | `humanoid/realman/aidal_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 7.9 · 20 · 10 |  |
| 97 | `humanoid/realman/aidal_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 8.7 · 20 · 8.1 |  |
| 97 | `humanoid/realman/aidal_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 8.7 · 20 · 8.1 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/unitree/unitree_g1_description</b>: best 100, 5 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `humanoid/unitree/unitree_g1_description/xacro/hand.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 99 | `humanoid/unitree/unitree_g1_description/urdf/unitree_g1.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 8.9 |  |
| 99 | `humanoid/unitree/unitree_g1_description/urdf/unitree_g1_revo2.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 8.9 |  |
| 99 | `humanoid/unitree/unitree_g1_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 8.9 |  |
| 99 | `humanoid/unitree/unitree_g1_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 8.9 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/manipulator/agilex/piper_description</b>: best 100, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `manipulator/agilex/piper_description/urdf/piper.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 9.6 |  |
| 100 | `manipulator/agilex/piper_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.5 |  |
| 100 | `manipulator/agilex/piper_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.5 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/manipulator/airbot/airbot_play_description</b>: best 100, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `manipulator/airbot/airbot_play_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `manipulator/airbot/airbot_play_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 25 | `manipulator/airbot/airbot_play_description/xacro/ros2_control/gazebo.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/manipulator/galaxea/galaxea_a1_description</b>: best 100, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `manipulator/galaxea/galaxea_a1_description/xacro/gripper.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `manipulator/galaxea/galaxea_a1_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `manipulator/galaxea/galaxea_a1_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/manipulator/galaxea/galaxea_r1lite_description</b>: best 100, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `manipulator/galaxea/galaxea_r1lite_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 99 | `manipulator/galaxea/galaxea_r1lite_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.4 · 20 · 9.5 |  |
| 99 | `manipulator/galaxea/galaxea_r1lite_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.4 · 20 · 9.5 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/manipulator/realman/rm75_description</b>: best 100, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `manipulator/realman/rm75_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `manipulator/realman/rm75_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 90 | `manipulator/realman/rm75_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 0 · 20 · 10 |  |

</details>

<details><summary><b>lbr-stack/lbr_fri_ros2_stack</b>: best 100, 5 robot(s), Apache-2.0, last commit 2026-11-06</summary>

From: awesome-robot-descriptions. Commit `d37b75142d53`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `lbr_demos/lbr_dual_arm/lbr_dual_arm/urdf/lbr_dual_arm.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `lbr_ros2_control/system_integration/iiwa14/iiwa14.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `lbr_ros2_control/system_integration/iiwa7/iiwa7.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `lbr_ros2_control/system_integration/med14/med14.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `lbr_ros2_control/system_integration/med7/med7.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |

</details>

<details><summary><b>learnsyslab/gym-pybullet-drones</b>: best 100, 5 robot(s), MIT, last commit 2026-11-13</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `410c2395947f`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `gym_pybullet_drones/assets/cf2p.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `gym_pybullet_drones/assets/cf2x.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `gym_pybullet_drones/assets/racer.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 85 | `gym_pybullet_drones/assets/architrave.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `gym_pybullet_drones/assets/box.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 10 |  |

</details>

<details><summary><b>mesh-iit/ergocub-software</b>: best 100, 18 robot(s), BSD-3-Clause, last commit 2026-11-03</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `6c255e258cd1`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `urdf/ergoCub/robots/ergoCubGazeboV1/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 9.6 |  |
| 100 | `urdf/ergoCub/robots/ergoCubGazeboV1_1/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 19.8 · 9.8 |  |
| 100 | `urdf/ergoCub/robots/ergoCubGazeboV1_1_minContacts/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 19.8 · 9.8 |  |
| 100 | `urdf/ergoCub/robots/ergoCubGazeboV1_minContacts/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 9.6 |  |
| 85 | `urdf/ergoCub/robots/ergoCubGazeboSN000/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubGazeboSN000_minContacts/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubGazeboSN001/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubGazeboSN001_minContacts/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubGazeboSN002/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubGazeboSN002_minContacts/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubGazeboSN003/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubGazeboSN003_minContacts/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubGazeboV1_3/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubGazeboV1_3_minContacts/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubSN000/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubSN001/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubSN002/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `urdf/ergoCub/robots/ergoCubSN003/model.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |

</details>

<details><summary><b>ros-industrial/universal_robot</b>: best 100, 16 robot(s), no licence named, last commit 2026-07-20</summary>

From: awesome-robot-descriptions. Commit `39ad110d8f2e`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `ur_description/urdf/ur10.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur10e.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur12e.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur15.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur16e.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur18.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur20.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur3.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur30.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur3e.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur5.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur5e.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur7e.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `ur_description/urdf/ur8long.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 25 | `ur_description/urdf/ur.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &#91;Errno 2&#93; No such file or directory: '.\\' when evaluating expression 'xacro.load_yaml(joint_limits_parameters_file)' when evaluating expression 'config_joint_limit_parameters&#91;'joint_limits'&#93;' when evaluating expression 'sec_limits&#91;'shoulder_pan'&#93;&#91;'min_position'&#93;' |
| 25 | `ur_gazebo/urdf/ur.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &#91;Errno 2&#93; No such file or directory: '.\\' when evaluating expression 'xacro.load_yaml(joint_limits_parameters_file)' when evaluating expression 'config_joint_limit_parameters&#91;'joint_limits'&#93;' when evaluating expression 'sec_limits&#91;'shoulder_pan'&#93;&#91;'min_position'&#93;' |

</details>

<details><summary><b>SCHUNK-SE-Co-KG/schunk_svh_ros_driver</b>: best 100, 13 robot(s), GPL-3.0, last commit 2026-11-19</summary>

From: awesome-robot-descriptions. Commit `67bcc89cd5ca`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 100 | `schunk_svh_description/urdf/svh-standalone.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `schunk_svh_driver/urdf/schunk_svh_driver.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 100 | `schunk_svh_simulation/urdf/schunk_svh_simulation.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 25 | `schunk_svh_driver/urdf/parameters/finger_spread.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `schunk_svh_driver/urdf/parameters/index_finger_distal.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `schunk_svh_driver/urdf/parameters/index_finger_proximal.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `schunk_svh_driver/urdf/parameters/middle_finger_distal.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `schunk_svh_driver/urdf/parameters/middle_finger_proximal.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `schunk_svh_driver/urdf/parameters/pinky.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `schunk_svh_driver/urdf/parameters/ring_finger.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `schunk_svh_driver/urdf/parameters/thumb_flexion.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `schunk_svh_driver/urdf/parameters/thumb_opposition.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `schunk_svh_simulation/etc/svh_mujoco.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 23 visual mesh file(s) missing |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/airbot/airbot_mmk2_description</b>: best 99, 4 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 99 | `humanoid/airbot/airbot_mmk2_description/xacro/mmk2_base.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.1 |  |
| 98 | `humanoid/airbot/airbot_mmk2_description/urdf/airbot_mmk2.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 7.9 |  |
| 98 | `humanoid/airbot/airbot_mmk2_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 7.9 |  |
| 98 | `humanoid/airbot/airbot_mmk2_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 7.9 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/manipulator/agilex/agilex_aloha_description</b>: best 99, 15 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 99 | `manipulator/agilex/agilex_aloha_description/xacro/base/ranger_mini.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 8.9 |  |
| 99 | `manipulator/agilex/agilex_aloha_description/xacro/base/tracer.xacro` | xacro | 15 · 10 · 20 · 15 · 9.1 · 20 · 9.6 |  |
| 99 | `manipulator/agilex/agilex_aloha_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 8.9 |  |
| 95 | `manipulator/agilex/agilex_aloha_description/xacro/base/tracer_v2.xacro` | xacro | 15 · 10 · 20 · 15 · 6.4 · 20 · 8.4 |  |
| 25 | `manipulator/agilex/agilex_aloha_description/urdf/agilex_aloha.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `manipulator/agilex/agilex_aloha_description/urdf/agilex_aloha_v1.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 11 visual mesh file(s) missing |
| 25 | `manipulator/agilex/agilex_aloha_description/urdf/agilex_aloha_v1_x5.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 11 visual mesh file(s) missing |
| 25 | `manipulator/agilex/agilex_aloha_description/urdf/agilex_aloha_v2-1.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `manipulator/agilex/agilex_aloha_description/urdf/agilex_aloha_v2.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `manipulator/agilex/agilex_aloha_description/xacro/aloha_split.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `manipulator/agilex/agilex_aloha_description/xacro/body/split.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `manipulator/agilex/agilex_aloha_description/xacro/body/v1.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `manipulator/agilex/agilex_aloha_description/xacro/body/v2.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `manipulator/agilex/agilex_aloha_description/xacro/robot.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `manipulator/agilex/agilex_aloha_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/manipulator/elite/elite_ec_description</b>: best 99, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 99 | `manipulator/elite/elite_ec_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.2 |  |
| 99 | `manipulator/elite/elite_ec_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 9.2 |  |
| 98 | `manipulator/elite/elite_ec_description/urdf/elite_ec.urdf` | urdf | 15 · 10 · 20 · 15 · 8.8 · 20 · 9.2 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/manipulator/openarm/openarm_description</b>: best 99, 5 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 99 | `manipulator/openarm/openarm_description/urdf/openarm_left.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 8.7 |  |
| 99 | `manipulator/openarm/openarm_description/urdf/openarm_right.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 8.7 |  |
| 96 | `manipulator/openarm/openarm_description/urdf/openarm.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 20 · 6 |  |
| 96 | `manipulator/openarm/openarm_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 6 |  |
| 96 | `manipulator/openarm/openarm_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 6 |  |

</details>

<details><summary><b>hsr-project/hsrb_common</b>: best 98, 4 robot(s), BSD-3-Clause-Clear, last commit 2026-10-02</summary>

From: robot_descriptions.py. Commit `c0b8ad5f813f`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 98 | `hsrb_description/robots/hsrb4s.urdf.xacro` | xacro | 15 · 10 · 20 · 13.5 · 10 · 19 · 10 |  |
| 97 | `hsrc_description/robots/hsrc1s.urdf.xacro` | xacro | 15 · 10 · 20 · 13.5 · 10 · 18.9 · 10 |  |
| 25 | `hsrb_description/urdf/materials.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `hsrc_description/urdf/materials.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>google-deepmind/mujoco</b>: best 97, 365 robot(s), Apache-2.0, last commit 2026-11-19</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `be581a690cdd`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 97 | `model/plugin/sdf/mug.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 16.7 · 10 |  |
| 95 | `model/cards/cards.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 15 · 10 |  |
| 95 | `model/cards/house_of_cards.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 15 · 10 |  |
| 90 | `mjx/mujoco/mjx/test_data/shadow_hand/right_hand.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 10.4 · 10 |  |
| 90 | `mjx/mujoco/mjx/test_data/shadow_hand/scene_right.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 10.5 · 10 |  |
| 90 | `model/mug/mug.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 10.4 · 10 |  |
| 90 | `test/experimental/usd/plugins/mjcf/testdata/mesh_obj.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 10 · 10 |  |
| 90 | `test/user/testdata/inertia_concave.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 10 · 10 |  |
| 85 | `doc/_static/hello.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `doc/_static/tendon.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/actuator/arm26.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/convex.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/humanoid/01_humanoids.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/humanoid/02_humanoids.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/humanoid/03_humanoids.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/humanoid/04_humanoids.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/humanoid/05_humanoids.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/humanoid/06_humanoids.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/humanoid/07_humanoids.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/humanoid/08_humanoids.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/humanoid/09_humanoids.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/humanoid/10_humanoids.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/humanoid/humanoid.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/quadratic_frictionloss.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `mjx/mujoco/mjx/test_data/tendon/tendon.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/adhesion/fridge_door.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/adhesion/sand_castle.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/arch/gothic.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/arch/hyperbolic.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/arch/roman.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/balloons/balloons.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/flex/basket.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/flex/cloth_sdf.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/flex/hollow_vs_solid.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/flex/mannequin.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/flex/mechanisms/cantilever.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/flex/strain.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/humanoid/humanoid.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/humanoid/humanoid100.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `model/plastic/clay.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| | and 325 more, in `audit.json` | | | |

</details>

<details><summary><b>fiveages-sim/robot-descriptions-quadruped</b>: best 96, 48 robot(s), no licence named, last commit 2025-12-15</summary>

From: fiveages submodules. Commit `98107c72260b`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 96 | `zsibot/zsl1_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 20 · 6.5 |  |
| 95 | `unitree/unitree_go2_description/urdf/unitree_go2.urdf` | urdf | 15 · 10 · 20 · 15 · 9.5 · 16.8 · 9 |  |
| 95 | `unitree/unitree_go2_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.5 · 16.8 · 9 |  |
| 95 | `unitree/unitree_go2_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.5 · 16.8 · 9 |  |
| 94 | `unitree/unitree_b2_description/urdf/unitree_b2.urdf` | urdf | 15 · 10 · 20 · 15 · 9.7 · 14.8 · 9.5 |  |
| 94 | `unitree/unitree_b2_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.7 · 14.8 · 9.5 |  |
| 94 | `unitree/unitree_b2_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.7 · 14.8 · 9.5 |  |
| 93 | `deep_robotics/lite3_description/urdf/lite3.urdf` | urdf | 15 · 10 · 20 · 15 · 9.5 · 18.7 · 4.6 |  |
| 93 | `deep_robotics/lite3_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.5 · 18.7 · 4.6 |  |
| 93 | `deep_robotics/lite3_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.5 · 18.7 · 4.6 |  |
| 90 | `deep_robotics/x30_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.5 · 18.7 · 1.8 |  |
| 90 | `deep_robotics/x30_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.5 · 18.7 · 1.8 |  |
| 88 | `magiclab/magicdog_description/urdf/magicdog.urdf` | urdf | 15 · 10 · 20 · 15 · 7.4 · 19.3 · 1.4 |  |
| 88 | `magiclab/magicdog_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 7.4 · 19.3 · 1.4 |  |
| 88 | `magiclab/magicdog_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 7.4 · 19.3 · 1.4 |  |
| 87 | `unitree/aliengo_description/urdf/aliengo.urdf` | urdf | 7.5 · 10 · 20 · 15 · 9.7 · 14.8 · 10 |  |
| 87 | `unitree/aliengo_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.7 · 14.8 · 10 |  |
| 87 | `unitree/aliengo_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.7 · 14.8 · 10 |  |
| 87 | `unitree/unitree_a1_description/urdf/unitree_a1.urdf` | urdf | 7.5 · 10 · 20 · 15 · 7.8 · 16.8 · 9.9 |  |
| 87 | `unitree/unitree_a1_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 7.8 · 16.8 · 9.9 |  |
| 87 | `unitree/unitree_a1_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 7.8 · 16.8 · 9.9 |  |
| 86 | `unitree/unitree_go1_description/urdf/unitree_go1.urdf` | urdf | 7.5 · 10 · 20 · 15 · 9.7 · 15.4 · 8 |  |
| 84 | `unitree/unitree_go1_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 7.7 · 15.4 · 8 |  |
| 84 | `unitree/unitree_go1_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 7.7 · 15.4 · 8 |  |
| 80 | `deep_robotics/x30_description/xacro/imu_link.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 0 · 10 |  |
| 79 | `magiclab/cyberdog_description/urdf/cyberdog.urdf` | urdf | 0 · 10 · 20 · 15 · 7.5 · 16.8 · 10 |  |
| 79 | `magiclab/cyberdog_description/xacro/robot.xacro` | xacro | 0 · 10 · 20 · 15 · 7.5 · 16.8 · 10 |  |
| 79 | `magiclab/cyberdog_description/xacro/ros2_control/robot.xacro` | xacro | 0 · 10 · 20 · 15 · 7.5 · 16.8 · 10 |  |
| 25 | `deep_robotics/lite3_description/xacro/ros2_control/gazebo.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: gz_quadruped_hardware Package not found: gz_quadruped_hardware |
| 25 | `deep_robotics/lite3_description/xacro/ros2_control/ros2_control.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `deep_robotics/x30_description/urdf/x30.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 4 visual mesh file(s) missing |
| 25 | `deep_robotics/x30_description/urdf/x30_generated.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 4 visual mesh file(s) missing |
| 25 | `deep_robotics/x30_description/xacro/ros2_control/gazebo.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: gz_quadruped_hardware Package not found: gz_quadruped_hardware |
| 25 | `deep_robotics/x30_description/xacro/ros2_control/ros2_control.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `magiclab/magicdog_description/xacro/ros2_control/gazebo.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `unitree/unitree_b2_description/xacro/materials.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `unitree/unitree_b2_description/xacro/ros2_control/gazebo.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: gz_quadruped_hardware Package not found: gz_quadruped_hardware |
| 25 | `unitree/unitree_b2_description/xacro/ros2_control/ros2_control.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `unitree/unitree_go2_description/xacro/ros2_control/gazebo.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: gz_quadruped_hardware Package not found: gz_quadruped_hardware |
| 25 | `unitree/unitree_go2_description/xacro/ros2_control/ros2_control.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| | and 8 more, in `audit.json` | | | |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/zerith/zerith_h1_description</b>: best 96, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 96 | `humanoid/zerith/zerith_h1_description/xacro/components/body.xacro` | xacro | 15 · 10 · 20 · 13.5 · 8.3 · 20 · 9 |  |
| 96 | `humanoid/zerith/zerith_h1_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 14.3 · 9.7 · 20 · 7 |  |
| 25 | `humanoid/zerith/zerith_h1_description/urdf/ZR_H1PRO-1.2.00.H.V4.3_URDF_2025.12.02.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 35 visual mesh file(s) missing |

</details>

<details><summary><b>ANYbotics/anymal_d_simple_description</b>: best 95, 1 robot(s), BSD-3-Clause, last commit 2025-02-15</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `d5bf4dc3a81a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 95 | `urdf/anymal.urdf` | urdf | 15 · 5 · 20 · 15 · 9.7 · 20 · 10 |  |

</details>

<details><summary><b>enactic/openarm_mujoco</b>: best 95, 24 robot(s), Apache-2.0, last commit 2026-11-19</summary>

From: robot_descriptions.py. Commit `ed2046f30981`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 95 | `v2/cell/cell.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 14.6 · 10 |  |
| 92 | `v2/openarm_bimanual_cell.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 12 · 9.9 |  |
| 92 | `v2/openarm_bimanual_model.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 12 · 9.9 |  |
| 85 | `v2/cell/articulated_cell_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/cell/demo.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/cell/move_puck_cell_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/cell/peg_socket_cell_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/cell/tool_cell_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/cell/valve_cell_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/pedestal/articulated_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/pedestal/balance_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/pedestal/catch_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/pedestal/move_puck_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/pedestal/peg_socket_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/pedestal/throw_multi_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/pedestal/throw_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/pedestal/tool_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `v2/pedestal/valve_scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 83 | `v0.3/openarm.mjcf.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 2.6 · 10 |  |
| 83 | `v1/openarm.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 8.6 · 4.7 |  |
| 82 | `v0.3/openarm_bimanual.mjcf.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 2.5 · 10 |  |
| 79 | `v1/openarm_bimanual.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 8.7 · 0 |  |
| 78 | `v2/cell/bottle_cell_scene.xml` | mjcf | 15 · 10 · 20 · 7.5 · 10 · 5 · 10 |  |
| 78 | `v2/pedestal/bottle_scene.xml` | mjcf | 15 · 10 · 20 · 7.5 · 10 · 5 · 10 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/agibot/agibot_a2_description</b>: best 95, 2 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 95 | `humanoid/agibot/agibot_a2_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 12.9 · 10 · 20 · 7.2 |  |
| 25 | `humanoid/agibot/agibot_a2_description/xacro/component.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: Invalid parameter "joint_idx_offset" |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/galaxea/galaxea_r1_description</b>: best 95, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 95 | `humanoid/galaxea/galaxea_r1_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 5 · 20 · 10 |  |
| 94 | `humanoid/galaxea/galaxea_r1_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 7.9 · 20 · 5.8 |  |
| 94 | `humanoid/galaxea/galaxea_r1_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 7.9 · 20 · 5.8 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/spiritai/moz1_description</b>: best 95, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 95 | `humanoid/spiritai/moz1_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 5 · 20 · 10 |  |
| 90 | `humanoid/spiritai/moz1_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.6 · 20 · 0 |  |
| 90 | `humanoid/spiritai/moz1_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 9.6 · 20 · 0 |  |

</details>

<details><summary><b>jrl-umi3218/jvrc_description</b>: best 95, 1 robot(s), BSD-2-Clause, last commit 2025-05-19</summary>

From: robot_descriptions.py. Commit `80a2aacca2dc`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 95 | `urdf/jvrc1.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 20 · 10 |  |

</details>

<details><summary><b>SCHUNK-SE-Co-KG/schunk_description</b>: best 95, 11 robot(s), GPL-3.0, last commit 2024-06-07</summary>

From: awesome-robot-descriptions. Commit `f88f51309a1d`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 95 | `egp_description/urdf/egp.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 20 · 10 |  |
| 95 | `egu_description/urdf/egu_50.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 20 · 10 |  |
| 95 | `pzn_plus_description/urdf/pzn_plus.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 20 · 10 |  |
| 94 | `pzv_64_description/urdf/pzv_64.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 8.9 · 20 · 10 |  |
| 94 | `ur_schunk_gripper_description/urdf/ur_schunk_gripper.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 9.4 · 20 · 10 |  |
| 20 | `egp_description/urdf/egp.gazebo.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 20 | `egu_description/urdf/egu_50.gazebo.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 20 | `egu_description/urdf/egu_50_base_link.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 20 | `egu_description/urdf/egu_50_fingers_link.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 20 | `pzn_plus_description/urdf/pzn_plus.gazebo.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 20 | `pzv_64_description/urdf/pzv_64.gazebo.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>unitreerobotics/unitree_mujoco</b>: best 95, 14 robot(s), BSD-3-Clause, last commit 2026-09-07</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `1eb6642e3f3f`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 95 | `unitree_robots/go2/go2.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 15.9 · 8.9 |  |
| 94 | `unitree_robots/b2/b2.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 16.2 · 8.3 |  |
| 86 | `unitree_robots/a2/qrc_map_sloped.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 6.6 · 9 |  |
| 86 | `unitree_robots/b2w/b2w.xml` | mjcf | 15 · 10 · 20 · 11.2 · 10 · 12 · 7.9 |  |
| 85 | `unitree_robots/go2w/go2w.xml` | mjcf | 15 · 10 · 20 · 11.2 · 10 · 11.2 · 7.5 |  |
| 84 | `unitree_robots/a2/a2.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 9.5 |  |
| 84 | `unitree_robots/h2/h2_mujoco.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.8 |  |
| 83 | `unitree_robots/as2/as2.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 7.7 |  |
| 83 | `unitree_robots/g1/g1_29dof.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 7.9 |  |
| 80 | `unitree_robots/h1/h1.xml` | mjcf | 15 · 10 · 20 · 14.2 · 10 · 2.6 · 8 |  |
| 80 | `unitree_robots/h1_2/h1_2_handless.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 5.3 |  |
| 80 | `unitree_robots/r1/R1_C++.xml` | mjcf | 15 · 10 · 20 · 12.4 · 10 · 5 · 7.6 |  |
| 79 | `unitree_robots/g1/g1_23dof.xml` | mjcf | 15 · 10 · 20 · 11.9 · 10 · 5 · 7.2 |  |
| 25 | `unitree_robots/a2/qrc_map_flat.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 146 visual mesh file(s) missing |

</details>

<details><summary><b>uynitsuj/rby1_description</b>: best 95, 97 robot(s), MIT, last commit 2025-07-03</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `e4c07203aa0a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 95 | `models/rby1a/urdf/model.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 20 · 9.7 |  |
| 95 | `models/rby1t5/urdf/model.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 20 · 9.7 |  |
| 94 | `models/rby1m/urdf/model.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 20 · 9 |  |
| 85 | `models/rby1a/mujoco/assets/LINK_10/LINK_10.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 10 · 10 |  |
| 85 | `models/rby1a/mujoco/assets/LINK_17/LINK_17.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 10 · 10 |  |
| 85 | `models/rby1m/mujoco/assets/LINK_10/LINK_10.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 10 · 10 |  |
| 85 | `models/rby1m/mujoco/assets/LINK_17/LINK_17.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 10 · 10 |  |
| 85 | `models/rby1t5/mujoco/assets/LINK_10/LINK_10.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 10 · 10 |  |
| 85 | `models/rby1t5/mujoco/assets/LINK_17/LINK_17.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 10 · 10 |  |
| 84 | `models/rby1a/mujoco/assets/EE_FINGER/EE_FINGER.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 9.3 · 10 |  |
| 84 | `models/rby1m/mujoco/assets/EE_FINGER/EE_FINGER.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 9.3 · 10 |  |
| 84 | `models/rby1t5/mujoco/assets/EE_FINGER/EE_FINGER.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 9.3 · 10 |  |
| 83 | `models/rby1a/mujoco/assets/LINK_9/LINK_9.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.7 · 10 |  |
| 83 | `models/rby1a/mujoco/assets/base/base.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 8 · 10 |  |
| 83 | `models/rby1m/mujoco/assets/LINK_9/LINK_9.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.7 · 10 |  |
| 83 | `models/rby1t5/mujoco/assets/LINK_9/LINK_9.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.7 · 10 |  |
| 83 | `models/rby1t5/mujoco/assets/base/base.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 8 · 10 |  |
| 82 | `models/rby1a/mujoco/assets/LINK_12/LINK_12.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.1 · 10 |  |
| 82 | `models/rby1a/mujoco/assets/LINK_16/LINK_16.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.1 · 10 |  |
| 82 | `models/rby1a/mujoco/assets/LINK_19/LINK_19.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.5 · 10 |  |
| 82 | `models/rby1a/mujoco/assets/LINK_2/LINK_2.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 6.6 · 10 |  |
| 82 | `models/rby1a/mujoco/assets/LINK_3/LINK_3.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.1 · 10 |  |
| 82 | `models/rby1a/mujoco/assets/PAN_TILT_1/PAN_TILT_1.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 6.7 · 10 |  |
| 82 | `models/rby1m/mujoco/assets/LINK_12/LINK_12.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.1 · 10 |  |
| 82 | `models/rby1m/mujoco/assets/LINK_16/LINK_16.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.1 · 10 |  |
| 82 | `models/rby1m/mujoco/assets/LINK_19/LINK_19.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.5 · 10 |  |
| 82 | `models/rby1m/mujoco/assets/LINK_2/LINK_2.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 6.6 · 10 |  |
| 82 | `models/rby1m/mujoco/assets/LINK_3/LINK_3.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.1 · 10 |  |
| 82 | `models/rby1m/mujoco/assets/PAN_TILT_1/PAN_TILT_1.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 6.7 · 10 |  |
| 82 | `models/rby1m/mujoco/assets/base/base.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.3 · 10 |  |
| 82 | `models/rby1t5/mujoco/assets/LINK_12/LINK_12.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.1 · 10 |  |
| 82 | `models/rby1t5/mujoco/assets/LINK_16/LINK_16.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.1 · 10 |  |
| 82 | `models/rby1t5/mujoco/assets/LINK_19/LINK_19.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.5 · 10 |  |
| 82 | `models/rby1t5/mujoco/assets/LINK_2/LINK_2.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 6.6 · 10 |  |
| 82 | `models/rby1t5/mujoco/assets/LINK_3/LINK_3.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 7.1 · 10 |  |
| 82 | `models/rby1t5/mujoco/assets/PAN_TILT_1/PAN_TILT_1.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 6.7 · 10 |  |
| 81 | `models/rby1a/mujoco/assets/EE_BODY/EE_BODY.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 5.6 · 10 |  |
| 81 | `models/rby1a/mujoco/assets/FT_SENSOR_L/FT_SENSOR_L.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 6.3 · 10 |  |
| 81 | `models/rby1a/mujoco/assets/FT_SENSOR_R/FT_SENSOR_R.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 6.3 · 10 |  |
| 81 | `models/rby1a/mujoco/assets/LINK_1/LINK_1.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 6.4 · 10 |  |
| | and 57 more, in `audit.json` | | | |

</details>

<details><summary><b>OpenGalaxea/GalaxeaManipSim</b>: best 94, 15 robot(s), Apache-2.0, last commit 2025-08-18</summary>

From: robot_descriptions.py. Commit `abe7f5161eea`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 94 | `galaxea_sim/assets/r1_lite/robot.urdf` | urdf | 15 · 5 · 20 · 15 · 9.7 · 20 · 9.4 |  |
| 94 | `galaxea_sim/assets/r1_lite/robot_origin.urdf` | urdf | 15 · 5 · 20 · 15 · 9.7 · 20 · 9.4 |  |
| 93 | `galaxea_sim/assets/r1_pro/robot.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 20 · 8.2 |  |
| 93 | `galaxea_sim/assets/r1_pro/robot_origin.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 20 · 8.2 |  |
| 92 | `galaxea_sim/assets/r1/robot.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 20 · 6.6 |  |
| 78 | `galaxea_sim/assets/r1_pro/new_robot.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 8.2 |  |
| 20 | `galaxea_sim/assets/r1/configs/urdfs/r1_v2_1_0.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 34 visual mesh file(s) missing |
| 20 | `galaxea_sim/assets/r1/configs/urdfs/r1_v2_1_0_floating_left.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 11 visual mesh file(s) missing |
| 20 | `galaxea_sim/assets/r1/configs/urdfs/r1_v2_1_0_floating_right.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 11 visual mesh file(s) missing |
| 20 | `galaxea_sim/assets/r1_lite/configs/urdfs/r1lite_floating_left.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 10 visual mesh file(s) missing |
| 20 | `galaxea_sim/assets/r1_lite/configs/urdfs/r1lite_floating_right.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 10 visual mesh file(s) missing |
| 20 | `galaxea_sim/assets/r1_pro/configs/urdfs/r1_pro_left.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |
| 20 | `galaxea_sim/assets/r1_pro/configs/urdfs/r1_pro_right.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |
| 20 | `galaxea_sim/assets/r1_pro/configs/urdfs/r1pro.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 36 visual mesh file(s) missing |
| 20 | `galaxea_sim/assets/r1_pro/meshes/r1_pro_with_gripper.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 36 visual mesh file(s) missing |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/engineai/pm01_description</b>: best 93, 1 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 93 | `humanoid/engineai/pm01_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 19.3 · 3.6 |  |

</details>

<details><summary><b>frankarobotics/franka_ros</b>: best 93, 5 robot(s), Apache-2.0, last commit 2025-10-24</summary>

From: awesome-robot-descriptions. Commit `ddd2fffd9de4`. Also 5 SDF file(s), not measured.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 93 | `franka_gazebo/test/launch/panda-gazebo.urdf` | urdf | 15 · 5 · 20 · 15 · 8.9 · 18.9 · 10 |  |
| 85 | `franka_description/robots/common/hand.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 20 · 10 |  |
| 85 | `franka_description/robots/fr3/fr3.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 20 · 10 |  |
| 85 | `franka_description/robots/panda/panda.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 20 · 10 |  |
| 84 | `franka_description/robots/dual_panda/dual_panda_example.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 19.8 · 9.6 |  |

</details>

<details><summary><b>RobotLocomotion/drake</b>: best 93, 54 robot(s), NOASSERTION, last commit 2026-11-18</summary>

From: robot_descriptions.py. Commit `407526d3e2bd`. Also 89 SDF file(s), not measured.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 93 | `multibody/parsing/test/urdf_parser_test/non_conflicting_materials_2.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 13.3 · 10 |  |
| 90 | `multibody/parsing/test/drake_manifest_resolution_test/cube_visual.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 10 · 10 |  |
| 90 | `multibody/parsing/test/links_with_visuals_and_collisions.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 10 · 10 |  |
| 90 | `multibody/parsing/test/urdf_parser_test/all_geometries_as_visual.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 10 · 10 |  |
| 85 | `examples/kuka_iiwa_arm/models/objects/black_box.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `examples/kuka_iiwa_arm/models/objects/block_for_pick_and_place.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `examples/kuka_iiwa_arm/models/objects/block_for_pick_and_place_large_size.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `examples/kuka_iiwa_arm/models/objects/block_for_pick_and_place_mid_size.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `examples/kuka_iiwa_arm/models/objects/folding_table.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `examples/kuka_iiwa_arm/models/objects/round_table.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `examples/kuka_iiwa_arm/models/objects/simple_cuboid.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `examples/kuka_iiwa_arm/models/objects/simple_cylinder.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `examples/kuka_iiwa_arm/models/objects/yellow_post.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `examples/multibody/strandbeest/model/StrandbeestBushings.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `examples/multibody/strandbeest/model/StrandbeestConstraints.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `examples/pendulum/Pendulum.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `examples/quadrotor/office.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `multibody/benchmarks/free_body/uniform_solid_cylinder.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `multibody/parsing/test/urdf_parser_test/duplicate_but_same_materials_with_texture.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `multibody/parsing/test/urdf_parser_test/non_conflicting_materials_3.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `multibody/parsing/test/urdf_parser_test/zero_dof_robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 82 | `bindings/pydrake/multibody/test/Acrobot_unicode.urdf` | urdf | 15 · 10 · 20 · 15 · 6.7 · 5 · 10 |  |
| 82 | `examples/acrobot/Acrobot.urdf` | urdf | 15 · 10 · 20 · 15 · 6.7 · 5 · 10 |  |
| 82 | `examples/acrobot/Acrobot_no_collision.urdf` | urdf | 15 · 10 · 20 · 15 · 6.7 · 5 · 10 |  |
| 82 | `multibody/parsing/test/box_package/urdfs/box.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 10 · 10 |  |
| 80 | `examples/kuka_iiwa_arm/models/objects/open_top_box.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 10 |  |
| 80 | `multibody/models/box.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 10 |  |
| 80 | `multibody/models/box_small.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 10 |  |
| 80 | `multibody/plant/test/atlas_with_fixed_joints.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0.3 · 10 |  |
| 75 | `multibody/parsing/test/urdf_parser_test/conflicting_materials.urdf` | urdf | 15 · 10 · 20 · 15 · 0 · 5 · 10 |  |
| 75 | `multibody/parsing/test/urdf_parser_test/duplicate_materials.urdf` | urdf | 15 · 10 · 20 · 15 · 0 · 5 · 10 |  |
| 74 | `multibody/parsing/test/urdf_parser_test/non_conflicting_materials_1.urdf` | urdf | 15 · 10 · 20 · 15 · 0 · 3.8 · 10 |  |
| 73 | `multibody/parsing/test/urdf_parser_test/accepting_renderer.urdf` | urdf | 15 · 10 · 20 · 15 · 0 · 3.3 · 10 |  |
| 70 | `multibody/benchmarks/acrobot/acrobot.urdf` | urdf | 15 · 10 · 20 · 0 · 10 · 5 · 10 |  |
| 70 | `multibody/benchmarks/acrobot/acrobot.xml` | mjcf | 15 · 10 · 20 · 0 · 10 · 5 · 10 |  |
| 70 | `multibody/parsing/test/mujoco_parser_test/pendulum.xml` | mjcf | 15 · 10 · 20 · 0 · 10 · 5 · 10 |  |
| 70 | `multibody/parsing/test/urdf_parser_test/all_geometries_as_collision.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 0 |  |
| 60 | `bindings/pydrake/visualization/test/massless_robot.urdf` | urdf | 15 · 10 · 20 · 15 · 0 · 0 · 0 |  |
| 60 | `multibody/benchmarks/acrobot/double_pendulum.urdf` | urdf | 15 · 10 · 20 · 15 · 0 · 0 · 0 |  |
| 60 | `multibody/parsing/test/sdf_parser_test/imported_joint_frames.urdf` | urdf | 15 · 10 · 20 · 15 · 0 · 0 · 0 |  |
| | and 14 more, in `audit.json` | | | |

</details>

<details><summary><b>bulletphysics/bullet3</b>: best 92, 1232 robot(s), NOASSERTION, last commit 2026-10-09</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `d3afe76132fc`. Also 32 SDF file(s), not measured.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 92 | `data/cloth_z_up.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/cube.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/cube_collisionfilter.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/cube_concave.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/cube_convex.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/cube_gripper_left.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/cube_gripper_right.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/cube_no_friction.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/cube_small.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/cube_soft.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/dinnerware/cup/cup_small.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/dinnerware/plate.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/duck_vhacd.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/jenga/jenga.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/kuka_iiwa/model_free_base.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/sphere2.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/sphere2_rolling_friction.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/sphere2red.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/sphere_small.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/sphere_small_zeroinertia.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/sphere_transparent.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/sphere_with_restitution.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/torus/torus.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/torus/torus_with_plane.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/torus/torus_with_separate_plane.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `data/user_data_test_object.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/cloth_z_up.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/cube.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/cube_collisionfilter.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/cube_rotate.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/cube_small.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/domino/domino.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/jenga/jenga.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/laikago/laikago.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/soccerball.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/sphere2.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/sphere2red.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/sphere8cube.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/sphere_small.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `examples/pybullet/gym/pybullet_data/sphere_transparent.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| | and 1192 more, in `audit.json` | | | |

</details>

<details><summary><b>fiveages-sim/fa-s2-description</b>: best 92, 3 robot(s), no licence named, last commit 2026-11-12</summary>

From: fiveages submodules. Commit `91ac627054d3`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 92 | `xacro/component.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 9.3 |  |
| 87 | `xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 8.8 · 20 · 5.3 |  |
| 87 | `xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 8.8 · 20 · 5.3 |  |

</details>

<details><summary><b>fiveages-sim/fa-w1-description</b>: best 92, 4 robot(s), no licence named, last commit 2026-10-10</summary>

From: fiveages submodules. Commit `b0f8b6f649d0`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 92 | `xacro/component.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 90 | `xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.6 · 20 · 7.5 |  |
| 90 | `xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.6 · 20 · 7.5 |  |
| 18 | `xacro/gazebo.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>fiveages-sim/fa-w2-components</b>: best 92, 1 robot(s), no licence named, last commit 2026-10-21</summary>

From: fiveages submodules. Commit `78c595884616`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 92 | `xacro/component.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 9.3 |  |

</details>

<details><summary><b>fiveages-sim/fa-w2-description</b>: best 92, 3 robot(s), no licence named, last commit 2026-11-12</summary>

From: fiveages submodules. Commit `812e1615b922`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 92 | `xacro/component.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 9.3 |  |
| 82 | `xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 6.7 · 20 · 2.5 |  |
| 82 | `xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 6.7 · 20 · 2.5 |  |

</details>

<details><summary><b>fiveages-sim/robot-descriptions-ht</b>: best 92, 4 robot(s), no licence named, last commit 2026-11-16</summary>

From: fiveages submodules. Commit `4b7810f95bb5`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 92 | `panthera_ht_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 9.9 |  |
| 92 | `panthera_ht_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 9.9 |  |
| 91 | `openarm_ht_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 8.5 |  |
| 91 | `openarm_ht_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 8.5 |  |

</details>

<details><summary><b>fiveages-sim/robot-descriptions-rokae</b>: best 92, 4 robot(s), no licence named, last commit 2026-11-19</summary>

From: fiveages submodules. Commit `e5cca775371d`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 92 | `ar5_srs_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.4 · 20 · 9.7 |  |
| 92 | `ar5_srs_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.4 · 20 · 9.7 |  |
| 90 | `ar5_ccs_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.4 · 20 · 8.6 |  |
| 90 | `ar5_ccs_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.4 · 20 · 8.6 |  |

</details>

<details><summary><b>fiveages-sim/robot-descriptions-tianji</b>: best 92, 13 robot(s), no licence named, last commit 2026-11-16</summary>

From: fiveages submodules. Commit `9bca827ae4c6`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 92 | `m6_srs_description/urdf/m6_srs.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `m6_srs_description/urdf/m6_srs_right.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `m6_srs_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `m6_srs_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `marvin_pro_description/xacro/component.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 91 | `m20s_ccs_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.4 · 20 · 9.4 |  |
| 91 | `m20s_ccs_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.4 · 20 · 9.4 |  |
| 91 | `m6_ccs_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.4 · 20 · 9.3 |  |
| 91 | `m6_ccs_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.4 · 20 · 9.3 |  |
| 90 | `m6s_lite_ccs_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.3 · 20 · 8.7 |  |
| 90 | `m6s_lite_ccs_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 9.3 · 20 · 8.7 |  |
| 87 | `marvin_pro_description/xacro/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 7.7 · 20 · 6.7 |  |
| 87 | `marvin_pro_description/xacro/ros2_control/robot.xacro` | xacro | 7.5 · 10 · 20 · 15 · 7.7 · 20 · 6.7 |  |

</details>

<details><summary><b>google-deepmind/mujoco_menagerie</b>: best 92, 131 robot(s), NOASSERTION, last commit 2026-11-10</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `370c43965323`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 92 | `flexiv_rizon4/assets/link0/link0.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `flexiv_rizon4/assets/link1/link1.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `flexiv_rizon4/assets/link2/link2.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `flexiv_rizon4/assets/link3/link3.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `flexiv_rizon4/assets/link5/link5.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `flexiv_rizon4/assets/link6/link6.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `flexiv_rizon4/assets/link7/link7.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `flexiv_rizon4/flexiv_rizon4.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 19.3 · 10 |  |
| 92 | `flexiv_rizon4s/flexiv_rizon4s.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 19.3 · 10 |  |
| 92 | `realsense_d435i/d435i.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 20 · 9.2 |  |
| 92 | `rethink_robotics_sawyer/sawyer.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 19.1 · 10 |  |
| 90 | `rainbow_robotics_rby1/rby1a_1.2.xml` | mjcf | 7.5 · 10 · 20 · 13.9 · 10 · 19.3 · 9.8 |  |
| 90 | `rainbow_robotics_rby1/rby1a_1.2_no_gripper.xml` | mjcf | 7.5 · 10 · 20 · 13.8 · 10 · 19.2 · 9.9 |  |
| 89 | `agilex_piper/piper.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 17.3 · 8.8 |  |
| 89 | `franka_emika_panda/mjx_panda_nohand.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 16.6 · 10 |  |
| 89 | `franka_emika_panda/panda_nohand.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 16.6 · 10 |  |
| 89 | `universal_robots_ur10e/ur10e.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 16.9 · 10 |  |
| 89 | `universal_robots_ur5e/ur5e.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 16.9 · 10 |  |
| 88 | `boston_dynamics_spot/spot.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 15.8 · 10 |  |
| 88 | `flexiv_rizon4/assets/link4/link4.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 15 · 10 |  |
| 88 | `franka_emika_panda/mjx_panda.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 15.9 · 10 |  |
| 88 | `franka_emika_panda/mjx_single_cube.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 15.9 · 10 |  |
| 88 | `franka_emika_panda/panda.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 15.9 · 10 |  |
| 88 | `franka_fr3/fr3.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 15.6 · 9.8 |  |
| 88 | `franka_fr3_v2/fr3v2.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 15.6 · 9.7 |  |
| 88 | `rainbow_robotics_rby1/rby1m_1.2.xml` | mjcf | 7.5 · 10 · 20 · 13 · 10 · 19.4 · 8.5 |  |
| 88 | `rainbow_robotics_rby1/rby1m_1.2_no_gripper.xml` | mjcf | 7.5 · 10 · 20 · 12.7 · 10 · 19.3 · 8.6 |  |
| 87 | `boston_dynamics_spot/spot_arm.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 14.9 · 10 |  |
| 87 | `franka_emika_panda/hand.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 14.2 · 10 |  |
| 87 | `franka_emika_panda/mjx_hand.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 14.4 · 10 |  |
| 87 | `pndbotics_adam_lite/adam_lite.xml` | mjcf | 7.5 · 10 · 20 · 13.8 · 10 · 18.6 · 7.2 |  |
| 87 | `trossen_wxai/wxai_follower.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 14.9 · 10 |  |
| 87 | `trossen_wxai/wxai_follower_biarm.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 14.9 · 10 |  |
| 87 | `unitree_go2/go2.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 15.9 · 8.9 |  |
| 87 | `unitree_go2/go2_mjx.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 15.9 · 8.9 |  |
| 86 | `arx_l5/arx_l5.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 14 · 10 |  |
| 85 | `flybody/fruitfly.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 15 · 7.9 |  |
| 85 | `franka_fr3_duo/fr3_duo.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 16.5 · 6.2 |  |
| 85 | `franka_fr3_duo/fr3_duo_with_spine.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 16.4 · 6.1 |  |
| 85 | `hello_robot_stretch/scene.xml` | mjcf | 7.5 · 10 · 20 · 9.7 · 10 · 18.7 · 8.7 |  |
| | and 91 more, in `audit.json` | | | |

</details>

<details><summary><b>jrl-umi3218/pepper_description</b>: best 92, 1 robot(s), BSD-2-Clause, last commit 2024-03-15</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `b953b44c3993`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 92 | `urdf/pepper.urdf` | urdf | 15 · 5 · 20 · 15 · 9 · 18.5 · 9.8 |  |

</details>

<details><summary><b>nickswalker/robotiq-2f-85</b>: best 92, 2 robot(s), BSD-2-Clause, last commit 2026-04-30</summary>

From: robot_descriptions.py. Commit `5f5178e69c13`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 92 | `robotiq_2f_85_gripper_gazebo/urdf/robotiq_arg2f_85.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 11.8 · 10 |  |
| 92 | `robotiq_2f_85_gripper_visualization/urdf/robotiq_arg2f_85.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 11.8 · 10 |  |

</details>

<details><summary><b>RobotLocomotion/models</b>: best 92, 44 robot(s), no licence named, last commit 2026-11-05</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `a7ba22fa4f54`. Also 45 SDF file(s), not measured.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 92 | `allegro_hand_description/urdf/allegro_hand_description_left.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `allegro_hand_description/urdf/allegro_hand_description_right.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `dishes/evo_bowl_compliant.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `franka_description/urdf/hand.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `franka_description/urdf/panda_arm_hand.urdf` | urdf | 7.5 · 10 · 20 · 15 · 9.2 · 20 · 10 |  |
| 92 | `franka_description/urdf/panda_hand.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `iiwa_description/urdf/dual_iiwa14_polytope_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `iiwa_description/urdf/iiwa14_no_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `iiwa_description/urdf/iiwa14_polytope_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `iiwa_description/urdf/iiwa14_primitive_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `iiwa_description/urdf/iiwa14_spheres_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `iiwa_description/urdf/iiwa14_spheres_dense_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `iiwa_description/urdf/iiwa14_spheres_dense_elbow_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `iiwa_description/urdf/planar_iiwa14_spheres_dense_elbow_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `jaco_description/urdf/j2n6s300.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `skydio_2/quadrotor.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `tri_homecart/homecart_bimanual.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `tri_homecart/homecart_bimanual.urdf.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `ur_description/urdf/ur3e_cylinders_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `ur_description/urdf/ur3e_cylinders_collision.urdf.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `ur_description/urdf/ur3e_spheres_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 92 | `ur_description/urdf/ur3e_spheres_collision.urdf.xacro` | xacro | 7.5 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 91 | `franka_description/urdf/panda_arm.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8.9 · 20 · 10 |  |
| 91 | `franka_description/urdf/panda_arm_hand_link5split.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8.5 · 20 · 10 |  |
| 91 | `jaco_description/urdf/j2s7s300_arm.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8.8 · 19.3 · 10 |  |
| 91 | `jaco_description/urdf/j2s7s300_arm_sphere_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8.9 · 19.3 · 10 |  |
| 90 | `franka_description/urdf/panda_arm_link5split.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8 · 20 · 10 |  |
| 90 | `jaco_description/urdf/j2s7s300.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8.8 · 19.1 · 10 |  |
| 90 | `jaco_description/urdf/j2s7s300_hand.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8.8 · 18.9 · 10 |  |
| 90 | `jaco_description/urdf/j2s7s300_hand_sphere_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8.8 · 18.9 · 10 |  |
| 90 | `jaco_description/urdf/j2s7s300_sphere_collision.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8.8 · 19.1 · 10 |  |
| 88 | `atlas/atlas_convex_hull.urdf` | urdf | 7.5 · 10 · 20 · 15 · 9.4 · 16.2 · 10 |  |
| 88 | `atlas/atlas_minimal_contact.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 16 · 10 |  |
| 82 | `realsense2_description/urdf/d415.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 10 · 10 |  |
| 79 | `pr2_description/urdf/pr2_simplified.urdf` | urdf | 7.5 · 10 · 20 · 13.8 · 10 · 7.9 · 10 |  |
| 78 | `dishes/table_top.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 78 | `jaco_description/urdf/j2n6s300_col.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 18 | `iiwa_description/urdf/dual_iiwa14_polytope_collision.urdf.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: Invalid parameter "collision_type" |
| 18 | `iiwa_description/urdf/iiwa14.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 18 | `iiwa_description/urdf/iiwa14_polytope_collision.urdf.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: Invalid parameter "collision_type" |
| | and 4 more, in `audit.json` | | | |

</details>

<details><summary><b>psyonicinc/ability-hand-api</b>: best 91, 26 robot(s), MIT, last commit 2026-11-16</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `26ca07956df2`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 91 | `python/ah_simulators/mujoco_xml/franka_fr3/fr3.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 11.4 · 9.5 |  |
| 91 | `python/ah_simulators/mujoco_xml/universal_robots_ur10e/ur10e.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 10.8 · 10 |  |
| 91 | `python/ah_simulators/mujoco_xml/universal_robots_ur5e/ur5e.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 10.8 · 10 |  |
| 85 | `python/ah_simulators/mujoco_xml/ufactory_xarm7/hand.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `python/ah_simulators/mujoco_xml/ufactory_xarm7/xarm7.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `python/ah_simulators/mujoco_xml/ufactory_xarm7/xarm7_abilityhand.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 83 | `python/ah_simulators/mujoco_xml/unitree_z1/scene.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 3.3 · 10 |  |
| 83 | `python/ah_simulators/mujoco_xml/unitree_z1/z1.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 3 · 10 |  |
| 82 | `python/ah_simulators/mujoco_xml/unitree_h1/h1.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 3 · 9.2 |  |
| 81 | `python/ah_simulators/mujoco_xml/unitree_g1/g1.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 3.8 · 7.5 |  |
| 80 | `URDF/ability_hand_left_large.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 10 |  |
| 80 | `URDF/ability_hand_left_small.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 10 |  |
| 80 | `URDF/ability_hand_right_large.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 10 |  |
| 80 | `URDF/ability_hand_right_large_no_fsr.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 10 |  |
| 80 | `URDF/ability_hand_right_small.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 10 |  |
| 80 | `python/ah_simulators/mujoco_xml/unitree_z1/z1_gripper.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 0 · 9.7 |  |
| 77 | `python/ah_simulators/mujoco_xml/apptronik_apollo/apptronik_apollo.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 2.4 |  |
| 77 | `python/ah_simulators/mujoco_xml/unitree_g1/g1_with_hands.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 2.5 · 4.7 |  |
| 25 | `python/ah_simulators/mujoco_xml/franka_fr3/hands/abh_left_large.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 6 visual mesh file(s) missing |
| 25 | `python/ah_simulators/mujoco_xml/franka_fr3/hands/abh_left_small.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 6 visual mesh file(s) missing |
| 25 | `python/ah_simulators/mujoco_xml/franka_fr3/hands/abh_right_large.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 6 visual mesh file(s) missing |
| 25 | `python/ah_simulators/mujoco_xml/franka_fr3/hands/abh_right_small.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 6 visual mesh file(s) missing |
| 25 | `python/ah_simulators/mujoco_xml/hands/abh_left_large.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |
| 25 | `python/ah_simulators/mujoco_xml/hands/abh_left_small.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 11 visual mesh file(s) missing |
| 25 | `python/ah_simulators/mujoco_xml/hands/abh_right_large.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |
| 25 | `python/ah_simulators/mujoco_xml/hands/abh_right_small.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 11 visual mesh file(s) missing |

</details>

<details><summary><b>timqian/bambot</b>: best 91, 6 robot(s), Apache-2.0, last commit 2025-07-14</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `eba23eb2f4db`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 91 | `website/public/URDFs/unitree-go2/go2.urdf` | urdf | 15 · 5 · 20 · 15 · 7 · 20 · 8.9 |  |
| 79 | `website/public/URDFs/so101.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 8.9 |  |
| 79 | `website/public/URDFs/unitree-g1/g1_23dof.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 8.9 |  |
| 75 | `website/public/URDFs/sts3215.urdf` | urdf | 15 · 5 · 20 · 15 · 5 · 5 · 10 |  |
| 67 | `website/public/URDFs/bambot_v0.urdf` | urdf | 15 · 5 · 20 · 15 · 6.7 · 5 · 0 |  |
| 65 | `website/public/URDFs/bambot_v0_base.urdf` | urdf | 15 · 5 · 20 · 15 · 0 · 5 · 4.7 |  |

</details>

<details><summary><b>Derek-TH-Wang/mini_cheetah_urdf</b>: best 90, 6 robot(s), no licence named, last commit 2021-02-02</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `1988bceb26e8`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 90 | `urdf/laikago.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 88 | `urdf/laikago_toes.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 17.7 · 10 |  |
| 88 | `urdf/laikago_toes_limits.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 17.7 · 10 |  |
| 88 | `urdf/laikago_toes_zup.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 17.7 · 10 |  |
| 82 | `urdf/quadruped_robot.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 12.3 · 10 |  |
| 15 | `urdf/mini_cheetah.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 4 visual mesh file(s) missing |

</details>

<details><summary><b>facebookresearch/differentiable-robot-model</b>: best 90, 13 robot(s), MIT, last commit 2022-04-22 **archived**</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `d7bd1b3b8ef1`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 90 | `diff_robot_data/fetch_description/urdf/fetch_arm_no_gripper.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 90 | `diff_robot_data/fetch_description/urdf/fetch_arm_no_gripper_small_damping.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 90 | `diff_robot_data/kinova_description/urdf/jaco.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 90 | `diff_robot_data/kinova_description/urdf/jaco_clean.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 75 | `diff_robot_data/2link_robot.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 5 · 10 |  |
| 72 | `diff_robot_data/allegro/urdf/allegro_hand_description_left.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 1.7 · 10 |  |
| 72 | `diff_robot_data/allegro/urdf/allegro_hand_description_left_small_damping.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 1.7 · 10 |  |
| 15 | `diff_robot_data/kuka_iiwa/urdf/iiwa7.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 8 visual mesh file(s) missing |
| 15 | `diff_robot_data/kuka_iiwa/urdf/iiwa7_allegro.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 8 visual mesh file(s) missing |
| 15 | `diff_robot_data/panda_description/urdf/panda.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 10 visual mesh file(s) missing |
| 15 | `diff_robot_data/panda_description/urdf/panda_no_gripper.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 8 visual mesh file(s) missing |
| 15 | `diff_robot_data/trifinger_edu_description/trifinger_edu.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |
| 15 | `examples/jaco.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 10 visual mesh file(s) missing |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/ai2robotics/ai2_bot2_description</b>: best 90, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 90 | `humanoid/ai2robotics/ai2_bot2_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 5.8 · 19.8 · 4.9 |  |
| 90 | `humanoid/ai2robotics/ai2_bot2_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 5.8 · 19.8 · 4.9 |  |
| 90 | `humanoid/ai2robotics/ai2_bot2_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 5.8 · 19.8 · 4.9 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/x2robot/quanta_x1_description</b>: best 90, 4 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 90 | `humanoid/x2robot/quanta_x1_description/xacro/component.xacro` | xacro | 15 · 10 · 20 · 15 · 3.8 · 20 · 6.4 |  |
| 87 | `humanoid/x2robot/quanta_x1_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 6.1 · 19.8 · 0.7 |  |
| 25 | `humanoid/x2robot/quanta_x1_description/urdf/ex001_robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 44 visual mesh file(s) missing |
| 25 | `humanoid/x2robot/quanta_x1_description/urdf/ex001_robot_mock.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 44 visual mesh file(s) missing |

</details>

<details><summary><b>gundam-global-challenge/gundam_robot</b>: best 90, 1 robot(s), no licence named, last commit 2020-08-28</summary>

From: awesome-robot-descriptions. Commit `411d5db72a12`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 90 | `gundam_rx78_description/urdf/GGC_TestModel_rx78_20170112.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |

</details>

<details><summary><b>Kinovarobotics/kinova-ros</b>: best 90, 13 robot(s), BSD-3-Clause, last commit 2023-02-01</summary>

From: robot_descriptions.py. Commit `924781d3dfe2`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 90 | `kinova_description/urdf/j2n4s300_standalone.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 90 | `kinova_description/urdf/j2n6s200_standalone.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 19.7 · 10 |  |
| 90 | `kinova_description/urdf/j2n6s300_standalone.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 90 | `kinova_description/urdf/j2n7s300_standalone.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 19.5 · 10 |  |
| 90 | `kinova_description/urdf/j2s6s300_integration.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 19.5 · 10 |  |
| 90 | `kinova_description/urdf/j2s6s300_standalone.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 19.5 · 10 |  |
| 90 | `kinova_description/urdf/m1n6s300_standalone.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 19.5 · 10 |  |
| 89 | `kinova_description/urdf/j2s6s200_integration.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 19.1 · 10 |  |
| 89 | `kinova_description/urdf/j2s6s200_standalone.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 19.1 · 10 |  |
| 89 | `kinova_description/urdf/j2s7s300_standalone.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 19.1 · 10 |  |
| 89 | `kinova_description/urdf/m1n4s200_standalone.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 18.9 · 10 |  |
| 89 | `kinova_description/urdf/m1n6s200_standalone.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 19.1 · 10 |  |
| 89 | `kinova_description/urdf/two_arm_robot_example_standalone.xacro` | xacro | 15 · 0 · 20 · 15 · 9.6 · 19.7 · 10 |  |

</details>

<details><summary><b>RethinkRobotics/baxter_common</b>: best 90, 10 robot(s), BSD-3-Clause, last commit 2015-12-30</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `6c4b0f375fe4`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 90 | `baxter_description/urdf/left_end_effector.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 90 | `baxter_description/urdf/pedestal/pedestal.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 90 | `baxter_description/urdf/right_end_effector.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 90 | `rethink_ee_description/urdf/electric_gripper/example_end_effector.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 87 | `baxter_description/urdf/baxter.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 17.8 · 8.9 |  |
| 87 | `baxter_description/urdf/baxter.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 18.7 · 8.6 |  |
| 87 | `baxter_description/urdf/baxter_base/baxter_base.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 18.1 · 9.3 |  |
| 50 | `rethink_ee_description/urdf/null_gripper/example_end_effector.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 0 · 0 · 0 |  |
| 15 | `baxter_description/urdf/baxter_base/baxter_base.gazebo.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `rethink_ee_description/urdf/pneumatic_gripper/example_end_effector.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: rethink_ee_description/urdf/electric_gripper/rethink_pneumatic_gripper.xacro &#91;Errno 2&#93; No such file or directory: 'rethink_ee |

</details>

<details><summary><b>robot-descriptions/jvrc_description</b>: best 90, 1 robot(s), BSD-2-Clause, last commit 2025-01-09 **archived**</summary>

From: awesome-robot-descriptions. Commit `704b766e0e62`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 90 | `urdf/jvrc1.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |

</details>

<details><summary><b>whoenig/crazyflie_ros</b>: best 90, 2 robot(s), MIT, last commit 2021-08-03 **archived**</summary>

From: awesome-robot-descriptions. Commit `df3ce76f7009`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 90 | `crazyflie_description/urdf/crazyflie.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 90 | `crazyflie_description/urdf/crazyflie2.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 20 · 10 |  |

</details>

<details><summary><b>ros-industrial-attic/robotiq</b>: best 89, 9 robot(s), BSD-2-Clause, last commit 2021-05-28</summary>

From: awesome-robot-descriptions. Commit `45196f6558fe`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 89 | `robotiq_3f_gripper_visualization/cfg/robotiq-3f-gripper_articulated.xacro` | xacro | 15 · 0 · 20 · 15 · 9.2 · 20 · 10 |  |
| 80 | `robotiq_2f_c2_gripper_visualization/urdf/robotiq_c2_model.urdf` | urdf | 15 · 0 · 20 · 15 · 0 · 20 · 10 |  |
| 80 | `robotiq_2f_c2_gripper_visualization/urdf/robotiq_c2_model.xacro` | xacro | 15 · 0 · 20 · 15 · 0 · 20 · 10 |  |
| 79 | `robotiq_2f_85_gripper_visualization/urdf/robotiq_arg2f_85_model.xacro` | xacro | 15 · 0 · 20 · 15 · 0.9 · 18.2 · 10 |  |
| 73 | `robotiq_2f_140_gripper_visualization/urdf/robotiq_arg2f_140_model.xacro` | xacro | 15 · 0 · 20 · 15 · 8.2 · 5 · 10 |  |
| 70 | `robotiq_ft_sensor/urdf/examples_of_macros/example_use_robotiq_ft300.xacro` | xacro | 15 · 0 · 20 · 15 · 5 · 5 · 10 |  |
| 61 | `robotiq_3f_gripper_visualization/cfg/robotiq-3f-gripper_mesh.urdf` | urdf | 15 · 0 · 20 · 15 · 0 · 1.2 · 10 |  |
| 61 | `robotiq_3f_gripper_visualization/cfg/robotiq-3f-gripper_mesh.xacro` | xacro | 15 · 0 · 20 · 15 · 0 · 1.2 · 10 |  |
| 15 | `robotiq_3f_gripper_visualization/cfg/robotiq-3f-gripper_articulated.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |

</details>

<details><summary><b>isri-aist/jvrc_mj_description</b>: best 88, 1 robot(s), BSD-2-Clause, last commit 2026-03-24</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `8cfc65f5c579`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 88 | `xml/jvrc1.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 7.9 · 10 |  |

</details>

<details><summary><b>RethinkRobotics/sawyer_robot</b>: best 88, 4 robot(s), Apache-2.0, last commit 2020-01-06</summary>

From: awesome-robot-descriptions. Commit `d1ef3d0ca83d`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 88 | `sawyer_description/urdf/sawyer.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 8.9 · 18.8 · 9.8 |  |
| 88 | `sawyer_description/urdf/sawyer_base.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 8.9 · 18.8 · 9.8 |  |
| 50 | `sawyer_description/urdf/sawyer_base.gazebo.xacro` | xacro | 15 · 0 · 20 · 15 · 0 · 0 · 0 |  |
| 15 | `sawyer_description/urdf/sawyer_electric_gripper.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: intera_tools_description Package not found: intera_tools_description |

</details>

<details><summary><b>tork-a/rtmros_nextage</b>: best 88, 6 robot(s), no licence named, last commit 2025-05-09</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `5fe35ea32825`. Also 3 SDF file(s), not measured.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 88 | `nextage_calibration/models/checkerboard_horizontal.urdf` | urdf | 7.5 · 5 · 20 · 15 · 10 · 20 · 10 |  |
| 88 | `nextage_calibration/models/checkerboard_waist.urdf` | urdf | 7.5 · 5 · 20 · 15 · 10 · 20 · 10 |  |
| 88 | `nextage_description/urdf/NextageOpen.urdf` | urdf | 7.5 · 5 · 20 · 15 · 10 · 20 · 10 |  |
| 86 | `nextage_description/urdf/nxo_gz.xacro` | xacro | 7.5 · 5 · 20 · 15 · 10 · 18.9 · 10 |  |
| 12 | `nextage_calibration/models/sensor_kinect.xacro` | xacro | 7.5 · 5 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: turtlebot_description Package not found: turtlebot_description |
| 12 | `nextage_description/urdf/materials.urdf.xacro` | xacro | 7.5 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>david-dorf/perseverance-ingenuity-urdfs</b>: best 86, 2 robot(s), Apache-2.0, last commit 2025-02-21</summary>

From: awesome-robot-descriptions. Commit `17b93151ff60`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 86 | `ingenuity/ingenuity.urdf` | urdf | 15 · 5 · 20 · 15 · 1.4 · 20 · 9.8 |  |
| 73 | `perseverance/perseverance.urdf` | urdf | 15 · 5 · 20 · 15 · 0 · 10 · 8.1 |  |

</details>

<details><summary><b>ADVRHumanoids/iit-dagana-ros-pkg</b>: best 85, 2 robot(s), Apache-2.0, last commit 2026-04-13</summary>

From: awesome-robot-descriptions. Commit `6254f2dd3332`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 85 | `dagana_urdf/urdf/dagana.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 25 | `dagana_urdf/urdf/config/dagana_config.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>ankurhanda/robot-assets</b>: best 85, 51 robot(s), no licence named, last commit 2026-04-10</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `24b61c71c07e`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 85 | `urdfs/robots/franka_panda/panda.urdf` | urdf | 0 · 10 · 20 · 15 · 10 · 20 · 10 |  |
| 84 | `urdfs/robots/kuka_iiwa/model.urdf` | urdf | 0 · 10 · 20 · 15 · 8.8 · 20 · 10 |  |
| 84 | `urdfs/robots/ur10/ur10_robot.urdf` | urdf | 0 · 10 · 20 · 15 · 8.8 · 20 · 10 |  |
| 82 | `urdfs/robots/kinova/kinova.urdf` | urdf | 0 · 10 · 20 · 15 · 8.5 · 18.2 · 10 |  |
| 81 | `urdfs/robots/anymal/anymal.urdf` | urdf | 0 · 10 · 20 · 15 · 7.6 · 20 · 8.4 |  |
| 81 | `urdfs/robots/ur5/ur5_gripper.urdf` | urdf | 0 · 10 · 20 · 15 · 7.8 · 18.5 · 10 |  |
| 74 | `urdfs/robots/pr2/pr2.urdf` | urdf | 0 · 10 · 20 · 15 · 10 · 9.3 · 10 |  |
| 70 | `urdfs/asset_store/kitchen/kitchen.urdf` | urdf | 0 · 10 · 20 · 15 · 9.7 · 4.9 · 10 |  |
| 70 | `urdfs/robots/robotiq_gripper/robotiq_arg85_description.URDF` | urdf | 0 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 69 | `urdfs/robots/ginger_robot/gingerurdf.urdf` | urdf | 0 · 10 · 20 · 15 · 10 · 5 · 9.1 |  |
| 10 | `urdfs/asset_store/fork/fork.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 10 | `urdfs/robots/barret_hand/bhand_model.URDF` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 9 visual mesh file(s) missing |
| 10 | `urdfs/robots/halodi/eve_r3.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 9 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2_left_forearm.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 8 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2_left_gripper.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 2 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2b.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 32 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2b_control.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 30 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2b_dynamics.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 21 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2b_sim_upperbody_control.urdf.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 25 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2b_sim_upperbody_dynamics.urdf.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 16 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c1.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 32 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c1_control.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 30 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c1_dynamics.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 21 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c5.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 28 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c5_control.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 25 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c5_dynamics.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 16 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c6.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 32 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c6_control.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 30 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c6_dynamics.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 21 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c6_valve.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 32 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c_sim_full_control.urdf.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 30 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c_sim_full_dynamics.urdf.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 21 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c_sim_legs_control.urdf.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c_sim_legs_dynamics.urdf.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c_sim_upperbody_control.urdf.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 25 visual mesh file(s) missing |
| 10 | `urdfs/robots/r2_description/robots/r2c_sim_upperbody_dynamics.urdf.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 16 visual mesh file(s) missing |
| 10 | `urdfs/robots/val_description/model/robots/forearm_left.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 16 visual mesh file(s) missing |
| 10 | `urdfs/robots/val_description/model/robots/forearm_right.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 16 visual mesh file(s) missing |
| 10 | `urdfs/robots/val_description/model/robots/valkyrie_A.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 55 visual mesh file(s) missing |
| 10 | `urdfs/robots/val_description/model/robots/valkyrie_A_arm_mass_sims.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 23 visual mesh file(s) missing |
| | and 11 more, in `audit.json` | | | |

</details>

<details><summary><b>G-Levine/pupper_v3_description</b>: best 85, 24 robot(s), MIT, last commit 2024-11-08</summary>

From: awesome-robot-descriptions. Commit `1a3c8590189d`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 85 | `description/urdf/pupper_v3.edited.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 10 · 10 |  |
| 77 | `description/mujoco_xml/model_with_obstacles.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 1.8 · 10 |  |
| 76 | `description/mujoco_xml/pupper_v3_complete.backlash.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0.5 · 10 |  |
| 76 | `description/mujoco_xml/pupper_v3_complete.mjx.position.feet_only.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0.5 · 10 |  |
| 75 | `description/mujoco_xml/exported_mjmodel.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0 · 10 |  |
| 75 | `description/mujoco_xml/hfield_mjx_model_for_baruch.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0.2 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.fixed_base.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.mjx.fixed_base.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.mjx.position.feet_only.no_plane.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0.3 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.mjx.position.fixed_base.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.mjx.position.no_body.self_collision.two_iterations.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0.4 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.mjx.position.no_body.self_collision.weak.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.mjx.position.no_body.self_collision.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0.4 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.mjx.position.no_body.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.mjx.position.no_ground.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0.2 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.mjx.position.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0.4 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.mjx.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0.4 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.position.fixed_base.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.position.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0.4 · 10 |  |
| 75 | `description/mujoco_xml/pupper_v3_complete.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 0.4 · 10 |  |
| 75 | `description/pupper_v3.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 0 · 10 |  |
| 75 | `description/urdf/pupper_v3.edited.fixed.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 0 · 10 |  |
| 20 | `description/pupper_v3_mujoco.urdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |
| 20 | `description/urdf/pupper_v3.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |

</details>

<details><summary><b>i2rt-robotics/i2rt</b>: best 85, 30 robot(s), MIT, last commit 2026-11-16</summary>

From: robot_descriptions.py. Commit `234d895b3e54`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 85 | `i2rt/robot_models/arm/big_yam/v1/big_yam.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 9.6 |  |
| 85 | `i2rt/robot_models/arm/big_yam/v1/big_yam.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/arm/yam/v1/yam.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/arm/yam/v1/yam.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/arm/yam_7dof_left/v1/yam_7dof_left.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/arm/yam_7dof_left/v1/yam_7dof_left.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/arm/yam_7dof_right/v1/yam_7dof_right.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/arm/yam_7dof_right/v1/yam_7dof_right.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/arm/yam_pro/v1/yam_pro.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/arm/yam_pro/v1/yam_pro.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/arm/yam_ultra/v2/yam_ultra.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/arm/yam_ultra/v2/yam_ultra.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/gripper/crank_4310/crank_4310.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/gripper/flexible_4310/flexible_4310.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/gripper/flexible_4310/flexible_4310.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/gripper/linear_3507/linear_3507.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/gripper/linear_4310/linear_4310.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/gripper/yam_teaching_handle/v1/yam_teaching_handle.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/gripper/yam_teaching_handle/v2/yam_teaching_handle.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/linearbot/linearbot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `i2rt/robot_models/station/yam_station_crank_4310_d405/yam_station_crank_4310_d405.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 9.8 |  |
| 85 | `i2rt/robot_models/station/yam_station_crank_4310_d405/yam_station_crank_4310_d405.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 9.8 |  |
| 84 | `i2rt/robot_models/arm/yam_ultra/v1/yam_ultra.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 9.2 |  |
| 84 | `i2rt/robot_models/station/yam_station_linear_4310_d405/yam_station_linear_4310_d405.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 9.3 |  |
| 84 | `i2rt/robot_models/station/yam_station_linear_4310_d405/yam_station_linear_4310_d405.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 9.3 |  |
| 84 | `i2rt/robot_models/station/yambox_linear_4310_d405_decxin/yambox_linear_4310_d405_decxin.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 9.2 |  |
| 84 | `i2rt/robot_models/station/yambox_linear_4310_d405_decxin/yambox_linear_4310_d405_decxin.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 9.2 |  |
| 82 | `i2rt/robot_models/arm/yam_ultra/v1/yam_ultra.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 7.5 |  |
| 72 | `i2rt/robot_models/linearbot/linearbot.xml` | mjcf | 15 · 10 · 20 · 1.7 · 10 · 5 · 10 |  |
| 60 | `i2rt/robot_models/gripper/no_gripper/no_gripper.xml` | mjcf | 15 · 10 · 20 · 15 · 0 · 0 · 0 |  |

</details>

<details><summary><b>Kinovarobotics/ros_kortex</b>: best 85, 25 robot(s), NOASSERTION, last commit 2025-09-29</summary>

From: awesome-robot-descriptions. Commit `c3280d8a6a6b`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 85 | `kortex_description/robots/gen3_robotiq_2f_85.xacro` | xacro | 15 · 5 · 20 · 15 · 8.9 · 11.3 · 10 |  |
| 80 | `kortex_description/arms/gen3/6dof/urdf/GEN3-6DOF_NO-VISION_URDF_ARM_V01.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `kortex_description/arms/gen3/6dof/urdf/GEN3-6DOF_VISION_URDF_ARM_V01.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `kortex_description/arms/gen3/7dof/urdf/GEN3-7DOF-NOVISION_FOR_URDF_ARM_V12.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `kortex_description/arms/gen3/7dof/urdf/GEN3-7DOF-VISION_ARM_URDF_V12.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `kortex_description/arms/gen3/7dof/urdf/GEN3-7DOF_BRAKES_NO-VISION_URDF_ARM_V01.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `kortex_description/arms/gen3/7dof/urdf/GEN3-7DOF_BRAKES_VISION_URDF_ARM_V01.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `kortex_description/robots/gen3.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `kortex_description/robots/gen3.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `kortex_description/robots/gen3_lite_gen3_lite_2f.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `kortex_move_it_config/gen3_6dof_dual_arm_move_it_config/config/gazebo_dual_robot.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 9.9 |  |
| 80 | `kortex_move_it_config/gen3_7dof_dual_arm_move_it_config/config/gazebo_dual_robot.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 79 | `kortex_description/robots/gen3_robotiq_2f_140.xacro` | xacro | 15 · 5 · 20 · 15 · 8.9 · 5 · 10 |  |
| 20 | `kortex_description/arms/gen3/6dof/urdf/GEN3-6DOF_BRAKES_NO-VISION_URDF_ARM_V01.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 20 | `kortex_description/arms/gen3/6dof/urdf/GEN3-6DOF_BRAKES_VISION_URDF_ARM_V01.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 20 | `kortex_description/arms/gen3_lite/6dof/urdf/GEN3-LITE.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 6 visual mesh file(s) missing |
| 20 | `kortex_description/grippers/gen3_lite_2f/urdf/GEN3-LITE-GRIPPER_URDF_SIMPLIFIED_V2.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 20 | `kortex_description/multiple_robots/kortex_dual_robots.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: kortex_description/arms//dof/urdf/_macro.xacro &#91;Errno 2&#93; No such file or directory: 'kortex_description/arms//dof/urdf/_macro.xacro' |
| 20 | `kortex_move_it_config/gen3_lite_gen3_lite_2f_move_it_config/config/gen3_lite_gen3_lite_2f.srdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 20 | `kortex_move_it_config/gen3_move_it_config/config/6dof/gen3.srdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 20 | `kortex_move_it_config/gen3_move_it_config/config/7dof/gen3.srdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 20 | `kortex_move_it_config/gen3_robotiq_2f_140_move_it_config/config/6dof/gen3_robotiq_2f_140.srdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 20 | `kortex_move_it_config/gen3_robotiq_2f_140_move_it_config/config/7dof/gen3_robotiq_2f_140.srdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 20 | `kortex_move_it_config/gen3_robotiq_2f_85_move_it_config/config/6dof/gen3_robotiq_2f_85.srdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 20 | `kortex_move_it_config/gen3_robotiq_2f_85_move_it_config/config/7dof/gen3_robotiq_2f_85.srdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>pal-robotics/pmb2_robot</b>: best 85, 2 robot(s), Apache-2.0, last commit 2026-09-23</summary>

From: robot_descriptions.py. Commit `e6584136f153`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 85 | `pmb2_description/robots/pmb2.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 25 | `pmb2_description/urdf/cameras_add_on/cameras_add_on.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: name 'camera_model' is not defined when evaluating expression 'camera_model == 'structure'' |

</details>

<details><summary><b>pal-robotics/tiago_robot</b>: best 85, 2 robot(s), Apache-2.0, last commit 2026-11-18</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `734095ca1844`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 85 | `tiago_description/robots/tiago.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 9.8 · 5 · 10 |  |
| 25 | `tiago_description/ros2_control/ros2_control.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: name 'base_type' is not defined when evaluating expression 'base_type' |

</details>

<details><summary><b>Rhoban/onshape-to-robot-examples</b>: best 85, 24 robot(s), MIT, last commit 2026-02-02</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `7e40fd653205`. Also 1 SDF file(s), not measured.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 85 | `field_mujoco/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 74 | `adjustable_height_arm_mujoco/robot.xml` | mjcf | 15 · 10 · 20 · 3.8 · 10 · 5 · 10 |  |
| 70 | `2wheels_mujoco/robot.xml` | mjcf | 15 · 10 · 20 · 0 · 10 · 5 · 10 |  |
| 70 | `orbita_mujoco/robot.xml` | mjcf | 15 · 10 · 20 · 0 · 10 · 5 · 10 |  |
| 70 | `planar-2dof/robot.xml` | mjcf | 15 · 10 · 20 · 0 · 10 · 5 · 10 |  |
| 65 | `quadruped_mujoco/robot.xml` | mjcf | 15 · 10 · 20 · 0 · 10 · 1.2 · 8.9 |  |
| 64 | `dog_mujoco/robot.xml` | mjcf | 15 · 10 · 20 · 0 · 10 · 5 · 3.5 |  |
| 62 | `rsk_mujoco/robot.xml` | mjcf | 15 · 10 · 20 · 0.2 · 10 · 4.2 · 3 |  |
| 62 | `sigmaban2019_mujoco/robot.xml` | mjcf | 15 · 10 · 20 · 0 · 10 · 3.5 · 3.2 |  |
| 61 | `rsk_urdf/robot.xml` | mjcf | 15 · 10 · 20 · 0.2 · 10 · 4.2 · 1.6 |  |
| 25 | `2wheels_mujoco/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 2 visual mesh file(s) missing |
| 25 | `2wheels_urdf/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 2 visual mesh file(s) missing |
| 25 | `adjustable_height_arm_mujoco/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 25 | `adjustable_height_arm_urdf/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 25 | `dog_mujoco/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |
| 25 | `dog_urdf/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |
| 25 | `field_mujoco/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 12 visual mesh file(s) missing |
| 25 | `field_urdf/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 12 visual mesh file(s) missing |
| 25 | `quadruped_mujoco/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |
| 25 | `quadruped_sdf/prev.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |
| 25 | `quadruped_sdf/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |
| 25 | `quadruped_urdf/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |
| 25 | `rsk_urdf/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 27 visual mesh file(s) missing |
| 25 | `sigmaban2019_urdf/robot.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 21 visual mesh file(s) missing |

</details>

<details><summary><b>roboninecom/SO-ARM100-101-102-Parallel-Gripper</b>: best 85, 8 robot(s), CC-BY-4.0, last commit 2026-11-18</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `42b4e72ffc37`. Also 1 SDF file(s), not measured.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 85 | `community/histology-slide-gripper/mujoco/so_101.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 9.8 |  |
| 85 | `simulation/so_arm_101_description/urdf/so_101.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 9.8 |  |
| 81 | `community/histology-slide-gripper/mujoco/so101_slide_gripper.xml` | mjcf | 15 · 10 · 20 · 13.1 · 10 · 3.3 · 10 |  |
| 80 | `community/histology-slide-gripper/mujoco/scene_gripper.xml` | mjcf | 15 · 10 · 20 · 11.2 · 8.3 · 5 · 10 |  |
| 80 | `community/histology-slide-gripper/mujoco/so_101_arm.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 0 · 9.9 |  |
| 25 | `community/histology-slide-gripper/mujoco/so_101_arm.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 6 visual mesh file(s) missing |
| 25 | `simulation/so_arm_101_description/urdf/materials.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `simulation/so_arm_101_description/urdf/so_101.ros2_control.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: name 'plugin_name' is not defined when evaluating expression 'plugin_name' |

</details>

<details><summary><b>roboninecom/SO-ARM102</b>: best 85, 3 robot(s), CC-BY-4.0, last commit 2026-11-19</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `c35b70c372a3`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 85 | `simulation/urdf/so_arm_102.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 85 | `simulation/urdf/so_arm_102.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 25 | `simulation/urdf/materials.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>robot-descriptions/halodi-robot-models</b>: best 85, 15 robot(s), Apache-2.0, last commit 2022-05-18 **archived**</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `5d1d5eb3c15c`. Also 4 SDF file(s), not measured.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 85 | `eve_r3_description/urdf.in/robotiq_2f_85.left.in.urdf` | urdf | 15 · 0 · 20 · 15 · 8.2 · 16.4 · 10 |  |
| 85 | `eve_r3_description/urdf.in/robotiq_2f_85.right.in.urdf` | urdf | 15 · 0 · 20 · 15 · 8.2 · 16.4 · 10 |  |
| 83 | `eve_r3_description/urdf/eve_r3_robotiq_2f_85.urdf` | urdf | 15 · 0 · 20 · 10.2 · 9.1 · 18.3 · 10 |  |
| 82 | `eve_r3_description/urdf.in/eve_r3_head.in.urdf` | urdf | 15 · 0 · 20 · 7.5 · 10 · 20 · 10 |  |
| 82 | `eve_r3_description/urdf.in/eve_r3_left_arm.in.urdf` | urdf | 15 · 0 · 20 · 7.5 · 10 · 20 · 10 |  |
| 82 | `eve_r3_description/urdf.in/eve_r3_leg.in.urdf` | urdf | 15 · 0 · 20 · 7.5 · 10 · 20 · 10 |  |
| 82 | `eve_r3_description/urdf.in/eve_r3_right_arm.in.urdf` | urdf | 15 · 0 · 20 · 7.5 · 10 · 20 · 10 |  |
| 82 | `eve_r3_description/urdf.in/eve_r3_upper_body.in.urdf` | urdf | 15 · 0 · 20 · 7.5 · 10 · 20 · 10 |  |
| 15 | `eve_r3_description/urdf.in/qbhand.left.in.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |
| 15 | `eve_r3_description/urdf.in/qbhand.right.in.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |
| 15 | `eve_r3_description/urdf.in/robotiq_hand-e.left.in.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 4 visual mesh file(s) missing |
| 15 | `eve_r3_description/urdf.in/robotiq_hand-e.right.in.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 4 visual mesh file(s) missing |
| 15 | `eve_r3_description/urdf/eve_r3.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 9 visual mesh file(s) missing |
| 15 | `eve_r3_description/urdf/eve_r3_robotiq_hand-e.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 4 visual mesh file(s) missing |
| 15 | `eve_r3_description/urdf/eve_r3_upper_body.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 9 visual mesh file(s) missing |

</details>

<details><summary><b>hshi74/toddlerbot</b>: best 84, 62 robot(s), MIT, last commit 2026-11-16</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `6258f95d23d8`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 84 | `toddlerbot/descriptions/assemblies/left_leg_2xc_430/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.6 |  |
| 84 | `toddlerbot/descriptions/assemblies/left_leg_2xm_430/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.6 |  |
| 84 | `toddlerbot/descriptions/assemblies/right_leg_2xc_430/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.6 |  |
| 84 | `toddlerbot/descriptions/assemblies/right_leg_2xm_430/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.6 |  |
| 84 | `toddlerbot/descriptions/assemblies/teleop_leader/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 9 |  |
| 83 | `toddlerbot/descriptions/assemblies/left_arm_leader/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.2 |  |
| 83 | `toddlerbot/descriptions/assemblies/left_arm_palm/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 7.8 |  |
| 83 | `toddlerbot/descriptions/assemblies/right_arm_leader/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.2 |  |
| 83 | `toddlerbot/descriptions/assemblies/right_arm_palm/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 7.8 |  |
| 83 | `toddlerbot/descriptions/teleop_leader/teleop_leader_fixed.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 7.8 |  |
| 83 | `toddlerbot/descriptions/teleop_leader/teleop_leader_pos_fixed.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 7.8 |  |
| 82 | `toddlerbot/descriptions/assemblies/left_arm_gripper/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 7.2 |  |
| 82 | `toddlerbot/descriptions/assemblies/right_arm_gripper/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 7.2 |  |
| 80 | `toddlerbot/descriptions/assemblies/2xc_430_gripper/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 4.9 |  |
| 80 | `toddlerbot/descriptions/assemblies/2xc_430_palm/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 4.9 |  |
| 80 | `toddlerbot/descriptions/assemblies/2xm_430_gripper/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 4.9 |  |
| 80 | `toddlerbot/descriptions/assemblies/2xm_430_palm/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 4.9 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xc/scene_teleop.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xc/toddlerbot_2xc.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xc/toddlerbot_2xc.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xc/toddlerbot_2xc_fixed.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xc/toddlerbot_2xc_mjx.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xc/toddlerbot_2xc_mjx_fixed.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xc/toddlerbot_2xc_pos.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xc/toddlerbot_2xc_pos_fixed.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xm/scene_teleop.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xm/toddlerbot_2xm.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xm/toddlerbot_2xm.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xm/toddlerbot_2xm_fixed.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xm/toddlerbot_2xm_mjx.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xm/toddlerbot_2xm_mjx_fixed.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xm/toddlerbot_2xm_pos.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 79 | `toddlerbot/descriptions/toddlerbot_2xm/toddlerbot_2xm_pos_fixed.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3.6 |  |
| 78 | `toddlerbot/descriptions/toddlerbot_2xc_gripper/toddlerbot_2xc_gripper.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 3 |  |
| 78 | `toddlerbot/descriptions/toddlerbot_2xc_gripper/toddlerbot_2xc_gripper.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3 |  |
| 78 | `toddlerbot/descriptions/toddlerbot_2xc_gripper/toddlerbot_2xc_gripper_fixed.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3 |  |
| 78 | `toddlerbot/descriptions/toddlerbot_2xc_gripper/toddlerbot_2xc_gripper_mjx.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3 |  |
| 78 | `toddlerbot/descriptions/toddlerbot_2xc_gripper/toddlerbot_2xc_gripper_mjx_fixed.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3 |  |
| 78 | `toddlerbot/descriptions/toddlerbot_2xc_gripper/toddlerbot_2xc_gripper_pos.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3 |  |
| 78 | `toddlerbot/descriptions/toddlerbot_2xc_gripper/toddlerbot_2xc_gripper_pos_fixed.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 3 |  |
| | and 22 more, in `audit.json` | | | |

</details>

<details><summary><b>limxdynamics/humanoid-description</b>: best 84, 8 robot(s), Apache-2.0, last commit 2026-11-05</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `4c0a3c71200b`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 84 | `HU_D03_description/xml/HU_D03_03.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.8 |  |
| 84 | `HU_D03_description/xml/HU_D03_03_vis.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.9 |  |
| 84 | `HU_D04_description/urdf/HU_D04_01.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 9.1 |  |
| 84 | `HU_D04_description/urdf/HU_D04_01_with_gripper.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 9 |  |
| 84 | `HU_D04_description/xml/HU_D04_01.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 9 |  |
| 84 | `HU_D04_description/xml/HU_D04_01_vis.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 9.1 |  |
| 83 | `HU_D03_description/urdf/HU_D03_03.urdf` | urdf | 15 · 10 · 20 · 15 · 9.5 · 4.8 · 8.8 |  |
| 82 | `HU_D04_description/urdf/HU_D04_01_with_hand.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 7.3 |  |

</details>

<details><summary><b>limxdynamics/tron1-robot-description</b>: best 84, 52 robot(s), Apache-2.0, last commit 2026-11-05</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `ac417d44656d`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 84 | `pointfoot/PF_P441A/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.5 · 9.4 |  |
| 84 | `pointfoot/PF_P441A/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 9.2 |  |
| 84 | `pointfoot/PF_P441A/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 9.4 |  |
| 84 | `pointfoot/PF_P441C/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.5 |  |
| 84 | `pointfoot/PF_P441C2/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.5 · 9.4 |  |
| 84 | `pointfoot/PF_P441C2/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 9.1 |  |
| 84 | `pointfoot/PF_P441C2/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 9.4 |  |
| 84 | `pointfoot/PF_TRON1A/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.5 · 9.1 |  |
| 84 | `pointfoot/PF_TRON1A/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 8.9 |  |
| 84 | `pointfoot/PF_TRON1A/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 9.1 |  |
| 84 | `pointfoot/PF_TRON1B/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.5 · 9.1 |  |
| 84 | `pointfoot/PF_TRON1B/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 8.9 |  |
| 84 | `pointfoot/PF_TRON1B/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 9.1 |  |
| 84 | `pointfoot/SF_TRON1A/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 8.9 |  |
| 84 | `pointfoot/SF_TRON1A/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.8 |  |
| 84 | `pointfoot/SF_TRON1B/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 8.9 |  |
| 84 | `pointfoot/SF_TRON1B/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.8 |  |
| 84 | `pointfoot/WF_TRON1A/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 8.9 |  |
| 84 | `pointfoot/WF_TRON1A/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.9 |  |
| 84 | `pointfoot/WF_TRON1B/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 8.9 |  |
| 84 | `pointfoot/WF_TRON1B/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.9 |  |
| 83 | `pointfoot/PF_P441B/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.5 · 8.4 |  |
| 83 | `pointfoot/PF_P441B/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 8.1 |  |
| 83 | `pointfoot/PF_P441B/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 8.4 |  |
| 83 | `pointfoot/PF_P441C/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.5 · 8.5 |  |
| 83 | `pointfoot/PF_P441C/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 5 · 8.3 |  |
| 83 | `pointfoot/SF_TRON1A/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.5 · 8.9 |  |
| 83 | `pointfoot/SF_TRON1B/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.5 · 8.9 |  |
| 83 | `pointfoot/WF_TRON1A/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.5 · 8.9 |  |
| 83 | `pointfoot/WF_TRON1B/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.5 · 8.9 |  |
| 80 | `wheellegged/WL_P311D/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 8.2 · 3.9 · 8.1 |  |
| 80 | `wheellegged/WL_P311E/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 8.2 · 3.9 · 7.6 |  |
| 25 | `pointfoot/PF_P441A/xacro/gazebo.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `pointfoot/PF_P441A/xacro/materials.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `pointfoot/PF_P441B/xacro/gazebo.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `pointfoot/PF_P441B/xacro/materials.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `pointfoot/PF_P441C/xacro/gazebo.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `pointfoot/PF_P441C/xacro/materials.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `pointfoot/PF_P441C2/xacro/gazebo.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `pointfoot/PF_P441C2/xacro/materials.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| | and 12 more, in `audit.json` | | | |

</details>

<details><summary><b>PR2/pr2_common</b>: best 84, 6 robot(s), no licence named, last commit 2025-01-14</summary>

From: awesome-robot-descriptions. Commit `9a8e4fbcf665`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 84 | `pr2_description/robots/pr2.urdf.xacro` | xacro | 7.5 · 5 · 20 · 15 · 10 · 16.2 · 10 |  |
| 84 | `pr2_description/robots/pr2_no_arms.urdf.xacro` | xacro | 7.5 · 5 · 20 · 15 · 10 · 16.3 · 10 |  |
| 84 | `pr2_description/robots/pr2_no_kinect.urdf.xacro` | xacro | 7.5 · 5 · 20 · 15 · 10 · 16.2 · 10 |  |
| 83 | `pr2_description/robots/pr2_se.urdf.xacro` | xacro | 7.5 · 5 · 20 · 15 · 10 · 15.2 · 10 |  |
| 12 | `pr2_description/gazebo/gazebo.urdf.xacro` | xacro | 7.5 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 12 | `pr2_description/urdf/materials.urdf.xacro` | xacro | 7.5 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>limxdynamics/tron2-robot-description</b>: best 83, 73 robot(s), Apache-2.0, last commit 2026-11-13</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `d81d2a83a3c7`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 83 | `tron2a/SF_TRON2A/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.6 · 8.1 |  |
| 83 | `tron2b/SF_TRON2B/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 7.8 |  |
| 82 | `tron2a/DA_TRON2A/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.8 · 7.4 |  |
| 82 | `tron2a/WF_TRON2A/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.6 · 7.1 |  |
| 82 | `tron2b/WF_TRON2B/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 7.1 |  |
| 81 | `tron2a/SFYG_TRON2A/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.6 · 6.5 |  |
| 81 | `tron2a/WFYG_TRON2A/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 4.6 · 6.6 |  |
| 81 | `tron2b/DA_TRON2B/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 6 |  |
| 81 | `tron2b/SFYG_TRON2B/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 6.2 |  |
| 80 | `tron2a/SF_TRON2A/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 5.5 |  |
| 80 | `tron2b/DACH_TRON2B/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 5.4 |  |
| 80 | `tron2b/DACH_TRON2B/urdf/robot_grasper.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 5.4 |  |
| 80 | `tron2b/DACH_TRON2B/urdf/robot_zeromass_graser.urdf` | urdf | 15 · 10 · 20 · 15 · 9.2 · 5 · 5.4 |  |
| 80 | `tron2b/SF_TRON2B/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 5.1 |  |
| 80 | `tron2b/WFYG_TRON2B/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 5.5 |  |
| 79 | `tron2a/DA_TRON2A/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 4.1 |  |
| 79 | `tron2a/WF_TRON2A/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 4.4 |  |
| 79 | `tron2b/WF_TRON2B/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 4.3 |  |
| 78 | `tron2a/SF_TRON2A/urdf/robot_rl.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 8.1 |  |
| 78 | `tron2a/WFYG_TRON2A/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 2.5 |  |
| 78 | `tron2b/DASF_TRON2B/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 2.6 |  |
| 78 | `tron2b/DASF_TRON2B/urdf/robot_zeromass_graser.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 5 · 2.6 |  |
| 78 | `tron2b/SF_TRON2B/urdf/robot_rl.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 7.8 |  |
| 77 | `tron2a/DA_TRON2A/urdf/robot_rl.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 7.4 |  |
| 77 | `tron2a/SFYG_TRON2A/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 2.2 |  |
| 77 | `tron2a/WFYG_TRON2A/urdf/robot_rl.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 6.6 |  |
| 77 | `tron2a/WF_TRON2A/urdf/robot_rl.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 7.1 |  |
| 77 | `tron2b/DA_TRON2B/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 1.6 |  |
| 77 | `tron2b/SFYG_TRON2B/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 1.8 |  |
| 77 | `tron2b/WF_TRON2B/urdf/robot_rl.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 7.1 |  |
| 76 | `tron2a/DACH_TRON2A/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 5.5 |  |
| 76 | `tron2a/DACH_TRON2A/urdf/robot_rl.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 5.5 |  |
| 76 | `tron2a/DACH_TRON2A/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 0.7 |  |
| 76 | `tron2a/DACH_TRON2A/xml/robot_grasper.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 0.7 |  |
| 76 | `tron2a/SFYG_TRON2A/urdf/robot_rl.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 6.5 |  |
| 76 | `tron2b/DACH_TRON2B/xml/robot_grasper.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 0.5 |  |
| 76 | `tron2b/DA_TRON2B/urdf/robot_rl.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 6 |  |
| 76 | `tron2b/SFYG_TRON2B/urdf/robot_rl.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 6.2 |  |
| 76 | `tron2b/WFYG_TRON2B/urdf/robot_rl.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 5.5 |  |
| 76 | `tron2b/WFYG_TRON2B/xml/robot.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 0.9 |  |
| | and 33 more, in `audit.json` | | | |

</details>

<details><summary><b>openai/roboschool</b>: best 82, 15 robot(s), NOASSERTION, last commit 2019-10-09 **archived**</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `d32bcb2b35b9`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 82 | `roboschool/models_household/dinnerware/plate.urdf` | urdf | 7.5 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 80 | `roboschool/models_household/dinnerware/pan_tefal.urdf` | urdf | 7.5 · 0 · 20 · 15 · 10 · 17.5 · 10 |  |
| 78 | `roboschool/models_household/bottle/bottle.urdf` | urdf | 7.5 · 0 · 20 · 15 · 10 · 15 · 10 |  |
| 68 | `roboschool/models_household/ball.urdf` | urdf | 7.5 · 0 · 20 · 15 · 10 · 5 · 10 |  |
| 68 | `roboschool/models_household/cube.urdf` | urdf | 7.5 · 0 · 20 · 15 · 10 · 5 · 10 |  |
| 68 | `roboschool/models_robot/roboschool_pong.xml` | mjcf | 7.5 · 0 · 20 · 15 · 10 · 5 · 10 |  |
| 68 | `roboschool/mujoco_assets/ant.xml` | mjcf | 7.5 · 0 · 20 · 15 · 10 · 5 · 10 |  |
| 68 | `roboschool/mujoco_assets/humanoid_symmetric.xml` | mjcf | 7.5 · 0 · 20 · 15 · 10 · 5 · 10 |  |
| 64 | `roboschool/mujoco_assets/reacher.xml` | mjcf | 7.5 · 0 · 20 · 11.2 · 10 · 5 · 10 |  |
| 62 | `roboschool/mujoco_assets/half_cheetah.xml` | mjcf | 7.5 · 0 · 20 · 10 · 10 · 5 · 10 |  |
| 62 | `roboschool/mujoco_assets/walker2d.xml` | mjcf | 7.5 · 0 · 20 · 10 · 10 · 5 · 10 |  |
| 60 | `roboschool/mujoco_assets/hopper.xml` | mjcf | 7.5 · 0 · 20 · 7.5 · 10 · 5 · 10 |  |
| 60 | `roboschool/mujoco_assets/inverted_pendulum.xml` | mjcf | 7.5 · 0 · 20 · 7.5 · 10 · 5 · 10 |  |
| 58 | `roboschool/mujoco_assets/inverted_double_pendulum.xml` | mjcf | 7.5 · 0 · 20 · 5 · 10 · 5 · 10 |  |
| 8 | `roboschool/models_robot/atlas_description/urdf/atlas_v4_with_multisense.urdf` | urdf | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | 23 visual mesh file(s) missing |

</details>

<details><summary><b>ridgeback/ridgeback_manipulation</b>: best 82, 38 robot(s), no licence named, last commit 2023-09-26</summary>

From: awesome-robot-descriptions. Commit `748d28497861`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 82 | `ridgeback_kinova_description/urdf/ridgeback_dual_j2n6s200_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 19.7 · 9.9 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_dual_j2n6s300_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_dual_j2n7s300_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 19.5 · 10 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_dual_j2s6s300_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 19.5 · 10 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_dual_j2s7s300_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 19.1 · 9.9 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_dual_m1n6s200_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 19.1 · 9.9 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_dual_m1n6s300_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 19.5 · 10 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_j2n6s200_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 19.7 · 10 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_j2n6s300_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_j2n7s300_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 19.5 · 10 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_j2s6s300_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 19.5 · 10 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_j2s7s300_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 19.1 · 10 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_m1n6s200_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 19.1 · 10 |  |
| 82 | `ridgeback_kinova_description/urdf/ridgeback_m1n6s300_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 19.5 · 10 |  |
| 82 | `ridgeback_ur_description/urdf/ridgeback_dual_ur10_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 20 · 9.8 |  |
| 82 | `ridgeback_ur_description/urdf/ridgeback_dual_ur10_e_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 20 · 9.7 |  |
| 82 | `ridgeback_ur_description/urdf/ridgeback_dual_ur5_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 82 | `ridgeback_ur_description/urdf/ridgeback_dual_ur5_e_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 20 · 9.8 |  |
| 82 | `ridgeback_ur_description/urdf/ridgeback_ur10_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 82 | `ridgeback_ur_description/urdf/ridgeback_ur10_e_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 82 | `ridgeback_ur_description/urdf/ridgeback_ur5_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 82 | `ridgeback_ur_description/urdf/ridgeback_ur5_e_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 20 · 10 |  |
| 73 | `ridgeback_kinova_description/urdf/ridgeback_dual_gen3_robotiq_2f_85_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 8.9 · 11.3 · 10 |  |
| 73 | `ridgeback_kinova_description/urdf/ridgeback_gen3_robotiq_2f_85_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 8.9 · 11.3 · 10 |  |
| 68 | `ridgeback_kinova_description/urdf/ridgeback_dual_gen3_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 5 · 10 |  |
| 68 | `ridgeback_kinova_description/urdf/ridgeback_gen3_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 5 · 10 |  |
| 66 | `ridgeback_kinova_description/urdf/ridgeback_dual_gen3_robotiq_2f_140_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 8.9 · 5 · 10 |  |
| 66 | `ridgeback_kinova_description/urdf/ridgeback_gen3_robotiq_2f_140_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 8.9 · 5 · 10 |  |
| 52 | `ridgeback_manipulation_description/urdf/fams.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 0 · 0 · 10 |  |
| 52 | `ridgeback_manipulation_description/urdf/hams.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 0 · 0 · 10 |  |
| 42 | `ridgeback_kinova_description/urdf/ridgeback_dual_kinova_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 0 · 0 · 0 |  |
| 42 | `ridgeback_kinova_description/urdf/ridgeback_kinova_description.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 0 · 0 · 0 |  |
| 8 | `ridgeback_franka_description/urdf/ridgeback_dual_panda_description.urdf.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: &lt;cache&gt;/frankarobotics__franka_ros/franka_description/robots/panda_arm.xacro &#91;Errno 2&#93; No such file or directory: '&lt;cache&gt;/frankarobotics__franka_ros/franka_description/robots/panda_arm.xacro' |
| 8 | `ridgeback_franka_description/urdf/ridgeback_dual_panda_hand_description.urdf.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: &lt;cache&gt;/frankarobotics__franka_ros/franka_description/robots/panda_arm.xacro &#91;Errno 2&#93; No such file or directory: '&lt;cache&gt;/frankarobotics__franka_ros/franka_description/robots/panda_arm.xacro' |
| 8 | `ridgeback_franka_description/urdf/ridgeback_panda_description.urdf.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: &lt;cache&gt;/frankarobotics__franka_ros/franka_description/robots/panda_arm.xacro &#91;Errno 2&#93; No such file or directory: '&lt;cache&gt;/frankarobotics__franka_ros/franka_description/robots/panda_arm.xacro' |
| 8 | `ridgeback_franka_description/urdf/ridgeback_panda_hand_description.urdf.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: &lt;cache&gt;/frankarobotics__franka_ros/franka_description/robots/panda_arm.xacro &#91;Errno 2&#93; No such file or directory: '&lt;cache&gt;/frankarobotics__franka_ros/franka_description/robots/panda_arm.xacro' |
| 8 | `ridgeback_iiwa_description/urdf/ridgeback_iiwa_14_description.urdf.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: Undefined parameters &#91;collision_postfix&#93; |
| 8 | `ridgeback_iiwa_description/urdf/ridgeback_iiwa_7_description.urdf.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: Undefined parameters &#91;collision_postfix&#93; |

</details>

<details><summary><b>ros-aldebaran/romeo_robot</b>: best 82, 12 robot(s), no licence named, last commit 2017-03-28</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `e53c8f3d7057`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 82 | `romeo_description/urdf/romeo_generated_urdf/romeo.urdf` | urdf | 7.5 · 0 · 20 · 15 · 10 · 19.8 · 10 |  |
| 72 | `romeo_description/urdf/romeo_generated_urdf/romeo_cap.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 10 · 10 |  |
| 52 | `romeo_description/urdf/romeo_generated_urdf/romeo_sensors.xacro` | xacro | 7.5 · 0 · 20 · 15 · 10 · 0 · 0 |  |
| 8 | `romeo_description/urdf/romeo_generated_urdf/romeoGazebo.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 8 | `romeo_description/urdf/romeo_generated_urdf/romeoTransmission.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 8 | `romeo_description/urdf/romeo_generated_urdf/romeo_arms.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_LShoulderYaw_link |
| 8 | `romeo_description/urdf/romeo_generated_urdf/romeo_eyes.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_LEye |
| 8 | `romeo_description/urdf/romeo_generated_urdf/romeo_fingers.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_RFinger13_link |
| 8 | `romeo_description/urdf/romeo_generated_urdf/romeo_head.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_NeckPitch_link |
| 8 | `romeo_description/urdf/romeo_generated_urdf/romeo_legs.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_LThigh |
| 8 | `romeo_description/urdf/romeo_generated_urdf/romeo_material.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 8 | `romeo_description/urdf/romeo_generated_urdf/romeo_torso.xacro` | xacro | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_torso |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/robotera/xbot_description</b>: best 81, 2 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 81 | `humanoid/robotera/xbot_description/urdf/robot.urdf` | urdf | 15 · 10 · 20 · 15 · 5.9 · 5.8 · 9.3 |  |
| 81 | `humanoid/robotera/xbot_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 5.9 · 5.8 · 9.3 |  |

</details>

<details><summary><b>epfl-lasa/iiwa_ros</b>: best 80, 3 robot(s), GPL-3.0, last commit 2024-01-16</summary>

From: robot_descriptions.py. Commit `9d2b99f1c62e`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 80 | `iiwa_description/urdf/iiwa14.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `iiwa_description/urdf/iiwa7.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 20 | `iiwa_description/urdf/materials.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>FFTAI/Wiki-GRx-Models</b>: best 80, 21 robot(s), GPL-3.0, last commit 2025-11-13</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `7d96c758f048`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 80 | `GR1_legacy/GR1/GR1T2/urdf/GR1T2.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 9.7 |  |
| 80 | `GRX/GR2/GR2v3.0.1/urdf/GR2v3.0.1.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 9.7 |  |
| 79 | `GR1_legacy/GR1/GR1T1/urdf/GR1T1.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 9.2 |  |
| 79 | `GR1_legacy/GR1/GR1T1/urdf/GR1T1_simple.urdf` | urdf | 15 · 5 · 20 · 15 · 9.7 · 5 · 9.2 |  |
| 79 | `GR1_legacy/GR1/GR1T2/urdf/GR1T2_simple.urdf` | urdf | 15 · 5 · 20 · 15 · 9.7 · 5 · 9.7 |  |
| 79 | `GRX/GR1/gr1t1/basic_urdf/gr1t1.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 9.1 |  |
| 79 | `GRX/GR1/gr1t1/basic_urdf/gr1t1_dummy_hand.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 8.8 |  |
| 79 | `GRX/GR1/gr1t2/basic_urdf/gr1t2.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 9.1 |  |
| 79 | `GRX/GR1/gr1t2/basic_urdf/gr1t2_dummy_hand.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 8.8 |  |
| 78 | `GRX/GR2/gr2v3_8_7/basic_urdf/gr2v3_8_7.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 8 |  |
| 78 | `GRX/GR2/gr2v3_8_7/basic_urdf/gr2v3_8_7_dummy_hand.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 7.8 |  |
| 78 | `GRX/GR2/gr2v3_8_7/mjcf/gr2v3_8_7.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 5 · 8 |  |
| 78 | `GRX/GR2/gr2v3_8_7/mjcf/gr2v3_8_7_dummy_hand.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 5 · 7.8 |  |
| 78 | `GRX/GR3/gr3v2_1_1/basic_urdf/gr3v2_1_1.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 7.8 |  |
| 78 | `GRX/GR3/gr3v2_1_1/basic_urdf/gr3v2_1_1_dummy_hand.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 7.6 |  |
| 78 | `GRX/GR3/gr3v2_1_1/mjcf/gr3v2_1_1.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 5 · 7.8 |  |
| 78 | `GRX/GR3/gr3v2_1_1/mjcf/gr3v2_1_1_dummy_hand.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 5 · 7.6 |  |
| 74 | `GRX/GR1/gr1t1/urdf/gr1t1_fourier_hand_6dof.urdf` | urdf | 15 · 5 · 20 · 11.9 · 8.6 · 5 · 8 |  |
| 74 | `GRX/GR1/gr1t2/urdf/gr1t2_fourier_hand_6dof.urdf` | urdf | 15 · 5 · 20 · 11.9 · 8.6 · 5 · 8 |  |
| 70 | `Dexterous_hand/fourier_hand_6dof/urdf/fourier_left_hand_6dof.urdf` | urdf | 15 · 5 · 20 · 7.5 · 7.1 · 5 · 10 |  |
| 70 | `Dexterous_hand/fourier_hand_6dof/urdf/fourier_right_hand_6dof.urdf` | urdf | 15 · 5 · 20 · 7.5 · 7.1 · 5 · 10 |  |

</details>

<details><summary><b>hello-robot/stretch_ros</b>: best 80, 125 robot(s), no licence named, last commit 2024-05-20</summary>

From: awesome-robot-descriptions. Commit `7397a97a7843`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 80 | `stretch_description/batch/guthrie/urdf/stretch_base_imu.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/guthrie/urdf/stretch_dry_erase_marker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/guthrie/urdf/stretch_gripper.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/guthrie/urdf/stretch_gripper_with_puller.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/guthrie/urdf/stretch_laser_range_finder.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/guthrie/urdf/stretch_respeaker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/hank/urdf/stretch_base_imu.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/hank/urdf/stretch_dry_erase_marker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/hank/urdf/stretch_gripper.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/hank/urdf/stretch_gripper_with_puller.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/hank/urdf/stretch_laser_range_finder.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/hank/urdf/stretch_respeaker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/irma/urdf/stretch_base_imu.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/irma/urdf/stretch_dry_erase_marker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/irma/urdf/stretch_gripper.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/irma/urdf/stretch_gripper_with_puller.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/irma/urdf/stretch_laser_range_finder.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/irma/urdf/stretch_respeaker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/joplin/urdf/stretch_base_imu.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/joplin/urdf/stretch_dry_erase_marker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/joplin/urdf/stretch_gripper.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/joplin/urdf/stretch_gripper_with_puller.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/joplin/urdf/stretch_laser_range_finder.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/joplin/urdf/stretch_respeaker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/kendrick/urdf/stretch_base_imu.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/kendrick/urdf/stretch_dry_erase_marker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/kendrick/urdf/stretch_gripper.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/kendrick/urdf/stretch_gripper_with_puller.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/kendrick/urdf/stretch_laser_range_finder.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/kendrick/urdf/stretch_respeaker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/louis/urdf/stretch_base_imu.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/louis/urdf/stretch_dry_erase_marker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/louis/urdf/stretch_gripper.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/louis/urdf/stretch_gripper_with_puller.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/louis/urdf/stretch_laser_range_finder.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/louis/urdf/stretch_respeaker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/mitski/urdf/stretch_base_imu.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/mitski/urdf/stretch_dex_wrist.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/mitski/urdf/stretch_dry_erase_marker.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `stretch_description/batch/mitski/urdf/stretch_gripper.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| | and 85 more, in `audit.json` | | | |

</details>

<details><summary><b>pal-robotics/pal_hey5</b>: best 80, 1 robot(s), Apache-2.0, last commit 2025-06-27</summary>

From: robot_descriptions.py. Commit `344de441fa3c`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 80 | `pal_hey5_description/robots/pal_hey5_test.urdf.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |

</details>

<details><summary><b>pal-robotics/talos_robot</b>: best 80, 8 robot(s), Apache-2.0, last commit 2026-02-19</summary>

From: awesome-robot-descriptions. Commit `79709aa4f4f4`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 80 | `talos_description/robots/talos_arm_right.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 10 · 0.3 · 10 |  |
| 25 | `talos_description/robots/talos_full_fake_grippers.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: talos_description/urdf/leg/foot_collision_false.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'talos_description/urdf/leg/foot_collis |
| 25 | `talos_description/robots/talos_full_no_grippers.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: talos_description/urdf/leg/foot_collision_false.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'talos_description/urdf/leg/foot_collis |
| 25 | `talos_description/robots/talos_lower_body.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: talos_description/urdf/leg/foot_collision_false.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'talos_description/urdf/leg/foot_collis |
| 25 | `talos_description/robots/talos_lower_body_torso_head.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: talos_description/urdf/leg/foot_collision_false.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'talos_description/urdf/leg/foot_collis |
| 25 | `talos_description/urdf/crane/crane.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 25 | `talos_description/urdf/talos_full_common.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: talos_description/urdf/leg/foot_collision_false.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'talos_description/urdf/leg/foot_collis |
| 25 | `talos_description/urdf/torso/torso.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>tc-huang/low_cost_robot</b>: best 80, 3 robot(s), MIT, last commit 2024-09-21</summary>

From: awesome-robot-descriptions. Commit `0602b0c1e6a6`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 80 | `simulation/low_cost_robot/low_cost_robot.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 80 | `simulation/low_cost_robot/scene.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 20 | `simulation/low_cost_robot/low-cost-arm.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 6 visual mesh file(s) missing |

</details>

<details><summary><b>upkie/upkie_description</b>: best 80, 5 robot(s), Apache-2.0, last commit 2025-11-25</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `94735fbe6137`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 80 | `urdf/upkie.urdf` | urdf | 15 · 10 · 20 · 12.5 · 10 · 4 · 8.2 |  |
| 80 | `urdf/upkie_camera.urdf` | urdf | 15 · 10 · 20 · 12.5 · 10 · 4 · 8.1 |  |
| 25 | `xacro/upkie.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: .\.\xacro/utils/box_inertia.xacro &#91;Errno 2&#93; No such file or directory: '.\\.\\xacro/utils/box_inertia.xacro' |
| 25 | `xacro/upkie_camera.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: .\.\xacro/utils/box_inertia.xacro &#91;Errno 2&#93; No such file or directory: '.\\.\\xacro/utils/box_inertia.xacro' |
| 25 | `xacro/utils/materials.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/manipulator/lerobot/so_arm_description</b>: best 79, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 79 | `manipulator/lerobot/so_arm_description/urdf/so_arm.urdf` | urdf | 15 · 10 · 20 · 15 · 4.7 · 5.8 · 8.5 |  |
| 79 | `manipulator/lerobot/so_arm_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 15 · 4.7 · 5.8 · 8.5 |  |
| 73 | `manipulator/lerobot/so_arm_description/urdf/so_arm_100.urdf` | urdf | 15 · 10 · 20 · 7.5 · 5.4 · 5 · 10 |  |

</details>

<details><summary><b>iotdesignshop/dexhand_description</b>: best 79, 5 robot(s), NOASSERTION, last commit 2024-06-30</summary>

From: awesome-robot-descriptions. Commit `211b0ea23e21`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 79 | `urdf/dexhand-left.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 9.4 |  |
| 79 | `urdf/dexhand-left.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 9.4 |  |
| 79 | `urdf/dexhand-right.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 9.1 |  |
| 79 | `urdf/dexhand-right.xacro` | xacro | 15 · 5 · 20 · 15 · 10 · 5 · 9.1 |  |
| 20 | `urdf/materials.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>leap-hand/LEAP_Hand_Sim</b>: best 79, 3 robot(s), MIT, last commit 2024-05-18</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `150bc3d4b61f`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 79 | `assets/leap_hand/robot.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 5 · 8.6 |  |
| 75 | `assets/cube.urdf` | urdf | 15 · 5 · 20 · 15 · 10 · 0 · 10 |  |
| 20 | `assets/ball.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |

</details>

<details><summary><b>rt-net/sciurus17_description</b>: best 79, 1 robot(s), NOASSERTION, last commit 2026-07-28</summary>

From: awesome-robot-descriptions. Commit `607dea2f14e4`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 79 | `urdf/sciurus17.urdf.xacro` | xacro | 15 · 10 · 20 · 15 · 9.2 · 5 · 5 |  |

</details>

<details><summary><b>BoosterRobotics/booster_gym</b>: best 78, 4 robot(s), NOASSERTION, last commit 2025-12-23</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `da396a06d6ee`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 78 | `resources/T1/T1_locomotion.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 78 | `resources/T1/T1_locomotion.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 78 | `resources/T1/T1_serial.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 78 | `resources/T1/T1_serial.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 5 · 10 |  |

</details>

<details><summary><b>Chestnut-Robotics/aero-hand-open</b>: best 78, 2 robot(s), NOASSERTION, last commit 2026-09-15</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `7bb2f23485a7`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 78 | `ros2/src/aero_hand_open_description/urdf/aero_hand_open_left.urdf` | urdf | 15 · 10 · 20 · 7.5 · 10 · 5 · 10 |  |
| 78 | `ros2/src/aero_hand_open_description/urdf/aero_hand_open_right.urdf` | urdf | 15 · 10 · 20 · 7.5 · 10 · 5 · 10 |  |

</details>

<details><summary><b>userguide-galaxea/robot_descriptions</b>: best 78, 13 robot(s), no licence named, last commit 2026-11-12</summary>

From: awesome-robot-descriptions. Commit `72008ea950a4`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 78 | `a1x_description/urdf/a1x.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 78 | `a1y_description/urdf/a1y.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 78 | `a1z_description/a1z_flange_description/urdf/A1Z_Flange.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 5 · 10 |  |
| 77 | `a1z_description/a1z_g1z_description/urdf/A1Z_G1Z.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 5 · 9.8 |  |
| 76 | `lemo_description/urdf/LEMO.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 5 · 8 |  |
| 75 | `r1_description/urdf/r1_v2_1_0.urdf` | urdf | 7.5 · 10 · 20 · 15 · 10 · 5 · 7.4 |  |
| 71 | `r1pro_description/r1pro_g1z_2026_description/urdf/r1pro_2026.urdf` | urdf | 7.5 · 10 · 20 · 12.7 · 10 · 5 · 5.6 |  |
| 18 | `a1_description/urdf/A1_URDF_0607_0028.urdf` | urdf | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 9 visual mesh file(s) missing |
| 18 | `a1x_description/meshes/mmp_revB_invconfig_upright_a1x.urdf` | urdf | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 30 visual mesh file(s) missing |
| 10 | `r1lite_description/urdf_r1lite_2025.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 32 visual mesh file(s) missing |
| 10 | `r1lite_description/urdf_r1lite_2026/urdf_r1lite_2026_a1x.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 32 visual mesh file(s) missing |
| 10 | `r1lite_description/urdf_r1lite_2026/urdf_r1lite_2026_a1z.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 37 visual mesh file(s) missing |
| 10 | `r1pro_description/urdf_r1pro_2025.urdf` | urdf | 0 · 10 · 0 · 0 · 0 · 0 · 0 | 46 visual mesh file(s) missing |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/manipulator/lerobot/lekiwi_description</b>: best 76, 2 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 76 | `manipulator/lerobot/lekiwi_description/urdf/lekiwi.urdf` | urdf | 15 · 10 · 20 · 7.5 · 8.6 · 5.7 · 9.4 |  |
| 76 | `manipulator/lerobot/lekiwi_description/xacro/robot.xacro` | xacro | 15 · 10 · 20 · 7.5 · 8.6 · 5.7 · 9.4 |  |

</details>

<details><summary><b>limxdynamics/luna-description</b>: best 76, 3 robot(s), Apache-2.0, last commit 2026-11-05</summary>

From: robot_descriptions.py. Commit `e5132226c9d6`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 76 | `HU_L04_description/urdf/HU_L04_01.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 1.4 · 4.3 |  |
| 75 | `HU_L04_description/xml/HU_L04_01.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 0 |  |
| 75 | `HU_L04_description/xml/HU_L04_01_vis.xml` | mjcf | 15 · 10 · 20 · 15 · 10 · 5 · 0 |  |

</details>

<details><summary><b>hello-robot/stretch_urdf</b>: best 75, 52 robot(s), NOASSERTION, last commit 2026-06-05</summary>

From: robot_descriptions.py. Commit `c8c6e27e1f87`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 75 | `stretch_urdf/RE1V0/stretch_description_RE1V0_tool_none.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8.8 · 5.2 · 8.7 |  |
| 75 | `stretch_urdf/RE1V0/stretch_description_RE1V0_tool_stretch_dex_wrist.urdf` | urdf | 7.5 · 10 · 20 · 15 · 9.1 · 5.2 · 7.9 |  |
| 75 | `stretch_urdf/RE1V0/stretch_description_RE1V0_tool_stretch_gripper.urdf` | urdf | 7.5 · 10 · 20 · 15 · 9 · 5.2 · 8.5 |  |
| 75 | `stretch_urdf/SE3/stretch_description_SE3_eoa_wrist_dw3_tool_nil.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8.9 · 5.2 · 8.7 |  |
| 75 | `stretch_urdf/SE3/stretch_description_SE3_eoa_wrist_dw3_tool_tablet_12in.urdf` | urdf | 7.5 · 10 · 20 · 15 · 9 · 5.2 · 8.7 |  |
| 74 | `stretch_urdf/RE2V0/stretch_description_RE2V0_eoa_wrist_dw3_tool_nil.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8.9 · 5.2 · 7.7 |  |
| 74 | `stretch_urdf/RE2V0/stretch_description_RE2V0_eoa_wrist_dw3_tool_tablet_12in.urdf` | urdf | 7.5 · 10 · 20 · 15 · 9 · 5.2 · 7.7 |  |
| 74 | `stretch_urdf/RE2V0/stretch_description_RE2V0_tool_none.urdf` | urdf | 7.5 · 10 · 20 · 15 · 8.8 · 5.2 · 7.8 |  |
| 74 | `stretch_urdf/RE2V0/stretch_description_RE2V0_tool_stretch_dex_wrist.urdf` | urdf | 7.5 · 10 · 20 · 15 · 9.1 · 5.2 · 7 |  |
| 74 | `stretch_urdf/RE2V0/stretch_description_RE2V0_tool_stretch_gripper.urdf` | urdf | 7.5 · 10 · 20 · 15 · 9 · 5.2 · 7.6 |  |
| 73 | `stretch_urdf/SE3/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf` | urdf | 7.5 · 10 · 20 · 12.7 · 9.2 · 5.1 · 8.6 |  |
| 73 | `stretch_urdf/SE3/stretch_description_SE3_eoa_wrist_dw3_tool_sg3_pro.urdf` | urdf | 7.5 · 10 · 20 · 12.7 · 9.2 · 5.1 · 8.6 |  |
| 72 | `stretch_urdf/RE2V0/stretch_description_RE2V0_eoa_wrist_dw3_tool_sg3.urdf` | urdf | 7.5 · 10 · 20 · 12.7 · 9.2 · 5.1 · 7.6 |  |
| 18 | `stretch_urdf/RE1V0/xacro/d435i/_materials.urdf.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 18 | `stretch_urdf/RE1V0/xacro/stretch_aruco.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE1V0/xacro/stretch_base_imu.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE1V0/xacro/stretch_d435i.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE1V0/xacro/stretch_dex_wrist.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 8 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE1V0/xacro/stretch_gripper.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE1V0/xacro/stretch_gripper_with_puller.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 6 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE1V0/xacro/stretch_laser_range_finder.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE1V0/xacro/stretch_main.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 15 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE1V0/xacro/stretch_respeaker.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/d405/_materials_d405.urdf.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 18 | `stretch_urdf/RE2V0/xacro/d435i/_materials.urdf.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_aruco.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_base_imu.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_d405_sg3.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_d435i.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_dex_wrist.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 8 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_gripper.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_gripper_with_puller.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 6 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_head_nav_cam.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_laser_range_finder.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_main.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 15 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_respeaker.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_tool_sg3.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 8 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_tool_tablet_12in.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 18 | `stretch_urdf/RE2V0/xacro/stretch_wrist_dw3.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 3 visual mesh file(s) missing |
| 18 | `stretch_urdf/SE3/xacro/d405/_materials_d405.urdf.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| | and 12 more, in `audit.json` | | | |

</details>

<details><summary><b>stack-of-tasks/talos-data</b>: best 75, 21 robot(s), LGPL-3.0, last commit 2022-12-29 **archived**</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `dc636c94d307`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 75 | `robots/talos_left_arm.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 4.7 · 10 |  |
| 75 | `robots/talos_reduced.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 4.7 · 10 |  |
| 75 | `urdf/talos_full.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 4.7 · 10 |  |
| 75 | `urdf/talos_full_v2.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 4.7 · 10 |  |
| 75 | `urdf/talos_full_v2_with_lidar.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 4.9 · 10 |  |
| 75 | `urdf/talos_reduced.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 4.7 · 10 |  |
| 75 | `urdf/talos_reduced_v2.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 4.7 · 10 |  |
| 15 | `gazebo/gazebo.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `robots/talos_full.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: urdf/arm/arm.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'urdf/arm/arm.urdf.xacro' |
| 15 | `robots/talos_full_no_grippers.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: urdf/leg/foot_collision_false.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'urdf/leg/foot_collision_false.urdf.xacro' |
| 15 | `robots/talos_full_v1.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: urdf/leg/foot_collision_false.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'urdf/leg/foot_collision_false.urdf.xacro' |
| 15 | `robots/talos_full_v2.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: urdf/leg/foot_collision_false.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'urdf/leg/foot_collision_false.urdf.xacro' |
| 15 | `robots/talos_lower_body.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: urdf/leg/foot_collision_false.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'urdf/leg/foot_collision_false.urdf.xacro' |
| 15 | `robots/talos_small.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: urdf/arm/arm.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'urdf/arm/arm.urdf.xacro' |
| 15 | `urdf/arm/left_arm.transmissions.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: name 'name' is not defined when evaluating expression 'name' |
| 15 | `urdf/arm/left_wrist.transmissions.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: name 'name' is not defined when evaluating expression 'name' |
| 15 | `urdf/arm/right_arm.transmissions.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: name 'name' is not defined when evaluating expression 'name' |
| 15 | `urdf/arm/right_wrist.transmissions.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: name 'name' is not defined when evaluating expression 'name' |
| 15 | `urdf/crane/crane.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `urdf/materials.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `urdf/talos_full_common.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: urdf/arm/arm.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'urdf/arm/arm.urdf.xacro' |

</details>

<details><summary><b>Rhoban/microban</b>: best 74, 2 robot(s), NOASSERTION, last commit 2026-09-10</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `d0a128d180ec`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 74 | `src/model/mjcf/robot.xml` | mjcf | 7.5 · 10 · 20 · 15 · 10 · 3.2 · 8.4 |  |
| 52 | `src/model/urdf/robot.urdf` | urdf | 7.5 · 10 · 20 · 15 · 0 · 0 · 0 |  |

</details>

<details><summary><b>ADVRHumanoids/iit-walkman-ros-pkg</b>: best 73, 18 robot(s), BSD-3-Clause, last commit 2018-02-16</summary>

From: awesome-robot-descriptions. Commit `d38fe56a844f`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 73 | `walkman_urdf/urdf/walkman.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 4.9 · 8.4 |  |
| 73 | `walkman_urdf/urdf/walkman_robot.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 4.9 · 8.4 |  |
| 70 | `walkman_urdf/urdf/parts/arms.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 0 · 10 |  |
| 70 | `walkman_urdf/urdf/parts/legs.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 0 · 9.9 |  |
| 70 | `walkman_urdf/urdf/parts/neck.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 0 · 10 |  |
| 70 | `walkman_urdf/urdf/parts/torso.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 0 · 10 |  |
| 70 | `walkman_urdf/urdf/sensors/imu.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 0 · 10 |  |
| 68 | `walkman_urdf/urdf/walkman_base.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 0 · 8.4 |  |
| 50 | `walkman_urdf/urdf/parts/foot_reference_frame.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 0 · 0 · 0 |  |
| 15 | `walkman_srdf/srdf/walkman.srdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: walkman_srdf/urdf/walkman_config.urdf.xacro &#91;Errno 2&#93; No such file or directory: 'walkman_srdf/urdf/walkman_config.ur |
| 15 | `walkman_urdf/urdf/gazebo/force_torque.gazebo.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `walkman_urdf/urdf/gazebo/magnetic_attach_ros.gazebo.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `walkman_urdf/urdf/gazebo/microstrain_3dmgx2_imu.gazebo.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `walkman_urdf/urdf/gazebo/walkman.gazebo.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `walkman_urdf/urdf/gazebo/walkman_materials.gazebo.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `walkman_urdf/urdf/gazebo/xbot_control.gazebo.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `walkman_urdf/urdf/parts/soft_hand.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: name 'mmTom' is not defined when evaluating expression '2.0955992*mmTom' |
| 15 | `walkman_urdf/urdf/walkman_materials.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>bxirobotics/robot_descriptions</b>: best 73, 3 robot(s), Apache-2.0, last commit 2025-04-03</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `a190d0f428b3`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 73 | `elf2_dof25/xml/elf2_dof25.xml` | mjcf | 15 · 5 · 20 · 15 · 10 · 5 · 2.9 |  |
| 72 | `elf2_dof12/elf2_dof12.urdf` | urdf | 15 · 5 · 20 · 15 · 9.6 · 5 · 2.9 |  |
| 72 | `elf2_dof25/urdf/elf2_dof25.urdf` | urdf | 15 · 5 · 20 · 15 · 9.6 · 5 · 2.9 |  |

</details>

<details><summary><b>lvjonok/skydio_x2_description</b>: best 73, 1 robot(s), Apache-2.0, last commit 2024-01-14</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `66d04eccece8`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 73 | `urdf/skydio_x2.urdf` | urdf | 15 · 5 · 20 · 15 · 8 · 0 · 10 |  |

</details>

<details><summary><b>mathieu-celerier/kinova_mj_description</b>: best 72, 6 robot(s), BSD-2-Clause, last commit 2026-02-05</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `2877d305f7c5`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 72 | `xml/kinova_camera_gripper.xml` | mjcf | 15 · 10 · 20 · 1.9 · 10 · 5 · 10 |  |
| 70 | `xml/kinova.xml` | mjcf | 15 · 10 · 20 · 0 · 10 · 5 · 10 |  |
| 70 | `xml/kinova_camera.xml` | mjcf | 15 · 10 · 20 · 0 · 10 · 5 · 10 |  |
| 25 | `xml/kinova_bota.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `xml/kinova_bota_ds4.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `xml/kinova_callib.xml` | mjcf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |

</details>

<details><summary><b>poppy-project/poppy_ergo_jr_description</b>: best 72, 2 robot(s), no licence named, last commit 2020-08-13</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `7eb32bd385af`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 72 | `urdf/poppy_ergo_jr.urdf` | urdf | 7.5 · 0 · 20 · 15 · 8.6 · 11.4 · 10 |  |
| 70 | `urdf/poppy_ergo_jr.urdf.xacro` | xacro | 7.5 · 0 · 20 · 15 · 8.3 · 9.2 · 10 |  |

</details>

<details><summary><b>rimim/AWD</b>: best 72, 13 robot(s), NOASSERTION, last commit 2024-10-21</summary>

From: awesome-robot-descriptions. Commit `9022468fb50c`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 72 | `awd/data/assets/go_bdx/go_bdx.urdf` | urdf | 7.5 · 5 · 20 · 15 · 10 · 5 · 10 |  |
| 72 | `awd/data/assets/go_bdx/go_bdx.xml` | mjcf | 7.5 · 5 · 20 · 15 · 9.4 · 5 · 10 |  |
| 72 | `awd/data/assets/go_bdx/scene.xml` | mjcf | 7.5 · 5 · 20 · 15 · 9.5 · 5 · 10 |  |
| 70 | `awd/data/assets/mini_bdx/robot.xml` | mjcf | 7.5 · 5 · 20 · 15 · 9.4 · 5 · 7.8 |  |
| 70 | `awd/data/assets/mini_bdx/scene.xml` | mjcf | 7.5 · 5 · 20 · 15 · 9.4 · 5 · 7.8 |  |
| 70 | `awd/data/assets/mini_bdx/urdf/bdx.urdf` | urdf | 7.5 · 5 · 20 · 15 · 10 · 5 · 7.8 |  |
| 68 | `awd/data/assets/mjcf/amp_humanoid.xml` | mjcf | 7.5 · 5 · 20 · 15 · 10 · 0.3 · 10 |  |
| 68 | `awd/data/assets/mjcf/amp_humanoid_sword_shield.xml` | mjcf | 7.5 · 5 · 20 · 15 · 10 · 0.2 · 10 |  |
| 62 | `awd/data/assets/mjcf/block_projectile.urdf` | urdf | 7.5 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 62 | `awd/data/assets/mjcf/block_projectile_large.urdf` | urdf | 7.5 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 62 | `awd/data/assets/mjcf/heading_marker.urdf` | urdf | 7.5 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 62 | `awd/data/assets/mjcf/location_marker.urdf` | urdf | 7.5 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 62 | `awd/data/assets/mjcf/strike_target.urdf` | urdf | 7.5 · 5 · 20 · 15 · 0 · 5 · 10 |  |

</details>

<details><summary><b>aubrune/reachy_description</b>: best 71, 2 robot(s), Apache-2.0, last commit 2020-11-10</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `ce171a0aac7f`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 71 | `reachy.URDF` | urdf | 15 · 0 · 20 · 7.5 · 8.7 · 18.7 · 0.7 |  |
| 71 | `reachy.URDF.xacro` | xacro | 15 · 0 · 20 · 7.5 · 8.7 · 18.7 · 0.7 |  |

</details>

<details><summary><b>HybridRobotics/berkeley_humanoid_description</b>: best 71, 1 robot(s), no licence named, last commit 2024-08-23</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `d0d13d3f81d7`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 71 | `urdf/robot.urdf` | urdf | 7.5 · 5 · 20 · 15 · 10 · 5 · 8.1 |  |

</details>

<details><summary><b>laas/simple_humanoid_description</b>: best 71, 2 robot(s), BSD-2-Clause, last commit 2022-11-23</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `4e859aed7df3`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 71 | `urdf/simple_humanoid.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 0.9 · 10 |  |
| 50 | `urdf/simple_humanoid_classical.urdf` | urdf | 15 · 0 · 20 · 15 · 0 · 0 · 0 |  |

</details>

<details><summary><b>robot-descriptions/cassie_description</b>: best 71, 1 robot(s), MIT, last commit 2022-10-25 **archived**</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `81a2d8bbd772`. Also 2 SDF file(s), not measured.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 71 | `urdf/cassie_v4.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 5 · 6.3 |  |

</details>

<details><summary><b>robot-descriptions/stretch_description</b>: best 71, 1 robot(s), NOASSERTION, last commit 2023-04-13 **archived**</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `4b838429fe4c`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 71 | `urdf/stretch.urdf` | urdf | 15 · 0 · 20 · 15 · 9 · 5.2 · 7 |  |

</details>

<details><summary><b>boxer-cpr/boxer</b>: best 70, 4 robot(s), BSD-3-Clause, last commit 2022-09-23</summary>

From: awesome-robot-descriptions. Commit `6998d896ba8b`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 70 | `boxer_description/urdf/include/wheels_and_casters.urdf.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 0 · 10 |  |
| 15 | `boxer_description/urdf/boxer.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: realsense2_description Package not found: realsense2_description |
| 15 | `boxer_description/urdf/include/sensors.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: realsense2_description Package not found: realsense2_description |
| 15 | `boxer_description/urdf/materials.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>Gepetto/example-robot-data</b>: best 70, 69 robot(s), BSD-2-Clause, last commit 2026-11-05</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `78b6101a6387`. Also 5 SDF file(s), not measured.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 70 | `robots/double_pendulum_description/urdf/double_pendulum_simple.urdf` | urdf | 15 · 10 · 20 · 0 · 10 · 5 · 10 |  |
| 70 | `robots/simple_humanoid_description/urdf/simple_humanoid.urdf` | urdf | 15 · 10 · 20 · 15 · 10 · 0 · 0 |  |
| 60 | `robots/simple_humanoid_description/urdf/simple_humanoid_classical.urdf` | urdf | 15 · 10 · 20 · 15 · 0 · 0 · 0 |  |
| 25 | `robots/a1_description/urdf/a1.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 25 | `robots/alex_description/urdf/alex_nub_hands.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 21 visual mesh file(s) missing |
| 25 | `robots/alex_description/urdf/alex_psyonic_hands.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 29 visual mesh file(s) missing |
| 25 | `robots/alex_description/urdf/alex_sake_hands.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 23 visual mesh file(s) missing |
| 25 | `robots/alexander_description/urdf/alexander_v1.lowerBodyOnly.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 12 visual mesh file(s) missing |
| 25 | `robots/allegro_hand_description/urdf/allegro_left_hand.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 11 visual mesh file(s) missing |
| 25 | `robots/allegro_hand_description/urdf/allegro_right_hand.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 11 visual mesh file(s) missing |
| 25 | `robots/anymal_b_simple_description/robots/anymal-kinova.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 20 visual mesh file(s) missing |
| 25 | `robots/anymal_b_simple_description/robots/anymal.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |
| 25 | `robots/anymal_c_simple_description/urdf/anymal.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 19 visual mesh file(s) missing |
| 25 | `robots/asr_twodof_description/urdf/TwoDofs.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 4 visual mesh file(s) missing |
| 25 | `robots/b1_description/urdf/b1-z1.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 14 visual mesh file(s) missing |
| 25 | `robots/b1_description/urdf/b1.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 25 | `robots/baxter_description/urdf/baxter.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 15 visual mesh file(s) missing |
| 25 | `robots/bolt_description/robots/bolt.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 8 visual mesh file(s) missing |
| 25 | `robots/borinot_description/urdf/borinot_flying_arm_2.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 3 visual mesh file(s) missing |
| 25 | `robots/centauro_description/urdf/centauro.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 19 visual mesh file(s) missing |
| 25 | `robots/double_pendulum_description/urdf/double_pendulum.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 3 visual mesh file(s) missing |
| 25 | `robots/double_pendulum_description/urdf/double_pendulum_continuous.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 3 visual mesh file(s) missing |
| 25 | `robots/finger_edu_description/robots/finger_edu.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |
| 25 | `robots/g1_description/urdf/g1_29dof_rev_1_0.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 35 visual mesh file(s) missing |
| 25 | `robots/g1_description/urdf/g1_29dof_with_hand_rev_1_0.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 49 visual mesh file(s) missing |
| 25 | `robots/go1_description/urdf/go1.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |
| 25 | `robots/go2_description/urdf/go2.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |
| 25 | `robots/hector_description/robots/quadrotor_base.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `robots/hector_description/robots/quadrotor_base.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: Invalid argument: .\.\package://example-robot-data/robots/hector_description/urdf/quadrotor_base.urdf.xacro &#91;Errno 22&#93; Invalid argument: '.\\.\\package://example-robot-data/robots/hector_description/urdf/quadrotor_base.urdf.xacro' |
| 25 | `robots/hextilt_description/urdf/hextilt_flying_arm_5.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |
| 25 | `robots/human_description/robots/human.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 14 visual mesh file(s) missing |
| 25 | `robots/hyq_description/robots/hyq_no_sensors.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 4 visual mesh file(s) missing |
| 25 | `robots/icub_description/robots/icub.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 28 visual mesh file(s) missing |
| 25 | `robots/icub_description/robots/icub_reduced.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 28 visual mesh file(s) missing |
| 25 | `robots/iris_description/robots/iris.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 3 visual mesh file(s) missing |
| 25 | `robots/iris_description/robots/iris_simple.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 3 visual mesh file(s) missing |
| 25 | `robots/kinova_description/robots/kinova.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 11 visual mesh file(s) missing |
| 25 | `robots/laikago_description/urdf/laikago.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 25 | `robots/panda_description/urdf/panda.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 10 visual mesh file(s) missing |
| 25 | `robots/panda_description/urdf/panda_collision.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 10 visual mesh file(s) missing |
| | and 29 more, in `audit.json` | | | |

</details>

<details><summary><b>OrebroUniversity/yumi</b>: best 70, 4 robot(s), BSD-2-Clause, last commit 2019-08-19 **archived**</summary>

From: awesome-robot-descriptions. Commit `fb7f57df0544`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 70 | `yumi_description/urdf/yumi.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 5 · 4.6 |  |
| 15 | `yumi_description/urdf/Gazebo/gazebo.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `yumi_description/urdf/Util/materials.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `yumi_description/urdf/yumi.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: name 'yumi_parent' is not defined when evaluating expression 'yumi_parent' |

</details>

<details><summary><b>ros-industrial/fanuc</b>: best 70, 40 robot(s), NOASSERTION, last commit 2025-02-19</summary>

From: awesome-robot-descriptions. Commit `d8f42bd73584`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 70 | `fanuc_cr35ia_support/urdf/cr35ia.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_cr7ia_support/urdf/cr7ia.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_cr7ia_support/urdf/cr7ial.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_crx10ia_support/urdf/crx10ial.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200i_support/urdf/lrmate200i.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200ib_support/urdf/lrmate200ib.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200ib_support/urdf/lrmate200ib3l.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200ic_support/urdf/lrmate200ic.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200ic_support/urdf/lrmate200ic5f.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200ic_support/urdf/lrmate200ic5h.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200ic_support/urdf/lrmate200ic5hs.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200ic_support/urdf/lrmate200ic5l.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200id_support/urdf/lrmate200id.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200id_support/urdf/lrmate200id4s.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200id_support/urdf/lrmate200id4sc.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200id_support/urdf/lrmate200id4sh.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200id_support/urdf/lrmate200id7h.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200id_support/urdf/lrmate200id7l.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_lrmate200id_support/urdf/lrmate200id7lc.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m10ia_support/urdf/m10ia.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m10ia_support/urdf/m10ia7l.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m16ib_support/urdf/m16ib20.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m20ia_support/urdf/m20ia.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m20ia_support/urdf/m20ia10l.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m20ib_support/urdf/m20ib25.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m430ia_support/urdf/m430ia2f.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m430ia_support/urdf/m430ia2p.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m6ib_support/urdf/m6ib.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m6ib_support/urdf/m6ib6s.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m710ic_support/urdf/m710ic45m.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m710ic_support/urdf/m710ic50.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m900ia_support/urdf/m900ia260l.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_m900ib_support/urdf/m900ib700.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_r1000ia_support/urdf/r1000ia80f.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_r2000ib_support/urdf/r2000ib210f.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_r2000ic_support/urdf/r2000ic125l.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_r2000ic_support/urdf/r2000ic165f.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_r2000ic_support/urdf/r2000ic210f.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_r2000ic_support/urdf/r2000ic210l.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |
| 70 | `fanuc_r2000ic_support/urdf/r2000ic270f.xacro` | xacro | 15 · 5 · 20 · 15 · 0 · 5 · 10 |  |

</details>

<details><summary><b>ros-naoqi/nao_robot</b>: best 70, 45 robot(s), BSD-3-Clause, last commit 2018-10-31</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `67476469a137`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 70 | `nao_description/urdf/naoV32_generated_urdf/nao.urdf` | urdf | 15 · 0 · 20 · 15 · 10 · 0 · 10 |  |
| 60 | `nao_description/urdf/naoV32_generated_urdf/nao_sensors.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 0 · 0 |  |
| 60 | `nao_description/urdf/naoV33_generated_urdf/nao_sensors.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 0 · 0 |  |
| 60 | `nao_description/urdf/naoV40_generated_urdf/nao_sensors.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 0 · 0 |  |
| 60 | `nao_description/urdf/naoV50_generated_urdf/nao_sensors.xacro` | xacro | 15 · 0 · 20 · 15 · 10 · 0 · 0 |  |
| 15 | `nao_description/urdf/naoV32_generated_urdf/naoGazebo.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `nao_description/urdf/naoV32_generated_urdf/naoTransmission.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `nao_description/urdf/naoV32_generated_urdf/nao_arms.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_LShoulder |
| 15 | `nao_description/urdf/naoV32_generated_urdf/nao_fingers.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_RFinger23_link |
| 15 | `nao_description/urdf/naoV32_generated_urdf/nao_head.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_Neck |
| 15 | `nao_description/urdf/naoV32_generated_urdf/nao_legs.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_LPelvis |
| 15 | `nao_description/urdf/naoV32_generated_urdf/nao_material.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `nao_description/urdf/naoV32_generated_urdf/nao_torso.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_torso |
| 15 | `nao_description/urdf/naoV33_generated_urdf/nao.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 15 | `nao_description/urdf/naoV33_generated_urdf/naoGazebo.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `nao_description/urdf/naoV33_generated_urdf/naoTransmission.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `nao_description/urdf/naoV33_generated_urdf/nao_arms.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_LShoulder |
| 15 | `nao_description/urdf/naoV33_generated_urdf/nao_fingers.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_RFinger23_link |
| 15 | `nao_description/urdf/naoV33_generated_urdf/nao_head.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_Neck |
| 15 | `nao_description/urdf/naoV33_generated_urdf/nao_legs.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_LPelvis |
| 15 | `nao_description/urdf/naoV33_generated_urdf/nao_material.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `nao_description/urdf/naoV33_generated_urdf/nao_torso.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_torso |
| 15 | `nao_description/urdf/naoV40_generated_urdf/nao.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 15 | `nao_description/urdf/naoV40_generated_urdf/naoGazebo.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `nao_description/urdf/naoV40_generated_urdf/naoTransmission.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `nao_description/urdf/naoV40_generated_urdf/nao_arms.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_LShoulder |
| 15 | `nao_description/urdf/naoV40_generated_urdf/nao_fingers.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_RFinger23_link |
| 15 | `nao_description/urdf/naoV40_generated_urdf/nao_head.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_Neck |
| 15 | `nao_description/urdf/naoV40_generated_urdf/nao_legs.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_LPelvis |
| 15 | `nao_description/urdf/naoV40_generated_urdf/nao_material.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `nao_description/urdf/naoV40_generated_urdf/nao_torso.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_torso |
| 15 | `nao_description/urdf/naoV50_generated_urdf/nao.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 15 | `nao_description/urdf/naoV50_generated_urdf/naoGazebo.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `nao_description/urdf/naoV50_generated_urdf/naoTransmission.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `nao_description/urdf/naoV50_generated_urdf/nao_arms.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_LShoulder |
| 15 | `nao_description/urdf/naoV50_generated_urdf/nao_fingers.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_RFinger13_link |
| 15 | `nao_description/urdf/naoV50_generated_urdf/nao_head.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_Neck |
| 15 | `nao_description/urdf/naoV50_generated_urdf/nao_legs.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_LPelvis |
| 15 | `nao_description/urdf/naoV50_generated_urdf/nao_material.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 15 | `nao_description/urdf/naoV50_generated_urdf/nao_torso.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: unknown macro name: xacro:insert_visu_torso |
| | and 5 more, in `audit.json` | | | |

</details>

<details><summary><b>a-price/robotiq_arg85_description</b>: best 68, 1 robot(s), no licence named, last commit 2020-05-19</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `a65190bdbb06`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 68 | `robots/robotiq_arg85_description.URDF` | urdf | 7.5 · 0 · 20 · 15 · 10 · 5 · 10 |  |

</details>

<details><summary><b>bbokser/spryped</b>: best 68, 1 robot(s), GPL-3.0, last commit 2021-07-05</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `f360a6b78667`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 68 | `spryped_urdf_rev06/urdf/spryped_urdf_rev06.urdf` | urdf | 15 · 0 · 20 · 7.5 · 10 · 5 · 10 |  |

</details>

<details><summary><b>poppy-project/poppy_torso_description</b>: best 68, 1 robot(s), no licence named, last commit 2017-02-16</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `6beeec3d76fb`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 68 | `urdf/Poppy_Torso.URDF` | urdf | 7.5 · 0 · 20 · 15 · 10 · 5 · 10 |  |

</details>

<details><summary><b>Rhoban/sigmaban_urdf</b>: best 68, 1 robot(s), MIT, last commit 2022-10-14</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `d5d023fd3580`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 68 | `robot.urdf` | urdf | 15 · 0 · 20 · 7.5 · 10 · 5 · 10 |  |

</details>

<details><summary><b>Rayckey/GingerURDF</b>: best 67, 1 robot(s), no licence named, last commit 2019-02-13</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `6a1307cd0ee2`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 67 | `urdf/gingerurdf.urdf` | urdf | 7.5 · 0 · 20 · 15 · 10 · 5 · 9.1 |  |

</details>

<details><summary><b>AgibotTech/agibot_x1_train</b>: best 58, 2 robot(s), no licence named, last commit 2024-10-23</summary>

From: awesome-robot-descriptions. Commit `e6651b9ab843`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 58 | `resources/robots/x1/urdf/x1.urdf` | urdf | 0 · 5 · 20 · 15 · 10 · 5 · 2.6 |  |
| 5 | `resources/robots/x1/mjcf/robot/xyber_x1/xyber_x1_serial.xml` | mjcf | 0 · 5 · 0 · 0 · 0 · 0 · 0 | 30 visual mesh file(s) missing |

</details>

<details><summary><b>rohanpsingh/cassie_mj_description</b>: best 57, 1 robot(s), no licence named, last commit 2021-12-28</summary>

From: robot_descriptions.py. Commit `fcc3775453e4`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 57 | `xml/cassie.xml` | mjcf | 0 · 0 · 20 · 12 · 10 · 5 · 10 |  |

</details>

<details><summary><b>fiveages-sim/robot_descriptions/humanoid/realman/rs01_description</b>: best 25, 3 robot(s), Apache-2.0, last commit 2026-09-08</summary>

From: fiveages robots. Commit `bd491829961a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 25 | `humanoid/realman/rs01_description/xacro/component.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `humanoid/realman/rs01_description/xacro/robot.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 25 | `humanoid/realman/rs01_description/xacro/ros2_control/robot.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |

</details>

<details><summary><b>flexivrobotics/flexiv_description</b>: best 25, 1 robot(s), Apache-2.0, last commit 2026-11-16</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `2fc4f62329fa`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 25 | `urdf/flexiv.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: can only concatenate str (not "bool") to str when evaluating expression ''$(arg kinematics_parameters_file)' if '$(arg kinematics_parameters_file)' != '' else cfg + '/' + robot_type_str + '/default_kinematics.yaml'' when evaluating expression 'single_kinematics' |

</details>

<details><summary><b>gbionics/gb-robot-models</b>: best 25, 1 robot(s), NOASSERTION, last commit 2026-07-28</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `3377978fefa3`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 25 | `share/gb_robot_models/robots/gene01_0/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 71 visual mesh file(s) missing |

</details>

<details><summary><b>pal-robotics/pal_urdf_utils</b>: best 25, 1 robot(s), Apache-2.0, last commit 2026-10-06</summary>

From: robot_descriptions.py. Commit `e8600a339a3a`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 25 | `urdf/materials.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |

</details>

<details><summary><b>RobotnikAutomation/robotnik_description</b>: best 25, 16 robot(s), BSD-3-Clause, last commit 2026-11-11</summary>

From: awesome-robot-descriptions. Commit `48b4d3cbe9c9`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 25 | `robots/rb1/rb1.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotnik_sensors Package not found: robotnik_sensors |
| 25 | `robots/rbcar/rbcar.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotnik_sensors Package not found: robotnik_sensors |
| 25 | `robots/rbfiqus/rbfiqus.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotnik_sensors Package not found: robotnik_sensors |
| 25 | `robots/rbkairos/rbkairos.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotnik_sensors Package not found: robotnik_sensors |
| 25 | `robots/rbkairos/rbkairos_plus.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: &lt;cache&gt;/ros-industrial__universal_robot/ur_description/urdf/ur_macro.xacro &#91;Errno 2&#93; No such file or directory: '&lt;cache&gt;/ros-industrial__universal_robot/ur_description/urdf/ur_macro.xacro' |
| 25 | `robots/rbrobout/rbrobout.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotnik_sensors Package not found: robotnik_sensors |
| 25 | `robots/rbrobout/rbrobout_plus.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: &lt;cache&gt;/ros-industrial__universal_robot/ur_description/urdf/ur_macro.xacro &#91;Errno 2&#93; No such file or directory: '&lt;cache&gt;/ros-industrial__universal_robot/ur_description/urdf/ur_macro.xacro' |
| 25 | `robots/rbsummit/rbsummit.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotnik_sensors Package not found: robotnik_sensors |
| 25 | `robots/rbsummit_steel/rbsummit_steel.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotnik_sensors Package not found: robotnik_sensors |
| 25 | `robots/rbtheron/rbtheron.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotnik_sensors Package not found: robotnik_sensors |
| 25 | `robots/rbtheron/rbtheron_plus.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: &lt;cache&gt;/ros-industrial__universal_robot/ur_description/urdf/ur_macro.xacro &#91;Errno 2&#93; No such file or directory: '&lt;cache&gt;/ros-industrial__universal_robot/ur_description/urdf/ur_macro.xacro' |
| 25 | `robots/rbvogui/rbvogui.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotnik_sensors Package not found: robotnik_sensors |
| 25 | `robots/rbvogui/rbvogui_plus.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: &lt;cache&gt;/ros-industrial__universal_robot/ur_description/urdf/ur_macro.xacro &#91;Errno 2&#93; No such file or directory: '&lt;cache&gt;/ros-industrial__universal_robot/ur_description/urdf/ur_macro.xacro' |
| 25 | `robots/rbvogui_xl/rbvogui_xl.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotnik_sensors Package not found: robotnik_sensors |
| 25 | `robots/rbwatcher/rbwatcher.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: robotnik_sensors Package not found: robotnik_sensors |
| 25 | `urdf/bodies/rb1/rb1_base.urdf.xacro` | xacro | 15 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: &lt;cache&gt;/limxdynamics__tron1-robot-description/urdf/bases/rb1_base_v3.urdf.xacro &#91;Errno 2&#93; No such file or directory: '&lt;cache&gt;/limxdynamics__tron1-robot-description/urdf/bases/rb1_base_v3.urdf.xacro' |

</details>

<details><summary><b>robotology/icub-models</b>: best 25, 19 robot(s), CC-BY-SA-4.0, last commit 2026-02-26</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `dca8c618c264`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 25 | `iCub/robots/iCubDarmstadt01/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubErzelli02/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubGazeboV2_5/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubGazeboV2_5_KIT_007/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubGazeboV2_6/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubGazeboV2_7/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubGenova01/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubGenova02/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubGenova03/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 28 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubGenova04/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubGenova11/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubLisboa01/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 28 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubNancy01/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 28 visual mesh file(s) missing |
| 25 | `iCub/robots/iCubWaterloo01/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |
| 25 | `iCub/robots/left_hand_mk3/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 12 visual mesh file(s) missing |
| 25 | `iCub/robots/left_wrist_mk2/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 4 visual mesh file(s) missing |
| 25 | `iCub_creo2urdf/robots/iCubGazeboV2_10/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 41 visual mesh file(s) missing |
| 25 | `iCub_creo2urdf/robots/iCubStanford01/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 41 visual mesh file(s) missing |
| 25 | `iCub_manual/robots/iCubGazeboV2_5_visuomanip/model.urdf` | urdf | 15 · 10 · 0 · 0 · 0 · 0 · 0 | 37 visual mesh file(s) missing |

</details>

<details><summary><b>G-Levine/rhea_description</b>: best 20, 2 robot(s), MIT, last commit 2024-02-21</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `cd305cf289e8`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 20 | `description/rhea.urdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |
| 20 | `description/urdf/rhea.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |

</details>

<details><summary><b>husky/husky</b>: best 20, 2 robot(s), BSD-3-Clause, last commit 2025-10-01</summary>

From: awesome-robot-descriptions. Commit `41e15d283a8d`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 20 | `husky_description/urdf/decorations.urdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | renders no links with its default arguments |
| 20 | `husky_description/urdf/husky.urdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: fath_pivot_mount_description Package not found: fath_pivot_mount_description |

</details>

<details><summary><b>jackal/jackal</b>: best 20, 2 robot(s), BSD-3-Clause, last commit 2024-05-24</summary>

From: awesome-robot-descriptions. Commit `4ddf9b578bb7`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 20 | `jackal_description/urdf/accessories.urdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: sick_tim Package not found: sick_tim |
| 20 | `jackal_description/urdf/jackal.urdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: sick_tim Package not found: sick_tim |

</details>

<details><summary><b>ridgeback/ridgeback</b>: best 20, 2 robot(s), BSD-3-Clause, last commit 2024-07-22</summary>

From: awesome-robot-descriptions. Commit `7f2489993f13`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 20 | `ridgeback_description/urdf/accessories.urdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: lms1xx Package not found: lms1xx |
| 20 | `ridgeback_description/urdf/ridgeback.urdf.xacro` | xacro | 15 · 5 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: lms1xx Package not found: lms1xx |

</details>

<details><summary><b>s1lent4gnt/koch-v1-1</b>: best 20, 1 robot(s), Apache-2.0, last commit 2025-02-25</summary>

From: awesome-robot-descriptions. Commit `cc1a4eb9b279`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 20 | `simulation/follower.urdf` | urdf | 15 · 5 · 0 · 0 · 0 · 0 · 0 | 13 visual mesh file(s) missing |

</details>

<details><summary><b>hello-robot/stretch4_urdf</b>: best 18, 8 robot(s), NOASSERTION, last commit 2026-11-06</summary>

From: robot_descriptions.py. Commit `46aaace1c235`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 18 | `stretch4_urdf/SE4.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | XacroException: No such file or directory: .\.\none/SE4_none/xacro/stretch_main.xacro &#91;Errno 2&#93; No such file or directory: '.\\.\\none/SE4_none/xacro/stretch_main.xacro' |
| 18 | `stretch4_urdf/SE4_accessories/docking_station/docking_station.urdf` | urdf | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 4 visual mesh file(s) missing |
| 18 | `stretch4_urdf/SE4_francis/xacro/stretch_main.xacro` | xacro | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 20 visual mesh file(s) missing |
| 18 | `stretch4_urdf/SE4_tools/eoa_wrist_dw4_tool_calibration/eoa_wrist_dw4_tool_calibration.urdf` | urdf | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |
| 18 | `stretch4_urdf/SE4_tools/eoa_wrist_dw4_tool_pg4/eoa_wrist_dw4_tool_pg4.urdf` | urdf | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 18 | `stretch4_urdf/SE4_tools/eoa_wrist_dw4_tool_sg4/eoa_wrist_dw4_tool_sg4.urdf` | urdf | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |
| 18 | `stretch4_urdf/SE4_tools/eoa_wrist_dw4_tool_sg4_v2/eoa_wrist_dw4_tool_sg4.urdf` | urdf | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |
| 18 | `stretch4_urdf/SE4_tools/eoa_wrist_dw4_tool_tablet/eoa_wrist_dw4_tool_tablet.urdf` | urdf | 7.5 · 10 · 0 · 0 · 0 · 0 · 0 | 1 visual mesh file(s) missing |

</details>

<details><summary><b>dingo-cpr/dingo</b>: best 15, 4 robot(s), BSD-3-Clause, last commit 2023-04-24</summary>

From: awesome-robot-descriptions. Commit `68806fdffabf`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 15 | `dingo_description/urdf/accessories.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: sick_tim Package not found: sick_tim |
| 15 | `dingo_description/urdf/dingo-d.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: sick_tim Package not found: sick_tim |
| 15 | `dingo_description/urdf/dingo-o.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: sick_tim Package not found: sick_tim |
| 15 | `dingo_description/urdf/dingo.urdf.xacro` | xacro | 15 · 0 · 0 · 0 · 0 · 0 · 0 | XacroException: &lt;class 'xacrodoc.packages.PackageNotFoundError'&gt;: Package not found: sick_tim Package not found: sick_tim |

</details>

<details><summary><b>ianathompson/eDO_description</b>: best 15, 1 robot(s), BSD-3-Clause, last commit 2018-03-01</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `17b3f92f8347`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 15 | `robots/edo_sim.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |

</details>

<details><summary><b>robot-descriptions/fanuc_m710ic_description</b>: best 15, 1 robot(s), BSD-3-Clause, last commit 2023-05-23 **archived**</summary>

From: awesome-robot-descriptions. Commit `bd15b7138c68`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 15 | `urdf/m710ic70.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 7 visual mesh file(s) missing |

</details>

<details><summary><b>shbang91/draco3_description</b>: best 15, 1 robot(s), BSD-2-Clause, last commit 2023-02-21</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `5afd19733d7b`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 15 | `urdf/draco3.urdf` | urdf | 15 · 0 · 0 · 0 · 0 · 0 · 0 | 33 visual mesh file(s) missing |

</details>

<details><summary><b>robot-descriptions/jaxon_description</b>: best 8, 1 robot(s), NOASSERTION, last commit 2022-10-03 **archived**</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `4a0cb7a4a737`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 8 | `urdf/jaxon_jvrc.urdf` | urdf | 7.5 · 0 · 0 · 0 · 0 · 0 · 0 | 39 visual mesh file(s) missing |

</details>

<details><summary><b>adubredu/DigitRobot.jl</b>: best 0, 1 robot(s), no licence named, last commit 2023-08-23</summary>

From: awesome-robot-descriptions. Commit `bd3b99e2297c`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 0 | `urdf/digit_model.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 14 visual mesh file(s) missing |

</details>

<details><summary><b>gkjohnson/nasa-urdf-robots</b>: best 0, 37 robot(s), no licence named, last commit 2022-12-02</summary>

From: awesome-robot-descriptions, robot_descriptions.py. Commit `1f89ecba9112`.

| Score | Robot | Kind | Parts: licence · alive · flattens · limits · inertia · look · weight | Note |
|--:|---|---|---|---|
| 0 | `r2_description/robots/r2_left_forearm.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 8 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2_left_gripper.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 2 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2b.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 32 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2b_control.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 30 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2b_dynamics.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 21 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2b_sim_upperbody_control.urdf.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 25 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2b_sim_upperbody_dynamics.urdf.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 16 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c1.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 32 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c1_control.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 30 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c1_dynamics.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 21 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c5.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 28 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c5_control.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 25 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c5_dynamics.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 16 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c6.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 32 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c6_control.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 30 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c6_dynamics.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 21 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c6_valve.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 32 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c_sim_full_control.urdf.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 30 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c_sim_full_dynamics.urdf.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 21 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c_sim_legs_control.urdf.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c_sim_legs_dynamics.urdf.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 5 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c_sim_upperbody_control.urdf.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 25 visual mesh file(s) missing |
| 0 | `r2_description/robots/r2c_sim_upperbody_dynamics.urdf.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 16 visual mesh file(s) missing |
| 0 | `val_description/model/robots/forearm_left.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 16 visual mesh file(s) missing |
| 0 | `val_description/model/robots/forearm_right.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 16 visual mesh file(s) missing |
| 0 | `val_description/model/robots/valkyrie_A.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 55 visual mesh file(s) missing |
| 0 | `val_description/model/robots/valkyrie_A_arm_mass_sims.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 23 visual mesh file(s) missing |
| 0 | `val_description/model/robots/valkyrie_B.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 55 visual mesh file(s) missing |
| 0 | `val_description/model/robots/valkyrie_B_arm_mass_sims.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 23 visual mesh file(s) missing |
| 0 | `val_description/model/robots/valkyrie_C.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 55 visual mesh file(s) missing |
| 0 | `val_description/model/robots/valkyrie_C_arm_mass_sims.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 23 visual mesh file(s) missing |
| 0 | `val_description/model/robots/valkyrie_D.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 55 visual mesh file(s) missing |
| 0 | `val_description/model/robots/valkyrie_D_arm_mass_sims.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 23 visual mesh file(s) missing |
| 0 | `val_description/model/robots/valkyrie_sim.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 56 visual mesh file(s) missing |
| 0 | `val_description/model/robots/valkyrie_sim_angled_legj1s.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 56 visual mesh file(s) missing |
| 0 | `val_description/model/robots/valkyrie_sim_arm_mass_sims.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 24 visual mesh file(s) missing |
| 0 | `val_description/model/robots/valkyrie_sim_gazebo_sync.urdf` | urdf | 0 · 0 · 0 · 0 · 0 · 0 · 0 | 56 visual mesh file(s) missing |

</details>

## Candidates with no robot file

Cloned, but holding no URDF, robot xacro or MJCF robot (SDF, meshes only, or another layout).

- [fiveages-sim/robot_descriptions/manipulator/hightorque/panthera_ht_description](https://github.com/fiveages-sim/robot_descriptions/tree/HEAD/manipulator/hightorque/panthera_ht_description)
- [gbionics/awesome-urdf](https://github.com/gbionics/awesome-urdf)
- [jhu-lcsr-attic/bhand_model](https://github.com/jhu-lcsr-attic/bhand_model)
- [ros-naoqi/nao_meshes](https://github.com/ros-naoqi/nao_meshes)
- [start-jsk/rtmros_choreonoid](https://github.com/start-jsk/rtmros_choreonoid)
- [stephane-caron/awesome-open-source-robots](https://github.com/stephane-caron/awesome-open-source-robots)
- [stephane-caron/openrave_models](https://github.com/stephane-caron/openrave_models)

## Could not be audited

- [fiveages-sim/agibot-g2-description](https://github.com/fiveages-sim/agibot-g2-description): GitHub: GET repos/fiveages-sim/agibot-g2-description: not found
- [fiveages-sim/fa-w2r-description](https://github.com/fiveages-sim/fa-w2r-description): GitHub: GET repos/fiveages-sim/fa-w2r-description: not found
- [fiveages-sim/robot-descriptions-ubtech](https://github.com/fiveages-sim/robot-descriptions-ubtech): GitHub: GET repos/fiveages-sim/robot-descriptions-ubtech: not found

