from app.knowledge_base import (
    get_disease_record,
    get_treatment,
    search_by_symptoms,
)


def test_get_disease_record_returns_tomato_early_blight():
    record = get_disease_record("Tomato", "Early Blight")

    assert record is not None
    assert record["crop"] == "Tomato"
    assert record["disease"] == "Early Blight"


def test_get_disease_record_returns_none_for_unknown_disease():
    record = get_disease_record("Tomato", "Unknown Disease")

    assert record is None


def test_search_by_symptoms_returns_matching_result():
    records = search_by_symptoms("Tomato", "brown spots on older leaves")

    assert records
    assert any(
        record["crop"] == "Tomato" and record["disease"] == "Early Blight"
        for record in records
    )


def test_search_by_symptoms_returns_empty_result_for_unknown_crop():
    records = search_by_symptoms("Unknown Crop", "brown spots on older leaves")

    assert records == []


def test_get_treatment_does_not_invent_missing_treatment():
    treatment = get_treatment("Tomato", "Early Blight")

    assert treatment is None