"""Providers behind web_agent tools.

Live internet search (``search_web``, ``get_news``) is served by Tavily's hosted
MCP server (``tavily_search`` tool) — requires ``TAVILY_API_KEY``. Weather and
page-fetch remain best-effort LLM answers through the shared ``agent_core.llm``
factory (no mock fallback: missing ``GEMMA_API_KEY`` raises ``LLMConfigError``).
"""

from __future__ import annotations

import json
from urllib.parse import urlparse

from fastmcp import Client
from langchain_core.language_models.chat_models import BaseChatModel

from agent_core.llm import build_chat_model
from web_agent.config import settings
from web_agent.prompts.generate import PAGE_GEN, WEATHER_GEN
from web_agent.schemas.web import (
    NewsItem,
    NewsResult,
    SearchItem,
    SearchResult,
    Weather,
    WebPage,
)

_model: BaseChatModel | None = None


def _chat_model() -> BaseChatModel:
    global _model
    if _model is None:
        _model = build_chat_model(
            provider=settings.llm_provider,
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
    return _model


async def _tavily_results(query: str, max_results: int, topic: str) -> list[dict]:
    """Call Tavily MCP's ``tavily_search`` and return its ``results`` list."""
    url = settings.tavily_mcp_url()
    if not url:
        raise RuntimeError(
            "TAVILY_API_KEY is not set — live web search is unavailable."
        )
    async with Client(url) as client:
        res = await client.call_tool(
            "tavily_search",
            {"query": query, "max_results": max_results, "topic": topic},
        )
    data = getattr(res, "data", None)
    if not isinstance(data, dict):
        text = next(
            (b.text for b in res.content if getattr(b, "text", None)), "{}"
        )
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {"results": [{"title": "Tavily", "url": "", "content": text}]}
    results = data.get("results", [])
    return results if isinstance(results, list) else []


async def search_web(query: str, max_results: int) -> SearchResult:
    raw = await _tavily_results(query, max_results, topic="general")
    return SearchResult(
        query=query,
        results=[
            SearchItem(
                title=str(r.get("title", "")),
                url=str(r.get("url", "")),
                content=str(r.get("content", ""))[:1000],
            )
            for r in raw
        ],
    )


async def fetch_news(query: str, limit: int) -> NewsResult:
    raw = await _tavily_results(query, min(limit, 10), topic="news")
    return NewsResult(
        query=query,
        items=[
            NewsItem(
                title=str(r.get("title", "")),
                source=urlparse(str(r.get("url", ""))).netloc or "unknown",
                url=str(r.get("url", "")),
                summary=str(r.get("content", ""))[:500],
            )
            for r in raw
        ],
    )


async def fetch_weather(location: str) -> Weather:
    structured = _chat_model().with_structured_output(Weather)
    return await structured.ainvoke(WEATHER_GEN.format(location=location))


async def fetch_page(url: str) -> WebPage:
    structured = _chat_model().with_structured_output(WebPage)
    return await structured.ainvoke(PAGE_GEN.format(url=url))
