"""Deterministic symptom matching and clarification helpers."""

import re
from typing import Any

from app.knowledge_base import get_disease_record


def normalize_symptoms(symptoms: str) -> str:
    """Return lowercase symptom text with punctuation and extra spaces removed."""
    lowercase_symptoms = symptoms.lower()
    text_without_punctuation = re.sub(r"[^\w\s]", " ", lowercase_symptoms)
    return " ".join(text_without_punctuation.split())


def calculate_symptom_match(
    crop: str,
    disease: str,
    symptoms: str,
) -> float:
    """Return the proportion of known symptom phrases matched by the input."""
    record = get_disease_record(crop, disease)
    if record is None:
        return 0.0

    known_symptoms = _get_symptom_phrases(record)
    if not known_symptoms:
        return 0.0

    input_keywords = set(normalize_symptoms(symptoms).split())
    matched_symptoms = sum(
        set(normalize_symptoms(symptom).split()) <= input_keywords
        for symptom in known_symptoms
    )
    return matched_symptoms / len(known_symptoms)


def generate_clarification_question(
    crop: str,
    disease: str,
    symptoms: str,
) -> str:
    """Return one simple question about a missing known symptom."""
    record = get_disease_record(crop, disease)
    known_symptoms = _get_symptom_phrases(record)
    input_keywords = set(normalize_symptoms(symptoms).split())

    for symptom in known_symptoms:
        symptom_keywords = set(normalize_symptoms(symptom).split())
        if not input_keywords or not symptom_keywords <= input_keywords:
            return f"Are you seeing {symptom}?"

    return "Can you describe any other symptoms you are seeing on the crop?"


def _get_symptom_phrases(record: dict[str, Any] | None) -> list[str]:
    if record is None:
        return []

    symptoms = record.get("symptoms")
    if isinstance(symptoms, str):
        return [symptoms] if normalize_symptoms(symptoms) else []
    if isinstance(symptoms, list):
        return [
            symptom
            for symptom in symptoms
            if isinstance(symptom, str) and normalize_symptoms(symptom)
        ]
    return []