"""HTTP request / response contracts for the orchestrator."""

from __future__ import annotations

from pydantic import BaseModel, Field

from agent_core.envelope import AgentResponse
from master_orchestrator.schemas.plan import OrchestrationResult


class OrchestrateRequest(BaseModel):
    prompt: str = Field(..., description="The end-user prompt to fulfil.")
    context: dict[str, str] = Field(
        default_factory=dict,
        description="Optional hints, e.g. {'pdf_path': ..., 'image_path': ...}.",
    )


OrchestrateResponse = AgentResponse[OrchestrationResult]
