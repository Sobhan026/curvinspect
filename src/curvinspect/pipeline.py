"""End-to-end CurvInspect analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from curvinspect.anomaly import AnomalyDetectionResult, detect_curvature_anomalies
from curvinspect.contour import ContourExtractionResult, extract_main_contour
from curvinspect.curvature import (
    bending_energy,
    curvature_signal,
    discrete_curvature,
    total_curvature,
)
from curvinspect.deviation import chord_deviation_signal, deviation_signal
from curvinspect.image_io import read_image
from curvinspect.report import build_analysis_report, save_json_report
from curvinspect.resampling import resample_polyline
from curvinspect.smoothing import median_filter, moving_average
from curvinspect.visualization import save_curvature_plot, save_debug_overlay, save_overlay

INSPECTION_SIGNAL_MODES = {
    "curvature",
    "deviation",
    "chord",
    "combined",
}


@dataclass(frozen=True)
class AnalysisResult:
    """Complete result returned by the analysis pipeline."""

    output_dir: Path
    contour: ContourExtractionResult
    analysis_points: np.ndarray
    resampled_points: np.ndarray
    curvatures: np.ndarray
    detection_signal: np.ndarray
    processed_curvatures: np.ndarray
    anomalies: AnomalyDetectionResult
    report: dict


def normalize_signal(signal: np.ndarray, *, eps: float = 1e-12) -> np.ndarray:
    """Normalize a signal to the range [0, 1] using its maximum absolute value."""
    signal_values = np.asarray(signal, dtype=float)
    normalized = np.zeros_like(signal_values, dtype=float)

    valid_mask = np.isfinite(signal_values)

    if not np.any(valid_mask):
        return normalized

    max_value = float(np.max(np.abs(signal_values[valid_mask])))

    if max_value <= eps:
        return normalized

    normalized[valid_mask] = signal_values[valid_mask] / max_value
    return normalized


def process_curvature_signal(
    signal: np.ndarray,
    *,
    smoothing: str = "median",
    window_size: int = 5,
) -> np.ndarray:
    """Apply optional smoothing to a curvature-derived detection signal."""
    signal_values = np.asarray(signal, dtype=float)

    if smoothing == "none":
        return signal_values.copy()

    if smoothing == "median":
        return median_filter(signal_values, window_size=window_size)

    if smoothing == "moving_average":
        return moving_average(signal_values, window_size=window_size)

    raise ValueError("smoothing must be one of: 'none', 'median', 'moving_average'.")


def select_analysis_points(
    contour: ContourExtractionResult,
    *,
    analysis_contour: str = "raw",
) -> np.ndarray:
    """Select the contour representation used for curvature analysis."""
    if analysis_contour == "raw":
        return contour.points

    if analysis_contour == "simplified":
        return contour.simplified_points

    raise ValueError("analysis_contour must be either 'raw' or 'simplified'.")


def build_detection_signal(
    points: np.ndarray,
    *,
    inspection_signal: str = "curvature",
    curvature_mode: str = "absolute",
    deviation_mode: str = "absolute",
    deviation_window: int = 31,
    chord_mode: str = "absolute",
    chord_step: int = 15,
) -> np.ndarray:
    """Build the signal used for anomaly detection."""
    if inspection_signal not in INSPECTION_SIGNAL_MODES:
        valid_modes = ", ".join(sorted(INSPECTION_SIGNAL_MODES))
        raise ValueError(f"inspection_signal must be one of: {valid_modes}.")

    curvature_values = curvature_signal(
        points,
        closed=True,
        mode=curvature_mode,
    )

    if inspection_signal == "curvature":
        return curvature_values

    deviation_values = deviation_signal(
        points,
        reference_window=deviation_window,
        mode=deviation_mode,
    )

    if inspection_signal == "deviation":
        return deviation_values

    chord_values = chord_deviation_signal(
        points,
        chord_step=chord_step,
        mode=chord_mode,
    )

    if inspection_signal == "chord":
        return chord_values

    normalized_curvature = normalize_signal(curvature_values)
    normalized_deviation = normalize_signal(deviation_values)
    normalized_chord = normalize_signal(chord_values)

    return np.maximum.reduce(
        [
            normalized_curvature,
            normalized_deviation,
            normalized_chord,
        ]
    )


def analyze_image(
    input_path: str | Path,
    output_dir: str | Path,
    *,
    contour_method: str = "threshold",
    analysis_contour: str = "raw",
    inspection_signal: str = "curvature",
    curvature_mode: str = "absolute",
    deviation_mode: str = "absolute",
    deviation_window: int = 31,
    chord_mode: str = "absolute",
    chord_step: int = 15,
    invert: bool = False,
    min_area: float = 25.0,
    epsilon_ratio: float = 0.005,
    num_samples: int = 300,
    smoothing: str = "median",
    smoothing_window: int = 5,
    anomaly_threshold: float = 3.5,
    min_abs_curvature: float | None = None,
) -> AnalysisResult:
    """Analyze an object image and export visual and JSON outputs."""
    if num_samples < 16:
        raise ValueError("num_samples must be at least 16.")

    image_path = Path(input_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    image = read_image(image_path)
    contour = extract_main_contour(
        image,
        method=contour_method,
        invert=invert,
        min_area=min_area,
        epsilon_ratio=epsilon_ratio,
    )

    analysis_points = select_analysis_points(
        contour,
        analysis_contour=analysis_contour,
    )

    resampled_points = resample_polyline(
        analysis_points,
        num_points=num_samples,
        closed=True,
    )

    curvatures = discrete_curvature(resampled_points, closed=True)
    detection_signal = build_detection_signal(
        resampled_points,
        inspection_signal=inspection_signal,
        curvature_mode=curvature_mode,
        deviation_mode=deviation_mode,
        deviation_window=deviation_window,
        chord_mode=chord_mode,
        chord_step=chord_step,
    )

    processed_curvatures = process_curvature_signal(
        detection_signal,
        smoothing=smoothing,
        window_size=smoothing_window,
    )

    anomalies = detect_curvature_anomalies(
        processed_curvatures,
        threshold=anomaly_threshold,
        min_abs_curvature=min_abs_curvature,
    )

    raw_anomaly_points = resampled_points[anomalies.indices]
    peak_anomaly_points = resampled_points[anomalies.peak_indices]

    overlay_path = output_path / "overlay.png"
    debug_overlay_path = output_path / "overlay_debug.png"
    plot_path = output_path / "curvature_signal.png"
    report_path = output_path / "anomaly_report.json"

    save_overlay(
        overlay_path,
        image,
        resampled_points,
        peak_anomaly_points,
    )

    save_debug_overlay(
        debug_overlay_path,
        image,
        resampled_points,
        raw_anomaly_points,
        peak_anomaly_points,
    )

    save_curvature_plot(
        plot_path,
        processed_curvatures,
        scores=anomalies.scores,
        anomaly_indices=anomalies.peak_indices,
        title="Boundary Inspection Signal",
    )

    abs_curvatures = np.abs(curvatures)
    report = build_analysis_report(
        input_path=str(image_path),
        image_shape=tuple(image.shape),
        contour_area=contour.area,
        contour_perimeter=contour.perimeter,
        num_original_points=len(contour.points),
        num_resampled_points=len(resampled_points),
        num_anomalies=len(anomalies.peak_indices),
        anomaly_indices=anomalies.indices,
        anomaly_peak_indices=anomalies.peak_indices,
        anomaly_groups=anomalies.groups,
        max_abs_curvature=float(np.max(abs_curvatures)),
        mean_abs_curvature=float(np.mean(abs_curvatures)),
        bending_energy=bending_energy(resampled_points, closed=True),
        total_curvature=total_curvature(resampled_points, closed=True),
        threshold=anomaly_threshold,
    )

    report["contour"]["analysis_contour"] = analysis_contour
    report["contour"]["num_analysis_points"] = len(analysis_points)

    report["curvature"]["mode"] = curvature_mode
    report["curvature"]["max_detection_signal"] = float(np.max(processed_curvatures))
    report["curvature"]["mean_detection_signal"] = float(np.mean(processed_curvatures))

    report["inspection"] = {
        "signal": inspection_signal,
        "curvature_mode": curvature_mode,
        "deviation_mode": deviation_mode,
        "deviation_window": deviation_window,
        "chord_mode": chord_mode,
        "chord_step": chord_step,
    }

    report["outputs"] = {
        "overlay": str(overlay_path),
        "debug_overlay": str(debug_overlay_path),
        "signal_plot": str(plot_path),
        "report": str(report_path),
    }

    save_json_report(report_path, report)

    return AnalysisResult(
        output_dir=output_path,
        contour=contour,
        analysis_points=analysis_points,
        resampled_points=resampled_points,
        curvatures=curvatures,
        detection_signal=detection_signal,
        processed_curvatures=processed_curvatures,
        anomalies=anomalies,
        report=report,
    )