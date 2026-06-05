"""JSON report utilities for CurvInspect analysis results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


def to_serializable(value: Any) -> Any:
    """Convert NumPy values to JSON-serializable Python objects."""
    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    if isinstance(value, dict):
        return {key: to_serializable(item) for key, item in value.items()}

    if isinstance(value, list | tuple):
        return [to_serializable(item) for item in value]

    return value


def save_json_report(path: str | Path, data: dict[str, Any]) -> None:
    """Save an analysis report as a JSON file."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    serializable_data = to_serializable(data)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(serializable_data, file, indent=2)


def build_analysis_report(
    *,
    input_path: str,
    image_shape: tuple[int, ...],
    contour_area: float,
    contour_perimeter: float,
    num_original_points: int,
    num_resampled_points: int,
    num_anomalies: int,
    anomaly_indices: np.ndarray,
    anomaly_peak_indices: np.ndarray,
    anomaly_groups: list[tuple[int, int]],
    max_abs_curvature: float,
    mean_abs_curvature: float,
    bending_energy: float,
    total_curvature: float,
    threshold: float,
) -> dict[str, Any]:
    """Build a structured analysis report dictionary."""
    return {
        "input": {
            "path": input_path,
            "image_shape": image_shape,
        },
        "contour": {
            "area": contour_area,
            "perimeter": contour_perimeter,
            "num_original_points": num_original_points,
            "num_resampled_points": num_resampled_points,
        },
        "curvature": {
            "max_abs_curvature": max_abs_curvature,
            "mean_abs_curvature": mean_abs_curvature,
            "total_curvature": total_curvature,
            "bending_energy": bending_energy,
        },
        "anomalies": {
            "threshold": threshold,
            "count": num_anomalies,
            "indices": anomaly_indices,
            "peak_indices": anomaly_peak_indices,
            "groups": anomaly_groups,
        },
    }