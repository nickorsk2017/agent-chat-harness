"""web_agent settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class WebAgentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WEB_AGENT_", env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 8101
    transport: str = "stdio"  # "stdio" | "sse" | "streamable-http"

    # Providers: "mock" ships by default; set real keys to go live.
    search_provider: str = "mock"
    search_api_key: str | None = None
    weather_provider: str = "mock"
    weather_api_key: str | None = None
    request_timeout_s: float = 15.0


settings = WebAgentSettings()
