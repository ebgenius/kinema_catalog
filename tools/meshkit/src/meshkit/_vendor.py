"""Provenance of the vendored COLLADA importer.

``blender_side/kinema_dae.py`` is kinema's ``src/kinema/io/dae.py`` at a pinned
commit, plus the patches listed in ``PATCHES``. It is vendored rather than
depended on because kinema is never pip-installed (``package = false``), and
importing it as a package would run ``kinema/__init__.py``, which registers the
whole add-on. The file itself only needs ``bpy``, ``mathutils`` and ``collada``,
so it is loaded by path inside Blender instead.

Converting through kinema's own importer is the point: a GLB made here should
look like the robot kinema imports. So every departure from upstream is a patch
file under ``tools/meshkit/patches/``, applicable to kinema as-is, and meant to
go upstream -- after which the file is re-vendored from the new commit and the
patch deleted. Anything else changing the file is drift, and ``meshkit convert``
refuses to run on it.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

REPOSITORY = "https://github.com/ebgenius/kinema"
UPSTREAM_PATH = "src/kinema/io/dae.py"
COMMIT = "cf35e9cf35e467f8851498fb5d011fabdf184129"  # Release 0.5.0 (#55)
# sha256 values are of the file with line endings normalised to LF, so a CRLF
# checkout on Windows does not read as drift.
UPSTREAM_SHA256 = "085541ac346a05f5bb8b8855991564288846671ee0ff2cce9663c1d7a60e05a5"
PATCHES = (
    # Custom normals were set before the faces were marked smooth, and Blender
    # then averaged them across every hard edge: authored normals were lost on
    # every .dae kinema imported.
    "0001-dae-keep-custom-normals.patch",
    # When a material failed to bind, pycollada dropped that <instance_geometry>
    # and its node with it: lost outright if other instances survived, and
    # otherwise imported from the library alone, unplaced and only once.
    "0002-dae-fallback-keeps-node-placement.patch",
    # <lines> were read three indices at a time, as if they were triangles:
    # franka's link7 gained two triangles the file never had.
    "0003-dae-skip-line-primitives.patch",
)
# COMMIT's file with PATCHES applied -- what VENDORED_FILE must hash to.
SHA256 = "80963a10ddd803de032ad667fcfd0e7688344a2df540cfdc48d332f5bd3dfc08"

VENDORED_FILE = Path(__file__).parent / "blender_side" / "kinema_dae.py"


def normalised_sha256(path: Path) -> str:
    """sha256 of a text file with CRLF folded to LF."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def importer_provenance() -> dict:
    """What the report records about the importer that produced a GLB."""
    actual = normalised_sha256(VENDORED_FILE)
    return {
        "repository": REPOSITORY,
        "path": UPSTREAM_PATH,
        "commit": COMMIT,
        "patches": list(PATCHES),
        "sha256": actual,
        "matches_pinned": actual == SHA256,
    }
