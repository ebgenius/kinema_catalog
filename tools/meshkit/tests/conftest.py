import pytest

from meshkit.blender import BlenderNotFound, find_blender


@pytest.fixture(scope="session")
def blender():
    try:
        return find_blender()
    except BlenderNotFound as exc:
        pytest.skip(f"no Blender 5.2+: {exc}")


def pytest_collection_modifyitems(config, items):
    # A `blender` test without the fixture would run and fail on a machine
    # without Blender; make the marker imply the fixture.
    for item in items:
        if item.get_closest_marker("blender") and "blender" not in item.fixturenames:
            item.fixturenames.append("blender")
