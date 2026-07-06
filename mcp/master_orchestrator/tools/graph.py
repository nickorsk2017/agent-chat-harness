"""LangGraph orchestration: plan -> parallel dispatch -> synthesize, with
thread memory.

The dispatch node runs every sub-task concurrently with ``asyncio.gather`` and
only returns once all have resolved (rule 6). A failed sub-agent yields an error
result but does not stop the others. Planning and synthesis are LangChain
chains; graph nodes and chains are traced by LangSmith automatically, the
custom per-task dispatch step via ``@traceable``.

Memory: the graph is compiled ONCE with a checkpointer (Postgres when
``ORCHESTRATOR_DATABASE_URL`` is set, in-memory otherwise) and invoked with
``configurable.thread_id``. Two channels persist across turns:

- ``messages``  — conversation history (``add_messages`` reducer).
- ``documents`` — ``{document_name: text}``. PDF text is extracted by the
  GATEWAY (in-memory, never on disk) and arrives as ``document_name`` +
  ``document_text`` context keys; the plan node stores it deterministically
  and shows the planner only ``new_document: <name>``. Dispatch injects the
  stored text into doc_analyzer arguments, so the planner LLM never carries
  document text and follow-up turns answer from the thread without
  re-uploading the file.

Per-turn channels (request/tasks/results/answer) are overwritten each turn.
"""

from __future__ import annotations

import asyncio
import json
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langsmith import traceable

from agent_core.envelope import Status
from agent_core.llm import build_chat_model
from master_orchestrator.config import settings
from master_orchestrator.db.checkpointer import get_checkpointer
from master_orchestrator.prompts.orchestrate import SYNTHESIS_HUMAN, SYNTHESIS_SYSTEM
from master_orchestrator.schemas.http import OrchestrateRequest
from master_orchestrator.schemas.plan import (
    AgentName,
    OrchestrationResult,
    SubTask,
    SubTaskResult,
)
from master_orchestrator.tools import planner
from master_orchestrator.tools.subagent_client import call_subagent


def merge_documents(
    left: dict[str, str] | None, right: dict[str, str] | None
) -> dict[str, str]:
    """Reducer for the persistent ``documents`` channel: accumulate by name."""
    return {**(left or {}), **(right or {})}


class OrchestratorState(TypedDict, total=False):
    # Persistent across turns (checkpointer):
    messages: Annotated[list[AnyMessage], add_messages]
    documents: Annotated[dict[str, str], merge_documents]
    # Per-turn (overwritten on every invocation):
    request: OrchestrateRequest
    tasks: list[SubTask]
    results: list[SubTaskResult]
    answer: str


def format_history(messages: list[AnyMessage], limit: int | None = None) -> str:
    """Render the last ``limit`` messages as ``role: text`` lines for prompts."""
    limit = limit or settings.history_max_messages
    lines: list[str] = []
    for msg in messages[-limit:]:
        role = "user" if msg.type == "human" else "assistant"
        text = msg.text() if callable(getattr(msg, "text", None)) else str(msg.content)
        lines.append(f"{role}: {text}")
    return "\n".join(lines)


def format_documents(documents: dict[str, str], with_text: bool) -> str:
    """Render stored documents: names only (planner) or capped text (synthesis)."""
    if not documents:
        return ""
    if not with_text:
        return "\n".join(f"- {name}" for name in documents)
    cap = settings.document_max_chars
    parts: list[str] = []
    for name, text in documents.items():
        body = text if len(text) <= cap else text[:cap] + "\n[...truncated]"
        parts.append(f"### {name}\n{body}")
    return "\n\n".join(parts)


def build_synthesis_chain() -> Runnable:
    """Build the synthesis chain: prompt -> chat model -> merged answer text."""
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYNTHESIS_SYSTEM), ("human", SYNTHESIS_HUMAN)]
    )
    model = build_chat_model(
        provider=settings.llm_provider,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )
    return prompt | model | StrOutputParser()


_synthesis_chain: Runnable | None = None


def _split_document_context(
    context: dict[str, str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Split gateway context into ``(new_documents, planner_hints)``.

    ``document_text`` (paired with ``document_name``) is stored verbatim in the
    thread's ``documents`` channel; the planner only ever sees the lightweight
    hint ``new_document: <name>`` — never the text itself.
    """
    text = context.get("document_text")
    if text is None:
        return {}, dict(context)
    name = context.get("document_name") or "document.pdf"
    hints = {
        k: v for k, v in context.items() if k not in ("document_text", "document_name")
    }
    hints["new_document"] = name
    return {name: text}, hints


async def _plan_node(state: OrchestratorState) -> OrchestratorState:
    # messages already contains the current prompt (appended on invoke) —
    # history for the planner is everything before it.
    history = format_history(list(state.get("messages", []))[:-1])
    new_docs, hints = _split_document_context(state["request"].context)
    # Deterministic memorization (no LLM, no sub-agent): new document text goes
    # straight into the persistent channel before planning.
    documents = format_documents(state.get("documents", {}), with_text=False)
    request = state["request"].model_copy(update={"context": hints})
    tasks = await planner.plan(request, history=history, documents=documents)
    update: OrchestratorState = {"tasks": tasks}
    if new_docs:
        update["documents"] = new_docs
    return update


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


def _inject_doc_text(task: SubTask, documents: dict[str, str]) -> SubTask:
    """Fill a doc_analyzer task's ``text`` from the thread's stored documents.

    The planner references documents by name only; the actual text is injected
    here so the planner LLM never round-trips document content. Falls back to
    the most recently stored document when the name doesn't match.
    """
    if task.agent is not AgentName.DOC or not documents:
        return task
    request = task.arguments.get("request")
    if not isinstance(request, dict) or request.get("text"):
        return task
    doc = str(request.get("doc") or "")
    text = documents.get(doc)
    if text is None:  # planner typo'd/omitted the name -> latest document
        doc, text = next(reversed(documents.items()))
    new_request = {**request, "doc": doc, "text": text}
    return task.model_copy(update={"arguments": {"request": new_request}})


async def _dispatch_node(state: OrchestratorState) -> OrchestratorState:
    documents = state.get("documents", {})
    planned = list(state.get("tasks", []))
    calls = [_inject_doc_text(t, documents) for t in planned]
    raw = (
        list(await asyncio.gather(*(_run_subtask(t) for t in calls))) if calls else []
    )
    # Report results against the PLANNED tasks (no injected text) so the full
    # document body never leaks into the synthesis `results` JSON — stored
    # documents are already passed to synthesis separately.
    results = [res.model_copy(update={"task": task}) for res, task in zip(raw, planned)]
    return {"results": results}


async def _synthesize_node(state: OrchestratorState) -> OrchestratorState:
    global _synthesis_chain
    if _synthesis_chain is None:
        _synthesis_chain = build_synthesis_chain()
    results = state.get("results", [])
    answer: str = await _synthesis_chain.ainvoke(
        {
            "prompt": state["request"].prompt,
            "history": format_history(list(state.get("messages", []))[:-1]),
            "documents": format_documents(state.get("documents", {}), with_text=True),
            "results": json.dumps(
                [r.model_dump(mode="json") for r in results], ensure_ascii=False
            ),
        }
    )
    return {"answer": answer, "messages": [AIMessage(content=answer)]}


def build_graph(checkpointer: BaseCheckpointSaver | None = None):
    graph = StateGraph(OrchestratorState)
    graph.add_node("plan", _plan_node)
    graph.add_node("dispatch", _dispatch_node)
    graph.add_node("synthesize", _synthesize_node)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "dispatch")
    graph.add_edge("dispatch", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile(checkpointer=checkpointer)


_graph = None
_graph_lock = asyncio.Lock()


async def _get_graph():
    """Compile the graph once per process, bound to the checkpointer."""
    global _graph
    if _graph is None:
        async with _graph_lock:
            if _graph is None:
                _graph = build_graph(await get_checkpointer())
    return _graph


async def run_orchestration(request: OrchestrateRequest) -> OrchestrationResult:
    graph = await _get_graph()
    final: OrchestratorState = await graph.ainvoke(
        {"request": request, "messages": [HumanMessage(content=request.prompt)]},
        {"configurable": {"thread_id": request.thread_id}},
    )
    return OrchestrationResult(
        prompt=request.prompt,
        answer=final.get("answer", ""),
        results=final.get("results", []),
    )
