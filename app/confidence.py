"""Deterministic confidence gating for the crop-disease prototype.

The decision thresholds in this module are hackathon prototype thresholds.
They are not scientifically validated diagnostic thresholds.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


Decision = Literal["TREATMENT", "CLARIFY", "REFER"]


@dataclass(frozen=True)
class ConfidenceGateResult:
    """The combined confidence, decision, and explanation for a gate result."""

    combined_confidence: float
    decision: Decision
    reason: str


def gate_confidence(
    classifier_confidence: float,
    symptom_match_score: float,
) -> ConfidenceGateResult:
    """Combine confidence inputs and deterministically select a next step.

    The classifier contributes 70% and the symptom match contributes 30%.
    """
    _validate_score("classifier_confidence", classifier_confidence)
    _validate_score("symptom_match_score", symptom_match_score)

    combined_confidence_decimal = (
        Decimal(str(classifier_confidence)) * Decimal("0.7")
        + Decimal(str(symptom_match_score)) * Decimal("0.3")
    )
    combined_confidence = float(combined_confidence_decimal)

    if combined_confidence_decimal >= Decimal("0.80"):
        decision: Decision = "TREATMENT"
        reason = "Combined confidence is at least 0.80."
    elif combined_confidence_decimal >= Decimal("0.50"):
        decision = "CLARIFY"
        reason = "Combined confidence is at least 0.50 but below 0.80."
    else:
        decision = "REFER"
        reason = "Combined confidence is below 0.50."

    return ConfidenceGateResult(
        combined_confidence=combined_confidence,
        decision=decision,
        reason=reason,
    )


def _validate_score(name: str, score: float) -> None:
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise TypeError(f"{name} must be a number between 0 and 1.")
    if not 0 <= score <= 1:
        raise ValueError(f"{name} must be between 0 and 1.")