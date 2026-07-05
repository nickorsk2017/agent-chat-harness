# TASK — 2026-07-04-simplify-orchestrator-langchain
owner: Engineer
immutable: true

## Requirements
- R1: Simplify `mcp/master_orchestrator` by replacing custom logic with canonical
  LangChain/LangGraph idioms; the stack is LangChain + LangGraph + LangSmith end-to-end.
- R2: Keep `graph.py` StateGraph (plan -> dispatch -> synthesize) as the spine of the agent.
- R3: Replace the keyword planner in `tools/planner.py` with a LangChain structured-output
  chain over `prompts/orchestrate.PLANNER_SYSTEM` emitting `list[SubTask]`. Remove the
  keyword heuristics and the `NotImplementedError` stub. `provider == "mock"` must still
  work with zero external keys (fake model with canned structured JSON, or a minimal
  deterministic fallback — Planner decides).
- R4: Replace `_merge`/`_summarize` in `graph.py` with a LangChain synthesis chain over
  `prompts/orchestrate.SYNTHESIS_SYSTEM`. No hardcoded payload-key lists.
- R5: Replace the hand-rolled FastMCP client plumbing in `tools/subagent_client.py`
  (`_client_for`, `_parse`) with `langchain-mcp-adapters` (`MultiServerMCPClient`) so
  sub-agent calls are LangChain tool calls. Preserve rule 6 (parallel dispatch, per-call
  timeout, fail-soft error envelope) and rule 7 (no exception crosses the MCP boundary).
- R6: Add LangSmith tracing: env-backed settings in `config.py`
  (tracing flag, API key, project name); LangChain/LangGraph components traced
  automatically; any remaining custom async step wrapped with `@traceable`.
- R7: Remove dead code: unused `OrchestrateResponse` in `schemas/http.py`, unused
  `host`/`port` settings, unread `history.recent()` path (keep `record` only if the
  Planner justifies it; otherwise drop `db.history` entirely).
- R8: Single envelope representation across boundaries: sub-agent results are parsed into
  typed models (`AgentResponse`/`SubTaskResult`), no raw-dict `env.get("status")` plumbing
  (subsystem rule 2).
- R9: Planner must verify the current stable APIs before designing: exact
  `langchain-mcp-adapters` package name/version and client API, and the current LangSmith
  env variable names (`mcp/CLAUDE.md` pins all frameworks to latest stable).

## Acceptance
- A1: `orchestrate` MCP tool contract is unchanged: `OrchestrateRequest` in,
  `AgentResponse[OrchestrationResult]` out; existing gateway callers work unmodified.
- A2: Full run works with zero external API keys (mock provider), and with a real
  provider + LangSmith key produces a trace showing the graph nodes, planner chain,
  sub-agent tool calls, and synthesis chain.
- A3: A failed/slow sub-agent yields an error entry in `results` without blocking or
  failing the other sub-tasks (rule 6/7 preserved).
- A4: No keyword hints, no `NotImplementedError` paths, no raw-dict envelopes, and no
  unused symbols remain in `mcp/master_orchestrator`.
- A5: `mcp/master_orchestrator` type-checks and its tests pass; `prompts/orchestrate.py`
  is actually imported by runtime code.

## Constraints
- Scope: `mcp/master_orchestrator/**`, `mcp/agent_core/llm.py` (only if the chain factory
  needs extension), `mcp/pyproject.toml` deps, and `mcp/CLAUDE.md` only if a stack rule
  needs a wording update. No changes to sub-agents' logic or the backend gateway.
- Do not remove planning from the orchestrator: the public contract stays
  "one prompt in -> one merged answer out" (option B, agreed with Engineer).
- All frameworks at latest stable; prompts stay in `prompts/`, settings in `config.py`
  (subsystem rules 4, 5).
