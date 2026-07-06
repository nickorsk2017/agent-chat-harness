"""Thread-memory tests: reducers, gateway-extracted document capture, persistence.

Run over an ``InMemorySaver`` checkpointer — the Postgres saver shares the
exact same ``BaseCheckpointSaver`` contract, so graph-level memory semantics
are covered without a database.
"""

from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agent_core.envelope import AgentResponse
from master_orchestrator.schemas.http import OrchestrateRequest
from master_orchestrator.schemas.plan import AgentName, SubTask
from master_orchestrator.tools import graph as graph_mod

CV_TEXT = "TEXT OF CV: python, fastapi"


class FakeSynthesis:
    """Stands in for the LLM synthesis chain; records its inputs."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def ainvoke(self, inputs: dict) -> str:
        self.calls.append(inputs)
        return "ANSWER"


@pytest.fixture
def fake_env(monkeypatch):
    synth = FakeSynthesis()
    monkeypatch.setattr(graph_mod, "_synthesis_chain", synth)

    plan_calls: list[dict] = []

    async def fake_plan(request, history="", documents=""):
        plan_calls.append(
            {"context": dict(request.context), "history": history, "documents": documents}
        )
        return []

    monkeypatch.setattr(graph_mod.planner, "plan", fake_plan)

    subagent_calls: list[tuple[str, str, dict]] = []

    async def fake_call_subagent(agent, tool, arguments):
        subagent_calls.append((agent, tool, arguments))
        request = arguments["request"]
        return AgentResponse.ok(
            agent,
            {
                "doc": request.get("doc", ""),
                "summary": f"SUMMARY OF {request.get('doc', '')}",
                "key_points": [],
            },
        )

    monkeypatch.setattr(graph_mod, "call_subagent", fake_call_subagent)
    return synth, plan_calls, subagent_calls


def test_merge_documents_reducer():
    assert graph_mod.merge_documents({"a": "1"}, {"b": "2"}) == {"a": "1", "b": "2"}
    assert graph_mod.merge_documents(None, {"b": "2"}) == {"b": "2"}
    assert graph_mod.merge_documents({"a": "1"}, None) == {"a": "1"}
    # right side wins on collision (newer upload)
    assert graph_mod.merge_documents({"a": "old"}, {"a": "new"}) == {"a": "new"}


def test_split_document_context():
    docs, hints = graph_mod._split_document_context(
        {"document_name": "cv.pdf", "document_text": CV_TEXT, "lang": "ru"}
    )
    assert docs == {"cv.pdf": CV_TEXT}
    assert hints == {"new_document": "cv.pdf", "lang": "ru"}
    # no document attached -> context passes through untouched
    docs, hints = graph_mod._split_document_context({"image_path": "/data/i.png"})
    assert docs == {} and hints == {"image_path": "/data/i.png"}


async def _invoke(g, prompt: str, context: dict, thread_id: str):
    request = OrchestrateRequest(prompt=prompt, context=context, thread_id=thread_id)
    return await g.ainvoke(
        {"request": request, "messages": [HumanMessage(content=prompt)]},
        {"configurable": {"thread_id": thread_id}},
    )


async def test_document_text_and_history_persist_across_turns(fake_env):
    synth, plan_calls, subagent_calls = fake_env
    g = graph_mod.build_graph(InMemorySaver())

    # Turn 1: prompt + gateway-extracted PDF text -> stored without any sub-agent.
    final1 = await _invoke(
        g,
        "Проанализируй мой CV",
        {"document_name": "cv.pdf", "document_text": CV_TEXT},
        "t1",
    )
    assert final1["documents"] == {"cv.pdf": CV_TEXT}
    assert final1["answer"] == "ANSWER"
    assert subagent_calls == []  # no extract round-trip anymore
    # Planner saw the lightweight hint, never the raw text.
    assert plan_calls[0]["context"] == {"new_document": "cv.pdf"}

    # Turn 2: follow-up without a file — answered from the thread.
    final2 = await _invoke(g, "Какие технологии в моем CV?", {}, "t1")
    last = synth.calls[-1]
    assert CV_TEXT in last["documents"]  # stored text reaches synthesis
    assert "Проанализируй мой CV" in last["history"]  # prior user turn
    assert "ANSWER" in last["history"]  # prior assistant turn
    assert "cv.pdf" in plan_calls[-1]["documents"]  # planner sees stored doc
    assert plan_calls[-1]["context"] == {}  # no stale new_document hint
    assert len(final2["messages"]) == 4  # 2 turns x (human + ai)
    assert subagent_calls == []


async def test_thread_isolation(fake_env):
    synth, _, _ = fake_env
    g = graph_mod.build_graph(InMemorySaver())
    await _invoke(
        g, "hi", {"document_name": "a.pdf", "document_text": "AAA"}, "thread-A"
    )
    final = await _invoke(g, "yo", {}, "thread-B")
    assert synth.calls[-1]["documents"] == ""  # no leakage of A's document
    assert synth.calls[-1]["history"] == ""
    assert len(final["messages"]) == 2


async def test_dispatch_injects_stored_text_into_doc_tasks(fake_env, monkeypatch):
    synth, _, subagent_calls = fake_env

    async def plan_with_summarize(request, history="", documents=""):
        return [
            SubTask(
                agent=AgentName.DOC,
                tool="summarize_document",
                arguments={"request": {"doc": "cv.pdf", "max_points": 5}},
            )
        ]

    monkeypatch.setattr(graph_mod.planner, "plan", plan_with_summarize)
    g = graph_mod.build_graph(InMemorySaver())
    final = await _invoke(
        g,
        "Проанализируй мое CV",
        {"document_name": "cv.pdf", "document_text": CV_TEXT},
        "t-inject",
    )
    # The sub-agent received the stored text although the planner never had it.
    assert subagent_calls == [
        (
            "doc_analyzer",
            "summarize_document",
            {"request": {"doc": "cv.pdf", "max_points": 5, "text": CV_TEXT}},
        )
    ]
    # Result is merged, but reported against the PLANNED task: the injected
    # text must not leak into the synthesis `results` JSON.
    assert len(final["results"]) == 1
    assert "text" not in final["results"][0].task.arguments["request"]
    assert CV_TEXT not in synth.calls[-1]["results"]


async def test_doc_task_falls_back_to_latest_document(fake_env, monkeypatch):
    _, _, subagent_calls = fake_env

    async def plan_with_bad_name(request, history="", documents=""):
        return [
            SubTask(
                agent=AgentName.DOC,
                tool="ask_document",
                arguments={"request": {"doc": "WRONG.pdf", "question": "q?"}},
            )
        ]

    monkeypatch.setattr(graph_mod.planner, "plan", plan_with_bad_name)
    g = graph_mod.build_graph(InMemorySaver())
    await _invoke(
        g,
        "q?",
        {"document_name": "cv.pdf", "document_text": CV_TEXT},
        "t-fallback",
    )
    request = subagent_calls[0][2]["request"]
    assert request["doc"] == "cv.pdf"  # corrected to the stored document
    assert request["text"] == CV_TEXT
