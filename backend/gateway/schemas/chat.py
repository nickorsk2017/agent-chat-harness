"""Chat request/response contracts.

Kept compatible with the frontend's existing shape so
``frontend/services/chatService.ts`` can adopt the real gateway without changing
its caller signature:

    request  : { "prompt": str }          (SendMessageRequest)
    response : ApiResponse[ChatReply]      where ChatReply.reply == SendMessageResponse.reply
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Payload the frontend sends when the user submits a message."""

    prompt: str = Field(..., min_length=1, description="The end-user prompt.")
    context: dict[str, str] = Field(
        default_factory=dict,
        description="Optional hints forwarded to the orchestrator "
        "(e.g. {'document_name': ..., 'document_text': ...} or {'image_path': ...}).",
    )
    thread_id: str | None = Field(
        default=None,
        description="Conversation thread key. Omit on the first message; the "
        "gateway generates one and echoes it in the reply. Send it back on "
        "follow-ups so the orchestrator keeps history and stored documents.",
    )


class ChatReply(BaseModel):
    """Successful payload: the orchestrator's merged answer."""

    reply: str = Field(..., description="Merged answer from the sub-agents.")
    subtasks: int = Field(
        default=0, description="How many sub-agent results were merged."
    )
    thread_id: str = Field(
        default="",
        description="Thread key this turn was checkpointed under; clients send "
        "it with the next message to continue the conversation.",
    )


class DeleteThreadReply(BaseModel):
    """Successful payload of a thread deletion."""

    thread_id: str = Field(..., description="The thread that was deleted.")
    deleted: bool = Field(default=True, description="Always true on success.")
