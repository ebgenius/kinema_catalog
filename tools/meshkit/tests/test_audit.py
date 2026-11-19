"""meshkit audit: finding robots, measuring them, scoring them."""

import json
import struct
from datetime import datetime, timezone
from pathlib import Path

import pytest

from meshkit import audit

NOW = datetime(2026, 11, 19, tzinfo=timezone.utc)

XACRO = 'xmlns:xacro="http://www.ros.org/wiki/xacro"'


def write(path: Path, text: str | bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")
    return path


def binary_stl(triangles: int) -> bytes:
    return b"\0" * 80 + struct.pack("<I", triangles) + b"\0" * (50 * triangles)


# ------------------------------------------------------------- finding robots

@pytest.mark.parametrize("name, text, kind", [
    ("arm.urdf", '<robot name="arm"><link name="a"/></robot>', "urdf"),
    ("empty.urdf", '<robot name="arm"/>', None),
    ("arm.urdf.xacro", f'<robot {XACRO} name="arm"><xacro:include filename="m.xacro"/>'
                       '<xacro:arm prefix=""/></robot>', "xacro"),
    ("macros.xacro", f'<robot {XACRO}><xacro:macro name="arm" params="prefix">'
                     '<link name="${prefix}a"/></xacro:macro></robot>', None),
    ("wiki.xacro", '<robot xmlns:xacro="http://wiki.ros.org/xacro"><xacro:property '
                   'name="x" value="1"/></robot>', None),
    ("model.xml", '<mujoco model="arm"><worldbody><body name="b"/></worldbody></mujoco>',
     "mjcf"),
    ("scene.xml", '<mujoco><include file="arm.xml"/><worldbody><geom type="plane"/>'
                  '</worldbody></mujoco>', None),
    ("other.xml", "<launch/>", None),
    ("broken.urdf", "<robot", None),
])
def test_a_robot_file_is_one_that_describes_a_robot_of_its_own(tmp_path, name, text, kind):
    assert audit.robot_kind(write(tmp_path / name, text)) == kind


def test_robots_are_found_and_build_dirs_skipped(tmp_path):
    write(tmp_path / "a" / "urdf" / "a.urdf", '<robot name="a"><link name="l"/></robot>')
    write(tmp_path / "build" / "a.urdf", '<robot name="a"><link name="l"/></robot>')
    write(tmp_path / ".git" / "a.urdf", '<robot name="a"><link name="l"/></robot>')
    assert [p.relative_to(tmp_path).as_posix() for p, _ in audit.find_robots(tmp_path)] == [
        "a/urdf/a.urdf"]


# --------------------------------------------------------------------- meshes

def test_mesh_facts_read_each_format_without_a_mesh_library(tmp_path):
    stl = audit.mesh_facts(write(tmp_path / "a.stl", binary_stl(12)))
    assert (stl["triangles"], stl["normals"], stl["materials"]) == (12, False, False)
    ascii_stl = audit.mesh_facts(write(tmp_path / "b.STL", "solid x\n" + "facet normal 0 0 1\n"
                                       "outer loop\nendloop\nendfacet\n" * 3 + "endsolid x\n"))
    assert ascii_stl["triangles"] == 3
    obj = audit.mesh_facts(write(tmp_path / "c.obj", "mtllib c.mtl\nv 0 0 0\nvn 0 0 1\n"
                                 "usemtl red\nf 1 2 3\nf 1 2 3 4\n"))
    assert (obj["triangles"], obj["normals"], obj["materials"]) == (3, True, True)
    dae = audit.mesh_facts(write(tmp_path / "d.dae", '<COLLADA><library_materials><material '
                                 'id="m"/></library_materials><triangles count="7">'
                                 '<input semantic="NORMAL"/></triangles></COLLADA>'))
    assert (dae["triangles"], dae["normals"], dae["materials"]) == (7, True, True)
    bare = audit.mesh_facts(write(tmp_path / "e.dae", '<COLLADA><polylist count="4"/>'
                                  '</COLLADA>'))
    assert (bare["triangles"], bare["normals"], bare["materials"]) == (4, False, False)


def test_a_glb_is_read_from_its_json_chunk(tmp_path):
    document = json.dumps({"accessors": [{"count": 30}],
                           "meshes": [{"primitives": [{"attributes": {"POSITION": 0,
                                                                      "NORMAL": 0},
                                                       "indices": 0}]}],
                           "materials": [{"name": "orange"}]}).encode()
    document += b" " * (-len(document) % 4)
    glb = (b"glTF" + struct.pack("<II", 2, 20 + len(document))
           + struct.pack("<I", len(document)) + b"JSON" + document)
    facts = audit.mesh_facts(write(tmp_path / "a.glb", glb))
    assert (facts["triangles"], facts["normals"], facts["materials"]) == (10, True, True)


def test_a_mesh_left_in_git_lfs_is_named_not_counted(tmp_path):
    facts = audit.mesh_facts(write(tmp_path / "a.stl", "version https://git-lfs.github.com/"
                                   "spec/v1\noid sha256:00\nsize 99\n"))
    assert facts["error"] == "in Git LFS, not fetched" and facts["triangles"] is None


# ---------------------------------------------------------------- measuring

def urdf(*body: str) -> str:
    return '<robot name="arm">' + "".join(body) + "</robot>"


def link(name, mesh=None, mass=None, colour=False):
    visual = ""
    if mesh is not None:
        material = '<material name="m"><color rgba="1 0 0 1"/></material>' if colour else ""
        visual = f'<visual><geometry><mesh filename="{mesh}"/></geometry>{material}</visual>'
    inertial = f'<inertial><mass value="{mass}"/></inertial>' if mass is not None else ""
    return f'<link name="{name}">{visual}{inertial}</link>'


def joint(kind, lower=None, upper=None, velocity=None):
    attributes = "".join(f' {k}="{v}"' for k, v in
                         (("lower", lower), ("upper", upper), ("velocity", velocity))
                         if v is not None)
    limit = f"<limit{attributes}/>" if attributes else ""
    return f'<joint name="j{kind}" type="{kind}"><parent link="a"/><child link="b"/>{limit}</joint>'


def test_limits_inertia_and_meshes_are_measured_from_the_urdf(tmp_path):
    write(tmp_path / "pkg" / "meshes" / "a.dae",
          '<COLLADA><material id="m"/><triangles count="5"><input semantic="NORMAL"/>'
          "</triangles></COLLADA>")
    write(tmp_path / "pkg" / "meshes" / "b.stl", binary_stl(3))
    text = urdf(link("a", "package://pkg/meshes/a.dae", mass=1),
                link("b", "../meshes/b.stl", colour=True),
                link("c", "package://pkg/meshes/gone.stl", mass=2),
                link("frame"),
                joint("revolute", -1, 1, 2), joint("prismatic", 0, 0, 1),
                joint("continuous"), joint("fixed"))
    source = write(tmp_path / "pkg" / "urdf" / "arm.urdf", text)
    result = audit.measure_urdf(text, source, {"pkg": str(tmp_path / "pkg")})
    assert result["links"] == 4 and result["moving_joints"] == 3
    # prismatic 0..0 has no range; continuous needs none.
    assert result["limited_share"] == round(2 / 3, 3)
    # A wheel's continuous joint is not asked for a velocity.
    assert result["velocity_share"] == 1.0
    # "frame" has no geometry, so only a, b and c are asked for a mass.
    assert result["inertia_share"] == round(2 / 3, 3)
    assert result["missing_count"] == 1 and result["missing_meshes"][0].endswith("gone.stl")
    assert result["formats"] == {"dae": 1, "stl": 1}
    assert result["normals_share"] == 0.5          # the DAE has normals, the STL none
    # a.dae's own material is a point, b's whole-part colour half, the missing one nothing.
    assert result["materials_share"] == 0.5
    assert result["triangles"] == 8


def test_a_missing_mesh_means_it_does_not_flatten(tmp_path):
    text = urdf(link("a", "meshes/none.stl"))
    path = write(tmp_path / "a.urdf", text)
    result = audit.measure(path, "urdf", {})
    assert result["flattened"] is False and result["error"] == "1 visual mesh file(s) missing"


def test_a_xacro_that_cannot_be_evaluated_is_an_error_on_its_row(tmp_path):
    path = write(tmp_path / "a.urdf.xacro", f'<robot {XACRO}><xacro:include '
                 'filename="$(find nowhere)/a.xacro"/><xacro:a/></robot>')
    result = audit.measure(path, "xacro", {})
    assert result["flattened"] is False and result["error"]


def test_mjcf_includes_are_followed_and_meshes_found(tmp_path):
    write(tmp_path / "assets" / "base.obj", "v 0 0 0\nvn 0 0 1\nusemtl a\nf 1 1 1\n")
    write(tmp_path / "arm.xml", '<mujoco model="arm"><compiler meshdir="assets"/>'
          '<asset><mesh file="base.obj"/></asset><worldbody><body name="b">'
          '<joint type="hinge" range="-1 1"/><joint type="slide"/><geom type="mesh" '
          'mesh="base" material="m"/></body><body name="c"><inertial mass="1" pos="0 0 0"/>'
          "</body></worldbody></mujoco>")
    scene = write(tmp_path / "scene.xml", '<mujoco><include file="arm.xml"/></mujoco>')
    result = audit.measure(scene, "mjcf", {})
    assert result["flattened"] and result["name"] is None
    assert result["moving_joints"] == 2 and result["limited_share"] == 0.5
    assert result["velocity_share"] is None        # MJCF has no velocity limits
    assert result["inertia_share"] == 1.0          # from the geom, and an explicit one
    assert result["formats"] == {"obj": 1} and result["normals_share"] == 1.0


# ------------------------------------------------------------------- scoring

def row(**fields):
    base = {"licence": "BSD-3-Clause", "licence_file": True,
            "last_commit": "2026-10-01T00:00:00Z", "archived": False, "flattened": True,
            "moving_joints": 6, "limited_share": 1.0, "velocity_share": 1.0,
            "inertia_share": 1.0, "normals_share": 1.0, "materials_share": 1.0,
            "visuals": 7, "triangles": 100_000, "megabytes": 10}
    return base | fields


def test_a_complete_robot_scores_100():
    assert audit.score(row(), today=NOW) == (100, {k: float(v) for k, v in
                                                   audit.WEIGHTS.items()})


def test_each_part_scores_what_it_measures():
    total, parts = audit.score(row(licence="NOASSERTION", last_commit="2024-06-01T00:00:00Z",
                                   velocity_share=0.0, inertia_share=0.5, normals_share=0.0,
                                   materials_share=0.5, triangles=1_100_000), today=NOW)
    assert parts == {"licence": 7.5, "alive": 5.0, "flattens": 20.0, "limits": 7.5,
                     "inertia": 5.0, "look": 5.0, "weight": 5.0}
    assert total == 55


def test_what_does_not_flatten_keeps_only_licence_and_activity():
    total, parts = audit.score(row(flattened=False, archived=True), today=NOW)
    assert parts["licence"] == 15 and parts["alive"] == 0
    assert total == 15


def test_mjcf_is_not_asked_for_velocity_limits():
    _, parts = audit.score(row(velocity_share=None, limited_share=0.5), today=NOW)
    assert parts["limits"] == 7.5


def test_megabytes_weigh_like_triangles():
    _, parts = audit.score(row(megabytes=500), today=NOW)
    assert parts["weight"] == 0


# ----------------------------------------------------------------- gathering

class FakeGitHub:
    def __init__(self, repos, files):
        self.repos, self.files = repos, files

    def repo(self, name):
        from meshkit.upstream import NotFound

        try:
            return self.repos[name.lower()]
        except KeyError:
            raise NotFound(name) from None

    def file(self, repo, path):
        return self.files.get((repo, path), "")


def test_candidates_are_named_as_github_names_them_once_and_never_the_catalogs(
        tmp_path, monkeypatch):
    from meshkit import upstream

    write(tmp_path / ".gitmodules", '[submodule "src/arm"]\n\tpath = src/arm\n'
          "\turl = git@github.com:me/arm.git\n\tbranch = main\n")
    monkeypatch.setattr(upstream, "_pin", lambda root, path: "a" * 40)
    sources = upstream.SOURCES
    files = {(sources[0].repo, sources[0].path):
             "github.com/maker/arm github.com/old/menagerie github.com/new/menagerie "
             "github.com/gone/away",
             (sources[2].repo, sources[2].path): "| A | [X](humanoid/x) |"}
    repos = {"me/arm": {"full_name": "me/arm", "parent": {"full_name": "maker/arm"}},
             "old/menagerie": {"full_name": "new/menagerie", "license": {"spdx_id": "MIT"}},
             "new/menagerie": {"full_name": "new/menagerie", "license": {"spdx_id": "MIT"}},
             "fiveages-sim/robot_descriptions": {"full_name": "fiveages-sim/robot_descriptions"}}
    found = audit.gather(tmp_path, FakeGitHub(repos, files))
    keys = [(c.repo, c.folder) for c in found]
    assert keys[0] == ("me/arm", "") and found[0].fork == "arm"
    # maker/arm is the fork's upstream; old/menagerie is new/menagerie renamed.
    assert ("maker/arm", "") not in keys
    assert keys.count(("new/menagerie", "")) == 1
    assert ("fiveages-sim/robot_descriptions", "humanoid/x") in keys
    gone = next(c for c in found if c.repo == "gone/away")
    assert gone.error.startswith("GitHub:")


def test_a_package_comes_from_the_robots_own_repository_first():
    packages = [("arm_description", "/a/arm_description", "/a"),
                ("arm_description", "/b/arm_description", "/b"),
                ("gripper", "/a/gripper", "/a")]
    assert audit.package_map(packages, "/b") == {"arm_description": "/b/arm_description",
                                                  "gripper": "/a/gripper"}
    assert audit.package_map(packages, "/c")["arm_description"] == "/a/arm_description"


# -------------------------------------------------------------------- worker

def test_the_worker_measures_a_repository_in_its_own_process(tmp_path):
    write(tmp_path / "LICENSE", "MIT")
    write(tmp_path / "a" / "package.xml", "<package><name>a</name></package>")
    write(tmp_path / "a" / "meshes" / "a.stl", binary_stl(4))
    write(tmp_path / "a" / "urdf" / "a.urdf",
          urdf(link("a", "package://a/meshes/a.stl", mass=1)))
    write(tmp_path / "b.sdf", "<sdf/>")
    packages = audit.index_packages({str(tmp_path): tmp_path})
    spec = {"dir": str(tmp_path), "folder": "", "root": str(tmp_path),
            "packages": audit.package_map(packages, str(tmp_path)), "entries": None,
            "path_base": None}
    result = audit._run_worker(spec, 120)
    assert result["sdf_files"] == 1
    [robot] = result["robots"]
    assert robot["path"] == "a/urdf/a.urdf" and robot["flattened"] and robot["licence_file"]
    assert robot["triangles"] == 4 and robot["package"] == "a"


def test_a_licence_file_is_looked_for_up_to_the_repository_and_no_further(tmp_path):
    write(tmp_path / "LICENSE.txt", "x")
    robot = write(tmp_path / "repo" / "pkg" / "urdf" / "a.urdf", "<robot/>")
    assert not audit.licence_file(robot, tmp_path / "repo")
    write(tmp_path / "repo" / "pkg" / "COPYING", "x")
    assert audit.licence_file(robot, tmp_path / "repo")


# -------------------------------------------------------------------- report

def test_the_markdown_scores_rows_and_keeps_upstream_text_inert():
    robot = {"path": "urdf/<!-- x -->`a`.urdf", "kind": "urdf", "score": 80,
             "parts": {k: 1.0 for k in audit.WEIGHTS}, "error": "@someone <b>",
             "licence": "MIT", "formats": {"stl": 2}, "triangles": 10}
    report = audit.RepoReport("x/y", "x/y", "", ["awesome-robot-descriptions"], None, "MIT",
                              False, commit="c" * 40, last_commit="2026-01-01T00:00:00Z",
                              robots=[robot])
    failed = audit.RepoReport("x/z", "x/z", "", ["robot_descriptions.py"], None, None, False,
                              error="clone failed: <oops>")
    text = audit.render_markdown(audit.Audit("now", dict(audit.WEIGHTS), [report, failed]))
    assert "| 80 | ``urdf/<!-- x -->`a`.urdf`` | urdf |" in text
    assert "&#64;someone &lt;b&gt;" in text and "@someone" not in text
    assert "clone failed: &lt;oops&gt;" in text
    assert audit.PARTS_HEADER in text


# ------------------------------------------------------- what gets committed

def test_paths_on_this_machine_never_reach_the_report(tmp_path):
    home, cache = tmp_path / "home", tmp_path / "home" / "cache"
    repo = cache / "x__y"
    places = [(repo, ""), (cache, "<cache>"), (home, "~")]
    text = (f"No such file or directory: {repo.as_posix()}/urdf/a.xacro; "
            f"{repo}{chr(92)}meshes{chr(92)}b.stl; {cache / 'z__w'}; {home / 'x'}")
    assert audit.scrub(text, places) == (
        "No such file or directory: urdf/a.xacro; meshes" + chr(92) + "b.stl; "
        "<cache>/z__w; ~/x")


def test_the_workers_rows_name_no_absolute_path(tmp_path):
    write(tmp_path / "a" / "urdf" / "a.urdf", urdf(link("a", "../meshes/gone.stl")))
    spec = {"dir": str(tmp_path), "folder": "", "root": str(tmp_path / "elsewhere"),
            "packages": {}, "entries": None, "path_base": None, "scrub": []}
    [robot] = audit.audit_repo(spec)["robots"]
    assert robot["missing_meshes"] == ["a/urdf/../meshes/gone.stl"]
    assert str(tmp_path) not in json.dumps(robot)
    assert tmp_path.as_posix() not in json.dumps(robot)


def test_every_worldbody_counts_in_mjcf(tmp_path):
    write(tmp_path / "body.xml", '<mujoco><worldbody><body name="b"><joint type="hinge" '
          'range="0 1"/><geom type="box"/></body></worldbody></mujoco>')
    model = write(tmp_path / "model.xml", '<mujoco model="m"><worldbody><light/></worldbody>'
                  '<include file="body.xml"/></mujoco>')
    result = audit.measure(model, "mjcf", {})
    assert result["links"] == 1 and result["moving_joints"] == 1 and result["flattened"]


def test_the_top_table_has_one_row_per_package():
    def robot(path, score, package):
        return {"path": path, "kind": "xacro", "score": score, "package": package,
                "parts": {k: 1.0 for k in audit.WEIGHTS}, "error": None, "licence": "MIT",
                "formats": {}, "triangles": 1}
    report = audit.RepoReport("x/y", "x/y", "", ["s"], None, "MIT", False, robots=[
        robot("arm/xacro/robot.xacro", 90, "arm"),
        robot("arm/xacro/ros2_control/robot.xacro", 90, "arm"),
        robot("hand/urdf/hand.urdf", 70, "hand")])
    text = audit.render_markdown(audit.Audit("now", dict(audit.WEIGHTS), [report]))
    top = text.split("## The 2 best-scoring candidates")[1].split("## Every candidate")[0]
    assert "| 90 | arm | `arm/xacro/robot.xacro` | 0 | 2 |" in top
    assert "| 70 | hand | `hand/urdf/hand.urdf` | 0 | 1 |" in top
    assert "ros2_control" not in top


def test_a_package_row_is_its_complete_robot_not_a_component_that_ties():
    def robot(path, score, links, flattened=True):
        return {"path": path, "kind": "xacro", "score": score, "package": "g1",
                "links": links, "flattened": flattened, "parts": {k: 1.0 for k in audit.WEIGHTS},
                "error": None, "licence": "MIT", "formats": {}, "triangles": 1}
    report = audit.RepoReport("x/y", "x/y", "", ["s"], None, "MIT", False, robots=[
        robot("g1/xacro/hand.xacro", 100, 2),
        robot("g1/urdf/unitree_g1_full.urdf", 98, 39),
        robot("g1/xacro/broken.xacro", 25, 0, flattened=False)])
    text = audit.render_markdown(audit.Audit("now", dict(audit.WEIGHTS), [report]))
    top = text.split("## The 1 best-scoring candidates")[1].split("## Every candidate")[0]
    assert "| 98 | g1 | `g1/urdf/unitree_g1_full.urdf` | 39 | 3 |" in top


# ------------------------------------------------------------ review round 1

def test_mjcf_defaults_classes_and_childclass_are_applied(tmp_path):
    write(tmp_path / "assets" / "a.obj", "v 0 0 0\nvn 0 0 1\nf 1 1 1\n")
    model = write(tmp_path / "arm.xml", (
        '<mujoco model="arm"><compiler meshdir="assets"/><asset><mesh file="a.obj"/></asset>'
        '<default><joint range="-1 1"/>'
        '<default class="visual"><geom type="mesh" mesh="a" material="m"/></default>'
        '<default class="free"><joint limited="false"/></default></default>'
        '<worldbody><body name="b" childclass="visual"><joint type="hinge"/><geom/>'
        '<body name="c"><joint type="hinge" class="free"/><geom class="main" type="box"/>'
        '</body></body></worldbody></mujoco>'))
    result = audit.measure(model, "mjcf", {})
    # b's joint takes main's range; c's is unlimited by its class.
    assert result["moving_joints"] == 2 and result["limited_share"] == 0.5
    # b's bare geom is a coloured mesh by childclass; c's box is main's: no colour.
    assert result["formats"] == {"obj": 1} and result["mesh_visuals"] == 1
    assert result["materials_share"] == 0.25 and result["flattened"]


def test_an_mjcf_include_that_is_missing_or_repeated_is_an_error(tmp_path):
    write(tmp_path / "body.xml", '<mujoco><worldbody><body name="b"><geom type="box"/>'
          "</body></worldbody></mujoco>")
    missing = write(tmp_path / "a.xml", '<mujoco><include file="body.xml"/>'
                    '<include file="gone.xml"/></mujoco>')
    result = audit.measure(missing, "mjcf", {})
    assert not result["flattened"] and "gone.xml is not there" in result["error"]
    twice = write(tmp_path / "b.xml", '<mujoco><include file="body.xml"/>'
                  '<include file="body.xml"/></mujoco>')
    assert "included twice" in audit.measure(twice, "mjcf", {})["error"]


def test_an_include_is_found_beside_the_main_model_too(tmp_path):
    write(tmp_path / "parts" / "arm.xml", '<mujoco><include file="parts/hand.xml"/></mujoco>')
    write(tmp_path / "parts" / "hand.xml", '<mujoco><worldbody><body name="h"><geom '
          'type="box"/></body></worldbody></mujoco>')
    scene = write(tmp_path / "scene.xml", '<mujoco><include file="parts/arm.xml"/></mujoco>')
    assert audit.measure(scene, "mjcf", {})["flattened"]


def test_a_robot_whose_mesh_is_left_in_git_lfs_does_not_flatten(tmp_path):
    write(tmp_path / "meshes" / "a.stl", "version https://git-lfs.github.com/spec/v1\n"
          "oid sha256:00\nsize 99\n")
    path = write(tmp_path / "a.urdf", urdf(link("a", "meshes/a.stl", mass=1)))
    result = audit.measure(path, "urdf", {})
    assert not result["flattened"]
    assert result["error"] == "1 visual mesh file(s) unreadable: in Git LFS, not fetched"


def test_gltf_strips_and_fans_count_and_its_buffers_weigh(tmp_path):
    write(tmp_path / "a.bin", b"\0" * 5000)
    document = {"accessors": [{"count": 12}, {"count": 10}, {"count": 7}, {"count": 4}],
                "buffers": [{"uri": "a.bin"}, {"uri": "data:application/octet-stream;base64,"}],
                "meshes": [{"primitives": [
                    {"attributes": {"POSITION": 0, "NORMAL": 0}},             # 4 triangles
                    {"attributes": {"POSITION": 1, "NORMAL": 1}, "mode": 5},  # strip: 8
                    {"attributes": {"POSITION": 2, "NORMAL": 2}, "mode": 6},  # fan: 5
                    {"attributes": {"POSITION": 3}, "mode": 1}]}]}            # lines: none
    path = write(tmp_path / "a.gltf", json.dumps(document))
    facts = audit.mesh_facts(path)
    assert facts["triangles"] == 17 and facts["normals"] is True
    assert facts["bytes"] == path.stat().st_size + 5000
    write(tmp_path / "b.gltf", json.dumps({"buffers": [{"uri": "gone.bin"}]}))
    assert "gone.bin" in audit.mesh_facts(tmp_path / "b.gltf")["error"]


def test_meshes_are_streamed_and_nothing_split_between_chunks_is_lost(tmp_path, monkeypatch):
    monkeypatch.setattr(audit, "_CHUNK", 7)
    dae = audit.mesh_facts(write(tmp_path / "a.dae", '<COLLADA><material id="m"/>'
                                 + '<triangles count="5"><input semantic="NORMAL"/></triangles>'
                                 * 3 + "</COLLADA>"))
    assert (dae["triangles"], dae["normals"], dae["materials"]) == (15, True, True)
    stl = audit.mesh_facts(write(tmp_path / "b.stl", "solid x\n" + "facet normal 0 0 1\n"
                                 "outer loop\nendloop\nendfacet\n" * 4 + "endsolid x\n"))
    assert stl["triangles"] == 4


def test_the_cache_never_clears_a_folder_it_did_not_make(tmp_path):
    mine = write(tmp_path / "x__y" / "notes.txt", "keep me")
    with pytest.raises(RuntimeError, match="not a git clone"):
        audit.fetch("x/y", tmp_path, update=False)
    assert mine.read_text() == "keep me"


def test_the_cache_never_resets_a_clone_of_something_else(tmp_path):
    import subprocess

    dest = tmp_path / "x__y"
    dest.mkdir()
    subprocess.run(["git", "init", "-q", str(dest)], check=True)
    subprocess.run(["git", "-C", str(dest), "remote", "add", "origin",
                    "https://github.com/someone/else.git"], check=True)
    with pytest.raises(RuntimeError, match="not of x/y"):
        audit.fetch("x/y", tmp_path)


def test_a_relative_path_renders_from_the_robots_own_folder(tmp_path, monkeypatch):
    from meshkit.scan import render_xacro

    write(tmp_path / "cache" / "r" / "urdf" / "parts.xacro",
          f'<robot {XACRO}><xacro:macro name="arm"><link name="a"/></xacro:macro></robot>')
    write(tmp_path / "cache" / "r" / "urdf" / "arm.urdf.xacro",
          f'<robot {XACRO} name="arm"><xacro:include filename="parts.xacro"/><xacro:arm/>'
          "</robot>")
    monkeypatch.chdir(tmp_path)
    text = render_xacro(Path("cache/r/urdf/arm.urdf.xacro"), {}, {})
    assert '<link name="a"' in text


def test_an_mjcf_mesh_written_inline_is_not_a_missing_file(tmp_path):
    model = write(tmp_path / "cube.xml", (
        '<mujoco><default><default class="c"><geom type="mesh" mesh="cubelet"/></default>'
        '</default><asset><mesh name="cubelet" vertex="0 0 0 1 0 0 0 1 0 0 0 1"/></asset>'
        '<worldbody><body name="b"><geom class="c"/></body></worldbody></mujoco>'))
    result = audit.measure(model, "mjcf", {})
    assert result["flattened"] and result["missing_count"] == 0


def test_a_packages_mesh_is_looked_for_in_every_copy_of_it(tmp_path):
    write(tmp_path / "b" / "grip" / "meshes" / "a.stl", binary_stl(2))
    (tmp_path / "a" / "grip").mkdir(parents=True)
    packages = [("grip", str(tmp_path / "a" / "grip"), "a"),
                ("grip", str(tmp_path / "b" / "grip"), "b")]
    mapping, copies = audit.package_map(packages, "r"), audit.package_copies(packages, "r")
    text = urdf(link("l", "package://grip/meshes/a.stl", mass=1))
    path = write(tmp_path / "r" / "a.urdf", text)
    assert audit.measure(path, "urdf", mapping, copies=copies)["flattened"]
    assert not audit.measure(path, "urdf", mapping)["flattened"]
    # The robot's own repository's copy is looked in first.
    assert audit.package_copies(packages, "b")["grip"][0] == str(tmp_path / "b" / "grip")


# ------------------------------------------------------------ review round 2

def fake_git(monkeypatch, origin="https://github.com/x/y.git"):
    """git as far as fetch needs it, without a network."""
    calls = []

    def run(*args, cwd=None, timeout=None):
        calls.append(args)
        if args[0] == "clone":
            (Path(args[-1]) / ".git").mkdir(parents=True)
        return {"remote": origin, "rev-parse": "c" * 40, "log": "2026-11-01T00:00:00Z"}.get(
            args[0], "")
    monkeypatch.setattr(audit, "_git", run)
    return calls


def test_a_staging_folder_is_cleared_only_when_the_audit_marked_it(tmp_path, monkeypatch):
    fake_git(monkeypatch)
    theirs = write(tmp_path / f"x__y{audit.PARTIAL}-mine" / "notes.txt", "keep me")
    ours = tmp_path / f"x__y{audit.PARTIAL}-old"
    write(ours / audit.OWNED, "made by meshkit audit")
    import os
    import time

    dead = time.time() - audit.STALE - 60          # a run killed long ago
    os.utime(ours / audit.OWNED, (dead, dead))
    dest, commit, _ = audit.fetch("x/y", tmp_path)
    assert theirs.read_text() == "keep me" and not ours.exists()
    assert (dest / ".git" / audit.OWNED).is_file() and commit == "c" * 40
    # The staging folder this run used is gone; only the unmarked one is left.
    assert [p.name for p in tmp_path.glob(f"x__y{audit.PARTIAL}-*")] == [theirs.parent.name]


def test_an_unmarked_clone_of_the_same_repository_is_never_reset(tmp_path, monkeypatch):
    calls = fake_git(monkeypatch)
    (tmp_path / "x__y" / ".git").mkdir(parents=True)
    with pytest.raises(RuntimeError, match="not cloned by the audit"):
        audit.fetch("x/y", tmp_path)
    assert not any(c[0] in ("fetch", "reset") for c in calls)
    # Without fetching it is only read, so it can be measured as it stands.
    assert audit.fetch("x/y", tmp_path, update=False)[0] == tmp_path / "x__y"
    write(tmp_path / "x__y" / ".git" / audit.OWNED, "made by meshkit audit")
    audit.fetch("x/y", tmp_path)
    assert [c[0] for c in calls if c[0] in ("fetch", "reset")] == ["fetch", "reset"]


def test_an_stl_too_short_to_measure_is_unreadable(tmp_path):
    assert audit.mesh_facts(write(tmp_path / "a.stl", b""))["error"].startswith(
        "not a readable STL")
    short = audit.mesh_facts(write(tmp_path / "b.stl", binary_stl(10)[:-50]))
    assert "10 triangles promised" in short["error"] and short["triangles"] is None
    padded = audit.mesh_facts(write(tmp_path / "c.stl", binary_stl(2) + b"\0\0"))
    assert padded["triangles"] == 2 and padded["error"] is None


def test_a_gltf_buffer_in_lfs_or_short_of_its_length_is_unreadable(tmp_path):
    write(tmp_path / "lfs.bin", "version https://git-lfs.github.com/spec/v1\nsize 9000\n")
    write(tmp_path / "short.bin", b"\0" * 10)
    lfs = audit.mesh_facts(write(tmp_path / "a.gltf", json.dumps(
        {"buffers": [{"uri": "lfs.bin", "byteLength": 9000}]})))
    assert lfs["error"] == "its buffer lfs.bin is in Git LFS, not fetched"
    short = audit.mesh_facts(write(tmp_path / "b.gltf", json.dumps(
        {"buffers": [{"uri": "short.bin", "byteLength": 100}]})))
    assert short["error"] == "its buffer short.bin has 10 of the 100 bytes it declares"
    good = audit.mesh_facts(write(tmp_path / "c.gltf", json.dumps(
        {"buffers": [{"uri": "short.bin", "byteLength": 10}]})))
    assert good["error"] is None


def test_an_mjcf_frame_without_geometry_or_joint_is_not_asked_for_a_mass(tmp_path):
    model = write(tmp_path / "m.xml", '<mujoco><worldbody><body name="frame">'
                  '<body name="arm"><joint type="hinge" range="0 1"/><geom type="box"/></body>'
                  '<body name="bare"><joint type="slide" range="0 1"/></body>'
                  "</body></worldbody></mujoco>")
    result = audit.measure(model, "mjcf", {})
    assert result["links"] == 3 and result["inertia_share"] == 0.5   # arm yes, bare no
    no_geoms = write(tmp_path / "n.xml", '<mujoco><compiler inertiafromgeom="false"/>'
                     '<worldbody><body name="arm"><joint/><geom type="box"/></body>'
                     "</worldbody></mujoco>")
    assert audit.measure(no_geoms, "mjcf", {})["inertia_share"] == 0.0


def test_triangles_count_each_visual_that_draws_a_mesh(tmp_path):
    write(tmp_path / "meshes" / "finger.stl", binary_stl(100))
    text = urdf(*(link(f"f{i}", "meshes/finger.stl", mass=1) for i in range(12)))
    path = write(tmp_path / "hand.urdf", text)
    result = audit.measure(path, "urdf", {})
    assert result["triangles"] == 1200
    assert result["megabytes"] == round((84 + 50 * 100) / 1e6, 2)   # downloaded once


def test_an_only_name_that_matches_nothing_is_refused():
    c = [audit.Candidate("fork:turtlebot4", "me/turtlebot4", fork="turtlebot4")]
    with pytest.raises(audit.SelectionError, match="turtlebot44"):
        audit.select(c, ["turtlebot4", "turtlebot44"])


def test_the_markdown_links_the_json_it_was_written_with():
    report = audit.RepoReport("x/y", "x/y", "", ["s"], None, "MIT", False)
    audit_ = audit.Audit("now", dict(audit.WEIGHTS), [report])
    assert "[`audit.json`](audit.json)" in audit.render_markdown(audit_)
    assert "[`report.json`](../json/report.json)" in audit.render_markdown(
        audit_, json_link="../json/report.json")
    # On another drive there is no relative path: named, never linked wrongly.
    other = audit.render_markdown(audit_, json_link=None, json_name="report.json")
    assert "`report.json`, written with this report, has every" in other
    assert "](report.json)" not in other


def test_a_live_staging_folder_is_left_and_a_dead_one_cleared(tmp_path):
    import os

    dest = tmp_path / "x__y"
    live, dead, theirs = (tmp_path / f"x__y{audit.PARTIAL}-{n}" for n in ("live", "dead", "z"))
    for folder in (live, dead):
        write(folder / audit.OWNED, "made by meshkit audit")
    write(theirs / "notes.txt", "keep me")
    old = 1_000_000.0
    os.utime(dead / audit.OWNED, (old, old))
    os.utime(live / audit.OWNED, (old + audit.STALE, old + audit.STALE))
    audit._clear_dead_staging(dest, now=old + audit.STALE + 1)
    assert live.exists() and theirs.exists() and not dead.exists()


def test_a_clone_another_audit_finished_first_is_used(tmp_path, monkeypatch):
    def run(*args, cwd=None, timeout=None):
        if args[0] == "clone":
            # Meanwhile the other audit put its clone in place.
            write(tmp_path / "x__y" / ".git" / audit.OWNED, "made by meshkit audit")
            write(tmp_path / "x__y" / "a.urdf", "<robot/>")
            (Path(args[-1]) / ".git").mkdir(parents=True)
        return {"rev-parse": "c" * 40, "log": "2026-11-01T00:00:00Z"}.get(args[0], "")
    monkeypatch.setattr(audit, "_git", run)
    dest, commit, _ = audit.fetch("x/y", tmp_path)
    assert (dest / "a.urdf").is_file() and commit == "c" * 40
    assert not list(tmp_path.glob(f"x__y{audit.PARTIAL}-*"))      # ours removed


def test_a_failed_clone_leaves_no_staging_folder(tmp_path, monkeypatch):
    def run(*args, cwd=None, timeout=None):
        raise RuntimeError("fatal: repository not found")
    monkeypatch.setattr(audit, "_git", run)
    with pytest.raises(RuntimeError):
        audit.fetch("x/y", tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_select_narrows_by_key_repository_or_submodule():
    c = [audit.Candidate("fork:arm", "me/arm", fork="arm"), audit.Candidate("k", "a/b")]
    assert audit.select(c, None) == c
    assert [x.repo for x in audit.select(c, ["ARM"])] == ["me/arm"]
    assert [x.repo for x in audit.select(c, ["a/b"])] == ["a/b"]
