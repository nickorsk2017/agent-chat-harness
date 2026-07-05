"""MCP clients for the sub-agents.

The orchestrator talks to each sub-agent as an MCP client using the FastMCP
in-process/stdio ``Client``. Each ``call`` opens a session, invokes one tool,
and returns the parsed envelope. Calls are independent, so the orchestrator can
fire them concurrently with ``asyncio.gather`` (rule 6).
"""

from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client

from master_orchestrator.config import SubAgentEndpoint, settings


def _client_for(endpoint: SubAgentEndpoint) -> Client:
    """Build a FastMCP client for a sub-agent.

    Local dev: spawn the sub-agent module over stdio.
    Networked deploy: pass the endpoint URL instead.
    """
    if endpoint.url:
        return Client(endpoint.url)
    # FastMCP accepts a stdio server spec as {command, args}.
    return Client({"command": endpoint.command, "args": endpoint.args})


async def call_subagent(
    agent: str, tool: str, arguments: dict[str, Any]
) -> dict[str, Any]:
    """Invoke ``tool`` on ``agent`` and return its envelope as a dict.

    Never raises across the boundary — failures come back as an error envelope
    so one bad sub-agent can't sink the whole run.
    """
    endpoint = settings.subagents.get(agent)
    if endpoint is None:
        return {"status": "error", "agent": agent, "error": f"unknown agent {agent!r}"}

    try:
        async with asyncio.timeout(settings.subagent_timeout_s):
            async with _client_for(endpoint) as client:
                result = await client.call_tool(tool, {"request": arguments})
        return _parse(result, agent)
    except TimeoutError:
        return {"status": "error", "agent": agent, "error": "sub-agent timed out"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "agent": agent, "error": str(exc)}


def _parse(result: Any, agent: str) -> dict[str, Any]:
    """Normalize FastMCP tool output into a plain dict envelope."""
    data = getattr(result, "structured_content", None) or getattr(result, "data", None)
    if isinstance(data, dict):
        return data
    if data is not None:
        return {"status": "ok", "agent": agent, "data": data}
    # Fall back to text content blocks.
    content = getattr(result, "content", None)
    text = None
    if content:
        first = content[0]
        text = getattr(first, "text", None)
    return {"status": "ok", "agent": agent, "data": text}
