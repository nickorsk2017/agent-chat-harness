"""doc_analyzer MCP server entry point."""

from __future__ import annotations

from fastmcp import FastMCP

from doc_analyzer.config import settings
from doc_analyzer.tools import doc_tools

mcp = FastMCP("doc_analyzer")
doc_tools.register(mcp)


def main() -> None:
    mcp.run(transport=settings.transport)


if __name__ == "__main__":
    main()
