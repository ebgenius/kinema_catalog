"""Where each fork stands against the repository it was forked from.

``meshkit upstream`` reports; it never merges, syncs or pushes. Per fork it
compares three commits on the branch the catalog tracks (``.gitmodules``
``branch``, not the upstream's default, which can be another line entirely):

- the **pin**, the commit this repository's submodule records;
- the **fork's branch** on GitHub;
- the **upstream's branch**, in the repository GitHub lists as the fork's parent.

From those come what to do: *sync* the fork's branch when it is behind and has
no commits of its own, *bump* the pin when it is behind, *reconvert* when
upstream changed meshes, and *review* anything a person has to look at -- a
fork that has diverged, robots upstream added, an upstream that was archived,
renamed, lost the branch or changed its licence.

It also reads the lists the catalog draws its candidates from and reports the
repositories each one gained since the last run: what the next audit should
look at (*fork*). "Since the last run" needs the last run's state, which the
Markdown report carries at its end, so the weekly job only has to hand back
the issue it last wrote.
"""

from __future__ import annotations

import base64
import configparser
import gzip
import http.client
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

API = "https://api.github.com"
STATE_MARKER = "meshkit-upstream-state:v1"
# GitHub lists at most this many files in a comparison.
COMPARE_FILE_LIMIT = 300
# Per category, in the Markdown; the JSON has every file.
LISTED_FILES = 25
BODY_LIMIT = 60_000   # GitHub refuses an issue body over 65,536 characters

MESH_SUFFIXES = {".dae", ".stl", ".obj", ".mtl", ".glb", ".gltf", ".ply"}
DESCRIPTION_SUFFIXES = (".urdf", ".xacro", ".srdf", ".sdf")
ROBOT_SUFFIXES = (".urdf", ".urdf.xacro")
# The licences GitHub reports when it cannot name one.
UNNAMED_LICENCES = {None, "", "NOASSERTION", "OTHER"}

ACTIONS = ("sync", "bump", "reconvert", "review", "fork")


class GitHubError(RuntimeError):
    """A GitHub API request failed."""


class NotFound(GitHubError):
    """GitHub answered 404."""


class GitHub:
    """The few read-only GitHub API calls this needs."""

    def __init__(self, token: str):
        self.token = token

    def get(self, path: str, *, raw: bool = False):
        request = urllib.request.Request(f"{API}/{path}", headers={
            "Accept": "application/vnd.github.raw" if raw else "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "meshkit-upstream",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise NotFound(f"GET {path}: not found") from None
            raise GitHubError(f"GET {path}: HTTP {exc.code} {exc.reason}") from None
        except urllib.error.URLError as exc:
            raise GitHubError(f"GET {path}: {exc.reason}") from None
        except (OSError, http.client.HTTPException) as exc:
            # A timeout or reset while reading the response is not wrapped in
            # URLError. Raised as itself, it would end the whole report instead
            # of one fork's or one list's part of it.
            raise GitHubError(f"GET {path}: {type(exc).__name__}: {exc}") from None
        try:
            return body.decode("utf-8") if raw else json.loads(body)
        except ValueError as exc:
            raise GitHubError(f"GET {path}: unreadable response: {exc}") from None

    def repo(self, name: str) -> dict:
        return self.get(f"repos/{name}")

    def compare(self, repo: str, base: str, head: str) -> dict:
        quote = lambda ref: urllib.parse.quote(ref, safe="/:")  # noqa: E731
        return self.get(f"repos/{repo}/compare/{quote(base)}...{quote(head)}?per_page=100")

    def file(self, repo: str, path: str) -> str:
        return self.get(f"repos/{repo}/contents/{urllib.parse.quote(path)}", raw=True)


def token() -> str:
    """A GitHub token: GITHUB_TOKEN or GH_TOKEN, else the GitHub CLI's."""
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(name):
            return os.environ[name]
    try:
        result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True,
                                timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        result = None
    if result is not None and result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    raise GitHubError("no GitHub token: set GITHUB_TOKEN, or log in with `gh auth login`")


# ----------------------------------------------------------------------- forks

@dataclass(frozen=True)
class Fork:
    name: str            # its directory under src/
    repo: str            # owner/name on GitHub
    branch: str          # the branch the catalog tracks
    pin: str | None      # the commit the submodule records; None outside a git checkout


_GITHUB_URL = re.compile(r"github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?/?$")


def read_forks(root: Path) -> list[Fork]:
    """Every submodule under src/, as .gitmodules and the index's gitlinks give it."""
    parser = configparser.ConfigParser()
    parser.read(root / ".gitmodules", encoding="utf-8")
    forks = []
    for section in parser.sections():
        path = parser[section].get("path", "")
        if not path.startswith("src/"):
            continue
        name = path.removeprefix("src/")
        url = parser[section].get("url", "")
        match = _GITHUB_URL.search(url)
        if not match:
            raise GitHubError(f".gitmodules: {path} is not a GitHub URL: {url}")
        branch = parser[section].get("branch")
        if not branch:
            raise GitHubError(f".gitmodules: {path} names no branch; the report compares "
                              "the branch the catalog tracks")
        forks.append(Fork(name, f"{match.group(1)}/{match.group(2)}", branch, _pin(root, path)))
    return sorted(forks, key=lambda f: f.name.lower())


def _pin(root: Path, path: str) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(root), "ls-tree", "HEAD", "--", path],
                                capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    fields = result.stdout.split()
    return fields[2] if result.returncode == 0 and len(fields) >= 3 and fields[1] == "commit" \
        else None


def classify(filename: str) -> str | None:
    """Which of the changes that matter a file is, or None."""
    path = PurePosixPath(filename.lower())
    if path.name.endswith(DESCRIPTION_SUFFIXES):
        return "description"
    if path.suffix in MESH_SUFFIXES:
        return "meshes"
    if path.suffix in (".yaml", ".yml") and ("config" in path.parts[:-1] or "limit" in path.name):
        return "config"
    return None


@dataclass
class ForkReport:
    name: str
    repo: str
    branch: str
    pin: str | None
    upstream: str | None = None
    upstream_default_branch: str | None = None
    upstream_archived: bool = False
    upstream_licence: str | None = None
    behind: int | None = None        # upstream commits the pin lacks
    own: int | None = None           # pinned commits upstream lacks
    fork_behind: int | None = None   # upstream commits the fork's branch lacks
    fork_own: int | None = None      # the fork branch's commits upstream lacks
    pin_behind_fork: int | None = None
    changed: dict[str, list[str]] = field(default_factory=dict)
    other_changed: int = 0
    truncated: bool = False
    new_robots: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)

    @property
    def level(self) -> bool:
        """The pin has every upstream commit on the tracked branch."""
        return self.behind == 0

    @property
    def compare_url(self) -> str | None:
        if not (self.upstream and self.pin):
            return None
        owner = self.upstream.split("/")[0]
        return f"https://github.com/{self.repo}/compare/{self.pin}...{owner}:{self.branch}"


def check_fork(fork: Fork, github: GitHub, *, licences: list[str],
               previous: dict | None = None) -> ForkReport:
    """One fork against its upstream. ``licences`` are its catalog entries' licences."""
    report = ForkReport(fork.name, fork.repo, fork.branch, fork.pin)
    try:
        _check_fork(report, fork, github, licences, previous or {})
    except GitHubError as exc:
        report.notes.append(f"could not be checked: {exc}")
    report.actions = _actions(report)
    return report


def _check_fork(report: ForkReport, fork: Fork, github: GitHub, licences: list[str],
                previous: dict) -> None:
    parent = github.repo(fork.repo).get("parent")
    if not parent:
        report.notes.append(f"{fork.repo} is not a fork on GitHub: nothing to compare with")
        return
    report.upstream = parent["full_name"]
    report.upstream_default_branch = parent.get("default_branch")
    report.upstream_archived = bool(parent.get("archived"))
    report.upstream_licence = (parent.get("license") or {}).get("spdx_id")

    if report.upstream_archived:
        report.notes.append(f"upstream {report.upstream} is archived: find out whether it "
                            "moved, or the fork is now the maintainer")
    if previous.get("upstream") and previous["upstream"] != report.upstream:
        report.notes.append(f"upstream renamed or moved: {previous['upstream']} -> "
                            f"{report.upstream}")
    if (previous.get("default_branch")
            and previous["default_branch"] != report.upstream_default_branch):
        report.notes.append(f"upstream default branch changed: {previous['default_branch']} "
                            f"-> {report.upstream_default_branch}")
    if "licence" in previous and previous["licence"] != report.upstream_licence:
        report.notes.append(f"upstream licence changed: {previous['licence'] or 'none'} -> "
                            f"{report.upstream_licence or 'none'}")
    # Not an elif: this holds every week, not only until a previous run exists.
    if (report.upstream_licence not in UNNAMED_LICENCES and licences
            and not any(_licence_id(report.upstream_licence) in _licence_ids(licence)
                        for licence in licences)):
        report.notes.append(f"upstream licence is {report.upstream_licence}; the catalog "
                            f"says {', '.join(sorted(set(licences)))}")

    owner = report.upstream.split("/")[0]
    upstream_head = f"{owner}:{fork.branch}"
    try:
        fork_vs = github.compare(fork.repo, f"{fork.repo.split('/')[0]}:{fork.branch}",
                                 upstream_head)
    except NotFound:
        report.notes.append(f"upstream has no branch {fork.branch!r} (its default is "
                            f"{report.upstream_default_branch!r})")
        return
    report.fork_behind, report.fork_own = fork_vs["ahead_by"], fork_vs["behind_by"]

    if fork.pin is None:
        return
    try:
        pinned = github.compare(fork.repo, fork.pin, upstream_head)
    except NotFound:
        report.notes.append(f"the pin {fork.pin[:12]} is not in {fork.repo}: push it")
        return
    report.behind, report.own = pinned["ahead_by"], pinned["behind_by"]
    report.pin_behind_fork = github.compare(
        fork.repo, fork.pin, f"{fork.repo.split('/')[0]}:{fork.branch}")["ahead_by"]

    if report.behind:
        files = pinned.get("files") or []
        report.truncated = len(files) >= COMPARE_FILE_LIMIT
        for item in files:
            category = classify(item["filename"])
            if category is None:
                report.other_changed += 1
                continue
            report.changed.setdefault(category, []).append(item["filename"])
            if (item.get("status") in ("added", "renamed")
                    and item["filename"].lower().endswith(ROBOT_SUFFIXES)):
                report.new_robots.append(item["filename"])


_SPDX_OPERATORS = {"AND", "OR", "WITH"}


def _licence_id(spdx: str) -> str:
    """An SPDX id, with GPL's -only/-or-later/+ folded: GitHub says GPL-3.0 for both."""
    return re.sub(r"(-only|-or-later|\+)$", "", spdx).lower()


def _licence_ids(expression: str) -> set[str]:
    """The licence ids an SPDX expression names, whole: LGPL-3.0 does not contain GPL-3.0."""
    return {_licence_id(token) for token in re.findall(r"[\w.+-]+", expression)
            if token not in _SPDX_OPERATORS}


def _actions(report: ForkReport) -> list[str]:
    actions = []
    if report.fork_behind:
        actions.append("review" if report.fork_own else "sync")
    if report.behind or report.pin_behind_fork:
        actions.append("bump")
    if report.behind and report.changed.get("meshes"):
        actions.append("reconvert")
    # A pin with commits upstream lacks has diverged, whatever the fork's branch
    # says now: bumping it without a look could drop them from the catalog.
    if report.notes or report.new_robots or report.own:
        actions.append("review")
    return [a for a in ACTIONS if a in actions]


# ----------------------------------------------------------------------- lists

@dataclass(frozen=True)
class Source:
    name: str
    repo: str
    path: str
    kind: str   # "github": repository links; "table": relative links in Markdown tables


SOURCES = (
    Source("awesome-robot-descriptions", "robot-descriptions/awesome-robot-descriptions",
           "README.md", "github"),
    Source("robot_descriptions.py", "robot-descriptions/robot_descriptions.py",
           "robot_descriptions/_repositories.py", "github"),
    Source("fiveages robots", "fiveages-sim/robot_descriptions", "README.md", "table"),
    Source("fiveages submodules", "fiveages-sim/robot_descriptions", ".gitmodules", "github"),
)

_LINK = re.compile(r"github\.com[/:]([\w.-]+)/([\w.-]+)")
_NOT_OWNERS = {"orgs", "sponsors", "topics", "features", "marketplace", "apps", "settings",
               "about", "login", "collections", "user-attachments", "notifications"}
_TABLE_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def extract(source: Source, text: str) -> dict[str, str]:
    """The list's candidates, as key -> label."""
    found: dict[str, str] = {}
    if source.kind == "github":
        for owner, name in _LINK.findall(text):
            name = name.removesuffix(".git").rstrip(".")
            if owner.lower() in _NOT_OWNERS or not name:
                continue
            key = f"{owner}/{name}".lower()
            if key != source.repo.lower():
                found.setdefault(key, f"{owner}/{name}")
        return found
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        for label, target in _TABLE_LINK.findall(line):
            if "://" in target or target.startswith("#") or label.startswith("!"):
                continue
            path = target.strip("./").rstrip("/")
            if path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".md")):
                continue
            brand = cells[0] if cells and "[" not in cells[0] else ""
            found.setdefault(f"{source.repo}:{path}".lower(),
                             f"{brand} {label}".strip() + f" ({source.repo}/{path})")
    return found


@dataclass
class ListReport:
    name: str
    repo: str
    count: int = 0
    new: dict[str, str] = field(default_factory=dict)
    baseline: bool = False
    error: str | None = None


def check_list(source: Source, github: GitHub, *, known: set[str],
               previous: list[str] | None) -> tuple[ListReport, list[str] | None]:
    """The list's report, and the keys to remember for the next run.

    None for the keys when there is nothing to remember: a first run that
    could not read the list leaves no baseline, so the next run makes one
    instead of reporting the whole list as new.
    """
    report = ListReport(source.name, source.repo)
    try:
        candidates = extract(source, github.file(source.repo, source.path))
    except GitHubError as exc:
        report.error = str(exc)
        return report, None if previous is None else list(previous)
    candidates = {k: v for k, v in candidates.items() if k not in known}
    report.count = len(candidates)
    if previous is None:
        report.baseline = True
    else:
        seen = set(previous)
        report.new = {k: v for k, v in sorted(candidates.items()) if k not in seen}
    return report, sorted(candidates)


# ---------------------------------------------------------------------- report

@dataclass
class Report:
    generated: str
    forks: list[ForkReport]
    lists: list[ListReport]
    state: dict

    def as_json(self) -> dict:
        return {"generated": self.generated,
                "forks": [asdict(f) | {"level": f.level, "compare_url": f.compare_url}
                          for f in self.forks],
                "lists": [asdict(item) for item in self.lists],
                "state": self.state}


def run(root: Path, github: GitHub, *, only: list[str] | None = None,
        previous: dict | None = None, lists: bool = True, workers: int = 8) -> Report:
    from meshkit import catalog

    previous = previous or {}
    forks = all_forks = read_forks(root)
    if only:
        unknown = set(only) - {f.name for f in forks}
        if unknown:
            raise GitHubError(f"not a submodule under src/: {', '.join(sorted(unknown))}")
        forks = [f for f in forks if f.name in only]
    licences: dict[str, list[str]] = {}
    for entry in catalog.load_sources(root):
        licences.setdefault(entry["submodule"], []).append(entry["licence"])

    old_forks = previous.get("forks", {})
    with ThreadPoolExecutor(max_workers=workers) as pool:
        reports = list(pool.map(lambda f: check_fork(
            f, github, licences=licences.get(f.name, []), previous=old_forks.get(f.name)),
            forks))

    state_forks = dict(old_forks)
    for report in reports:
        if report.upstream:
            state_forks[report.name] = {"upstream": report.upstream,
                                        "default_branch": report.upstream_default_branch,
                                        "licence": report.upstream_licence}

    old_lists = previous.get("lists", {})
    state_lists = dict(old_lists)
    list_reports = []
    if lists:
        # The whole catalog, not only the forks this run checked (--fork), and
        # every upstream known: one whose lookup failed today is in the state.
        known = ({f.repo.lower() for f in all_forks}
                 | {s["upstream"].lower() for s in state_forks.values() if s.get("upstream")})
        for source in SOURCES:
            report, keys = check_list(source, github, known=known,
                                      previous=old_lists.get(source.name))
            list_reports.append(report)
            if keys is not None:
                state_lists[source.name] = keys

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return Report(generated, reports, list_reports,
                  {"forks": state_forks, "lists": state_lists})


def encode_state(state: dict) -> str:
    packed = gzip.compress(json.dumps(state, sort_keys=True).encode("utf-8"), mtime=0)
    return base64.b64encode(packed).decode("ascii")


def read_previous(text: str) -> dict:
    """The state a previous report carries: from its Markdown, or its JSON."""
    match = re.search(rf"<!--\s*{re.escape(STATE_MARKER)}\s+([A-Za-z0-9+/=\s]+?)\s*-->", text)
    if match:
        try:
            return json.loads(gzip.decompress(base64.b64decode("".join(match.group(1).split()))))
        except (ValueError, OSError) as exc:
            raise GitHubError(f"the previous report's state cannot be read: {exc}") from None
    if not text.strip():
        return {}
    try:
        document = json.loads(text)
    except json.JSONDecodeError:
        # A report from before there was any state, or not a report at all:
        # start again, so every list reads as a new baseline.
        return {}
    return document.get("state", {}) if isinstance(document, dict) else {}


def _count(value: int | None) -> str:
    return "?" if value is None else str(value)


def render_markdown(report: Report, *, file_lists: bool = True) -> str:
    forks = report.forks
    level = sum(f.level for f in forks)
    lines = [
        "# Upstream report",
        "",
        f"Written by `meshkit upstream` on {report.generated}. Each fork is compared on the "
        "branch the catalog tracks: **behind** is upstream commits the pinned commit lacks, "
        "**own** is pinned commits upstream lacks. Nothing here has been merged or synced.",
        "",
        f"**{level} of {len(forks)} forks are level with upstream.**",
        "",
        "| Fork | Upstream | Branch | Behind | Own | Changes that matter | Do |",
        "|---|---|---|--:|--:|---|---|",
    ]
    for f in forks:
        behind = _count(f.behind)
        if f.behind and f.compare_url:
            behind = f"[{behind}]({f.compare_url})"
        changes = ", ".join(f"{len(files)} {category}"
                            for category, files in sorted(f.changed.items()))
        if f.truncated:
            changes += " (first 300 files)"
        if f.new_robots:
            changes += f"; **{len(f.new_robots)} new robot file(s)**"
        upstream = f"[{f.upstream}](https://github.com/{f.upstream})" if f.upstream else "?"
        lines.append(f"| {f.name} | {upstream} | {f.branch} | {behind} | {_count(f.own)} | "
                     f"{changes or '-'} | {', '.join(f.actions) or '-'} |")

    noted = [f for f in forks if f.notes]
    if noted:
        lines += ["", "## Needs a look", ""]
        for f in noted:
            lines += [f"- **{f.name}:** {note}" for note in f.notes]

    changed = [f for f in forks if f.behind and (f.changed or f.new_robots)]
    if changed and file_lists:
        lines += ["", "## What upstream changed", ""]
        for f in changed:
            total = sum(len(v) for v in f.changed.values()) + f.other_changed
            lines += [f"<details><summary><b>{f.name}</b>: {f.behind} commit(s), "
                      f"{total} file(s)</summary>", ""]
            if f.new_robots:
                lines += ["New robot files, not in the index:", ""]
                lines += [f"- `{name}`" for name in f.new_robots] + [""]
            for category, files in sorted(f.changed.items()):
                lines += [f"{category.capitalize()} ({len(files)}):", ""]
                lines += [f"- `{name}`" for name in files[:LISTED_FILES]]
                if len(files) > LISTED_FILES:
                    lines.append(f"- and {len(files) - LISTED_FILES} more")
                lines.append("")
            if f.other_changed:
                lines += [f"And {f.other_changed} other file(s).", ""]
            lines += ["</details>", ""]

    if report.lists:
        lines += ["", "## New in the lists the catalog draws from", ""]
        for item in report.lists:
            source = f"[{item.name}](https://github.com/{item.repo})"
            if item.error:
                lines.append(f"- {source}: could not be read ({item.error})")
            elif item.baseline:
                lines.append(f"- {source}: {item.count} candidates not in the catalog; "
                             "recorded as the baseline, so the next report shows what is new")
            elif not item.new:
                lines.append(f"- {source}: nothing new ({item.count} not in the catalog)")
            else:
                lines.append(f"- {source}: {len(item.new)} new (*fork*, after the audit):")
                for key, label in item.new.items():
                    link = f"https://github.com/{key}" if ":" not in key else None
                    lines.append(f"  - [{label}]({link})" if link else f"  - {label}")

    lines += [
        "",
        "## What the actions mean",
        "",
        "- **sync:** the fork's branch is behind and has no commits of its own: "
        "`gh repo sync <fork> --branch <branch>`.",
        "- **bump:** the pin is behind; after syncing, update the submodule in a pull "
        "request and run `./kinema_catalog.sh --check`.",
        "- **reconvert:** upstream changed meshes; convert them again after the bump.",
        "- **review:** something a person has to decide: a fork with its own commits, "
        "new robots, or the notes above.",
        "- **fork:** a candidate for the next audit.",
        "",
        f"<!-- {STATE_MARKER} {encode_state(report.state)} -->",
        "",
    ]
    text = "\n".join(lines)
    if len(text) > BODY_LIMIT and file_lists:
        return render_markdown(report, file_lists=False)
    return text
