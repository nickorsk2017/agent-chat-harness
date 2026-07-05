"""doc_analyzer settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class DocAnalyzerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DOC_ANALYZER_", env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 8102
    transport: str = "stdio"  # "stdio" | "sse" | "streamable-http"

    # Providers: "mock" ships by default; set real keys to go live.
    extract_provider: str = "mock"
    llm_provider: str = "mock"
    llm_api_key: str | None = None
    request_timeout_s: float = 30.0


settings = DocAnalyzerSettings()
