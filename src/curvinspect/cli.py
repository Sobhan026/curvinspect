"""Command-line interface for CurvInspect."""

from __future__ import annotations

import argparse
from pathlib import Path

from curvinspect.demo import save_demo_summary
from curvinspect.pipeline import analyze_image
from curvinspect.synthetic import save_demo_images

CURVATURE_MODE_CHOICES = [
    "signed",
    "absolute",
    "positive",
    "negative",
    "convex",
    "concave",
]

INSPECTION_SIGNAL_CHOICES = [
    "curvature",
    "deviation",
    "chord",
    "combined",
]

DEVIATION_MODE_CHOICES = [
    "signed",
    "absolute",
    "positive",
    "negative",
]

BASE_ANALYSIS_OPTIONS = {
    "method": "threshold",
    "analysis_contour": "raw",
    "inspection_signal": "curvature",
    "curvature_mode": "absolute",
    "deviation_mode": "absolute",
    "deviation_window": 31,
    "chord_mode": "absolute",
    "chord_step": 15,
    "invert": False,
    "min_area": 25.0,
    "epsilon_ratio": 0.005,
    "num_samples": 300,
    "smoothing": "median",
    "smoothing_window": 5,
    "threshold": 3.5,
    "min_abs_curvature": None,
}

DEMO_DEFAULT_OVERRIDES = {
    "smoothing": "none",
    "threshold": 1.5,
}

PRESET_CONFIGS = {
    "general-curvature": {
        "inspection_signal": "curvature",
        "curvature_mode": "absolute",
        "analysis_contour": "raw",
        "num_samples": 300,
        "smoothing": "median",
        "smoothing_window": 5,
        "threshold": 3.5,
    },
    "smooth-shape": {
        "inspection_signal": "curvature",
        "curvature_mode": "absolute",
        "analysis_contour": "raw",
        "num_samples": 400,
        "smoothing": "median",
        "smoothing_window": 9,
        "threshold": 3.0,
    },
    "clean-simplified": {
        "inspection_signal": "curvature",
        "curvature_mode": "absolute",
        "analysis_contour": "simplified",
        "epsilon_ratio": 0.01,
        "num_samples": 500,
        "smoothing": "median",
        "smoothing_window": 5,
        "threshold": 2.0,
    },
    "concave-notch": {
        "inspection_signal": "curvature",
        "curvature_mode": "concave",
        "analysis_contour": "simplified",
        "epsilon_ratio": 0.005,
        "num_samples": 500,
        "smoothing": "median",
        "smoothing_window": 3,
        "threshold": 1.3,
    },
    "industrial-chord": {
        "inspection_signal": "chord",
        "chord_mode": "absolute",
        "analysis_contour": "raw",
        "chord_step": 25,
        "num_samples": 700,
        "smoothing": "median",
        "smoothing_window": 11,
        "threshold": 1.9,
    },
    "industrial-chord-strict": {
        "inspection_signal": "chord",
        "chord_mode": "absolute",
        "analysis_contour": "raw",
        "chord_step": 35,
        "num_samples": 700,
        "smoothing": "median",
        "smoothing_window": 11,
        "threshold": 2.2,
    },
    "sensitive-chord": {
        "inspection_signal": "chord",
        "chord_mode": "absolute",
        "analysis_contour": "raw",
        "chord_step": 15,
        "num_samples": 700,
        "smoothing": "median",
        "smoothing_window": 7,
        "threshold": 1.4,
    },
    "industrial-combined": {
        "inspection_signal": "combined",
        "curvature_mode": "absolute",
        "deviation_mode": "absolute",
        "chord_mode": "absolute",
        "analysis_contour": "raw",
        "deviation_window": 91,
        "chord_step": 25,
        "num_samples": 700,
        "smoothing": "median",
        "smoothing_window": 11,
        "threshold": 1.8,
    },
}

PRESET_CHOICES = sorted(PRESET_CONFIGS)

ANALYSIS_OPTION_KEYS = [
    "method",
    "analysis_contour",
    "inspection_signal",
    "curvature_mode",
    "deviation_mode",
    "deviation_window",
    "chord_mode",
    "chord_step",
    "invert",
    "min_area",
    "epsilon_ratio",
    "num_samples",
    "smoothing",
    "smoothing_window",
    "threshold",
    "min_abs_curvature",
]


def add_shared_analysis_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments shared by analyze and demo commands."""
    parser.add_argument(
        "--preset",
        choices=PRESET_CHOICES,
        default=None,
        help="Named starting configuration. Explicit CLI options override the preset.",
    )

    parser.add_argument(
        "--analysis-contour",
        choices=["raw", "simplified"],
        default=None,
        help="Contour representation used for boundary analysis.",
    )

    parser.add_argument(
        "--inspection-signal",
        choices=INSPECTION_SIGNAL_CHOICES,
        default=None,
        help="Signal used for anomaly detection.",
    )

    parser.add_argument(
        "--curvature-mode",
        choices=CURVATURE_MODE_CHOICES,
        default=None,
        help="Curvature-derived signal used when inspection signal uses curvature.",
    )

    parser.add_argument(
        "--deviation-mode",
        choices=DEVIATION_MODE_CHOICES,
        default=None,
        help="Deviation-derived signal used when inspection signal uses deviation.",
    )

    parser.add_argument(
        "--deviation-window",
        type=int,
        default=None,
        help="Odd smoothing window used to build the reference contour for deviation.",
    )

    parser.add_argument(
        "--chord-mode",
        choices=DEVIATION_MODE_CHOICES,
        default=None,
        help="Chord-deviation signal mode.",
    )

    parser.add_argument(
        "--chord-step",
        type=int,
        default=None,
        help="Half-window step used for local chord deviation.",
    )

    parser.add_argument(
        "--num-samples",
        type=int,
        default=None,
        help="Number of uniformly resampled boundary points.",
    )

    parser.add_argument(
        "--smoothing",
        choices=["none", "median", "moving_average"],
        default=None,
        help="Detection signal smoothing method.",
    )

    parser.add_argument(
        "--smoothing-window",
        type=int,
        default=None,
        help="Odd window size used by the smoothing filter.",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Robust z-score threshold for anomaly detection.",
    )


def resolve_analysis_options(
    args: argparse.Namespace,
    *,
    command: str,
) -> dict:
    """Resolve base defaults, preset values, and explicit CLI overrides."""
    options = dict(BASE_ANALYSIS_OPTIONS)

    if command == "demo":
        options.update(DEMO_DEFAULT_OVERRIDES)

    if args.preset is not None:
        options.update(PRESET_CONFIGS[args.preset])

    for key in ANALYSIS_OPTION_KEYS:
        value = getattr(args, key, None)
        if value is not None:
            options[key] = value

    return options


def build_analyze_kwargs(options: dict) -> dict:
    """Convert resolved CLI options into analyze_image keyword arguments."""
    kwargs = dict(options)
    kwargs["contour_method"] = kwargs.pop("method")
    kwargs["anomaly_threshold"] = kwargs.pop("threshold")
    return kwargs


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="curvinspect",
        description="Analyze object boundaries using discrete curvature.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze one image and export overlay, signal plot, and JSON report.",
    )

    analyze_parser.add_argument(
        "image",
        type=Path,
        help="Path to the input image.",
    )

    analyze_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("examples/output"),
        help="Output directory.",
    )

    analyze_parser.add_argument(
        "--method",
        choices=["threshold", "canny"],
        default=None,
        help="Contour extraction method.",
    )

    add_shared_analysis_arguments(analyze_parser)

    analyze_parser.add_argument(
        "--invert",
        action="store_true",
        default=None,
        help="Invert the thresholded image before contour extraction.",
    )

    analyze_parser.add_argument(
        "--min-abs-curvature",
        type=float,
        default=None,
        help="Optional minimum detection signal value required for anomaly detection.",
    )

    analyze_parser.add_argument(
        "--epsilon-ratio",
        type=float,
        default=None,
        help="Contour simplification ratio used for metadata extraction.",
    )

    analyze_parser.add_argument(
        "--min-area",
        type=float,
        default=None,
        help="Minimum area required for the selected contour.",
    )

    demo_parser = subparsers.add_parser(
        "demo",
        help="Generate synthetic demo images and analyze them.",
    )

    demo_parser.add_argument(
        "--image-output",
        type=Path,
        default=Path("examples/input"),
        help="Directory where synthetic demo images will be saved.",
    )

    demo_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("examples/output/demo"),
        help="Directory where demo analysis outputs will be saved.",
    )

    add_shared_analysis_arguments(demo_parser)

    return parser


def run_analyze(args: argparse.Namespace) -> int:
    """Run the analyze command."""
    options = resolve_analysis_options(args, command="analyze")
    analyze_kwargs = build_analyze_kwargs(options)

    result = analyze_image(
        input_path=args.image,
        output_dir=args.output,
        **analyze_kwargs,
    )

    print("CurvInspect analysis completed.")
    print(f"Output directory: {result.output_dir}")
    print(f"Preset: {args.preset or 'none'}")
    print(f"Analysis contour: {options['analysis_contour']}")
    print(f"Inspection signal: {options['inspection_signal']}")
    print(f"Curvature mode: {options['curvature_mode']}")
    print(f"Deviation mode: {options['deviation_mode']}")
    print(f"Deviation window: {options['deviation_window']}")
    print(f"Chord mode: {options['chord_mode']}")
    print(f"Chord step: {options['chord_step']}")
    print(f"Detected anomaly regions: {len(result.anomalies.peak_indices)}")
    print(f"Raw anomalous points: {len(result.anomalies.indices)}")
    print("Generated files:")
    print(f"- {result.output_dir / 'overlay.png'}")
    print(f"- {result.output_dir / 'overlay_debug.png'}")
    print(f"- {result.output_dir / 'curvature_signal.png'}")
    print(f"- {result.output_dir / 'anomaly_report.json'}")

    return 0


def run_demo(args: argparse.Namespace) -> int:
    """Run the demo command."""
    options = resolve_analysis_options(args, command="demo")
    analyze_kwargs = build_analyze_kwargs(options)

    image_paths = save_demo_images(args.image_output)

    normal_output = args.output / "normal"
    defective_output = args.output / "defective"

    normal_result = analyze_image(
        input_path=image_paths["normal"],
        output_dir=normal_output,
        **analyze_kwargs,
    )

    defective_result = analyze_image(
        input_path=image_paths["defective"],
        output_dir=defective_output,
        **analyze_kwargs,
    )

    summary_path = args.output / "demo_summary.json"
    summary = save_demo_summary(
        summary_path,
        normal_regions=len(normal_result.anomalies.peak_indices),
        defective_regions=len(defective_result.anomalies.peak_indices),
        normal_output_dir=normal_result.output_dir,
        defective_output_dir=defective_result.output_dir,
    )

    print("CurvInspect demo completed.")
    print("Generated synthetic images:")
    print(f"- {image_paths['normal']}")
    print(f"- {image_paths['defective']}")
    print("Demo analysis outputs:")
    print(f"- {normal_result.output_dir}")
    print(f"- {defective_result.output_dir}")
    print("Analysis settings:")
    print(f"- preset: {args.preset or 'none'}")
    print(f"- analysis contour: {options['analysis_contour']}")
    print(f"- inspection signal: {options['inspection_signal']}")
    print(f"- curvature mode: {options['curvature_mode']}")
    print(f"- deviation mode: {options['deviation_mode']}")
    print(f"- deviation window: {options['deviation_window']}")
    print(f"- chord mode: {options['chord_mode']}")
    print(f"- chord step: {options['chord_step']}")
    print("High-curvature region comparison:")
    print(f"- normal reference: {summary['normal_high_curvature_regions']}")
    print(f"- defective sample: {summary['defective_high_curvature_regions']}")
    print(f"- extra defect candidates: {summary['extra_candidate_regions']}")
    print("Generated summary:")
    print(f"- {summary_path}")

    return 0


def main() -> int:
    """Run the CurvInspect command-line interface."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "analyze":
        return run_analyze(args)

    if args.command == "demo":
        return run_demo(args)

    parser.error(f"Unknown command: {args.command}")
    return 2