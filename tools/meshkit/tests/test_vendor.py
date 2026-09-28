from meshkit._vendor import PATCHES, VENDORED_FILE, importer_provenance


def test_vendored_importer_matches_pin():
    assert importer_provenance()["matches_pinned"], (
        "blender_side/kinema_dae.py changed: record the change as a patch and re-pin SHA256, "
        "or re-vendor from kinema")


def test_every_patch_is_in_the_tree():
    patches = VENDORED_FILE.parents[3] / "patches"
    for name in PATCHES:
        assert (patches / name).is_file(), name
