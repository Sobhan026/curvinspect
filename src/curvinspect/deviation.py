"""Contour deviation tools for closed polygonal curves."""

from __future__ import annotations

import numpy as np

from curvinspect.curvature import as_points

DEVIATION_SIGNAL_MODES = {
    "signed",
    "absolute",
    "positive",
    "negative",
}


def validate_odd_window_size(window_size: int) -> int:
    """Validate an odd smoothing window size."""
    if window_size < 1:
        raise ValueError("window_size must be positive.")

    if window_size % 2 == 0:
        raise ValueError("window_size must be odd.")

    return window_size


def validate_chord_step(chord_step: int, num_points: int) -> int:
    """Validate the half-window step used for local chord deviation."""
    if chord_step < 1:
        raise ValueError("chord_step must be positive.")

    if num_points < 3:
        raise ValueError("at least three points are required.")

    if 2 * chord_step >= num_points:
        raise ValueError("2 * chord_step must be smaller than the number of points.")

    return chord_step


def smooth_closed_curve(points: np.ndarray, *, window_size: int = 31) -> np.ndarray:
    """Smooth a closed polygonal curve using a circular moving average."""
    pts = as_points(points)
    window_size = validate_odd_window_size(window_size)

    if window_size == 1:
        return pts.copy()

    if window_size > len(pts):
        raise ValueError("window_size must not be larger than the number of points.")

    half_window = window_size // 2
    smoothed = np.zeros_like(pts, dtype=float)

    for offset in range(-half_window, half_window + 1):
        smoothed += np.roll(pts, shift=offset, axis=0)

    return smoothed / window_size


def closed_tangents(points: np.ndarray) -> np.ndarray:
    """Estimate unit tangent vectors on a closed polygonal curve."""
    pts = as_points(points)
    tangent_vectors = np.roll(pts, shift=-1, axis=0) - np.roll(pts, shift=1, axis=0)
    lengths = np.linalg.norm(tangent_vectors, axis=1)

    if np.any(lengths == 0):
        raise ValueError("zero-length tangent vectors are not allowed.")

    return tangent_vectors / lengths[:, None]


def left_normals_from_tangents(tangents: np.ndarray) -> np.ndarray:
    """Return left normal vectors from unit tangent vectors."""
    tangent_values = np.asarray(tangents, dtype=float)

    if tangent_values.ndim != 2 or tangent_values.shape[1] != 2:
        raise ValueError("tangents must have shape (n, 2).")

    return np.column_stack([-tangent_values[:, 1], tangent_values[:, 0]])


def normal_deviation(
    points: np.ndarray,
    *,
    reference_window: int = 31,
) -> np.ndarray:
    """Project contour displacement onto normals of a smoothed reference contour.

    The original contour is compared against a smoothed version of itself.
    This produces a signed normal-direction deviation signal. The sign depends
    on contour orientation, but the absolute value gives an orientation-neutral
    measure of local boundary deviation.
    """
    pts = as_points(points)
    reference = smooth_closed_curve(pts, window_size=reference_window)
    reference_tangents = closed_tangents(reference)
    reference_normals = left_normals_from_tangents(reference_tangents)

    displacement = pts - reference
    return np.sum(displacement * reference_normals, axis=1)


def local_chord_deviation(
    points: np.ndarray,
    *,
    chord_step: int = 15,
) -> np.ndarray:
    """Return signed local chord deviation for a closed polygonal curve.

    For each point p_i, this compares p_i with the chord connecting
    p_{i-k} and p_{i+k}. The signed value is the perpendicular distance
    from p_i to that local chord.

    This is a discrete, scale-dependent boundary irregularity measure.
    Large values indicate that a point deviates strongly from the local
    chord implied by its wider neighborhood.
    """
    pts = as_points(points)
    chord_step = validate_chord_step(chord_step, len(pts))

    left_points = np.roll(pts, shift=chord_step, axis=0)
    right_points = np.roll(pts, shift=-chord_step, axis=0)

    chord_vectors = right_points - left_points
    chord_lengths = np.linalg.norm(chord_vectors, axis=1)

    if np.any(chord_lengths == 0):
        raise ValueError("zero-length chord vectors are not allowed.")

    chord_unit_vectors = chord_vectors / chord_lengths[:, None]
    relative_points = pts - left_points

    signed_distances = (
        chord_unit_vectors[:, 0] * relative_points[:, 1]
        - chord_unit_vectors[:, 1] * relative_points[:, 0]
    )

    return signed_distances


def deviation_signal(
    points: np.ndarray,
    *,
    reference_window: int = 31,
    mode: str = "absolute",
) -> np.ndarray:
    """Return a deviation-derived signal for boundary irregularity detection.

    Modes:
        signed:
            Signed normal-direction deviation.

        absolute:
            Absolute normal-direction deviation.

        positive:
            Positive signed deviation only.

        negative:
            Magnitude of negative signed deviation only.
    """
    if mode not in DEVIATION_SIGNAL_MODES:
        valid_modes = ", ".join(sorted(DEVIATION_SIGNAL_MODES))
        raise ValueError(f"mode must be one of: {valid_modes}.")

    deviations = normal_deviation(points, reference_window=reference_window)

    if mode == "signed":
        return deviations

    if mode == "absolute":
        return np.abs(deviations)

    if mode == "positive":
        return np.maximum(deviations, 0.0)

    if mode == "negative":
        return np.maximum(-deviations, 0.0)

    raise ValueError(f"unsupported deviation signal mode: {mode}")


def chord_deviation_signal(
    points: np.ndarray,
    *,
    chord_step: int = 15,
    mode: str = "absolute",
) -> np.ndarray:
    """Return a local-chord deviation signal for boundary irregularity detection.

    Modes:
        signed:
            Signed local chord deviation.

        absolute:
            Absolute local chord deviation.

        positive:
            Positive signed chord deviation only.

        negative:
            Magnitude of negative signed chord deviation only.
    """
    if mode not in DEVIATION_SIGNAL_MODES:
        valid_modes = ", ".join(sorted(DEVIATION_SIGNAL_MODES))
        raise ValueError(f"mode must be one of: {valid_modes}.")

    deviations = local_chord_deviation(points, chord_step=chord_step)

    if mode == "signed":
        return deviations

    if mode == "absolute":
        return np.abs(deviations)

    if mode == "positive":
        return np.maximum(deviations, 0.0)

    if mode == "negative":
        return np.maximum(-deviations, 0.0)

    raise ValueError(f"unsupported chord deviation signal mode: {mode}")