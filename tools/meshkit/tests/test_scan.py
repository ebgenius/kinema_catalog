"""scan against a small synthetic catalog, laid out the way the real one is."""

from pathlib import Path

import pytest

from meshkit.scan import scan

DAE = """<?xml version="1.0"?>
<COLLADA><asset><unit meter="1"/><up_axis>{axis}</up_axis></asset></COLLADA>
"""


def write(root: Path, relative: str, text: str = "") -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def catalog(tmp_path: Path) -> Path:
    arm = "src/arm_fork/arm_description"
    write(tmp_path, f"{arm}/package.xml", "<package><name>arm_description</name></package>")
    for name in ("link0", "link1"):
        write(tmp_path, f"{arm}/meshes/visual/{name}.dae", DAE.format(axis="Z_UP"))
        write(tmp_path, f"{arm}/meshes/collision/{name}.dae", DAE.format(axis="Y_UP"))
    write(tmp_path, f"{arm}/meshes/unused/spare.dae", DAE.format(axis="Z_UP"))
    write(tmp_path, f"{arm}/urdf/arm.urdf.xacro", """<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="arm">
  <xacro:macro name="link" params="name">
    <link name="${name}">
      <visual><geometry>
        <mesh filename="package://arm_description/meshes/visual/${name}.dae"/>
      </geometry></visual>
      <collision><geometry>
        <mesh filename="package://arm_description/meshes/collision/${name}.dae"/>
      </geometry></collision>
      <collision><geometry><mesh filename="${name}.stl"/></geometry></collision>
      <!-- <visual><mesh filename="package://arm_description/meshes/unused/spare.dae"/></visual> -->
    </link>
  </xacro:macro>
  <xacro:link name="link0"/>
  <xacro:link name="link1"/>
</robot>
""")

    # Universal Robots style: meshes named in YAML, with custom tags.
    ur = "src/ur_fork/ur_description"
    write(tmp_path, f"{ur}/package.xml", "<package><name>ur_description</name></package>")
    write(tmp_path, f"{ur}/meshes/ur5/visual/base.dae", DAE.format(axis="Z_UP"))
    write(tmp_path, f"{ur}/config/ur5/visual_parameters.yaml", """
offsets:
  shoulder_offset: !degrees 90.0
mesh_files:
  base:
    visual:
      mesh:
        package: ur_description
        path: meshes/ur5/visual/base.dae
""")

    # Only a rendered robot can say which of these it uses.
    param = "src/param_fork/param_description"
    write(tmp_path, f"{param}/package.xml", "<package><name>param_description</name></package>")
    write(tmp_path, f"{param}/meshes/a.dae", DAE.format(axis="Z_UP"))
    write(tmp_path, f"{param}/meshes/b.dae", DAE.format(axis="Z_UP"))
    write(tmp_path, f"{param}/urdf/common.xacro", """<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:macro name="mlink" params="mesh_path mesh_filename">
    <link name="${mesh_filename}"><visual><geometry>
      <mesh filename="${mesh_path}/${mesh_filename}"/>
    </geometry></visual></link>
  </xacro:macro>
</robot>
""")
    write(tmp_path, f"{param}/urdf/robot.urdf.xacro", """<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="p">
  <xacro:arg name="which" default="a"/>
  <xacro:include filename="$(find param_description)/urdf/common.xacro"/>
  <xacro:mlink mesh_path="package://param_description/meshes" mesh_filename="$(arg which).dae"/>
</robot>
""")

    write(tmp_path, "docker/robots.tsv",
          "# id\tfamily\tsubmodule\ttype\tpath\targs\tmesh_base\tlabel\n"
          f"p\tarm\tparam_fork\txacro\t{param}/urdf/robot.urdf.xacro\twhich:=b\t-\tP\n")
    return tmp_path


def roles(inventory, fork):
    return {m.path.relative_to(inventory.root / "src").as_posix(): m.roles
            for m in inventory.in_fork(fork)}


def test_visual_and_collision_come_from_the_reference(catalog):
    found = roles(scan(catalog, render=False), "arm_fork")
    base = "arm_fork/arm_description/meshes"
    assert found[f"{base}/visual/link0.dae"] == {"visual"}
    assert found[f"{base}/visual/link1.dae"] == {"visual"}
    assert found[f"{base}/collision/link0.dae"] == {"collision"}


def test_commented_references_do_not_count(catalog):
    found = roles(scan(catalog, render=False), "arm_fork")
    assert found["arm_fork/arm_description/meshes/unused/spare.dae"] == set()


def test_a_literal_stl_is_not_an_unresolved_dae(catalog):
    assert scan(catalog, render=False).unresolved("arm_fork") == []


def test_yaml_with_custom_tags_is_read(catalog):
    found = roles(scan(catalog, render=False), "ur_fork")
    assert found["ur_fork/ur_description/meshes/ur5/visual/base.dae"] == {"visual"}


def test_up_axis_is_read(catalog):
    inventory = scan(catalog, render=False)
    axes = {m.path.parent.name: m.up_axis for m in inventory.in_fork("arm_fork")}
    assert axes["visual"] == "Z_UP" and axes["collision"] == "Y_UP"


def test_all_variable_reference_is_unresolved_not_greedy(catalog):
    inventory = scan(catalog, render=False)
    assert all(not m.roles for m in inventory.in_fork("param_fork"))
    assert any("all variables" in (r.problem or "") for r in inventory.unresolved("param_fork"))


def test_rendered_manifest_robot_resolves_exactly(catalog):
    found = roles(scan(catalog), "param_fork")
    assert found["param_fork/param_description/meshes/b.dae"] == {"visual"}
    assert found["param_fork/param_description/meshes/a.dae"] == set()
