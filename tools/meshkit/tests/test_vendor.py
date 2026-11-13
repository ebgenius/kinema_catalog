from meshkit._vendor import importer_provenance


def test_vendored_importer_matches_pin():
    assert importer_provenance()["matches_pinned"], (
        "blender_side/kinema_dae.py changed: fix the importer in kinema and re-vendor "
        "from that commit")
