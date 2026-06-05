"""Visualization utilities for CurvInspect."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from curvinspect.image_io import save_image


def ensure_color_image(image: np.ndarray) -> np.ndarray:
    """Return a BGR color image."""
    arr = np.asarray(image)

    if arr.ndim == 2:
        return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)

    if arr.ndim == 3 and arr.shape[2] == 3:
        return arr.copy()

    if arr.ndim == 3 and arr.shape[2] == 4:
        return cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)

    raise ValueError("image must be grayscale, BGR, or BGRA.")


def validate_point_array(points: np.ndarray, *, name: str) -> np.ndarray:
    """Validate and convert a point array to integer OpenCV coordinates."""
    point_array = np.asarray(points, dtype=np.int32)

    if point_array.ndim != 2 or point_array.shape[1] != 2:
        raise ValueError(f"{name} must have shape (n, 2).")

    return point_array


def draw_points(
    image: np.ndarray,
    points: np.ndarray,
    *,
    color: tuple[int, int, int],
    radius: int,
    thickness: int = -1,
) -> None:
    """Draw points on an image in-place."""
    point_array = validate_point_array(points, name="points")

    for point in point_array:
        cv2.circle(
            image,
            center=(int(point[0]), int(point[1])),
            radius=radius,
            color=color,
            thickness=thickness,
        )


def draw_analysis_overlay(
    image: np.ndarray,
    contour_points: np.ndarray,
    anomaly_points: np.ndarray | None = None,
    *,
    contour_color: tuple[int, int, int] = (0, 255, 255),
    anomaly_color: tuple[int, int, int] = (0, 0, 255),
    contour_thickness: int = 2,
    anomaly_radius: int = 6,
) -> np.ndarray:
    """Draw contour and representative anomaly points on top of an image."""
    output = ensure_color_image(image)

    contour = validate_point_array(contour_points, name="contour_points")

    cv2.polylines(
        output,
        [contour.reshape(-1, 1, 2)],
        isClosed=True,
        color=contour_color,
        thickness=contour_thickness,
    )

    if anomaly_points is not None and len(anomaly_points) > 0:
        draw_points(
            output,
            anomaly_points,
            color=anomaly_color,
            radius=anomaly_radius,
        )

    return output


def draw_debug_overlay(
    image: np.ndarray,
    contour_points: np.ndarray,
    raw_anomaly_points: np.ndarray | None = None,
    peak_anomaly_points: np.ndarray | None = None,
    *,
    contour_color: tuple[int, int, int] = (0, 255, 255),
    raw_anomaly_color: tuple[int, int, int] = (255, 0, 0),
    peak_anomaly_color: tuple[int, int, int] = (0, 0, 255),
    contour_thickness: int = 2,
    raw_radius: int = 3,
    peak_radius: int = 7,
) -> np.ndarray:
    """Draw a debug overlay with raw anomaly points and peak anomaly points.

    Raw anomaly points are all points that pass the anomaly threshold.
    Peak anomaly points are the representative points selected from each group.
    """
    output = ensure_color_image(image)

    contour = validate_point_array(contour_points, name="contour_points")

    cv2.polylines(
        output,
        [contour.reshape(-1, 1, 2)],
        isClosed=True,
        color=contour_color,
        thickness=contour_thickness,
    )

    if raw_anomaly_points is not None and len(raw_anomaly_points) > 0:
        draw_points(
            output,
            raw_anomaly_points,
            color=raw_anomaly_color,
            radius=raw_radius,
        )

    if peak_anomaly_points is not None and len(peak_anomaly_points) > 0:
        draw_points(
            output,
            peak_anomaly_points,
            color=peak_anomaly_color,
            radius=peak_radius,
        )

    return output


def save_overlay(
    path: str | Path,
    image: np.ndarray,
    contour_points: np.ndarray,
    anomaly_points: np.ndarray | None = None,
) -> None:
    """Save an overlay image with contour and representative anomaly markers."""
    overlay = draw_analysis_overlay(image, contour_points, anomaly_points)
    save_image(path, overlay)


def save_debug_overlay(
    path: str | Path,
    image: np.ndarray,
    contour_points: np.ndarray,
    raw_anomaly_points: np.ndarray | None = None,
    peak_anomaly_points: np.ndarray | None = None,
) -> None:
    """Save a debug overlay showing raw and representative anomaly markers."""
    overlay = draw_debug_overlay(
        image,
        contour_points,
        raw_anomaly_points,
        peak_anomaly_points,
    )
    save_image(path, overlay)


def save_curvature_plot(
    path: str | Path,
    curvatures: np.ndarray,
    scores: np.ndarray | None = None,
    anomaly_indices: np.ndarray | None = None,
    *,
    title: str = "Discrete Curvature Signal",
) -> None:
    """Save a curvature signal plot."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    curvature_values = np.asarray(curvatures, dtype=float)
    x_values = np.arange(len(curvature_values))

    figure = Figure(figsize=(12, 5))
    FigureCanvasAgg(figure)

    axis = figure.subplots()
    axis.plot(x_values, curvature_values, linewidth=1.8, label="Curvature")

    if scores is not None:
        score_values = np.asarray(scores, dtype=float)
        finite_scores = score_values[np.isfinite(score_values)]

        if len(finite_scores) > 0:
            scaled_scores = score_values / max(np.max(np.abs(finite_scores)), 1e-12)
            scaled_scores *= max(np.max(np.abs(curvature_values)), 1e-12)
            axis.plot(
                x_values,
                scaled_scores,
                linewidth=1.2,
                linestyle="--",
                label="Scaled anomaly score",
            )

    if anomaly_indices is not None and len(anomaly_indices) > 0:
        indices = np.asarray(anomaly_indices, dtype=int)
        axis.scatter(
            indices,
            curvature_values[indices],
            s=45,
            marker="x",
            label="Detected anomalies",
        )

    axis.set_title(title)
    axis.set_xlabel("Boundary vertex index")
    axis.set_ylabel("Discrete curvature")
    axis.grid(True, alpha=0.35)
    axis.legend()

    figure.tight_layout()
    figure.savefig(output_path, dpi=160)