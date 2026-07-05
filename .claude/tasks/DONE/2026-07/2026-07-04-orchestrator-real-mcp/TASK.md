# TASK — 2026-07-04-orchestrator-real-mcp
owner: Engineer
immutable: true

## Requirements
- R1: The gateway must reach the `master_orchestrator` MCP server over **stdio**
  (spawn it as a subprocess), mirroring the existing sub-agent pattern in
  `mcp/master_orchestrator/tools/subagent_client.py` — `Client({"command", "args"})`.
  NOT over HTTP.
- R2: Add a real `StdioMcpOrchestratorClient` in
  `backend/gateway/services/orchestrator_client.py` that invokes the configured
  `orchestrate` tool with `{"request": {"prompt", "context"}}` and reuses the
  existing `_parse_envelope`/`_extract` to return an `OrchestrationOutcome`.
  It must fail soft: never raise across its boundary (timeout / spawn / any error
  -> `ok=False`), same contract as the http client.
- R3: `GATEWAY_ORCHESTRATOR_MODE` gains `"stdio"` and its **default becomes `stdio`**
  so the real MCP orchestrator is the active path out of the box (replacing the
  mock). `"http"` and `"mock"` remain selectable.
- R4: Spawn command is config, not constants (backend/CLAUDE.md rule 4): new settings
  `orchestrator_command` (default `python`) and `orchestrator_args`
  (default `["-m", "master_orchestrator.main"]`), env `GATEWAY_ORCHESTRATOR_COMMAND`
  / `GATEWAY_ORCHESTRATOR_ARGS`. Reuse existing `orchestrator_tool` + `orchestrator_timeout_s`.
- R5: `MockOrchestratorClient` is retained and still selected by
  `GATEWAY_ORCHESTRATOR_MODE=mock` (offline / test path). `build_orchestrator_client`
  routes mode -> {stdio, http, mock}.
- R6: The gateway must not import any `mcp/` package (backend/CLAUDE.md rule 7);
  it only spawns the module as a subprocess via config-supplied command/args.
  `fastmcp` stays a lazy import inside the call path so the package imports without it.
- R7: Update `backend/.env.example` and `backend/CLAUDE.md` (rule 6 + Running) to
  reflect stdio-real-by-default with mock as the opt-in offline mode.

## Acceptance
- A1: With no env overrides, `build_orchestrator_client(Settings())` returns the
  stdio client; `mode=http` -> http client; `mode=mock` -> mock client.
- A2: `StdioMcpOrchestratorClient.orchestrate` builds the spec
  `{"command": <cmd>, "args": <args>}`, calls `orchestrate` with the request envelope,
  and maps a well-formed `AgentResponse` to `ok=True, answer, subtasks`; an error
  envelope / timeout / spawn failure maps to `ok=False`.
- A3: All changed Python files compile (`py_compile`) and the module imports with
  `fastmcp` absent (lazy import preserved).

## Constraints
- Services/ remains the orchestrator boundary; ChatService/router unchanged.
- No new runtime dependencies (fastmcp already pinned in pyproject).
- Fail-soft contract and `_parse_envelope`/`_extract` reused, not duplicated.
