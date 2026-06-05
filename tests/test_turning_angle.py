import numpy as np

from curvinspect.curvature import discrete_curvature, signed_turning_angles


def test_left_turn_angle_is_positive_half_pi():
    points = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
        ]
    )

    angles = signed_turning_angles(points)

    assert np.isnan(angles[0])
    assert np.isclose(angles[1], np.pi / 2)
    assert np.isnan(angles[2])


def test_right_turn_angle_is_negative_half_pi():
    points = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, -1.0],
        ]
    )

    angles = signed_turning_angles(points)

    assert np.isclose(angles[1], -np.pi / 2)


def test_straight_line_has_zero_curvature():
    points = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [2.0, 0.0],
        ]
    )

    curvatures = discrete_curvature(points)

    assert np.isclose(curvatures[1], 0.0)