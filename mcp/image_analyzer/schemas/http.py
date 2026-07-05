"""HTTP request / response contracts for image_analyzer tools."""

from __future__ import annotations

from pydantic import BaseModel, Field

from image_analyzer.schemas.image import (
    Caption,
    DetectionResult,
    OcrResult,
)
from agent_core.envelope import AgentResponse


class DescribeRequest(BaseModel):
    path: str = Field(..., description="Path to the image to describe.")


class DetectRequest(BaseModel):
    path: str = Field(..., description="Path to the image to run detection on.")
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class OcrRequest(BaseModel):
    path: str = Field(..., description="Path to the image to run OCR on.")
    lang: str = Field(default="eng", description="OCR language code, e.g. 'eng'.")


DescribeResponse = AgentResponse[Caption]
DetectResponse = AgentResponse[DetectionResult]
OcrResponse = AgentResponse[OcrResult]
