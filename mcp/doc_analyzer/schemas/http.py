"""HTTP request / response contracts for doc_analyzer tools.

Requests carry the document TEXT directly (extracted by the gateway and
injected by the orchestrator's dispatch step) — doc_analyzer never reads files.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from doc_analyzer.schemas.document import DocAnswer, DocSummary
from agent_core.envelope import AgentResponse


class SummarizeRequest(BaseModel):
    doc: str = Field(..., description="Document name (thread memory key).")
    text: str = Field(..., min_length=1, description="Full document text to summarize.")
    max_points: int = Field(default=5, ge=1, le=20)


class AskRequest(BaseModel):
    doc: str = Field(..., description="Document name (thread memory key).")
    text: str = Field(..., min_length=1, description="Full document text to query.")
    question: str = Field(..., description="Natural-language question about the document.")


SummarizeResponse = AgentResponse[DocSummary]
AskResponse = AgentResponse[DocAnswer]
