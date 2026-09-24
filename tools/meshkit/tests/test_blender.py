import sys

import pytest

from meshkit import blender
from meshkit.blender import ENV_VAR, BlenderNotFound, find_blender, parse_version


def test_parse_version():
    assert parse_version("Blender 5.2.1 LTS\n\tbuild date: ...") == ((5, 2, 1), "Blender 5.2.1 LTS")
    assert parse_version("Blender 5.3\n") == ((5, 3, 0), "Blender 5.3")
    assert parse_version("not blender") is None


def test_env_var_pointing_nowhere_is_an_error(tmp_path):
    with pytest.raises(BlenderNotFound, match="does not exist"):
        find_blender(env={ENV_VAR: str(tmp_path / "nope")}, home=tmp_path)


def test_env_var_is_authoritative_even_when_others_exist(tmp_path, monkeypatch):
    # A bad KINEMA_BLENDER must not silently fall back to some other install.
    exe = tmp_path / "blender.exe"
    exe.write_text("")
    monkeypatch.setattr(blender, "probe", lambda path: ((4, 5, 0), "Blender 4.5.0"))
    with pytest.raises(BlenderNotFound, match="needs Blender 5.2.0"):
        find_blender(env={ENV_VAR: str(exe)}, home=tmp_path)


def test_launcher_library_is_searched(tmp_path, monkeypatch):
    name = "blender.exe" if sys.platform == "win32" else "blender"
    exe = tmp_path / "blender" / "blender_releases" / "stable" / "blender-5.2.1-lts.abc" / name
    exe.parent.mkdir(parents=True)
    exe.write_text("")
    monkeypatch.setattr(blender.shutil, "which", lambda _: None)
    monkeypatch.setattr(blender, "_system_candidates", lambda: [])
    monkeypatch.setattr(blender, "probe", lambda path: ((5, 2, 1), "Blender 5.2.1 LTS"))
    found = find_blender(env={}, home=tmp_path)
    assert found.path == exe and found.source == "Blender Launcher library"


def test_too_old_is_reported(tmp_path, monkeypatch):
    exe = tmp_path / "old-blender"
    exe.write_text("")
    monkeypatch.setattr(blender.shutil, "which", lambda _: str(exe))
    monkeypatch.setattr(blender, "_system_candidates", lambda: [])
    monkeypatch.setattr(blender, "probe", lambda path: ((4, 2, 0), "Blender 4.2.0"))
    with pytest.raises(BlenderNotFound, match="too old"):
        find_blender(env={}, home=tmp_path)
