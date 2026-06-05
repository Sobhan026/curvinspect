"""Curvature-based anomaly detection utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AnomalyDetectionResult:
    """Result object returned by curvature anomaly detection."""

    indices: np.ndarray
    peak_indices: np.ndarray
    scores: np.ndarray
    threshold: float
    groups: list[tuple[int, int]]


def validate_curvature_signal(values: np.ndarray) -> np.ndarray:
    """Convert input data to a valid one-dimensional curvature signal."""
    arr = np.asarray(values, dtype=float)

    if arr.ndim != 1:
        raise ValueError("curvature values must be a one-dimensional array.")

    if len(arr) == 0:
        raise ValueError("curvature values must not be empty.")

    return arr


def robust_z_scores(values: np.ndarray, *, eps: float = 1e-12) -> np.ndarray:
    """Return robust z-scores based on the median absolute deviation."""
    signal = validate_curvature_signal(values)

    scores = np.full_like(signal, np.nan, dtype=float)
    valid_mask = np.isfinite(signal)

    if not np.any(valid_mask):
        return scores

    valid_values = signal[valid_mask]
    median = float(np.median(valid_values))
    mad = float(np.median(np.abs(valid_values - median)))

    if mad > eps:
        scores[valid_mask] = 0.67448975 * (valid_values - median) / mad
        return scores

    std = float(np.std(valid_values))

    if std > eps:
        mean = float(np.mean(valid_values))
        scores[valid_mask] = (valid_values - mean) / std
    else:
        scores[valid_mask] = 0.0

    return scores


def group_consecutive_indices(indices: np.ndarray) -> list[tuple[int, int]]:
    """Group consecutive integer indices into inclusive ranges."""
    idx = np.asarray(indices, dtype=int)

    if len(idx) == 0:
        return []

    idx = np.sort(idx)
    groups: list[tuple[int, int]] = []

    start = int(idx[0])
    previous = int(idx[0])

    for value in idx[1:]:
        current = int(value)

        if current == previous + 1:
            previous = current
            continue

        groups.append((start, previous))
        start = current
        previous = current

    groups.append((start, previous))
    return groups


def peak_indices_from_groups(
    groups: list[tuple[int, int]],
    scores: np.ndarray,
) -> np.ndarray:
    """Return one representative peak index for each anomaly group."""
    score_values = validate_curvature_signal(scores)

    peaks: list[int] = []

    for start, end in groups:
        if start < 0 or end >= len(score_values) or start > end:
            raise ValueError("invalid anomaly group range.")

        group_indices = np.arange(start, end + 1)
        group_scores = score_values[group_indices]

        if not np.any(np.isfinite(group_scores)):
            continue

        best_local_index = int(np.nanargmax(group_scores))
        peaks.append(int(group_indices[best_local_index]))

    return np.asarray(peaks, dtype=int)


def detect_curvature_anomalies(
    curvatures: np.ndarray,
    *,
    threshold: float = 3.5,
    min_abs_curvature: float | None = None,
) -> AnomalyDetectionResult:
    """Detect unusually high absolute curvature values."""
    curvature_values = validate_curvature_signal(curvatures)

    if threshold <= 0:
        raise ValueError("threshold must be positive.")

    absolute_curvature = np.abs(curvature_values)
    scores = robust_z_scores(absolute_curvature)

    mask = np.isfinite(scores) & (scores >= threshold)

    if min_abs_curvature is not None:
        if min_abs_curvature < 0:
            raise ValueError("min_abs_curvature must be non-negative.")

        mask &= absolute_curvature >= min_abs_curvature

    indices = np.where(mask)[0]
    groups = group_consecutive_indices(indices)
    peak_indices = peak_indices_from_groups(groups, scores)

    return AnomalyDetectionResult(
        indices=indices,
        peak_indices=peak_indices,
        scores=scores,
        threshold=threshold,
        groups=groups,
    )