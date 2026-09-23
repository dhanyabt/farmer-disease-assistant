"""Image quality checks for the HACKMINT Person A pipeline."""

from pathlib import Path
from typing import Any

import cv2

# These values are intentionally easy to change for a hackathon demo.
MIN_WIDTH = 224
MIN_HEIGHT = 224
BLUR_THRESHOLD = 100.0


def check_image_quality(
    image_path: str | Path,
    min_width: int = MIN_WIDTH,
    min_height: int = MIN_HEIGHT,
    blur_threshold: float = BLUR_THRESHOLD,
) -> dict[str, Any]:
    """Check whether an image is usable for disease classification.

    The blur score is the variance of the grayscale image's Laplacian.
    Higher scores generally indicate more visible edges and a sharper image.
    """
    path = Path(image_path)

    if not path.is_file():
        return _rejected_result("Image file was not found.")

    image = cv2.imread(str(path))
    if image is None:
        return _rejected_result("Image could not be opened. Please upload a valid image.")

    height, width = image.shape[:2]
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_score = float(cv2.Laplacian(gray_image, cv2.CV_64F).var())

    if width < min_width or height < min_height:
        return {
            "accepted": False,
            "blur_score": round(blur_score, 2),
            "width": width,
            "height": height,
            "message": (
                f"Image is too small. Minimum size is {min_width}x{min_height} pixels."
            ),
        }

    if blur_score < blur_threshold:
        return {
            "accepted": False,
            "blur_score": round(blur_score, 2),
            "width": width,
            "height": height,
            "message": "Image is too blurry. Please upload a clearer image.",
        }

    return {
        "accepted": True,
        "blur_score": round(blur_score, 2),
        "width": width,
        "height": height,
        "message": "Image quality is acceptable",
    }


def _rejected_result(message: str) -> dict[str, Any]:
    """Return a consistent result when dimensions or blur cannot be measured."""
    return {
        "accepted": False,
        "blur_score": None,
        "width": None,
        "height": None,
        "message": message,
    }
