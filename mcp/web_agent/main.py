"""web_agent MCP server entry point."""

from __future__ import annotations

from fastmcp import FastMCP

from web_agent.config import settings
from web_agent.tools import web_tools

mcp = FastMCP("web_agent")
web_tools.register(mcp)


def main() -> None:
    mcp.run(transport=settings.transport)


if __name__ == "__main__":
    main()
