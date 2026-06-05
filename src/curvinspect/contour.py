"""Contour extraction utilities for object boundary analysis."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from curvinspect.preprocessing import binary_threshold, canny_edges


@dataclass(frozen=True)
class ContourExtractionResult:
    """Result object returned by contour extraction."""

    points: np.ndarray
    simplified_points: np.ndarray
    mask: np.ndarray
    area: float
    perimeter: float


def contour_to_points(contour: np.ndarray) -> np.ndarray:
    """Convert an OpenCV contour to an array of 2D points."""
    arr = np.asarray(contour)

    if arr.ndim == 3 and arr.shape[1] == 1 and arr.shape[2] == 2:
        return arr[:, 0, :].astype(float)

    if arr.ndim == 2 and arr.shape[1] == 2:
        return arr.astype(float)

    raise ValueError("contour must have shape (n, 1, 2) or (n, 2).")


def find_external_contours(mask: np.ndarray) -> list[np.ndarray]:
    """Find external contours in a binary or edge image."""
    arr = np.asarray(mask)

    if arr.ndim != 2:
        raise ValueError("mask must be a two-dimensional image.")

    contours, _ = cv2.findContours(
        arr.astype(np.uint8),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE,
    )

    return list(contours)


def select_largest_contour(contours: list[np.ndarray], *, min_area: float = 0.0) -> np.ndarray:
    """Select the largest contour by area."""
    if min_area < 0:
        raise ValueError("min_area must be non-negative.")

    if not contours:
        raise ValueError("no contours were found.")

    largest = max(contours, key=cv2.contourArea)
    area = float(cv2.contourArea(largest))

    if area < min_area:
        raise ValueError(f"largest contour area is smaller than min_area: {area} < {min_area}")

    return largest


def simplify_contour(
    contour: np.ndarray,
    *,
    epsilon_ratio: float = 0.005,
    closed: bool = True,
) -> np.ndarray:
    """Simplify a contour using the Douglas-Peucker algorithm."""
    if epsilon_ratio <= 0:
        raise ValueError("epsilon_ratio must be positive.")

    contour_array = np.asarray(contour)

    if contour_array.ndim == 2 and contour_array.shape[1] == 2:
        contour_array = contour_array.reshape(-1, 1, 2).astype(np.float32)

    if contour_array.ndim != 3 or contour_array.shape[1:] != (1, 2):
        raise ValueError("contour must have shape (n, 1, 2) or (n, 2).")

    perimeter = cv2.arcLength(contour_array, closed)
    epsilon = epsilon_ratio * perimeter

    simplified = cv2.approxPolyDP(contour_array, epsilon, closed)
    return contour_to_points(simplified)


def extract_main_contour(
    image: np.ndarray,
    *,
    method: str = "threshold",
    invert: bool = False,
    min_area: float = 25.0,
    epsilon_ratio: float = 0.005,
) -> ContourExtractionResult:
    """Extract the main object contour from an image."""
    if method not in {"threshold", "canny"}:
        raise ValueError("method must be either 'threshold' or 'canny'.")

    if method == "threshold":
        mask = binary_threshold(image, threshold=None, invert=invert)
    else:
        mask = canny_edges(image)

    contours = find_external_contours(mask)
    largest = select_largest_contour(contours, min_area=min_area)

    points = contour_to_points(largest)
    simplified_points = simplify_contour(largest, epsilon_ratio=epsilon_ratio, closed=True)

    area = float(cv2.contourArea(largest))
    perimeter = float(cv2.arcLength(largest, True))

    return ContourExtractionResult(
        points=points,
        simplified_points=simplified_points,
        mask=mask,
        area=area,
        perimeter=perimeter,
    )