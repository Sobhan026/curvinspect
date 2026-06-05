"""Uniform resampling tools for polygonal curves."""

from __future__ import annotations

import numpy as np


def validate_points(points: np.ndarray, *, min_points: int = 2) -> np.ndarray:
    """Convert input data to a valid array of 2D points."""
    arr = np.asarray(points, dtype=float)

    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError("points must be a 2D array with shape (n, 2).")

    if len(arr) < min_points:
        raise ValueError(f"at least {min_points} points are required.")

    if not np.all(np.isfinite(arr)):
        raise ValueError("points must contain only finite values.")

    return arr


def remove_consecutive_duplicates(
    points: np.ndarray,
    *,
    closed: bool = False,
    tolerance: float = 1e-12,
) -> np.ndarray:
    """Remove consecutive duplicate points from a polyline."""
    pts = validate_points(points)

    keep = np.ones(len(pts), dtype=bool)
    diffs = np.linalg.norm(pts[1:] - pts[:-1], axis=1)
    keep[1:] = diffs > tolerance

    cleaned = pts[keep]

    if closed and len(cleaned) > 1:
        if np.linalg.norm(cleaned[0] - cleaned[-1]) <= tolerance:
            cleaned = cleaned[:-1]

    min_points = 3 if closed else 2
    if len(cleaned) < min_points:
        raise ValueError(f"at least {min_points} unique points are required.")

    return cleaned


def arc_length(points: np.ndarray, *, closed: bool = False) -> float:
    """Return the total arc length of a polygonal curve."""
    pts = remove_consecutive_duplicates(points, closed=closed)

    if closed:
        path = np.vstack([pts, pts[0]])
    else:
        path = pts

    segment_lengths = np.linalg.norm(path[1:] - path[:-1], axis=1)
    return float(np.sum(segment_lengths))


def resample_polyline(
    points: np.ndarray,
    num_points: int,
    *,
    closed: bool = False,
) -> np.ndarray:
    """Resample a polygonal curve using equally spaced arc-length samples."""
    min_points = 3 if closed else 2

    if num_points < min_points:
        raise ValueError(f"num_points must be at least {min_points}.")

    pts = remove_consecutive_duplicates(points, closed=closed)

    if closed:
        path = np.vstack([pts, pts[0]])
    else:
        path = pts

    segments = path[1:] - path[:-1]
    segment_lengths = np.linalg.norm(segments, axis=1)

    if np.any(segment_lengths == 0):
        raise ValueError("zero-length segments are not allowed.")

    cumulative = np.concatenate([[0.0], np.cumsum(segment_lengths)])
    total_length = cumulative[-1]

    if total_length == 0:
        raise ValueError("total arc length must be positive.")

    target_distances = np.linspace(
        0.0,
        total_length,
        num_points,
        endpoint=not closed,
    )

    segment_indices = np.searchsorted(cumulative, target_distances, side="right") - 1
    segment_indices = np.clip(segment_indices, 0, len(segment_lengths) - 1)

    local_distances = target_distances - cumulative[segment_indices]
    local_parameters = local_distances / segment_lengths[segment_indices]

    start_points = path[segment_indices]
    segment_vectors = segments[segment_indices]

    return start_points + local_parameters[:, None] * segment_vectors


def resample_by_spacing(
    points: np.ndarray,
    spacing: float,
    *,
    closed: bool = False,
) -> np.ndarray:
    """Resample a polygonal curve using an approximate target spacing."""
    if spacing <= 0:
        raise ValueError("spacing must be positive.")

    total_length = arc_length(points, closed=closed)

    if closed:
        num_points = max(3, int(np.ceil(total_length / spacing)))
    else:
        num_segments = max(1, int(np.ceil(total_length / spacing)))
        num_points = num_segments + 1

    return resample_polyline(points, num_points, closed=closed)