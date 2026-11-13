"""Provenance of the vendored COLLADA importer.

``blender_side/kinema_dae.py`` is kinema's ``src/kinema/io/dae.py`` at a pinned
commit, unchanged. It is vendored rather than depended on because kinema is
never pip-installed (``package = false``), and importing it as a package would
run ``kinema/__init__.py``, which registers the whole add-on. The file itself
only needs ``bpy``, ``mathutils`` and ``collada``, so it is loaded by path
inside Blender instead.

Converting through kinema's own importer is the point: a GLB made here should
look like the robot kinema imports. So a fix to the importer goes to kinema
first, and the file is then re-vendored from the commit that has it. Anything
else changing the file is drift, and ``meshkit convert`` refuses to run on it.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

REPOSITORY = "https://github.com/ebgenius/kinema"
UPSTREAM_PATH = "src/kinema/io/dae.py"
# The COLLADA importer fixes from ebgenius/kinema#126: authored normals kept,
# instances whose material failed to bind kept where their nodes put them,
# <lines> skipped, and corners kept on the faces Blender keeps.
COMMIT = "fac9fcae5e17b4affae251133c31a07ac754fe8a"
# COMMIT's file, with line endings normalised to LF so that a CRLF checkout on
# Windows does not read as drift.
SHA256 = "0ddb7af279755eaa0c782503b0d8fac6d8192cc922695742059097355b246669"

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
        "sha256": actual,
        "matches_pinned": actual == SHA256,
    }
