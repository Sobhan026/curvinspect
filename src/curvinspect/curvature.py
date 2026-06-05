"""Discrete curvature tools for planar polygonal curves."""

from __future__ import annotations

import numpy as np

CURVATURE_SIGNAL_MODES = {
    "signed",
    "absolute",
    "positive",
    "negative",
    "convex",
    "concave",
}


def as_points(points: np.ndarray) -> np.ndarray:
    """Convert input data to a valid array of 2D points."""
    arr = np.asarray(points, dtype=float)

    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError("points must be a 2D array with shape (n, 2).")

    if len(arr) < 3:
        raise ValueError("at least three points are required.")

    if not np.all(np.isfinite(arr)):
        raise ValueError("points must contain only finite values.")

    return arr


def edge_vectors(points: np.ndarray, *, closed: bool = False) -> np.ndarray:
    """Return edge vectors of a polygonal curve."""
    pts = as_points(points)

    if closed:
        next_pts = np.roll(pts, shift=-1, axis=0)
        return next_pts - pts

    return pts[1:] - pts[:-1]


def edge_lengths(points: np.ndarray, *, closed: bool = False) -> np.ndarray:
    """Return Euclidean lengths of the edge vectors."""
    edges = edge_vectors(points, closed=closed)
    return np.linalg.norm(edges, axis=1)


def unit_tangents(points: np.ndarray, *, closed: bool = False) -> np.ndarray:
    """Return unit tangent vectors along the edges."""
    edges = edge_vectors(points, closed=closed)
    lengths = np.linalg.norm(edges, axis=1)

    if np.any(lengths == 0):
        raise ValueError("zero-length edges are not allowed.")

    return edges / lengths[:, None]


def signed_turning_angles(points: np.ndarray, *, closed: bool = False) -> np.ndarray:
    """Return signed turning angles at polygon vertices.

    For an open polyline, endpoint angles are returned as NaN because the
    turning angle is only defined at internal vertices.

    For a closed polygon, one signed turning angle is returned for every vertex.
    Positive values correspond to counterclockwise turns in the coordinate
    system used by the input points.
    """
    pts = as_points(points)

    if closed:
        prev_edges = pts - np.roll(pts, shift=1, axis=0)
        next_edges = np.roll(pts, shift=-1, axis=0) - pts

        prev_lengths = np.linalg.norm(prev_edges, axis=1)
        next_lengths = np.linalg.norm(next_edges, axis=1)

        if np.any(prev_lengths == 0) or np.any(next_lengths == 0):
            raise ValueError("zero-length edges are not allowed.")

        prev_tangents = prev_edges / prev_lengths[:, None]
        next_tangents = next_edges / next_lengths[:, None]

        dots = np.sum(prev_tangents * next_tangents, axis=1)
        dets = (
            prev_tangents[:, 0] * next_tangents[:, 1]
            - prev_tangents[:, 1] * next_tangents[:, 0]
        )

        return np.arctan2(dets, dots)

    angles = np.full(len(pts), np.nan, dtype=float)

    prev_edges = pts[1:-1] - pts[:-2]
    next_edges = pts[2:] - pts[1:-1]

    prev_lengths = np.linalg.norm(prev_edges, axis=1)
    next_lengths = np.linalg.norm(next_edges, axis=1)

    if np.any(prev_lengths == 0) or np.any(next_lengths == 0):
        raise ValueError("zero-length edges are not allowed.")

    prev_tangents = prev_edges / prev_lengths[:, None]
    next_tangents = next_edges / next_lengths[:, None]

    dots = np.sum(prev_tangents * next_tangents, axis=1)
    dets = (
        prev_tangents[:, 0] * next_tangents[:, 1]
        - prev_tangents[:, 1] * next_tangents[:, 0]
    )

    angles[1:-1] = np.arctan2(dets, dots)
    return angles


def local_arc_lengths(points: np.ndarray, *, closed: bool = False) -> np.ndarray:
    """Return local arc-length scale around each vertex."""
    pts = as_points(points)

    if closed:
        prev_edges = pts - np.roll(pts, shift=1, axis=0)
        next_edges = np.roll(pts, shift=-1, axis=0) - pts

        prev_lengths = np.linalg.norm(prev_edges, axis=1)
        next_lengths = np.linalg.norm(next_edges, axis=1)

        if np.any(prev_lengths == 0) or np.any(next_lengths == 0):
            raise ValueError("zero-length edges are not allowed.")

        return 0.5 * (prev_lengths + next_lengths)

    scales = np.full(len(pts), np.nan, dtype=float)

    prev_edges = pts[1:-1] - pts[:-2]
    next_edges = pts[2:] - pts[1:-1]

    prev_lengths = np.linalg.norm(prev_edges, axis=1)
    next_lengths = np.linalg.norm(next_edges, axis=1)

    if np.any(prev_lengths == 0) or np.any(next_lengths == 0):
        raise ValueError("zero-length edges are not allowed.")

    scales[1:-1] = 0.5 * (prev_lengths + next_lengths)
    return scales


def discrete_curvature(
    points: np.ndarray,
    *,
    closed: bool = False,
    absolute: bool = False,
) -> np.ndarray:
    """Return discrete curvature values at polygon vertices."""
    angles = signed_turning_angles(points, closed=closed)
    scales = local_arc_lengths(points, closed=closed)

    curvature = angles / scales

    if absolute:
        return np.abs(curvature)

    return curvature


def total_signed_turning(points: np.ndarray, *, closed: bool = True) -> float:
    """Return the total signed turning angle of a polygonal curve."""
    angles = signed_turning_angles(points, closed=closed)
    return float(np.nansum(angles))


def total_curvature(points: np.ndarray, *, closed: bool = False) -> float:
    """Return total curvature as the sum of absolute turning angles."""
    angles = signed_turning_angles(points, closed=closed)
    return float(np.nansum(np.abs(angles)))


def dominant_turning_sign(points: np.ndarray, *, eps: float = 1e-12) -> float:
    """Return the dominant turning sign of a closed polygonal curve.

    Convex vertices of a simple closed contour usually share the same sign.
    Concave vertices usually have the opposite sign. This helper is used to
    normalize curvature signs before extracting convex or concave signals.
    """
    total_turning = total_signed_turning(points, closed=True)

    if abs(total_turning) <= eps:
        return 1.0

    return float(np.sign(total_turning))


def orientation_normalized_curvature(points: np.ndarray) -> np.ndarray:
    """Return signed curvature normalized by the contour's dominant orientation.

    After normalization, convex turns tend to be positive and concave turns
    tend to be negative for simple closed contours.
    """
    curvatures = discrete_curvature(points, closed=True)
    sign = dominant_turning_sign(points)
    return sign * curvatures


def positive_part(values: np.ndarray) -> np.ndarray:
    """Return the positive part of a numeric signal."""
    arr = np.asarray(values, dtype=float)
    return np.maximum(arr, 0.0)


def negative_part(values: np.ndarray) -> np.ndarray:
    """Return the magnitude of the negative part of a numeric signal."""
    arr = np.asarray(values, dtype=float)
    return np.maximum(-arr, 0.0)


def curvature_signal(
    points: np.ndarray,
    *,
    closed: bool = True,
    mode: str = "absolute",
) -> np.ndarray:
    """Return a curvature-derived signal for detection.

    Modes:
        signed:
            Raw signed discrete curvature.

        absolute:
            Absolute discrete curvature.

        positive:
            Positive signed curvature only.

        negative:
            Magnitude of negative signed curvature only.

        convex:
            Convex curvature signal for a closed contour.

        concave:
            Concave curvature signal for a closed contour.
    """
    if mode not in CURVATURE_SIGNAL_MODES:
        valid_modes = ", ".join(sorted(CURVATURE_SIGNAL_MODES))
        raise ValueError(f"mode must be one of: {valid_modes}.")

    curvatures = discrete_curvature(points, closed=closed)

    if mode == "signed":
        return curvatures

    if mode == "absolute":
        return np.abs(curvatures)

    if mode == "positive":
        return positive_part(curvatures)

    if mode == "negative":
        return negative_part(curvatures)

    if not closed:
        raise ValueError("'convex' and 'concave' modes require a closed contour.")

    normalized = orientation_normalized_curvature(points)

    if mode == "convex":
        return positive_part(normalized)

    if mode == "concave":
        return negative_part(normalized)

    raise ValueError(f"unsupported curvature signal mode: {mode}")


def bending_energy(points: np.ndarray, *, closed: bool = False) -> float:
    """Return a discrete bending energy approximation."""
    curvatures = discrete_curvature(points, closed=closed)
    scales = local_arc_lengths(points, closed=closed)

    valid = np.isfinite(curvatures) & np.isfinite(scales)
    return float(np.sum((curvatures[valid] ** 2) * scales[valid]))