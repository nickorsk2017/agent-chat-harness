"""Providers behind doc_analyzer tools. Mock implementations ship by default;
swap in real PDF extraction (pypdf) and an LLM chain keyed off ``settings``
without touching tools."""

from __future__ import annotations

from doc_analyzer.config import settings
from doc_analyzer.schemas.document import (
    DocAnswer,
    DocSummary,
    ExtractedText,
)


async def extract_text(path: str, pages: str | None = None) -> ExtractedText:
    if settings.extract_provider == "mock":
        span = f" (pages {pages})" if pages else ""
        text = (
            f"[mock] Extracted text from {path}{span}.\n"
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "This document discusses the quarterly results and outlook."
        )
        return ExtractedText(path=path, text=text, pages=12)
    # Real path:
    # from pypdf import PdfReader
    # reader = PdfReader(path); ... extract per-page text for the requested range.
    raise NotImplementedError("Wire real PDF extraction here (e.g. pypdf).")


async def summarize_document(path: str, max_points: int) -> DocSummary:
    if settings.llm_provider == "mock" or not settings.llm_api_key:
        points = [f"[mock] Key point {i + 1} from {path}." for i in range(max_points)]
        return DocSummary(
            path=path,
            summary=f"[mock] Concise summary of {path}.",
            key_points=points,
        )
    # Real path:
    # extract text (pypdf) -> feed into an LLM chain with the SUMMARIZE_DOC prompt.
    raise NotImplementedError("Wire a real LLM summarization chain here.")


async def ask_document(path: str, question: str) -> DocAnswer:
    if settings.llm_provider == "mock" or not settings.llm_api_key:
        return DocAnswer(
            path=path,
            question=question,
            answer=f"[mock] Answer to '{question}' based on {path}.",
            cited_pages=[1, 3],
        )
    # Real path:
    # extract text (pypdf) -> LLM chain with the ANSWER_DOC prompt -> parse citations.
    raise NotImplementedError("Wire a real LLM question-answering chain here.")
