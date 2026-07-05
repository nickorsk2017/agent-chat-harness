"""MCP tools for doc_analyzer. Thin: validate -> provider -> envelope."""

from __future__ import annotations

from fastmcp import FastMCP

from doc_analyzer.schemas.document import (
    DocAnswer,
    DocSummary,
    ExtractedText,
)
from doc_analyzer.schemas.http import (
    AskRequest,
    ExtractRequest,
    SummarizeRequest,
)
from doc_analyzer.tools import providers
from agent_core.envelope import AgentResponse

AGENT = "doc_analyzer"


def register(mcp: FastMCP) -> None:
    @mcp.tool
    async def extract_text(request: ExtractRequest) -> AgentResponse[ExtractedText]:
        """Extract raw text from a document (PDF)."""
        try:
            result = await providers.extract_text(request.path, request.pages)
            return AgentResponse.ok(AGENT, result)
        except Exception as exc:  # noqa: BLE001
            return AgentResponse.fail(AGENT, str(exc))

    @mcp.tool
    async def summarize_document(request: SummarizeRequest) -> AgentResponse[DocSummary]:
        """Summarize a document into a brief and key points."""
        try:
            result = await providers.summarize_document(request.path, request.max_points)
            return AgentResponse.ok(AGENT, result)
        except Exception as exc:  # noqa: BLE001
            return AgentResponse.fail(AGENT, str(exc))

    @mcp.tool
    async def ask_document(request: AskRequest) -> AgentResponse[DocAnswer]:
        """Answer a natural-language question about a document."""
        try:
            result = await providers.ask_document(request.path, request.question)
            return AgentResponse.ok(AGENT, result)
        except Exception as exc:  # noqa: BLE001
            return AgentResponse.fail(AGENT, str(exc))
