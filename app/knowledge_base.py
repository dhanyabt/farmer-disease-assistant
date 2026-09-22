"""Read-only access to the crop-disease knowledge base."""

import json
import re
from pathlib import Path
from typing import Any


_KNOWLEDGE_BASE_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"
)


def _load_records() -> list[dict[str, Any]]:
    """Load valid disease records, returning no records for invalid data."""
    try:
        with _KNOWLEDGE_BASE_PATH.open(encoding="utf-8") as knowledge_base_file:
            data = json.load(knowledge_base_file)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, dict):
        return []

    records = data.get("diseases")
    if not isinstance(records, list):
        return []

    return [record for record in records if isinstance(record, dict)]


def get_disease_record(crop: str, disease: str) -> dict[str, Any] | None:
    """Return the record with the exact crop and disease, if it exists."""
    for record in _load_records():
        if record.get("crop") == crop and record.get("disease") == disease:
            return record
    return None


def search_by_symptoms(crop: str, symptoms: str) -> list[dict[str, Any]]:
    """Return records for a crop whose symptom keywords appear in the input."""
    input_keywords = set(re.findall(r"\b\w+\b", symptoms.lower()))
    if not input_keywords:
        return []

    matching_records: list[dict[str, Any]] = []
    for record in _load_records():
        if record.get("crop") != crop:
            continue

        record_symptoms = record.get("symptoms")
        if isinstance(record_symptoms, list):
            symptom_text = " ".join(
                item for item in record_symptoms if isinstance(item, str)
            )
        elif isinstance(record_symptoms, str):
            symptom_text = record_symptoms
        else:
            continue

        record_keywords = set(re.findall(r"\b\w+\b", symptom_text.lower()))
        if input_keywords & record_keywords:
            matching_records.append(record)

    return matching_records


def get_treatment(crop: str, disease: str) -> str | None:
    """Return a sourced treatment, or None when it is unavailable."""
    record = get_disease_record(crop, disease)
    if record is None:
        return None

    treatment = record.get("treatment")
    source = record.get("source")
    if (
        not isinstance(treatment, str)
        or not treatment.strip()
        or not isinstance(source, str)
        or not source.strip()
    ):
        return None

    return treatment