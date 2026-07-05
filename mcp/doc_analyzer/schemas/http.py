"""HTTP request / response contracts for doc_analyzer tools."""

from __future__ import annotations

from pydantic import BaseModel, Field

from doc_analyzer.schemas.document import (
    DocAnswer,
    DocSummary,
    ExtractedText,
)
from agent_core.envelope import AgentResponse


class ExtractRequest(BaseModel):
    path: str = Field(..., description="Path to the document (PDF) to extract.")
    pages: str | None = Field(default=None, description="Page range, e.g. '1-3' or '2'.")


class SummarizeRequest(BaseModel):
    path: str = Field(..., description="Path to the document to summarize.")
    max_points: int = Field(default=5, ge=1, le=20)


class AskRequest(BaseModel):
    path: str = Field(..., description="Path to the document to query.")
    question: str = Field(..., description="Natural-language question about the document.")


ExtractResponse = AgentResponse[ExtractedText]
SummarizeResponse = AgentResponse[DocSummary]
AskResponse = AgentResponse[DocAnswer]
