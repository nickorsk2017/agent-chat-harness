"""LangGraph orchestration: plan -> parallel dispatch -> synthesize.

The dispatch node runs every sub-task concurrently with ``asyncio.gather`` and
only returns once all have resolved (rule 6). A failed sub-agent yields an error
result but does not stop the others. Planning and synthesis are LangChain
chains; graph nodes and chains are traced by LangSmith automatically, the
custom per-task dispatch step via ``@traceable``.
"""

from __future__ import annotations

import asyncio
import json
from typing import TypedDict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph
from langsmith import traceable

from agent_core.envelope import Status
from agent_core.llm import build_chat_model
from master_orchestrator.config import settings
from master_orchestrator.prompts.orchestrate import SYNTHESIS_HUMAN, SYNTHESIS_SYSTEM
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


def build_synthesis_chain() -> Runnable:
    """Build the synthesis chain: prompt -> chat model -> merged answer text."""
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYNTHESIS_SYSTEM), ("human", SYNTHESIS_HUMAN)]
    )
    if settings.llm_provider == "mock" or not settings.llm_api_key:
        model = build_chat_model(
            provider="mock",
            mock_responses=["[mock-llm] merged answer from sub-agent results"],
        )
    else:
        model = build_chat_model(
            provider=settings.llm_provider,
            model=settings.llm_model,
            api_key=settings.llm_api_key,
        )
    return prompt | model | StrOutputParser()


_synthesis_chain: Runnable | None = None


async def _plan_node(state: OrchestratorState) -> OrchestratorState:
    tasks = await planner.plan(state["request"])
    return {"tasks": tasks}


@traceable(name="dispatch_subtask")
async def _run_subtask(task: SubTask) -> SubTaskResult:
    env = await call_subagent(task.agent.value, task.tool, task.arguments)
    ok = env.status is Status.OK
    return SubTaskResult(
        task=task,
        ok=ok,
        payload=env.data if ok else None,
        error=env.error if not ok else None,
    )


async def _dispatch_node(state: OrchestratorState) -> OrchestratorState:
    tasks = state.get("tasks", [])
    results = await asyncio.gather(*(_run_subtask(t) for t in tasks)) if tasks else []
    return {"results": list(results)}


async def _synthesize_node(state: OrchestratorState) -> OrchestratorState:
    global _synthesis_chain
    if _synthesis_chain is None:
        _synthesis_chain = build_synthesis_chain()
    results = state.get("results", [])
    answer: str = await _synthesis_chain.ainvoke(
        {
            "prompt": state["request"].prompt,
            "results": json.dumps(
                [r.model_dump(mode="json") for r in results], ensure_ascii=False
            ),
        }
    )
    return {"answer": answer}


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
