"""Central deterministic orchestration for crop-disease analysis."""
from pathlib import Path

from app.ai.person_a_pipeline import analyze_image

from app.clarification import calculate_symptom_match, generate_clarification_question
from app.confidence import gate_confidence
from app.knowledge_base import get_disease_record, get_treatment
from app.models import AnalysisResponse


def analyze_case(
    crop: str,
    disease: str,
    classifier_confidence: float,
    symptoms: str,
) -> AnalysisResponse:
    """Analyze a case using only the deterministic backend components."""
    disease_record = get_disease_record(crop, disease)
    symptom_match_score = calculate_symptom_match(crop, disease, symptoms)
    confidence_result = gate_confidence(
        classifier_confidence,
        symptom_match_score,
    )

    if disease_record is None or confidence_result.decision == "REFER":
        return AnalysisResponse(
            decision="REFER",
            crop=crop,
            disease=disease,
            confidence=confidence_result.combined_confidence,
            needs_expert=True,
        )

    if confidence_result.decision == "CLARIFY":
        return AnalysisResponse(
            decision="CLARIFY",
            crop=crop,
            disease=disease,
            confidence=confidence_result.combined_confidence,
            question=generate_clarification_question(crop, disease, symptoms),
            needs_expert=False,
        )

    treatment = get_treatment(crop, disease)
    source = disease_record.get("source")
    if (
        treatment is None
        or not isinstance(source, str)
        or not source.strip()
    ):
        return AnalysisResponse(
            decision="REFER",
            crop=crop,
            disease=disease,
            confidence=confidence_result.combined_confidence,
            needs_expert=True,
        )

    return AnalysisResponse(
        decision="TREATMENT",
        crop=crop,
        disease=disease,
        confidence=confidence_result.combined_confidence,
        treatment=treatment,
        source=source,
        needs_expert=False,
    )
def analyze_image_case(
    image_path: str | Path,
    symptoms: str,
) -> AnalysisResponse:
    """Run Person A image analysis and pass its prediction to Person B."""

    image_result = analyze_image(str(image_path))

    # Person A rejected the image.
    if image_result["status"] != "success":
        return AnalysisResponse(
            decision="REFER",
            crop="Unknown",
            disease="Unknown",
            confidence=0.0,
            needs_expert=True,
        )

    prediction = image_result["prediction"]

    crop = prediction["crop"]
    disease = prediction["disease"]
    confidence = float(prediction["confidence"])

    # Person A could not make a sufficiently confident prediction.
    if crop == "Unknown" or disease == "Uncertain":
        return AnalysisResponse(
            decision="REFER",
            crop=crop,
            disease=disease,
            confidence=confidence,
            needs_expert=True,
        )

    # Send Person A's result into the existing Person B decision engine.
    return analyze_case(
        crop=crop,
        disease=disease,
        classifier_confidence=confidence,
        symptoms=symptoms,
    )