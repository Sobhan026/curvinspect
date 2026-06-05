import json

from curvinspect.demo import build_demo_summary, save_demo_summary


def test_build_demo_summary_counts_extra_candidates():
    summary = build_demo_summary(
        normal_regions=4,
        defective_regions=7,
        normal_output_dir="normal",
        defective_output_dir="defective",
    )

    assert summary["normal_high_curvature_regions"] == 4
    assert summary["defective_high_curvature_regions"] == 7
    assert summary["extra_candidate_regions"] == 3


def test_build_demo_summary_never_returns_negative_extra_candidates():
    summary = build_demo_summary(
        normal_regions=7,
        defective_regions=4,
        normal_output_dir="normal",
        defective_output_dir="defective",
    )

    assert summary["extra_candidate_regions"] == 0


def test_save_demo_summary_writes_json_file(tmp_path):
    output_path = tmp_path / "demo_summary.json"

    save_demo_summary(
        output_path,
        normal_regions=4,
        defective_regions=7,
        normal_output_dir="normal",
        defective_output_dir="defective",
    )

    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data["extra_candidate_regions"] == 3