import numpy as np

from curvinspect.resampling import (
    arc_length,
    remove_consecutive_duplicates,
    resample_by_spacing,
    resample_polyline,
)


def test_open_line_resampling_has_uniform_points():
    points = np.array(
        [
            [0.0, 0.0],
            [10.0, 0.0],
        ]
    )

    resampled = resample_polyline(points, num_points=6)

    expected = np.array(
        [
            [0.0, 0.0],
            [2.0, 0.0],
            [4.0, 0.0],
            [6.0, 0.0],
            [8.0, 0.0],
            [10.0, 0.0],
        ]
    )

    assert np.allclose(resampled, expected)


def test_closed_square_arc_length_is_four():
    points = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
        ]
    )

    assert np.isclose(arc_length(points, closed=True), 4.0)


def test_closed_square_resampling_returns_corners_for_four_samples():
    points = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
        ]
    )

    resampled = resample_polyline(points, num_points=4, closed=True)

    assert np.allclose(resampled, points)


def test_resample_by_spacing_on_open_line():
    points = np.array(
        [
            [0.0, 0.0],
            [10.0, 0.0],
        ]
    )

    resampled = resample_by_spacing(points, spacing=2.5)

    assert len(resampled) == 5
    assert np.allclose(resampled[:, 0], [0.0, 2.5, 5.0, 7.5, 10.0])
    assert np.allclose(resampled[:, 1], 0.0)


def test_remove_consecutive_duplicates():
    points = np.array(
        [
            [0.0, 0.0],
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 0.0],
            [2.0, 0.0],
        ]
    )

    cleaned = remove_consecutive_duplicates(points)

    expected = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [2.0, 0.0],
        ]
    )

    assert np.allclose(cleaned, expected)