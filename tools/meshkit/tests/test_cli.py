"""Bad input to the command line is an error message, never a traceback."""

import pytest

import meshkit._vendor
from meshkit.cli import main


def test_file_outside_the_catalog_is_refused_with_out(tmp_path):
    # --out mirrors paths under the catalog root; this one has none to mirror.
    root = tmp_path / "catalog"
    root.mkdir()
    elsewhere = tmp_path / "elsewhere.dae"
    elsewhere.write_text("", encoding="utf-8")
    with pytest.raises(SystemExit, match="outside it"):
        main(["--root", str(root), "convert", "--file", str(elsewhere),
              "--out", str(tmp_path / "out")])


@pytest.mark.parametrize("size", ["0", "-1", "two"])
def test_batch_size_must_be_at_least_one(size, capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["convert", "--file", "x.dae", "--batch-size", size])
    assert exit_info.value.code == 2
    assert "--batch-size" in capsys.readouterr().err


@pytest.mark.parametrize("argv", [
    ["convert", "--fork", "arm_fork", "--file", "x.dae"],   # one selection would be dropped
    ["scan", "--json", "--list", "visual"],                  # one format would be ignored
])
def test_options_that_would_silently_lose_each_other_are_refused(argv, capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(argv)
    assert exit_info.value.code == 2
    assert "not allowed with" in capsys.readouterr().err


def test_malformed_manifest_row_is_an_error_not_a_skip(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "docker").mkdir()
    (tmp_path / "docker" / "robots.tsv").write_text(
        "# id\tfamily\tsubmodule\ttype\tpath\targs\n"
        "fer arm franka_description xacro robots/fer.urdf.xacro -\n",   # spaces, not tabs
        encoding="utf-8")
    with pytest.raises(SystemExit, match=r"robots\.tsv:2: 1 tab-separated column"):
        main(["--root", str(tmp_path), "scan"])


@pytest.mark.blender
def test_doctor_reports_drift_without_running_the_importer(tmp_path, monkeypatch, capsys):
    # The probe only reports the environment. It has no use for the importer,
    # and must not execute one that doctor is about to report as drifted.
    marker = tmp_path / "importer-ran"
    drifted = tmp_path / "kinema_dae.py"
    drifted.write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('ran')\n",
                       encoding="utf-8")
    monkeypatch.setattr(meshkit._vendor, "VENDORED_FILE", drifted)

    assert main(["doctor"]) == 1
    out = capsys.readouterr().out
    assert "DIFFERS from the pinned copy" in out and "NOT ready" in out
    assert not marker.exists()
