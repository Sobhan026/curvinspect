import cv2
import numpy as np

from curvinspect.pipeline import analyze_image


def test_analyze_image_generates_expected_outputs(tmp_path):
    image = np.zeros((160, 160, 3), dtype=np.uint8)
    cv2.rectangle(image, (40, 40), (120, 120), (255, 255, 255), thickness=-1)

    input_path = tmp_path / "rectangle.png"
    output_dir = tmp_path / "output"

    cv2.imwrite(str(input_path), image)

    result = analyze_image(
        input_path,
        output_dir,
        contour_method="threshold",
        analysis_contour="raw",
        num_samples=128,
        smoothing="median",
        smoothing_window=5,
        anomaly_threshold=3.5,
    )

    assert len(result.resampled_points) == 128
    assert len(result.analysis_points) == len(result.contour.points)
    assert result.report["contour"]["analysis_contour"] == "raw"
    assert result.report["contour"]["num_analysis_points"] == len(result.contour.points)

    assert (output_dir / "overlay.png").exists()
    assert (output_dir / "curvature_signal.png").exists()
    assert (output_dir / "anomaly_report.json").exists()


def test_analyze_image_can_use_simplified_contour(tmp_path):
    image = np.zeros((200, 200, 3), dtype=np.uint8)

    points = np.array(
        [
            [40, 40],
            [160, 40],
            [160, 90],
            [130, 100],
            [160, 110],
            [160, 160],
            [40, 160],
        ],
        dtype=np.int32,
    )

    cv2.fillPoly(image, [points], (255, 255, 255))

    input_path = tmp_path / "defective_polygon.png"
    output_dir = tmp_path / "output_simplified"

    cv2.imwrite(str(input_path), image)

    result = analyze_image(
        input_path,
        output_dir,
        contour_method="threshold",
        analysis_contour="simplified",
        epsilon_ratio=0.01,
        num_samples=128,
        smoothing="median",
        smoothing_window=3,
        anomaly_threshold=1.5,
    )

    assert len(result.resampled_points) == 128
    assert len(result.analysis_points) == len(result.contour.simplified_points)
    assert result.report["contour"]["analysis_contour"] == "simplified"
    assert result.report["contour"]["num_analysis_points"] == len(result.contour.simplified_points)

    assert (output_dir / "overlay.png").exists()
    assert (output_dir / "curvature_signal.png").exists()
    assert (output_dir / "anomaly_report.json").exists()