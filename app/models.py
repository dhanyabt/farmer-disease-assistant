from typing import Literal

from pydantic import BaseModel, Field


Confidence = float
Decision = Literal["TREATMENT", "CLARIFY", "REFER"]


class ClassifierResult(BaseModel):
    crop: str
    disease: str
    confidence: Confidence = Field(ge=0, le=1)


class AnalysisRequest(BaseModel):
    crop: str
    disease: str
    confidence: Confidence = Field(ge=0, le=1)
    symptoms: str


class AnalysisResponse(BaseModel):
    decision: Decision
    crop: str
    disease: str
    confidence: Confidence = Field(ge=0, le=1)
    treatment: str | None = None
    source: str | None = None
    question: str | None = None
    needs_expert: bool