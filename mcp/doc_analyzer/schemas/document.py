"""Domain models for doc_analyzer."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DocSummary(BaseModel):
    doc: str
    summary: str
    key_points: list[str] = Field(default_factory=list)


class DocAnswer(BaseModel):
    doc: str
    question: str
    answer: str
    cited_sections: list[str] = Field(default_factory=list)
