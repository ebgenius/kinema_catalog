"""meshkit upstream, against a GitHub that answers from a dict."""

import json
import re

import pytest

from meshkit import upstream
from meshkit.upstream import Fork, GitHubError, NotFound, Source

PIN = "a" * 40
FORK_SHA = "f" * 40          # where the fork's branch is
UPSTREAM_SHA = "e" * 40      # where upstream's is
ME, MAKER = f"me:{FORK_SHA}", f"maker:{UPSTREAM_SHA}"


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
    branch_sha = upstream.GitHub.branch_sha


def compare_path(base, head, repo="me/arm"):
    return f"repos/{repo}/compare/{base}...{head}?per_page=100"


def github(*, behind=3, own=0, fork_behind=3, fork_own=0, pin_behind_fork=0, pin_only=0,
           files=(), parent=None):
    parent = parent or {"full_name": "maker/arm", "default_branch": "main",
                        "archived": False, "license": {"spdx_id": "BSD-3-Clause"}}
    return FakeGitHub({
        "repos/me/arm": {"full_name": "me/arm", "parent": parent},
        "repos/me/arm/branches/main": {"name": "main", "commit": {"sha": FORK_SHA}},
        "repos/maker/arm/branches/main": {"name": "main", "commit": {"sha": UPSTREAM_SHA}},
        compare_path(ME, MAKER): {"ahead_by": fork_behind, "behind_by": fork_own},
        compare_path(PIN, MAKER): {"ahead_by": behind, "behind_by": own,
                                          "files": [dict(f) for f in files]},
        compare_path(PIN, ME): {"ahead_by": pin_behind_fork, "behind_by": pin_only},
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
    del gh.responses["repos/maker/arm/branches/main"]
    del gh.responses[compare_path(ME, MAKER)]
    report = check(gh)
    assert report.notes == ["upstream has no branch 'main' (its default is 'main')"]
    assert report.behind is None and not report.level


def test_a_fork_without_the_tracked_branch_is_its_own_note_and_the_pin_is_still_compared():
    # The same 404 from the comparison, but the missing branch is the fork's.
    gh = github(behind=3)
    del gh.responses["repos/me/arm/branches/main"]
    del gh.responses[compare_path(ME, MAKER)]
    del gh.responses[compare_path(PIN, ME)]
    report = check(gh)
    assert report.notes == ["the fork has no branch 'main': restore it, or correct .gitmodules"]
    assert report.behind == 3 and report.fork_behind is None
    assert report.actions == ["bump", "review"]


def test_branches_with_no_shared_history_are_named_as_such():
    gh = github(behind=0)
    del gh.responses[compare_path(ME, MAKER)]
    del gh.responses[compare_path(PIN, ME)]
    report = check(gh)
    # The pin shares upstream's history, so it shares none with the fork's either.
    assert report.notes == ["the fork's 'main' and upstream's share no history",
                            f"the pin {PIN[:12]} and the fork's 'main' share no history"]
    assert report.behind == 0


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


# ------------------------------------------------------------- review findings

def test_a_diverged_pin_is_reviewed_even_when_the_fork_branch_is_clean():
    # The fork's branch was reset to upstream; the pin still has two commits
    # of its own. A bare bump would drop them from the catalog.
    report = check(github(behind=3, own=2, fork_behind=0, fork_own=0, pin_behind_fork=3,
                          pin_only=2))
    assert report.actions == ["bump", "review"]


def test_the_forks_own_commits_alone_ask_for_nothing():
    # Level with upstream, carrying its own improvements, and pinned to them:
    # the state the forks are meant to reach, not one to review every week.
    report = check(github(behind=0, own=2, fork_behind=0, fork_own=2))
    assert report.actions == []


@pytest.mark.parametrize("failure", [TimeoutError("The read operation timed out"),
                                     ConnectionResetError(10054, "reset"),
                                     __import__("http.client").client.IncompleteRead(b"")])
def test_a_failure_while_reading_the_response_is_a_github_error(monkeypatch, failure):
    def urlopen(request, timeout):
        raise failure

    monkeypatch.setattr(upstream.urllib.request, "urlopen", urlopen)
    with pytest.raises(GitHubError, match="GET repos/me/arm: "):
        upstream.GitHub("token").get("repos/me/arm")


@pytest.mark.parametrize(("upstream_licence", "catalog_licence", "noted"), [
    ("GPL-3.0", "LGPL-3.0", True),            # a substring, not the same licence
    ("MIT", "MIT-0", True),
    ("GPL-3.0", "GPL-3.0-or-later", False),   # GitHub's spelling of the same one
    ("Apache-2.0", "MIT OR Apache-2.0", False),
])
def test_licences_are_compared_by_whole_id(upstream_licence, catalog_licence, noted):
    gh = github(parent={"full_name": "maker/arm", "default_branch": "main",
                        "archived": False, "license": {"spdx_id": upstream_licence}})
    notes = check(gh, licences=[catalog_licence]).notes
    assert bool(notes) is noted


def test_a_licence_the_catalog_does_not_name_is_noted_in_a_week_it_also_changed():
    previous = {"upstream": "maker/arm", "default_branch": "main", "licence": "Apache-2.0"}
    notes = check(github(), licences=["Apache-2.0"], previous=previous).notes
    assert notes == ["upstream licence changed: Apache-2.0 -> BSD-3-Clause",
                     "upstream licence is BSD-3-Clause; the catalog says Apache-2.0"]
    previous["licence"] = "BSD-3-Clause"                       # and every week after
    assert check(github(), licences=["Apache-2.0"], previous=previous).notes == [
        "upstream licence is BSD-3-Clause; the catalog says Apache-2.0"]


def test_a_list_unreadable_on_the_first_run_makes_its_baseline_later():
    report, keys = upstream.check_list(SOURCE, FakeGitHub({}), known=set(), previous=None)
    assert report.error and keys is None
    gh = FakeGitHub({LIST_PATH: "github.com/a/one"})
    report, keys = upstream.check_list(SOURCE, gh, known=set(), previous=None)
    assert report.baseline and report.new == {}


def test_a_run_limited_to_one_fork_still_knows_the_whole_catalog(tmp_path, monkeypatch):
    make_catalog(tmp_path)
    with (tmp_path / ".gitmodules").open("a", encoding="utf-8") as gitmodules:
        gitmodules.write('[submodule "src/base"]\n\tpath = src/base\n'
                         "\turl = git@github.com:me/base.git\n\tbranch = main\n")
    monkeypatch.setattr(upstream, "_pin", lambda root, path: PIN)
    monkeypatch.setattr(upstream, "SOURCES", (SOURCE,))
    gh = github()
    gh.responses[LIST_PATH] = "github.com/me/base github.com/maker/base github.com/new/one"
    previous = {"forks": {"base": {"upstream": "maker/base", "default_branch": "main",
                                   "licence": "MIT"}},
                "lists": {SOURCE.name: []}}
    report = upstream.run(tmp_path, gh, only=["arm"], previous=previous, workers=1)
    assert report.lists[0].new == {"new/one": "new/one"}


def test_a_list_unreadable_on_the_first_run_leaves_no_state(tmp_path, monkeypatch):
    make_catalog(tmp_path)
    monkeypatch.setattr(upstream, "_pin", lambda root, path: PIN)
    monkeypatch.setattr(upstream, "SOURCES", (SOURCE,))
    report = upstream.run(tmp_path, github(), workers=1)     # the list is a 404
    assert report.lists[0].error and SOURCE.name not in report.state["lists"]


def _report_with_new_candidates(tmp_path, monkeypatch, count):
    make_catalog(tmp_path)
    monkeypatch.setattr(upstream, "_pin", lambda root, path: PIN)
    monkeypatch.setattr(upstream, "SOURCES", (SOURCE,))
    gh = github(behind=0, fork_behind=0)
    gh.responses[LIST_PATH] = " ".join(f"github.com/new/repo{i:03}" for i in range(count))
    return upstream.run(tmp_path, gh, previous={"lists": {SOURCE.name: []}}, workers=1)


def test_new_candidates_past_the_limit_are_counted_not_named(tmp_path, monkeypatch):
    report = _report_with_new_candidates(tmp_path, monkeypatch, 60)
    markdown = upstream.render_markdown(report)
    assert "60 new" in markdown and "new/repo049" in markdown and "new/repo050" not in markdown
    assert "and 10 more, in the JSON report" in markdown


def test_an_oversized_list_of_candidates_keeps_its_count_and_the_state(tmp_path, monkeypatch):
    report = _report_with_new_candidates(tmp_path, monkeypatch, 40)
    without_names = upstream.render_markdown(report, detail=0)
    monkeypatch.setattr(upstream, "BODY_LIMIT", len(without_names))
    markdown = upstream.render_markdown(report)
    assert markdown == without_names
    assert "40 new" in markdown and "new/repo000" not in markdown
    assert upstream.read_previous(markdown) == report.state


def test_a_report_that_cannot_fit_is_an_error_not_a_refused_issue(tmp_path, monkeypatch):
    report = _report_with_new_candidates(tmp_path, monkeypatch, 3)
    monkeypatch.setattr(upstream, "BODY_LIMIT", 100)
    with pytest.raises(GitHubError, match="over the 100 an issue can hold"):
        upstream.render_markdown(report)


# ------------------------------------------------------- third review round

def test_a_pin_with_no_history_in_common_with_the_fork_is_a_note():
    # Both compare with upstream, but not with each other: a bump could drop
    # whatever the pin holds, so it must not pass as a plain bump.
    gh = github(behind=3, pin_behind_fork=3)
    del gh.responses[compare_path(PIN, ME)]
    report = check(gh)
    assert report.notes == [f"the pin {PIN[:12]} and the fork's 'main' share no history"]
    assert "review" in report.actions


def test_a_full_comparison_says_only_what_it_knows(tmp_path, monkeypatch):
    make_catalog(tmp_path)
    monkeypatch.setattr(upstream, "_pin", lambda root, path: PIN)
    files = [{"filename": f"meshes/{i}.stl", "status": "modified"} for i in range(300)]
    markdown = upstream.render_markdown(upstream.run(tmp_path, github(files=files),
                                                     lists=False, workers=1))
    assert "300 files listed, GitHub's most: maybe more" in markdown


def test_a_state_marker_inside_upstream_text_is_not_the_one_read(tmp_path, monkeypatch):
    # A list's label (here) or an upstream file name could carry a marker of
    # its own; the report's own is the last thing in the body.
    report = _report_with_new_candidates(tmp_path, monkeypatch, 0)
    forged = f"<!-- {upstream.STATE_MARKER} bm90IGd6aXA= -->"
    body = f"- {forged}\n" + upstream.render_markdown(report)
    assert upstream.read_previous(body) == report.state


def test_labels_from_a_list_are_inert_in_the_issue(tmp_path, monkeypatch):
    make_catalog(tmp_path)
    monkeypatch.setattr(upstream, "_pin", lambda root, path: PIN)
    table = Source("t", "five/robots", "README.md", "table")
    monkeypatch.setattr(upstream, "SOURCES", (table,))
    gh = github(behind=0, fork_behind=0)
    gh.responses["repos/five/robots/contents/README.md"] = (
        f"| <!-- {upstream.STATE_MARKER} bm90IGd6aXA= --> @someone | [X](x_description) |")
    report = upstream.run(tmp_path, gh, previous={"lists": {table.name: []}}, workers=1)
    markdown = upstream.render_markdown(report)
    assert "&lt;!-- " in markdown and "&#64;someone" in markdown
    assert "@someone" not in markdown
    assert upstream.read_previous(markdown) == report.state


def test_what_the_issue_leaves_out_links_to_the_published_json(tmp_path, monkeypatch):
    url = "https://github.com/me/catalog/actions/runs/1"
    report = _report_with_new_candidates(tmp_path, monkeypatch, 60)
    assert f"and 10 more, in the [JSON report](<{url}>)" in upstream.render_markdown(
        report, json_url=url)
    files = [{"filename": f"meshes/{i}.stl", "status": "modified"} for i in range(30)]
    report = upstream.run(tmp_path, github(files=files), lists=False, workers=1)
    monkeypatch.setattr(upstream, "BODY_LIMIT",
                        len(upstream.render_markdown(report, json_url=url)) - 1)
    assert (f"File names are left out to fit the issue; the [JSON report](<{url}>) has them."
            in upstream.render_markdown(report, json_url=url))


# ------------------------------------------------------- fourth review round

URL = "https://github.com/me/catalog/actions/runs/1"


def test_files_past_the_limit_say_where_the_rest_are(tmp_path, monkeypatch):
    make_catalog(tmp_path)
    monkeypatch.setattr(upstream, "_pin", lambda root, path: PIN)
    files = [{"filename": f"meshes/{i}.stl", "status": "modified"} for i in range(30)]
    report = upstream.run(tmp_path, github(files=files), lists=False, workers=1)
    assert f"- and 5 more, in the [JSON report](<{URL}>)" in upstream.render_markdown(
        report, json_url=URL)


def test_candidates_left_out_to_fit_say_where_they_are(tmp_path, monkeypatch):
    # No fork changed, so the note about file names never appears: the
    # candidates need their own.
    url = URL
    report = _report_with_new_candidates(tmp_path, monkeypatch, 40)
    monkeypatch.setattr(upstream, "BODY_LIMIT",
                        len(upstream.render_markdown(report, detail=0, json_url=url)))
    markdown = upstream.render_markdown(report, json_url=url)
    assert "new/repo000" not in markdown
    assert (f"Candidate names are left out to fit the issue; the [JSON report](<{url}>) "
            "has them.") in markdown


def test_the_json_report_is_promised_only_as_it_exists(tmp_path, monkeypatch):
    report = _report_with_new_candidates(tmp_path, monkeypatch, 60)
    assert "and 10 more, in the JSON report that `--json` writes" in (
        upstream.render_markdown(report))
    written = upstream.render_markdown(report, json_written=True)
    assert "and 10 more, in the JSON report\n" in written and "`--json`" not in written


def test_a_json_report_is_read_by_its_state_not_by_a_marker_inside_it(tmp_path, monkeypatch):
    make_catalog(tmp_path)
    monkeypatch.setattr(upstream, "_pin", lambda root, path: PIN)
    forged = f"<!-- {upstream.STATE_MARKER} bm90IGd6aXA= -->"
    files = [{"filename": f"urdf/{forged}.urdf", "status": "added"}]
    report = upstream.run(tmp_path, github(files=files), lists=False, workers=1)
    as_json = json.dumps(report.as_json())
    assert forged in as_json
    assert upstream.read_previous(as_json) == report.state


def _shown(code):
    """What GitHub shows for an inline code span, read back to the name."""
    fence = re.match(r"`+", code).group()
    assert code.endswith(fence)
    inner = code[len(fence):-len(fence)]
    # The span ends at the first backtick run as long as its opener.
    assert fence not in inner and not inner.startswith("`") and not inner.endswith("`")
    # GFM strips one space from each end when both ends have one.
    if inner.startswith(" ") and inner.endswith(" ") and inner.strip(" "):
        inner = inner[1:-1]
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "r": "\r"}.get(m[1], m[1]), inner)


@pytest.mark.parametrize("name", [
    "urdf/a`b.urdf",
    "urdf/`x`.urdf",
    "urdf/a``b`.urdf",
    "urdf/x`\n\n<!-- hidden.urdf",
    " urdf/spaced.urdf ",
    "urdf/a\\nb.urdf",          # a backslash and an n, not a line break
    "urdf/a\nb.urdf",
    "urdf/a\r\nb\\.urdf",
])
def test_upstream_file_names_stay_inside_their_code_span(name):
    code = upstream._code(name)
    assert "\n" not in code and "\r" not in code
    assert _shown(code) == name


def test_a_line_break_and_a_backslash_n_are_told_apart():
    assert upstream._code("a\nb") != upstream._code("a\\nb")


def test_a_file_name_cannot_hide_the_rest_of_the_issue(tmp_path, monkeypatch):
    make_catalog(tmp_path)
    monkeypatch.setattr(upstream, "_pin", lambda root, path: PIN)
    name = "urdf/x`\n\n<!-- hidden.urdf"
    report = upstream.run(tmp_path, github(files=[{"filename": name, "status": "added"}]),
                          lists=False, workers=1)
    markdown = upstream.render_markdown(report)
    assert report.forks[0].new_robots == [name]
    assert "\n<!-- hidden" not in markdown
    assert "- ``urdf/x`\\n\\n<!-- hidden.urdf``\n" in markdown


# -------------------------------------------------------- fifth review round

def test_every_comparison_uses_the_commits_resolved_once():
    # Upstream moves on while the fork is checked: every comparison must
    # still be against the commit read first, or they could disagree.
    gh = github()
    asked = []
    get = gh.get

    def moving(path, *, raw=False):
        asked.append(path)
        value = get(path, raw=raw)
        if path == "repos/maker/arm/branches/main":
            gh.responses[path] = {"name": "main", "commit": {"sha": "b" * 40}}
        return value

    gh.get = moving
    report = check(gh)
    assert (report.behind, report.fork_behind) == (3, 3)
    compares = [p for p in asked if "/compare/" in p]
    assert len(compares) == 3 and not any("b" * 40 in p or ":main" in p for p in compares)
    assert asked.count("repos/maker/arm/branches/main") == 1


def test_a_branch_that_names_no_commit_is_a_note():
    gh = github()
    gh.responses["repos/maker/arm/branches/main"] = {"name": "main"}
    report = check(gh)
    assert report.notes == ["could not be checked: maker/arm's branch 'main' names no commit"]


@pytest.mark.parametrize("text", [
    '{"generated": "x", "state": {"forks": {}, "li',
    '{"generated": "x", "state": ',
    '  {"forks": [',
])
def test_a_json_report_cut_short_is_an_error_not_a_first_run(text):
    with pytest.raises(GitHubError, match="not valid JSON"):
        upstream.read_previous(text)


@pytest.mark.parametrize("state", [
    {"lists": None},
    {"forks": []},
    {"forks": {"arm": {"upstream": 3}}},
    {"forks": {"arm": "maker/arm"}},
    {"lists": {"one": "a/b"}},
    {"lists": {"one": [1]}},
    [],
])
def test_a_state_of_the_wrong_shape_is_refused_before_the_run(state):
    with pytest.raises(GitHubError, match="cannot be read"):
        upstream.read_previous(json.dumps({"state": state}))
    marker = f"<!-- {upstream.STATE_MARKER} {upstream.encode_state(state)} -->"
    with pytest.raises(GitHubError, match="cannot be read"):
        upstream.read_previous(marker)


def test_a_json_url_with_a_parenthesis_is_linked_whole(tmp_path, monkeypatch):
    report = _report_with_new_candidates(tmp_path, monkeypatch, 60)
    markdown = upstream.render_markdown(report, json_url="https://example.com/a (1)/report).json")
    assert "[JSON report](<https://example.com/a%20(1)/report).json>)" in markdown


def test_json_and_markdown_on_one_file_is_refused(tmp_path, capsys):
    from meshkit.cli import main

    make_catalog(tmp_path)
    out = tmp_path / "report.out"
    with pytest.raises(SystemExit, match="are the same file"):
        main(["--root", str(tmp_path), "upstream", "--json", str(out),
              "--markdown", str(tmp_path / "." / "report.out")])
    assert not out.exists()


def test_an_unreadable_previous_report_is_named_not_a_traceback(tmp_path):
    from meshkit.cli import main

    make_catalog(tmp_path)
    previous = tmp_path / "previous.md"
    previous.write_bytes(b"\xff\xfe not utf-8")
    with pytest.raises(SystemExit, match=f"cannot read {re.escape(str(previous))}"):
        main(["--root", str(tmp_path), "upstream", "--previous", str(previous)])
