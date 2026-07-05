"""LangChain chat-model factory shared by all agents.

Returns a real chat model when an API key is configured, otherwise a
deterministic fake model so the whole system runs with zero external keys.
"""

from __future__ import annotations

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.language_models.chat_models import BaseChatModel


def build_chat_model(
    *,
    provider: str = "mock",
    model: str = "mock-model",
    api_key: str | None = None,
    temperature: float = 0.0,
    mock_responses: list[str] | None = None,
) -> BaseChatModel:
    """Build a LangChain chat model.

    Swap this out for ``ChatOpenAI`` / ``ChatAnthropic`` etc. by setting
    ``provider`` and ``api_key`` in an agent's ``config.py``.
    ``mock_responses`` seeds the fake model's canned replies (mock path only).
    """
    if provider == "mock" or not api_key:
        return FakeListChatModel(responses=mock_responses or ["[mock-llm] response"])

    if provider == "openai":  # pragma: no cover - requires extra + key
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, api_key=api_key, temperature=temperature)

    if provider == "anthropic":  # pragma: no cover - requires extra + key
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=model, api_key=api_key, temperature=temperature)

    raise ValueError(f"Unknown LLM provider: {provider!r}")
