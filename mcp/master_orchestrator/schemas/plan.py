"""Domain models for orchestration: sub-tasks, their results, and the merge."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentName(str, Enum):
    WEB = "web_agent"
    DOC = "doc_analyzer"
    IMAGE = "image_analyzer"


class SubTask(BaseModel):
    """One unit of work routed to exactly one sub-agent."""

    agent: AgentName
    tool: str = Field(..., description="Tool name to invoke on the sub-agent.")
    arguments: dict[str, Any] = Field(default_factory=dict)


class SubTaskResult(BaseModel):
    task: SubTask
    ok: bool
    payload: Any | None = None
    error: str | None = None


class OrchestrationResult(BaseModel):
    prompt: str
    answer: str
    results: list[SubTaskResult] = Field(default_factory=list)
