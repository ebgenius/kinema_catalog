"""meshkit audit: every robot the catalog has or could have, measured and scored.

Per robot, not per repository: a repository with forty URDFs is forty rows.
The robots come from two places:

* **the catalog's forks**: every entry in ``catalog.json``, rendered exactly
  as the launcher renders it (its arguments, its ``mesh_base``);
* **the candidates**: every repository the lists in ``upstream.SOURCES`` name
  that the catalog does not carry yet, and fiveages' README folders. Each is
  shallow-cloned into a cache outside the repository, and every robot file in
  it is found and measured the same way.

A robot file is a ``.urdf``, a ``.xacro`` whose ``<robot>`` does something
besides define macros, or an MJCF ``.xml`` whose ``<worldbody>`` holds a body
of its own (a ``scene.xml`` that only includes the robot is not a second
robot). SDF is counted per repository but not measured: Kinema reads URDF and
MJCF.

Each repository is measured in a subprocess with a time limit, so one that
hangs xacro or holds a pathological mesh costs its own rows and nothing else.

Two of the plan's columns are not measured here, and the report says so:
whether Kinema imports the robot (that needs Blender and Kinema), and whether
the kinematics match the maker's own description (that needs a pairing of
sources per robot, which is step 5's call).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# What a score is made of, out of 100. Kept here, in one place, so a change of
# mind is one edit; the report prints this table.
WEIGHTS = {
    "licence": 15,    # a licence named, and a licence text present (not read)
    "alive": 10,      # upstream committed to in the last year (half: in three)
    "flattens": 20,   # xacro evaluates, or the MJCF parses, and every mesh is there
    "limits": 15,     # position and velocity limits on every moving joint
    "inertia": 10,    # mass on every link that has geometry
    "look": 20,       # meshes with authored normals, and with materials
    "weight": 10,     # small enough to download and to draw
}
# Full marks for weight up to the first number, none from the second.
TRIANGLES = (200_000, 2_000_000)
MEGABYTES = (50, 500)

MESH_SUFFIXES = (".stl", ".dae", ".obj", ".glb", ".gltf", ".ply")
SKIP_DIRS = {".git", "build", "install", "log", "__pycache__", "node_modules", ".github"}
UNNAMED = {None, "", "NOASSERTION", "NONE", "OTHER"}
LICENCE_FILES = ("license", "licence", "copying")
# What package.xml templates leave in <license> before anyone fills it in.
PLACEHOLDERS = {"todo", "todo: license declaration", "tbd", "unknown", "various",
                "see license", "see license file", "n/a", "na"}
LICENCE_TAGS = 10   # <license> names kept from one package.xml, each whole
REPO_TIMEOUT = 20 * 60
CLONE_TIMEOUT = 30 * 60
_LFS = b"version https://git-lfs"


def default_cache() -> Path:
    """Outside the repository: clones of a hundred-odd repositories are no source.

    Under the home folder, not %LOCALAPPDATA%: a packaged Windows app (the
    Claude desktop app, a Store Python) has that redirected to a folder of its
    own, so a run from a terminal would find none of its clones.
    """
    base = os.environ.get("XDG_CACHE_HOME")
    return (Path(base) if base else Path.home() / ".cache") / "kinema_catalog" / "audit"


# ------------------------------------------------------------------ candidates

@dataclass
class Candidate:
    """A repository (or one folder of it) to measure."""

    key: str                 # the list's key, or "fork:<submodule>"
    repo: str                # owner/name as GitHub calls it today
    folder: str = ""         # a folder inside it, for fiveages' README rows
    sources: list[str] = field(default_factory=list)
    fork: str | None = None  # the submodule, for the catalog's own
    licence: str | None = None
    archived: bool = False
    pushed: str | None = None
    error: str | None = None


REPO_SOURCE = "--repo"       # the source of a repository named on the command line


def gather(root: Path, github, *, lists: bool = True, repos: list[str] | None = None,
           unavailable: list[str] | None = None) -> list[Candidate]:
    """The catalog's forks, then every candidate the lists name, once each, then
    the repositories ``--repo`` names that neither has: the whole inventory.

    ``select`` chooses what is measured from it; the rest still supplies
    packages. A list that cannot be read stops a full audit. With ``repos``,
    it is noted in ``unavailable`` instead: a named repository does not
    depend on the lists.
    """
    from meshkit import upstream

    forks = upstream.read_forks(root)
    candidates: list[Candidate] = []
    known: set[str] = set()
    fork_of: dict[str, Candidate] = {}       # a fork, by its name and its upstream's
    for fork in forks:
        candidate = Candidate(f"fork:{fork.name}", fork.repo, fork=fork.name, sources=["catalog"])
        fork_of[fork.repo.lower()] = candidate
        try:
            meta = github.repo(fork.repo)
            parent = meta.get("parent") or meta
            known |= {fork.repo.lower(), parent["full_name"].lower()}
            fork_of[parent["full_name"].lower()] = candidate
            candidate.licence = (parent.get("license") or {}).get("spdx_id")
            candidate.archived = bool(parent.get("archived"))
            candidate.pushed = parent.get("pushed_at")
        except upstream.GitHubError as exc:
            known.add(fork.repo.lower())
            candidate.error = f"GitHub: {exc}"
        candidates.append(candidate)

    if lists:
        by_key: dict[str, Candidate] = {}
        for source in upstream.SOURCES:
            try:
                found = upstream.extract(source, github.file(source.repo, source.path))
            except upstream.GitHubError as exc:
                if not repos:
                    raise upstream.GitHubError(f"{source.name} cannot be read: {exc}") from None
                if unavailable is not None:
                    unavailable.append(f"{source.name} ({exc})")
                continue
            for key in found:
                repo, _, folder = key.partition(":")
                candidate = by_key.setdefault(key, Candidate(key, repo, folder))
                candidate.sources.append(source.name)
        # GitHub's own name: lists carry renamed repositories under their old
        # name (deepmind/mujoco_menagerie), and a fork's upstream is known by it.
        seen: dict[tuple[str, str], Candidate] = {}
        for candidate in by_key.values():
            try:
                meta = github.repo(candidate.repo)
            except upstream.GitHubError as exc:
                candidate.error = f"GitHub: {exc}"
            else:
                candidate.repo = meta["full_name"]
                candidate.licence = (meta.get("license") or {}).get("spdx_id")
                candidate.archived = bool(meta.get("archived"))
                candidate.pushed = meta.get("pushed_at")
            if candidate.repo.lower() in known and not candidate.folder:
                continue                              # the catalog has it already
            same = seen.get((candidate.repo.lower(), candidate.folder))
            if same:
                same.sources = sorted(set(same.sources) | set(candidate.sources))
                continue
            seen[(candidate.repo.lower(), candidate.folder)] = candidate
        candidates += sorted(seen.values(), key=lambda c: (c.repo.lower(), c.folder))

    def already(name: str) -> Candidate | None:
        """A fork or a list's candidate by that name: marked, not added again."""
        return fork_of.get(name.lower()) or next(
            (c for c in candidates if c.repo.lower() == name.lower() and not c.folder), None)

    for text in repos or []:
        name = repo_name(text)
        same = already(name)
        if same is None:
            try:
                meta = github.repo(name)
            except upstream.GitHubError as exc:
                # A name GitHub does not know is a typo, as with --only.
                raise SelectionError(f"--repo {text}: {exc}") from None
            full = meta["full_name"]
            same = already(full)
        if same is None:
            same = Candidate(full, full, licence=(meta.get("license") or {}).get("spdx_id"),
                             archived=bool(meta.get("archived")), pushed=meta.get("pushed_at"))
            candidates.append(same)
        if REPO_SOURCE not in same.sources:
            same.sources.append(REPO_SOURCE)

    return candidates


def repo_name(text: str) -> str:
    """owner/name, from that or a GitHub URL (https, ssh, with or without .git)."""
    name = text.strip().rstrip("/")
    for prefix in ("https://github.com/", "http://github.com/", "git@github.com:",
                   "github.com/"):
        if name.lower().startswith(prefix):
            name = name[len(prefix):]
            break
    name = name.removesuffix(".git")
    owner, _, repo = name.partition("/")
    if not owner or not repo or "/" in repo or ":" in name:
        raise SelectionError(f"--repo {text}: not a GitHub repository (owner/name)")
    return name


def select(candidates: list[Candidate], only: list[str] | None, *,
           named: bool = False) -> list[Candidate]:
    """The candidates ``--only`` names (by list key, repository or submodule), or all.

    With ``named``, the repositories ``--repo`` named are chosen too, and the
    rest only if ``--only`` names them: ``--repo`` audits what it names.
    """
    if named:
        chosen = select(candidates, only) if only else []
        return [c for c in candidates if REPO_SOURCE in c.sources or c in chosen]
    if not only:
        return candidates
    # Each candidate's names, as a set: matching is by whole name, never part.
    names = [{c.key.lower(), c.repo.lower()} | ({c.fork.lower()} if c.fork else set())
             for c in candidates]
    # A name that matches nothing is a typo, not a request for an empty audit
    # written over the committed one.
    unmatched = [o for o in only if not any(o.lower() in n for n in names)]
    if unmatched:
        raise SelectionError("--only matches nothing: " + ", ".join(unmatched))
    wanted = {o.lower() for o in only}
    return [c for c, n in zip(candidates, names) if n & wanted]


class SelectionError(ValueError):
    """``--only`` named something the audit does not know."""


# ----------------------------------------------------------------------- cache

def _git(*args: str, cwd: Path | None = None, timeout: int = CLONE_TIMEOUT) -> str:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_LFS_SKIP_SMUDGE="1")
    # Windows stops at 260 characters a path, and the cache's own path is long.
    done = subprocess.run(["git", "-c", "core.longpaths=true", *args], cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=timeout, check=False)
    if done.returncode:
        # git's first complaint says why; its last is advice on what to retry.
        lines = [line for line in (done.stderr or done.stdout).splitlines()
                 if line.startswith(("fatal:", "error:"))]
        raise RuntimeError(lines[0] if lines else f"git {args[0]} failed")
    return done.stdout.strip()


def cache_dir(cache: Path, repo: str) -> Path:
    return cache / repo.replace("/", "__")


PARTIAL = ".meshkit-partial"


def _same_remote(a: str, b: str) -> bool:
    def norm(url: str) -> str:
        return url.strip().rstrip("/").removesuffix(".git").lower()
    return norm(a) == norm(b)


def _remove(path: Path) -> None:
    """Delete a tree git wrote: Windows marks its object files read-only."""
    def writable(function, name, exc):
        if isinstance(exc, FileNotFoundError):
            return                        # removed meanwhile: as good as done
        os.chmod(name, 0o700)
        function(name)
    shutil.rmtree(path, onexc=writable)


OWNED = "meshkit-audit"          # the mark of a folder the audit made


def _mark(folder: Path, repo: str) -> None:
    (folder / OWNED).write_text(f"made by meshkit audit: {repo}\n", encoding="utf-8")


# A staging folder older than this cannot belong to a clone still running:
# git is stopped at CLONE_TIMEOUT.
STALE = CLONE_TIMEOUT + 10 * 60


def _clear_dead_staging(dest: Path, *, now: float | None = None) -> None:
    """Remove staging folders for ``dest`` that the audit marked and that died.

    A run's own staging folder is removed by that run, however it fails; one is
    left only when the process itself was killed. Such a folder is cleared once
    its mark is older than ``STALE``: a younger one may be another audit's,
    sharing the cache, with git still writing into it.
    """
    import time

    now = time.time() if now is None else now
    for old in dest.parent.glob(f"{dest.name}{PARTIAL}-*"):
        try:
            age = now - (old / OWNED).stat().st_mtime
        except OSError:
            continue                      # unmarked: not the audit's
        if age > STALE:
            try:
                _remove(old)
            except FileNotFoundError:
                pass                      # another audit cleared it first


def fetch(repo: str, cache: Path, *, update: bool = True) -> tuple[Path, str, str]:
    """A shallow clone of ``repo``'s default branch: (where, commit, its date).

    Only what the audit made is ever reset, replaced or deleted, and it knows
    what it made by a mark it leaves: ``.git/meshkit-audit`` in a clone, and
    ``meshkit-audit`` in a staging folder. ``--cache`` can point anywhere, so
    anything unmarked is refused and left as it is, a clone of the very same
    repository included: it may be someone's checkout, with their changes in
    it. With ``--no-fetch`` nothing is changed, so such a clone is measured as
    it stands. A clone is made in a staging folder of its own and moved in
    when complete; see ``_clear_dead_staging`` for one whose run was killed.
    """
    dest = cache_dir(cache, repo)
    url = f"https://github.com/{repo}.git"
    if dest.parent.is_dir():
        # Whether or not the clone is there now: a killed run's staging
        # folder can outlive a clone another run completed.
        _clear_dead_staging(dest)
    # Whether the place is taken is asked first, and what took it second: a
    # clone is put in place by one rename, .git and all, so a clone another
    # audit puts there between the two questions is seen as the clone it is.
    if not dest.exists():
        _clone(repo, url, dest)
    elif not (dest / ".git").is_dir():
        raise RuntimeError(f"{dest.name} in the cache is not a git clone: left as it is")
    else:
        origin = _git("remote", "get-url", "origin", cwd=dest)
        if not _same_remote(origin, url):
            raise RuntimeError(f"{dest.name} in the cache is a clone of {origin}, "
                               f"not of {repo}: left as it is")
        if update:
            if not (dest / ".git" / OWNED).is_file():
                raise RuntimeError(f"{dest.name} in the cache was not cloned by the audit, "
                                   "so it is not reset: left as it is (--no-fetch measures it)")
            _git("fetch", "--depth", "1", "--no-tags", "origin", "HEAD", cwd=dest)
            _git("reset", "--hard", "-q", "FETCH_HEAD", cwd=dest)
    commit = _git("rev-parse", "HEAD", cwd=dest)
    date = _git("log", "-1", "--format=%cI", cwd=dest)
    return dest, commit, date


def _clone(repo: str, url: str, dest: Path) -> None:
    """A fresh clone at ``dest``, made in a staging folder and moved in whole."""
    import tempfile

    dest.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f"{dest.name}{PARTIAL}-", dir=dest.parent))
    try:
        _mark(staging, repo)
        clone = staging / "clone"
        _git("clone", "--depth", "1", "--no-tags", "--single-branch", "-q", url, str(clone))
        _mark(clone / ".git", repo)
        try:
            clone.rename(dest)
        except OSError:
            # Another audit sharing the cache finished this clone first:
            # its clone is as good as ours, if it is the audit's.
            if not (dest / ".git" / OWNED).is_file():
                raise RuntimeError(f"{dest.name} appeared in the cache while cloning, "
                                   "and not from the audit: left as it is") from None
    finally:
        _remove(staging)


# -------------------------------------------------------------------- packages

def _walk(base: Path):
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            yield Path(dirpath) / name


def index_packages(bases: dict[str, Path]) -> list[tuple[str, str, str]]:
    """(package name, its directory, the repository it is in) for every package.xml."""
    found = []
    for owner, base in bases.items():
        for path in _walk(base):
            if path.name != "package.xml":
                continue
            try:
                name = ET.parse(path).getroot().findtext("name")
            except (ET.ParseError, OSError):
                continue
            if name and name.strip():
                found.append((name.strip(), str(path.parent), owner))
    return found


def package_map(packages: list[tuple[str, str, str]], owner: str) -> dict[str, str]:
    """Each package's directory: the robot's own repository's copy if it has
    one, else the first found elsewhere."""
    mapping: dict[str, str] = {}
    for name, where, _repo in packages:
        mapping.setdefault(name, where)
    for name, where, repo in packages:
        if repo == owner:
            mapping[name] = where
    return mapping


def package_copies(packages: list[tuple[str, str, str]], owner: str) -> dict[str, list[str]]:
    """Every copy of each package found twice or more, the robot's own first.

    xacro gets one copy (``package_map``), but a mesh is looked for in each:
    two repositories vendoring one package rarely vendor the same meshes, and
    which is found first is only the order they sort in.
    """
    copies: dict[str, list[str]] = {}
    for name, where, repo in sorted(packages, key=lambda p: p[2] != owner):
        copies.setdefault(name, []).append(where)
    return {name: dirs for name, dirs in copies.items() if len(dirs) > 1}


# ---------------------------------------------------------------------- robots

_DEFINES = {"macro", "property", "include", "arg"}


def _local(tag: str) -> tuple[str | None, str]:
    if tag.startswith("{"):
        namespace, _, name = tag[1:].partition("}")
        return namespace, name
    if ":" in tag:
        prefix, _, name = tag.partition(":")
        return prefix, name
    return None, tag


def robot_kind(path: Path) -> str | None:
    """'urdf', 'xacro' or 'mjcf' when the file is a robot of its own, else None."""
    name = path.name.lower()
    if not name.endswith((".urdf", ".xacro", ".xml")):
        return None
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError, ValueError):
        return None
    if name.endswith(".xml"):
        if root.tag != "mujoco":
            return None
        world = root.find("worldbody")
        return "mjcf" if world is not None and world.find(".//body") is not None else None
    if _local(root.tag)[1] != "robot":
        return None
    if name.endswith(".urdf"):
        return "urdf" if root.find("link") is not None else None
    for child in root:
        if not isinstance(child.tag, str):
            continue                          # a comment
        namespace, tag = _local(child.tag)
        # The xacro namespace is spelt several ways (ros.org, www.ros.org, wiki.ros.org).
        is_xacro = namespace is not None and "xacro" in namespace
        if not is_xacro or tag not in _DEFINES:
            return "xacro"                    # a link, a joint, or a macro called
    return None


def find_robots(base: Path) -> list[tuple[Path, str]]:
    return [(path, kind) for path in _walk(base) if (kind := robot_kind(path))]


# ---------------------------------------------------------------------- meshes

def mesh_facts(path: Path) -> dict:
    """What a mesh file carries: triangles, bytes, authored normals, materials.

    Read from the file's own structure, no mesh library: fast enough for every
    mesh of every candidate. Polygons in a DAE count as one triangle each, so
    its count is a floor. A file is streamed, or only its header read, never
    held whole: several workers measure at once, and a candidate's mesh can
    be any size. ``bytes`` is what drawing it downloads: a ``.gltf`` with the
    buffers it names.
    """
    facts = {"format": path.suffix.lower().lstrip("."), "bytes": 0, "triangles": None,
             "normals": None, "materials": None, "error": None}
    try:
        facts["bytes"] = path.stat().st_size
        with open(path, "rb") as handle:
            if handle.read(len(_LFS)) == _LFS:
                facts["error"] = "in Git LFS, not fetched"
                return facts
            handle.seek(0)
            reader = _READERS.get(facts["format"])
            if reader:
                facts.update(reader(handle, path, facts["bytes"]))
    except OSError as exc:
        facts["error"] = f"cannot read: {exc.strerror or exc}"
    return facts


_CHUNK = 1 << 20


def _count(handle, needle: bytes) -> int:
    """Occurrences of ``needle`` in the rest of ``handle``, a chunk at a time."""
    count, tail = 0, b""
    while block := handle.read(_CHUNK):
        data = tail + block
        count += data.count(needle)
        # Shorter than the needle, so never a match counted twice.
        tail = data[-(len(needle) - 1):]
    return count


def _stl(handle, _path, size) -> dict:
    head = handle.read(2048)
    facts = {"normals": False, "materials": False}
    if head[:5].lower() == b"solid" and b"facet" in head:
        handle.seek(0)
        facts["triangles"] = _count(handle, b"facet normal")
    elif len(head) < 84:
        facts["error"] = "not a readable STL: too short for a header"
    else:
        count = int.from_bytes(head[80:84], "little")
        # Trailing bytes are common and harmless; fewer than the count says are not.
        if size < 84 + 50 * count:
            facts["error"] = f"not a readable STL: {count} triangles promised, fewer there"
        else:
            facts["triangles"] = count
    return facts


def _obj(handle, _path, _size) -> dict:
    triangles = 0
    normals = materials = False
    for line in handle:
        if line.startswith(b"f "):
            triangles += max(len(line.split()) - 3, 1)
        elif line.startswith(b"vn "):
            normals = True
        elif line.startswith((b"usemtl", b"mtllib")):
            materials = True
    return {"triangles": triangles, "normals": normals, "materials": materials}


_DAE_COUNT = re.compile(rb"<(?:triangles|polylist|polygons)\b[^>]*\bcount=\"(\d+)\"")


def _dae(handle, _path, _size) -> dict:
    triangles, normals, materials, carry = 0, False, False, b""
    while True:
        block = handle.read(_CHUNK)
        data = carry + block
        carry = b""
        if block:
            # Everything matched is inside one tag: hold back a tag still open.
            opened, closed = data.rfind(b"<"), data.rfind(b">")
            if opened > closed:
                data, carry = data[:opened], data[opened:]
        triangles += sum(int(c) for c in _DAE_COUNT.findall(data))
        normals = normals or b'semantic="NORMAL"' in data
        materials = materials or re.search(rb"<material\b", data) is not None
        if not block:
            break
    return {"triangles": triangles, "normals": normals, "materials": materials}


def _ply(handle, _path, _size) -> dict:
    header = handle.read(1 << 16).split(b"end_header", 1)[0].decode("ascii", "replace")
    faces = re.search(r"element face (\d+)", header)
    return {"triangles": int(faces.group(1)) if faces else None,
            "normals": " nx" in header,
            "materials": bool(re.search(r"property \w+ (red|diffuse_red)", header))}


def _glb(handle, path, size) -> dict:
    head = handle.read(20)
    length = int.from_bytes(head[12:16], "little")
    return _gltf_facts(handle.read(length), path, size)


def _gltf(handle, path, size) -> dict:
    return _gltf_facts(handle.read(), path, size)


def _buffer_problem(where: Path, uri: str, declared) -> tuple[int, str | None]:
    """A named buffer's size, and what is wrong with it if anything is."""
    try:
        size = where.stat().st_size
        with open(where, "rb") as handle:
            lfs = handle.read(len(_LFS)) == _LFS
    except OSError:
        return 0, f"its buffer {uri} cannot be read"
    if lfs:
        return size, f"its buffer {uri} is in Git LFS, not fetched"
    if isinstance(declared, int) and size < declared:
        return size, f"its buffer {uri} has {size} of the {declared} bytes it declares"
    return size, None


def _gltf_facts(data: bytes, path: Path, _size: int) -> dict:
    try:
        document = json.loads(data)
    except ValueError:
        return {"error": "not a readable glTF"}
    accessors = document.get("accessors", [])
    triangles, normals = 0, True
    for mesh in document.get("meshes", []):
        for primitive in mesh.get("primitives", []):
            mode = primitive.get("mode", 4)
            if mode not in (4, 5, 6):
                continue                      # points and lines draw no faces
            normals &= "NORMAL" in primitive.get("attributes", {})
            index = primitive.get("indices")
            source = index if index is not None else primitive.get("attributes", {}).get(
                "POSITION")
            if isinstance(source, int) and source < len(accessors):
                count = accessors[source].get("count", 0)
                # A list of triangles, or a strip or fan of them.
                triangles += count // 3 if mode == 4 else max(count - 2, 0)
    facts = {"triangles": triangles, "normals": normals,
             "materials": bool(document.get("materials"))}
    # A .gltf keeps its geometry in the buffers it names, beside it (a .glb may
    # too): they weigh what they hold, and one left in Git LFS, or shorter
    # than it says, makes the mesh unreadable.
    from urllib.parse import unquote

    # Kept by path, apart from the file's own bytes: two meshes naming one
    # buffer download it once, and the robot's total counts it once.
    buffers: dict[str, int] = {}
    for buffer in document.get("buffers", []):
        uri = buffer.get("uri")
        if isinstance(uri, str) and not uri.startswith("data:"):
            where = path.parent / unquote(uri)
            extra, problem = _buffer_problem(where, uri, buffer.get("byteLength"))
            buffers[os.path.normcase(os.path.abspath(where))] = extra
            facts["error"] = facts.get("error") or problem
    if buffers:
        facts["buffers"] = buffers
    if facts.get("error") is None:
        facts.pop("error", None)
    return facts


_READERS = {"stl": _stl, "obj": _obj, "dae": _dae, "ply": _ply, "glb": _glb, "gltf": _gltf}


# --------------------------------------------------------------- measurement

def _resolve(filename: str, source: Path, mapping: dict[str, str],
             mesh_base: Path | None, copies: dict[str, list[str]] | None = None
             ) -> Path | None:
    from meshkit.scan import strip_file_uri

    text = filename.strip()
    if text.startswith("file://"):
        text = strip_file_uri(text)
        if re.match(r"^/[A-Za-z]:", text):
            text = text[1:]
    if text.startswith("package://"):
        package, _, rest = text[len("package://"):].partition("/")
        places = (copies or {}).get(package) or ([mapping[package]] if package in mapping
                                                 else [])
        found = [Path(where) / rest for where in places]
        return next((p for p in found if p.is_file()), found[0] if found else None)
    path = Path(text)
    if path.is_absolute():
        return path
    return (mesh_base or source.parent) / text


def _share(part: int, whole: int) -> float | None:
    return round(part / whole, 3) if whole else None


def measure_urdf(text: str, source: Path, mapping: dict[str, str], *,
                 mesh_base: Path | None = None, facts: dict | None = None,
                 copies: dict[str, list[str]] | None = None) -> dict:
    """What a URDF (xacro already evaluated) says about itself."""
    root = ET.fromstring(text)
    if _local(root.tag)[1] != "robot":
        raise ValueError(f"the root is <{root.tag}>, not <robot>")
    links = root.findall("link")
    joints = root.findall("joint")
    moving = [j for j in joints if j.get("type") in ("revolute", "prismatic", "continuous")]

    def limited(joint) -> bool:
        if joint.get("type") == "continuous":
            return True
        limit = joint.find("limit")
        try:
            return limit is not None and float(limit.get("upper")) > float(limit.get("lower"))
        except (TypeError, ValueError):
            return False

    def has_velocity(joint) -> bool:
        limit = joint.find("limit")
        try:
            return limit is not None and float(limit.get("velocity", "0")) > 0
        except ValueError:
            return False

    bodies = [link for link in links
              if link.find("visual") is not None or link.find("collision") is not None]

    def has_mass(link) -> bool:
        mass = link.find("inertial/mass")
        try:
            return mass is not None and float(mass.get("value", "0")) > 0
        except ValueError:
            return False

    coloured = {m.get("name") for m in root.findall("material")
                if m.find("color") is not None or m.find("texture") is not None}
    visuals = []
    for link in links:
        for visual in link.findall("visual"):
            material = visual.find("material")
            colour = material is not None and (
                material.find("color") is not None or material.find("texture") is not None
                or material.get("name") in coloured)
            mesh = visual.find("geometry/mesh")
            path = None
            if mesh is not None and mesh.get("filename"):
                path = _resolve(mesh.get("filename"), source, mapping, mesh_base, copies)
                visuals.append({"mesh": str(path) if path else mesh.get("filename"),
                                "found": bool(path and path.is_file()), "colour": colour})
            else:
                visuals.append({"mesh": None, "found": True, "colour": colour})
    # URDF asks a <limit> of revolute and prismatic joints only: a wheel's
    # continuous joint needs no velocity limit to be complete.
    bounded = [j for j in moving if j.get("type") != "continuous"]
    summary = _summarise(root.get("name"), len(links), len(moving),
                         sum(map(limited, moving)), sum(map(has_velocity, bounded)),
                         len(bodies), sum(map(has_mass, bodies)), visuals, facts)
    summary["velocity_share"] = _share(sum(map(has_velocity, bounded)), len(bounded))
    return summary


def _mjcf_tree(path: Path, seen: set[Path] | None = None, main: Path | None = None
               ) -> ET.Element:
    """The model with every <include> put in place, the way MuJoCo reads it.

    An include MuJoCo would refuse (a file that is not there, or one already
    included) is an error here too: the model left without it is not the
    robot, and must not be scored as one.
    """
    seen = set() if seen is None else seen
    main = main or path.parent
    root = ET.parse(path).getroot()
    seen.add(path.resolve())

    def expand(element: ET.Element) -> None:
        for index, child in reversed(list(enumerate(element))):
            if child.tag == "include" and child.get("file"):
                name = child.get("file")
                # Beside the including file, or beside the model MuJoCo was given.
                target = next((p.resolve() for p in (path.parent / name, main / name)
                               if p.is_file()), None)
                if target is None:
                    raise FileNotFoundError(f"included file {name} is not there")
                if target in seen:
                    raise ValueError(f"{name} is included twice")
                element.remove(child)
                included = _mjcf_tree(target, seen, main)
                for offset, grandchild in enumerate(list(included)):
                    element.insert(index + offset, grandchild)
            else:
                expand(child)

    expand(root)
    return root


_CLASSED = ("joint", "geom")


def _mjcf_defaults(root: ET.Element) -> dict[str, dict[str, dict]]:
    """Each default class's joint and geom attributes, inherited down the tree."""
    classes: dict[str, dict[str, dict]] = {"main": {tag: {} for tag in _CLASSED}}

    def visit(default: ET.Element, inherited: dict[str, dict], name: str) -> None:
        own = classes.get(name) if name == "main" else None
        own = own or {tag: dict(inherited[tag]) for tag in _CLASSED}
        for child in default:
            if child.tag in own:
                own[child.tag].update(child.attrib)
        classes[name] = own
        for child in default:
            if child.tag == "default":
                visit(child, own, child.get("class", "main"))

    for default in root.findall("default"):
        visit(default, classes["main"], "main")
    return classes


def _mjcf_elements(world: ET.Element, classes: dict[str, dict[str, dict]]
                   ) -> list[tuple[str, dict]]:
    """Every joint and geom under ``world``, with its default class applied.

    An element's class is its own ``class``, else the nearest ``childclass``
    above it, else ``main``.
    """
    found: list[tuple[str, dict]] = []

    def walk(element: ET.Element, childclass: str) -> None:
        for child in element:
            if child.tag in _CLASSED:
                defaults = classes.get(child.get("class") or childclass, classes["main"])
                found.append((child.tag, defaults[child.tag] | dict(child.attrib)))
            elif isinstance(child.tag, str):
                walk(child, child.get("childclass") or childclass)

    walk(world, "main")
    return found


def measure_mjcf(path: Path, *, facts: dict | None = None) -> dict:
    root = _mjcf_tree(path)
    compiler = root.find("compiler")
    meshdir = path.parent
    if compiler is not None:
        meshdir = path.parent / (compiler.get("meshdir") or compiler.get("assetdir") or "")
    meshes: dict[str, Path | None] = {}
    for mesh in root.iter("mesh"):
        if mesh.get("file"):
            name = mesh.get("name") or Path(mesh.get("file")).stem
            meshes[name] = meshdir / mesh.get("file")
        elif mesh.get("name"):
            meshes[mesh.get("name")] = None   # its vertices written in the model itself
    # MuJoCo merges every <worldbody>: an included file brings its own.
    worlds = list(root.iter("worldbody"))
    bodies = [b for world in worlds for b in world.iter("body")]
    classes = _mjcf_defaults(root)
    elements = [e for world in worlds for e in _mjcf_elements(world, classes)]
    joints = [a for tag, a in elements
              if tag == "joint" and a.get("type", "hinge") in ("hinge", "slide")]
    limited = sum(1 for j in joints if j.get("range") and j.get("limited") != "false")
    # Asked of a mass: a body with geometry, as of a URDF link, and a body that
    # moves, which MuJoCo refuses without one. A bare frame is asked nothing.
    # MuJoCo gives a body without <inertial> the inertia of its geoms, unless
    # the compiler says not to.
    from_geoms = compiler is None or compiler.get("inertiafromgeom", "auto") != "false"
    weighed = [b for b in bodies if b.find("geom") is not None or b.find("joint") is not None
               or b.find("freejoint") is not None]
    massed = sum(1 for b in weighed if b.find("inertial") is not None
                 or (from_geoms and b.find("geom") is not None))
    visuals = []
    for geom in (a for tag, a in elements if tag == "geom"):
        colour = bool(geom.get("material") or geom.get("rgba"))
        if (geom.get("type") == "mesh" or geom.get("mesh")) and (
                geom.get("mesh") not in meshes or meshes[geom.get("mesh")] is not None):
            target = meshes.get(geom.get("mesh"))
            visuals.append({"mesh": str(target) if target else geom.get("mesh"),
                            "found": bool(target and target.is_file()), "colour": colour})
        else:
            visuals.append({"mesh": None, "found": True, "colour": colour})
    # MJCF has no velocity limits: that half of the score is not asked of it.
    return _summarise(root.get("model"), len(bodies), len(joints), limited, None,
                      len(weighed), massed, visuals, facts)


def _summarise(name, links, moving, limited, velocity, bodies, massed, visuals, facts) -> dict:
    facts = facts if facts is not None else {}
    files: dict[str, dict] = {}
    missing = []
    for visual in visuals:
        if visual["mesh"] is None:
            continue
        if not visual["found"]:
            missing.append(visual["mesh"])
            continue
        if visual["mesh"] not in files:
            files[visual["mesh"]] = facts.get(visual["mesh"]) or mesh_facts(Path(visual["mesh"]))
            facts[visual["mesh"]] = files[visual["mesh"]]
    meshed = [v for v in visuals if v["mesh"] and v["found"]]
    readable = [v for v in meshed if files[v["mesh"]]["error"] is None]
    normals = sum(1 for v in readable if files[v["mesh"]]["normals"])
    # A mesh's own materials are worth a whole point; a whole-part colour in
    # the description, half.
    material_points = sum(1.0 if v["mesh"] and v["found"] and files[v["mesh"]]["materials"]
                          else 0.5 if v["colour"] else 0.0 for v in visuals)
    formats: dict[str, int] = {}
    for fact in files.values():
        formats[fact["format"]] = formats.get(fact["format"], 0) + 1
    return {
        "name": name,
        "links": links,
        "moving_joints": moving,
        "limited_share": _share(limited, moving),
        "velocity_share": None if velocity is None else _share(velocity, moving),
        "inertia_share": _share(massed, bodies),
        "visuals": len(visuals),
        "mesh_visuals": len(meshed) + len(missing),
        "missing_meshes": sorted(set(missing))[:20],
        "missing_count": len(set(missing)),
        "unreadable_meshes": sum(1 for f in files.values() if f["error"]),
        "unreadable_reasons": sorted({f["error"] for f in files.values() if f["error"]})[:5],
        "formats": formats,
        "normals_share": _share(normals, len(readable)),
        "materials_share": round(material_points / len(visuals), 3) if visuals else None,
        # Drawn per visual: a mesh used by twelve links is drawn twelve times.
        # Downloaded per file: it is fetched once.
        "triangles": sum(files[v["mesh"]]["triangles"] or 0 for v in meshed),
        "megabytes": round((sum(f["bytes"] for f in files.values()) + sum(
            {p: n for f in files.values() for p, n in f.get("buffers", {}).items()}.values()))
            / 1e6, 2),
    }


def measure(path: Path, kind: str, mapping: dict[str, str], *, args: dict | None = None,
            mesh_base: Path | None = None, facts: dict | None = None,
            copies: dict[str, list[str]] | None = None) -> dict:
    """One robot: its measurements, or why it could not be measured."""
    from meshkit.scan import render_xacro

    try:
        if kind == "mjcf":
            result = measure_mjcf(path, facts=facts)
        else:
            text = (render_xacro(path, args or {}, mapping) if kind == "xacro"
                    else path.read_text(encoding="utf-8", errors="replace"))
            result = measure_urdf(text, path, mapping, mesh_base=mesh_base, facts=facts,
                                  copies=copies)
    except Exception as exc:  # noqa: BLE001 - one robot must not stop the audit
        message = " ".join(str(exc).split())[:300]
        return {"flattened": False, "error": f"{type(exc).__name__}: {message}"}
    # A mesh that is there but cannot be read (left in Git LFS, a glTF without
    # its buffer) is as unmeasured as one that is not there: its triangles,
    # normals and size are unknown, so it earns nothing.
    result["flattened"] = (result["links"] > 0 and result["missing_count"] == 0
                           and result["unreadable_meshes"] == 0)
    result["error"] = (
        None if result["flattened"] else
        "renders no links with its default arguments" if not result["links"] else
        f"{result['missing_count']} visual mesh file(s) missing" if result["missing_count"] else
        f"{result['unreadable_meshes']} visual mesh file(s) unreadable: "
        + "; ".join(result["unreadable_reasons"]))
    return result


# ---------------------------------------------------------------------- score

def _taper(value: float, good: float, bad: float) -> float:
    if value <= good:
        return 1.0
    if value >= bad:
        return 0.0
    return (bad - value) / (bad - good)


def score(row: dict, *, today: datetime | None = None) -> tuple[int, dict]:
    """The robot's score out of 100, and each part of it."""
    today = today or datetime.now(timezone.utc)
    parts = {name: 0.0 for name in WEIGHTS}
    named = row.get("licence") not in UNNAMED
    parts["licence"] = WEIGHTS["licence"] * (1.0 if named and row.get("licence_file")
                                             else 0.5 if named or row.get("licence_file")
                                             else 0.0)
    pushed = row.get("last_commit")
    if pushed and not row.get("archived"):
        days = (today - datetime.fromisoformat(pushed.replace("Z", "+00:00"))).days
        parts["alive"] = WEIGHTS["alive"] * (1.0 if days <= 365 else 0.5 if days <= 3 * 365
                                             else 0.0)
    if row.get("flattened"):
        parts["flattens"] = WEIGHTS["flattens"]
        limited = row.get("limited_share")
        velocity = row.get("velocity_share")
        if limited is not None:
            shares = [limited] if velocity is None else [limited, velocity]
            parts["limits"] = WEIGHTS["limits"] * sum(shares) / len(shares)
        elif row.get("moving_joints") == 0:
            parts["limits"] = WEIGHTS["limits"]          # nothing moves: nothing to limit
        if row.get("inertia_share") is not None:
            parts["inertia"] = WEIGHTS["inertia"] * row["inertia_share"]
        look = [(row.get("normals_share") or 0.0), (row.get("materials_share") or 0.0)]
        parts["look"] = WEIGHTS["look"] * sum(look) / 2
        if row.get("visuals"):
            parts["weight"] = WEIGHTS["weight"] * min(
                _taper(row.get("triangles") or 0, *TRIANGLES),
                _taper(row.get("megabytes") or 0, *MEGABYTES))
    parts = {name: round(value, 1) for name, value in parts.items()}
    return round(sum(parts.values())), parts


# --------------------------------------------------------------------- worker

def _is_licence(path: Path) -> bool:
    """LICENSE, LICENCE.md, COPYING, LICENSE-APACHE, LICENSE_MIT.txt..., or a
    REUSE-style LICENSES/ folder with a text in it (FANUC's). A dotfile such
    as .gitkeep is no text."""
    if path.is_dir():
        return path.name.lower() in ("licenses", "licences") and any(
            p.is_file() and not p.name.startswith(".") for p in path.iterdir())
    stem = path.name.lower().split(".")[0]
    return path.is_file() and any(stem == word or stem.startswith((word + "-", word + "_"))
                                  for word in LICENCE_FILES)


def licence_file(base: Path, up_to: Path) -> bool:
    """A licence text beside the robot or in a folder above it (``_is_licence``)."""
    here = base if base.is_dir() else base.parent
    while True:
        try:
            if any(_is_licence(p) for p in here.iterdir()):
                return True
        except OSError:
            return False
        if here == up_to or here.parent == here or not here.is_relative_to(up_to):
            return False
        here = here.parent


def _manifest(path: Path, up_to: Path) -> tuple[Path, ET.Element | None] | None:
    """The nearest package.xml above a robot file: its folder, and its root
    element (None when it does not parse). None when there is no package.xml."""
    here = path.parent
    while here.is_relative_to(up_to):
        manifest = here / "package.xml"
        if manifest.is_file():
            try:
                return here, ET.parse(manifest).getroot()
            except (ET.ParseError, OSError):
                return here, None
        if here == up_to or here.parent == here:
            break
        here = here.parent
    return None


def package_of(path: Path, up_to: Path) -> str | None:
    """The ROS package a robot file belongs to: the nearest package.xml above it.

    A package's variants (robot.xacro, ros2_control/robot.xacro, a URDF
    generated from them) are one robot as far as forking goes.
    """
    found = _manifest(path, up_to)
    if found is None:
        return None
    here, root = found
    name = root.findtext("name") if root is not None else None
    return (name or here.name).strip()


def package_licence(path: Path, up_to: Path) -> str | None:
    """The licence the robot's package.xml declares, or None.

    For a repository GitHub cannot name a licence for (Yaskawa states it
    per package, FANUC in a LICENSES/ folder GitHub does not read). Several
    <license> tags, which ROS uses when parts are licensed differently, are
    kept as they are written, joined with " AND ". A placeholder is not a
    licence.
    """
    found = _manifest(path, up_to)
    if found is None or found[1] is None:
        return None
    # Free text from someone else's file: one line, and not a page of it.
    named = [" ".join((tag.text or "").split())[:100] for tag in found[1].findall("license")]
    named = [n for n in named if n.upper() not in UNNAMED and n.lower() not in PLACEHOLDERS]
    # Whole names only: cutting the joined text mid-name turns "MPL-2.0" into
    # "AN", a licence nobody wrote. Past a handful, say how many were left out.
    named = list(dict.fromkeys(named))
    kept, extra = named[:LICENCE_TAGS], len(named) - LICENCE_TAGS
    return (" AND ".join(kept) + (f" (and {extra} more)" if extra > 0 else "")) or None


def audit_repo(spec: dict) -> dict:
    """Every robot in one repository. Runs in a subprocess; ``spec`` is JSON."""
    base = Path(spec["dir"])
    scope = base / spec.get("folder", "") if spec.get("folder") else base
    mapping = {name: where for name, where in spec["packages"].items()}
    facts: dict = {}
    rows = []
    if spec.get("entries"):
        # A catalog entry's path is from the repository root: some are
        # wrappers kept beside the forks, under descriptions/.
        robots = [(Path(spec["root"]) / e["entry"], e["format"], e) for e in spec["entries"]]
    else:
        robots = [(path, kind, None) for path, kind in find_robots(scope)]
    for path, kind, entry in robots:
        result = measure(path, kind, mapping,
                         args=(entry or {}).get("args"),
                         mesh_base=(Path(spec["root"]) / entry["mesh_base"]
                                    if entry and entry.get("mesh_base") else None),
                         facts=facts, copies=spec.get("copies"))
        relative =path.relative_to(spec["path_base"]).as_posix() if spec.get(
            "path_base") else path.relative_to(base).as_posix()
        # A wrapper under descriptions/ describes its fork's robot: the fork's
        # LICENSE is the one that covers it.
        result.update(path=relative, kind=kind, id=(entry or {}).get("id"),
                      package=package_of(path, base),
                      licence_file=licence_file(path, base) or licence_file(base, base),
                      package_licence=package_licence(path, base))
        rows.append(result)
    sdf = sum(1 for p in _walk(scope) if p.suffix.lower() == ".sdf")
    places = [(base, ""), (Path(spec["root"]), "")] + [(Path(p), label) for p, label in
                                                        spec.get("scrub", [])]
    for row in rows:
        if row.get("error"):
            row["error"] = scrub(row["error"], places)
        if row.get("missing_meshes"):
            row["missing_meshes"] = [scrub(m, places).replace("\\", "/")
                                     for m in row["missing_meshes"]]
    return {"robots": rows, "sdf_files": sdf}


def scrub(text: str, places: list[tuple[Path, str]]) -> str:
    """``text`` with each place's path replaced by its label.

    What the audit writes is committed: a path on this machine (the user's
    name in it, the cache's location) has no business there. A path inside
    the repository audited becomes relative to it.
    """
    for place, label in places:
        # The path as given, and as the system resolves it: Windows can redirect
        # a folder, and an error then names where the file really is.
        real = Path(os.path.realpath(place))
        for form in dict.fromkeys((str(place), place.as_posix(), str(real), real.as_posix())):
            for separator in ("\\", "/"):
                text = text.replace(form + separator, label + ("/" if label else ""))
            text = text.replace(form, label or ".")
    return text


def _worker() -> int:
    import contextlib

    spec = json.load(sys.stdin)
    out = sys.stdout
    # xacro prints its warnings: they go to stderr, so stdout stays one JSON document.
    with contextlib.redirect_stdout(sys.stderr):
        result = audit_repo(spec)
    json.dump(result, out)
    return 0


# ------------------------------------------------------------------------ run

@dataclass
class RepoReport:
    key: str
    repo: str
    folder: str
    sources: list[str]
    fork: str | None
    licence: str | None
    archived: bool
    commit: str | None = None
    last_commit: str | None = None
    sdf_files: int = 0
    error: str | None = None
    robots: list[dict] = field(default_factory=list)

    @property
    def best(self) -> int | None:
        return max((r["score"] for r in self.robots), default=None)


@dataclass
class Audit:
    generated: str
    weights: dict
    repos: list[RepoReport]
    # What --only and --repo named, when the audit is not of everything.
    selection: list[str] | None = None
    # Candidate lists a named audit could not read (a full audit stops instead).
    unavailable: list[str] | None = None

    def as_json(self) -> dict:
        return {"generated": self.generated, "weights": self.weights,
                "selection": self.selection, "unavailable_lists": self.unavailable,
                "thresholds": {"triangles": TRIANGLES, "megabytes": MEGABYTES},
                "not_measured": ["imports in Kinema",
                                 "kinematics against the maker's own description"],
                "repos": [asdict(r) | {"best": r.best} for r in self.repos]}


def _run_worker(spec: dict, timeout: int) -> dict:
    done = subprocess.run([sys.executable, "-m", "meshkit.audit", "--worker"],
                          input=json.dumps(spec), capture_output=True, text=True,
                          timeout=timeout, check=False, encoding="utf-8")
    if done.returncode:
        tail = (done.stderr or "").strip().splitlines()[-1:] or ["no output"]
        raise RuntimeError(f"the measuring process failed: {tail[0][:300]}")
    return json.loads(done.stdout)


def dependency_bases(everyone: list[Candidate], candidates: list[Candidate],
                     places: dict[str, Path], root: Path, cache: Path) -> list[Path]:
    """Where packages come from: what is measured, plus every other fork and
    clone already on disk, read as it is (nothing is fetched or reset).

    A GitHub error about one of the others does not leave it out: it stops
    that repository being measured, not its clone being read. In a fixed
    order, so a package found in two repositories comes from the same one
    every run.
    """
    bases = set(places.values())
    for other in everyone:
        if other in candidates:
            continue
        where = root / "src" / other.fork if other.fork else cache_dir(cache, other.repo)
        if (where / ".git").exists():
            bases.add(where)
    return sorted(bases, key=str)


def run(root: Path, github, cache: Path, *, lists: bool = True, only: list[str] | None = None,
        repos: list[str] | None = None, update: bool = True, workers: int = 4,
        timeout: int = REPO_TIMEOUT, progress=print) -> Audit:
    from meshkit.catalog import load as load_catalog

    # Absolute: xacro is evaluated from the robot's own folder, where a path
    # relative to here would point somewhere else.
    root, cache = root.absolute(), cache.absolute()
    unavailable: list[str] = []
    everyone = gather(root, github, lists=lists, repos=repos, unavailable=unavailable)
    for note in unavailable:
        progress(f"  not read, so its candidates supply no packages: {note}")
    candidates = select(everyone, only, named=bool(repos))
    entries: dict[str, list[dict]] = {}
    for entry in load_catalog(root):
        entries.setdefault(entry["submodule"], []).append(entry)

    # Paths on this machine, as the committed report names them.
    outside = [(root, ""), (cache, "<cache>"), (Path.home(), "~")]
    reports = {c.key: RepoReport(c.key, c.repo, c.folder, c.sources, c.fork, c.licence,
                                 c.archived, error=c.error) for c in candidates}
    places: dict[str, Path] = {}

    def place(candidate: Candidate) -> None:
        report = reports[candidate.key]
        if candidate.fork:
            where = root / "src" / candidate.fork
            if not where.is_dir() or not any(where.iterdir()):
                report.error = "the submodule is not checked out"
                return
            places[candidate.key] = where
            report.commit = _git("rev-parse", "HEAD", cwd=where)
            report.last_commit = candidate.pushed
            return
        if report.error:
            return
        try:
            where, commit, date = fetch(candidate.repo, cache, update=update)
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            report.error = scrub(f"clone failed: {exc}", outside)
            return
        places[candidate.key] = where
        report.commit, report.last_commit = commit, date

    # One clone per repository, however many of its folders are candidates.
    by_repo: dict[str, list[Candidate]] = {}
    for candidate in candidates:
        by_repo.setdefault(candidate.repo.lower(), []).append(candidate)

    def place_repo(group: list[Candidate]) -> None:
        place(group[0])
        for other in group[1:]:
            source = reports[group[0].key]
            if group[0].key in places:
                places[other.key] = places[group[0].key]
                reports[other.key].commit = source.commit
                reports[other.key].last_commit = source.last_commit
            else:
                reports[other.key].error = source.error

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for done, _ in enumerate(pool.map(place_repo, by_repo.values()), 1):
            if done % 20 == 0:
                progress(f"  {done} of {len(by_repo)} repositories in place")

    # Packages from every repository audited, so a candidate that depends on
    # another's description (a gripper on an arm) can still flatten. Each
    # clone is indexed once, however many folders of it are candidates.
    # --only narrows what is measured, not what can be depended on: the other
    # forks, and the clones already in the cache, are indexed as they are.
    bases = dependency_bases(everyone, candidates, places, root, cache)
    packages = index_packages({str(where): where for where in bases})
    progress(f"{len(bases)} repositories in place, {len(packages)} ROS packages found")

    def measure_one(candidate: Candidate) -> None:
        report = reports[candidate.key]
        where = places.get(candidate.key)
        if where is None:
            return
        spec = {"dir": str(where), "folder": candidate.folder, "root": str(root),
                "packages": package_map(packages, str(where)),
                "copies": package_copies(packages, str(where)),
                "entries": entries.get(candidate.fork, []) if candidate.fork else None,
                "path_base": str(root) if candidate.fork else None,
                "scrub": [(str(where), label) for where, label in outside]}
        try:
            result = _run_worker(spec, timeout)
        except subprocess.TimeoutExpired:
            report.error = f"measuring took over {timeout // 60} minutes"
            return
        except (RuntimeError, ValueError) as exc:
            report.error = scrub(str(exc), outside)
            return
        report.sdf_files = result["sdf_files"]
        for robot in result["robots"]:
            robot.update(licence=_robot_licence(candidate, robot, entries),
                         last_commit=report.last_commit, archived=report.archived)
            robot["score"], robot["parts"] = score(robot)
        report.robots = sorted(result["robots"], key=lambda r: (-r["score"], r["path"]))

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for done, _ in enumerate(pool.map(measure_one, candidates), 1):
            if done % 20 == 0:
                progress(f"  {done} of {len(candidates)} measured")

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    selection = [*(only or []), *(repo_name(r) for r in repos or [])] or None
    return Audit(generated, dict(WEIGHTS), [reports[c.key] for c in candidates], selection,
                 unavailable or None)


def _robot_licence(candidate: Candidate, robot: dict, entries: dict) -> str | None:
    """The catalog's own licence for its entries. For a candidate, GitHub's,
    or where GitHub names none, the one its package.xml declares."""
    if candidate.fork:
        for entry in entries.get(candidate.fork, []):
            if entry["id"] == robot.get("id"):
                return entry["licence"]
    if candidate.licence in UNNAMED and robot.get("package_licence"):
        return robot["package_licence"]
    return candidate.licence


# --------------------------------------------------------------------- report

def _cell(text: str) -> str:
    """Text from someone else's file (a package.xml licence), safe in a table cell."""
    from meshkit.upstream import _inert

    # Backslashes first: in a GFM table, "\\|" is a literal backslash, then a column bar.
    return _inert(" ".join(text.split())).replace("\\", "\\\\").replace("|", "\\|")


def render_markdown(audit: Audit, *, listed: int = 40, top_rows: int = 100,
                    json_link: str | None = "audit.json", json_name: str | None = None
                    ) -> str:
    """The audit as Markdown. ``json_link`` is the JSON's path from the
    Markdown's folder; None when there is none (another drive), and then the
    JSON is named, by ``json_name``, but not linked."""
    from urllib.parse import quote

    from meshkit.upstream import _code, _inert

    json_name = _inert(json_name or (json_link or "audit.json").rsplit("/", 1)[-1])
    json_ref = (f"[`{json_name}`]({quote(json_link)})" if json_link
                else f"`{json_name}`, written with this report,")
    forks = [r for r in audit.repos if r.fork]
    candidates = [r for r in audit.repos if not r.fork]
    measured = [r for r in candidates if r.robots]
    robots = [(r, robot) for r in measured for robot in r.robots]
    if audit.selection:
        named = ", ".join(_code(name) for name in audit.selection)
        scope = (f"Only what `--only` and `--repo` named ({named}), not the whole audit; "
                 "every robot in it measured the way the full audit measures them and "
                 "scored out of 100. ")
    else:
        scope = ("Every robot in the catalog's forks, and every robot in the repositories "
                 "the upstream report's lists name, measured the same way and scored out "
                 "of 100. ")
    # A selection with no fork in it has no catalog to show.
    catalog = bool(forks or not audit.selection)
    lines = [
        "# Robot description audit",
        "",
        f"Written by `meshkit audit` on {audit.generated}. {scope}"
        f"{json_ref} has every measurement.",
        "",
        *([f"- **The catalog:** {sum(len(r.robots) for r in forks)} entries in "
           f"{len(forks)} forks."] if catalog else []),
        f"- **Candidates:** {len(robots)} robots in {len(measured)} of {len(candidates)} "
        "repositories or folders; "
        f"{sum(1 for r in candidates if r.error)} could not be audited (listed at the end).",
        *([f"- **Lists not read:** {_inert('; '.join(audit.unavailable))}. Their candidates "
           "were not available as dependencies."] if audit.unavailable else []),
        "",
        "## How a robot is scored",
        "",
        "| Part | Points | Full marks when |",
        "|---|--:|---|",
        f"| Licence | {WEIGHTS['licence']} | A licence is named (by GitHub, else by the "
        "robot's package.xml) and there is a licence text: a LICENSE, LICENCE or COPYING "
        "file (LICENSE-MIT and the like too) or a LICENSES/ folder with a file in it "
        "(present, not read; half for one of the two) |",
        f"| Alive | {WEIGHTS['alive']} | Upstream committed to in the last year (half: in "
        "three); not archived |",
        f"| Flattens | {WEIGHTS['flattens']} | xacro evaluates (or the MJCF parses) and every "
        "visual mesh is there. Without it the parts below score nothing |",
        f"| Limits | {WEIGHTS['limits']} | Every moving joint has position and velocity limits "
        "(MJCF: position only) |",
        f"| Inertia | {WEIGHTS['inertia']} | Every link with geometry has a mass (MJCF: every "
        "body with geometry or a joint) |",
        f"| Look | {WEIGHTS['look']} | Half for meshes with authored normals, half for "
        "materials (a whole-part colour counts half) |",
        f"| Weight | {WEIGHTS['weight']} | Under {TRIANGLES[0]:,} triangles and "
        f"{MEGABYTES[0]} MB of visual meshes, none from {TRIANGLES[1]:,} or {MEGABYTES[1]} MB "
        "(triangles as drawn, once per visual; megabytes once per file) |",
        "",
        "Not measured: whether Kinema imports the robot, and whether its kinematics match "
        "the maker's own description. A xacro is evaluated with its default arguments, "
        "using packages from every repository audited; one that needs a package none of "
        "them carries does not flatten. A DAE's polygons count as one triangle each.",
    ]
    if catalog:
        lines += [
            "",
            "## The catalog's entries",
            "",
            "| Entry | Fork | Score | Licence | Limits | Inertia | Normals | Materials | "
            "Triangles | MB |",
            "|---|---|--:|---|--:|--:|--:|--:|--:|--:|",
        ]
    pct = lambda v: "-" if v is None else f"{round(v * 100)}%"  # noqa: E731
    for report in forks:
        for robot in sorted(report.robots, key=lambda r: (-r["score"], r.get("id") or "")):
            lines.append(
                f"| {robot.get('id')} | {report.fork} | {robot['score']} | "
                f"{_cell(robot.get('licence') or '-')} | {pct(robot.get('limited_share'))} | "
                f"{pct(robot.get('inertia_share'))} | {pct(robot.get('normals_share'))} | "
                f"{pct(robot.get('materials_share'))} | {robot.get('triangles') or 0:,} | "
                f"{robot.get('megabytes') or 0} |")
        if report.error:
            lines.append(f"| - | {report.fork} | - | {_inert(report.error)} | | | | | | |")

    # One row per package: its variants (a ros2_control wrapper, a generated
    # URDF) are the same robot. A file outside any package is its own row.
    groups: dict[tuple, list[tuple[RepoReport, dict]]] = {}
    for report, robot in robots:
        unit = robot.get("package") or robot["path"]
        groups.setdefault((report.key, unit), []).append((report, robot))
    # The row stands for the package's robot: its most complete file that
    # flattens, not a hand or an arm of it that happens to score as well.
    best = [max(group, key=_completeness) + (len(group),) for group in groups.values()]
    top = sorted(best, key=lambda t: (-t[1]["score"], t[0].repo.lower(), t[1]["path"]))
    top = top[:top_rows]
    lines += ["", f"## The {len(top)} best-scoring candidates", "",
              f"One row per ROS package: {len(groups)} packages (or files outside any) hold "
              f"the {len(robots)} candidate robots. Each row shows the package's most "
              "complete robot (the file with the most links among those that flatten) and "
              "how many robot files the package has; its components and other variants are "
              "in the repository's details below.", "",
              "| Score | Package | Robot | Links | Files | Repository | Licence | Formats | "
              "Triangles |",
              "|--:|---|---|--:|--:|---|---|---|--:|"]
    for report, robot, count in top:
        lines.append(f"| {robot['score']} | {_inert(robot.get('package') or '-')} | "
                     f"{_code(robot['path'])} | {robot.get('links') or 0} | {count} | "
                     f"{_repo_link(report)} | {_cell(robot.get('licence') or '-')} | "
                     f"{_formats(robot)} | {robot.get('triangles') or 0:,} |")

    lines += ["", "## Every candidate, by repository", "",
              "Best score first. Each repository lists its robots, best first.", ""]
    for report in sorted(measured, key=lambda r: (-(r.best or 0), r.repo.lower())):
        last = (report.last_commit or "")[:10] or "?"
        flags = " **archived**" if report.archived else ""
        lines += [f"<details><summary><b>{_inert(report.repo)}"
                  f"{('/' + _inert(report.folder)) if report.folder else ''}</b>: best "
                  f"{report.best}, {len(report.robots)} robot(s), "
                  f"{_inert(report.licence or 'no licence named')}, last commit {last}{flags}"
                  "</summary>", "",
                  f"From: {', '.join(report.sources)}. "
                  f"Commit `{(report.commit or '')[:12]}`."
                  + (f" Also {report.sdf_files} SDF file(s), not measured." if report.sdf_files
                     else ""), "",
                  f"| Score | Robot | Kind | {PARTS_HEADER} | Note |", "|--:|---|---|---|---|"]
        for robot in report.robots[:listed]:
            parts = " · ".join(f"{robot['parts'][k]:g}" for k in WEIGHTS)
            note = _inert(robot["error"]) if robot.get("error") else ""
            lines.append(f"| {robot['score']} | {_code(robot['path'])} | {robot['kind']} | "
                         f"{parts} | {note} |")
        if len(report.robots) > listed:
            lines.append(f"| | and {len(report.robots) - listed} more, in "
                         f"`{json_name}` | | | |")
        lines += ["", "</details>", ""]

    empty = [r for r in candidates if not r.robots and not r.error]
    failed = [r for r in audit.repos if r.error]
    if empty:
        lines += ["## Candidates with no robot file", "",
                  "Cloned, but holding no URDF, robot xacro or MJCF robot "
                  "(SDF, meshes only, or another layout).", ""]
        lines += [f"- {_repo_link(r)}" + (f": {r.sdf_files} SDF file(s)" if r.sdf_files else "")
                  for r in empty] + [""]
    if failed:
        lines += ["## Could not be audited", ""]
        lines += [f"- {_repo_link(r)}: {_inert(r.error)}" for r in failed] + [""]
    return "\n".join(lines) + "\n"


PARTS_HEADER = "Parts: " + " · ".join(WEIGHTS)


def _repo_link(report: RepoReport) -> str:
    from meshkit.upstream import _inert

    path = f"/tree/HEAD/{report.folder}" if report.folder else ""
    label = report.repo + (f"/{report.folder}" if report.folder else "")
    return f"[{_inert(label)}](https://github.com/{report.repo}{path})"


def _completeness(pair: tuple[RepoReport, dict]) -> tuple:
    robot = pair[1]
    return (bool(robot.get("flattened")), robot.get("links") or 0, robot["score"],
            -len(robot["path"]))


def _formats(robot: dict) -> str:
    return ", ".join(f"{n} {k.upper()}" for k, n in sorted(robot.get("formats", {}).items())) or "-"


if __name__ == "__main__" and "--worker" in sys.argv:
    raise SystemExit(_worker())
