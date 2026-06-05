"""Image preprocessing utilities."""

from __future__ import annotations

import cv2
import numpy as np


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert an image to grayscale."""
    arr = np.asarray(image)

    if arr.ndim == 2:
        return arr.copy()

    if arr.ndim != 3:
        raise ValueError("image must be either grayscale or color.")

    if arr.shape[2] == 3:
        return cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)

    if arr.shape[2] == 4:
        return cv2.cvtColor(arr, cv2.COLOR_BGRA2GRAY)

    raise ValueError("color image must have either 3 or 4 channels.")


def gaussian_blur(image: np.ndarray, *, kernel_size: int = 5, sigma: float = 0.0) -> np.ndarray:
    """Apply Gaussian blur to an image."""
    if kernel_size < 1:
        raise ValueError("kernel_size must be positive.")

    if kernel_size % 2 == 0:
        raise ValueError("kernel_size must be odd.")

    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)


def canny_edges(
    image: np.ndarray,
    *,
    lower_threshold: float = 50.0,
    upper_threshold: float = 150.0,
    blur_kernel_size: int = 5,
) -> np.ndarray:
    """Detect edges using the Canny edge detector."""
    if lower_threshold < 0 or upper_threshold < 0:
        raise ValueError("Canny thresholds must be non-negative.")

    if lower_threshold >= upper_threshold:
        raise ValueError("lower_threshold must be smaller than upper_threshold.")

    gray = to_grayscale(image)
    blurred = gaussian_blur(gray, kernel_size=blur_kernel_size)

    return cv2.Canny(blurred, lower_threshold, upper_threshold)


def binary_threshold(
    image: np.ndarray,
    *,
    threshold: float | None = None,
    invert: bool = False,
) -> np.ndarray:
    """Create a binary image using a fixed threshold or Otsu thresholding."""
    gray = to_grayscale(image)

    threshold_type = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY

    if threshold is None:
        threshold_type |= cv2.THRESH_OTSU
        _, binary = cv2.threshold(gray, 0, 255, threshold_type)
        return binary

    if not 0 <= threshold <= 255:
        raise ValueError("threshold must be between 0 and 255.")

    _, binary = cv2.threshold(gray, threshold, 255, threshold_type)
    return binary