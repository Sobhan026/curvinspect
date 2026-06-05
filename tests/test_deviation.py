import numpy as np

from curvinspect.deviation import (
    chord_deviation_signal,
    closed_tangents,
    deviation_signal,
    local_chord_deviation,
    normal_deviation,
    smooth_closed_curve,
)


def make_circle_points(radius: float = 10.0, n: int = 128) -> np.ndarray:
    angles = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    x = radius * np.cos(angles)
    y = radius * np.sin(angles)
    return np.column_stack([x, y])


def test_smooth_closed_curve_preserves_shape():
    points = make_circle_points()

    smoothed = smooth_closed_curve(points, window_size=9)

    assert smoothed.shape == points.shape
    assert np.all(np.isfinite(smoothed))


def test_closed_tangents_are_unit_vectors():
    points = make_circle_points()

    tangents = closed_tangents(points)
    lengths = np.linalg.norm(tangents, axis=1)

    assert np.allclose(lengths, 1.0)


def test_normal_deviation_returns_one_value_per_point():
    points = make_circle_points()

    deviations = normal_deviation(points, reference_window=9)

    assert deviations.shape == (len(points),)
    assert np.all(np.isfinite(deviations))


def test_deviation_signal_absolute_is_non_negative():
    points = make_circle_points()

    signal = deviation_signal(points, reference_window=9, mode="absolute")

    assert np.all(signal >= 0.0)


def test_local_indentation_has_large_deviation_near_indentation():
    n = 128
    angles = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    radii = np.full(n, 10.0)

    radii[:4] = 7.0
    radii[-4:] = 7.0

    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    points = np.column_stack([x, y])

    signal = deviation_signal(points, reference_window=15, mode="absolute")
    peak_index = int(np.argmax(signal))

    assert peak_index <= 6 or peak_index >= n - 6


def test_local_chord_deviation_returns_one_value_per_point():
    points = make_circle_points()

    deviations = local_chord_deviation(points, chord_step=7)

    assert deviations.shape == (len(points),)
    assert np.all(np.isfinite(deviations))


def test_chord_deviation_signal_absolute_is_non_negative():
    points = make_circle_points()

    signal = chord_deviation_signal(points, chord_step=7, mode="absolute")

    assert signal.shape == (len(points),)
    assert np.all(signal >= 0.0)


def test_local_chord_deviation_detects_local_bump():
    points = make_circle_points(radius=10.0, n=128)
    points[0] = np.array([14.0, 0.0])

    signal = chord_deviation_signal(points, chord_step=6, mode="absolute")
    peak_index = int(np.argmax(signal))

    assert peak_index == 0


def test_chord_deviation_signal_modes_have_expected_shapes():
    points = make_circle_points()

    signed = chord_deviation_signal(points, chord_step=7, mode="signed")
    absolute = chord_deviation_signal(points, chord_step=7, mode="absolute")
    positive = chord_deviation_signal(points, chord_step=7, mode="positive")
    negative = chord_deviation_signal(points, chord_step=7, mode="negative")

    assert signed.shape == absolute.shape == positive.shape == negative.shape
    assert np.allclose(absolute, positive + negative)