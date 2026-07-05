"""Client to the master_orchestrator MCP agent.

The gateway is an MCP *client* of the orchestrator's MCP server. It invokes the
``orchestrate`` tool with ``{"request": {"prompt", "context"}}`` and reads the
orchestrator's ``AgentResponse[OrchestrationResult]`` envelope, extracting the
merged ``answer``.

Three implementations behind one Protocol, selected by config:
- ``StdioMcpOrchestratorClient`` — real MCP-over-stdio; spawns the orchestrator as a
  subprocess (fastmcp Client on a ``{command, args}`` spec). This is the default.
- ``HttpMcpOrchestratorClient``  — real MCP-over-HTTP (fastmcp Client on a URL).
- ``MockOrchestratorClient``     — in-process stub; zero external processes (tests).

The client never raises across its boundary: failures are returned as an
``OrchestrationOutcome`` with ``ok=False`` so the service layer can map them into
the fail-soft envelope.
"""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel

from _common.env import Settings


class OrchestrationOutcome(BaseModel):
    """Normalized result of one orchestration call."""

    ok: bool
    answer: str = ""
    subtasks: int = 0
    error: str | None = None


class OrchestratorClient(Protocol):
    """Anything that can turn a prompt into a merged answer."""

    async def orchestrate(
        self, prompt: str, context: dict[str, str] | None = None
    ) -> OrchestrationOutcome: ...


def _parse_envelope(payload: Any) -> OrchestrationOutcome:
    """Map the orchestrator's AgentResponse[OrchestrationResult] dict -> outcome.

    Envelope shape (from agent_core.envelope.AgentResponse):
        {status: "ok"|"error", agent, data: {prompt, answer, results:[...]}, error, meta}
    """
    if not isinstance(payload, dict):
        return OrchestrationOutcome(ok=False, error="malformed orchestrator payload")

    status = payload.get("status")
    if status == "error":
        return OrchestrationOutcome(
            ok=False, error=payload.get("error") or "orchestrator error"
        )

    data = payload.get("data") or {}
    if isinstance(data, dict):
        answer = str(data.get("answer") or "")
        results = data.get("results") or []
        subtasks = len(results) if isinstance(results, list) else 0
    else:  # data came back as a bare string
        answer, subtasks = str(data), 0

    if not answer:
        return OrchestrationOutcome(ok=False, error="empty answer from orchestrator")
    return OrchestrationOutcome(ok=True, answer=answer, subtasks=subtasks)


async def _run_orchestration(
    spec: Any, tool: str, timeout: float, prompt: str, context: dict[str, str] | None
) -> OrchestrationOutcome:
    """Invoke the orchestrator ``tool`` via a FastMCP ``Client(spec)``.

    ``spec`` is whatever FastMCP's ``Client`` accepts as a server: a URL string
    (HTTP) or a ``{"command", "args"}`` dict (stdio subprocess). Shared by both
    real transports so the call/parse/fail-soft body lives in exactly one place.
    Never raises across the boundary — every failure becomes ``ok=False``.
    """
    # Imported lazily so the package imports even if fastmcp isn't installed
    # (e.g. when running purely in mock mode).
    try:
        import asyncio

        from fastmcp import Client
    except ImportError as exc:  # pragma: no cover - env issue
        return OrchestrationOutcome(ok=False, error=f"fastmcp not available: {exc}")

    request = {"prompt": prompt, "context": context or {}}
    try:
        async with asyncio.timeout(timeout):
            async with Client(spec) as client:
                result = await client.call_tool(tool, {"request": request})
        return _parse_envelope(_extract(result))
    except TimeoutError:
        return OrchestrationOutcome(ok=False, error="orchestrator timed out")
    except Exception as exc:  # noqa: BLE001 - fail soft across the boundary
        return OrchestrationOutcome(ok=False, error=str(exc))


class StdioMcpOrchestratorClient:
    """Real client: spawns the orchestrator's MCP server over stdio.

    Mirrors how the orchestrator itself reaches its sub-agents
    (``mcp/master_orchestrator/tools/subagent_client.py``): hand FastMCP a
    ``{command, args}`` spec and it launches the module as a subprocess. The
    gateway never imports any ``mcp/`` package — it only spawns the configured
    command (backend/CLAUDE.md rule 7).
    """

    def __init__(self, settings: Settings) -> None:
        self._spec = {
            "command": settings.orchestrator_command,
            "args": settings.orchestrator_args,
        }
        self._tool = settings.orchestrator_tool
        self._timeout = settings.orchestrator_timeout_s

    async def orchestrate(
        self, prompt: str, context: dict[str, str] | None = None
    ) -> OrchestrationOutcome:
        return await _run_orchestration(
            self._spec, self._tool, self._timeout, prompt, context
        )


class HttpMcpOrchestratorClient:
    """Real client: connects to the orchestrator's MCP server over HTTP."""

    def __init__(self, settings: Settings) -> None:
        self._url = settings.orchestrator_mcp_url
        self._tool = settings.orchestrator_tool
        self._timeout = settings.orchestrator_timeout_s

    async def orchestrate(
        self, prompt: str, context: dict[str, str] | None = None
    ) -> OrchestrationOutcome:
        return await _run_orchestration(
            self._url, self._tool, self._timeout, prompt, context
        )


def _extract(result: Any) -> Any:
    """Pull the structured envelope out of a FastMCP tool result."""
    data = getattr(result, "structured_content", None)
    if data is None:
        data = getattr(result, "data", None)
    if data is not None:
        return data
    content = getattr(result, "content", None)
    if content:
        return getattr(content[0], "text", None)
    return None


class MockOrchestratorClient:
    """In-process stub — mirrors mcp/'s 'mock by default' rule.

    Returns a deterministic merged answer without any external process, so the
    gateway runs and is testable with zero dependencies.
    """

    async def orchestrate(
        self, prompt: str, context: dict[str, str] | None = None
    ) -> OrchestrationOutcome:
        text = prompt.strip()
        answer = (
            f"(mock orchestrator) Merged answer for: “{text}”. "
            "The web, PDF and image sub-agents would run in parallel and their "
            "results would be synthesized here."
        )
        return OrchestrationOutcome(ok=True, answer=answer, subtasks=0)


def build_orchestrator_client(settings: Settings) -> OrchestratorClient:
    """Factory: pick the client implementation from settings.orchestrator_mode."""
    if settings.orchestrator_mode == "stdio":
        return StdioMcpOrchestratorClient(settings)
    if settings.orchestrator_mode == "http":
        return HttpMcpOrchestratorClient(settings)
    return MockOrchestratorClient()
