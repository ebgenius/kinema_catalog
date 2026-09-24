"""Which .dae files in the catalog are visual meshes, and which are not.

A mesh's role comes from where it is *referenced*, never from where it sits on
disk: only a third of the catalog's .dae files live under a ``visual/``
directory (Unitree keeps visuals in ``dae/``), so a path rule would convert
collision meshes and miss most visuals.

It works in two passes. The first reads the description sources statically --
no xacro, no ROS -- and maps every mesh reference to the files it can mean:

* URDF and xacro: ``<mesh filename="...">`` inside ``<visual>`` or
  ``<collision>``. xacro expressions (``${name}``, ``$(arg robot)``) vary per
  invocation, so each becomes a wildcard, and one reference can stand for many
  files -- ``.../${robot_type}/visual/${name}.dae`` covers every Franka arm's
  visuals at once, which is exactly the set wanted.
* YAML: Universal Robots names its meshes in config (``visual_parameters.yaml``)
  rather than in xacro; a ``.dae`` string under a ``visual`` key counts as a
  visual reference, resolved against a sibling ``package:`` key.

A reference that is all variable -- ``filename="${mesh}"`` -- would match every
file in sight, so it is reported as unresolved instead of being allowed to
claim anything. An unresolved visual reference means a mesh is not converted;
it never means the wrong one is.

Static reading has a ceiling: xArm builds every mesh path from macro
parameters (``${mesh_path}/${mesh_filename}.${mesh_suffix}``) whose values only
exist at the call site. So the second pass *renders* the robots in
``docker/robots.tsv`` -- xacro evaluated with xacrodoc, the engine kinema uses,
no ROS required -- and the rendered URDFs contribute exact references. (For
xArm they settle it the other way: its default ``mesh_suffix`` is ``stl``, so
its .dae files are not what the robot shows.) The two passes are unioned; the
static one still covers variants the manifest does not list.
"""

from __future__ import annotations

import contextlib
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

MESH_SUFFIX = ".dae"
XML_SUFFIXES = (".urdf", ".xacro")
YAML_SUFFIXES = (".yaml", ".yml")
SKIP_DIRS = {".git", "build", "install", "log", "__pycache__", "node_modules"}

ROLES = ("visual", "collision", "other")

# ${...} and $(arg ...), $(env ...), $(eval ...) -- anything decided at xacro time.
# $(find pkg) is handled separately, because it can be resolved.
_VAR = re.compile(r"\$\{[^}]*\}|\$\((?!find\s)[^)]*\)")
_FIND = re.compile(r"\$\(find\s+([^)\s]+)\s*\)")
_BLOCK = re.compile(r"<(visual|collision)\b[^>]*?(?<!/)>(.*?)</\1\s*>", re.S)
_FILENAME = re.compile(r"""\bfilename\s*=\s*(["'])(.*?)\1""", re.S)
_PROPERTY = re.compile(
    r"""<xacro:property\s+[^>]*?name\s*=\s*(["'])(?P<name>[^"']+)\1[^>]*?"""
    r"""value\s*=\s*(["'])(?P<value>[^"']*)\3""", re.S)
_LONE_VAR = re.compile(r"^\$\{\s*([A-Za-z_][\w.]*)\s*\}$")
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_UP_AXIS = re.compile(rb"<up_axis>\s*([A-Z_]+)\s*</up_axis>")
_WIN_DRIVE = re.compile(r"^/?([A-Za-z]:[\\/].*)$")
_UNDEFINED_ARG = re.compile(r"Undefined substitution argument (\w+)")


class _TolerantLoader(yaml.SafeLoader):
    """SafeLoader that reads unknown tags as plain values instead of failing.

    Universal Robots' configs use xacro's own YAML tags (``yaw: !degrees 180``).
    ``safe_load`` rejects the whole document over one of them, and the mesh
    paths in it were lost with it -- which is how UR came out with zero visuals.
    """


def _construct_any(loader: yaml.SafeLoader, _suffix: str, node: yaml.Node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


_TolerantLoader.add_multi_constructor("!", _construct_any)


@dataclass(frozen=True)
class Package:
    name: str
    root: Path
    fork: str


@dataclass
class MeshRef:
    source: Path
    line: int
    raw: str
    role: str
    matches: list[Path] = field(default_factory=list)
    problem: str | None = None
    via: str = "static"   # or "rendered:<robot id>"


@dataclass
class MeshFile:
    path: Path
    fork: str
    up_axis: str | None
    roles: set[str] = field(default_factory=set)

    @property
    def is_visual(self) -> bool:
        return "visual" in self.roles

    @property
    def is_collision(self) -> bool:
        return "collision" in self.roles


@dataclass
class Inventory:
    root: Path
    packages: dict[str, list[Package]]
    meshes: dict[Path, MeshFile]
    refs: list[MeshRef]

    def forks(self) -> list[str]:
        return sorted({mesh.fork for mesh in self.meshes.values()})

    def in_fork(self, fork: str | None) -> list[MeshFile]:
        items = self.meshes.values()
        if fork is not None:
            items = [m for m in items if m.fork == fork]
        return sorted(items, key=lambda m: m.path)

    def visual(self, fork: str | None = None) -> list[MeshFile]:
        return [m for m in self.in_fork(fork) if m.is_visual]

    def unresolved(self, fork: str | None = None) -> list[MeshRef]:
        refs = [r for r in self.refs if r.problem is not None]
        if fork is not None:
            refs = [r for r in refs if self.fork_of(r.source) == fork]
        return refs

    def fork_of(self, path: Path) -> str:
        return fork_of(self.root, path)


# --------------------------------------------------------------------- helpers

def fork_of(root: Path, path: Path) -> str:
    """The submodule a path belongs to: the first component under ``src/``."""
    rel = path.resolve().relative_to((root / "src").resolve())
    return rel.parts[0]


def _walk(base: Path):
    """Files under base, skipping VCS and build trees."""
    stack = [base]
    while stack:
        current = stack.pop()
        try:
            entries = list(current.iterdir())
        except OSError:
            continue
        for entry in entries:
            if entry.is_dir():
                if entry.name not in SKIP_DIRS:
                    stack.append(entry)
            else:
                yield entry


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _blank_comments(text: str) -> str:
    """Remove XML comments but keep their newlines, so line numbers stay true."""
    return _COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def _line_of(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def _up_axis(path: Path) -> str | None:
    try:
        with path.open("rb") as handle:
            head = handle.read(16384)
    except OSError:
        return None
    match = _UP_AXIS.search(head)
    return match.group(1).decode() if match else None


def _is_too_broad(relative: str) -> bool:
    """True when nothing but variables and the extension pins a reference down."""
    segments = [s for s in relative.split("/") if s]
    if not segments:
        return True
    literal_dirs = [s for s in segments[:-1] if not _VAR.search(s)]
    stem_literal = not _VAR.search(segments[-1])
    return not literal_dirs and not stem_literal


def _to_regex(relative: str) -> re.Pattern[str]:
    parts: list[str] = []
    position = 0
    for match in _VAR.finditer(relative):
        parts.append(re.escape(relative[position:match.start()]))
        parts.append(".*")
        position = match.end()
    parts.append(re.escape(relative[position:]))
    return re.compile("".join(parts), re.IGNORECASE)


# ---------------------------------------------------------------------- scanner

class Scanner:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.src = self.root / "src"
        self.packages: dict[str, list[Package]] = {}
        self.meshes: dict[Path, MeshFile] = {}
        self.refs: list[MeshRef] = []
        self._files_by_fork: dict[str, list[Path]] = {}
        # base directory -> [(mesh, path relative to base)], built once per base.
        # Without it every reference re-walked every mesh in the catalog.
        self._under: dict[Path, list[tuple[Path, str]]] = {}
        self._by_root: dict[Path, Package] | None = None

    # -- indexing

    def index(self) -> None:
        for fork_dir in sorted(p for p in self.src.iterdir() if p.is_dir()):
            files = list(_walk(fork_dir))
            self._files_by_fork[fork_dir.name] = files
            for path in files:
                if path.name == "package.xml":
                    name = self._package_name(path)
                    if name:
                        self.packages.setdefault(name, []).append(
                            Package(name, path.parent.resolve(), fork_dir.name))
                elif path.suffix.lower() == MESH_SUFFIX:
                    resolved = path.resolve()
                    self.meshes[resolved] = MeshFile(resolved, fork_dir.name, _up_axis(path))

    @staticmethod
    def _package_name(path: Path) -> str | None:
        match = re.search(r"<name>\s*([^<\s]+)\s*</name>", _read_text(path))
        return match.group(1) if match else None

    def _packages_named(self, name: str, fork: str) -> list[Package]:
        candidates = self.packages.get(name, [])
        same_fork = [p for p in candidates if p.fork == fork]
        return same_fork or candidates

    def _packages_in(self, fork: str) -> list[Package]:
        return [p for group in self.packages.values() for p in group if p.fork == fork]

    def _owning_package(self, path: Path) -> Package | None:
        """The innermost package containing ``path``: a walk up its parents.

        A dict lookup per ancestor. Testing every package with ``relative_to``
        cost two ``realpath`` calls each, and was most of a scan's time.
        """
        if self._by_root is None:
            self._by_root = {p.root: p for group in self.packages.values() for p in group}
        for parent in path.resolve().parents:
            if parent in self._by_root:
                return self._by_root[parent]
        return None

    # -- resolution

    def _meshes_under(self, base: Path) -> list[tuple[Path, str]]:
        cached = self._under.get(base)
        if cached is None:
            cached = [(m.path, m.path.relative_to(base).as_posix())
                      for m in self.meshes.values() if m.path.is_relative_to(base)]
            self._under[base] = cached
        return cached

    def resolve(self, raw: str, source: Path, *, package_hint: str | None = None
                ) -> tuple[list[Path], str | None]:
        """Files a reference can mean, or the reason it cannot be pinned down."""
        text = raw.strip()
        fork = fork_of(self.root, source)
        bases: list[Path]
        relative: str

        if text.startswith("file://"):
            text = text[len("file://"):]

        # The literal text after the last variable decides the format. A variable
        # stem with a literal extension -- ${name}.stl -- is plainly not a .dae;
        # only a variable *extension* (x.${suffix}) leaves it open. Decided before
        # any package lookup: a missing package matters only for a .dae.
        last = _FIND.sub("", text).replace("\\", "/").rsplit("/", 1)[-1]
        tail = _VAR.split(last)[-1]
        if "." in tail and not tail.lower().endswith(MESH_SUFFIX):
            return [], None
        if not _VAR.search(last) and not last.lower().endswith(MESH_SUFFIX):
            return [], None  # not a .dae reference -- not this tool's concern

        if text.startswith("package://"):
            package_part, _, relative = text[len("package://"):].partition("/")
            if _VAR.search(package_part):
                bases = [p.root for p in self._packages_in(fork)]
            else:
                found = self._packages_named(package_part, fork)
                if not found:
                    return [], f"package '{package_part}' is not in the catalog"
                bases = [p.root for p in found]
        elif (find := _FIND.match(text)) is not None:
            package_part = find.group(1)
            relative = text[find.end():].lstrip("/")
            if _VAR.search(package_part):
                bases = [p.root for p in self._packages_in(fork)]
            else:
                found = self._packages_named(package_part, fork)
                if not found:
                    return [], f"package '{package_part}' is not in the catalog"
                bases = [p.root for p in found]
        elif package_hint and not _VAR.search(package_hint):
            found = self._packages_named(package_hint, fork)
            if not found:
                return [], f"package '{package_hint}' is not in the catalog"
            bases, relative = [p.root for p in found], text.lstrip("/")
        elif (text.startswith("/") or _WIN_DRIVE.match(text)) and not _VAR.search(text):
            # What xacrodoc emits once it has resolved package:// -- an exact file.
            # file:///C:/x arrives here as /C:/x; drop the slash before the drive.
            drive = _WIN_DRIVE.match(text)
            candidate = Path(drive.group(1) if drive else text).resolve()
            if candidate in self.meshes:
                return [candidate], None
            if candidate.suffix.lower() != MESH_SUFFIX:
                return [], None
            if candidate.is_relative_to(self.root):
                return [], "no such .dae file"
            return [], "absolute path outside the catalog"
        elif text.startswith("/") or _WIN_DRIVE.match(text):
            return [], "absolute path outside any package"
        else:
            owner = self._owning_package(source)
            bases = [source.parent.resolve()]
            if owner is not None and owner.root not in bases:
                bases.append(owner.root)
            relative = text

        relative = relative.replace("\\", "/")
        if _is_too_broad(relative):
            return [], "reference is all variables; it would match every mesh"

        pattern = _to_regex(relative)
        matches: set[Path] = set()
        for base in bases:
            for mesh_path, rel in self._meshes_under(base):
                if pattern.fullmatch(rel):
                    matches.add(mesh_path)
        if not matches:
            return [], "no .dae file matches"
        return sorted(matches), None

    def _record(self, source: Path, line: int, raw: str, role: str,
                package_hint: str | None = None, via: str = "static") -> None:
        matches, problem = self.resolve(raw, source, package_hint=package_hint)
        if not matches and problem is None:
            return  # a non-.dae reference
        self.refs.append(MeshRef(source, line, raw, role, matches, problem, via))
        for path in matches:
            self.meshes[path].roles.add(role)

    # -- sources

    def scan_xml(self, path: Path) -> None:
        text = _blank_comments(_read_text(path))
        properties = {m.group("name"): m.group("value") for m in _PROPERTY.finditer(text)}
        covered: list[tuple[int, int]] = []

        def expand(raw: str) -> str:
            # One level of indirection: filename="${mesh}" with the property
            # defined in the same file. Deeper chains stay variables.
            for _ in range(3):
                lone = _LONE_VAR.match(raw.strip())
                if not lone or lone.group(1) not in properties:
                    break
                raw = properties[lone.group(1)]
            return raw

        for block in _BLOCK.finditer(text):
            covered.append(block.span())
            role = block.group(1)
            for name in _FILENAME.finditer(block.group(2)):
                position = block.start(2) + name.start()
                self._record(path, _line_of(text, position), expand(name.group(2)), role)

        for name in _FILENAME.finditer(text):
            if any(start <= name.start() < end for start, end in covered):
                continue
            self._record(path, _line_of(text, name.start()), expand(name.group(2)), "other")

    def scan_yaml(self, path: Path) -> None:
        text = _read_text(path)
        if MESH_SUFFIX not in text.lower():
            return
        try:
            documents = list(yaml.load_all(text, Loader=_TolerantLoader))
        except yaml.YAMLError:
            self.refs.append(MeshRef(path, 1, "", "other", [],
                                     "YAML mentions .dae but could not be parsed"))
            return

        def walk(node, keys: tuple[str, ...], parent: dict | None) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    walk(value, keys + (str(key),), node)
            elif isinstance(node, list):
                for item in node:
                    walk(item, keys, parent)
            elif isinstance(node, str) and node.strip().lower().endswith(MESH_SUFFIX):
                lowered = [k.lower() for k in keys]
                role = ("visual" if any("visual" in k for k in lowered)
                        else "collision" if any("collision" in k for k in lowered)
                        else "other")
                hint = parent.get("package") if isinstance(parent, dict) else None
                line = next((i + 1 for i, row in enumerate(text.splitlines())
                             if node.strip() in row), 1)
                self._record(path, line, node, role,
                             package_hint=str(hint) if hint else None)

        for document in documents:
            walk(document, (), None)

    # -- rendered manifest robots

    def _manifest_rows(self):
        manifest = self.root / "docker" / "robots.tsv"
        if not manifest.is_file():
            return
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) >= 6:
                yield {"id": cols[0], "fork": cols[2], "type": cols[3],
                       "path": cols[4], "args": cols[5]}

    def _render(self, row: dict) -> str:
        """The robot's URDF, with xacro evaluated.

        The package map comes from this scanner's own index, preferring the
        robot's own submodule when two forks ship a package of the same name.
        xacrodoc's package cache is module-global, so it is reset first -- a
        previous robot's packages must not stay resolvable in the next render.
        """
        path = self.root / row["path"]
        if row["type"] != "xacro":
            return _read_text(path)

        from xacrodoc import XacroDoc, packages

        mapping: dict[str, str] = {}
        for name, group in self.packages.items():
            same_fork = [p for p in group if p.fork == row["fork"]]
            mapping[name] = str((same_fork or group)[0].root)
        packages.reset()
        packages.update_package_cache(mapping)

        args = {}
        if row["args"] not in ("", "-"):
            for pair in row["args"].split():
                key, _, value = pair.partition(":=")
                args[key] = value

        # Relative includes (husky's `empty.urdf`) resolve against the working
        # directory, the way a launch file started from the package would.
        # Some unitree robots read $(arg DEBUG) without declaring it; their
        # launch files pass it, so an undeclared argument is retried as "false".
        with contextlib.chdir(path.parent):
            for _ in range(8):
                try:
                    doc = XacroDoc.from_file(str(path), resolve_packages=True, subargs=args)
                    return doc.to_urdf_string()
                except Exception as exc:  # noqa: BLE001 - xacro raises its own types
                    missing = _UNDEFINED_ARG.search(str(exc))
                    if missing is None or missing.group(1) in args:
                        raise
                    args[missing.group(1)] = "false"
        raise RuntimeError("too many undeclared xacro arguments")

    def scan_rendered(self) -> None:
        import xml.etree.ElementTree as ET

        for row in self._manifest_rows():
            source = (self.root / row["path"]).resolve()
            via = f"rendered:{row['id']}"
            try:
                tree = ET.fromstring(self._render(row))
            except Exception as exc:  # noqa: BLE001 - one robot must not stop the scan
                self.refs.append(MeshRef(source, 1, "", "other", [],
                                         f"could not render: {type(exc).__name__}: {exc}", via))
                continue
            for role in ("visual", "collision"):
                for block in tree.iter(role):
                    for mesh in block.iter("mesh"):
                        filename = mesh.get("filename")
                        if filename:
                            self._record(source, 0, filename, role, via=via)

    def run(self, *, render: bool = True) -> Inventory:
        self.index()
        for files in self._files_by_fork.values():
            for path in files:
                name = path.name.lower()
                if name.endswith(XML_SUFFIXES):
                    self.scan_xml(path)
                elif name.endswith(YAML_SUFFIXES):
                    self.scan_yaml(path)
        if render:
            self.scan_rendered()
        return Inventory(self.root, self.packages, self.meshes, self.refs)


def scan(root: Path, *, render: bool = True) -> Inventory:
    """Scan every submodule under ``root/src``; ``render`` adds the manifest robots."""
    return Scanner(root).run(render=render)
