"""Domain models for image_analyzer."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ImageMeta(BaseModel):
    path: str
    width: int
    height: int
    format: str


class Caption(BaseModel):
    path: str
    caption: str


class Detection(BaseModel):
    label: str
    confidence: float
    box: list[float] = Field(default_factory=list)


class DetectionResult(BaseModel):
    path: str
    detections: list[Detection] = Field(default_factory=list)


class OcrResult(BaseModel):
    path: str
    text: str
