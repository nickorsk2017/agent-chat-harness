# VALIDATION — 2026-07-04-orchestrator-real-mcp
validation_version: 1
result: PASS

## v1 — PASS
Verified the real logic via a stub harness (pydantic/fastmcp absent, PyPI blocked in
sandbox — environment limit, not a code defect) exercising the ACTUAL module code:

- R1/R2/A2: `StdioMcpOrchestratorClient` builds spec `{"command":"python","args":["-m",
  "master_orchestrator.main"]}` (== the `subagent_client` stdio idiom), wires tool/timeout,
  and delegates to shared `_run_orchestration`. Real `.orchestrate()` with fastmcp absent
  returns `ok=False, error="fastmcp not available: ..."` — fail-soft holds, no raise. ✔
- R3/A1: `build_orchestrator_client` -> stdio→Stdio, http→Http, mock→Mock; `Settings`
  default `orchestrator_mode` is `stdio` (source-confirmed) so the real path is default. ✔
- R4: `orchestrator_command` / `orchestrator_args` present with env-backed defaults via
  `Field(default_factory=...)`; url/tool/timeout retained. Config, not constants. ✔
- R5: `MockOrchestratorClient` retained; mode=mock selects it; still returns ok. ✔
- R6/A3: module imports with `fastmcp` absent (lazy import inside `_run_orchestration`);
  gateway spawns via config command/args, imports no `mcp/` package. `_parse_envelope`
  ok/error/empty/malformed all correct. ✔
- R7: `.env.example` (MODE=stdio + COMMAND/ARGS + mode comments) and `backend/CLAUDE.md`
  (rule 6 "Real by default, mock on demand"; Running snippet) updated. ✔
- A3: `py_compile` clean on all 5 changed files + unchanged consumers (chat_service,
  routers/chat). Protocol unchanged -> service/router/DI untouched.

Deferred to Engineer (host, not sandbox): live end-to-end smoke requires
`pip install -e backend[dev]` + `pip install -e mcp/master_orchestrator`, then
`uvicorn gateway.main:app` and `POST /api/chat` — expected to spawn the orchestrator
over stdio and return a real merged answer.

No blocking issues. open_issues empty.
