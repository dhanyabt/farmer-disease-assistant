from app.orchestrator import analyze_case


def test_unknown_disease_returns_refer():
    result = analyze_case(
        crop="Tomato",
        disease="Unknown Disease",
        classifier_confidence=0.9,
        symptoms="brown spots",
    )

    assert result.decision == "REFER"
    assert result.needs_expert is True
    assert result.treatment is None


def test_low_confidence_returns_refer():
    result = analyze_case(
        crop="Tomato",
        disease="Early Blight",
        classifier_confidence=0.2,
        symptoms="brown spots dark spots yellowing leaves older leaves affected",
    )

    assert result.decision == "REFER"
    assert result.needs_expert is True
    assert result.treatment is None


def test_borderline_confidence_returns_clarify():
    result = analyze_case(
        crop="Tomato",
        disease="Early Blight",
        classifier_confidence=0.7,
        symptoms="brown spots",
    )

    assert result.decision == "CLARIFY"
    assert result.needs_expert is False
    assert result.treatment is None
    assert result.question is not None
    assert result.question.count("?") == 1


def test_high_confidence_without_verified_treatment_returns_refer():
    result = analyze_case(
        crop="Tomato",
        disease="Early Blight",
        classifier_confidence=1.0,
        symptoms="brown spots dark spots yellowing leaves older leaves affected",
    )

    assert result.decision == "REFER"
    assert result.treatment is None
    assert result.needs_expert is True