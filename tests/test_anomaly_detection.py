import numpy as np

from curvinspect.anomaly import (
    detect_curvature_anomalies,
    group_consecutive_indices,
    peak_indices_from_groups,
    robust_z_scores,
)


def test_robust_z_scores_are_zero_for_constant_signal():
    signal = np.array([2.0, 2.0, 2.0, 2.0])

    scores = robust_z_scores(signal)

    assert np.allclose(scores, 0.0)


def test_detects_single_positive_curvature_spike():
    curvatures = np.array([0.05, 0.06, 0.04, 3.0, 0.05, 0.04, 0.06])

    result = detect_curvature_anomalies(curvatures, threshold=3.5)

    assert result.indices.tolist() == [3]
    assert result.peak_indices.tolist() == [3]
    assert result.groups == [(3, 3)]


def test_detects_single_negative_curvature_spike_using_absolute_curvature():
    curvatures = np.array([0.05, 0.06, 0.04, -3.0, 0.05, 0.04, 0.06])

    result = detect_curvature_anomalies(curvatures, threshold=3.5)

    assert result.indices.tolist() == [3]
    assert result.peak_indices.tolist() == [3]


def test_min_abs_curvature_can_filter_small_statistical_outliers():
    curvatures = np.array([0.01, 0.02, 0.01, 0.15, 0.01, 0.02, 0.01])

    result = detect_curvature_anomalies(
        curvatures,
        threshold=3.5,
        min_abs_curvature=0.5,
    )

    assert result.indices.tolist() == []
    assert result.peak_indices.tolist() == []


def test_group_consecutive_indices():
    indices = np.array([2, 3, 4, 8, 10, 11])

    groups = group_consecutive_indices(indices)

    assert groups == [(2, 4), (8, 8), (10, 11)]


def test_peak_indices_from_groups():
    scores = np.array([0.0, 1.0, 5.0, 3.0, 0.0, 2.0, 7.0, 1.0])
    groups = [(1, 3), (5, 7)]

    peaks = peak_indices_from_groups(groups, scores)

    assert peaks.tolist() == [2, 6]


def test_detects_peak_for_wide_anomaly_region():
    curvatures = np.array([0.05, 0.05, 1.5, 2.5, 1.8, 0.05, 0.05])

    result = detect_curvature_anomalies(curvatures, threshold=0.6)

    assert result.groups == [(2, 4)]
    assert result.peak_indices.tolist() == [3]