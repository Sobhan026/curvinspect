"""Image input/output utilities."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def read_image(path: str | Path, *, grayscale: bool = False) -> np.ndarray:
    """Read an image from disk."""
    image_path = Path(path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image file does not exist: {image_path}")

    flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    image = cv2.imread(str(image_path), flag)

    if image is None:
        raise ValueError(f"Failed to read image: {image_path}")

    return image


def save_image(path: str | Path, image: np.ndarray) -> None:
    """Save an image to disk."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    success = cv2.imwrite(str(output_path), image)

    if not success:
        raise ValueError(f"Failed to save image: {output_path}")


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """Convert a BGR image to RGB."""
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("image must have shape (height, width, 3).")

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def rgb_to_bgr(image: np.ndarray) -> np.ndarray:
    """Convert an RGB image to BGR."""
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("image must have shape (height, width, 3).")

    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)