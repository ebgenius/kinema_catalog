"""Bad input to the command line is an error message, never a traceback."""

import pytest

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
