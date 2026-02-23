"""Image processing utilities."""
import os
from typing import Any

import cv2
import numpy as np
from PIL import Image
from loguru import logger


def resize_image(
    image: np.ndarray,
    max_width: int = 800,
    max_height: int = 600,
) -> np.ndarray:
    """
    Resize image while maintaining aspect ratio.

    Args:
        image: Input image as numpy array
        max_width: Maximum width
        max_height: Maximum height

    Returns:
        Resized image
    """
    height, width = image.shape[:2]

    if width <= max_width and height <= max_height:
        return image

    # Calculate scaling factor
    scale = min(max_width / width, max_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)

    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)


def crop_image(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
) -> np.ndarray:
    """
    Crop a region from an image.

    Args:
        image: Input image
        x: Left coordinate
        y: Top coordinate
        width: Crop width
        height: Crop height

    Returns:
        Cropped image
    """
    img_height, img_width = image.shape[:2]

    # Clamp coordinates to image bounds
    x = max(0, min(x, img_width - 1))
    y = max(0, min(y, img_height - 1))
    x2 = min(x + width, img_width)
    y2 = min(y + height, img_height)

    return image[y:y2, x:x2]


def draw_bounding_box(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
    color: tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
    label: str | None = None,
) -> np.ndarray:
    """
    Draw a bounding box on an image.

    Args:
        image: Input image
        x: Left coordinate
        y: Top coordinate
        width: Box width
        height: Box height
        color: BGR color tuple
        thickness: Line thickness
        label: Optional text label

    Returns:
        Image with bounding box drawn
    """
    result = image.copy()
    cv2.rectangle(result, (x, y), (x + width, y + height), color, thickness)

    if label:
        # Draw label background
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        (text_width, text_height), baseline = cv2.getTextSize(
            label, font, font_scale, 1
        )
        cv2.rectangle(
            result,
            (x, y - text_height - 10),
            (x + text_width + 10, y),
            color,
            -1
        )
        cv2.putText(
            result,
            label,
            (x + 5, y - 5),
            font,
            font_scale,
            (255, 255, 255),
            1
        )

    return result


def save_image(image: np.ndarray, path: str, quality: int = 90) -> str:
    """
    Save image to file.

    Args:
        image: Image as numpy array
        path: Output file path
        quality: JPEG quality (0-100)

    Returns:
        Path to saved file
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if path.lower().endswith(('.jpg', '.jpeg')):
        cv2.imwrite(path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    else:
        cv2.imwrite(path, image)

    logger.debug(f"Saved image to {path}")
    return path


def load_image(path: str) -> np.ndarray:
    """
    Load an image from file.

    Args:
        path: Path to image file

    Returns:
        Image as numpy array (BGR format)
    """
    image = cv2.imread(path)
    if image is None:
        raise ValueError(f"Cannot load image: {path}")
    return image
