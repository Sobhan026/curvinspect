"""Signal smoothing utilities for curvature sequences."""

from __future__ import annotations

import numpy as np


def validate_signal(values: np.ndarray) -> np.ndarray:
    """Convert input data to a valid one-dimensional numeric signal."""
    arr = np.asarray(values, dtype=float)

    if arr.ndim != 1:
        raise ValueError("values must be a one-dimensional array.")

    if len(arr) == 0:
        raise ValueError("values must not be empty.")

    return arr


def validate_window_size(window_size: int) -> int:
    """Validate a centered smoothing window size."""
    if window_size < 1:
        raise ValueError("window_size must be positive.")

    if window_size % 2 == 0:
        raise ValueError("window_size must be odd.")

    return window_size


def moving_average(values: np.ndarray, window_size: int = 5) -> np.ndarray:
    """Apply a centered moving-average filter to a one-dimensional signal."""
    signal = validate_signal(values)
    window_size = validate_window_size(window_size)

    if window_size == 1:
        return signal.copy()

    half_window = window_size // 2
    smoothed = np.empty_like(signal, dtype=float)

    for index in range(len(signal)):
        start = max(0, index - half_window)
        end = min(len(signal), index + half_window + 1)

        window = signal[start:end]
        finite_values = window[np.isfinite(window)]

        if len(finite_values) == 0:
            smoothed[index] = np.nan
        else:
            smoothed[index] = float(np.mean(finite_values))

    return smoothed


def median_filter(values: np.ndarray, window_size: int = 5) -> np.ndarray:
    """Apply a centered median filter to a one-dimensional signal."""
    signal = validate_signal(values)
    window_size = validate_window_size(window_size)

    if window_size == 1:
        return signal.copy()

    half_window = window_size // 2
    filtered = np.empty_like(signal, dtype=float)

    for index in range(len(signal)):
        start = max(0, index - half_window)
        end = min(len(signal), index + half_window + 1)

        window = signal[start:end]
        finite_values = window[np.isfinite(window)]

        if len(finite_values) == 0:
            filtered[index] = np.nan
        else:
            filtered[index] = float(np.median(finite_values))

    return filtered