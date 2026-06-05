import numpy as np

from curvinspect.contour import extract_main_contour, find_external_contours, simplify_contour


def make_rectangle_image() -> np.ndarray:
    image = np.zeros((120, 160), dtype=np.uint8)
    image[30:90, 40:120] = 255
    return image


def test_find_external_contours_finds_rectangle():
    image = make_rectangle_image()

    contours = find_external_contours(image)

    assert len(contours) == 1


def test_extract_main_contour_from_threshold_image():
    image = make_rectangle_image()

    result = extract_main_contour(image, method="threshold")

    assert result.area > 4000
    assert result.perimeter > 200
    assert len(result.points) > 0
    assert len(result.simplified_points) >= 4


def test_simplify_contour_returns_polygon_points():
    image = make_rectangle_image()
    result = extract_main_contour(image, method="threshold")

    simplified = simplify_contour(result.points, epsilon_ratio=0.01)

    assert simplified.ndim == 2
    assert simplified.shape[1] == 2
    assert len(simplified) >= 4