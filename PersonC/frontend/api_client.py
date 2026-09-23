"""Backend adapter connecting Person C → Person A → Person B."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

import requests

from config import settings


class ApiClientError(RuntimeError):
    """Raised when an API cannot return a usable response."""


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


def _number(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default

    if number > 1:
        number = number / 100

    return max(
        0.0,
        min(1.0, number),
    )


def normalize_response(
    payload: dict[str, Any],
    source: str = "backend",
) -> Diagnosis:

    confidence = _number(
        payload.get("confidence", 0)
    )

    decision = str(
        payload.get("decision", "")
    ).upper()

    if decision == "TREATMENT":
        status = "high"

    elif decision == "CLARIFY":
        status = "borderline"

    else:
        status = "low"

    question = payload.get(
        "question",
        "",
    )

    questions = []

    if question:
        questions.append(
            str(question)
        )

    needs_expert = bool(
        payload.get(
            "needs_expert",
            False,
        )
    )

    return Diagnosis(
        disease=str(
            payload.get(
                "disease",
                "Unknown",
            )
        ),

        confidence=confidence,

        status=status,

        treatment=str(
            payload.get("treatment") or ""
        ),

        explanation=f"Decision: {decision}",

        questions=tuple(
            questions
        ),

        expert_referral=(
            "Please consult an agricultural expert."
            if needs_expert
            else ""
        ),

        source=str(
            payload.get("source")
            or source
        ),
    )


def _fixture_path(
    status: str,
) -> Path:

    names = {
        "high": "high_confidence.json",
        "borderline": "borderline.json",
        "low": "low_confidence.json",
    }

    return (
        Path(__file__).parent
        / "test_data"
        / names[status]
    )


def demo_diagnosis(
    symptoms: str,
) -> Diagnosis:

    text = symptoms.lower()

    if any(
        word in text
        for word in (
            "uncertain",
            "not sure",
            "mixed",
            "borderline",
        )
    ):
        status = "borderline"

    elif any(
        word in text
        for word in (
            "severe",
            "unknown",
            "many",
            "wilting",
        )
    ):
        status = "low"

    else:
        status = "high"

    with _fixture_path(status).open(
        encoding="utf-8"
    ) as fixture:

        return normalize_response(
            json.load(fixture),
            source="demo fixture",
        )


def analyze_crop(
    image: BinaryIO,
    crop_name: str,
    plant_part: str,
    symptoms: str,
    location: str,
) -> Diagnosis:

    """
    HACKMINT pipeline:

    Person C
        ↓
    Person A
        ↓
    Person B
        ↓
    Person C
    """

    # ---------------------------------------------------------
    # CHECK BACKEND CONFIGURATION
    # ---------------------------------------------------------

    if not settings.backend_url:

        if settings.demo_mode:
            return demo_diagnosis(symptoms)

        raise ApiClientError(
            "HACKMINT_BACKEND_URL is not configured "
            "and demo mode is disabled."
        )

    # =========================================================
    # PERSON A — IMAGE ANALYSIS
    # =========================================================

    person_a_url = settings.backend_url

    try:
        image.seek(0)

        image_bytes = image.read()

        if not image_bytes:
            raise ApiClientError(
                "The uploaded image is empty."
            )

        filename = getattr(
            image,
            "name",
            "crop.jpg",
        )

        content_type = getattr(
            image,
            "type",
            None,
        ) or "image/jpeg"

        response_a = requests.post(
            person_a_url,
            files={
                "file": (
                    filename,
                    image_bytes,
                    content_type,
                )
            },
            timeout=settings.request_timeout_seconds,
        )

        response_a.raise_for_status()

        person_a = response_a.json()

    except requests.HTTPError as exc:

        try:
            detail = response_a.text
        except Exception:
            detail = ""

        raise ApiClientError(
            f"Person A rejected the request: {exc}\n"
            f"Details: {detail}"
        ) from exc

    except (
        requests.RequestException,
        ValueError,
    ) as exc:

        raise ApiClientError(
            f"Person A image-analysis request failed: {exc}"
        ) from exc

    if not isinstance(
        person_a,
        dict,
    ):
        raise ApiClientError(
            "Person A returned an invalid response."
        )

    if person_a.get(
        "status"
    ) != "success":

        raise ApiClientError(
            str(
                person_a.get(
                    "message",
                    "Person A rejected the image.",
                )
            )
        )

    # ---------------------------------------------------------
    # EXTRACT PERSON A PREDICTION
    # ---------------------------------------------------------

    prediction = person_a.get(
        "prediction"
    )

    if not isinstance(
        prediction,
        dict,
    ):
        raise ApiClientError(
            "Person A did not return a prediction."
        )

    crop = str(
        prediction.get(
            "crop",
            crop_name,
        )
    )

    disease = str(
        prediction.get(
            "disease",
            "Unknown",
        )
    )

    confidence = _number(
        prediction.get(
            "confidence",
            0,
        )
    )

    # =========================================================
    # PERSON B — ORCHESTRATOR
    # =========================================================

    person_b_url = (
        "http://127.0.0.1:8000/analyze"
    )

    try:

        response_b = requests.post(
            person_b_url,
            json={
                "crop": crop,
                "disease": disease,
                "confidence": confidence,
                "symptoms": symptoms,
                "location": location,
                "plant_part": plant_part,
            },
            timeout=settings.request_timeout_seconds,
        )

        response_b.raise_for_status()

        person_b = response_b.json()

    except requests.HTTPError as exc:

        try:
            detail = response_b.text
        except Exception:
            detail = ""

        raise ApiClientError(
            f"Person B rejected the request: {exc}\n"
            f"Details: {detail}"
        ) from exc

    except (
        requests.RequestException,
        ValueError,
    ) as exc:

        raise ApiClientError(
            f"Person B orchestration request failed: {exc}"
        ) from exc

    if not isinstance(
        person_b,
        dict,
    ):
        raise ApiClientError(
            "Person B returned an invalid response."
        )

    # =========================================================
    # RETURN FINAL RESULT TO PERSON C
    # =========================================================

    return normalize_response(
        person_b,
        source="Person B orchestrator",
    )