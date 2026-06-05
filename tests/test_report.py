import json

import numpy as np

from curvinspect.report import build_analysis_report, save_json_report


def test_save_json_report_writes_file(tmp_path):
    report = build_analysis_report(
        input_path="sample.png",
        image_shape=(100, 100, 3),
        contour_area=200.0,
        contour_perimeter=80.0,
        num_original_points=120,
        num_resampled_points=64,
        num_anomalies=2,
        anomaly_indices=np.array([4, 8]),
        anomaly_peak_indices=np.array([4, 8]),
        anomaly_groups=[(4, 4), (8, 8)],
        max_abs_curvature=1.5,
        mean_abs_curvature=0.2,
        bending_energy=3.0,
        total_curvature=6.28,
        threshold=3.5,
    )

    output_path = tmp_path / "report.json"
    save_json_report(output_path, report)

    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data["anomalies"]["count"] == 2
    assert data["anomalies"]["indices"] == [4, 8]
    assert data["anomalies"]["peak_indices"] == [4, 8]
    assert data["anomalies"]["groups"] == [[4, 4], [8, 8]]