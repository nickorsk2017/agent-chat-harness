"""The orchestrator's own MCP tool: one prompt in, one merged answer out."""

from __future__ import annotations

from fastmcp import FastMCP

from master_orchestrator.db import history
from master_orchestrator.schemas.http import OrchestrateRequest
from master_orchestrator.schemas.plan import OrchestrationResult
from master_orchestrator.tools.graph import run_orchestration
from agent_core.envelope import AgentResponse

AGENT = "master_orchestrator"


def register(mcp: FastMCP) -> None:
    @mcp.tool
    async def orchestrate(request: OrchestrateRequest) -> AgentResponse[OrchestrationResult]:
        """Split the prompt into sub-tasks, run the relevant sub-agents in
        parallel, and return one merged answer."""
        try:
            result = await run_orchestration(request)
            history.record(result)
            return AgentResponse.ok(AGENT, result, subtasks=len(result.results))
        except Exception as exc:  # noqa: BLE001
            return AgentResponse.fail(AGENT, str(exc))
