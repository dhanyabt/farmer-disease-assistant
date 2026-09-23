"""Backend adapter for connecting Person C to Persons A and B."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

import requests

from config import settings


class ApiClientError(RuntimeError):
    """Raised when the diagnosis service cannot return a usable response."""


@dataclass(frozen=True)
class Diagnosis:
    disease: str
    confidence: float
    status: str
    treatment: str
    explanation: str = ""
    questions: tuple[str, ...] = ()
    expert_referral: str = ""
    source: str = "backend"


def _number(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, number if number <= 1 else number / 100))


def normalize_response(payload: dict[str, Any], source: str = "backend") -> Diagnosis:
    """Accept common orchestrator response names without changing A/B contracts."""
    confidence = _number(
        payload.get("confidence", payload.get("image_confidence", 0))
    )
    status = str(payload.get("status", "")).lower()
    if status not in {"high", "borderline", "low"}:
        status = "high" if confidence >= 0.8 else "borderline" if confidence >= 0.5 else "low"

    questions = payload.get("questions", payload.get("clarifying_questions", []))
    if isinstance(questions, str):
        questions = [questions]
    if not isinstance(questions, list):
        questions = []

    return Diagnosis(
        disease=str(payload.get("disease", payload.get("diagnosis", "Unknown"))),
        confidence=confidence,
        status=status,
        treatment=str(payload.get("treatment", payload.get("recommendation", ""))),
        explanation=str(payload.get("explanation", payload.get("reason", ""))),
        questions=tuple(str(question) for question in questions),
        expert_referral=str(
            payload.get("expert_referral", payload.get("referral", ""))
        ),
        source=source,
    )


def _fixture_path(status: str) -> Path:
    names = {
        "high": "high_confidence.json",
        "borderline": "borderline.json",
        "low": "low_confidence.json",
    }
    return Path(__file__).parent / "test_data" / names[status]


def demo_diagnosis(symptoms: str) -> Diagnosis:
    """Return deterministic demo data when no Person A/B service is configured."""
    text = symptoms.lower()
    if any(word in text for word in ("uncertain", "not sure", "mixed", "borderline")):
        status = "borderline"
    elif any(word in text for word in ("severe", "unknown", "many", "wilting")):
        status = "low"
    else:
        status = "high"
    with _fixture_path(status).open(encoding="utf-8") as fixture:
        return normalize_response(json.load(fixture), source="demo fixture")


def analyze_crop(
    image: BinaryIO,
    crop_name: str,
    plant_part: str,
    symptoms: str,
) -> Diagnosis:
    """Send farmer input to the orchestrator, or use the local demo fixtures."""
    if not settings.backend_url:
        if settings.demo_mode:
            return demo_diagnosis(symptoms)
        raise ApiClientError(
            "HACKMINT_BACKEND_URL is not configured and demo mode is disabled."
        )

    try:
        response = requests.post(
            settings.backend_url,
            files={"image": (getattr(image, "name", "crop.jpg"), image, "image/jpeg")},
            data={
                "crop_name": crop_name,
                "plant_part": plant_part,
                "symptoms": symptoms,
            },
            timeout=settings.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise ApiClientError(f"Diagnosis service request failed: {exc}") from exc
    if not isinstance(payload, dict):
        raise ApiClientError("Diagnosis service returned an invalid response.")
    return normalize_response(payload)
