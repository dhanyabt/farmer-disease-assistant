"""FastAPI entry point for the crop-disease backend."""

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile

from app.models import AnalysisRequest, AnalysisResponse
from app.orchestrator import analyze_case, analyze_image_case


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


@app.post("/analyze-image", response_model=AnalysisResponse)
async def analyze_image_endpoint(
    image: UploadFile = File(...),
    symptoms: str = Form(""),
) -> AnalysisResponse:
    """Analyze an uploaded crop image together with farmer symptoms."""

    suffix = Path(image.filename or "upload.jpg").suffix or ".jpg"
    temporary_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temporary_file:
            temporary_file.write(await image.read())
            temporary_path = temporary_file.name

        return analyze_image_case(
            image_path=temporary_path,
            symptoms=symptoms,
        )

    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)