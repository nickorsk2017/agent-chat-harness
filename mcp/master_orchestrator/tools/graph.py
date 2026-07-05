"""LangGraph orchestration: plan -> parallel dispatch -> synthesize.

The dispatch node runs every sub-task concurrently with ``asyncio.gather`` and
only returns once all have resolved (rule 6). A failed sub-agent yields an error
result but does not stop the others.
"""

from __future__ import annotations

import asyncio
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from master_orchestrator.schemas.http import OrchestrateRequest
from master_orchestrator.schemas.plan import (
    OrchestrationResult,
    SubTask,
    SubTaskResult,
)
from master_orchestrator.tools import planner
from master_orchestrator.tools.subagent_client import call_subagent


class OrchestratorState(TypedDict, total=False):
    request: OrchestrateRequest
    tasks: list[SubTask]
    results: list[SubTaskResult]
    answer: str


async def _plan_node(state: OrchestratorState) -> OrchestratorState:
    tasks = planner.plan(state["request"])
    return {"tasks": tasks}


async def _dispatch_node(state: OrchestratorState) -> OrchestratorState:
    tasks = state.get("tasks", [])

    async def run(task: SubTask) -> SubTaskResult:
        env = await call_subagent(task.agent.value, task.tool, task.arguments)
        ok = env.get("status") == "ok"
        return SubTaskResult(
            task=task,
            ok=ok,
            payload=env.get("data") if ok else None,
            error=env.get("error") if not ok else None,
        )

    results = await asyncio.gather(*(run(t) for t in tasks)) if tasks else []
    return {"results": list(results)}


async def _synthesize_node(state: OrchestratorState) -> OrchestratorState:
    results = state.get("results", [])
    return {"answer": _merge(state["request"], results)}


def _merge(request: OrchestrateRequest, results: list[SubTaskResult]) -> str:
    """Deterministic merge (mock). Replace with a LangChain synthesis chain
    over ``prompts.orchestrate.SYNTHESIS_SYSTEM`` for LLM-quality output."""
    if not results:
        return f"No sub-tasks were needed for: {request.prompt}"
    lines = [f"Results for: {request.prompt}", ""]
    for r in results:
        agent = r.task.agent.value
        if r.ok:
            lines.append(f"- [{agent}/{r.task.tool}] {_summarize(r.payload)}")
        else:
            lines.append(f"- [{agent}/{r.task.tool}] FAILED: {r.error}")
    return "\n".join(lines)


def _summarize(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("summary", "answer", "caption", "text", "condition"):
            if key in payload:
                return str(payload[key])
        return ", ".join(f"{k}={v}" for k, v in list(payload.items())[:3])
    return str(payload)


def build_graph():
    graph = StateGraph(OrchestratorState)
    graph.add_node("plan", _plan_node)
    graph.add_node("dispatch", _dispatch_node)
    graph.add_node("synthesize", _synthesize_node)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "dispatch")
    graph.add_edge("dispatch", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile()


_COMPILED = build_graph()


async def run_orchestration(request: OrchestrateRequest) -> OrchestrationResult:
    final: OrchestratorState = await _COMPILED.ainvoke({"request": request})
    return OrchestrationResult(
        prompt=request.prompt,
        answer=final.get("answer", ""),
        results=final.get("results", []),
    )
