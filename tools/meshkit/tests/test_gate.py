import pytest

from meshkit.gate import Tolerance, check_smoothed, compare, compare_normals

SOURCE = {"triangles": 100, "area": 2.0, "centroid": [0.0, 0.0, 0.5],
          "aabb_min": [-0.5, -0.5, 0.0], "aabb_max": [0.5, 0.5, 1.0]}


def moved(**changes):
    return {**SOURCE, **changes}


def test_identical_passes():
    assert compare(SOURCE, dict(SOURCE)) == []


def test_triangle_count_is_exact():
    assert any("triangle count" in p for p in compare(SOURCE, moved(triangles=99)))


def test_area_is_relative():
    assert compare(SOURCE, moved(area=2.0 * (1 + 5e-5))) == []
    assert any("surface area" in p for p in compare(SOURCE, moved(area=2.002)))


def test_lost_unit_scale_fails():
    problems = compare(SOURCE, moved(area=2.0e6))
    assert any("surface area" in p for p in problems)


def test_lost_node_transform_fails_on_position_only():
    # The OBJ failure: same triangles, same area, wrong place.
    shifted = moved(centroid=[0.0, 0.0, 0.692], aabb_min=[-0.5, -0.5, 0.192],
                    aabb_max=[0.5, 0.5, 1.192])
    problems = compare(SOURCE, shifted)
    assert problems and all("moved by" in p for p in problems)
    assert compare(SOURCE, shifted, check_frame=False) == []


def test_position_tolerance_scales_with_the_mesh():
    diagonal = 3 ** 0.5
    nudge = 0.5 * Tolerance().position * diagonal
    assert compare(SOURCE, moved(centroid=[nudge, 0.0, 0.5])) == []


def test_normals_within_tolerance():
    assert compare_normals([0.0, 0.1, 0.3], [0.0, 0.2, 1.1]) == []


def test_averaged_normals_fail():
    # finger.dae through kinema's importer before #126: flat faces became smooth.
    problems = compare_normals([0.0, 0.02, 0.03], [42.9, 61.4, 82.4])
    assert len(problems) == 3


def test_missing_normals_fail():
    assert compare_normals(None, [0.0, 0.0, 0.0])


def smoothing(p99_9=0.3, corners=1000, unchecked=20):
    return {"p99_9": p99_9, "max": p99_9, "corners": corners, "unchecked": unchecked,
            "ambiguous_edges": 0}


def test_normals_that_smoothing_makes_pass():
    assert check_smoothed(smoothing(), 30.0) == []


def test_normals_away_from_what_smoothing_makes_fail():
    (problem,) = check_smoothed(smoothing(p99_9=5.6), 30.0)
    assert problem == ("normals: p99.9 corner is 5.6 deg from what smoothing at 30 deg "
                       "makes (limit 2)")


def test_the_normals_tolerance_is_the_limit():
    assert check_smoothed(smoothing(p99_9=1.9), 30.0) == []
    assert check_smoothed(smoothing(p99_9=2.1), 30.0) != []
    assert check_smoothed(smoothing(p99_9=2.1), 30.0, Tolerance(normals=3.0)) == []


def test_a_mesh_mostly_unchecked_fails():
    (problem,) = check_smoothed(smoothing(corners=400, unchecked=600), 30.0)
    assert "only 40% of corners could be checked" in problem


@pytest.mark.parametrize("measured", [
    None, {}, smoothing(p99_9=None), smoothing(corners=0),
])
def test_smoothing_unmeasured_fails(measured):
    assert check_smoothed(measured, 30.0) == [
        "normals: no corner could be checked against smoothing by angle"]
