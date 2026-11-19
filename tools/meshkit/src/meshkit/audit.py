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
    "licence": 15,    # a licence named, and a LICENSE file that says it
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


def gather(root: Path, github, *, lists: bool = True, only: list[str] | None = None
           ) -> list[Candidate]:
    """The catalog's forks, then every candidate the lists name, once each."""
    from meshkit import upstream

    forks = upstream.read_forks(root)
    candidates: list[Candidate] = []
    known: set[str] = set()
    for fork in forks:
        candidate = Candidate(f"fork:{fork.name}", fork.repo, fork=fork.name, sources=["catalog"])
        try:
            meta = github.repo(fork.repo)
            parent = meta.get("parent") or meta
            known |= {fork.repo.lower(), parent["full_name"].lower()}
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
                raise upstream.GitHubError(f"{source.name} cannot be read: {exc}") from None
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

    if only:
        wanted = {o.lower() for o in only}
        candidates = [c for c in candidates
                      if {c.key.lower(), c.repo.lower(), (c.fork or "").lower()} & wanted]
    return candidates


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


def fetch(repo: str, cache: Path, *, update: bool = True) -> tuple[Path, str, str]:
    """A shallow clone of ``repo``'s default branch: (where, commit, its date)."""
    dest = cache_dir(cache, repo)
    url = f"https://github.com/{repo}.git"
    if (dest / ".git").is_dir():
        if update:
            _git("fetch", "--depth", "1", "--no-tags", "origin", "HEAD", cwd=dest)
            _git("reset", "--hard", "-q", "FETCH_HEAD", cwd=dest)
    else:
        if dest.exists():
            shutil.rmtree(dest)       # a clone that died halfway
        dest.parent.mkdir(parents=True, exist_ok=True)
        _git("clone", "--depth", "1", "--no-tags", "--single-branch", "-q", url, str(dest))
    commit = _git("rev-parse", "HEAD", cwd=dest)
    date = _git("log", "-1", "--format=%cI", cwd=dest)
    return dest, commit, date


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
    its count is a floor.
    """
    facts = {"format": path.suffix.lower().lstrip("."), "bytes": 0, "triangles": None,
             "normals": None, "materials": None, "error": None}
    try:
        facts["bytes"] = path.stat().st_size
        with open(path, "rb") as handle:
            head = handle.read(512)
            if head.startswith(_LFS):
                facts["error"] = "in Git LFS, not fetched"
                return facts
            data = head + handle.read()
    except OSError as exc:
        facts["error"] = f"cannot read: {exc.strerror or exc}"
        return facts
    kind = facts["format"]
    if kind == "stl":
        facts["normals"] = facts["materials"] = False
        if data[:5].lower() == b"solid" and b"facet" in data[:2048]:
            facts["triangles"] = data.count(b"facet normal")
        elif len(data) >= 84:
            facts["triangles"] = int.from_bytes(data[80:84], "little")
    elif kind == "obj":
        triangles = 0
        normals = materials = False
        for line in data.splitlines():
            if line.startswith(b"f "):
                triangles += max(len(line.split()) - 3, 1)
            elif line.startswith(b"vn "):
                normals = True
            elif line.startswith((b"usemtl", b"mtllib")):
                materials = True
        facts.update(triangles=triangles, normals=normals, materials=materials)
    elif kind == "dae":
        text = data.decode("utf-8", "replace")
        counts = re.findall(r"<(?:triangles|polylist|polygons)\b[^>]*\bcount=\"(\d+)\"", text)
        facts.update(triangles=sum(int(c) for c in counts),
                     normals='semantic="NORMAL"' in text,
                     materials=bool(re.search(r"<material\b", text)))
    elif kind in ("glb", "gltf"):
        facts.update(_gltf_facts(data, binary=kind == "glb"))
    elif kind == "ply":
        header = data.split(b"end_header", 1)[0].decode("ascii", "replace")
        faces = re.search(r"element face (\d+)", header)
        facts.update(triangles=int(faces.group(1)) if faces else None,
                     normals=" nx" in header,
                     materials=bool(re.search(r"property \w+ (red|diffuse_red)", header)))
    return facts


def _gltf_facts(data: bytes, *, binary: bool) -> dict:
    try:
        if binary:
            length = int.from_bytes(data[12:16], "little")
            document = json.loads(data[20:20 + length])
        else:
            document = json.loads(data)
    except (ValueError, IndexError):
        return {"error": "not a readable glTF"}
    accessors = document.get("accessors", [])
    triangles, normals = 0, True
    for mesh in document.get("meshes", []):
        for primitive in mesh.get("primitives", []):
            if primitive.get("mode", 4) != 4:
                continue
            normals &= "NORMAL" in primitive.get("attributes", {})
            index = primitive.get("indices")
            source = index if index is not None else primitive.get("attributes", {}).get(
                "POSITION")
            if isinstance(source, int) and source < len(accessors):
                triangles += accessors[source].get("count", 0) // 3
    return {"triangles": triangles, "normals": normals,
            "materials": bool(document.get("materials"))}


# --------------------------------------------------------------- measurement

def _resolve(filename: str, source: Path, mapping: dict[str, str],
             mesh_base: Path | None) -> Path | None:
    text = filename.strip()
    if text.startswith("file://"):
        text = text[len("file://"):]
        if re.match(r"^/[A-Za-z]:", text):
            text = text[1:]
    if text.startswith("package://"):
        package, _, rest = text[len("package://"):].partition("/")
        where = mapping.get(package)
        return Path(where) / rest if where else None
    path = Path(text)
    if path.is_absolute():
        return path
    return (mesh_base or source.parent) / text


def _share(part: int, whole: int) -> float | None:
    return round(part / whole, 3) if whole else None


def measure_urdf(text: str, source: Path, mapping: dict[str, str], *,
                 mesh_base: Path | None = None, facts: dict | None = None) -> dict:
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
                path = _resolve(mesh.get("filename"), source, mapping, mesh_base)
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


def _mjcf_tree(path: Path, seen: set[Path] | None = None) -> ET.Element:
    """The model with every <include> put in place, the way MuJoCo reads it."""
    seen = seen or set()
    root = ET.parse(path).getroot()
    seen.add(path.resolve())

    def expand(element: ET.Element) -> None:
        for index, child in reversed(list(enumerate(element))):
            if child.tag == "include" and child.get("file"):
                target = (path.parent / child.get("file")).resolve()
                element.remove(child)
                if target in seen or not target.is_file():
                    continue
                included = _mjcf_tree(target, seen)
                for offset, grandchild in enumerate(list(included)):
                    element.insert(index + offset, grandchild)
            else:
                expand(child)

    expand(root)
    return root


def measure_mjcf(path: Path, *, facts: dict | None = None) -> dict:
    root = _mjcf_tree(path)
    compiler = root.find("compiler")
    meshdir = path.parent
    if compiler is not None:
        meshdir = path.parent / (compiler.get("meshdir") or compiler.get("assetdir") or "")
    meshes = {}
    for mesh in root.iter("mesh"):
        if mesh.get("file"):
            name = mesh.get("name") or Path(mesh.get("file")).stem
            meshes[name] = meshdir / mesh.get("file")
    # MuJoCo merges every <worldbody>: an included file brings its own.
    worlds = list(root.iter("worldbody"))
    bodies = [b for world in worlds for b in world.iter("body")]
    joints = [j for world in worlds for j in world.iter("joint")
              if j.get("type", "hinge") in ("hinge", "slide")]
    limited = sum(1 for j in joints if j.get("range") and j.get("limited") != "false")
    # MuJoCo gives a body without <inertial> the inertia of its geoms.
    massed = sum(1 for b in bodies if b.find("inertial") is not None or b.find("geom") is not None)
    visuals = []
    for geom in (g for world in worlds for g in world.iter("geom")):
        colour = bool(geom.get("material") or geom.get("rgba"))
        if geom.get("type") == "mesh" or geom.get("mesh"):
            target = meshes.get(geom.get("mesh"))
            visuals.append({"mesh": str(target) if target else geom.get("mesh"),
                            "found": bool(target and target.is_file()), "colour": colour})
        else:
            visuals.append({"mesh": None, "found": True, "colour": colour})
    # MJCF has no velocity limits: that half of the score is not asked of it.
    return _summarise(root.get("model"), len(bodies), len(joints), limited, None,
                      len(bodies), massed, visuals, facts)


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
        "formats": formats,
        "normals_share": _share(normals, len(readable)),
        "materials_share": round(material_points / len(visuals), 3) if visuals else None,
        "triangles": sum(f["triangles"] or 0 for f in files.values()),
        "megabytes": round(sum(f["bytes"] for f in files.values()) / 1e6, 2),
    }


def measure(path: Path, kind: str, mapping: dict[str, str], *, args: dict | None = None,
            mesh_base: Path | None = None, facts: dict | None = None) -> dict:
    """One robot: its measurements, or why it could not be measured."""
    from meshkit.scan import render_xacro

    try:
        if kind == "mjcf":
            result = measure_mjcf(path, facts=facts)
        else:
            text = (render_xacro(path, args or {}, mapping) if kind == "xacro"
                    else path.read_text(encoding="utf-8", errors="replace"))
            result = measure_urdf(text, path, mapping, mesh_base=mesh_base, facts=facts)
    except Exception as exc:  # noqa: BLE001 - one robot must not stop the audit
        message = " ".join(str(exc).split())[:300]
        return {"flattened": False, "error": f"{type(exc).__name__}: {message}"}
    result["flattened"] = result["missing_count"] == 0 and result["links"] > 0
    result["error"] = (None if result["flattened"] else
                       "renders no links with its default arguments" if not result["links"]
                       else
                       f"{result['missing_count']} visual mesh file(s) missing")
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

def licence_file(base: Path, up_to: Path) -> bool:
    """A LICENSE (or LICENCE, COPYING) beside the robot or in a folder above it."""
    here = base if base.is_dir() else base.parent
    while True:
        try:
            if any(p.is_file() and p.name.lower().split(".")[0] in LICENCE_FILES
                   for p in here.iterdir()):
                return True
        except OSError:
            return False
        if here == up_to or here.parent == here or not here.is_relative_to(up_to):
            return False
        here = here.parent


def package_of(path: Path, up_to: Path) -> str | None:
    """The ROS package a robot file belongs to: the nearest package.xml above it.

    A package's variants (robot.xacro, ros2_control/robot.xacro, a URDF
    generated from them) are one robot as far as forking goes.
    """
    here = path.parent
    while here.is_relative_to(up_to):
        manifest = here / "package.xml"
        if manifest.is_file():
            try:
                name = ET.parse(manifest).getroot().findtext("name")
            except (ET.ParseError, OSError):
                name = None
            return (name or here.name).strip()
        if here == up_to or here.parent == here:
            break
        here = here.parent
    return None


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
                         facts=facts)
        relative = path.relative_to(spec["path_base"]).as_posix() if spec.get(
            "path_base") else path.relative_to(base).as_posix()
        # A wrapper under descriptions/ describes its fork's robot: the fork's
        # LICENSE is the one that covers it.
        result.update(path=relative, kind=kind, id=(entry or {}).get("id"),
                      package=package_of(path, base),
                      licence_file=licence_file(path, base) or licence_file(base, base))
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

    def as_json(self) -> dict:
        return {"generated": self.generated, "weights": self.weights,
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


def run(root: Path, github, cache: Path, *, lists: bool = True, only: list[str] | None = None,
        update: bool = True, workers: int = 4, timeout: int = REPO_TIMEOUT,
        progress=print) -> Audit:
    from meshkit.catalog import load as load_catalog

    candidates = gather(root, github, lists=lists, only=only)
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
    packages = index_packages({str(where): where for where in set(places.values())})
    progress(f"{len(set(places.values()))} repositories in place, "
             f"{len(packages)} ROS packages found")

    def measure_one(candidate: Candidate) -> None:
        report = reports[candidate.key]
        where = places.get(candidate.key)
        if where is None:
            return
        spec = {"dir": str(where), "folder": candidate.folder, "root": str(root),
                "packages": package_map(packages, str(where)),
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
    return Audit(generated, dict(WEIGHTS), [reports[c.key] for c in candidates])


def _robot_licence(candidate: Candidate, robot: dict, entries: dict) -> str | None:
    """The catalog's own licence for its entries; GitHub's for a candidate."""
    if candidate.fork:
        for entry in entries.get(candidate.fork, []):
            if entry["id"] == robot.get("id"):
                return entry["licence"]
    return candidate.licence


# --------------------------------------------------------------------- report

def render_markdown(audit: Audit, *, listed: int = 40, top_rows: int = 100) -> str:
    from meshkit.upstream import _code, _inert

    forks = [r for r in audit.repos if r.fork]
    candidates = [r for r in audit.repos if not r.fork]
    measured = [r for r in candidates if r.robots]
    robots = [(r, robot) for r in measured for robot in r.robots]
    lines = [
        "# Robot description audit",
        "",
        f"Written by `meshkit audit` on {audit.generated}. Every robot in the catalog's forks, "
        "and every robot in the repositories the upstream report's lists name, measured "
        "the same way and scored out of 100. "
        "[`audit.json`](audit.json) has every measurement.",
        "",
        f"- **The catalog:** {sum(len(r.robots) for r in forks)} entries in {len(forks)} forks.",
        f"- **Candidates:** {len(robots)} robots in {len(measured)} of {len(candidates)} "
        "repositories or folders; "
        f"{sum(1 for r in candidates if r.error)} could not be audited (listed at the end).",
        "",
        "## How a robot is scored",
        "",
        "| Part | Points | Full marks when |",
        "|---|--:|---|",
        f"| Licence | {WEIGHTS['licence']} | A licence is named and a LICENSE file says it "
        "(half for one of the two) |",
        f"| Alive | {WEIGHTS['alive']} | Upstream committed to in the last year (half: in "
        "three); not archived |",
        f"| Flattens | {WEIGHTS['flattens']} | xacro evaluates (or the MJCF parses) and every "
        "visual mesh is there. Without it the parts below score nothing |",
        f"| Limits | {WEIGHTS['limits']} | Every moving joint has position and velocity limits "
        "(MJCF: position only) |",
        f"| Inertia | {WEIGHTS['inertia']} | Every link with geometry has a mass |",
        f"| Look | {WEIGHTS['look']} | Half for meshes with authored normals, half for "
        "materials (a whole-part colour counts half) |",
        f"| Weight | {WEIGHTS['weight']} | Under {TRIANGLES[0]:,} triangles and "
        f"{MEGABYTES[0]} MB of visual meshes, none from {TRIANGLES[1]:,} or {MEGABYTES[1]} MB |",
        "",
        "Not measured: whether Kinema imports the robot, and whether its kinematics match "
        "the maker's own description. A xacro is evaluated with its default arguments, "
        "using packages from every repository audited; one that needs a package none of "
        "them carries does not flatten. A DAE's polygons count as one triangle each.",
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
                f"{robot.get('licence') or '-'} | {pct(robot.get('limited_share'))} | "
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
    best = [max(group, key=lambda pair: (pair[1]["score"], -len(pair[1]["path"])))
            + (len(group),) for group in groups.values()]
    top = sorted(best, key=lambda t: (-t[1]["score"], t[0].repo.lower(), t[1]["path"]))
    top = top[:top_rows]
    lines += ["", f"## The {len(top)} best-scoring candidates", "",
              f"One row per ROS package: {len(groups)} packages (or files outside any) hold "
              f"the {len(robots)} candidate robots. Each row shows the package's best file "
              "and how many robot files it has.", "",
              "| Score | Package | Best file | Files | Repository | Licence | Formats | "
              "Triangles |",
              "|--:|---|---|--:|---|---|---|--:|"]
    for report, robot, count in top:
        lines.append(f"| {robot['score']} | {_inert(robot.get('package') or '-')} | "
                     f"{_code(robot['path'])} | {count} | {_repo_link(report)} | "
                     f"{robot.get('licence') or '-'} | {_formats(robot)} | "
                     f"{robot.get('triangles') or 0:,} |")

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
            lines.append(f"| | and {len(report.robots) - listed} more, in `audit.json` | | | |")
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


def _formats(robot: dict) -> str:
    return ", ".join(f"{n} {k.upper()}" for k, n in sorted(robot.get("formats", {}).items())) or "-"


if __name__ == "__main__" and "--worker" in sys.argv:
    raise SystemExit(_worker())
