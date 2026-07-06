"""Chat business logic: process attachments, orchestrate a prompt, map the result.

PDFs are never persisted: their text is extracted in-memory (pypdf) and travels
to the orchestrator as ``document_name`` + ``document_text`` context. Images
still go through ``upload_dir`` (vision sub-agents need the bytes on disk).
"""

from __future__ import annotations

import io
import uuid
from pathlib import Path

from fastapi import UploadFile

from _common.env import Settings
from gateway.schemas.chat import ChatReply, ChatRequest, DeleteThreadReply
from gateway.services.orchestrator_client import OrchestratorClient

# Attachment policy: images and PDFs only, capped per file.
ALLOWED_TYPES: dict[str, str] = {
    "application/pdf": "pdf",
    "image/png": "image",
    "image/jpeg": "image",
    "image/webp": "image",
    "image/gif": "image",
}
_SUFFIX: dict[str, str] = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_FILE_BYTES = 15 * 1024 * 1024  # 15 MB


class GatewayError(Exception):
    """Domain-level failure: orchestration/upstream problems (HTTP 502)."""


class GatewayValidationError(GatewayError):
    """Client-side input problem — bad prompt or attachment (HTTP 400)."""


class ChatService:
    """Turns a ChatRequest (optionally with attachments) into a ChatReply."""

    def __init__(self, client: OrchestratorClient, settings: Settings | None = None) -> None:
        self._client = client
        self._settings = settings

    async def reply(self, request: ChatRequest) -> ChatReply:
        """Call the orchestrator and map its outcome to a ChatReply.

        Ensures a ``thread_id`` (generated when the client sent none) so every
        turn is checkpointed to a conversation thread, and echoes it back so
        the client can continue the same thread.

        Raises GatewayError on any orchestration failure so the router returns a
        ``status="Failed"`` envelope instead of leaking a 500.
        """
        thread_id = request.thread_id or uuid.uuid4().hex
        outcome = await self._client.orchestrate(
            request.prompt, request.context, thread_id=thread_id
        )
        if not outcome.ok:
            raise GatewayError(outcome.error or "orchestration failed")
        return ChatReply(
            reply=outcome.answer, subtasks=outcome.subtasks, thread_id=thread_id
        )

    async def delete_thread(self, thread_id: str) -> DeleteThreadReply:
        """Delete a conversation thread from the orchestrator's memory.

        Raises GatewayValidationError on a blank id (HTTP 400) and GatewayError
        when the orchestrator reports a failure (HTTP 502).
        """
        key = thread_id.strip()
        if not key:
            raise GatewayValidationError("thread_id is required")
        outcome = await self._client.delete_thread(key)
        if not outcome.ok:
            raise GatewayError(outcome.error or "thread deletion failed")
        return DeleteThreadReply(thread_id=key, deleted=True)

    async def reply_with_files(
        self,
        prompt: str,
        files: list[UploadFile],
        thread_id: str | None = None,
    ) -> ChatReply:
        """Persist attachments, build file context, then orchestrate.

        The prompt is mandatory (enforced again here — files never travel without
        one); files must be images or PDFs within the size cap.
        """
        text = prompt.strip()
        if not text:
            raise GatewayValidationError(
                "prompt is required — files cannot be sent without text"
            )
        context = await self.process_uploads(files)
        return await self.reply(
            ChatRequest(prompt=text, context=context, thread_id=thread_id)
        )

    async def process_uploads(self, files: list[UploadFile]) -> dict[str, str]:
        """Turn the (single) allowed upload into orchestrator context.

        PDF -> in-memory text extraction: {"document_name": ..., "document_text": ...}.
        Image -> saved under ``settings.upload_dir``: {"image_path": ...}.
        These are the exact keys the planner prompt routes on.
        """
        if self._settings is None:
            raise GatewayError("upload storage is not configured")
        if len(files) > 1:
            raise GatewayValidationError("only one file can be attached per message")

        context: dict[str, str] = {}
        for file in files:
            kind = ALLOWED_TYPES.get(file.content_type or "")
            if kind is None:
                raise GatewayValidationError(
                    f"unsupported file type {file.content_type!r} for "
                    f"{file.filename!r} — only images (png/jpg/webp/gif) and PDF"
                )
            data = await file.read()
            if len(data) > MAX_FILE_BYTES:
                raise GatewayValidationError(
                    f"{file.filename!r} exceeds the {MAX_FILE_BYTES // (1024 * 1024)} MB limit"
                )
            if kind == "pdf":
                name = file.filename or "document.pdf"
                context["document_name"] = name
                context["document_text"] = self._extract_pdf_text(name, data)
            else:
                upload_dir = Path(self._settings.upload_dir)
                upload_dir.mkdir(parents=True, exist_ok=True)
                target = upload_dir / f"{uuid.uuid4().hex}{_SUFFIX[file.content_type or '']}"
                target.write_bytes(data)
                context["image_path"] = str(target)
        return context

    @staticmethod
    def _extract_pdf_text(name: str, data: bytes) -> str:
        """Extract all text from PDF bytes in-memory; never touches disk."""
        from pypdf import PdfReader

        try:
            reader = PdfReader(io.BytesIO(data))
            chunks = [page.extract_text() or "" for page in reader.pages]
        except Exception as exc:  # noqa: BLE001 - malformed upload is a client error
            raise GatewayValidationError(f"could not read PDF {name!r}: {exc}") from exc
        text = "\n".join(c for c in chunks if c).strip()
        if not text:
            raise GatewayValidationError(
                f"{name!r} contains no extractable text — if it is a scanned "
                "document, attach the pages as images instead"
            )
        return text
