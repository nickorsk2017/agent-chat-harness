"""Planner: a LangChain structured-output chain that emits the sub-task plan.

Real providers run ``with_structured_output(Plan)`` over the planner prompt.
The mock provider pipes a fake chat model seeded with a canned ``Plan`` JSON
through a ``PydanticOutputParser`` (fake models cannot bind tools, so the
tool-calling structured-output path is unavailable there) — deterministic and
key-free.
"""

from __future__ import annotations

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from agent_core.llm import build_chat_model
from master_orchestrator.config import settings
from master_orchestrator.prompts.orchestrate import PLANNER_HUMAN, PLANNER_SYSTEM
from master_orchestrator.schemas.http import OrchestrateRequest
from master_orchestrator.schemas.plan import AgentName, Plan, SubTask

# Canned mock plan: one fixed web_agent/get_news sub-task (static, zero keys).
_MOCK_PLAN = Plan(
    tasks=[
        SubTask(
            agent=AgentName.WEB,
            tool="get_news",
            arguments={"query": "latest news", "limit": 5},
        )
    ]
)


def build_planner_chain() -> Runnable:
    """Build the planning chain: prompt -> chat model -> ``Plan``."""
    prompt = ChatPromptTemplate.from_messages(
        [("system", PLANNER_SYSTEM), ("human", PLANNER_HUMAN)]
    )
    if settings.llm_provider == "mock" or not settings.llm_api_key:
        model = build_chat_model(
            provider="mock", mock_responses=[_MOCK_PLAN.model_dump_json()]
        )
        return prompt | model | PydanticOutputParser(pydantic_object=Plan)
    model = build_chat_model(
        provider=settings.llm_provider,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
    )
    return prompt | model.with_structured_output(Plan)


_chain: Runnable | None = None


async def plan(request: OrchestrateRequest) -> list[SubTask]:
    """Split the request into parallel sub-tasks via the planning chain."""
    global _chain
    if _chain is None:
        _chain = build_planner_chain()
    result: Plan = await _chain.ainvoke(
        {"prompt": request.prompt, "context": request.context}
    )
    return result.tasks
