"""Disease classification interface for the HACKMINT Person A pipeline.

The default MOCK_MODE keeps this one-day prototype runnable without downloading
or training a large model. Mock output is deliberately uncertain and must not
be presented as a real AI diagnosis.
"""

from pathlib import Path
from typing import Any

from PIL import Image

# Set this to False when a real model and its prediction code are available.
MOCK_MODE = True
CONFIDENCE_THRESHOLD = 0.75


def preprocess_image(image_path: str | Path) -> Image.Image:
    """Open and normalize an image before it reaches a model."""
    with Image.open(image_path) as image:
        return image.convert("RGB")


def load_model() -> Any:
    """Load a future PlantVillage/PlantDoc model.

    A real implementation can load a local model here without changing the
    public classify_image function.
    """
    if MOCK_MODE:
        return None

    raise RuntimeError(
        "MOCK_MODE is disabled, but no real local classifier has been configured."
    )


def predict(image: Image.Image, model: Any) -> dict[str, Any]:
    """Run model inference and return its raw crop, disease, and confidence."""
    if MOCK_MODE:
        # This is intentionally low confidence: it exercises the expert-review path.
        return {
            "disease": "Mock prediction - not a real diagnosis",
            "confidence": 0.0,
            "crop": "Unknown",
        }

    raise NotImplementedError("Add preprocessing and inference for the selected model.")


def classify_image(
    image_path: str | Path,
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> dict[str, Any]:
    """Classify an image and apply the confidence gate."""
    image = preprocess_image(image_path)
    model = load_model()
    raw_prediction = predict(image, model)
    confidence = float(raw_prediction["confidence"])

    if confidence < confidence_threshold:
        return {
            "disease": "Uncertain",
            "confidence": round(confidence, 2),
            "crop": raw_prediction.get("crop", "Unknown"),
        }

    return {
        "disease": raw_prediction["disease"],
        "confidence": round(confidence, 2),
        "crop": raw_prediction.get("crop", "Unknown"),
    }
