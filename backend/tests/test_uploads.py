"""Upload processing: PDFs become in-memory text context, images go to disk."""

from __future__ import annotations

import io
from types import SimpleNamespace

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from gateway.services.chat_service import ChatService, GatewayValidationError


def _upload(name: str, content_type: str, data: bytes) -> UploadFile:
    return UploadFile(
        file=io.BytesIO(data),
        filename=name,
        headers=Headers({"content-type": content_type}),
    )


def _service(tmp_path) -> ChatService:
    return ChatService(client=None, settings=SimpleNamespace(upload_dir=str(tmp_path)))


async def test_pdf_is_extracted_in_memory_and_never_saved(tmp_path, monkeypatch):
    service = _service(tmp_path)
    monkeypatch.setattr(
        ChatService, "_extract_pdf_text", staticmethod(lambda name, data: "CV TEXT")
    )
    context = await service.process_uploads(
        [_upload("cv.pdf", "application/pdf", b"%PDF-fake")]
    )
    assert context == {"document_name": "cv.pdf", "document_text": "CV TEXT"}
    assert list(tmp_path.iterdir()) == []  # nothing written to upload_dir


async def test_image_still_saved_to_upload_dir(tmp_path):
    service = _service(tmp_path)
    context = await service.process_uploads([_upload("pic.png", "image/png", b"\x89PNG")])
    saved = list(tmp_path.iterdir())
    assert len(saved) == 1 and saved[0].suffix == ".png"
    assert context == {"image_path": str(saved[0])}


async def test_malformed_pdf_is_a_validation_error(tmp_path):
    service = _service(tmp_path)
    with pytest.raises(GatewayValidationError, match="could not read PDF"):
        await service.process_uploads(
            [_upload("bad.pdf", "application/pdf", b"not a pdf at all")]
        )
    assert list(tmp_path.iterdir()) == []


async def test_unsupported_type_rejected(tmp_path):
    service = _service(tmp_path)
    with pytest.raises(GatewayValidationError, match="unsupported file type"):
        await service.process_uploads([_upload("x.txt", "text/plain", b"hi")])
