"""Chat REST endpoints. Thin: validate -> service -> envelope.

Fail-soft: every failure is returned as ``ApiResponse.fail(...)`` at HTTP 200,
never as an unstructured 500.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from _common.env import Settings, get_settings
from _common.schemas import ApiResponse
from gateway.schemas.chat import ChatReply, ChatRequest
from gateway.services.chat_service import ChatService, GatewayError
from gateway.services.orchestrator_client import build_orchestrator_client

router = APIRouter(prefix="/api", tags=["chat"])


def get_chat_service(settings: Settings = Depends(get_settings)) -> ChatService:
    """Build a ChatService from the config-selected orchestrator client."""
    return ChatService(build_orchestrator_client(settings))


@router.post("/chat", response_model=ApiResponse[ChatReply])
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ApiResponse[ChatReply]:
    """Send a user prompt to the orchestrator and return the merged answer."""
    try:
        reply = await service.reply(request)
        return ApiResponse.ok(reply)
    except GatewayError as exc:
        return ApiResponse.fail(str(exc))
    except Exception as exc:  # noqa: BLE001 - never leak a raw 500
        return ApiResponse.fail(f"unexpected error: {exc}")


@router.get("/health", response_model=ApiResponse[dict])
async def health() -> ApiResponse[dict]:
    """Liveness probe."""
    return ApiResponse.ok({"status": "up"})
