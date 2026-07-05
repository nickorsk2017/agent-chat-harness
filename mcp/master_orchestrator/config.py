"""master_orchestrator settings, including the sub-agent MCP client registry."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SubAgentEndpoint(BaseModel):
    """How to reach one sub-agent's MCP server.

    For local dev the orchestrator spawns each sub-agent over stdio using
    ``command`` + ``args``. For a networked deploy set ``url`` and the client
    connects over streamable HTTP instead.
    """

    name: str
    command: str = "python"
    args: list[str] = Field(default_factory=list)
    url: str | None = None

    def to_connection(self) -> dict[str, Any]:
        """Map this endpoint to a ``langchain-mcp-adapters`` Connection dict."""
        if self.url:
            return {"url": self.url, "transport": "http"}
        return {"command": self.command, "args": self.args, "transport": "stdio"}


class OrchestratorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ORCHESTRATOR_", env_file=".env", extra="ignore"
    )

    transport: str = "stdio"

    # LLM used for task splitting + final synthesis.
    llm_provider: str = "mock"
    llm_model: str = "mock-model"
    llm_api_key: str | None = None

    # Hard cap so one slow sub-agent can't hang the whole request (rule 6).
    subagent_timeout_s: float = 30.0

    # LangSmith tracing — canonical LANGSMITH_* env names (not ORCHESTRATOR_-prefixed).
    langsmith_tracing: bool = Field(
        default=False, validation_alias="LANGSMITH_TRACING"
    )
    langsmith_api_key: str | None = Field(
        default=None, validation_alias="LANGSMITH_API_KEY"
    )
    langsmith_project: str = Field(
        default="agent-chat", validation_alias="LANGSMITH_PROJECT"
    )

    @property
    def subagents(self) -> dict[str, SubAgentEndpoint]:
        return {
            "web_agent": SubAgentEndpoint(
                name="web_agent", args=["-m", "web_agent.main"]
            ),
            "doc_analyzer": SubAgentEndpoint(
                name="doc_analyzer", args=["-m", "doc_analyzer.main"]
            ),
            "image_analyzer": SubAgentEndpoint(
                name="image_analyzer", args=["-m", "image_analyzer.main"]
            ),
        }


settings = OrchestratorSettings()
