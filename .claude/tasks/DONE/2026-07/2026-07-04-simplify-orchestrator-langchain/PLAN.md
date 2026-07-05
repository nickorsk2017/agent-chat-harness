# PLAN — 2026-07-04-simplify-orchestrator-langchain

## v1

### Verified facts (R9, checked 2026-07-04)
- `langchain-mcp-adapters` — exact PyPI name; latest stable **0.2.2** (released 2026-03-16).
  Source: https://pypi.org/project/langchain-mcp-adapters/ (a search snippet claimed 0.3.0;
  the PyPI project page is authoritative — 0.2.2).
- Client API: `from langchain_mcp_adapters.client import MultiServerMCPClient`;
  constructor takes `connections: dict[str, Connection]` where a stdio connection is
  `{"command", "args", "transport": "stdio"}` and HTTP is `{"url", "transport": "http"}`.
  Tools via `await client.get_tools()` (LangChain `BaseTool`s; each invocation opens a
  fresh session), or `client.session(name)` + `load_mcp_tools(session)` for an explicit
  session. Constructor kwargs incl. `tool_name_prefix: bool = False`,
  `handle_tool_errors: bool = True`. **No per-tool-call timeout parameter** in the tool
  invocation API → keep our own `asyncio.timeout` wrapper for R5/rule 6.
  Sources: https://pypi.org/project/langchain-mcp-adapters/ ,
  https://reference.langchain.com/python/langchain-mcp-adapters/client/MultiServerMCPClient
- LangSmith env vars (current names): `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`,
  `LANGSMITH_PROJECT` (optional `LANGSMITH_ENDPOINT`). `LANGCHAIN_TRACING_V2` is the
  legacy alias. With these set, LangChain/LangGraph runs (chains, graph nodes, tool
  calls) are traced automatically; custom async steps use
  `from langsmith import traceable`. `langsmith` PyPI latest stable **0.8.16**.
  Sources: https://docs.langchain.com/langsmith/trace-without-env-vars ,
  https://pypi.org/project/langsmith/
- Framework latest stable (PyPI, 2026-07): **langchain 1.3.11**, **langchain-core 1.4.8**,
  **langgraph 1.2.7**. `BaseChatModel.with_structured_output` and
  `langchain_core.output_parsers.PydanticOutputParser` current;
  `langchain_core.language_models.fake_chat_models.{FakeListChatModel,GenericFakeChatModel}`
  still present in core 1.x.
  Sources: https://pypi.org/project/langchain/ , https://pypi.org/project/langchain-core/ ,
  https://pypi.org/project/langgraph/ ,
  https://reference.langchain.com/python/langchain-core/language_models/fake_chat_models/GenericFakeChatModel
- Mock caveat: fake chat models have **no working `bind_tools`** (GH discussion
  langchain-ai/langchain#31761), so `with_structured_output` (tool-calling method) cannot
  run on them → mock path must parse canned JSON text instead (decision D3).

### Architecture decisions
- D1 (R1, R2): keep `graph.py` StateGraph plan→dispatch→synthesize as the spine; nodes
  delegate to LangChain runnables (planner chain, adapter tools, synthesis chain). No new
  nodes, no conditional edges.
- D2 (R3): planner becomes a chain factory: `ChatPromptTemplate` built from
  `prompts.orchestrate.PLANNER_SYSTEM` (+ a human template carrying prompt & context,
  stored in `prompts/`) piped to structured output. New pydantic wrapper `Plan`
  (`tasks: list[SubTask]`) in `schemas/plan.py` because `with_structured_output` needs a
  single top-level schema. Keyword hint tuples and `_plan_with_llm` stub are deleted.
- D3 (R3 mock strategy): provider-split inside the factory —
  real provider → `prompt | model.with_structured_output(Plan)`;
  `provider == "mock"` → `prompt | fake-chat-model(canned Plan JSON) | PydanticOutputParser(Plan)`.
  Canned response = one fixed `web_agent/get_news` sub-task (static, deterministic, zero
  keys). Chosen over faking tool-calls because fake models lack `bind_tools`
  (verified above). No prompt-text heuristics anywhere (A4).
- D4 (R3): extend `agent_core/llm.py::build_chat_model` with an optional
  `mock_responses: list[str] | None` parameter so callers can seed the fake model's canned
  output; default behavior unchanged for other agents (allowed by scope).
- D5 (R4): `_merge`/`_summarize` deleted. Synthesis = `ChatPromptTemplate` from
  `SYNTHESIS_SYSTEM` (+ human template rendering original prompt and serialized
  `SubTaskResult`s) piped to chat model piped to `StrOutputParser`. Same chain shape for
  mock and real (mock returns a canned string). No payload-key lists; results are
  serialized generically via pydantic dump.
- D6 (R5): `subagent_client.py` rebuilt on `MultiServerMCPClient`. One lazily-built
  module-level client from `settings.subagents` (each endpoint mapped to a stdio or http
  Connection dict; `SubAgentEndpoint` gains a converter to that dict). Tool lookup by
  server-prefixed name (`tool_name_prefix=True`) so `(agent, tool)` from a `SubTask`
  resolves unambiguously; invoke via the tool's `ainvoke` with the `{"request": ...}`
  argument shape (unchanged wire contract with sub-agents). `handle_tool_errors=False`
  so failures surface as exceptions we catch, not success-shaped strings.
- D7 (R5 timeout/fail-soft): adapters expose no per-call timeout (verified) → each
  dispatch wraps the tool call in `asyncio.timeout(settings.subagent_timeout_s)`;
  `asyncio.gather` over all sub-tasks stays in the dispatch node (rule 6). Every
  exception/timeout is converted to a failed `SubTaskResult`; nothing raises across the
  MCP boundary (rule 7) — the outer try/except in `orchestrate_tools.py` remains the
  last-resort net.
- D8 (R8): single envelope typing — adapter tool output (dict or JSON text) is validated
  into `agent_core.envelope.AgentResponse` immediately at the client boundary;
  `subagent_client` returns typed results, `graph.py` builds `SubTaskResult` from
  `AgentResponse.status/data/error`. No `env.get(...)` raw-dict plumbing anywhere.
- D9 (R6): `config.py` gains `langsmith_tracing: bool`, `langsmith_api_key`,
  `langsmith_project` read from the canonical `LANGSMITH_*` env names (validation aliases,
  not the `ORCHESTRATOR_` prefix). `main.py` exports them to `os.environ` at startup when
  tracing is on, so LangChain/LangGraph auto-trace. The per-sub-task dispatch coroutine
  (the one remaining custom async step) gets `@traceable`.
- D10 (R7): `OrchestrateResponse` alias and `host`/`port` settings deleted. `db.history`
  dropped entirely — `recent()` has no reader anywhere (repo-wide grep), the store is
  in-memory/lossy, and LangSmith tracing (R6) supersedes it as run observability;
  `db/__init__.py` stays as an empty placeholder module (subsystem folder template),
  `orchestrate_tools.py` loses the import/record call.
- D11 (deps): `master_orchestrator/pyproject.toml` adds `langchain-mcp-adapters>=0.2.2`
  and `langsmith>=0.8.16`; bump floors langchain>=1.0, langchain-core>=1.0,
  langgraph>=1.0 (latest-stable pin per mcp/CLAUDE.md). `agent_core/pyproject.toml`
  unchanged (D4 uses only langchain-core). `mcp/CLAUDE.md` needs no rule change
  (LangSmith already implied by stack line? it is NOT listed → one-line wording update
  adding LangSmith to the stack sentence is permitted by constraints; keep to that).
- D12 (A1): `orchestrate` tool signature and `OrchestrateRequest` /
  `AgentResponse[OrchestrationResult]` contract untouched; gateway
  `orchestrator_client.py` keeps working unmodified.

### File impact map
| File | Action | Req |
|---|---|---|
| mcp/master_orchestrator/config.py | modify (drop host/port; add LangSmith fields; SubAgentEndpoint→Connection dict) | R5 R6 R7 |
| mcp/master_orchestrator/schemas/plan.py | modify (add `Plan` wrapper) | R3 |
| mcp/master_orchestrator/schemas/http.py | modify (remove `OrchestrateResponse`) | R7 |
| mcp/master_orchestrator/prompts/orchestrate.py | modify (add human templates for planner & synthesis; prompts stay data) | R3 R4 |
| mcp/master_orchestrator/tools/planner.py | rewrite (structured-output chain factory + mock path; delete heuristics/stub) | R3 |
| mcp/master_orchestrator/tools/subagent_client.py | rewrite (MultiServerMCPClient; typed AgentResponse parse; timeout+fail-soft) | R5 R7(rule) R8 |
| mcp/master_orchestrator/tools/graph.py | modify (nodes call chains/tools; delete `_merge`/`_summarize`; `@traceable` on dispatch step) | R2 R4 R5 R6 R8 |
| mcp/master_orchestrator/tools/orchestrate_tools.py | modify (drop history import/record) | R7 |
| mcp/master_orchestrator/db/__init__.py | modify (empty placeholder; delete RunHistory) | R7 |
| mcp/master_orchestrator/main.py | modify (LangSmith env export at startup) | R6 |
| mcp/master_orchestrator/pyproject.toml | modify (add adapters+langsmith; bump floors) | R5 R6 R9 |
| mcp/agent_core/llm.py | modify (optional `mock_responses` param) | R3 |
| mcp/CLAUDE.md | modify (add LangSmith to stack sentence only) | R1 R6 |

### Steps
- P1 — files: pyproject.toml (master_orchestrator), agent_core/llm.py — add deps, extend
  chat-model factory with `mock_responses`. (R3 R9)
- P2 — files: schemas/plan.py, schemas/http.py, prompts/orchestrate.py — add `Plan`,
  remove dead alias, add planner/synthesis human templates. (R3 R4 R7)
- P3 — files: config.py — remove host/port, add LangSmith settings with `LANGSMITH_*`
  aliases, add endpoint→Connection conversion. (R5 R6 R7)
- P4 — files: tools/planner.py — structured-output chain factory (real vs mock per D3),
  delete keyword planner and NotImplementedError stub. (R3)
- P5 — files: tools/subagent_client.py — MultiServerMCPClient wiring, typed
  `AgentResponse` parsing, unknown-agent guard, timeout + fail-soft envelope. (R5 R8)
- P6 — files: tools/graph.py — plan node awaits planner chain; dispatch node gathers
  `@traceable` per-task calls building `SubTaskResult` from typed envelopes; synthesize
  node awaits synthesis chain; delete `_merge`/`_summarize`. (R2 R4 R5 R6 R8)
- P7 — files: tools/orchestrate_tools.py, db/__init__.py, main.py — drop history, add
  LangSmith env export. (R6 R7)
- P8 — files: mcp/CLAUDE.md — add LangSmith to the stack line. (R1)
- P9 — run test plan below; record in EXEC.md. (A2 A3 A4 A5)

### Risks
- Adapter tool invocation arg shape: sub-agent tools take a single `request` model param;
  adapter tools expose that as the tool's input schema — Executor must confirm
  `{"request": {...}}` maps cleanly (fallback: pass the dict directly if the adapter
  flattens the schema). Logic-level risk, contained in P5.
- `tool_name_prefix` naming format (0.2.2) must be checked at implementation time
  (prefix separator); tool lookup must fail-soft to an error `SubTaskResult`, never raise.
- Mock canned plan is static: mock runs always dispatch the same sub-task; acceptable per
  R3/A2 (deterministic, zero keys) — flagged so Validator does not treat it as a defect.
- Version floors bump may pull breaking langchain 1.x API changes into other agents via
  the dev aggregator; scope keeps their code untouched — Executor should verify the fleet
  still imports (A5 covers orchestrator type-check/tests only).

### Test plan (Executor must run)
- Install: editable install of agent_core + master_orchestrator with new deps resolving.
- Mock e2e (A2/A3): with `ORCHESTRATOR_LLM_PROVIDER=mock` and no keys, invoke
  `run_orchestration` (or the `orchestrate` tool via a FastMCP in-process client) with a
  plain prompt → `AgentResponse[OrchestrationResult]` with non-empty `answer` and typed
  `results`; then simulate one failing/unknown sub-agent → error entry in `results`,
  other sub-tasks unaffected, no exception escapes.
- A4 sweep: grep confirms no keyword hint tuples, no `NotImplementedError`, no
  `env.get(`, no `OrchestrateResponse`, no `RunHistory` in mcp/master_orchestrator.
- A5: `prompts/orchestrate.py` imported by planner+graph (runtime); type-check
  (ruff/mypy-equivalent used by repo) and existing pytest suite for master_orchestrator
  (currently none — add nothing beyond what EXEC needs to prove A2/A3 if the harness
  requires a runnable check).
- Real-provider + LangSmith path is config-only; documented in EXEC.md as manual
  verification (trace shows graph nodes, planner chain, tool calls, synthesis chain).
