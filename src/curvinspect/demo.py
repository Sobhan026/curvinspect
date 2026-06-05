"""Demo comparison utilities for CurvInspect."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from curvinspect.report import save_json_report


def build_demo_summary(
    *,
    normal_regions: int,
    defective_regions: int,
    normal_output_dir: str | Path,
    defective_output_dir: str | Path,
) -> dict[str, Any]:
    """Build a summary comparing normal and defective demo outputs."""
    extra_candidates = max(0, defective_regions - normal_regions)

    return {
        "normal_high_curvature_regions": normal_regions,
        "defective_high_curvature_regions": defective_regions,
        "extra_candidate_regions": extra_candidates,
        "normal_output_dir": str(normal_output_dir),
        "defective_output_dir": str(defective_output_dir),
        "interpretation": (
            "The defective part contains additional high-curvature regions "
            "compared to the normal reference shape."
            if extra_candidates > 0
            else "No additional high-curvature regions were detected in the defective part."
        ),
    }


def save_demo_summary(
    path: str | Path,
    *,
    normal_regions: int,
    defective_regions: int,
    normal_output_dir: str | Path,
    defective_output_dir: str | Path,
) -> dict[str, Any]:
    """Save a JSON summary for the synthetic demo comparison."""
    summary = build_demo_summary(
        normal_regions=normal_regions,
        defective_regions=defective_regions,
        normal_output_dir=normal_output_dir,
        defective_output_dir=defective_output_dir,
    )

    save_json_report(path, summary)
    return summary