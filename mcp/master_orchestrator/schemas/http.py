"""HTTP request / response contracts for the orchestrator."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OrchestrateRequest(BaseModel):
    prompt: str = Field(..., description="The end-user prompt to fulfil.")
    context: dict[str, str] = Field(
        default_factory=dict,
        description="Optional hints, e.g. {'document_name': ..., "
        "'document_text': ...} for gateway-extracted PDFs or "
        "{'image_path': ...} for saved images.",
    )
    thread_id: str = Field(
        default="default",
        description="Conversation thread key for LangGraph checkpointing; "
        "turns sharing a thread_id share history and stored documents.",
    )
