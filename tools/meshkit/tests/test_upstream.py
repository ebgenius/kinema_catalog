"""meshkit upstream, against a GitHub that answers from a dict."""

import json

import pytest

from meshkit import upstream
from meshkit.upstream import Fork, GitHubError, NotFound, Source

PIN = "a" * 40


class FakeGitHub:
    """Answers GET paths from a dict; a missing path is GitHub's 404."""

    def __init__(self, responses: dict):
        self.responses = responses

    def get(self, path, *, raw=False):
        try:
            value = self.responses[path]
        except KeyError:
            raise NotFound(f"GET {path}: not found") from None
        if isinstance(value, Exception):
            raise value
        return value

    repo = upstream.GitHub.repo
    compare = upstream.GitHub.compare
    file = upstream.GitHub.file


def compare_path(base, head, repo="me/arm"):
    return f"repos/{repo}/compare/{base}...{head}?per_page=100"


def github(*, behind=3, own=0, fork_behind=3, fork_own=0, pin_behind_fork=0, files=(),
           parent=None):
    parent = parent or {"full_name": "maker/arm", "default_branch": "main",
                        "archived": False, "license": {"spdx_id": "BSD-3-Clause"}}
    return FakeGitHub({
        "repos/me/arm": {"full_name": "me/arm", "parent": parent},
        compare_path("me:main", "maker:main"): {"ahead_by": fork_behind, "behind_by": fork_own},
        compare_path(PIN, "maker:main"): {"ahead_by": behind, "behind_by": own,
                                          "files": [dict(f) for f in files]},
        compare_path(PIN, "me:main"): {"ahead_by": pin_behind_fork, "behind_by": 0},
    })


FORK = Fork("arm", "me/arm", "main", PIN)


def check(gh, *, licences=("BSD-3-Clause",), previous=None):
    return upstream.check_fork(FORK, gh, licences=list(licences), previous=previous)


# ------------------------------------------------------------------- one fork

def test_a_level_fork_needs_nothing():
    report = check(github(behind=0, fork_behind=0))
    assert report.level and report.actions == [] and report.notes == []


def test_behind_with_no_commits_of_its_own_is_sync_then_bump():
    report = check(github())
    assert (report.behind, report.own, report.fork_behind) == (3, 0, 3)
    assert not report.level
    assert report.actions == ["sync", "bump"]


def test_a_fork_with_its_own_commits_is_reviewed_not_synced():
    report = check(github(own=2, fork_own=2))
    assert report.actions == ["bump", "review"]


def test_a_synced_fork_with_an_old_pin_is_a_bump():
    report = check(github(fork_behind=0, pin_behind_fork=3))
    assert report.actions == ["bump"]


def test_changed_files_are_sorted_into_what_matters():
    report = check(github(files=[
        {"filename": "arm_description/urdf/arm.urdf.xacro", "status": "modified"},
        {"filename": "arm_description/meshes/visual/link1.DAE", "status": "modified"},
        {"filename": "arm_description/config/joint_limits.yaml", "status": "modified"},
        {"filename": "arm_description/launch/view.launch.py", "status": "modified"},
        {"filename": "README.md", "status": "modified"},
    ]))
    assert report.changed == {
        "description": ["arm_description/urdf/arm.urdf.xacro"],
        "meshes": ["arm_description/meshes/visual/link1.DAE"],
        "config": ["arm_description/config/joint_limits.yaml"],
    }
    assert report.other_changed == 2
    assert report.actions == ["sync", "bump", "reconvert"]


def test_an_added_robot_file_is_a_new_robot_and_a_review():
    report = check(github(files=[
        {"filename": "arm_description/urdf/arm2.urdf.xacro", "status": "added"},
        {"filename": "arm_description/urdf/macros.xacro", "status": "added"},   # an include
        {"filename": "arm_description/urdf/arm.urdf", "status": "modified"},
    ]))
    assert report.new_robots == ["arm_description/urdf/arm2.urdf.xacro"]
    assert "review" in report.actions


def test_a_full_comparison_says_it_is_truncated():
    files = [{"filename": f"meshes/{i}.stl", "status": "modified"} for i in range(300)]
    assert check(github(files=files)).truncated


def test_an_archived_upstream_is_a_note():
    report = check(github(behind=0, fork_behind=0, parent={
        "full_name": "maker/arm", "default_branch": "main", "archived": True, "license": None}))
    assert any("archived" in note for note in report.notes)
    assert report.level and report.actions == ["review"]


def test_changes_since_the_last_run_are_notes():
    previous = {"upstream": "oldmaker/arm", "default_branch": "master", "licence": "MIT"}
    notes = check(github(), previous=previous).notes
    assert "upstream renamed or moved: oldmaker/arm -> maker/arm" in notes
    assert "upstream default branch changed: master -> main" in notes
    assert "upstream licence changed: MIT -> BSD-3-Clause" in notes


def test_a_licence_the_catalog_does_not_name_is_a_note():
    notes = check(github(), licences=["Apache-2.0"]).notes
    assert notes == ["upstream licence is BSD-3-Clause; the catalog says Apache-2.0"]
    # Part of an expression is enough; a licence GitHub cannot name says nothing.
    assert check(github(), licences=["BSD-3-Clause AND LicenseRef-X"]).notes == []
    unnamed = github(parent={"full_name": "maker/arm", "default_branch": "main",
                             "archived": False, "license": {"spdx_id": "NOASSERTION"}})
    assert check(unnamed, licences=["Apache-2.0"]).notes == []


def test_an_upstream_without_the_tracked_branch_is_a_note():
    gh = github()
    del gh.responses[compare_path("me:main", "maker:main")]
    report = check(gh)
    assert report.notes == ["upstream has no branch 'main' (its default is 'main')"]
    assert report.behind is None and not report.level


def test_a_failed_request_is_a_note_not_a_crash():
    gh = github()
    gh.responses["repos/me/arm"] = GitHubError("GET repos/me/arm: HTTP 502 Bad Gateway")
    report = check(gh)
    assert report.notes == ["could not be checked: GET repos/me/arm: HTTP 502 Bad Gateway"]
    assert report.actions == ["review"]


def test_a_repository_that_is_not_a_fork_is_a_note():
    gh = github()
    gh.responses["repos/me/arm"] = {"full_name": "me/arm"}
    assert "not a fork" in check(gh).notes[0]


# ---------------------------------------------------------------------- lists

def test_repository_links_are_extracted_once_each():
    text = """
- [Arm](https://github.com/Maker/arm_description) and https://github.com/maker/ARM_description/
- url="https://github.com/other/hand.git",
- git@github.com:other/hand.git
- [sponsor](https://github.com/sponsors/someone)
- [self](https://github.com/lists/awesome)
"""
    found = upstream.extract(Source("l", "lists/awesome", "README.md", "github"), text)
    assert found == {"maker/arm_description": "Maker/arm_description", "other/hand": "other/hand"}


def test_table_links_are_extracted_with_their_brand():
    text = """
| Brand | Model | Images |
|---|---|---|
| Agibot | [G1](humanoid/Agibot/agibot_g1_description) | <img src="humanoid/.images/g1.png"> |
| Unitree | [H1](./humanoid/Unitree/h1_description/) | |
Some prose with [a link](docs/guide.md).
"""
    found = upstream.extract(Source("f", "five/robots", "README.md", "table"), text)
    assert found == {
        "five/robots:humanoid/agibot/agibot_g1_description":
            "Agibot G1 (five/robots/humanoid/Agibot/agibot_g1_description)",
        "five/robots:humanoid/unitree/h1_description":
            "Unitree H1 (five/robots/humanoid/Unitree/h1_description)",
    }


SOURCE = Source("l", "lists/awesome", "README.md", "github")
LIST_PATH = "repos/lists/awesome/contents/README.md"


def test_a_first_run_records_a_baseline():
    gh = FakeGitHub({LIST_PATH: "github.com/a/one github.com/b/two"})
    report, keys = upstream.check_list(SOURCE, gh, known=set(), previous=None)
    assert report.baseline and report.count == 2 and report.new == {}
    assert keys == ["a/one", "b/two"]


def test_later_runs_report_what_is_new_and_not_in_the_catalog():
    gh = FakeGitHub({LIST_PATH: "github.com/a/one github.com/b/two github.com/c/mine"})
    report, keys = upstream.check_list(SOURCE, gh, known={"c/mine"}, previous=["a/one"])
    assert report.new == {"b/two": "b/two"}
    assert keys == ["a/one", "b/two"]


def test_an_unreadable_list_keeps_its_previous_state():
    gh = FakeGitHub({})
    report, keys = upstream.check_list(SOURCE, gh, known=set(), previous=["a/one"])
    assert report.error and keys == ["a/one"]


# --------------------------------------------------------------------- report

def make_catalog(root):
    (root / "catalog").mkdir()
    (root / "catalog" / "acme.yaml").write_text(
        "family: acme\nmaker: Acme\nentries:\n"
        "  - id: arm\n    name: Arm\n    category: arm\n    submodule: arm\n"
        "    entry: src/arm/urdf/arm.urdf.xacro\n    licence: BSD-3-Clause\n",
        encoding="utf-8")
    (root / ".gitmodules").write_text(
        '[submodule "src/arm"]\n\tpath = src/arm\n\turl = git@github.com:me/arm.git\n'
        "\tbranch = main\n", encoding="utf-8")
    return root


def test_read_forks_wants_a_branch(tmp_path):
    make_catalog(tmp_path)
    [fork] = upstream.read_forks(tmp_path)
    assert (fork.name, fork.repo, fork.branch) == ("arm", "me/arm", "main")
    (tmp_path / ".gitmodules").write_text(
        '[submodule "src/arm"]\n\tpath = src/arm\n\turl = git@github.com:me/arm.git\n',
        encoding="utf-8")
    with pytest.raises(GitHubError, match="names no branch"):
        upstream.read_forks(tmp_path)


def test_the_markdown_carries_the_state_the_next_run_reads(tmp_path, monkeypatch):
    make_catalog(tmp_path)
    monkeypatch.setattr(upstream, "_pin", lambda root, path: PIN)
    gh = github(files=[{"filename": "urdf/arm2.urdf", "status": "added"}])
    gh.responses.update({f"repos/{s.repo}/contents/{s.path}": "github.com/a/one"
                         for s in upstream.SOURCES})
    gh.responses[f"repos/{upstream.SOURCES[2].repo}/contents/README.md"] = (
        "| B | [X](x_description) |\ngithub.com/a/one")

    first = upstream.run(tmp_path, gh, workers=1)
    markdown = upstream.render_markdown(first)
    assert "**0 of 1 forks are level with upstream.**" in markdown
    assert "| arm | [maker/arm](https://github.com/maker/arm) | main | [3](" in markdown
    assert "`urdf/arm2.urdf`" in markdown
    state = upstream.read_previous(markdown)
    assert state == first.state
    assert state["forks"]["arm"] == {"upstream": "maker/arm", "default_branch": "main",
                                     "licence": "BSD-3-Clause"}

    second = upstream.run(tmp_path, gh, previous=state, workers=1)
    assert all(not item.baseline and not item.new for item in second.lists)
    # The JSON report is also accepted as the previous one.
    as_json = json.dumps(second.as_json())
    assert upstream.read_previous(as_json) == second.state


def test_no_previous_report_is_a_first_run():
    assert upstream.read_previous("") == {}
    assert upstream.read_previous("# an issue someone wrote by hand") == {}


def test_a_damaged_state_is_an_error_not_a_first_run():
    with pytest.raises(GitHubError, match="cannot be read"):
        upstream.read_previous(f"<!-- {upstream.STATE_MARKER} bm90IGd6aXA= -->")


def test_an_oversized_report_drops_the_file_lists(tmp_path, monkeypatch):
    make_catalog(tmp_path)
    monkeypatch.setattr(upstream, "_pin", lambda root, path: PIN)
    files = [{"filename": f"meshes/part_{i:03}.stl", "status": "modified"} for i in range(200)]
    report = upstream.run(tmp_path, github(files=files), lists=False, workers=1)
    monkeypatch.setattr(upstream, "BODY_LIMIT", len(upstream.render_markdown(report)) - 1)
    markdown = upstream.render_markdown(report)
    assert "200 meshes" in markdown and "part_000" not in markdown
    assert upstream.read_previous(markdown) == report.state
