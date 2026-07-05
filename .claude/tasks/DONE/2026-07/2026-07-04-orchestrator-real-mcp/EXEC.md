# EXEC — 2026-07-04-orchestrator-real-mcp

## v1
Per PLAN v1:
1. `_common/env/settings.py` — `OrchestratorMode` += `"stdio"`; default
   `orchestrator_mode="stdio"` (R3). Added `orchestrator_command="python"` and
   `orchestrator_args` (`default_factory` -> `["-m","master_orchestrator.main"]`) (R4).
   Kept url/tool/timeout; regrouped comments by transport.
2. `gateway/services/orchestrator_client.py` — extracted shared
   `_run_orchestration(spec, tool, timeout, prompt, context)` holding the lazy
   `fastmcp` import, `asyncio.timeout`, `Client(spec)`, `call_tool(tool,{"request":...})`,
   `_parse_envelope(_extract(...))`, and TimeoutError/broad-except -> `ok=False`
   fail-soft (R2, R6). `HttpMcpOrchestratorClient.orchestrate` now delegates with its
   URL spec (behaviour identical). Added `StdioMcpOrchestratorClient(settings)` building
   spec `{"command","args"}` and delegating (R1). `build_orchestrator_client`: stdio->Stdio,
   http->Http, else Mock (R5). Module docstring updated to three impls.
3. `gateway/services/__init__.py` — export `StdioMcpOrchestratorClient`.
4. `backend/.env.example` — `GATEWAY_ORCHESTRATOR_MODE=stdio` + COMMAND/ARGS lines; mode
   comments document stdio/http/mock (R7).
5. `backend/CLAUDE.md` — rule 6 -> "Real by default, mock on demand"; Running snippet
   shows default real path + mock override (R7).

Unchanged: chat_service.py, routers/chat.py, schemas, mcp/ (Protocol stable).
Checks: `py_compile` OK on all 3 changed .py files (A3). Runtime smoke deferred —
pydantic/fastmcp absent in sandbox, PyPI blocked (see Validator).
