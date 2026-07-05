# TASK — 2026-07-04-split-agents-packages
owner: Engineer
immutable: true

## Context
Today all four agents (master_orchestrator, web_agent, doc_analyzer, image_analyzer)
live under one `mcp_agents` namespace built by a single `mcp/pyproject.toml`, and every
agent imports `mcp_agents.shared.*` (envelope, llm). They run as separate MCP servers but
cannot be installed, versioned, or deployed independently. Goal: make each agent a
genuinely independent, separately-installable Python package.

## Requirements
- R1: Each agent becomes its own installable Python distribution with its own
  `pyproject.toml` (own name, version, dependency set, build target). Installing one agent
  must NOT require installing another agent's package.
- R2: Eliminate the shared runtime coupling `mcp_agents.shared.*`. The shared envelope and
  llm factory must be available to each agent WITHOUT importing another agent's package
  (vendor per-package, or publish as a standalone shared distribution each agent depends on
  explicitly). No agent may import a sibling agent's modules.
- R3: The orchestrator reaches sub-agents only as MCP servers (stdio/HTTP), never by
  Python-importing their packages. Its sub-agent registry keeps working after the split.
- R4: Each agent preserves the folder layout mandated by `mcp/CLAUDE.md`
  (db/ schemas/ tools/ prompts/ config.py main.py) and remains runnable via a documented
  entry point.
- R5: Update `mcp/README.md` and `mcp/.env.example` to reflect the new per-package install
  and run commands. Update `mcp/CLAUDE.md` only if its stated structure/running rules change.

## Acceptance
- A1: Each agent package's `pyproject.toml` exists, names a distinct distribution, and
  declares only that agent's dependencies (plus the shared dep if R2 uses a shared dist).
- A2: A repo-wide grep shows no module importing a sibling AGENT's package
  (web_agent / doc_analyzer / image_analyzer / master_orchestrator cross-imports) and no
  import of a removed `mcp_agents.shared` path. Shared code is resolved per R2.
- A3: Every agent's `main.py` (server) and the orchestrator's client registry import
  cleanly in a fresh interpreter with only that package's declared deps installed
  (verified by an import/collect smoke check; network calls remain mocked).
- A4: `mcp/README.md` documents the new independent install + run per agent; commands match
  the actual entry points. `.env.example` stays consistent with each `config.py`.
- A5: No regression to agent behavior: tools still return the `AgentResponse` envelope and
  the orchestrator still dispatches sub-agents concurrently (fail-soft preserved).

## Constraints
- Obey the harness (`.claude/CLAUDE.md`) and precedence `.claude/ > root CLAUDE.md > mcp/CLAUDE.md`.
- Keep Python >=3.11, async-first, Pydantic v2, FastMCP v2, pydantic-settings — no framework swaps.
- Mock-by-default must be preserved: the system still runs with zero external API keys.
- Prefer minimal, mechanical moves over rewrites; do not change tool/schema logic beyond
  what the repackaging requires.
- No secrets committed. No --no-verify, no bypassing the commit gate.
