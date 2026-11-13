"""The catalog index: ``catalog/*.yaml`` in, ``catalog.json`` out.

The YAML files are the hand-edited source, one per family (a maker's range,
which is usually one fork). ``catalog.json`` at the repository root is built
from them and committed, because everything that reads the catalog reads that
file: the launcher on the host and in the container, meshkit, and kinema. Each
entry in it is complete, with derived fields such as ``format`` filled in, so
a reader never needs to apply defaults. ``catalog.schema.json`` describes the
file, and the tests hold the two to each other.

``check`` is what keeps the index honest beyond its shape. The built file must
match the sources, every submodule must have an entry, and every entry must
name a submodule that exists and an entry point that does.
"""

from __future__ import annotations

import configparser
import json
import re
from pathlib import Path

import yaml

SOURCE_DIR = "catalog"
INDEX_FILE = "catalog.json"
SCHEMA_FILE = "catalog.schema.json"
SCHEMA_VERSION = 1

KINDS = ("robot", "end_effector", "hand", "base", "scene")
CATEGORIES = ("arm", "mobile", "legged")
FORMATS = {".xacro": "xacro", ".urdf": "urdf"}

_ID = re.compile(r"^[a-z][a-z0-9_]*$")
_FAMILY_KEYS = {"family", "maker", "entries"}
_REQUIRED = ("id", "name", "category", "submodule", "entry", "licence")
_OPTIONAL = ("kind", "tags", "args", "mesh_base", "licence_note")
# The order every entry is written in, so that a diff of catalog.json reads
# the same way as a diff of its source.
_FIELDS = ("id", "name", "kind", "category", "family", "maker", "tags", "licence",
           "licence_note", "submodule", "entry", "format", "args", "mesh_base")


class CatalogError(ValueError):
    """The catalog's sources or its index cannot be read as a catalog."""


def _entry(raw, *, where: str, family: str, maker: str) -> dict:
    if not isinstance(raw, dict):
        raise CatalogError(f"{where}: an entry must be a mapping, not {type(raw).__name__}")
    label = f"{where} ({raw.get('id', '?')})"
    unknown = set(raw) - set(_REQUIRED) - set(_OPTIONAL)
    if unknown:
        raise CatalogError(f"{label}: unknown key(s) {', '.join(sorted(unknown))}")
    missing = [key for key in _REQUIRED if key not in raw]
    if missing:
        raise CatalogError(f"{label}: missing {', '.join(missing)}")
    for key in (*_REQUIRED, "kind", "mesh_base", "licence_note"):
        if key in raw and not (isinstance(raw[key], str) and raw[key].strip()):
            raise CatalogError(f"{label}: {key} must be a non-empty string")
        if key in raw and ("\t" in raw[key] or "\n" in raw[key]):
            # The launcher reads entries as tab-separated lines (catalog_rows.py).
            raise CatalogError(f"{label}: {key} may not contain a tab or a newline")
    if not _ID.match(raw["id"]):
        raise CatalogError(f"{label}: id must be lowercase letters, digits and _, "
                           "starting with a letter")
    kind = raw.get("kind", "robot")
    if kind not in KINDS:
        raise CatalogError(f"{label}: kind must be one of {', '.join(KINDS)}")
    if raw["category"] not in CATEGORIES:
        raise CatalogError(f"{label}: category must be one of {', '.join(CATEGORIES)}")
    entry = raw["entry"]
    format_ = FORMATS.get(Path(entry).suffix)
    if format_ is None:
        raise CatalogError(f"{label}: entry must end in .xacro or .urdf: {entry}")
    if Path(entry).is_absolute() or ".." in Path(entry).parts:
        raise CatalogError(f"{label}: entry must be relative to the repository root: {entry}")
    args = raw.get("args", {})
    if not isinstance(args, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in args.items()):
        raise CatalogError(f"{label}: args must map names to strings (quote numbers)")
    if any(not k or any(c.isspace() for c in k + v) for k, v in args.items()):
        # The launcher passes them to xacro as name:=value words.
        raise CatalogError(f"{label}: an xacro argument may not be empty or contain whitespace")
    tags = raw.get("tags", [])
    if not isinstance(tags, list) or not all(isinstance(t, str) and t for t in tags):
        raise CatalogError(f"{label}: tags must be a list of strings")

    built = {
        "id": raw["id"], "name": raw["name"], "kind": kind, "category": raw["category"],
        "family": family, "maker": maker, "tags": tags, "licence": raw["licence"],
        "licence_note": raw.get("licence_note"), "submodule": raw["submodule"],
        "entry": entry, "format": format_, "args": args, "mesh_base": raw.get("mesh_base"),
    }
    if built["licence_note"] is None:
        del built["licence_note"]
    return {key: built[key] for key in _FIELDS if key in built}


def load_sources(root: Path) -> list[dict]:
    """Every entry of ``catalog/*.yaml``, complete, in file then entry order."""
    source_dir = root / SOURCE_DIR
    files = sorted(source_dir.glob("*.yaml"))
    if not files:
        raise CatalogError(f"{source_dir}: no family files (*.yaml)")
    entries: list[dict] = []
    seen: dict[str, str] = {}
    for path in files:
        where = path.relative_to(root).as_posix()
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise CatalogError(f"{where}: {exc}") from None
        if not isinstance(data, dict):
            raise CatalogError(f"{where}: must be a mapping with family, maker and entries")
        unknown = set(data) - _FAMILY_KEYS
        missing = _FAMILY_KEYS - set(data)
        if unknown or missing:
            raise CatalogError(f"{where}: needs exactly the keys family, maker and entries"
                               + (f"; unknown {', '.join(sorted(unknown))}" if unknown else "")
                               + (f"; missing {', '.join(sorted(missing))}" if missing else ""))
        family, maker = data["family"], data["maker"]
        if family != path.stem:
            raise CatalogError(f"{where}: family is {family!r}, but the file is named "
                               f"{path.name}; they must match")
        if not (isinstance(maker, str) and maker.strip()):
            raise CatalogError(f"{where}: maker must be a non-empty string")
        if not isinstance(data["entries"], list) or not data["entries"]:
            raise CatalogError(f"{where}: entries must be a non-empty list")
        for number, raw in enumerate(data["entries"], 1):
            entry = _entry(raw, where=f"{where} entry {number}", family=family, maker=maker)
            if entry["id"] in seen:
                raise CatalogError(f"{where}: id {entry['id']!r} is also in {seen[entry['id']]}")
            seen[entry["id"]] = where
            entries.append(entry)
    return entries


def build(root: Path) -> dict:
    """The catalog.json document for these sources."""
    return {
        "$schema": f"./{SCHEMA_FILE}",
        "schema_version": SCHEMA_VERSION,
        "generated_from": f"{SOURCE_DIR}/*.yaml",
        "entries": load_sources(root),
    }


def render(document: dict) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def write(root: Path) -> Path:
    path = root / INDEX_FILE
    path.write_text(render(build(root)), encoding="utf-8", newline="\n")
    return path


def load(root: Path) -> list[dict]:
    """The entries of the built catalog.json, which is what the catalog's readers use."""
    path = root / INDEX_FILE
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise CatalogError(f"{path} not found: build it with `meshkit index`") from None
    except json.JSONDecodeError as exc:
        raise CatalogError(f"{path}: {exc}") from None
    if not isinstance(document, dict) or document.get("schema_version") != SCHEMA_VERSION:
        raise CatalogError(f"{path}: not a schema_version {SCHEMA_VERSION} catalog")
    entries = document.get("entries")
    if not isinstance(entries, list):
        raise CatalogError(f"{path}: entries must be a list")
    for number, entry in enumerate(entries, 1):
        if not isinstance(entry, dict) or not all(key in entry for key in
                                                  ("id", "submodule", "format", "entry", "args")):
            raise CatalogError(f"{path}: entry {number} is incomplete; rebuild with "
                               "`meshkit index`")
    return entries


def submodules(root: Path) -> list[str]:
    """The submodules under src/ that .gitmodules declares, by directory name."""
    parser = configparser.ConfigParser()
    parser.read(root / ".gitmodules", encoding="utf-8")
    names = []
    for section in parser.sections():
        path = parser[section].get("path", "")
        if path.startswith("src/"):
            names.append(path.removeprefix("src/"))
    return sorted(names)


def _cloned(root: Path, submodule: str) -> bool:
    directory = root / "src" / submodule
    return directory.is_dir() and any(directory.iterdir())


def check(root: Path) -> list[str]:
    """What is wrong with the catalog, as sentences. Empty when nothing is."""
    try:
        document = build(root)
    except CatalogError as exc:
        return [str(exc)]
    problems = []
    index = root / INDEX_FILE
    if not index.is_file():
        problems.append(f"{INDEX_FILE} is missing: run `meshkit index`")
    elif index.read_text(encoding="utf-8").replace("\r\n", "\n") != render(document):
        problems.append(f"{INDEX_FILE} does not match {SOURCE_DIR}/*.yaml: run `meshkit index`")

    entries = document["entries"]
    declared = submodules(root)
    named = {entry["submodule"] for entry in entries}
    for submodule in declared:
        if submodule not in named:
            problems.append(f"src/{submodule} has no catalog entry")
    for entry in entries:
        label = f"{entry['family']}/{entry['id']}"
        if entry["submodule"] not in declared:
            problems.append(f"{label}: submodule {entry['submodule']!r} is not in .gitmodules")
            continue
        # A path inside an uncloned submodule cannot be checked; one outside
        # src/ (a wrapper kept in this repository) always can.
        for key in ("entry", "mesh_base"):
            value = entry.get(key)
            if value is None:
                continue
            inside = Path(value).parts[:2] == ("src", entry["submodule"])
            if value.startswith("src/") and not inside:
                problems.append(f"{label}: {key} {value} is not in src/{entry['submodule']}")
            elif (not inside or _cloned(root, entry["submodule"])) and not (root / value).exists():
                problems.append(f"{label}: {key} {value} does not exist")
    return problems
