"""web_agent settings."""

from __future__ import annotations

from agent_core.llm import DEFAULT_MODEL, NOVITA_BASE_URL
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WebAgentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WEB_AGENT_", env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 8101
    transport: str = "stdio"  # "stdio" | "sse" | "streamable-http"

    # LLM: gemma via Novita's OpenAI-compatible endpoint. GEMMA_API_KEY
    # (env) is REQUIRED; there is no mock LLM fallback.
    llm_provider: str = "novita"
    llm_model: str = DEFAULT_MODEL
    llm_base_url: str = NOVITA_BASE_URL
    llm_api_key: str | None = Field(default=None, validation_alias="GEMMA_API_KEY")
    request_timeout_s: float = 15.0

    # Live web search: Tavily's hosted MCP server. TAVILY_API_KEY (env) is
    # required for search_web/get_news; other tools work without it.
    tavily_api_key: str | None = Field(default=None, validation_alias="TAVILY_API_KEY")
    tavily_mcp_base: str = "https://mcp.tavily.com/mcp/"

    def tavily_mcp_url(self) -> str | None:
        if not self.tavily_api_key:
            return None
        return f"{self.tavily_mcp_base}?tavilyApiKey={self.tavily_api_key}"


settings = WebAgentSettings()
