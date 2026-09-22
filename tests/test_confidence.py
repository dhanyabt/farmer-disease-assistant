import pytest

from app.confidence import gate_confidence


def test_high_confidence_returns_treatment():
    result = gate_confidence(0.9, 0.8)

    assert result.decision == "TREATMENT"


def test_borderline_confidence_returns_clarify():
    result = gate_confidence(0.6, 0.5)

    assert result.decision == "CLARIFY"


def test_low_confidence_returns_refer():
    result = gate_confidence(0.2, 0.3)

    assert result.decision == "REFER"


def test_exactly_080_returns_treatment():
    result = gate_confidence(0.8, 0.8)

    assert result.combined_confidence == 0.8
    assert result.decision == "TREATMENT"


def test_exactly_050_returns_clarify():
    result = gate_confidence(0.5, 0.5)

    assert result.combined_confidence == 0.5
    assert result.decision == "CLARIFY"


def test_classifier_confidence_below_zero_raises_value_error():
    with pytest.raises(ValueError):
        gate_confidence(-0.1, 0.5)


def test_classifier_confidence_above_one_raises_value_error():
    with pytest.raises(ValueError):
        gate_confidence(1.1, 0.5)


def test_symptom_match_score_below_zero_raises_value_error():
    with pytest.raises(ValueError):
        gate_confidence(0.5, -0.1)


def test_symptom_match_score_above_one_raises_value_error():
    with pytest.raises(ValueError):
        gate_confidence(0.5, 1.1)


def test_boolean_input_is_rejected():
    with pytest.raises(TypeError):
        gate_confidence(True, 0.5)