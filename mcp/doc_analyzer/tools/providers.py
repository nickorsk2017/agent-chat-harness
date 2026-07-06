"""Providers behind doc_analyzer tools. Pure text -> LLM: the gateway extracts
PDF text in-memory and the orchestrator injects it into requests, so there is
no file IO here. Summarization and Q&A run through the real gemma LLM
(``google/gemma-4-31b-it`` via the NVIDIA endpoint). No mocks: a missing
``GEMMA_API_KEY`` raises ``LLMConfigError`` on first LLM use."""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel

from agent_core.llm import build_chat_model
from doc_analyzer.config import settings
from doc_analyzer.prompts.analyze import ANSWER_DOC, SUMMARIZE_DOC
from doc_analyzer.schemas.document import DocAnswer, DocSummary

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


async def summarize_document(doc: str, text: str, max_points: int) -> DocSummary:
    prompt = (
        SUMMARIZE_DOC.format(doc=doc, max_points=max_points)
        + f"\n\nDocument text:\n{text}"
    )
    structured = _chat_model().with_structured_output(DocSummary)
    return await structured.ainvoke(prompt)


async def ask_document(doc: str, text: str, question: str) -> DocAnswer:
    prompt = (
        ANSWER_DOC.format(doc=doc, question=question) + f"\n\nDocument text:\n{text}"
    )
    structured = _chat_model().with_structured_output(DocAnswer)
    return await structured.ainvoke(prompt)
