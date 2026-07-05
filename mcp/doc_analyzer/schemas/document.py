"""Domain models for doc_analyzer."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentMeta(BaseModel):
    path: str
    pages: int
    title: str


class ExtractedText(BaseModel):
    path: str
    text: str
    pages: int


class DocSummary(BaseModel):
    path: str
    summary: str
    key_points: list[str] = Field(default_factory=list)


class DocAnswer(BaseModel):
    path: str
    question: str
    answer: str
    cited_pages: list[int] = Field(default_factory=list)
