"""Chat business logic: orchestrate a prompt, map the result to ChatReply."""

from __future__ import annotations

from gateway.schemas.chat import ChatReply, ChatRequest
from gateway.services.orchestrator_client import OrchestratorClient


class GatewayError(Exception):
    """Domain-level failure the router maps into a fail-soft envelope."""


class ChatService:
    """Turns a ChatRequest into a ChatReply via the orchestrator client."""

    def __init__(self, client: OrchestratorClient) -> None:
        self._client = client

    async def reply(self, request: ChatRequest) -> ChatReply:
        """Call the orchestrator and map its outcome to a ChatReply.

        Raises GatewayError on any orchestration failure so the router returns a
        ``status="Failed"`` envelope instead of leaking a 500.
        """
        outcome = await self._client.orchestrate(request.prompt, request.context)
        if not outcome.ok:
            raise GatewayError(outcome.error or "orchestration failed")
        return ChatReply(reply=outcome.answer, subtasks=outcome.subtasks)
