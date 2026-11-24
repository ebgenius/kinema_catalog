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


def test_smoothed_normals_within_the_angle_pass():
    assert check_smoothed([3.0, 12.0, 21.0], 76.0, 30.0) == []


def test_smoothed_normals_beyond_the_angle_fail():
    (problem,) = check_smoothed([20.0, 35.0, 45.0], 80.0, 30.0)
    assert "p99 deviation from the face is 45.0 deg" in problem


def test_smoothed_normals_get_the_same_slack_as_kept_ones():
    assert check_smoothed([1.0, 2.0, 31.5], 40.0, 30.0) == []           # tolerance 2 deg
    assert check_smoothed([1.0, 2.0, 32.5], 40.0, 30.0) != []


def test_smoothed_normals_missing_fail():
    assert check_smoothed(None, None, 30.0) == ["normal deviation missing"]
