"""FastAPI adapter for the HACKMINT Person A image pipeline."""

import os
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from classifier import CONFIDENCE_THRESHOLD, classify_image
from quality_gate import check_image_quality

app = FastAPI(
    title="HACKMINT Person A API",
    description="Image quality and crop disease classification prototype.",
    version="0.1.0",
)


def analyze_image(image_path: str | Path) -> dict[str, Any]:
    """Run the reusable quality and classification pipeline on an image path."""
    quality = check_image_quality(image_path)

    if not quality["accepted"]:
        return {
            "quality": quality,
            "prediction": None,
            "decision": "REFER_TO_EXPERT",
            "message": quality["message"],
        }

    prediction = classify_image(image_path, CONFIDENCE_THRESHOLD)
    decision = (
        "PROCEED"
        if prediction["disease"] != "Uncertain"
        else "REFER_TO_EXPERT"
    )

    result: dict[str, Any] = {
        "quality": quality,
        "prediction": prediction,
        "decision": decision,
    }

    if decision == "REFER_TO_EXPERT":
        result["message"] = "Insufficient confidence for automated diagnosis."

    return result


@app.get("/health")
def health() -> dict[str, str]:
    """Confirm that the local API is running."""
    return {"status": "HACKMINT Person A API is running"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> JSONResponse:
    """Save one upload temporarily, run the pipeline, and remove the file."""
    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    temporary_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary_file:
            temporary_file.write(await file.read())
            temporary_path = temporary_file.name

        result = analyze_image(temporary_path)
        if not result["quality"]["accepted"]:
            return JSONResponse(status_code=400, content={"status": "error", **result})

        return JSONResponse(status_code=200, content={"status": "success", **result})
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)
