"""master_orchestrator MCP server entry point."""

from __future__ import annotations

from fastmcp import FastMCP

from master_orchestrator.config import settings
from master_orchestrator.tools import orchestrate_tools

mcp = FastMCP("master_orchestrator")
orchestrate_tools.register(mcp)


def main() -> None:
    mcp.run(transport=settings.transport)


if __name__ == "__main__":
    main()
