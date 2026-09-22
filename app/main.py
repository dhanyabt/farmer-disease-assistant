"""FastAPI entry point for the crop-disease backend."""

from fastapi import FastAPI

from app.models import AnalysisRequest, AnalysisResponse
from app.orchestrator import analyze_case


app = FastAPI(
    title="Farmer Disease Assistant API",
    description="Deterministic crop-disease analysis backend.",
    version="1.0.0",
)


@app.get("/")
def health_check() -> dict[str, str]:
    """Return the service health status."""
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """Analyze a crop-disease case through the orchestration layer."""
    return analyze_case(
        crop=request.crop,
        disease=request.disease,
        classifier_confidence=request.confidence,
        symptoms=request.symptoms,
    )
