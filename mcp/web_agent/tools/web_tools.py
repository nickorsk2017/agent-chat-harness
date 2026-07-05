"""MCP tools for web_agent. Thin: validate -> provider -> envelope."""

from __future__ import annotations

from fastmcp import FastMCP

from agent_core.envelope import AgentResponse
from web_agent.schemas.http import (
    FetchRequest,
    NewsRequest,
    WeatherRequest,
)
from web_agent.schemas.web import NewsResult, Weather, WebPage
from web_agent.tools import providers

AGENT = "web_agent"


def register(mcp: FastMCP) -> None:
    @mcp.tool
    async def get_news(request: NewsRequest) -> AgentResponse[NewsResult]:
        """Fetch recent news items about a topic."""
        try:
            result = await providers.fetch_news(request.query, request.limit)
            return AgentResponse.ok(AGENT, result)
        except Exception as exc:  # noqa: BLE001
            return AgentResponse.fail(AGENT, str(exc))

    @mcp.tool
    async def get_weather(request: WeatherRequest) -> AgentResponse[Weather]:
        """Fetch current weather for a location."""
        try:
            return AgentResponse.ok(AGENT, await providers.fetch_weather(request.location))
        except Exception as exc:  # noqa: BLE001
            return AgentResponse.fail(AGENT, str(exc))

    @mcp.tool
    async def fetch_url(request: FetchRequest) -> AgentResponse[WebPage]:
        """Fetch and extract text from a web page."""
        try:
            return AgentResponse.ok(AGENT, await providers.fetch_page(request.url))
        except Exception as exc:  # noqa: BLE001
            return AgentResponse.fail(AGENT, str(exc))
