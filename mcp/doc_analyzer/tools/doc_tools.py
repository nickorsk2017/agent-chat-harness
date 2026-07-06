"""MCP tools for doc_analyzer. Thin: validate -> provider -> envelope."""

from __future__ import annotations

from fastmcp import FastMCP

from doc_analyzer.schemas.document import DocAnswer, DocSummary
from doc_analyzer.schemas.http import AskRequest, SummarizeRequest
from doc_analyzer.tools import providers
from agent_core.envelope import AgentResponse

AGENT = "doc_analyzer"


def register(mcp: FastMCP) -> None:
    @mcp.tool
    async def summarize_document(request: SummarizeRequest) -> AgentResponse[DocSummary]:
        """Summarize the given document text into a brief and key points."""
        try:
            result = await providers.summarize_document(
                request.doc, request.text, request.max_points
            )
            return AgentResponse.ok(AGENT, result)
        except Exception as exc:  # noqa: BLE001
            return AgentResponse.fail(AGENT, str(exc))

    @mcp.tool
    async def ask_document(request: AskRequest) -> AgentResponse[DocAnswer]:
        """Answer a natural-language question about the given document text."""
        try:
            result = await providers.ask_document(
                request.doc, request.text, request.question
            )
            return AgentResponse.ok(AGENT, result)
        except Exception as exc:  # noqa: BLE001
            return AgentResponse.fail(AGENT, str(exc))
