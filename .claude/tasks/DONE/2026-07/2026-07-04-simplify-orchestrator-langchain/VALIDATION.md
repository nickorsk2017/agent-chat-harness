# VALIDATION — 2026-07-04-simplify-orchestrator-langchain

## v1

verdict: PASS
validated_against: PLAN v1, EXEC v1, git diff -- mcp/

### Requirements
- R1 PASS — custom merge/keyword logic replaced by LangChain chains + adapters;
  stack line updated (mcp/CLAUDE.md:3).
- R2 PASS — StateGraph spine intact, same 3 nodes/edges (tools/graph.py:104-113).
- R3 PASS — structured-output planner chain over PLANNER_SYSTEM (tools/planner.py:38-56);
  real: `with_structured_output(Plan)` (planner.py:56); mock: FakeListChatModel seeded
  with canned Plan JSON -> PydanticOutputParser (planner.py:43-47); keyword hints and
  NotImplementedError stub gone (grep clean). Mock chain hand-traced: FakeListChatModel
  returns `_MOCK_PLAN.model_dump_json()` verbatim; PydanticOutputParser(Plan) parses it
  (enum serialized as "web_agent", round-trips) — parseable Plan, zero keys.
- R4 PASS — `_merge`/`_summarize` deleted; synthesis chain SYNTHESIS_SYSTEM+HUMAN ->
  model -> StrOutputParser (graph.py:43-59); results serialized generically via
  `model_dump(mode="json")` + json.dumps (graph.py:96-98); no payload-key lists.
- R5 PASS — MultiServerMCPClient from `settings.subagents` via `to_connection()`
  (subagent_client.py:26-37, config.py:24-28); per-call `asyncio.timeout` wraps resolve+
  invoke (subagent_client.py:78-90); parallel `asyncio.gather` kept (graph.py:84);
  fail-soft: unknown agent (:74), unknown tool (:81), JSON/envelope faults (:49-61),
  TimeoutError (:91), catch-all (:93) all return `AgentResponse.fail` — nothing raises.
  Constructor kwargs (`handle_tool_errors`, `tool_name_prefix`) confirmed against live
  reference docs (reference.langchain.com MultiServerMCPClient).
- R6 PASS — `langsmith_tracing/api_key/project` with canonical LANGSMITH_* validation
  aliases (config.py:46-55); `_export_langsmith_env()` before tool import (main.py:9-21);
  `@traceable(name="dispatch_subtask")` on the custom async step (graph.py:70).
- R7 PASS — `OrchestrateResponse` gone (schemas/http.py); host/port gone (config.py);
  `db.history` dropped, placeholder module kept (db/__init__.py); orchestrate_tools no
  longer imports/records history. Repo-wide grep (incl. backend/): zero references to
  OrchestrateResponse/RunHistory/history.record/history.recent. backend/gateway/main.py
  host/port is the gateway's own settings — unrelated.
- R8 PASS — adapter output validated into `AgentResponse` at the boundary
  (subagent_client.py:49-61); graph consumes `env.status/env.data/env.error` typed
  (graph.py:72-79); grep: no `env.get(`/`.get("status")` in mcp/master_orchestrator.
- R9 PASS — PLAN v1 records verified package/API/env-var facts with sources; spot-checked
  live: MultiServerMCPClient constructor kwargs match; LANGSMITH_* names used.

### Acceptance
- A1 PASS — `orchestrate` signature unchanged: OrchestrateRequest in,
  AgentResponse[OrchestrationResult] out (tools/orchestrate_tools.py:17); gateway
  `_parse_envelope` contract (status/data/answer/results) unaffected; no gateway changes
  in diff.
- A2 PASS (static + config) — mock path hand-traced end-to-end: plan node awaits planner
  chain -> canned one-task Plan; dispatch fail-soft; synthesis chain returns canned
  string with FakeListChatModel (sync `_call` runs under ainvoke via executor fallback);
  `run_orchestration` returns OrchestrationResult with non-empty answer. Live run
  environment-blocked (see Verification limits). Real-provider+LangSmith half is
  config-only, documented in EXEC.md as manual — per PLAN test plan.
- A3 PASS (static) — every failure branch in call_subagent returns an error envelope;
  `_run_subtask` maps it to `SubTaskResult(ok=False, error=...)`; gather runs siblings
  concurrently; outer try/except net kept (orchestrate_tools.py:20-24).
- A4 PASS — grep sweep clean: no keyword hints, no NotImplementedError, no raw-dict
  envelope access, no dead symbols in mcp/master_orchestrator.
- A5 PASS (partial-static) — `prompts.orchestrate` imported at runtime by planner.py:17
  and graph.py:25; byte-compile clean (re-run by Validator); all cross-module imports
  resolve by inspection. mypy/ruff/pytest not executable in sandbox; no pytest suite
  exists (per PLAN, none added).

### EXEC deviation ruling
`get_tools(server_name=agent)` instead of D6's `tool_name_prefix=True` global lookup:
COMPLIANT. PLAN P5 risk item itself flagged the prefix format as unverified and mandated
fail-soft lookup; server-scoped listing preserves (agent, tool) disambiguation, contacts
only the dispatched server (strengthens rule 6 isolation), keeps
`handle_tool_errors=False` as planned. Logic-level choice within plan intent, not an
architecture change.

### Verification limits
Sandbox has Python 3.10 (< required 3.11; `asyncio.timeout` unavailable) and no PyPI
index (editable install fails resolving hatchling — verified by attempt). Live mock e2e
(A2/A3) and type-check (A5) therefore could not be executed by Executor or Validator.
Static evidence (full hand-trace of mock planner/synthesis chains, all fail-soft
branches, live API-doc spot-check of the adapters constructor) leaves no material doubt;
recorded as non-blocking issue NB-3 rather than FAIL.

### Issues
Blocking: none.

Non-blocking:
- {id: NB-1, type: logic, severity: low, ref: tools/graph.py:84,
  note: "gather lacks return_exceptions=True; call_subagent never raises, but an
  unexpected raise inside the @traceable wrapper would cancel sibling sub-tasks —
  defense-in-depth only."}
- {id: NB-2, type: logic, severity: low, ref: tools/subagent_client.py:53-55,
  note: "tuple branch in _to_envelope does not re-attempt JSON parse of a str content
  element; degrades to an error envelope (fail-soft preserved), never crashes."}
- {id: NB-3, type: logic, severity: medium, ref: EXEC.md test results,
  note: "A2/A3 live mock e2e and A5 type-check unexecuted anywhere (env-blocked:
  Py3.10, no PyPI). Run `ORCHESTRATOR_LLM_PROVIDER=mock` e2e + mypy/ruff once in a
  dev env with Py>=3.11 before relying on the orchestrator."}
- {id: NB-4, type: logic, severity: low, ref: mcp/**/__pycache__/*.pyc,
  note: "tracked .pyc artifacts modified as a side effect; pre-existing repo hygiene
  issue (pycache committed to git), out of task scope."}
