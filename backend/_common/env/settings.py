"""Environment-backed settings (pydantic-settings). Config, not constants.

All URLs, modes, timeouts and origins come from the environment (prefix
``GATEWAY_``) or a local ``.env`` file. No secrets are hardcoded.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

OrchestratorMode = Literal["mock", "http"]


class Settings(BaseSettings):
    """Gateway settings. Loaded from env / ``.env`` with the ``GATEWAY_`` prefix."""

    model_config = SettingsConfigDict(
        env_prefix="GATEWAY_", env_file=".env", extra="ignore"
    )

    # --- HTTP server ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- CORS (the frontend origin[s]) ---
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # --- Orchestrator MCP integration ---
    # "mock" -> in-process stub (default, zero external processes).
    # "http" -> connect to the running master_orchestrator MCP server over HTTP.
    orchestrator_mode: OrchestratorMode = "mock"
    orchestrator_mcp_url: str = "http://127.0.0.1:8100/mcp"
    orchestrator_tool: str = "orchestrate"
    orchestrator_timeout_s: float = 30.0

    # --- Persistence (scaffolded; not on the mock chat path) ---
    database_url: str = "sqlite+aiosqlite:///./gateway.db"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton (safe to use as a FastAPI dependency)."""
    return Settings()
