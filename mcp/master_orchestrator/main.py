"""master_orchestrator MCP server entry point."""

from __future__ import annotations
import os
from fastmcp import FastMCP
from master_orchestrator.config import settings


def _export_langsmith_env() -> None:
    """Export LangSmith settings so LangChain/LangGraph auto-trace runs (R6)."""
    if not settings.langsmith_tracing:
        return
    os.environ["LANGSMITH_TRACING"] = "true"
    if settings.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project


_export_langsmith_env()

from master_orchestrator.tools import orchestrate_tools  # noqa: E402 — after tracing env

mcp = FastMCP("master_orchestrator")
orchestrate_tools.register(mcp)


def main() -> None:
    mcp.run(transport=settings.transport)


if __name__ == "__main__":
    main()
