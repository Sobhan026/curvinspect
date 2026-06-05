"""Synthetic image generation utilities for CurvInspect demos."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from curvinspect.image_io import save_image


def create_blank_image(
    *,
    size: int = 480,
    channels: int = 3,
    background_value: int = 0,
) -> np.ndarray:
    """Create a blank square image."""
    if size <= 0:
        raise ValueError("size must be positive.")

    if channels not in {1, 3}:
        raise ValueError("channels must be either 1 or 3.")

    if not 0 <= background_value <= 255:
        raise ValueError("background_value must be between 0 and 255.")

    if channels == 1:
        return np.full((size, size), background_value, dtype=np.uint8)

    return np.full((size, size, channels), background_value, dtype=np.uint8)


def create_normal_part_image(*, size: int = 480) -> np.ndarray:
    """Create a simple normal synthetic part image."""
    image = create_blank_image(size=size, channels=3)

    margin = int(size * 0.23)
    max_coord = size - margin

    points = np.array(
        [
            [margin, margin],
            [max_coord, margin],
            [max_coord, max_coord],
            [margin, max_coord],
        ],
        dtype=np.int32,
    )

    cv2.fillPoly(image, [points], (255, 255, 255))
    return image


def create_defective_part_image(*, size: int = 480) -> np.ndarray:
    """Create a synthetic part image with a boundary defect."""
    image = create_blank_image(size=size, channels=3)

    left = int(size * 0.23)
    right = int(size * 0.77)
    top = int(size * 0.23)
    bottom = int(size * 0.77)

    notch_inner_x = int(size * 0.56)
    notch_top_y = int(size * 0.44)
    notch_mid_y = int(size * 0.50)
    notch_bottom_y = int(size * 0.56)

    points = np.array(
        [
            [left, top],
            [right, top],
            [right, notch_top_y],
            [notch_inner_x, notch_mid_y],
            [right, notch_bottom_y],
            [right, bottom],
            [left, bottom],
        ],
        dtype=np.int32,
    )

    cv2.fillPoly(image, [points], (255, 255, 255))

    small_chip = np.array(
        [
            [left, int(size * 0.62)],
            [int(size * 0.17), int(size * 0.66)],
            [left, int(size * 0.70)],
        ],
        dtype=np.int32,
    )

    cv2.fillPoly(image, [small_chip], (0, 0, 0))

    return image


def save_demo_images(output_dir: str | Path) -> dict[str, Path]:
    """Save synthetic demo images and return their paths."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    normal_path = output_path / "normal_part.png"
    defective_path = output_path / "defective_part.png"

    save_image(normal_path, create_normal_part_image())
    save_image(defective_path, create_defective_part_image())

    return {
        "normal": normal_path,
        "defective": defective_path,
    }