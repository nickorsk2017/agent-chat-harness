"""Providers behind web_agent tools. Mock implementations ship by default;
swap in real HTTP calls (httpx) keyed off ``settings`` without touching tools."""

from __future__ import annotations

from web_agent.config import settings
from web_agent.schemas.web import NewsItem, NewsResult, Weather, WebPage


async def fetch_news(query: str, limit: int) -> NewsResult:
    if settings.search_provider == "mock" or not settings.search_api_key:
        items = [
            NewsItem(
                title=f"[mock] Headline {i + 1} about {query}",
                source="mock-wire",
                url=f"https://example.com/{query}/{i + 1}",
                summary=f"Mock summary {i + 1} for {query}.",
            )
            for i in range(limit)
        ]
        return NewsResult(query=query, items=items)
    raise NotImplementedError("Wire a real search API here (e.g. httpx + provider).")


async def fetch_weather(location: str) -> Weather:
    if settings.weather_provider == "mock" or not settings.weather_api_key:
        return Weather(location=location, temperature_c=21.0, condition="Clear", humidity_pct=48)
    raise NotImplementedError("Wire a real weather API here.")


async def fetch_page(url: str) -> WebPage:
    if settings.search_provider == "mock":
        return WebPage(url=url, title="[mock] Page", text=f"Mock body of {url}.")
    # Real path:
    # async with httpx.AsyncClient(timeout=settings.request_timeout_s) as c:
    #     r = await c.get(url); r.raise_for_status(); ...
    raise NotImplementedError("Wire real httpx fetch here.")
