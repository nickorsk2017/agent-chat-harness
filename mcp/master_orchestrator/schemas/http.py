"""HTTP request / response contracts for the orchestrator."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OrchestrateRequest(BaseModel):
    prompt: str = Field(..., description="The end-user prompt to fulfil.")
    context: dict[str, str] = Field(
        default_factory=dict,
        description="Optional hints, e.g. {'pdf_path': ..., 'image_path': ...}.",
    )
