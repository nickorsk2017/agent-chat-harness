# PLAN — 2026-07-04-orchestrator-real-mcp

## v1

### Approach
The real MCP client already exists for HTTP. Add a sibling **stdio** client that
spawns `master_orchestrator` as a subprocess, and flip the default mode so the real
path replaces the mock (R1, R3). Both real transports differ only in the *spec*
passed to `fastmcp.Client` (URL string vs `{command, args}` dict — the exact idiom
already proven in `mcp/.../subagent_client.py`). Factor the shared call/parse/
fail-soft body into one helper so Http and Stdio share it (R2, no duplication).

### Files
1. `backend/_common/env/settings.py`
   - Extend `OrchestratorMode` literal with `"stdio"`; set default `orchestrator_mode = "stdio"` (R3).
   - Add `orchestrator_command: str = "python"` and
     `orchestrator_args: list[str]` via `Field(default_factory=lambda: ["-m", "master_orchestrator.main"])` (R4).
   - Keep `orchestrator_mcp_url`, `orchestrator_tool`, `orchestrator_timeout_s`.
2. `backend/gateway/services/orchestrator_client.py`
   - Introduce a private async helper `_run_orchestration(spec, tool, timeout, prompt, context)`
     holding the lazy `fastmcp` import, `asyncio.timeout`, `Client(spec)` open,
     `call_tool(tool, {"request": {...}})`, then `_parse_envelope(_extract(result))`,
     and the TimeoutError / broad-except -> `ok=False` fail-soft mapping (R2, R6).
   - Refactor `HttpMcpOrchestratorClient.orchestrate` to delegate to the helper with
     its URL spec (behaviour preserved).
   - Add `StdioMcpOrchestratorClient(settings)`: stores `spec = {"command": settings.orchestrator_command,
     "args": settings.orchestrator_args}`, tool, timeout; `orchestrate` delegates to the helper.
   - Extend `build_orchestrator_client`: `"stdio"` -> Stdio, `"http"` -> Http, else Mock (R5).
3. `backend/gateway/services/__init__.py` — export `StdioMcpOrchestratorClient`.
4. `backend/.env.example` — `GATEWAY_ORCHESTRATOR_MODE=stdio`; document command/args;
   note mock is the offline opt-in (R7).
5. `backend/CLAUDE.md` — rule 6 reworded: real (stdio) orchestrator by default,
   mock via `GATEWAY_ORCHESTRATOR_MODE=mock`; update the Running snippet (R7).

### Non-changes
- `chat_service.py`, `routers/chat.py`, schemas: the `OrchestratorClient` Protocol is
  unchanged, so the service/router/DI are untouched (Constraints).
- `mcp/` subsystem: orchestrator already defaults to stdio transport; its `main()`
  serves stdio when spawned. No mcp/ edits (user chose gateway-over-stdio).

### Risks / notes
- Subprocess needs `master_orchestrator` importable in its env (documented install
  path `pip install -e master_orchestrator`); command/args are config so a deploy can
  point elsewhere. No cwd coupling, matching subagent_client.
- Sandbox lacks pydantic/fastmcp and PyPI is blocked -> runtime smoke not possible
  here; Validator uses py_compile + a stubbed logic harness for factory + parse.
