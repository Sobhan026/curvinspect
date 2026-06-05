import numpy as np

from curvinspect.smoothing import median_filter, moving_average


def test_moving_average_smooths_center_spike():
    signal = np.array([0.0, 0.0, 9.0, 0.0, 0.0])

    smoothed = moving_average(signal, window_size=3)

    assert np.isclose(smoothed[2], 3.0)


def test_median_filter_removes_single_spike():
    signal = np.array([0.0, 0.0, 9.0, 0.0, 0.0])

    filtered = median_filter(signal, window_size=3)

    assert np.isclose(filtered[2], 0.0)


def test_window_size_must_be_odd():
    signal = np.array([1.0, 2.0, 3.0])

    try:
        moving_average(signal, window_size=2)
    except ValueError as exc:
        assert "window_size must be odd" in str(exc)
    else:
        raise AssertionError("Expected ValueError for even window_size.")