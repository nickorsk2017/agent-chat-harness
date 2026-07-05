"""Turns a user prompt into a list of parallel sub-tasks.

Ships with a deterministic keyword planner so the system runs with no LLM key.
Set an LLM provider in ``config.py`` to route via LangChain instead.
"""

from __future__ import annotations

from master_orchestrator.config import settings
from master_orchestrator.schemas.http import OrchestrateRequest
from master_orchestrator.schemas.plan import AgentName, SubTask

_WEATHER_HINTS = ("weather", "forecast", "temperature", "rain", "погода")
_NEWS_HINTS = ("news", "headline", "latest", "новости")


def plan(request: OrchestrateRequest) -> list[SubTask]:
    """Rule-based fan-out planner (mock)."""
    if settings.llm_provider != "mock" and settings.llm_api_key:
        return _plan_with_llm(request)

    prompt = request.prompt.lower()
    tasks: list[SubTask] = []

    if any(h in prompt for h in _WEATHER_HINTS):
        location = request.context.get("location", "current location")
        tasks.append(
            SubTask(agent=AgentName.WEB, tool="get_weather",
                    arguments={"location": location})
        )
    if any(h in prompt for h in _NEWS_HINTS) or not tasks:
        tasks.append(
            SubTask(agent=AgentName.WEB, tool="get_news",
                    arguments={"query": request.prompt, "limit": 5})
        )
    if "pdf_path" in request.context:
        tasks.append(
            SubTask(agent=AgentName.DOC, tool="summarize_document",
                    arguments={"path": request.context["pdf_path"], "max_points": 5})
        )
    if "image_path" in request.context:
        tasks.append(
            SubTask(agent=AgentName.IMAGE, tool="describe_image",
                    arguments={"path": request.context["image_path"]})
        )
    return tasks


def _plan_with_llm(request: OrchestrateRequest) -> list[SubTask]:  # pragma: no cover
    """Real planner: use a structured-output LangChain chain against
    ``prompts.orchestrate.PLANNER_SYSTEM`` to emit list[SubTask]."""
    raise NotImplementedError("Wire a LangChain structured-output planner here.")
