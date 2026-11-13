"""The catalog index: the repository's own, and the rules it is held to."""

import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

from meshkit import catalog

REPO = Path(__file__).resolve().parents[3]

ENTRY = """\
  - id: {id}
    name: Arm {id}
    category: arm
    submodule: {submodule}
    entry: src/{submodule}/urdf/arm.urdf.xacro
    licence: MIT
"""


def make(root: Path, *, family: str = "acme", entries: str | None = None,
         submodules=("arm_fork",), clone=True) -> Path:
    """A small catalog: one family file, its submodules declared and cloned."""
    (root / "catalog").mkdir(parents=True, exist_ok=True)
    body = entries if entries is not None else ENTRY.format(id="arm", submodule=submodules[0])
    (root / "catalog" / f"{family}.yaml").write_text(
        f"family: {family}\nmaker: Acme\nentries:\n{body}", encoding="utf-8")
    (root / ".gitmodules").write_text("".join(
        f'[submodule "src/{name}"]\n\tpath = src/{name}\n\turl = git@example.com:{name}.git\n'
        for name in submodules), encoding="utf-8")
    if clone:
        for name in submodules:
            urdf = root / "src" / name / "urdf" / "arm.urdf.xacro"
            urdf.parent.mkdir(parents=True, exist_ok=True)
            urdf.write_text("<robot name='arm'/>", encoding="utf-8")
    return root


# ------------------------------------------------------------- the real catalog

def test_the_repository_catalog_has_no_problems():
    # Built, current, every submodule listed, every entry point present (in
    # the submodules this checkout has cloned).
    assert catalog.check(REPO) == []


def test_the_repository_catalog_matches_its_schema():
    schema = json.loads((REPO / catalog.SCHEMA_FILE).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    document = json.loads((REPO / catalog.INDEX_FILE).read_text(encoding="utf-8"))
    jsonschema.validate(document, schema, cls=jsonschema.Draft202012Validator)


def test_built_entries_match_the_schema_with_every_optional_field(tmp_path):
    # The repository's own entries may not use every field; these do.
    make(tmp_path, entries=ENTRY.format(id="arm", submodule="arm_fork") + """\
    kind: end_effector
    tags: [gripper, two_finger]
    args:
      dof: "7"
    mesh_base: src/arm_fork/urdf
    licence_note: Non-commercial use only.
""")
    schema = json.loads((REPO / catalog.SCHEMA_FILE).read_text(encoding="utf-8"))
    jsonschema.validate(catalog.build(tmp_path), schema, cls=jsonschema.Draft202012Validator)


# ------------------------------------------------------------------ the sources

def test_an_entry_is_complete_after_building(tmp_path):
    [entry] = catalog.build(make(tmp_path))["entries"]
    assert entry == {
        "id": "arm", "name": "Arm arm", "kind": "robot", "category": "arm",
        "family": "acme", "maker": "Acme", "tags": [], "licence": "MIT",
        "submodule": "arm_fork", "entry": "src/arm_fork/urdf/arm.urdf.xacro",
        "format": "xacro", "args": {}, "mesh_base": None,
    }


@pytest.mark.parametrize(("extra", "message"), [
    ("    colour: red\n", "unknown key"),
    ("    args:\n      dof: 7\n", "quote numbers"),
    ("    args:\n      name: two words\n", "whitespace"),
    ("    mesh_base: /tmp\n", "mesh_base must be relative"),
    ("    mesh_base: C:/meshes\n", "mesh_base must be relative"),
    ("    mesh_base: src/arm_fork/../other_fork\n", "mesh_base must be relative"),
])
def test_a_bad_entry_names_itself(tmp_path, extra, message):
    make(tmp_path, entries=ENTRY.format(id="arm", submodule="arm_fork") + extra)
    with pytest.raises(catalog.CatalogError, match=message) as info:
        catalog.build(tmp_path)
    assert "catalog/acme.yaml entry 1 (arm)" in str(info.value)


def test_a_key_given_twice_is_an_error_not_the_last_one_winning(tmp_path):
    # Each args block passes alone; safe_load would keep the second and lose
    # the first without a word.
    make(tmp_path, entries=ENTRY.format(id="arm", submodule="arm_fork") + """\
    args:
      ur_type: ur5e
    args:
      name: ur5e
""")
    with pytest.raises(catalog.CatalogError, match="duplicate key 'args'"):
        catalog.build(tmp_path)
    assert any("duplicate key 'args'" in problem for problem in catalog.check(tmp_path))


def test_an_id_is_unique_across_families(tmp_path):
    make(tmp_path)
    (tmp_path / "catalog" / "other.yaml").write_text(
        "family: other\nmaker: Other\nentries:\n" + ENTRY.format(id="arm", submodule="arm_fork"),
        encoding="utf-8")
    with pytest.raises(catalog.CatalogError, match="also in catalog/acme.yaml"):
        catalog.build(tmp_path)


def test_the_family_is_the_file_name(tmp_path):
    make(tmp_path)
    path = tmp_path / "catalog" / "acme.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("family: acme", "family: acme_co"),
                    encoding="utf-8")
    with pytest.raises(catalog.CatalogError, match="must match"):
        catalog.build(tmp_path)


def test_entry_must_be_xacro_or_urdf_inside_the_repository(tmp_path):
    for entry, message in [("src/arm_fork/robot.sdf", ".xacro or .urdf"),
                           ("../elsewhere/arm.urdf", "relative to the repository root"),
                           ("/elsewhere/arm.urdf", "relative to the repository root")]:
        make(tmp_path, entries=ENTRY.format(id="arm", submodule="arm_fork").replace(
            "src/arm_fork/urdf/arm.urdf.xacro", entry))
        with pytest.raises(catalog.CatalogError, match=message):
            catalog.build(tmp_path)


# ---------------------------------------------------------------------- check

def test_check_passes_a_built_catalog(tmp_path):
    catalog.write(make(tmp_path))
    assert catalog.check(tmp_path) == []


def test_check_finds_a_stale_or_missing_index(tmp_path):
    make(tmp_path)
    assert catalog.check(tmp_path) == ["catalog.json is missing: run `meshkit index`"]
    catalog.write(tmp_path)
    path = tmp_path / "catalog" / "acme.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("Arm arm", "Arm A"),
                    encoding="utf-8")
    assert catalog.check(tmp_path) == [
        "catalog.json does not match catalog/*.yaml: run `meshkit index`"]


def test_check_reads_a_crlf_checkout_as_current(tmp_path):
    catalog.write(make(tmp_path))
    index = tmp_path / catalog.INDEX_FILE
    index.write_bytes(index.read_bytes().replace(b"\n", b"\r\n"))
    assert catalog.check(tmp_path) == []


def test_check_wants_an_entry_for_every_submodule(tmp_path):
    catalog.write(make(tmp_path, submodules=("arm_fork", "base_fork")))
    assert catalog.check(tmp_path) == ["src/base_fork has no catalog entry"]


def test_check_wants_every_entry_in_a_declared_submodule(tmp_path):
    make(tmp_path)
    (tmp_path / ".gitmodules").write_text("", encoding="utf-8")
    catalog.write(tmp_path)
    assert catalog.check(tmp_path) == [
        "acme/arm: submodule 'arm_fork' is not in .gitmodules"]


def test_check_finds_a_missing_entry_point_only_where_it_can_look(tmp_path):
    catalog.write(make(tmp_path, clone=False))
    assert catalog.check(tmp_path) == []          # not cloned: nothing to look at
    stray = tmp_path / "src" / "arm_fork" / "README.md"
    stray.parent.mkdir(parents=True)
    stray.write_text("", encoding="utf-8")
    assert catalog.check(tmp_path) == [
        "acme/arm: entry src/arm_fork/urdf/arm.urdf.xacro does not exist"]


def test_check_always_looks_for_a_wrapper_kept_in_this_repository(tmp_path):
    make(tmp_path, clone=False, entries=ENTRY.format(id="arm", submodule="arm_fork").replace(
        "src/arm_fork/urdf/arm.urdf.xacro", "descriptions/acme/arm.urdf.xacro"))
    catalog.write(tmp_path)
    assert catalog.check(tmp_path) == [
        "acme/arm: entry descriptions/acme/arm.urdf.xacro does not exist"]


def test_check_wants_a_path_under_src_in_the_entrys_own_submodule(tmp_path):
    make(tmp_path, submodules=("arm_fork", "other_fork"), entries=(
        ENTRY.format(id="arm", submodule="arm_fork").replace("src/arm_fork/", "src/other_fork/")
        + ENTRY.format(id="other", submodule="other_fork")))
    catalog.write(tmp_path)
    assert catalog.check(tmp_path) == [
        "acme/arm: entry src/other_fork/urdf/arm.urdf.xacro is not in src/arm_fork"]


# ---------------------------------------------------------------- the launcher

def test_catalog_rows_gives_the_launcher_eight_fields(tmp_path):
    make(tmp_path, entries=ENTRY.format(id="arm", submodule="arm_fork") + """\
    args:
      ur_type: ur5e
      name: ur5e
""" + ENTRY.format(id="plain", submodule="arm_fork"))
    catalog.write(tmp_path)
    out = subprocess.run(
        [sys.executable, "-I", str(REPO / "docker" / "catalog_rows.py"),
         str(tmp_path / catalog.INDEX_FILE)],
        capture_output=True, text=True, check=True).stdout
    assert [line.split("\t") for line in out.splitlines()] == [
        ["arm", "arm", "arm_fork", "xacro", "src/arm_fork/urdf/arm.urdf.xacro",
         "ur_type:=ur5e name:=ur5e", "-", "Arm arm"],
        ["plain", "arm", "arm_fork", "xacro", "src/arm_fork/urdf/arm.urdf.xacro",
         "-", "-", "Arm plain"],
    ]


def test_catalog_rows_fails_loudly_on_an_unreadable_file(tmp_path):
    bad = tmp_path / "catalog.json"
    bad.write_text("{not json", encoding="utf-8")
    result = subprocess.run([sys.executable, "-I", str(REPO / "docker" / "catalog_rows.py"),
                             str(bad)], capture_output=True, text=True)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "cannot read" in result.stderr
