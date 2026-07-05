"""MCP tools for image_analyzer. Thin: validate -> provider -> envelope."""

from __future__ import annotations

from fastmcp import FastMCP

from image_analyzer.schemas.http import (
    DescribeRequest,
    DetectRequest,
    OcrRequest,
)
from image_analyzer.schemas.image import (
    Caption,
    DetectionResult,
    OcrResult,
)
from image_analyzer.tools import providers
from agent_core.envelope import AgentResponse

AGENT = "image_analyzer"


def register(mcp: FastMCP) -> None:
    @mcp.tool
    async def describe_image(request: DescribeRequest) -> AgentResponse[Caption]:
        """Produce a natural-language caption for an image."""
        try:
            result = await providers.describe_image(request.path)
            return AgentResponse.ok(AGENT, result)
        except Exception as exc:  # noqa: BLE001
            return AgentResponse.fail(AGENT, str(exc))

    @mcp.tool
    async def detect_objects(request: DetectRequest) -> AgentResponse[DetectionResult]:
        """Detect objects in an image above a confidence threshold."""
        try:
            result = await providers.detect_objects(request.path, request.min_confidence)
            return AgentResponse.ok(AGENT, result)
        except Exception as exc:  # noqa: BLE001
            return AgentResponse.fail(AGENT, str(exc))

    @mcp.tool
    async def ocr_image(request: OcrRequest) -> AgentResponse[OcrResult]:
        """Extract text from an image via OCR."""
        try:
            result = await providers.ocr_image(request.path, request.lang)
            return AgentResponse.ok(AGENT, result)
        except Exception as exc:  # noqa: BLE001
            return AgentResponse.fail(AGENT, str(exc))
