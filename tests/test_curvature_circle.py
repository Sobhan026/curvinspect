import numpy as np

from curvinspect.curvature import discrete_curvature, total_signed_turning


def make_circle_points(radius: float = 2.0, n: int = 256) -> np.ndarray:
    angles = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    x = radius * np.cos(angles)
    y = radius * np.sin(angles)
    return np.column_stack([x, y])


def test_closed_polygon_total_turning_is_two_pi():
    points = make_circle_points(radius=3.0, n=128)

    total_turning = total_signed_turning(points, closed=True)

    assert np.isclose(total_turning, 2.0 * np.pi, atol=1e-10)


def test_regular_polygon_curvature_approximates_inverse_radius():
    radius = 4.0
    points = make_circle_points(radius=radius, n=512)

    curvatures = discrete_curvature(points, closed=True)
    mean_curvature = np.mean(curvatures)

    assert np.isclose(mean_curvature, 1.0 / radius, rtol=0.02)