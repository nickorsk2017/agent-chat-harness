"""Providers behind image_analyzer tools. Mock implementations ship by default;
swap in a real vision model and an OCR engine (e.g. tesseract) keyed off
``settings`` without touching tools."""

from __future__ import annotations

from image_analyzer.config import settings
from image_analyzer.schemas.image import (
    Caption,
    Detection,
    DetectionResult,
    OcrResult,
)


async def describe_image(path: str) -> Caption:
    if settings.vision_provider == "mock" or not settings.vision_api_key:
        return Caption(
            path=path,
            caption=f"[mock] A photo showing the main subject of {path} in a clear setting.",
        )
    # Real path:
    # send the image to a vision model with the DESCRIBE_IMAGE prompt.
    raise NotImplementedError("Wire a real vision model here.")


async def detect_objects(path: str, min_confidence: float) -> DetectionResult:
    if settings.vision_provider == "mock" or not settings.vision_api_key:
        candidates = [
            Detection(label="person", confidence=0.92, box=[0.10, 0.15, 0.40, 0.80]),
            Detection(label="dog", confidence=0.71, box=[0.55, 0.40, 0.85, 0.90]),
            Detection(label="ball", confidence=0.44, box=[0.60, 0.70, 0.70, 0.82]),
        ]
        detections = [d for d in candidates if d.confidence >= min_confidence]
        return DetectionResult(path=path, detections=detections)
    # Real path:
    # run an object-detection vision model and filter by min_confidence.
    raise NotImplementedError("Wire a real object-detection vision model here.")


async def ocr_image(path: str, lang: str) -> OcrResult:
    if settings.ocr_provider == "mock":
        return OcrResult(
            path=path,
            text=f"[mock] OCR text ({lang}) extracted from {path}: Hello World.",
        )
    # Real path:
    # from PIL import Image; import pytesseract
    # pytesseract.image_to_string(Image.open(path), lang=lang)
    raise NotImplementedError("Wire a real OCR engine here (e.g. tesseract).")
