"""Finding a usable Blender, and running a job script inside it.

meshkit does not install Blender and does not use the ``bpy`` wheel: it drives
the Blender a contributor already has, as a headless subprocess. That keeps the
engine identical to the one kinema runs in, and keeps a ~1 GB wheel out of the
environment.

Discovery order:

1. ``$KINEMA_BLENDER`` -- the path to the executable. When it is set it is
   authoritative: a wrong or too-old path is an error, never a silent fallback
   to some other Blender that happens to be lying around.
2. ``blender`` on ``PATH``.
3. Blender Launcher's library, ``~/blender/blender_releases/{stable,lts}/*`` --
   its folder names carry a build hash that changes on every update, so a fixed
   path would go stale; the newest qualifying build wins.
4. The usual per-OS install locations.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ENV_VAR = "KINEMA_BLENDER"
# kinema's blender_version_min. Blender 5.0 dropped COLLADA and changed enough
# of the Python API that older builds are not worth supporting here.
MIN_VERSION = (5, 2, 0)

_VERSION_RE = re.compile(r"Blender\s+(\d+)\.(\d+)(?:\.(\d+))?")

# A batch of 25 robot meshes takes well under a minute. An hour means Blender
# is stuck -- an endless loop on a malformed file -- and waiting longer would
# only hide it.
DEFAULT_TIMEOUT = 3600.0
# What run_script returns for a Blender it had to stop; timeout(1)'s status.
TIMED_OUT = 124


class BlenderNotFound(RuntimeError):
    """No usable Blender was found, or the one named explicitly is unusable."""


@dataclass(frozen=True)
class Blender:
    path: Path
    version: tuple[int, int, int]
    version_string: str
    source: str  # which discovery rule found it

    def describe(self) -> str:
        return f"{self.version_string} at {self.path} (via {self.source})"


def parse_version(text: str) -> tuple[tuple[int, int, int], str] | None:
    """Parse the first line of ``blender --version``."""
    for line in text.splitlines():
        match = _VERSION_RE.search(line)
        if match:
            major, minor, patch = match.groups()
            return (int(major), int(minor), int(patch or 0)), line.strip()
    return None


def probe(path: Path) -> tuple[tuple[int, int, int], str] | None:
    """Ask an executable for its Blender version; None if it is not Blender."""
    try:
        completed = subprocess.run(
            [str(path), "--version"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return parse_version(completed.stdout)


def _exe_name() -> str:
    return "blender.exe" if sys.platform == "win32" else "blender"


def _newest_first(paths) -> list[Path]:
    """Sort install paths newest first, reading each run of digits as a number.

    Plain string order puts blender-5.2.9 ahead of blender-5.2.10, and LTS
    point releases do reach two digits.
    """
    def key(path: Path) -> list:
        return [int(part) if part.isdigit() else part
                for part in re.split(r"(\d+)", str(path))]
    return sorted(paths, key=key, reverse=True)


def _launcher_candidates(home: Path) -> list[Path]:
    root = home / "blender" / "blender_releases"
    found: list[Path] = []
    for channel in ("stable", "lts"):
        base = root / channel
        if base.is_dir():
            found.extend(_newest_first(base.glob(f"*/{_exe_name()}")))
    return found


def _system_candidates() -> list[Path]:
    if sys.platform == "win32":
        roots = [os.environ.get("ProgramFiles", r"C:\Program Files")]
        found: list[Path] = []
        for root in roots:
            found.extend(
                _newest_first(Path(root, "Blender Foundation").glob("Blender */blender.exe"))
            )
        return found
    if sys.platform == "darwin":
        return [Path("/Applications/Blender.app/Contents/MacOS/Blender")]
    return _newest_first(Path("/opt").glob("blender*/blender")) + [Path("/usr/bin/blender")]


def find_blender(
    env: dict[str, str] | None = None,
    home: Path | None = None,
    *,
    min_version: tuple[int, int, int] = MIN_VERSION,
) -> Blender:
    """Return the Blender meshkit should use, or raise BlenderNotFound."""
    env = os.environ if env is None else env
    home = Path.home() if home is None else home

    explicit = env.get(ENV_VAR)
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise BlenderNotFound(f"{ENV_VAR} points at {path}, which does not exist")
        probed = probe(path)
        if probed is None:
            raise BlenderNotFound(f"{ENV_VAR}={path} did not report a Blender version")
        version, text = probed
        if version < min_version:
            raise BlenderNotFound(
                f"{ENV_VAR}={path} is {text}; meshkit needs Blender "
                f"{'.'.join(map(str, min_version))} or newer"
            )
        return Blender(path, version, text, ENV_VAR)

    candidates: list[tuple[Path, str]] = []
    on_path = shutil.which("blender")
    if on_path:
        candidates.append((Path(on_path), "PATH"))
    candidates += [(p, "Blender Launcher library") for p in _launcher_candidates(home)]
    candidates += [(p, "system install") for p in _system_candidates()]

    too_old: list[str] = []
    for path, source in candidates:
        if not path.is_file():
            continue
        probed = probe(path)
        if probed is None:
            continue
        version, text = probed
        if version >= min_version:
            return Blender(path, version, text, source)
        too_old.append(f"{text} at {path}")

    hint = f"Set {ENV_VAR} to the path of a Blender {'.'.join(map(str, min_version))}+ executable."
    if too_old:
        raise BlenderNotFound("only found Blender builds that are too old: "
                              + "; ".join(too_old) + ". " + hint)
    raise BlenderNotFound("no Blender found. " + hint)


def run_script(
    blender: Blender,
    script: Path,
    script_args: list[str],
    *,
    log_path: Path,
    timeout: float | None = DEFAULT_TIMEOUT,
) -> int:
    """Run ``script`` inside Blender, headless, and log everything it prints.

    ``--factory-startup`` keeps a contributor's preferences and enabled add-ons
    from changing the result: the same inputs must give the same GLB on any
    machine.

    A Blender still running after ``timeout`` seconds is stopped, and
    ``TIMED_OUT`` returned like any other failing status: whatever the job had
    already written to its results file is still there to read.
    """
    command = [
        str(blender.path),
        "--background",
        "--factory-startup",
        "--python-exit-code", "3",   # an uncaught exception in the script -> non-zero
        "--python", str(script),
        "--",
        *script_args,
    ]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with log_path.open("w", encoding="utf-8", errors="replace") as log:
            completed = subprocess.run(
                command,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                check=False,
            )
    except subprocess.TimeoutExpired:
        # subprocess.run has already killed Blender by the time this is raised.
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"\nmeshkit: stopped Blender after {timeout:g} s\n")
        return TIMED_OUT
    return completed.returncode
