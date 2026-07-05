# EXEC — 2026-07-04-simplify-orchestrator-langchain

## v1
(Resumed after a crashed Executor run: P1-P4 were already on disk; verified against
PLAN.md v1 — consistent, kept as-is. This run completed P5-P9.)

### Per-step summary
- P1 (pre-crash, verified): `master_orchestrator/pyproject.toml` — floors bumped to
  langchain/core/langgraph >=1.0, added `langchain-mcp-adapters>=0.2.2`,
  `langsmith>=0.8.16`; `agent_core/llm.py` — optional `mock_responses` param seeds
  `FakeListChatModel` (default behavior unchanged).
- P2 (pre-crash, verified): `schemas/plan.py` — `Plan` wrapper added; `schemas/http.py` —
  dead `OrchestrateResponse` alias + its imports removed; `prompts/orchestrate.py` —
  `PLANNER_HUMAN` / `SYNTHESIS_HUMAN` templates added (prompts stay data).
- P3 (pre-crash, verified): `config.py` — `host`/`port` removed; LangSmith fields with
  canonical `LANGSMITH_*` validation aliases; `SubAgentEndpoint.to_connection()` maps to
  adapters Connection dicts (stdio / streamable http).
- P4 (pre-crash, verified): `tools/planner.py` — keyword hints + `NotImplementedError`
  stub deleted; `build_planner_chain()` per D3: real -> `with_structured_output(Plan)`,
  mock -> fake model seeded with canned one-task `web_agent/get_news` Plan JSON ->
  `PydanticOutputParser(Plan)`; `plan()` is now async over a lazy module-level chain.
- P5: `tools/subagent_client.py` rewritten on `MultiServerMCPClient` (connections from
  `settings.subagents` via `to_connection()`, `handle_tool_errors=False`). Tool
  resolution via `get_tools(server_name=agent)` + exact name match (see Deviations).
  Arg shape: `{"request": arguments}` when the tool schema exposes `request`, flat dict
  fallback per PLAN risk note. Output validated into `AgentResponse` at the boundary
  (D8); per-call `asyncio.timeout(settings.subagent_timeout_s)`; unknown agent, unknown
  tool, timeout, and transport errors all return `AgentResponse.fail(...)` — nothing
  raises (rules 6/7).
- P6: `tools/graph.py` — `_merge`/`_summarize` deleted; plan node awaits the planner
  chain (also fixes the pre-crash `plan()` sync-call mismatch); dispatch node gathers
  `@traceable`-decorated `_run_subtask` coroutines building `SubTaskResult` from typed
  `AgentResponse.status/data/error`; synthesize node awaits `build_synthesis_chain()`
  (SYNTHESIS_SYSTEM + SYNTHESIS_HUMAN -> chat model -> `StrOutputParser`; mock = canned
  string, same chain shape); results serialized generically via
  `model_dump(mode="json")` — no payload-key lists.
- P7: `tools/orchestrate_tools.py` — `db.history` import + `record()` call removed
  (outer try/except last-resort net kept); `db/__init__.py` — `RunHistory` deleted,
  empty placeholder module retained; `main.py` — `_export_langsmith_env()` exports
  `LANGSMITH_TRACING/API_KEY/PROJECT` at startup when tracing is on, before tool import.
- P8: `mcp/CLAUDE.md` — LangSmith added to the stack sentence only.
- P9: test plan run — see Test results.

### Changed files
- mcp/agent_core/llm.py
- mcp/master_orchestrator/pyproject.toml
- mcp/master_orchestrator/config.py
- mcp/master_orchestrator/schemas/plan.py
- mcp/master_orchestrator/schemas/http.py
- mcp/master_orchestrator/prompts/orchestrate.py
- mcp/master_orchestrator/tools/planner.py
- mcp/master_orchestrator/tools/subagent_client.py
- mcp/master_orchestrator/tools/graph.py
- mcp/master_orchestrator/tools/orchestrate_tools.py
- mcp/master_orchestrator/db/__init__.py
- mcp/master_orchestrator/main.py
- mcp/CLAUDE.md

### Deviations from PLAN
- D6 specified `tool_name_prefix=True` + lookup by server-prefixed tool name. Implemented
  instead per-server lookup `get_tools(server_name=agent)` + exact unprefixed name match.
  Rationale (within the PLAN's own P5 risk item, which flagged the prefix-separator
  format as unverified and required fail-soft lookup): server-scoped listing removes the
  separator ambiguity entirely and only contacts the one server being dispatched — a
  global prefixed `get_tools()` would spawn/contact all servers per lookup, letting an
  unrelated broken sub-agent poison other dispatches (rule 6). Disambiguation of
  `(agent, tool)` is preserved. `handle_tool_errors=False` kept as planned.

### Test results
- RAN/PASSED — byte-compile: `python3 -m compileall mcp/agent_core mcp/master_orchestrator`
  clean (sandbox Python 3.10; syntax-level only).
- RAN/PASSED — A4 sweep: grep over mcp/master_orchestrator finds no keyword-hint tuples,
  no `NotImplementedError`, no `env.get(`/`.get("status")`, no `OrchestrateResponse`,
  no `RunHistory`/`history.record`, no `_merge`/`_summarize`, no host/port settings.
  Repo-wide grep: no external importer of the removed symbols (gateway unaffected, A1).
- RAN/PASSED — static import-consistency (AST): every `from master_orchestrator.*` /
  `from agent_core.*` import resolves to a real top-level name; `prompts.orchestrate`
  is imported by runtime code (tools/planner.py, tools/graph.py) — A5 import half.
- SKIPPED (environment-blocked) — editable install of agent_core + master_orchestrator:
  sandbox has no PyPI access (proxy returns 403 on pypi.org; `uv python install` also
  blocked) and only Python 3.10 (< required 3.11, `asyncio.timeout` needs 3.11). Deps
  (langchain 1.x, langgraph 1.x, langchain-mcp-adapters, langsmith, fastmcp) are not
  preinstalled, so the install step could not run.
- SKIPPED (blocked by the above) — mock e2e `run_orchestration` (A2) and failing/slow
  sub-agent fail-soft run (A3): cannot execute without the dependencies installed.
  Fail-soft paths were verified statically only (every exception/timeout branch in
  subagent_client returns an error envelope; dispatch uses `asyncio.gather` over
  per-task coroutines; orchestrate keeps the outer try/except). Validator must re-run
  the mock e2e in an environment with Python >=3.11 + deps.
- SKIPPED (tooling absent) — ruff/mypy/pytest not installed in sandbox and not
  installable offline; type-check half of A5 not executed. No pytest suite exists for
  master_orchestrator (per PLAN, none added).
- MANUAL (config-only, documented per PLAN) — real-provider + LangSmith trace (A2 second
  half): set `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`, optional `LANGSMITH_PROJECT`
  and a real `ORCHESTRATOR_LLM_PROVIDER`/`ORCHESTRATOR_LLM_API_KEY`; graph nodes, planner
  chain, adapter tool calls and synthesis chain auto-trace; per-task dispatch step is
  `@traceable`.
