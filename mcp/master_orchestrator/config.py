"""master_orchestrator settings, including the sub-agent MCP client registry."""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SubAgentEndpoint(BaseModel):
    """How to reach one sub-agent's MCP server.

    For local dev the orchestrator spawns each sub-agent over stdio using
    ``command`` + ``args``. For a networked deploy set ``url`` (SSE / HTTP) and
    the client will connect to that instead.
    """

    name: str
    command: str = "python"
    args: list[str] = Field(default_factory=list)
    url: str | None = None


class OrchestratorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ORCHESTRATOR_", env_file=".env", extra="ignore"
    )

    host: str = "127.0.0.1"
    port: int = 8100
    transport: str = "stdio"

    # LLM used for task splitting + final synthesis.
    llm_provider: str = "mock"
    llm_model: str = "mock-model"
    llm_api_key: str | None = None

    # Hard cap so one slow sub-agent can't hang the whole request (rule 6).
    subagent_timeout_s: float = 30.0

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
