"""MobileNetV2 disease classifier for the HACKMINT Person A pipeline."""

from pathlib import Path
from typing import Any

import torch
from PIL import Image
from torch import nn
from torchvision import models, transforms


MODEL_PATH = Path(__file__).resolve().parent / "plant_disease_model.pth"

CLASS_NAMES = [
    "early_blight",
    "healthy",
    "late_blight",
]

CONFIDENCE_THRESHOLD = 0.75

IMAGE_SIZE = 224


def preprocess_image(image_path: str | Path) -> torch.Tensor:
    """Prepare an image for MobileNetV2 inference."""

    transform = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )

    with Image.open(image_path) as image:
        image = image.convert("RGB")

    return transform(image).unsqueeze(0)


def load_model() -> Any:
    """Load the trained MobileNetV2 model."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location="cpu",
        weights_only=False,
    )

    model = models.mobilenet_v2(weights=None)

    model.classifier[1] = nn.Linear(
        model.last_channel,
        len(CLASS_NAMES),
    )

    model.load_state_dict(checkpoint["model_state_dict"])

    model.eval()

    return model


def predict(image: Image.Image, model: Any) -> dict[str, Any]:
    """Run MobileNetV2 inference on an image."""

    transform = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )

    image = image.convert("RGB")
    image_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(image_tensor)

    probabilities = torch.softmax(output, dim=1)[0]

    confidence, class_index = torch.max(
        probabilities,
        dim=0,
    )

    confidence_value = float(confidence.item())
    disease = CLASS_NAMES[int(class_index.item())]

    return {
        "crop": "Tomato",
        "disease": disease,
        "confidence": confidence_value,
    }


def classify_image(
    image_path: str | Path,
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> dict[str, Any]:
    """Classify an image and apply the confidence gate."""

    with Image.open(image_path) as image:
        image = image.convert("RGB")

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