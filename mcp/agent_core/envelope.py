"""Shared MCP response envelope used across all agents.

Every tool returns an ``AgentResponse`` so the orchestrator can merge results
uniformly and never has an exception cross the MCP boundary (rule 7).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Status(str, Enum):
    OK = "ok"
    ERROR = "error"
    PARTIAL = "partial"


class AgentResponse(BaseModel, Generic[T]):
    """Uniform envelope returned by every tool / sub-agent."""

    status: Status = Status.OK
    agent: str = Field(..., description="Name of the agent that produced this result.")
    data: T | None = Field(default=None, description="Domain payload on success.")
    error: str | None = Field(default=None, description="Human-readable error, if any.")
    meta: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def ok(cls, agent: str, data: T, **meta: Any) -> "AgentResponse[T]":
        return cls(status=Status.OK, agent=agent, data=data, meta=meta)

    @classmethod
    def fail(cls, agent: str, error: str, **meta: Any) -> "AgentResponse[T]":
        return cls(status=Status.ERROR, agent=agent, error=error, meta=meta)
