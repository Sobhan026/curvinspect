import numpy as np

from curvinspect.preprocessing import binary_threshold, canny_edges, gaussian_blur, to_grayscale


def test_to_grayscale_keeps_grayscale_shape():
    image = np.zeros((20, 30), dtype=np.uint8)

    gray = to_grayscale(image)

    assert gray.shape == (20, 30)


def test_to_grayscale_converts_color_image():
    image = np.zeros((20, 30, 3), dtype=np.uint8)

    gray = to_grayscale(image)

    assert gray.shape == (20, 30)


def test_gaussian_blur_preserves_shape():
    image = np.zeros((20, 30), dtype=np.uint8)

    blurred = gaussian_blur(image, kernel_size=5)

    assert blurred.shape == image.shape


def test_binary_threshold_returns_binary_image():
    image = np.zeros((20, 30), dtype=np.uint8)
    image[:, 15:] = 255

    binary = binary_threshold(image)

    unique_values = set(np.unique(binary).tolist())

    assert unique_values.issubset({0, 255})


def test_canny_edges_returns_grayscale_edge_image():
    image = np.zeros((100, 100), dtype=np.uint8)
    image[25:75, 25:75] = 255

    edges = canny_edges(image)

    assert edges.shape == image.shape
    assert edges.dtype == np.uint8